# Start here: read this before your issue

This page explains what we are building, how the pieces fit, the words we
use, and how to work on an issue. It takes about 15 minutes. Read it before
you open your own issue file.

---

## 1. What are we building?

A program that answers questions about Indian companies' annual reports, and
**shows where in the report the answer came from**.

> **Question:** "What was Acme's standalone profit for the year in FY2025?"
> **Answer:** "₹16,900 crore [C1]"  (C1 = page 4, Standalone Statement of Profit and Loss)

An annual report is 300+ pages. A language model (an "LLM", like ChatGPT or
Claude) can't read all of it for every question, and if you ask it without the
report it often **makes up** figures. So we do it in two halves:

1. **Find** the few passages of the report that contain the answer (this is called *retrieval*).
2. **Give** only those passages to the LLM, and tell it to answer **only** from them, citing each one.

Find, then generate: that's why it's called **RAG**, *Retrieval-Augmented Generation*.
"Vanilla" means the plain, basic version, with no extra tricks. We build every
part by hand so we understand it, then check it against a well-known library.

---

## 2. Follow one question through the system

The fake report in `tests/fixtures/acme_ar_fy2025.pdf` has 6 pages. Page 4 is
the standalone profit and loss table. Here is what each step does with it.

**Steps 1-5 happen once, before any question (building the "index"):**

| Step | Team | What happens | Example |
| --- | --- | --- | --- |
| 1. Parse | REP | Read the PDF into pages and text blocks | Page 4 has the block "Profit for the year", the block "16,900", ... |
| 2. Clean | REP | Remove repeated headers, fix broken words | The header "Acme Industries Limited \| Annual Report 2024-25" is removed |
| 3. Chunk | REP | Cut the text into pieces of up to 512 tokens | Chunk `acme_ar_fy2025:p4:c0003` = the page-4 table |
| 4. Metadata | REP | Label each chunk | company=acme, fy=FY2025, basis=standalone |
| 5. Embed | REP | Turn each chunk into a vector (384 numbers) | `[0.021, -0.113, 0.054, ...]` |

**Steps 6-10 happen for every question:**

| Step | Team | What happens | Example |
| --- | --- | --- | --- |
| 6. Retrieve | RET | Find the chunks most similar to the question | Rank 1: the page-4 chunk (score 0.82). Rank 2: the page-3 chunk (0.79) |
| 7. Context | GEN | Put the top 5 chunks into the prompt, tagged | `[C1] Acme · FY2025 · standalone · p. 4` then the text |
| 8. Generate | GEN | Ask the LLM; it replies in JSON | `{"status": "answered", "answer": "₹16,900 crore [C1]", ...}` |
| 9. Check | GEN | Check the citations with plain code | Is "16,900" really in passage C1? Yes |
| 10. Score | EVAL | Compare with the correct answer | Correct. (If wrong: which step failed?) |

Notice the trap in step 6: the **consolidated** profit (page 3, 18,200) looks
almost the same as the **standalone** one (page 4, 16,900). Telling apart years,
companies and standalone vs consolidated is the hardest part of this project.

**`src/rag/run.py` runs all 10 steps.** Try it now with fake models (no
download, no API key):

```bash
uv run python -m rag.run --config tests/ci.yaml --name smoke --overwrite
```

Then open `.cache/runs/smoke/results.jsonl` to see what happened to each question.

---

## 3. What a "stub" is, and why everything already runs

Every function in the pipeline already exists, but most of them are **stubs**:
they have the right name, inputs and output type, but return fake data. For
example, today `parse_pdf()` returns one fake page that says "STUB page text".

That's on purpose. Because every function exists, the whole pipeline runs
from day 1. **Your job is to replace your stub with real code**, without
changing its name or its inputs and outputs (other teams call it).

Find your stub with:
```bash
grep -rn "STUB(REP-01)" src/      # use your own issue id
```

---

## 4. Words we use

