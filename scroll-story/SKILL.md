---
name: scroll-story
description: Pace an explanation that animates as the reader scrolls or interacts: chapters as state changes, reading pauses, reader-controlled and reversible progress, predict-then-test experiments and reduced motion that keeps the meaning. Use when building or reviewing scrollytelling, a scroll-driven figure, an animated walkthrough or an interactive explainer in an article, docs page or landing page.
---

# Scroll story

Motion in an explanation shows a state change or a cause and its effect, and nothing else. It confirms what the text says; the page must still explain everything with motion off. A scroll story ties the figure's state to the reader's position in the text, so the reader sets the pace, can go back, and never waits for an animation to finish.

This skill is engine-neutral (CSS scroll timelines, a JavaScript timeline, a canvas or a video scrubbed by scroll). The figure itself follows [explanatory-figure](../explanatory-figure/SKILL.md); the article around it follows [tech-article](../tech-article/SKILL.md).

## Steps

### 1. Map chapters to states

Take the figure's storyboard and group its rows into chapters: one chapter carries one idea and covers one or more consecutive rows. The chapter's paragraph describes exactly what the figure does while that paragraph is on screen.

Give each chapter a scroll distance that follows its events, with a floor (enough to read the paragraph) and a cap (a long run of similar events is one idea, not a long chapter). Events that happen at the same time count once.

Done when every chapter has one idea, one paragraph and a distance within the floor and cap.

### 2. Build the clock

Apply every rule below. They make the figure a pure function of reading progress.

### 3. Add the experiment

Where the subject allows it, end with an interaction: ask the reader to predict, let them choose an input (where to cut the power, which value to insert), then show the consequence with the same figure vocabulary. Keep the prediction visible next to the result.

Done when the experiment uses the story's objects and colours, and works by pointer, touch, keyboard and in reduced motion.

## Rules

- **Purpose**: for each animation, name the state change or cause it shows. An animation without one is removed.
- **Plateaus**: each chapter plays its transition in the first part of its scroll distance (about 60 %), then holds the finished state while the reader reads.
- **Reader-paced**: motion follows scroll position or a control the reader moves. Anything that plays on its own gets play, pause and scrub, starts only when its figure is fully in view, and stops when it leaves.
- **Deterministic**: the figure's state depends only on progress. Seeking forwards, backwards or repeatedly to the same point gives the same frame. Resizing rebuilds the layout at the current progress.
- **Interruptible**: displayed progress eases toward the target with frame-rate independent smoothing (exponential, time constant around 0.1 s). Fast scrolling or clicking retargets the motion instead of queueing stale tweens, and rapid seeks still land on the true state.
- **Chapter boundaries from the scene**: the timeline reports where each chapter's transition ends, and the scroll mapping uses those times, so text and figure cannot drift apart.
- **A small motion vocabulary**: a handful of verbs (travel, roll, draw, retract, fade) and a small named set of easing curves: ease-out for things appearing, ease-in-out for things moving. Springs and overshoot only where the bounce itself means something. Reuse the page's easing tokens.
- **Ordinary scrolling**: the page scrolls at the reader's speed and some content always scrolls normally. The figure pins while its chapters pass; the page length stays constant; the wheel, trackpad gestures (including swipe-back), spacebar and Page Down keep working.
- **One change at a time**: stage simultaneous changes as a sequence the eye can follow, unless simultaneity is the point (several threads working at once).
- **Reduced motion keeps the meaning**: with `prefers-reduced-motion`, and with a visible motion toggle, the story jumps to each chapter's finished state. Large travel, parallax, flicker and rolls are replaced by short opacity or colour changes, so cause and effect still read. Automatic motion longer than five seconds can always be paused (WCAG 2.2.2).
- **Phones**: pin the figure at the top and let the chapter text scroll beneath it; use the figure's phone composition rather than a scaled desktop one.

## Completion

Verify in a real browser at desktop and phone sizes, and report the evidence:

- scrolling to each chapter's end lands on the boundary the scene reported;
- forward and reverse seeks give identical frames;
- the final state is correct with motion and in reduced mode;
- with all animation disabled, the page still explains the mechanism;
- keyboard scrolling (spacebar, Page Down) and the experiment work without a pointer;
- no horizontal overflow on a phone, and no console errors.

List what was not checked (other browsers, physical devices, frame rate under load, reader comprehension). The story is complete when every check above passes.
