# Sweet Crumbs Router: Day 6 (Workflows, planning and LangGraph)

A LangGraph workflow for a home bakery. Every customer message is **sorted first**
(order, FAQ or other), then handed to the path that handles it. Each path has its
own small agent with only the tools it needs.

```
START -> classify --+--> order  (order_agent: get_price, log_order) --> END
                    +--> faq    (faq_agent: search_faq, get_price, is_open) --> END
                    +--> other  (fixed greeting) --> END
```

## What it demonstrates

| Idea | Where in the code |
|---|---|
| Workflow outside, agents inside | `classify` + `route` decide the path; `faq_agent` / `order_agent` handle it |
| Structured output | `Intent` model with `Literal["order","faq","other"]` |
| State | `BakeryState` (`message`, `intent`, `reply`); nodes return only the keys they change |
| Nodes and edges | `add_node`, `add_edge`, `START`, `END`, `compile()` |
| Conditional edge | `add_conditional_edges("classify", route, {...})` |
| Draw and stream | `draw_mermaid_png()` and `graph.stream(..., stream_mode="updates")` |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then paste your key into .env
```

Set **one** of `OPENROUTER_API_KEY` or `OPENAI_API_KEY`. Optionally set `MODEL`
(default: `openai/gpt-4o-mini` on OpenRouter, `gpt-4o-mini` on OpenAI).

## Run

```bash
python sweet_crumbs_router.py            # saves graph.png, runs 5 test messages
python sweet_crumbs_router.py --chat     # type your own messages
python sweet_crumbs_router.py --draw     # only draw the graph
```

Example streamed output (one line per node, so you can see *why* a message went where it did):

```
Customer: Do you deliver to my area?
   {'classify': {'intent': 'faq'}}
   {'faq': {'reply': 'Delivery is free within 5 km on orders above Rs 1000...'}}
```

Confirmed orders are appended to `orders.csv`.

## Notes

- **Sample data.** Prices, FAQs and `is_open` hours in the script are placeholders;
  edit `PRICES`, `FAQS` and `is_open` to match your own business. In the Colab
  version, these were your Day 4/5 tools and FAQ collection.
- **No memory yet.** Each message is handled on its own. Day 7 adds a checkpointer
  and owner approval.
- **Graph picture.** `draw_mermaid_png()` uses an online service, so it needs
  internet. If it fails, the script prints Mermaid text you can paste into
  https://mermaid.live.
- **Wrong route?** Read the first streamed line (the intent). If the classifier is
  wrong, improve the `Field(description=...)` in `Intent` or add a few-shot example.
- **Adding an intent** (e.g. `"complaint"`): add it to the `Literal`, add a node,
  and add it to the mapping in `add_conditional_edges`. Keep all three in sync.

## Your 50% (adapt this to your own business)

1. Draw your workflow on paper; mark each decision as a diamond.
2. Write your own `TypedDict` state.
3. Build a `Literal` classifier and a graph with at least 3 nodes and 1 conditional edge.
4. Draw the graph and compare with your paper drawing.
5. Send at least one message down every branch and save the streamed output.

## Files

- `sweet_crumbs_router.py`: the whole workflow
- `requirements.txt`, `.env.example`: setup
