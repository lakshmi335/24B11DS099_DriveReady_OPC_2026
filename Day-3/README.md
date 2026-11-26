# Day 3 – Your first agent: what an agent is, and LangChain
 
Notebook: `day3.ipynb` (Google Colab) · Test file: `tests.csv`
Case study: **Sweet Crumbs Home Bakery**. The Day 2 chatbot is rebuilt with LangChain and gets its first automated tests.
 
## What this project does
- Rebuilds the bakery assistant with LangChain: chat model, prompt template, memory placeholder and chain.
- Adds a test runner (`tests.csv`) that prints PASS/FAIL per question and an overall pass rate.
- Shows a sneak peek of `create_agent` with an empty tool list (real tools arrive on Day 4).
## Setup
1. `GROQ_API_KEY` in Colab Secrets (🔑 icon, Notebook access ON), same as Days 1 and 2.
2. Upload the notebook to Colab and run the cells top to bottom. The first cell installs `langchain` and `langchain-groq`.
3. The cell with `%writefile tests.csv` creates the test file. If you upload `tests.csv` yourself, skip that cell.
## What is in the notebook
| Part | What it does | Concept |
|------|--------------|---------|
| Cell 1 | Install, load key, create `ChatGroq` | `llm.invoke()` |
| Task 1 | Model, template with `{business}`, chain with `\|` | Prompt template, chain, `StrOutputParser` |
| Build | Assistant with `MessagesPlaceholder("history")` and `ask()` | Memory with LangChain |
| Customer test | Asks eggless / same day / Kakinada / 6 cupcakes | Manual testing |
| Tests | `run_tests()` reads `tests.csv`, prints pass rate | Regression testing, evals |
| Agent peek | `create_agent(model, tools=[], system_prompt=SYSTEM)` | Agent with no tools = chain |
| 30% #1 | Reusable template with `{business}` and `{facts}` | One template, many businesses |
| 30% #2 | `my_tests.csv` for your own business | Your own evals |
| 30% #3 | Prompt v1 vs v2 pass rate | Change one thing, re-test |
| 30% #4 | Temperature 1.0, two runs | Randomness changes results |
| 30% #5 | Plain code / one LLM call / agent table | Agent or not? |
 
## Key ideas
- **Chatbot vs agent:** a chatbot answers with words; an agent has a goal, uses tools and decides the steps.
- **Four parts of an agent:** brain (LLM), instructions (system prompt), tools (Python functions, Day 4), memory (history).
- **Agent loop (ReAct):** think → act → observe → repeat until a final answer. Your code runs the tools, and you set a round limit.
- **Three levels:** traditional software (fixed rules), generative AI (creates), agentic AI (creates and acts).
- **Agent or not:** known steps → plain code; one-off text → one LLM call; unknown steps + tools → agent.
- **LangChain:** one interface for many models plus building blocks. `llm.invoke()` returns a reply and the text is in `.content`.
- **Chain:** `prompt | llm | StrOutputParser()`, run with `.invoke({...})` and one value per blank.
- **Testing:** each CSV row has a real question and a `must_include` text. Re-run all rows after every prompt change and watch the pass rate.
## Common traps
| Problem | Cause / fix |
|---------|-------------|
| Error about a missing template variable | Real `{ }` (for example JSON) in the system prompt. Write plain text or double the braces `{{ }}` |
| `NameError: agent / result` | Variable names don't match between lines (for example `agent_order` created but `agent` used) |
| `FileNotFoundError: tests.csv` | Run the `%writefile tests.csv` cell or upload the file. Check the filename (`tests.csv`, not `test.csv`) |
| Model not found | Check the model name; try `openai/gpt-oss-120b` or list models with `client.models.list()` |
| 429 rate limit | Wait a minute and re-run |
 
## Before Day 4
Write two Python functions your business needs (for example a price lookup and an "is it available?" check) with type hints and docstrings. Tomorrow they become the agent's tools.
 
