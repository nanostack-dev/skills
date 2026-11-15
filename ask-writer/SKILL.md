---
name: ask-writer
description: Ask which writing skill or flow fits a piece you want to write or review. A router over the article, documentation, figure, motion and wording skills in this repo.
disable-model-invocation: true
---

# Ask writer

A router over the writing skills. Before stating what a skill does or recommending a step be skipped, read that skill's SKILL.md: the summaries here are for orientation only.

A **flow** is a path through the skills. Pick the flow from what the reader will do with the page, then run its steps in order. Every flow ends with the same wording review.

## Which flow

| The reader wants to… | Flow |
| --- | --- |
| understand how or why one thing works | **Article** |
| learn, do a task, or look something up in a product | **Docs** |
| decide on a change before it is built | **Design** |
| learn what went wrong and what changed after an incident | **Incident** |
| see a figure or animation inside a page that already exists | **Figure only** |

## Article: one mechanism, explained

1. **`tech-article`** finds the question, the takeaway and the protagonist, verifies the mechanism against sources, and shapes the arc. Start here; its first step decides whether the piece is an article at all.
2. **`explanatory-figure`** for each figure the arc calls for: its question, its space, its storyboard, then the drawing rules.
3. **`scroll-story`** only when a figure changes state as the reader moves through the text. A static figure with a caption skips this step.
4. **Wording review**: run [writing-tells](../tech-article/references/writing-tells.md) and its checker on the draft.

The order of preference for examples (supplied pieces first) is set in `tech-article` step 4.

## Docs: tutorial, how-to, reference or explanation

1. **`tech-docs`** chooses the form and the reader first; one page is one form. A docs explanation that tells the story of one mechanism goes to the Article flow instead.
2. **`explanatory-figure`** for diagrams, with the caption written first.
3. **Wording review** with [writing-tells](../tech-article/references/writing-tells.md).

## Design: a change before it is built

1. **`design-change`** grounds the current system in evidence and shows the before and after.
2. **`change-map`** once the change is built: it turns the branch into a picture-first review page.
3. **Wording review** on the prose sections.

## Incident: a postmortem

1. **`postmortem`** builds the timeline, causes and actions from evidence.
2. A public write-up of the same incident is an Article: its question is the mechanism that failed, and the postmortem is its primary source.

## Figure only

**`explanatory-figure`**, then **`scroll-story`** if it moves. Read the surrounding page first: the figure answers a question that page asks.

## Underneath every flow

- **`real-world-examples`** supplies concrete, sourced cases when a draft leans on invented ones.
- **Writing tells** is the shared wording review, not a separate pass of its own: run it last, after the cut pass, and fix by adding facts rather than swapping synonyms.

The flow is complete when its last step's completion criteria pass.
