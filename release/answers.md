# VoiceDNA research answers

## A) yt-dlp default patch: `bestvideo+bestaudio/best`

Recommendation: yes, use `bestvideo+bestaudio/best` as the default selection expression if the goal is to maximize quality while keeping a fallback.

Why:
- `bestvideo+bestaudio` prefers separate highest-quality streams when available.
- `/best` gives a safe fallback for single-file formats or constrained sites.
- It is the usual quality-first default for download pipelines.

Caveats:
- The merge step may require `ffmpeg`.
- Some sites or formats can fail if the separate streams are not mergeable.
- If bandwidth or latency matter more than quality, a lower-resolution fallback policy may still be preferable.

Suggested implementation shape:
- Make the default explicit in one constant.
- Keep a site override path for cases where a merged file is better.
- Log when the fallback path is used so quality regressions are visible.

## B) Upload strategy tradeoffs

Recommendation: choose the upload strategy based on whether the target system values simplicity, latency, or portability most.

Tradeoffs:
- **Direct upload of the final merged media**
  - Pros: simplest for reviewers and downstream consumers; one artifact to store.
  - Cons: larger payloads; more bandwidth; less flexible if the source streams need to be reprocessed later.

- **Upload source video and audio separately**
  - Pros: more debuggable; preserves inputs; can avoid repeated extraction work.
  - Cons: more artifacts; more storage overhead; more moving parts for consumers.

- **Upload a compact package/manifest plus derived artifacts**
  - Pros: best for traceability and reproducibility.
  - Cons: highest complexity; needs clear manifest/versioning rules.

Practical recommendation:
- For a pilot, upload the final merged output plus a small manifest with source URLs, selection settings, and checksum metadata.
- Only add separate source uploads if you need auditability or reprocessing.

## C) Short-lived API tokens approach

Recommendation: use short-lived tokens whenever possible, with a refresh flow that minimizes long-lived secret exposure.

Why:
- Limits blast radius if a token leaks.
- Makes revocation and rotation safer.
- Fits CI and agent workflows where access is temporary and scoped.

Preferred pattern:
- Mint a short-lived token just before the operation.
- Scope it narrowly to the exact repo or API action.
- Store it only in memory or a protected ephemeral environment variable.
- Refresh on expiry rather than reusing a long-lived PAT.

Tradeoffs:
- More setup work than a static PAT.
- Requires reliable refresh or re-auth logic.
- Some GitHub operations still need a PAT with the right scope, so short-lived tokens may not replace all admin or workflow-modifying use cases.

For this branch:
- Use a short-lived token for ordinary push or API work if available.
- Fall back to a PAT only when the action truly requires it, especially for workflow-file changes.
