# GitHub, local development, and cloud tasks

GitHub is the canonical committed history. A local checkout and a cloud task are independent copies, not a shared live filesystem. Unsaved/uncommitted/unpushed work does not transfer between them. Keep this repository private; its visibility must be checked in GitHub settings.

## Local installation without overwriting existing work

The discovered local Codex project is `/home/adsy42/Documents/E-commerce/Noureli` and is not currently a Git repository. This cloud task cannot modify that computer's files. Preserve that directory. Use a new sibling location for the administrative clone:

```bash
git clone https://github.com/Adsy42/e-commerce.git "$HOME/Documents/e-commerce-monorepo"
cd "$HOME/Documents/e-commerce-monorepo"
python3 scripts/workspace.py check
```

Review and copy existing non-secret store material into `stores/Noureli/` without replacing either side blindly. Never import `.env`, authentication state, browser profiles, or customer exports. Configure store-only local runtimes before adding their paths as Codex projects; see `CODEX-PROJECTS.md`.

## Single active administrative task

Before starting, check `git status --short`, then `git fetch origin` and `git pull --ff-only origin main` from a clean `main` checkout. A failure means inspect the branch and preserve local changes; do not reset or force synchronization.

At a useful milestone:

```bash
python3 scripts/workspace.py check
python3 -m unittest discover -s tests -v
git diff --check
git diff
# Inspect untracked files too. Stage only the intended, non-secret paths:
git add <specific-files>
git diff --cached
git commit -m "Describe the store or shared change"
git push origin main
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

The two SHAs should match if nothing else has updated the branch. Do not use `git add .` as an unattended sync mechanism. Credential and personal-data review remains necessary even with `.gitignore`.

## Concurrent local and cloud work

Use a branch per task, push it, and merge through a pull request after review. A cloud checkout may already be on a task branch; inspect it before switching or creating another branch. Pull the merged `main` commit on the other machine before starting its next task. Resolve conflicts deliberately; never force-push or overwrite another task's changes.

Cloud publication snapshots prepared environment state; it does not mean the repository is continuously refreshed from GitHub. Fetch/pull or start from the current ref as appropriate. Live service processes and authentication sessions do not survive by virtue of being committed or snapshotted.

## Store workers and automation

Strictly isolated store workers should not hold credentials that can read/write the full monorepo. Return their store changes to the administrative integration workflow for review and push. If cloud tooling needs a Git repository per store, an administrator can maintain generated private store mirrors; do not create independent competing sources of truth.

Later automation may validate, build store projections, and propose pull requests on push. Give it only the permissions it needs and review its configuration first. No background auto-commit, auto-merge, auto-push, deployment, or bidirectional file watcher is installed by this repository. “Always updated” means successful synchronization at task boundaries, with any failures reported.
