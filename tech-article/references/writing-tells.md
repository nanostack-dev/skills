# Writing tells

A review list for wording that readers have learned to associate with machine-generated text, and that makes any text vaguer. Use it on a finished draft, after the cut pass. Each entry pairs a word or pattern with the plain alternative; the fix is usually a fact, a number or a deletion, rather than a synonym.

The list is for revising your own text. It cannot tell who wrote a page: people use every word below, and detectors built on such lists perform close to chance. Treat one hit as nothing and a cluster as a reason to rewrite the paragraph.

Run the checker for a first pass:

```bash
python3 tech-article/scripts/check_tells.py draft.md
```

It reports each hit with its line, and the rate per 10,000 words compared with a baseline measured on technical articles written by people before 2023. Words that those articles also use often are marked *context*: check the sentence, and keep the word when it carries meaning.

## Words and their plain replacements

### Inflated verbs

| Tell | Write instead |
| --- | --- |
| delve, delve into | look at, examine, or cut |
| underscore, highlight, emphasize | show, stress, or cut |
| showcase | show |
| foster | encourage, build |
| enhance, elevate | improve (and say by how much) |
| leverage, utilize, harness | use |
| streamline | simplify, or name what was removed |
| bolster | strengthen |
| garner | get |
| encompass | include |
| align with, resonate with | match, fit |
| prioritize | put first |
| facilitate | help, let |
| unlock, empower | let you |
| embark on | start |
| navigate (the complexities of) | handle |
| contribute to | cause, or cut |
| ensuring … (trailing) | so that …, or cut |
| reflecting / symbolizing … (trailing) | cut the clause |

### Dodging "is" and "has"

| Tell | Write instead |
| --- | --- |
| serves as, stands as, functions as, acts as | is |
| boasts, features, offers | has |
| represents | is |
| refers to (for a definition) | is |
| comprises | has, is made of |

### Intensifiers and vague praise

| Tell | Write instead |
| --- | --- |
| crucial, vital, essential, pivotal | name the effect, or cut |
| significant, key | give the number |
| robust | say what it survives |
| seamless, seamlessly | say what the reader no longer does |
| comprehensive | list what it covers |
| intricate, multifaceted | name the parts |
| nuanced | state the nuance |
| meticulous, meticulously | careful, or show the care |
| groundbreaking, renowned, cutting-edge, state-of-the-art | give the evidence |
| a diverse array of, a wide range of | many, or the count |
| vibrant, rich, profound, enduring | cut, or lasting |
| valuable insights | state the insight |

### Borrowed metaphors

| Tell | Write instead |
| --- | --- |
| landscape, realm, ecosystem (for a field) | field, area, or name it |
| tapestry | name the parts |
| testament to | shows |
| interplay | relationship, or say who affects whom |
| at the heart of, in the heart of, nestled, bustling | cut |
| setting the stage for, paving the way for | led to |
| focal point, cornerstone | center, or cut |
| game-changer | state the change |
| indelible mark, deeply rooted | cut |

### Adverbs and transitions

| Tell | Write instead |
| --- | --- |
| notably, importantly, interestingly, crucially | cut |
| remarkably, quietly, deeply, truly | cut |
| additionally, moreover, furthermore | and, also, or a new sentence |
| ultimately | cut, or "in the end" when it is the end |

### Fillers, hedges and sign-offs

| Tell | Write instead |
| --- | --- |
| it's worth noting that, it's important to note | cut |
| plays a crucial role in | say how |
| in today's fast-paced world, in the ever-evolving … | cut |
| let's dive in, a deep dive | cut |
| at its core | cut |
| think of it as, imagine a world where | state the thing |
| here's the kicker, the best part? | cut |
| experts say, studies show | name the source |
| based on available information | state what is known |
| potential, potentially | say when it happens |
| despite its challenges | state the problem |
| in conclusion, in summary, to sum up | cut, or a real conclusion |
| I hope this helps, happy coding, certainly! | cut |
| as of my last update | a date |

## Patterns

Patterns carry more signal than single words. Look for these:

| Pattern | Example | Fix |
| --- | --- | --- |
| Negative parallelism | "It's not just a queue, it's a contract." | State what it is |
| Rule of three | "fast, reliable and scalable" when only one is shown | Keep the items you can back with evidence |
| Trailing -ing analysis | "…, highlighting the need for care." | Cut the clause or make it a sentence with a subject |
| Punchy fragment reveal | "The result? A 40 % drop." | "Latency dropped by 40 %." |
| Stakes inflation | "This changes everything about testing." | Say what changes, for whom |
| One-line paragraphs for drama | A paragraph of one short sentence after every section | Merge into the paragraph it belongs to |
| Section summaries and tie-backs | "In this section we saw…", "As mentioned above…" | Cut; the heading and the text carry it |
| Preamble | "Before we begin, it's important to understand…" | Start with the first fact |
| Bold-header bullets | "- **Speed:** It is fast." in every list | Plain sentences, or a table with columns |
| Excess bold | Several bold phrases per paragraph | Bold at most the defined term |
| Title Case or Colon: Headings | "Scaling Runners: A Deep Dive" | Sentence case that names the topic |
| Symmetric pro and con blocks | Equal-length advantages and drawbacks for every option | Compare on the axes that decide, in a table |
| "Challenges and future outlook" ending | A closing section of vague hopes | End on the edge case or what the reader can try |
| Vague attribution | "Many developers find…" | Name who, or cut |
| Hedge stacks | "may potentially help to somewhat reduce" | One hedge, or a measured claim |
| Synonym cycling | runner, worker, agent, executor for one thing | One term per concept |
| Uniform rhythm | Every sentence 15–20 words, every paragraph three sentences | Vary length with the content |
| Sycophantic or chatty tone | "Great question!", "You've got this!" | Cut |
| Em dash in every paragraph | — | Commas, colons, parentheses or a full stop; a single dash is fine |
| Emoji in headings or bullets | 🚀 | Cut |

## How to use the list

1. Run the checker and read every hit in its sentence.
2. For each hit, ask what fact the word stands in for. Write the fact; when there is none, delete the word or the sentence.
3. Read the patterns table against the draft once, top to bottom.
4. Change a hit only when the replacement is clearer. A word from the list that is the precise term (a "key" in a map, a "robust" estimator, "significant" in a statistical sense) stays.

