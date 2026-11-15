---
name: tech-article
description: Plan, write and review a technical article that teaches one mechanism through a concrete story and figures that carry the explanation. Use when writing, outlining or reviewing a tech article, engineering blog post, release deep-dive, docs explainer or "how X works" page.
---

# Tech article

A tech article earns its reader by answering one question they already have, through something they can watch happen. The reader follows one concrete thing (an order, eight numbers, a single request), predicts what will happen, sees the mechanism assemble, then tests their understanding. Only after that does the article name the idea and show how a real system does it.

Explaining is part of understanding. A passage that resists clear writing usually marks a gap in the writer's own model; go back to the sources instead of polishing the sentence.

The bar is the editorial quality of a high-end newspaper site: readable type, clear hierarchy, restrained colour, and figures that are part of the explanation. This skill is about approach and voice. Any stack works; the project's guide owns the tooling and its house style (publication name, kicker, length, banned words).

Two companion skills go deeper. Use [explanatory-figure](../explanatory-figure/SKILL.md) for every figure, diagram or illustration. Use [scroll-story](../scroll-story/SKILL.md) when a figure changes as the reader scrolls or interacts.

## Steps

### 1. Find the question

An article is an **explanation**: it builds understanding of how and why. Step-by-step tasks, tutorials and reference tables are different forms; link to them rather than mixing them in.

Write three lines before anything else:

- **Question**: the title, phrased as the question the reader already has. "When does a write become permanent?" beats "Understanding write-ahead logging". When a title is given, rephrase it as a question if it reads naturally. A number in a title carries its condition ("in about 20 seconds, on a test folder").
- **Takeaway**: the one-sentence answer the reader leaves with. Two sentences means two subjects; pick one.
- **Protagonist**: the concrete thing the reader follows from start to end: order #1042 marked paid, the list 38 27 43 3 9 82 10 19, one HTTP request. Realistic names and numbers. An example input may be invented when it is labelled as an example and the mechanism it runs through is checkable.

Done when all three lines exist and the takeaway is one sentence.

### 2. Verify the mechanism

List every factual claim the article will make, and check each against a source:

- primary: official docs, the source code, the spec, a measurement you ran;
- project: the owning project's facts file or the owner's notes (keep the path).

Decide what you simplify and write it down: it becomes a caption ("Table pages stay in memory in this example; the drawings show file roles, not separate devices").

When the claims that make up the mechanism itself cannot be sourced, stop here. List the gaps and ask the owner for the missing facts before shaping the arc; an article built on guessed mechanics teaches the guess.

Done when each claim has a source or a declared simplification, and any gap list has been answered or reported.

### 3. Shape the arc

Default arc, in order:

1. **Hook**: open on the point. State the question, the problem it solves and why it matters now (the context that prompted the piece). A dek, a one-line subtitle, promises the surprise: "A database can save your change before it saves your table." Make the reader care about the question before answering it.
2. **Follow one thing**: the protagonist moves through the mechanism. Start with one case the reader can understand completely. When the mechanism is a design, show the naive version first, let its flaw appear, then add one fix at a time. Ask the reader to predict before each reveal that matters.
3. **Name it**: give the idea its real name only after the reader has seen it work ("That is the idea behind write-ahead logging").
4. **The real system**: how a named, real system does it, with sources and exact conditions. When part 2 already ran on the real system, this part is the measurement and its conditions.
5. **Try it**: an experiment with the story's own objects. The reader predicts, then controls an input (where to cut the power, which value to insert) and sees the consequence; an open sandbox at the end lets them ask their own questions. Leave this part out when it would need unsourced numbers or would read as a promise ("your disk will take N seconds").
6. **The edge**: the subtle case, the cost or the limit ("'I didn't receive success' does not mean 'it didn't commit'"; the n × log₂ n area).
7. **Sources**: the references from step 2.

A **chapter** of part 2 carries one idea, shown by one or more consecutive storyboard rows of the figure.

Done when every chapter has one idea and one short paragraph, and the parts left out are left out for a stated reason.

### 4. Write in the voice

Calibrate on exemplars before drafting, in this order of preference: pieces the user or project supplies; the project's own published articles; the pre-2023 list in [exemplars](references/exemplars.md); general knowledge last. Read two of them for how they open, pace and name things; borrow the approach, never the wording.

- **Show, then name**: the reader meets the thing before its term; jargon arrives as a label for something already seen.
- **Plain words** even on hard topics: the audience includes non-native readers and newcomers. Strong verbs with a real subject ("The database writes the record", "You mark the order paid").
- **Tense**: present for the mechanism, past for measurements ("took 20–23 s on the test folder").
- **Numbers, not adjectives**: replace "fast", "huge", "efficient" with the measured value and its condition.
- **More examples than feels natural**, each realistic and complete (a full input and its output, not `foo`), each attached to a claim as in [real-world-examples](../real-world-examples/SKILL.md).
- **Terms are an interface**: define each term once, then use exactly that word in the text and in the figure labels. Bold a term where it is defined.
- **Reasoning on the page**: show why, name the alternative you rejected, and mark uncertainty where it lives ("I'm not sure this holds for network file systems"). Say what is simplified, and claim only what you checked ("whether readers learn more from this is untested").
- **Skimmable**: each paragraph leads with its claim. Flag the hard part before the reader reaches it ("This next step is the subtle one").

Done when every paragraph passes these rules.

### 5. Make the figures

For each figure, follow [explanatory-figure](../explanatory-figure/SKILL.md). For chapters that animate with scroll or respond to input, follow [scroll-story](../scroll-story/SKILL.md).

Done when each figure answers a stated question and has a caption that says what it shows and what it simplifies.

### 6. Compose the page

- Type: a comfortable body size (about 19–21 px on desktop) and a measure of 60–75 characters; one title treatment, one subhead treatment, a small category kicker.
- Colour: a restrained palette where each colour means one thing across every figure.
- Phones: recompose figures for the narrow screen; keep text size and label legibility.

Done when the page reads well at desktop and phone width, with no horizontal scrolling.

### 7. Review

Run every check and keep the evidence (screenshots or notes):

- **Cold read**: read the page as someone who knows only what is written. Add every step your head supplied silently.
- **Cut pass**: delete announcements ("In this article we will…"), repeated points and decoration. Most editing is cutting.
- **Figures only**: a reader who only looks at the figures can state the takeaway.
- **Motion off**: with animation disabled, the text and the static figures still explain the whole mechanism.
- **Sources**: every claim from step 2 is sourced or declared as simplified.
- **Voice**: step 4's rules hold on every paragraph.
- **Wording**: run `python3 scripts/check_tells.py <draft>` from this skill's folder and work through [writing-tells](references/writing-tells.md); fix each hit with a fact, a number or a deletion.
- **Reach**: desktop and phone screenshots, reduced motion, keyboard access to every interaction.

The article is complete when every check passes and the final report lists the evidence and what was not checked (other browsers, real devices, reader comprehension).

The sources behind these rules are in [the research record](../docs/research/2026-11-15-tech-article-sources.md).
