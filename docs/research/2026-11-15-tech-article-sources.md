# Research: sources for the tech-article skills

Date: 2026-11-15. Scope: the [tech-article](../../tech-article/SKILL.md), [explanatory-figure](../../explanatory-figure/SKILL.md), [scroll-story](../../scroll-story/SKILL.md), [tech-docs](../../tech-docs/SKILL.md) and [ask-writer](../../ask-writer/SKILL.md) skills, the [writing tells](../../tech-article/references/writing-tells.md) list and the [exemplars](../../tech-article/references/exemplars.md).

The skills started from Trame, Nanostack's experiments in visual technical articles (a write-ahead-log article, a recovery motion study and a merge sort article). This record lists the outside sources used to improve them, what each source changed, and the findings of a dry run on a real topic.

## Method

- **Selection**: essays and articles discussed on Hacker News, in three areas: writing, visual explanation, and motion and scrolling. Most threads have 50 points or more; the exceptions are marked.
- **Verification**: each Hacker News thread was found through the Algolia HN API. Each article was fetched and lessons were taken from it, except two marked entries whose lessons come from the HN comments.
- **Caveat**: quotes were extracted through a summarising fetch. The skills paraphrase the lessons and do not quote the sources.
- **Dry run**: an agent with no other context followed the first draft on a Notes topic ("Reading 5 million files with one thread per core", Cadastre facts only) and reported every ambiguous, contradictory or no-op line.

## Sources

### Writing (10)

