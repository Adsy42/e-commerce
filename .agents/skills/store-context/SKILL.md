---
name: store-context
description: Establish the selected store identity, operating context, and runtime access boundary before e-commerce work.
---

# Establish store context

Read root `AGENTS.md`, the selected `stores/<Store>/AGENTS.md`, and its `store.json`. Read `docs/STORE-WORKFLOW.md` if present, otherwise follow the runtime requirements below. In a full checkout, `python3 scripts/workspace.py check --store <Store>` validates declarations only.

Confirm whether this is an administrative checkout or a store-only runtime. Do not use live credentials in the administrative workspace. Strict store work needs an isolated OS/container/cloud runtime with no other-store data, credentials, broadly scoped GitHub access, or global authenticated tools available.

For each requested external service, identify the actual credential binding, enabled tools, and permitted provider account. A manifest, directory name, or MCP name is not proof. Verify the real provider identity through a read-only operation and match it to the store's permanent domain/stable account ID. Unset identity or an unverified connection blocks external operations, not unrelated offline work.

Summarize the selected store and relevant constraints without exposing secrets. Ask for missing public identifiers only when needed. Direct secret entry to the appropriate secure settings rather than chat or repository files.
