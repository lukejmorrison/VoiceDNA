# Patch notes — CI / GitHub Actions scope review

## Current repo state
- No `.github/` directory is present in the workspace snapshot.
- The recovered diff is limited to application code, tests, and the OpenClaw demo.
- I did not find any workflow files to update in this branch snapshot.

## If CI/workflow files are added later
Any change under `.github/workflows/` should be treated as elevated-scope work because GitHub protects workflow files more strictly than ordinary source files.

### Why elevated scope may be needed
- Workflow files can change the commands run in CI.
- They can alter how repository secrets and tokens are used.
- GitHub often requires the `workflow` PAT scope for commits that modify workflow YAML.

### Practical guidance
- If only source/test files change: `contents:write` is usually enough for push access.
- If workflow YAML changes too: include `workflow` on the PAT.
- If the PR will be created via GitHub API/CLI: add the PR write scope your token provider requires.

## Recommendation
- Keep CI changes out of this PR unless they are required for the pilot.
- If workflow updates are unavoidable, split them into a separate reviewable commit and document the required PAT scopes in the PR body.
