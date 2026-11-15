---
name: tech-docs
description: Write and review technical documentation by first choosing its form (tutorial, how-to guide, reference or explanation) and then applying that form's rules, runnable samples and a page checklist. Use when writing or reviewing docs pages, READMEs, guides, API or CLI reference, getting-started pages, or when a docs page mixes teaching, steps and reference.
---

# Tech docs

Documentation serves four different needs, and each needs its own form. A page that tries to teach, list every option and walk through a task at once does all three badly. Choose the form first; the rules follow from it.

| The page informs… | …a reader who is… | Form |
| --- | --- | --- |
| action | studying | **tutorial** |
| action | working | **how-to guide** |
| knowledge | working | **reference** |
| knowledge | studying | **explanation** |

An explanation that teaches one mechanism through a story is an article: use [tech-article](../tech-article/SKILL.md) for it. Figures follow [explanatory-figure](../explanatory-figure/SKILL.md).

## Steps

### 1. Choose the form and the reader

Name the form with the table above, and the reader by role and what they already know ("a backend developer who has written HTTP tests, new to Echopoint"). Write for that one reader. When the content you have spans several forms, split it into pages and link them.

Done when the page's form and reader fit in one sentence each.

### 2. State the frame

The first lines say what the page covers, what it leaves out, and what the reader needs before starting (accounts, versions, installed tools), in the order they need them.

Done when a reader can tell from the opening whether this page is for them and whether they are ready.

### 3. Write to the form

Apply the rules of the chosen form, below.

### 4. Make every sample real

Every command and code sample is copied from something that ran. It is self-contained (dependencies, environment variables and setup shown), uses realistic names and data, and shows its expected output. Comments explain the non-obvious why. Where readers commonly go wrong, show the wrong version labelled as wrong. A sample you could not run is marked unverified.

Done when every sample has been run or marked.

### 5. Review

Compare the page with a strong example of the same form, in this order of preference: one the user or project supplies, the project's own docs, then the documentation exemplars in [exemplars](../tech-article/references/exemplars.md). Run the checklist at the end of this file, then a cut pass: remove each sentence that can go without loss.

## Forms

### Tutorial: a first success by doing

- Open with what the learner will build, then a complete working example and its output early on.
- Every step produces a visible result. Prompt the learner to look ("Notice that the run now shows two passed assertions").
- One path only: no options, alternatives or theory; link to the explanation instead.
- Steps are safe to repeat, and likely failure points are flagged before the learner reaches them.
- Voice: "we", with an unambiguous sequence ("First, create the flow. Now, run it.").
- End by saying what the learner has built and where to go next.
- Usual mistake: teaching by explaining, or offering choices, so the steps stop reliably reaching the promised result. Test it with someone new.

### How-to guide: a task done right

- Title it with the reader's goal: "How to run flows in CI", not "CI integration".
- Start from the task or problem; assume a competent reader and skip what they already know.
- Imperative steps in the order the reader works, with conditionals where real setups vary ("If your API needs a token, add it as a secret first").
- Leave out teaching and exhaustive options; link to reference and explanation.
- Usual mistake: drifting into a tutorial, or following the product's menus instead of the reader's goal.

### Reference: the facts, consulted while working

- Describe the machinery only: commands, flags, fields, defaults, limits, errors, warnings, each with a short usage example.
- Mirror the product's own structure, and use the same pattern for every entry so readers find things where they expect them.
- Neutral, exact wording; no instruction, opinion or marketing.
- Usual mistake: generated reference left bare, or entries that wander into how-to steps.

### Explanation: why things are the way they are

- Bound it with a real "why" question; give context, design decisions, constraints, alternatives and trade-offs.
- Examples before abstraction; name the conceptual obstacle and what to think instead.
- Discuss and judge ("We chose X because…; teams that need W use…"); link to related explanations.
- Usual mistake: facts with no reasons, or steps and reference creeping in.

## Writing rules for every form

- **First success fast**: the most important information first; readers decide within a few sentences whether to stay.
- **Headings**: say what the reader is doing or looking up; the headings alone outline the page; at most three levels; a sentence under every heading.
- **Paragraphs**: one idea each, its point in the first sentence. No previews or recaps of the page, and no "simply", "just" or "easy".
- **Lists and tables**: numbered lists for ordered steps, each starting with a verb; bullets for unordered items; tables for anything with several attributes, with a header on every column and short cells. Introduce each list or table with a sentence.
- **Terms**: one name per concept, defined once in a sentence; drop jargon that adds no meaning.
- **Diagrams**: write the caption first, one message per diagram, the caption below it states the takeaway.
- **Maintenance**: docs are never finished. Improve one page at a time and publish each improvement; keep samples under test so they stay true.

## Confusing patterns and their fixes

| Pattern | Fix |
| --- | --- |
| Assumed knowledge that readers lack, or that varies across the page | Write to the one reader from step 1; test with someone new |
| Too many new concepts at once | Introduce one at a time |
| Starting abstract | Start from something concrete the reader knows |
| Toy examples (`foo`, `bar`) | Real data and a real use case |
| A claim with no example | Add one the reader can check |
| An analogy stretched across many points | Use it for one point only |
| A wrong approach shown without a label | Say first that it is a mistake, an experiment or a story |
| "What" without "why" | Say why someone would choose this |
| Missing key information | Have someone who knows the system review for gaps |

## Checklist

The page is complete when every check passes:

1. Its form is clear in one sentence, and nothing from another form is mixed in.
2. Reader, scope, non-scope and prerequisites are stated at the top.
3. Title and headings name tasks or topics accurately and outline the page.
4. A first useful result appears early, with its expected output.
5. Every sample ran (or is marked unverified), copies as-is and uses realistic data.
6. Paragraphs carry one idea each, point first, with no meta-writing.
7. Steps are numbered and imperative; data with several attributes is in tables.
8. Terms are consistent and defined once.
9. None of the confusing patterns above applies.
10. Each diagram has one message and a caption with the takeaway.
11. It links to the next step and to related reference or explanation.
12. The wording passes the review in [writing-tells](../tech-article/references/writing-tells.md) and its checker script.

The sources behind these rules are in [the research record](../docs/research/2026-11-15-tech-article-sources.md).
