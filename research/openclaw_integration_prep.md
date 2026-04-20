# VoiceDNA × OpenClaw integration prep

Date: 2026-04-18
Scope: lock the remaining open decisions, keep the per-agent voice pilot conservative, and give Dr Voss a clean implementation checklist.

## Bottom line

Recommended choices:
1. **yt-dlp default**: set the download selector to `bestvideo+bestaudio/best` on the server side.
2. **Uploads**: ship **simple streaming uploads with a 1 GB cap** first; add resumable chunked uploads only when real multi-GB usage appears.
3. **Machine auth**: implement **`POST /api/auth/token`** for short-lived machine tokens with a **24h TTL**, narrow scope, and explicit revocation support.
4. **Push blocker**: prefer **bundle or user-side push** before asking Luke for a PAT; only use a PAT if he explicitly approves it.

All of the above are conservative, backwards-compatible defaults.

---

## 1) yt-dlp default patch: `bestvideo+bestaudio/best`

### Recommendation
Use `bestvideo+bestaudio/best` as the default format selector.

### Why
- Best quality when separate audio/video streams are available.
- Safe fallback to a single combined file via `/best`.
- Matches the quality-first default already discussed in the research notes.
- Keeps the change simple and easy to reason about.

### Requeue low-res downloads
When a low-res or fallback download is detected, requeue it with the quality-first selector and preserve the original artifact for traceability.

Suggested requeue pattern:
- mark the prior job as `fallback_download=true`
- enqueue a replacement job with `format=bestvideo+bestaudio/best`
- keep source URL, extractor id, and original job id in metadata
- de-dupe by canonical source URL + format selector

### Command template to apply the patch
The exact server file was not present in this workspace, so apply this in the repo that owns the yt-dlp selection constant.

```bash
# In the download-service repo
git checkout -b fix/ytdlp-quality-default
$EDITOR path/to/download_config.py   # replace the existing yt-dlp format selector
# set: format = "bestvideo+bestaudio/best"

git diff
```

If you want a scripted edit, use a patch file:

```bash
cat > /tmp/ytdlp_quality_default.patch <<'PATCH'
*** Begin Patch
*** Update File: path/to/download_config.py
@@
-DEFAULT_FORMAT = "best"
+DEFAULT_FORMAT = "bestvideo+bestaudio/best"
*** End Patch
PATCH

git apply /tmp/ytdlp_quality_default.patch
```

### Test command template
```bash
pytest -q tests/test_download_config.py tests/test_download_queue.py
```

Add one extra test that asserts the requeue path emits the quality selector for low-res downloads.

---

## 2) Upload strategy: simple streaming vs resumable chunked

### Recommendation
Choose **simple streaming uploads (1 GB cap)** for the first release.

### Why
- Lowest implementation and support cost.
- Smaller surface area for auth, retries, and corruption handling.
- Easier to keep backwards compatible.
- Good enough until you actually have multi-GB uploads in the wild.

### Migration plan to resumable chunked uploads
Only introduce chunked uploads when one of these is true:
- users hit the 1 GB cap regularly,
- upload failures from network interruption become common,
- the product genuinely needs multi-GB media transfer.

Migration steps:
1. Keep the current streaming endpoint as the default path.
2. Add a new resumable endpoint behind an explicit client opt-in, e.g. `upload_mode=resumable`.
3. Make chunk metadata immutable: `upload_id`, `part_number`, `sha256`, `size`.
4. Store a resumable manifest so uploads can be resumed without re-uploading completed chunks.
5. Preserve the old streaming path for smaller uploads.
6. Add observability before widening the feature flag.

### Stop point
Do **not** implement resumable chunking until Luke approves the size/complexity tradeoff.

### Approval text to present to Luke
> Luke, I recommend we ship simple streaming uploads with a 1 GB cap first, and only add resumable chunked uploads if multi-GB usage shows up. Approve that plan if you want the lowest-risk path.

---

## 3) `POST /api/auth/token` for short-lived machine API tokens

### Recommendation
Add `POST /api/auth/token` that mints a short-lived machine token with a 24-hour TTL.

### Required behavior
- Input: authenticated machine or user context, requested scope, optional subject/agent id.
- Output: opaque token, expiry time, scope, token id.
- TTL: 24 hours.
- Storage: store only a hash / fingerprint server-side; never log the raw token.
- Revocation: support explicit revocation by token id.
- Scope: narrow by default; no broad admin permissions.

### Safe implementation shape
Keep the change additive:
- existing auth remains unchanged,
- token minting is opt-in,
- no long-lived secrets are introduced,
- machine tokens are treated as disposable credentials.

