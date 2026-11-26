# Day 4 – Tools, structured output and Google Sheets

Notebook: `day4.ipynb` (Google Colab)
Case study: **Sweet Crumbs Home Bakery**. The Day 3 assistant gets tools, checks its data with Pydantic, and saves orders into a Google Sheet.

## What this project does
- Gives the agent three tools: `get_price`, `is_open` and `log_order`.
- Turns a messy chat message into a checked `Order` record (Pydantic).
- Saves each confirmed order as one row in a Google Sheet ("Sweet Crumbs Orders").
- Shows the full agent trace (question → tool calls → tool results → answer).
- Handles rate limits (429) and tool errors politely.

## Setup
1. `GROQ_API_KEY` in Colab Secrets (🔑 icon, Notebook access ON), your own key.
2. Upload the notebook to Colab and run the cells top to bottom.
3. In Cell 1 a Google pop-up asks you to sign in. Allow access so Colab can create the sheet in your Drive.
4. The notebook uses `gc.open(...)` first and only creates the sheet if it doesn't exist, so re-running won't make duplicate sheets or repeated header rows.
5. Open the sheet link printed in Cell 1 on your phone to watch orders arrive.

## What is in the notebook
| Part | What it does | Concept |
|------|--------------|---------|
| Cell 1 | Model with `max_retries=3`, Google sign-in, sheet created/opened | gspread, 429 retries |
| Cell 2 | `MENU`, `HOURS`, `Order` model, 3 `@tool` functions | Tools, Pydantic |
| Structured output | `llm.with_structured_output(Order)`, then rejected bad data (qty 0, donut) | Pydantic validation |
| Cell 3 | `create_agent(model, tools, system_prompt)` and `chat()` with memory + try/except | Agent loop |
| Cell 4 | `pretty_print()` for every message | The trace |
| Customer tests | donut, order with no date, 0 cupcakes; checks no wrong row was saved | Testing tools |
| tests.csv | Appends 4 new rows and runs them against the agent | Regression tests |
| 30% #1 | `get_fee` and `seats_available` tools for your business | Your tools |
| 30% #2 | `Enquiry` Pydantic class tested on 5 messy messages | Your record |
| 30% #3 | Your sheet, `log_enquiry` tool and agent | Your sheet |
| ★ Example | Multi-turn parent conversation, trace and sheet contents | How it all fits together |
| 30% #4 | Rename a tool to `tool1` ("does stuff") and watch it fail | Tool names and docstrings |
| 30% #5 | Counts model calls and tool calls from the trace | Reading traces |

## Worked business example: Bright Minds Tuition Centre
The notebook has a ★ section that runs one realistic conversation end to end, so you can see how every idea fits together.

| Bakery (class demo) | Tuition centre (example) | Idea |
|---|---|---|
| `get_price` | `get_fee` | Tool for exact numbers |
| `is_open` | `seats_available` | Tool for live facts |
| `Order` + `log_order` | `Enquiry` + `log_enquiry` | Pydantic check + save to sheet |
| Orders sheet | Enquiries sheet | Owner sees it on her phone |

**Typical conversation** (your wording will differ):

| Turn | Parent says | What the agent does |
|------|-------------|---------------------|
| 1 | "Fee for Maths for 3 months? Is there a seat?" | Calls `get_fee` and `seats_available`, answers with Rs 4500 and 4 free seats |
| 2 | "My daughter is in class 9." | No tool; asks for the parent's name and phone |
| 3 | "I'm Suresh, phone 98480 12345. Please note the enquiry." | Calls `log_enquiry`; Pydantic checks it; one row is added to the sheet |

**Try breaking it:** say "class 12" or "subject: physics". Pydantic rejects the record, the tool returns an error message, the agent asks the parent to correct it, and no wrong row reaches the sheet.

To adapt it to your own business, replace `FEES` and `SEATS`, the two tools, the `Enquiry` fields and the system prompt, and keep the same pattern.

## Key ideas
- **Tools:** the model only writes text. Tools give it live facts (prices, hours, stock), actions (save, send) and exact maths.
- **Function calling:** you send tool descriptions → the model replies with a tool call → your code runs it → the result goes back as a tool message. The model never runs your code.
- **Good tools:** snake_case name, type hints, a docstring that says *when* to use it, one job per tool, and a helpful message on bad input instead of a crash.
- **create_agent:** `create_agent(model, tools, system_prompt)`, then `.invoke({"messages": [...]})`. Last message = final answer; the whole list = the trace.
- **Rate limits:** 429 = too many requests. Use your own key, small tests, `max_retries`, and try/except around the agent.
- **Pydantic:** an `Order` class with field types and rules (`Literal`, `ge=1`). `with_structured_output(Order)` returns a checked object, not a string.
- **Google Sheets (Colab):** `auth.authenticate_user()` → `gspread.authorize(creds)` → `gc.open(...)` → `ws.append_row([...])`. One order = one row, columns always in the same order.
- **log_order:** checks the input with Pydantic again, works out the total in Python, saves the row, and returns a confirmation. The docstring says to use it only when the order is complete.

## Common traps
| Problem | Cause / fix |
|---------|-------------|
| Duplicate header rows in the sheet | Re-running `gc.create` + `append_row(header)`. The notebook uses `get_sheet()` to avoid this |
| `SpreadsheetNotFound` | Sheet name differs, or sign-in was cancelled. Re-run Cell 1 and allow access |
| 429 error | Too many requests. Wait a minute, test with fewer questions, use your own key |
| Agent calls the wrong tool | Fix the tool name and docstring first, not the model |
| Agent saves a half order | Add the "ask if missing" rule to the system prompt and "use only when…" to the tool docstring |
| Model error / 404 | Try `openai/gpt-oss-120b` in the `MODEL` line |
| Pydantic `ValidationError` inside the tool | Working as intended. The tool returns the message and the agent asks the customer to correct it |

## Before Day 5: the facts file
Write 15–20 facts about your business (policies, timings, delivery areas, FAQs) in a text file. Tomorrow the agent learns to search them (RAG) instead of carrying them all in the prompt.

Two ready examples are included. Use them as a pattern and replace every line with your own real facts:
- `sweet_crumbs_facts.txt` (20 facts for the bakery)
- `bright_minds_facts.txt` (19 facts for the tuition centre; the same lines are saved by the last cells of the notebook as `facts.txt`)

How to write good facts:
- **One fact per line**, each a complete sentence that names the business or the thing, so it makes sense on its own when searched.
- Cover prices, timings, policies, delivery areas, payment, cancellation and refunds, and common FAQs.
- Where the owner decides something, say so ("ask the owner"), so the agent never promises what it can't keep.
- Use real numbers and words customers use ("24 hours' notice", "Rs 1,500"), because search matches on them.
- The example facts beyond the prices and timings used in the lessons (payment, advance, cancellation, allergy and so on) are made up for practice. Replace them with your real policies.
