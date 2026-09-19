---
name: interview-me
description: Extract what the user actually wants before any spec; one question at a time, each carrying a guess.
---

# Interview me

Distilled from [`interview-me`](https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me) and
[`idea-refine`](https://github.com/addyosmani/agent-skills/tree/main/skills/idea-refine)
(MIT, Copyright (c) 2025 Addy Osmani); see `CREDITS.md`.

Read by `my-spec` before it writes anything down. Two entry conditions, one method:

- **Intent unclear** — a request arrived without who it is for or why now. Extract it.
- **Idea vague** — an idea exists but has not been stressed. Widen first, then narrow.

This is the interactive form, for a human who is present. A worker asking its coordinator uses the opposite
shape — the whole frontier in one batch — because there the round trip is what costs. See **When you are
blocked** in `~/.agents/skills/my-workflow/references/roles/task-worker.md`.

## State a confidence number, out loud

Before the first question, say what you think they want and how confident you are. A number forces the
estimate to be real, and it gives the user something concrete to correct rather than a blank prompt.

Stop at roughly 95%. Not 100% — that never arrives, and the last few points cost more than writing the spec
and being corrected. Stop early too: a user who has answered the same thing three ways is telling you the
question is settled.

## One question at a time, each carrying your guess

Never a numbered list of six. A batch gets answered at the depth of the shallowest item, and it hides which
answer actually moved you.

Attach your own answer to every question:

    Who hits this first — the operator, or an end user?
    GUESS: the operator, because the request mentions the admin console.

The guess does the work. It costs the user a yes instead of an essay, it exposes a wrong assumption before
it reaches the spec, and it keeps the interview from feeling like a form. A question you cannot attach a
guess to is usually a question you could have answered by reading the repository — go read it.

Ask about intent, constraints, and who is served. Do not ask about implementation; that is yours to decide
and asking outsources your job.

## Hear what they want, not what they think they should want

People ask for what sounds reasonable. The signal that you are hearing the performance rather than the need:
hedging ("I guess"), borrowed vocabulary that does not match how they described the problem, a requirement
with no story behind it.

When an answer conflicts with something said earlier, say so plainly and ask which holds. A contradiction
you smooth over becomes a spec that satisfies neither reading.

## Widen before you narrow, when the entry was a vague idea

Push out to several genuinely different framings before converging — and make them different in kind, not
three variations of the first one. Then close, with a recommendation rather than a menu: name the direction
you would take and why the others lost.

Carry forward what the narrowing produced: the assumptions still to be validated, the smallest version worth
building, and what you are deliberately not doing. That last one prevents most later scope arguments.

## Close with a restatement, and a real yes

Restate the intent in their words, not your vocabulary — a restatement in jargon proves nothing, because
they will agree with a summary they did not fully parse. Include what you understood to be out of scope.

Then get an explicit confirmation. "Whatever you think" is not one: it means the interview did not land, and
the honest move is to name the one decision still open rather than proceed on a shrug.
