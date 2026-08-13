---
name: real-world-examples
description: Ground any explanation, recommendation, comparison, or industry-feedback answer in at least one concrete real-world example, not just abstract description. Use whenever explaining a concept, mechanism, tradeoff, or "how X works", whenever comparing how different companies/tools/industries handle something, and whenever giving a recommendation or verdict — even if the user did not explicitly ask for an example. Trigger on "explain", "how does X work", "why", "what's the difference between", "walk me through", "recommend", "give feedback", "what would this look like in practice/in reality", or any answer that states a general claim or pattern without showing it applied to a specific case.
---

# Real-world examples

An abstract claim ("shared storage for multiple metric shapes is normal") does not
tell the reader what to picture. A concrete instance ("Prometheus stores counters
and gauges as the same untyped float sample — the docs say so explicitly") does.
The reader has to convert every unillustrated claim into a mental picture
themselves; a good example does that conversion for them. There is no numbered
industry spec for this, but there is precedent: the **worked-example effect** from
cognitive load research (Sweller: learners given worked examples outperform those
given the same content abstractly) and the "show, don't just tell" guidance in the
Google and Microsoft developer documentation style guides. Treat this skill as
codifying that convention, not as citing a formal standard.

## What to do

For every explanation, comparison, or recommendation with more than one non-trivial
claim, attach a concrete example to each claim, not just one example for the whole
answer. "Here's the general pattern, and here's an example" bolted onto the end
is weaker than interleaving — the reader forgets which part of the abstraction
the one example at the bottom was supposed to illustrate.

A good example is:
- **Specific** — a named company, product, API, error message, file, or scenario.
  Not "imagine a system that does X" — that is still abstract, just phrased as
  if it were concrete.
- **Checkable** — something the reader could look up or that you actually verified,
  not an invented illustrative story. If you are not sure the example is accurate,
  say so ("something like...") rather than presenting a guess as fact.
- **Load-bearing** — it should change what the reader pictures, not just decorate
  the sentence. If the example could be deleted without losing information, it is
  filler, not an example.

When a claim is comparative ("every system surveyed does X"), one example per
system beats one example for the category. "Prometheus flattens types; OpenTelemetry
keeps them as stream metadata; Stripe pins the aggregation formula at meter
creation" is three examples, not one — each anchors a different data point.

When a claim is about a recommendation or a risk, show the failure or success
case concretely: what input, what happens, what the reader would see. "A key can
silently flip shape" is a claim. "A key reports a windowed counter for a month,
then a buggy integration omits the window one day, `last()` rolls it into the
same series, and differencing across the flip computes garbage" is the example
version of that same claim — it gives the reader the actual sequence of events.

## What this is not

Not every sentence needs an example — a short factual answer, a direct instruction,
or a single unambiguous claim does not need one bolted on for its own sake. Padding
a simple answer with a contrived example is the same mistake as leaving a complex
one bare: it optimizes for the appearance of concreteness rather than for the
reader's actual comprehension. Use judgment: if a claim is a pattern, a tradeoff,
a comparison, or something the reader has to apply elsewhere, it needs an example.
If it is a fact or a single instruction, it usually does not.

## Pattern

**Weaker (claim only):**
> No comparable system lets shape be an emergent property of which columns
> happened to be filled in.

**Stronger (claim + example):**
> No comparable system lets shape be an emergent property of which columns
> happened to be filled in. Prometheus flattens type into one untyped float
> store, but the type is still declared once, in the metric's HELP/TYPE
> comment — never inferred from which fields are non-null on a given sample.

**Weaker (claim only):**
> Don't tell the reader something is easy — show them.

**Stronger (claim + example):**
> Don't tell the reader something is easy — show them. Microsoft's own style
> guide dogfoods this: instead of describing a setup flow as "easy" or "fun,"
> it has writers name the actual step — plug in the device, then follow the
> wizard. The instruction proves the claim instead of asserting it.
> ([Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice))