### Proposed file changes
The exact auth service layout was not present in this workspace, so these are the expected target files in the service repo:
- `server/auth/token_service.py` or equivalent new token helper
- `server/routes/auth.py` or equivalent API route file
- `server/models/machine_token.py` or equivalent token record model
- `migrations/*create_machine_tokens*` for token storage / revocation metadata
- `tests/test_auth_token.py`
- `tests/test_auth_token_permissions.py`
- `docs/auth.md` or equivalent API docs

### Safe migration steps
1. Add the new endpoint behind a feature flag or opt-in config.
2. Add tests for minting, expiry, and revocation.
3. Keep all old auth flows in place.
4. Roll out only after confirming no logging or secret-handling regressions.
5. Update docs with the exact TTL and scope model.

### Stop points
- Do **not** create or store a real token without Luke’s approval.
- Do **not** widen the scope beyond the minimum needed for the current operation.

### Approval text to present to Luke
> Luke, please approve adding `POST /api/auth/token` for short-lived machine tokens. I’ll keep it additive, 24-hour TTL, scope-limited, and I won’t mint or store any real token until you approve.

---

## 4) PAT-required push step: safe options

### Recommendation
Use the safest push path that avoids handing around a long-lived secret:

1. **Best**: create a **git bundle** and let Luke push from a trusted machine.
2. **Second best**: Luke runs the push himself.
3. **Only if necessary**: Luke provides a short-lived PAT with the smallest needed scope.

### Why
- Bundles avoid exposing any secret.
- User-side push keeps the credential on the human side.
- PATs are fine only when explicitly approved and short-lived.

### Relevant scope rule
- If the branch does **not** touch `.github/workflows/*`, a normal repo-write token is enough.
- If workflow files are changed later, GitHub may require `workflow` scope.

### Safe push options
#### Option A — bundle handoff
```bash
cd /home/namshub/dev/VoiceDNA
git bundle create /tmp/voicedna-openclaw.bundle feature/voicedna-openclaw-per-agent-voices
```

Luke can then import it on a trusted clone.

#### Option B — user-side push
Luke pushes the branch from his own clone or machine.

#### Option C — PAT push, only after approval
```bash
GIT_ASKPASS=echo git push https://<username>:<PAT>@github.com/lukejmorrison/VoiceDNA.git feature/voicedna-openclaw-per-agent-voices
```

### Stop point
Do **not** push with a PAT until Luke explicitly says yes.

### Approval text to present to Luke
> Luke, the branch is ready locally. Which push path do you want: bundle handoff, you push it, or I use a short-lived PAT you approve? I will not push until you pick one.

---

## 5) VoiceDNA repo: exact files to keep in scope

These are the current VoiceDNA files already in the pilot surface:
- `voicedna/openclaw_adapter.py`
- `examples/openclaw_voicedemo.py`
- `tests/test_voice_adapter.py`
- `README.md`
- `CHANGELOG.md`
- `INTEGRATION_NOTE.md`
- `research/implementation_checklist.md`

### Suggested PR body language
Keep the branch framed as additive and opt-in:

```md
## Summary
This PR adds an opt-in VoiceDNA per-agent routing layer for OpenClaw.

## Key points
- deterministic preset selection: agent_id -> agent_name -> default
- three presets only: neutral, friendly, flair
- local demo writes WAVs under examples/openclaw/output/
- no default behavior changes
- no cloud dependency for the demo path
```

### Local validation commands
```bash
cd /home/namshub/dev/VoiceDNA
python -m pytest tests/test_voice_adapter.py -v
ruff check voicedna/openclaw_adapter.py tests/test_voice_adapter.py examples/openclaw_voicedemo.py
VOICEDNA_OPENCLAW_PRESETS=1 PYTHONPATH=. python examples/openclaw_voicedemo.py
python -m pytest
```

### Demo sanity check
```bash
file examples/openclaw/output/*.wav
```

---

## 6) Explicit stop points

Stop and ask Luke before any of the following:
- minting or storing a real machine token
- pushing with a PAT
- changing upload strategy from streaming to resumable chunked
- adding `.github/workflows/*` changes that might require `workflow` scope
- broadening auth scope beyond the minimum needed

---

## 7) Next for Dr Voss

1. Verify the target repo file that currently owns the yt-dlp selector.
2. Apply the `bestvideo+bestaudio/best` default patch.
3. Add or update the low-res requeue test.
4. Keep uploads on the streaming path with the 1 GB cap.
5. Add `POST /api/auth/token` only as an additive 24h machine-token endpoint.
6. Prepare the branch for a bundle handoff unless Luke explicitly chooses a PAT.
7. Run the VoiceDNA validation commands above and keep the PR scope narrow.
