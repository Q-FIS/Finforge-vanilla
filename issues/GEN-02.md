# [GEN-02] Notebook: how the model behaves with no documents
labels: team:gen, size:S
**Owner:** G1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** the API key (use the `anthropic` package directly if GEN-01 isn't merged)

## In one sentence
Ask the model 10 financial questions with **no** documents, and record what it says and how much it varies.

## What to do
Create `notebooks/gen/closed_book.ipynb`:
1. Pick 10 questions about the 3 companies (use the question guideline once it exists).
2. Ask each one at temperature 0 and at 0.7, 5 times each.
3. Make a table: question · each answer · whether the answers changed · tokens in and out.
4. Count the tokens of one prompt yourself, and compare with what the API reports.
5. End with 3-5 sentences: how often did it make up a figure? Did temperature 0 give the same answer every time?

## Done when
- [ ] The notebook runs top to bottom, with the table and the summary
