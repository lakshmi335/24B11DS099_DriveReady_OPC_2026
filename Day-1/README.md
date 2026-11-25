# Day 1 – How LLMs work and first API call
 
Notebook: `day1.ipynb` (runs in Google Colab)
Case study: **Sweet Crumbs Home Bakery** – a bot that answers customer questions.
 
## What this project does
Makes your first call to an LLM through the Groq API (OpenAI-compatible) and then explores how LLMs behave: temperature, hallucination, memory, and tokens.
 
## Setup
1. Get a free API key at <https://console.groq.com> → API Keys.
2. In Colab: click the 🔑 icon (left bar) → **Add new secret** → name `GROQ_API_KEY` → paste key → turn on **Notebook access**.
3. Never paste the key into code or push it to GitHub.
4. Upload the notebook (File → Upload notebook) and run cells top to bottom.
 
## Tasks in the notebook
| # | Task | Concept |
|---|------|---------|
| 1 | First API call (joke bot) | `client.chat.completions.create()` |
| 2 | Sweet Crumbs bot with facts + `temperature=0.2` | System prompt, `response.usage` |
| 3 | Same prompt 3× at temperature 0.2 and 1.2 | Temperature = creativity dial |
| 4 | Remove FACTS, ask "Do you deliver to Kakinada?" | Hallucination and the fix (facts + "not found" rule) |
| 5 | Separate calls vs one `messages` list | The model has no memory; code resends history |
| 6 | English vs Telugu question | Telugu uses more tokens |
| 7 | System prompt for your own business | Your 10% |
| Bonus | Chat loop that keeps history | Preview of Day 2 |
 
## Key ideas
- An LLM predicts the next token in a loop; it does not look answers up.
- Token ≈ ¾ of an English word; cost and limits are counted in tokens.
- Low temperature (0–0.3) for facts and prices; ~1.0 for creative text.
- The model is stateless: memory = your code resending the conversation.
- Context window = one budget for system prompt + history + documents + answer.
- Hallucination = plausible but wrong. Fix: give facts in the prompt (RAG-style) and allow "not found".
 
## Your code in one line
```python
client = OpenAI(api_key=userdata.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
resp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[...])
print(resp.choices[0].message.content)
```
 
## Common errors
| Error | Meaning | Fix |
|-------|---------|-----|
| `api_key client option must be set` | Key not loaded | Check secret name and Notebook access |
| `401 AuthenticationError` | Wrong/expired key | Create a new key |
| `404 model not found` | Old or misspelt model | `[m.id for m in client.models.list().data]` |
| `429 RateLimitError` | Too many requests | Wait and retry |
 
