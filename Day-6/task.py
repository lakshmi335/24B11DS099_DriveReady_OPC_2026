"""
Day 6 · Workflows, planning and LangGraph
Sweet Crumbs Home Bakery router

Workflow on the outside:   START -> classify -> (order | faq | other) -> END
Focused agents inside:     faq agent (read-only tools), order agent (can save orders)

Run:
    python sweet_crumbs_router.py              # runs the 4 test messages
    python sweet_crumbs_router.py --chat       # type your own messages
    python sweet_crumbs_router.py --draw       # only save the graph picture
"""
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

# --------------------------------------------------------------------------
# 0. LLM  (OpenRouter or OpenAI, whichever key you set in .env)
# --------------------------------------------------------------------------
def get_llm() -> ChatOpenAI:
    if os.getenv("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            model=os.getenv("MODEL", "openai/gpt-4o-mini"),
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
        )
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=os.getenv("MODEL", "gpt-4o-mini"), temperature=0)
    sys.exit("Set OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file.")


llm = get_llm()

# --------------------------------------------------------------------------
# 1. Tools  (stand-ins for your Day 4/5 tools; sample data, edit freely)
# --------------------------------------------------------------------------
PRICES = {                      # price in rupees
    "cupcake": 80,
    "chocolate cake": 650,
    "plum cake": 500,
    "vanilla cake": 550,
}

FAQS = [
    "Delivery is free within 5 km on orders above Rs 1000. Otherwise Rs 60 delivery charge.",
    "Orders must be placed at least 24 hours before pickup or delivery.",
    "Eggless versions of all cakes and cupcakes are available at no extra cost.",
    "Plum cake contains cashew nuts and almonds, so it is not nut-free.",
    "We accept UPI and cash. Advance payment of 50 percent is needed for orders above Rs 2000.",
]

ORDERS_FILE = Path("orders.csv")


@tool
def get_price(item: str) -> str:
    """Get the price in rupees of one unit of a bakery item (e.g. 'cupcake', 'plum cake')."""
    key = item.lower().strip()
    for name, price in PRICES.items():
        if name in key or key in name:
            return f"{name}: Rs {price} each"
    return f"No price found for '{item}'. Available: {', '.join(PRICES)}"


@tool
def is_open(day: str) -> str:
    """Check if the bakery is open on a given day of the week, e.g. 'Sunday'."""
    closed = {"monday"}
    if day.lower().strip() in closed:
        return f"Closed on {day}."
    return f"Open on {day}, 9 AM to 8 PM."


@tool
def search_faq(query: str) -> str:
    """Search the bakery's policies (delivery, payment, ingredients, lead time)."""
    words = {w for w in query.lower().replace("?", "").split() if len(w) > 3}
    hits = [f for f in FAQS if words & set(f.lower().replace(",", "").replace(".", "").split())]
    return "\n".join(hits[:3]) if hits else "No matching policy found."


@tool
def log_order(name: str, item: str, quantity: int, pickup_date: str) -> str:
    """Save a confirmed order. Only call with name, item, quantity and pickup date all known."""
    new_file = not ORDERS_FILE.exists()
    with ORDERS_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "name", "item", "quantity", "pickup_date"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), name, item, quantity, pickup_date])
    return f"Order saved: {quantity} x {item} for {name}, pickup {pickup_date}."


# --------------------------------------------------------------------------
# 2. State and classifier
# --------------------------------------------------------------------------
class BakeryState(TypedDict):
    message: str   # what the customer wrote
    intent: str    # filled in by classify
    reply: str     # filled in by the path that handles it


class Intent(BaseModel):
    intent: Literal["order", "faq", "other"] = Field(
        description=(
            "order = wants to buy or book cakes; "
            "faq = asks about prices, timings or policies; "
            "other = greetings or anything unrelated to the bakery"
        )
    )


classifier = llm.with_structured_output(Intent)

# --------------------------------------------------------------------------
# 3. Two focused agents
# --------------------------------------------------------------------------
FAQ_PROMPT = """You answer questions for Sweet Crumbs Home Bakery.
Use get_price for prices, is_open for timings and search_faq for policies. Never guess.
If the answer isn't found, say "I'll check with the owner." Under 50 words."""

ORDER_PROMPT = """You take cake orders for Sweet Crumbs Home Bakery.
Use get_price for totals. Before log_order, make sure you have name, item, quantity and
pickup date; ask for anything missing. After saving, read the order back. Under 60 words."""

faq_agent = create_agent(model=llm, tools=[search_faq, get_price, is_open], system_prompt=FAQ_PROMPT)
order_agent = create_agent(model=llm, tools=[get_price, log_order], system_prompt=ORDER_PROMPT)


# --------------------------------------------------------------------------
# 4. Nodes, conditional edge, compile
# --------------------------------------------------------------------------
def classify(state: BakeryState) -> dict:
    return {"intent": classifier.invoke(state["message"]).intent}


def ask_agent(agent, message: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content


def answer_faq(state: BakeryState) -> dict:
    return {"reply": ask_agent(faq_agent, state["message"])}


def take_order(state: BakeryState) -> dict:
    return {"reply": ask_agent(order_agent, state["message"])}


def other(state: BakeryState) -> dict:
    return {"reply": "Hello from Sweet Crumbs! I can help with cakes, prices, orders and our policies."}


def route(state: BakeryState) -> str:
    return state["intent"]


builder = StateGraph(BakeryState)
builder.add_node("classify", classify)
builder.add_node("faq", answer_faq)
builder.add_node("order", take_order)
builder.add_node("other", other)

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify", route, {"order": "order", "faq": "faq", "other": "other"}
)
builder.add_edge("faq", END)
builder.add_edge("order", END)
builder.add_edge("other", END)

graph = builder.compile()


# --------------------------------------------------------------------------
# 5. See it, run it
# --------------------------------------------------------------------------
def save_graph_picture(path: str = "graph.png") -> None:
    print(graph.get_graph().draw_mermaid())          # text version, works offline
    try:                                             # PNG needs internet (mermaid.ink)
        Path(path).write_bytes(graph.get_graph().draw_mermaid_png())
        print(f"Saved graph picture to {path}")
    except Exception as e:
        print(f"(Could not draw PNG: {e}). Paste the Mermaid text above into mermaid.live.")


def run(message: str) -> None:
    print("\nCustomer:", message)
    for step in graph.stream({"message": message}, stream_mode="updates"):
        print("  ", step)


TESTS = [
    "Do you deliver to my area?",
    "I'm Ravi, book 2 eggless plum cakes for 24 Dec",
    "Good morning!",
    "Is the plum cake nut-free?",
    # hard-to-sort ones from the tutorial:
    "I want to know if you can make 2 cakes by tomorrow",
]

if __name__ == "__main__":
    if "--draw" in sys.argv:
        save_graph_picture()
    elif "--chat" in sys.argv:
        print("Sweet Crumbs bot. Type 'quit' to exit.")
        while (msg := input("\nYou: ").strip()).lower() not in {"quit", "exit"}:
            if msg:
                run(msg)
    else:
        save_graph_picture()
        for m in TESTS:
            run(m)
