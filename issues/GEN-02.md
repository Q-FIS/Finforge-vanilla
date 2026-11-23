# [GEN-02] Notebook: what the model does with no documents
labels: team:gen, size:S
**Owner:** G1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** the API key (use the `anthropic` package directly if GEN-01 isn't merged yet)

## What is this, in plain words?
Before we give the model any documents, we look at what it does **without**
them ("closed-book"). Does it know Infosys's FY2025 revenue? Does it make up
a number confidently? Does it give the same answer every time? This is why RAG
exists, and it's our first baseline.

## Step by step
Create `notebooks/gen/closed_book.ipynb`, with a markdown cell explaining each step:
1. Write 10 questions about our 3 companies' FY2024 and FY2025 figures (revenue, profit, employees...). Look up the right answers in the reports yourself and note them.
2. Ask each question with no documents: `client.messages.create(model="claude-haiku-5-5", max_tokens=1000, messages=[...])`. Ask each one **5 times**, at `output_config={"effort": "low"}` and again at `"medium"`. (This model doesn't accept a `temperature` setting.)
3. Make a table: question · correct answer · the 5 answers · how many were right · did the answers change between tries?
4. **Tokens:** for one question, print `response.usage.input_tokens` and `output_tokens`, and compare with `client.messages.count_tokens(model=..., messages=[...]).input_tokens`.
5. End with 3 to 5 sentences: how often did it invent a figure? Did it ever say it didn't know? Did repeating the same question change the answer?

## Done when
- [ ] The notebook runs top to bottom, with the table and your summary
