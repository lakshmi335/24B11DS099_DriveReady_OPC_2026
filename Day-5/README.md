# Day 5 – Memory and RAG: an agent that remembers and looks things up

Notebook: `Day5_Memory_RAG_Agent.ipynb` (Google Colab)
Case study: **Sweet Crumbs Home Bakery** (Part A) and **your own business** (Part B, example: Bright Minds Tuition Centre).

## What this project does
- Gives the agent **conversation memory** with a checkpointer and one `thread_id` per customer.
- Stores the business's policies in **ChromaDB** and lets the agent search them by meaning (**RAG**) through a `search_faq` tool.
- Finishes the **single agent**: brain, instructions, tools, memory, knowledge, and tests with a pass rate.

## Setup
1. `GROQ_API_KEY` in Colab Secrets (🔑 icon, Notebook access ON).
2. Upload the notebook to Colab and run the cells top to bottom. **Cell 0** is self-contained, so you can run Day 5 without the Day 4 notebook.
3. Orders are saved to a **local CSV** by default (no Google sign-in needed). Set `USE_GOOGLE_SHEETS = True` in Cell 0 only if your Google sign-in works.
4. For Part B, have your `facts.txt` (15–20 facts, one per line) in the Colab files. If it is missing, the notebook writes the Bright Minds example.

## What is in the notebook
| Part | What it does | Concept |
|------|--------------|---------|
| Cell 0 | Model, order saving, `get_price`, `is_open`, `log_order` | Day 3–4 pieces |
| Topic 2 | `InMemorySaver` + `thread_id`; Ravi and Sravani chat at the same time | Conversation memory |
| Topic 3 | Token estimate: all 12 facts vs 3 relevant facts | Why not everything in the prompt |
| Topics 4–5 | `chromadb`, `upsert`, `query`; distance for 4 questions | Embeddings, vector database |
| Topic 6 | `chunk()` with different sizes and overlap | Chunking |
| Topic 7 | `search_faq` tool; agent with memory and `chat(thread_id, text)` | RAG |
| Test it like a customer | Paraphrase, follow-up, not in FAQs, different thread | Manual testing |
| Cell 4 | 5 new rows in `tests.csv`, `run_tests()` with a fresh thread per question | Pass rate |
| Part B 1 | `facts.txt` → one fact per chunk in ChromaDB | Your knowledge |
| Part B 2 | Your tools and a `search_facts` tool with a topic list in its docstring | Your search tool |
| Part B 3 | Your agent with checkpointer; test with two `thread_id`s | Your agent |
| Part B 4 | Ask things your documents don't cover | Break it |
| Part B 5 | `my_tests.csv` and your pass rate (aim for 80%+) | Sign-off |

## Key ideas
- **Three kinds of memory:** conversation (this chat, threads), customer (facts across chats, saved in a sheet later), knowledge (documents, RAG).
- **Threads:** `create_agent(..., checkpointer=InMemorySaver())`, then pass `{"configurable": {"thread_id": ...}}` with every call. Same id = same conversation; different ids never mix. `InMemorySaver` is lost when the runtime restarts.
- **Not everything in the prompt:** you pay for every input token on every call. Search first and send only the 2–3 relevant facts.
- **Embeddings:** text → list of numbers; similar meaning → nearby numbers, even with different words. A **smaller distance** in the notebook means a closer match.
- **ChromaDB:** `get_or_create_collection` → `upsert(ids, documents)` → `query(query_texts, n_results)`. Results are lists of lists, so use `results["documents"][0]`. `upsert` adds or updates, so re-running or changing a fact doesn't create duplicates.
- **Chunking:** one chunk ≈ one idea; too big mixes topics, too small breaks meaning; a small overlap protects sentences at the cut. For FAQs, one fact = one chunk.
- **RAG:** retrieve → augment → generate. Make retrieval a tool, write the topics in its docstring, and add the rule "answer ONLY from what it returns; otherwise say I'll check with the owner". Update the documents, not the model.
- **Sign-off:** prices and hours → tools; policies → `search_faq`; earlier messages → thread memory; saving → `log_order`. Test every kind of message before building multiple agents.

## Reading the tests
- In `must_include`, `a|b` means either word is accepted (for example `3600|3,600`).
- Each test runs in a fresh thread, so earlier tests can't help or hurt later ones.
- The policy facts changed today. An old test (for example the Day 3 "Do you deliver to Kakinada?" row) may now fail. Update the `must_include` or the facts; that is normal.

## Common traps
| Problem | Cause / fix |
|---------|-------------|
| `FileNotFoundError: facts.txt` | Run the Day 4 facts cell or upload the file. The notebook writes the Bright Minds example if it is missing |
| Assertion "Aim for 15-20 facts" | Check for blank lines or fewer than 15 lines in `facts.txt` |
| Agent answers a policy from its own knowledge | Make the RULES stricter ("answer ONLY from what search_faq returns") and improve the tool docstring |
| Agent uses `search_faq` for prices | Add "not for prices or opening hours" to the docstring |
| Wrong fact retrieved | Rewrite the fact as a full sentence naming the topic; try `n_results=3` and read the distances |
| Ravi's messages are gone after a restart | `InMemorySaver` is in memory only; in Week 2 threads can be saved to a file or database |
| Chroma downloads a small model on first use | Normal; the first `query` takes a few extra seconds |
| 429 error | Too many requests; wait a minute, run fewer tests, use your own key |

## Before Day 6
Draw on paper the steps your business follows for one customer request (for example: question → answer, or order → check → save → confirm). Tomorrow it becomes a LangGraph workflow, the first step to multiple agents.
