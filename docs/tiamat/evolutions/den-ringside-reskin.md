# Tiamat evolution: Den — a Ringside reskin

- **Status:** **built, v1 live (2026-07-30, same day as the flag).** Two deltas, exactly the split upstream's guide prescribes: `f368e7a` — the face-selection mechanism (`/?face=<name>` serves `dashboard/faces/<name>.html`; stock default, presence changes nothing, loud 404s, slug-constrained names; tests + live-captured API fixtures) — and `25d9b87` — `dashboard/faces/den.html` (self-contained; hunts / kills ledger with per-task verdicts + verified sentences / fleet grouped by harness per Joe's original organizing principle; honest-data locked by DenContractTest). Full suite 261/261. View: `http://127.0.0.1:8700/?face=den`; stock and Den link to each other.
- **Upstream status:** the selection mechanism (`f368e7a`) is **PR-ready material now** — it is the exact "ideal first piece" their CONTRIBUTING names (#39), small, tested, no behavior change without opt-in. The Den face itself upstreams later, after daily-use wear-in. **v2 candidates:** per-task-type drilldown in the Heads (upstream's stock models view added this — adopt-lane), richer fixture-render tests, live log tails on hunting runs.

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