| Word | Meaning |
| --- | --- |
| **Token** | A piece of a word that a model reads. "consolidated" might be 2 tokens; "₹1,45,000" might be 6. Models have a maximum number of tokens they can read. |
| **Chunk** | A piece of the report (a few paragraphs, or one table) that we search over. |
| **Embedding / vector** | A list of numbers (384 of them, for us) that represents a text's meaning. Texts with similar meanings get similar vectors. |
| **Similarity / score** | How close two vectors are. We use the *dot product*; because our vectors have length 1, this is the same as *cosine similarity*. Higher = more similar. |
| **Retrieval / top-k** | Finding the k chunks most similar to the question (k = 5 for us). |
| **TF-IDF** | An older way to search, by counting matching words. Rare words count more. It's our comparison ("baseline"). |
| **Prompt** | Everything we send to the LLM: instructions + passages + question. |
| **Context** | The passages we put in the prompt, tagged [C1], [C2], ... |
| **Citation** | The model saying which passage a fact came from, like [C1]. |
| **Hallucination** | The model stating something that isn't in the passages. We catch invented numbers with code. |
| **Standalone vs consolidated** | *Standalone* = the parent company alone. *Consolidated* = the parent plus all its subsidiaries. Annual reports contain both, with different figures. |
| **FY2025** | Financial year April 2024 to March 2025. |
| **Crore / lakh** | 1 crore = 10,000,000 (1,00,00,000). 1 lakh = 100,000 (1,00,000). Indian grouping puts commas differently: 1,45,000 = 145,000. |
| **(1,234)** | In financial tables, brackets mean **negative**: -1,234. A dash "—" means **nil** (zero). |
| **Fixture** | A small, fixed test file we use in tests (our fake Acme report). |
| **Evidence / quote** | The exact words in the report that answer a question. Every eval question records them. |
| **Dev / test questions** | We tune the system on "dev" questions. "Test" questions are locked and only used at the very end, so we can't fool ourselves. |
| **Run / run folder** | One execution of the pipeline on all questions; its results are saved in `eval/runs/<name>/`. |
| **Noise floor** | How much scores change when we run the *same* thing twice. Smaller differences don't mean anything. |
| **Oracle** | "Perfect information" for comparison, e.g. handing the model the true evidence. It shows the best possible result. |

---

## 5. Where things are

```
src/rag/schema.py     the shared data types: Document, Page, Block, Chunk, Hit, Answer, ...
src/rag/config.py     reads config.yaml (every setting lives there)
src/rag/match.py      "is this quote in this text?", shared by everyone
src/rag/amounts.py    "is this the same amount of money?", shared by everyone
src/rag/rep/          Team 1: parse, clean, tokens, chunking, metadata, embed
src/rag/ret/          Team 2: tfidf, retrieve, filters, metrics
src/rag/gen/          Team 3: llm, context, generate, citations
src/rag/run.py        runs the whole pipeline (Team 4)
tests/fixtures/       the fake Acme report, its expected output, sample questions
tests/rep|ret|gen/    put your team's tests here
issues/               every task, written out
```

**Read `src/rag/schema.py` first.** It's the most important file: it defines
what every step receives and returns.

---

## 6. How to work on your issue, step by step

```bash
# 0. Once: install everything
uv sync
uv run pre-commit install

# 1. Get the latest code and make a branch for your issue
git switch main
git pull
git switch -c rep/REP-01-parser          # <team>/<issue id>-<short name>

# 2. Find what to replace
grep -rn "STUB(REP-01)" src/

# 3. Write code and tests. Run the tests often:
uv run pytest                            # all tests
uv run pytest tests/rep/test_parse.py    # just yours

# 4. Check the whole pipeline still runs
uv run python -m rag.run --config tests/ci.yaml --name smoke --overwrite

# 5. Save and share your work
git add -A
git commit -m "REP-01: parse PDF pages into blocks"
git push -u origin rep/REP-01-parser
# then open a Pull Request (PR) on GitHub, and write "Closes #<issue number>"
```

When you commit, the pre-commit hook formats your code automatically. If it
changes something, just `git add -A` and commit again.

**Your PR merges when:** the tests pass on GitHub (CI) + a teammate approves
(it's correct) + a fresher signs off (they understood it). Answer the 5
questions in the PR template; the fresher will ask you about them.

---

## 7. Rules

1. **Don't change a public function's name or its inputs and outputs.** Other teams call it. If you think it must change, ask the lead first.
2. **Settings go in `config.yaml`, not in your code.** No numbers like 512 hard-coded in a function.
3. **Test with the fixtures** (`tests/fixtures/`), not with another team's unfinished code.
4. **If you can't explain a line, it doesn't merge.** You may use AI to explain, review and debug, but you must understand every line you submit.
5. **Never commit PDFs, API keys, or anything in `data/cache/`.**
6. **Stuck for more than an hour?** Ask in the team channel: say what you tried and paste the error. Stuck for a day? Tell the lead. That's normal, not a failure.
