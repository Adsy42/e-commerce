# Repository-wide operating rules

This is the administrative source repository for multiple stores. A complete checkout is not a strict store sandbox. Store workers must use the isolated workflow in `docs/ACCESS.md` and `docs/CODEX-PROJECTS.md`.

## Context

- Read the target store's `AGENTS.md` and `store.json` before store work. Do not infer a Shopify domain or account from a display name.
- Shared skills live under `.agents/skills/`; operating practices live under `playbooks/`.
- Change shared guidance when it applies to all stores. Keep brand, commercial decisions, catalog, campaigns, and account identifiers in that store's directory.
- Never copy one store's credentials, private records, creative, or commercially sensitive findings into another store.

## Account boundaries

- A folder, manifest, project name, MCP server name, or instruction does not enforce authorization.
- A store session must have only that store's credentials and permitted tools. Do not attach a globally authenticated multi-store plugin, browser profile, or Shopify CLI session to it.
- Unknown or unverified connection identity means stop the affected external operation. Continue unrelated offline work.
- Verify the actual shop/account identity using a read-only provider request before using a newly configured connection. Compare stable IDs and the permanent Shopify domain to `store.json`.
- Do not weaken provider scopes, isolation, or approval settings to get a task to pass. Describe missing access accurately.

## Changes and evidence

- Prefer drafts and previews. Obtain explicit authorization for publishing themes, changing prices, sending campaigns, modifying billing, deleting data, or changing account permissions.
- Keep tokens, OAuth caches, browser cookies, passwords, customer/order-level records, and personal data out of Git and reports.
- Record the target store, proposed change, validation, and rollback for material live-store changes.
- Run `python3 scripts/workspace.py check` and relevant existing tests after structural/configuration changes.
- GitHub synchronization requires a successful push. Never claim local changes are on GitHub before verifying the remote commit. No force pushes, automatic conflict resolutions, or blanket `git add .`.
- Cloud tasks already have an isolated task checkout; use it. Do not create extra worktrees unless the user requests one. Task isolation does not imply isolation from other store files in the same checkout.
