# Daily store workflow

## Administrative workspace

Fetch and inspect the current Git state before starting work. Read `docs/SYNC.md`. Use this complete repository for shared methods, store configuration, and integrating reviewed store changes. Do not connect live store credentials to this workspace when strict isolation is required.

Run `python3 scripts/workspace.py check`. This validates repository structure and policy declarations; it neither authenticates providers nor proves runtime isolation.

## Store worker

Use a separate OS user/container/VM or supported isolated cloud environment containing only the selected store projection and the approved shared material. Prepare a projection from a clean committed checkout:

```bash
python3 scripts/workspace.py bundle Noureli /tmp/noureli-workspace
```

The destination must not exist and must be outside the source checkout. This exports committed files only, omits Git history and other stores, and rejects sensitive paths and symlinks. The command creates files; it does not start or sandbox Codex. Provisioning and credential binding follow `ACCESS.md` and `CODEX-PROJECTS.md`.

Inside the runtime, read root `AGENTS.md`, `stores/Noureli/AGENTS.md`, and `stores/Noureli/store.json`. Shared skills remain in `.agents/skills/`. Begin the task in `stores/Noureli` so ancestor/store instructions apply. Do not assume a copied projection is itself a security boundary.

Verify the connection's actual Shopify identity using the provider's read-only shop identity endpoint. Confirm the permanent `myshopify.com` domain and stable shop ID. Other services require equivalent verified account/workspace IDs and tenant-limited credentials. Unconfigured identity prevents external operations, while offline brand/content work can proceed.

Use `playbooks/shopify-change.md` for live-store work. At task end, return only the intended store files through a reviewed patch or broker. The administrative checkout integrates them, runs validation, commits, and pushes. Do not grant the store worker a broad GitHub token for the full monorepo as a shortcut.

Private exports and customer/order-level data stay in the store's external private storage, outside the repository and exported projection. Reports here must use aggregated, non-personal data.
