# Tiamat evolution: Den — a Ringside reskin

- **Status:** flagged 2026-07-30 (Joe: "reskin Ringside to Den, as in dragon's den") — not started
- **Upstream status:** `local-only` (but see below: upstream actively solicits this shape)

## The idea

Reskin the Ringside run UI as **Den** — the dragon's den. You peer into the
den to watch Tiamat's heads work. Fits the fork's mythology (multi-headed
dragon, one will, verified kills) and gives the fork a human-facing surface
with its own identity, replacing the retired Argus board as the
client-facing view.

## Why this is a sanctioned contribution, not just a skin

Upstream's `CONTRIBUTING.md` has an explicit section — *"Ringside UI
contributions — actively encouraged"*: "We *want* people shipping
alternative Ringside faces." Their mergeability rules are the build spec:

1. **Honest data** — build against the real `/api/runs`, `/api/library`,
   `/api/models` responses; capture them as fixtures and test rendering
   against the fixtures. The display contract (columns, identity taxonomy)
   is non-negotiable — displayed data must be true.
2. **Self-contained** — no CDNs, no external fonts, vendor everything.
3. **Escaped** — run names and worker output are untrusted text.
4. **Opt-in, not takeover** — stock UI stays default; alternates arrive via
   an explicit selection mechanism. **That mechanism doesn't exist yet, and
   upstream calls a small PR adding it "the ideal first piece" (#39's
   thread)** — so the Den effort naturally splits into two upstreamable
   deltas: (a) the face-selection mechanism (small, wanted, lands first),
   (b) the Den face itself.

## Path

Fixture capture from real runs (the smoke + ralph-live runs already in
`~/.ringer/runs/`) → selection-mechanism delta → Den face as a delta →
prove in daily use → upstream (a) immediately, (b) when it has worn in.
