# Day 2 – Prompts, memory and the Python agents need
 
Notebook: `Day2_Chatbot_Memory.ipynb` (runs in Google Colab)
Case study: **Sweet Crumbs Home Bakery** – the bot now follows rules, remembers the customer, returns structured data, and never crashes.
 
## What this project does
Turns the Day 1 single-call bot into a real chatbot and introduces the Python pieces used by every agent later: dicts/JSON, functions with type hints, decorators, and try/except.
 
## Setup
Same as Day 1: `GROQ_API_KEY` in Colab Secrets with Notebook access ON. The first cell installs `openai` and creates the client.
 
## Tasks in the notebook
| # | Task | Concept |
|---|------|---------|
| 1 | System prompt with Role · Facts · Rules · Format; run with and without RULES | Messages and roles, system prompt |
| 2 | Few-shot message classifier (order / question / complaint) | Examples fix the output format |
| 3 | Extract an order as JSON, parse with `json.loads` in try/except | Answers your code can use |
| 4 | `MENU` dict, `get_price()` with type hints, docstring and `@log_call` decorator | Dicts, functions, decorators |
| 5 | `safe_price()` catching `KeyError` | try / except |
| Build | Chatbot with history, trimming (`MAX_TURNS`) and error handling | Memory by hand |
| 10% | `MAX_TURNS = 2` memory experiment | Trimming makes the bot forget |
| 10% | Rebuild for your own business (example: tuition centre) | Your catalogue, function, SYSTEM prompt |
 
## Key ideas
- **Roles:** `system` = your instructions, `user` = the person, `assistant` = earlier model replies.
- **System prompt:** Role (who) · Facts (no guessing) · Rules (no risky promises) · Format (length/tone).
- **Few-shot:** 2–5 example question/answer turns make replies consistent.
- **JSON:** name every key, say "Return ONLY JSON", parse with `json.loads`, wrap in try/except.
- **Memory:** append user message → call with system + last N messages → append reply. Trimmed messages are forgotten.
- **Dicts:** `d[key]` crashes on a missing key; `d.get(key, default)` doesn't. Keys are exact, so normalise with `.lower().strip()`.
- **Functions:** one job, clear name, type hints, one-line docstring (on Day 4 the model reads these to pick tools).
- **Decorators:** `@deco` above `def f` means `f = deco(f)`.
- **try/except:** catch specific errors (`RateLimitError`, `APIConnectionError`, `KeyError`, `json.JSONDecodeError`); never `except: pass`.
## Test script for the chatbot
1. Say your name.
2. Ask for an eggless chocolate cake for tomorrow.
3. Ask the price for two (expected Rs 1,300).
4. Ask "what did I order?"
Expected: it remembers the name and order, quotes the right price, and never promises a delivery time.
 

 