| # | Source | HN thread | Lesson used |
| --- | --- | --- | --- |
| W1 | [Write Simply](http://paulgraham.com/simply.html), Paul Graham | [484 pts, 2021](https://news.ycombinator.com/item?id=26423090) | Plain words even on hard topics, for a mixed and non-native audience; editing is mostly cutting. |
| W2 | [Putting Ideas into Words](http://paulgraham.com/words.html), Paul Graham | [209 pts, 2022](https://news.ycombinator.com/item?id=30313438) | Review as a neutral reader with only the page; writing exposes what you did not understand. |
| W3 | [Research Debt](https://distill.pub/2017/research-debt/), Olah and Carter (Distill) | [508 pts, 2017](https://news.ycombinator.com/item?id=13932806) | Good explanation transforms the idea; notation and terms are an interface; an idea you cannot explain well is one you do not yet understand. |
| W4 | [Diátaxis](https://diataxis.fr/), Daniele Procida | [514 pts, 2024](https://news.ycombinator.com/item?id=42325011) | An explanation is one of four forms; keep tutorials, how-tos and reference out of it. |
| W5 | [Some tactics for writing in public](https://jvns.ca/blog/2023/08/07/tactics-for-writing-in-public/), Julia Evans | [566 pts, 2023](https://news.ycombinator.com/item?id=37033403) | Say why you are writing; name the alternatives you rejected; mark uncertainty where it lives. |
| W6 | [Some thoughts on writing](https://danluu.com/writing-non-advice/), Dan Luu | [150 pts, 2021](https://news.ycombinator.com/item?id=29545839) | Use more examples than feels natural; show reasoning, not only conclusions. |
| W7 | [How to write technical posts so people will read them](https://reasonablypolymorphic.com/blog/writing-technical-posts/), Sandy Maguire | [257 pts, 2020](https://news.ycombinator.com/item?id=23840787) | Motivate with the problem before the solution; one paragraph, one idea; flag the hard parts in advance. |
| W8 | [Technical Writing: Learning from Kernighan](https://entropicthoughts.com/technical-writing-learning-from-kernighan.html), Entropic Thoughts | [180 pts, 2018](https://news.ycombinator.com/item?id=17151560) | Realistic, complete examples (full input and output); brevity is a cost the writer pays. |
| W9 | [Notes on Technical Writing](https://mkaz.blog/misc/notes-on-technical-writing/), Marcus Kazmierczak | [414 pts, 2020](https://news.ycombinator.com/item?id=21955306) | Cut the preamble; invite the reader to try things. |
| W10 | [Technical Writing One: clear sentences](https://developers.google.com/tech-writing/one/clear-sentences), Google | [571 pts, 2020](https://news.ycombinator.com/item?id=22652241) | Strong verbs with a real subject; numbers instead of adjectives. |

### Visual explanation (11)

| # | Source | HN thread | Lesson used |
| --- | --- | --- | --- |
| V1 | [Up and Down the Ladder of Abstraction](https://worrydream.com/LadderOfAbstraction/), Bret Victor | [733 pts, 2011](https://news.ycombinator.com/item?id=3099595) | Give the reader control of the independent variables; insight comes from moving between concrete and abstract views; a static all-time view can replace a time slider. |
| V2 | [Visualizing Algorithms](https://bost.ocks.org/mike/algorithms/), Mike Bostock | [1557 pts, 2014](https://news.ycombinator.com/item?id=7949995) | Design the figure for a specific question; pair animation with a static view for close inspection; subtract marks that carry nothing. |
| V3 | [Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles/), Hohman et al. (Distill) | [100 pts, 2020](https://news.ycombinator.com/item?id=24535144) | Animation works for state transitions; ask for a prediction before the reveal; play, pause and scrub let readers set their pace. |
| V4 | [Learnable Programming](https://worrydream.com/LearnableProgramming/), Bret Victor | [1080 pts, 2012](https://news.ycombinator.com/item?id=4577133) | All state is shown or eliminated; start from one specific case, entirely understood. |
| V5 | [Explorable Explanations](https://worrydream.com/ExplorableExplanations/), Bret Victor | [91 pts, 2016](https://news.ycombinator.com/item?id=12283929) | Let readers change parameters; linked representations of one system; disclose the model behind the figure. |
| V6 | [How I Make Explorable Explanations](http://blog.ncase.me/how-i-make-an-explorable-explanation/), Nicky Case | [27 pts, 2017](https://news.ycombinator.com/item?id=15326045) (below the 50-point bar, kept as a practitioner process essay) | Give a concrete experience first; make the reader love the question; end with a sandbox. |
| V7 | [Memory Allocation](https://samwho.dev/memory-allocation/), Sam Rose | [1360 pts, 2023](https://news.ycombinator.com/item?id=36029087) | Naive version first, expose its flaw, add one fix at a time; a time slider; each square is a byte. |
| V8 | [Exposing Floating Point](https://ciechanow.ski/exposing-floating-point/), Bartosz Ciechanowski | [87 pts](https://news.ycombinator.com/item?id=47908139) (2026 repost of a 2019 article) | Build in layers from first principles; every dot is one float; an alternative for readers who cannot rely on colour. |
| V9 | [LLM abstraction levels inspired by fish eye lens](https://wattenberger.com/thoughts/fish-eye), Amelia Wattenberger | [261 pts, 2024](https://news.ycombinator.com/item?id=42308303) | Each zoom level carries different information; keep context around the focus. |
| V10 | [Science-based games and explorable explanations](https://p.migdal.pl/blog/2024/05/science-games-explorable-explanations/), Piotr Migdał | [68 pts, 2024](https://news.ycombinator.com/item?id=41648048) | Embedded simulations let readers challenge the author's assumptions. |
| V11 | [Draggable objects](https://www.redblobgames.com/making-of/draggable/), Amit Patel (Red Blob Games) | [1059 pts, 2023](https://news.ycombinator.com/item?id=37703291) | Interaction feel decides whether a figure is usable: the grab point stays under the pointer, touch works. |

### Motion and scrolling (10)

| # | Source | HN thread | Lesson used |
| --- | --- | --- | --- |
| M1 | [How To Scroll](http://bost.ocks.org/mike/scroll/), Mike Bostock | [233 pts, 2014](https://news.ycombinator.com/item?id=8551724) | Reveal by scrolling rather than clicking; keep some content scrolling normally; no autoplay on entering the viewport. HN comments: keep page length constant; fixed overlays break spacebar and Page Down. |
| M2 | [You Don't Need Animations](https://emilkowal.ski/ui/you-dont-need-animations), Emil Kowalski | [546 pts, 2025](https://news.ycombinator.com/item?id=45139088) | Every animation needs a named purpose; skip it for frequent and keyboard actions. HN comments: motion should confirm, not carry, the information. |
| M3 | [Allow disabling of motion or animation](https://accessibilityfordevelopers.com/allow-disable-of-motion-animation/), Accessibility for Developers | [214 pts, 2022](https://news.ycombinator.com/item?id=33222434) | A visible control plus `prefers-reduced-motion`; WCAG 2.2.2 for automatic motion over five seconds. |
| M4 | [An Interactive Guide to CSS Transitions](https://www.joshwcomeau.com/animation/css-transitions/), Josh Comeau | [309 pts, 2021](https://news.ycombinator.com/item?id=26274516) | Ease-out for things entering; quick entrances. |
| M5 | [Springs and bounces in native CSS](https://www.joshwcomeau.com/animation/linear-timing-function/), Josh Comeau | [273 pts, 2025](https://news.ycombinator.com/item?id=45736461) | Springs only where overshoot matters; a small named set of timing functions. |
| M6 | [My favourite animation trick: exponential smoothing](https://lisyarus.github.io/blog/posts/exponential-smoothing.html), lisyarus | [675 pts, 2024](https://news.ycombinator.com/item?id=39637487) | Ease toward a target each frame: interruptible, frame-rate independent, no stale queued motion. |
| M7 | [Snow Fall](http://www.nytimes.com/projects/2012/snow-fall/), The New York Times | [525 pts, 2012](https://news.ycombinator.com/item?id=4950054) (lessons from HN comments) | Scroll-triggered animation that starts before its content is in view annoys readers; media works when it complements the text. |
| M8 | [When animation is an accessibility problem](https://www.theverge.com/23191768/animation-accessibility-neurodivergence), The Verge | [56 pts, 2022](https://news.ycombinator.com/item?id=32081528) (article blocked; lessons from HN comments) | Reduced motion means shorter and subtler motion, not necessarily none. |
| M9 | [Designing Safer Web Animation for Motion Sensitivity](https://alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity/), Eric Bailey (A List Apart) | [2 pts, 2022](https://news.ycombinator.com/item?id=32156785) (thin thread, kept for the accessibility evidence) | Large movement, parallax and scrolljacking are the main triggers; opacity and colour changes are safer. |
| M10 | [Scroll-Driven Animations](https://scroll-driven-animations.style/) | [62 pts, 2025](https://news.ycombinator.com/item?id=42989635) (lessons from HN comments) | Many sites ignore reduced motion; scroll effects can break trackpad swipe-back. |

V1 and V3 were also found by the motion search, where they supplied the "static all-time view" and "play, pause and scrub" lessons. They are counted once: 31 sources in total.

### Documentation (4)

| # | Source | Discussion | What it changed |
| --- | --- | --- | --- |
| D1 | Daniele Procida, [What nobody tells you about documentation](https://docs.divio.com/documentation-system/) (Divio, 2017) | [HN, 37 points](https://news.ycombinator.com/item?id=15869296) (below 50, kept as the origin of D2) | The four forms and why one page serves one need |
| D2 | [Diátaxis](https://diataxis.fr/): tutorials, how-to guides, reference, explanation, the compass | Same thread; the framework is the maintained version of D1 | `tech-docs`: the compass table, the per-form rules and their usual mistakes, improving one page at a time |
| D3 | Julia Evans, [Patterns in confusing explanations](https://jvns.ca/blog/confusing-explanations/) (2021) | [HN, 566 points](https://news.ycombinator.com/item?id=28254630) | `tech-docs`: the confusing-patterns table (assumed knowledge, too many concepts, toy examples, unlabelled wrong approaches) |
| D4 | Google, [Technical Writing One and Two](https://developers.google.com/tech-writing) (audience, lists and tables, paragraphs, large documents, illustrations, sample code) | Already W10 | `tech-docs`: the frame at the top, list and table rules, caption-first diagrams, runnable samples with output |

### Wording that reads as generated (5)

| # | Source | Discussion | What it changed |
| --- | --- | --- | --- |
| T1 | Wikipedia, [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | [HN, 61 points](https://news.ycombinator.com/item?id=44700558) | Most word entries and the structural patterns in `writing-tells` |
| T2 | Kobak et al., [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016) (2024) | — | The inflated verbs and intensifiers measured as excess after 2022 ("delves", "underscores", "showcasing", "pivotal") |
| T3 | Liang et al., [arXiv 2404.01268](https://arxiv.org/abs/2404.01268) and [arXiv 2403.07183](https://arxiv.org/abs/2403.07183) (2024) | — | Only the caveat: shifts are measurable across a corpus, not in one document. No word list was taken from them |
| T4 | [tropes.fyi](https://tropes.fyi/) | [HN, 5 points](https://news.ycombinator.com/item?id=47088813) (below 50, used for patterns only) | Punchy fragments, stakes inflation, "here's the kicker" |
| T5 | Hacker News em-dash leaderboard thread | [HN, 377 points](https://news.ycombinator.com/item?id=45071722) | Treating the em dash as a weak signal: people used it long before 2023 |

The caveats at the top of `writing-tells` (one hit means nothing, detectors run near chance, the list revises your own text and never judges an author) come from T1, T3 and T5.

### Exemplars

[exemplars](../../tech-article/references/exemplars.md) lists 79 articles with at least 150 points before 2023, chosen from 1,269 unique URLs returned by 62 Hacker News searches (the terms are listed in the file). 29 of them, about 120,000 words, form the corpus behind `check_tells.py`'s baseline: across those human articles the listed words occur 11.2 times per 10,000 words, and eight of them at 0.4 or more ("significant", "robust", "utilize", "highlight", "furthermore", "additionally", "remarkable", "serves as"). The checker marks those eight as *context* so the reviewer reads the sentence instead of replacing the word. The corpus texts are not stored in the repository.

## What changed in the skills

### tech-article

| Added or changed | Sources |
| --- | --- |
| Opening principle: a passage that resists clear writing marks a gap in understanding; go back to the sources. | W2, W3 |
| Step 1 names the form: an explanation, with tutorials, how-tos and reference linked rather than mixed in. | W4 |
| Step 1: a given title is rephrased as a question; a number in a title carries its condition; invented example inputs are allowed when labelled and the mechanism is checkable. | dry run |
| Step 2: project facts files count as a source tier; when the mechanism cannot be sourced, stop, list the gaps and ask the owner. | dry run |
| Hook: open on the point, with the problem and the context that prompted the piece; make the reader care about the question. | W5, W7, W9, V6 |
| Follow one thing: one fully understood case; naive version first, then one fix at a time; a prediction before each important reveal. | V3, V4, V7, V8 |
| The real system and Try it: when part 2 already runs on the real system, part 4 shrinks to the measurement; the experiment gives the reader control and ends in a sandbox; leave it out when it needs unsourced numbers. | V1, V5, V6, V10, dry run |
| A chapter is one idea over one or more storyboard rows. | dry run |
| Voice: plain words, strong verbs with real subjects, present tense for the mechanism and past tense for measurements, numbers instead of adjectives, more and complete examples, terms defined once and reused in figure labels, reasoning and rejected alternatives on the page, inline uncertainty, the claim first, hard parts flagged. | W1, W3, W5, W6, W7, W8, W10, dry run |
| Removed no-ops: the reading-time label and the bold-terms rule as a separate item. | dry run |
| Review: a cold read with only the page, a cut pass, and a motion-off check. | W1, W2, W8, M2 |
| House style belongs to the project guide. | dry run |

### explanatory-figure

| Added or changed | Sources |
| --- | --- |
| New first step: write the question the figure answers and choose the encoding for it. | V2 |
| Zones come before the storyboard; competing axes go to a linked second view. | V5, dry run |
| A storyboard row may apply one change to several objects at once (concurrency). | dry run |
| Encoding rule: every mark maps to one thing, said in the caption; remove marks that map to nothing. | V2, V7, V8 |
| All state shown. | V4 |
| Concrete and summary views together, changing together; each level carries different information. | V1, V5, V9 |
| A static view beside every animation. | V2, V3 |
| The reader's own cases: variables as controls; the grab point under the pointer; touch and keyboard. | V1, V5, V10, V11 |
| Disclose the model behind the figure. | V5 |
| Colour never the only signal. | V8 |
| The watch-only test also answers the figure's question; controls are tested by pointer, touch and keyboard. | V2, V11 |

### scroll-story

| Added or changed | Sources |
| --- | --- |
| Motion shows a state change or cause, confirms the text, and the page explains everything with motion off. | V3, M2 |
| Chapter distance follows events with a floor and a cap; simultaneous events count once. | dry run |
| Purpose rule: name what each animation shows, or remove it. | M2 |
| Reader-paced: motion follows scroll or a control; anything that plays on its own gets play, pause and scrub, starts only when fully in view, and stops when it leaves. | M1, M7, V3 |
| Interruptible: exponential smoothing toward the target, which replaces "damped". | M6 |
| Easing: ease-out for entrances, a small named set, springs only where overshoot means something. | M4, M5 |
| Ordinary scrolling: some content always scrolls normally, constant page length, wheel, trackpad swipe-back, spacebar and Page Down keep working. | M1, M9, M10 |
| One change at a time, unless simultaneity is the point. | V3, dry run |
| Reduced motion keeps the meaning: finished states with short opacity or colour changes instead of travel and parallax; a visible toggle; pause for automatic motion over five seconds. | M3, M8, M9 |
| Completion: a motion-off check, and keyboard scrolling without a pointer. | M1, M2 |

## Dry run findings

The dry run (Cadastre scan topic, facts file only) found that the mechanism chapters could not be written: 10 of 18 claims had no source. The skill then had no path for that case; step 2 now stops and asks the owner. Its other findings are folded into the tables above, marked "dry run". The following findings were not addressed:

- A "predict the time" experiment on a speed topic would imply a speed promise. The skill now says to leave the experiment out; it does not offer an alternative.
- Nothing was built, so the build checks (screenshots, seeks, reduced motion) in all three skills have not been exercised on a consumer article yet.

## Left out

- Animation research by Heer and Robertson and by Tversky: no HN thread found.
- Pudding scrollytelling guides, NN/g on scrolljacking, Disney principles for UI, Material and Apple motion essays: threads under 10 points.
- Bartosz Ciechanowski on his process, Josh Comeau on interactive posts, Maggie Appleton, 3Blue1Brown: no qualifying HN thread for an essay on process.
- Tufte's Razor: the page needs JavaScript and could not be fetched.
