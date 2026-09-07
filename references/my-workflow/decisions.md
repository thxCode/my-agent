# Walking a decision

Shared by `/my-spec` Phase 3 and `/my-plan` Phase 3. Apply it at every fork that shapes the spec or the design
— what to build, which approach, which boundary. Its last section, *Overturning a decision that is already
written down*, is also read by `/my-build` Phase 3.6, `team-lane.md` and `multi-window.md`.

The failure this exists to prevent: the user states a preference, you agree with it, and the spec locks in the
option that is cheapest to build and most expensive to own. Agreement arrived at by mirroring is worth nothing;
the point of asking is to get a second judgment, and you only have one to offer if you formed it first.

## The gate

- **Look it up; only decisions go to the user.** Anything discoverable — in the repo, the dependency tree, the
  docs, the git history — is yours to find. Spend the user's attention on judgment calls only.
- **One decision at a time, in dependency order.** Resolve what the next decision rests on before asking it.
  A batch of questions is bewildering and gets answered carelessly.
- **State your recommendation before you hear the preference.** Name your pick and the reason, *then* ask.
  Committing to a position first is the mechanism that keeps the answer from mirroring theirs — asking open
  and agreeing afterward looks like consultation and isn't.
- **Price the maintenance bill for each option.** Who has to touch it later, what breaks first when the
  requirement shifts, what it costs to back out. The cheapest thing to build is frequently the most expensive
  thing to own — when that's the case, say which and by how much.
- **When the user's preference carries the higher bill, say so plainly, once, with the number or the mechanism
  behind it.** Then build what they choose — they have context you don't, and the call is theirs.
- **Lock nothing until the tree is walked and the user confirms.** An unresolved fork left implicit becomes an
  Open Question in the spec, not a silent default.

## Overturning a decision that is already written down

Whoever explores deepest finds the reasons that don't hold — a worker, a build, a later pass. **Exploration is
allowed to overturn the plan**, and the standing instruction to workers says so explicitly: *if what you find
shows my setting doesn't hold, overturn it and say why*, never *implement this design*. The value is mechanical:
**an argument gets used only against the option it was raised against, and its reach is larger.** Measured — a
spec rejected "derive this from elsewhere" because a quantity was the product of two degrees, and that same fact
rejected the single field the spec chose instead; the overturn came from outside the spec's author.

**Whether the user must rule on it is not a question of how big the change is** (that can't be judged). It is
these two:

1. **Does it invalidate something already merged, or reshape a published / already-stored interface?** ⇒ the
   user rules.
2. **Whose reason does it destroy?** If it also removes a prohibition written in a **code comment** ⇒ the user
   rules. Someone paid for that comment, and the next person meets it while editing code, not while reading a
   spec.

Otherwise decide it yourself and report it at the next gate: what you overturned, why, and that you checked 1
and 2. Two companions:

- **An authoritative action is not automatically a decision.** A bulk click and a considered ruling look
  identical in the record. Prefer the reversible direction, and never edit the text to make an action that
  already happened look intended.
- **"Leave it alone for now" is a decision, not a gap.** Don't file it as a todo and dispatch it — the known
  slide is that "not handled" becomes "does not exist" after two re-statements.

## Recording it

A decision with a real trade-off belongs in the spec — the chosen option in **Notes / Constraints / Caveats**
or **Design Details**, the rejected one in **Alternatives** with the reason. A fork you resolved by looking it
up isn't a decision and doesn't need recording.
