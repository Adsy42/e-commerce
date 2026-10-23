# E-commerce operations

One canonical monorepo for shared Shopify operating practices and store-specific work. GitHub holds committed, non-secret material. Local and cloud tasks use the same commits.

## Layout

```text
e-commerce/
├── AGENTS.md                    # Rules inherited by agents working in this repository
├── .agents/skills/              # Shared, reusable workflows
├── playbooks/                   # Operating principles and procedures
├── docs/                        # Access, Codex projects, Git sync, daily workflow
├── templates/integrations/      # Reusable configuration examples; no credentials
├── scripts/workspace.py         # Validate stores; export one store for an isolated runtime
├── tests/                       # Validation and export boundary checks
└── stores/
    └── Noureli/
        ├── AGENTS.md
        ├── store.json           # Store identity and connection requirements
        ├── .env.example         # Variable names only
        ├── brand/               # Positioning, voice, visual guidelines
        ├── catalog/             # Product source material; no customer records
        ├── content/             # Copy, campaigns, reusable creative
        ├── theme/               # Theme source when imported
        ├── config/              # Public configuration and account identifiers
        ├── operations/          # Plans, decisions, runbooks, change records
        └── reports/             # Aggregated, non-personal reporting
```

Another store gets another directory under `stores/`, with its own identity, instructions, and connection requirements. Shared integration implementation belongs at the root; authenticated instances belong to a store's isolated runtime.

## Start here

```bash
python3 scripts/workspace.py check
python3 -m unittest discover -s tests -v
```

- [Access boundaries](docs/ACCESS.md): what actually enforces strict store isolation.
- [Codex projects](docs/CODEX-PROJECTS.md): administrative versus store runtimes, locally and in cloud.
- [GitHub and local/cloud sync](docs/SYNC.md): commits, pushes, pulls, and concurrent tasks.
- [Daily store workflow](docs/STORE-WORKFLOW.md).
- [Operating principles](playbooks/principles.md).

## Status

The repository structure and store bundle tooling are configured. Noureli's user-supplied permanent Shopify domain is `30qqph-za.myshopify.com`; its stable shop ID and integration accounts remain unconfigured. No Shopify/MCP/plugin connection, isolated store runtime, or live-store access is configured by these files. A normal checkout of this monorepo is an administrative workspace with access to every file in it.

No credentials, customer/order-level exports, browser sessions, or local authentication caches belong in Git. Use a private repository and separate secret stores. Making this repository private, provisioning isolated runtimes, and binding external accounts are platform/account settings, not effects of creating folders.
