# Build Track → Race Ready V4 publishing

V4 automatically reads https://raw.githubusercontent.com/knollkyle4/race-ready/main/programming/v4-approved.json on authenticated load, focus and every minute while browsing (not while editing). No V4 deployment or athlete import is needed for later weeks. GitHub raw caching may add a few minutes.

## Publish only after Kyle approves the exact prescription
1. Commit the complete seven-day V3-compatible JSON to programming/cycle-N-week-N-YYYY-MM-DD.json on main. Keep all movements, loads, notes, optional flags and logging types exact. Monday through Sunday required.
2. Read the raw file from main and compute its SHA-256 over the exact UTF-8 bytes (including final newline).
3. Fetch programming/v4-approved.json fresh. Append one entry to weeks: {weekId:"YYYY-MM-DD",path:"programming/cycle-N-week-N-YYYY-MM-DD.json",sha256:"<64 lowercase hex>",approved:true,publishedAt:"<ISO UTC timestamp>"}. Preserve all previous entries. Commit this approval index to main using its current blob SHA. Merely creating a draft file does not publish it.
4. Open V4 or its authenticated /api/training endpoint. Verify programming.warning is null and programming.weeks includes weekId; verify seven calendar dates and exact prescriptions. Report publication only after verification.

## Data rules
Published weeks and approval digests are immutable. Do not edit approved file bytes or reuse a weekId. Stop and arrange an explicit correction workflow if a published prescription must change. V4 stores a verified cloud copy and appends athlete-scoped assignments with conflict protection. Existing assignments, drafts, completed snapshots, records and Podiums are never replaced by feed sync. Each admitted athlete gets their own assignments and logs. Sharing access is managed separately.

Supported log types: weight, notes, score (AMRAP), time, round, dual. Unknown types or invalid dates are rejected. Text is preserved exactly. Titles containing Honda Legends do not grant official Podium status; prototypes remain ordinary training. Official timed events need the separate Podium release metadata workflow.

## Connection health
V4 Settings lists published weeks. A feed failure shows a warning and retains all cloud programming and athlete data. After a week is cached, it remains available even if the source is unavailable or an index entry is removed. No expiring GitHub credential or personal token is stored in V4; it reads this public repository's fixed raw URL.
