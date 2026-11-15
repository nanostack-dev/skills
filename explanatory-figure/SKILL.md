---
name: explanatory-figure
description: Design and review diagrams, infographics and interactive figures that explain a mechanism: every mark maps to one thing, objects keep their identity, space carries meaning, connectors stand for real relationships and the reader can test their own cases. Use when drawing a technical diagram, architecture or data-flow figure, algorithm illustration, infographic or explorable, or when a figure's arrows and links feel improvised or decorative.
---

# Explanatory figure

A figure explains when a reader who only looks at it can tell what happens and why. A premium-looking frame does not make a diagram premium: the geometry has to say something true about the mechanism. The usual failure is boxes joined by arrows drawn between arbitrary corners, where nothing tells the reader what moved, what stayed, or what changed state.

This skill is tool-neutral (SVG, canvas, a 3D render, a slide). It is used by [tech-article](../tech-article/SKILL.md) for each figure, and by [scroll-story](../scroll-story/SKILL.md) when the figure animates.

## Steps

### 1. Ask the figure's question

Write the one question this figure answers ("Which part of the change survives a power cut?", "How many comparisons does each merge need?"). Choose the encoding that answers that question; a figure that answers no question is decoration.

Done when the question is written in one sentence.

### 2. Compose the space

Give every region of the canvas a meaning before placing objects: memory versus permanent storage, one row per level of recursion, one lane per thread. Changes of state become movements across those boundaries.

When the mechanism needs two axes that compete (zones and a time axis, say), give the main canvas the axis that shows the takeaway, and put the other in a second view linked to the first.

Done when you can say what each zone, row, lane or axis means.

### 3. Storyboard the states

Write a table: one row per state, with what changed, which objects changed, and where they are now. A row holds one change, which may apply to several objects at once (three threads each take a folder). For a write-ahead log: the order page changes in memory → a log record is built → the record and its commit reach storage → power is cut and memory is erased → recovery replays the record into the table.

Done when each row has one change and names its objects and their zones.

### 4. Draw against the rules

Apply every rule below, then check them one by one.

## Rules

- **Encoding**: every mark maps to exactly one thing, and the caption says so ("each square is a byte", "each dot is one float"). Remove marks that map to nothing.
- **All state shown**: whatever drives the next step is visible (the read cursor, the counter, which values are in memory). Hidden state forces the reader to simulate it in their head.
- **Identity**: one object is one thing from the first state to the last. It travels, rolls or changes colour; it does not fade out and reappear as a new shape. The reader should be able to follow the record chip from the table page into the log and see it stay there.
- **Meaning in space**: a state change is a crossing. A record becomes durable when it crosses from the memory zone into the storage zone, and its outline turns from dashed to solid as it crosses.
- **Connectors**: draw a link only for a real relationship, and attach it where that relationship lives (the row's edge, a port, the field being compared). Routes leave and enter on level (horizontal) or upright tangents, so direction reads at a glance. A moving object's trail is its own path: drawn beneath the cards, visible only between the two things it joins, then retracted into the destination.
- **Honest metaphors**: say "copy" when it is a copy. A replay is a distinct object (a solid blue copy) travelling to the table while the source record stays in the log. Disclose the model behind the figure, and put every simplification in the caption.
- **One action, one mark**: each event gets exactly one visual mark. One comparison is one arc between the two values compared; a counter shows the true count.
- **States change in place**: a value changes by rolling inside its cell, like a split-flap display ("pending" rolls to "paid"). Old and new values never overlap in a crossfade.
- **Concrete and summary together**: pair the fully concrete case with a summary view (all time at once, the totals, the shape of the cost), changing together so the reader can climb between them. Each level shows different information, not the same picture smaller.
- **Static beside motion**: an animation shows change; a static view allows close inspection and comparison. Give the reader both: the finished states, or an all-time view of the run.
- **The reader's own cases**: when a variable matters (input size, failure point, number of threads), make it a control the reader can drag, scrub or toggle, so they can test cases the author did not pick. The grabbed point stays under the pointer; touch and keyboard work too.
- **Derived from data**: when the mechanism is an algorithm, run it, record each event, and draw from that record. Changing the input then changes the figure correctly.
- **The ending shows the result**: the last state summarises what it cost or proved: dashed outlines of every position each number passed through, with dimension lines labelled n wide and log₂ n deep.
- **Labels**: each label is attached to its object and moves with it, uses the article's term for it, and is legible at phone size.
- **Colour**: few colours, one meaning each, consistent across every figure, with a second channel (shape, pattern, label) so colour is never the only signal.
- **Projection**: flat 2D first. Use isometric or 3D only when depth itself carries meaning.
- **Phones**: recompose rather than shrink. Shorten rows, drop secondary columns and metadata labels, or stack zones vertically. Sixteen values need a different layout, not smaller tiles.
- **Static form**: every state has a readable static version with a caption, for print, reduced motion and screen readers.

## Completion

The figure is complete when:

- every rule above has been checked against it, with the result noted;
- a watch-only test passes: someone who reads none of the text can retell the storyboard and answer the figure's question;
- desktop and phone screenshots exist and labels are legible in both;
- any control works by pointer, touch and keyboard;
- the caption states what the figure shows, what each mark means and what it simplifies.
