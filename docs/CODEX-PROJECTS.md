# Codex projects for the commerce monorepo

Use one canonical GitHub repository and a separate runtime/project for each store. Projects provide a convenient entry point; OS/cloud boundaries and service authorization enforce access. See [ACCESS.md](ACCESS.md) for the required strict isolation model.

## Recommended projects

| Codex project | Directory or source | Purpose | Connections |
| --- | --- | --- | --- |
| E-commerce control | Local clone of `Adsy42/e-commerce` | Shared philosophy, skills, integrations, projections, and Git review | Repository automation; no general collection of store operating credentials |
| Noureli | Isolated Noureli runtime projection | Noureli development and store operations | Noureli-only accounts and broker routes |
| Each future store | Its own isolated runtime projection | Work on that store | That store's accounts only |

The canonical store path is `stores/Noureli/`. Each projection also carries the approved shared instructions and skills, so improvements to shared practice can be distributed without copying another store's files or credentials.

The currently observed local Codex project path is `/home/adsy42/Documents/E-commerce/Noureli`, and it is reported as non-Git. A name or directory alone does not establish the desired runtime boundary. Replace that project's target, or create a new project, using the isolated Noureli projection once the host runtime has been provisioned. Keep the full local clone as the control project. A non-Git projection is intentional in this model; its changes go back through the control process.

This cloud session cannot edit the local computer's filesystem or retarget its project automatically. Do not assume a directory created under `/workspace` also exists at that local path.

## Local setup

1. Keep a local canonical clone of `Adsy42/e-commerce` for the control workflow. Fetch and pull with a clean working tree before starting work that depends on the latest shared state.
2. Provision a separate Noureli OS user/container with a dedicated writable working directory. Mount or copy only a sanitized Noureli projection from a known source commit, with no full checkout or `.git` metadata available to the worker.
3. Set up Codex inside that runtime with its own state and authentication store. Authenticate through the product's supported login flow; do not copy an existing general-purpose Codex home or browser profile.
4. Register only the necessary Noureli MCP servers/plugins. Reuse shared integration templates, with separate provider credentials and expected account IDs. Check effective configuration and tool availability for this installed Codex version.
5. Inject Noureli values through secure runtime settings or its secret manager. Do not put secret values in the projection, repository config, shell history, or chat.
6. Run the identity preflight in [ACCESS.md](ACCESS.md), then the store's required startup and functional checks.
7. Open the worker directory through a Codex-supported local or remote workspace connection. If the desktop client cannot attach to the isolated runtime, use a supported Codex client inside it; selecting a host folder does not create isolation.

Do not use a shared keychain or shared writable Codex directory as the only barrier between store accounts. A distinct `CODEX_HOME` helps organize state but does not guarantee that a shared OS keyring or hosted OAuth connection is separate.

## Cloud setup

Create a separate cloud environment for each store, with its own credentials and connection policy. Use the same canonical source commit and shared templates to generate its worker content. Keep the control/admin environment separate from store workers.

Check what the cloud platform actually mounts. If it restores the entire monorepo into every store environment, a different task working directory or an instruction to ignore other stores is insufficient for strict file isolation. A sparse checkout alone is also insufficient if history or a full-repository Git credential remains available.

Preferred delivery options, depending on platform support:

1. A restricted artifact/mount containing only the sanitized store projection and shared files, delivered by the trusted control process.
2. If subset artifacts/mounts are unsupported, a generated private per-store runtime mirror containing only the projection. The mirror is a delivery artifact, not a second source of truth. Do not include canonical Git history, other stores, or secrets. Its cloud Git credential must be limited to that mirror. Send changes through an allowed-path integration process back into the monorepo.

Creating a mirror requires GitHub repository provisioning and access policy; the documentation does not claim those resources already exist. If the available cloud product cannot enforce the worker boundary or restrict hosted account connections, label that environment as control/development only until an appropriate runtime is available.

The installation script should prepare tools and dependencies. Saved startup instructions should activate only the assigned store, perform identity preflight, start required services, and run readiness checks. Live processes and OAuth sessions must not be assumed to survive snapshots or new tasks. Use the existing isolated checkout where appropriate; do not create a Git worktree unless explicitly requested.

## Keeping GitHub, cloud, and local work current

GitHub holds the canonical committed state. Local and cloud files update after successful Git operations or projection refreshes; uncommitted files are not automatically synchronized.

- Start a control task by fetching current refs and updating a clean branch without overwriting local work.
- Give concurrent tasks separate branches. Rebase or merge deliberately when their work overlaps.
- Refresh each worker projection from a recorded source commit; do not silently replace a worker's unfinished files.
- Return store edits to the control process, validate allowed paths and contents, then commit and push them to the canonical repository.
- Refresh affected worker artifacts/mirrors after the canonical change lands. Record the new source commit.

Do not grant full monorepo access to a store worker merely to make syncing convenient. Automated publishing belongs in a trusted control workflow with narrow repository permissions and checks that reject cross-store changes. A completed local commit is not evidence of a successful push, and a successful push is not evidence that another machine has pulled it.

## Information and access still required

| Requirement | How to supply it | What it enables |
| --- | --- | --- |
| Noureli's permanent Shopify domain and known shop ID | Non-secret store configuration | Identity checks and correct Shopify target |
| Required services/plugins and account/resource IDs | Non-secret integration inventory | Precise connection selection and scope policy |
| Read versus write operations needed for each service | Store access policy | Minimum provider permissions and broker rules |
| Store-scoped service credentials/OAuth connection | Secure settings or supported provider login | Actual operational access |
| Local runtime choice and administrator access | Host configuration outside this cloud workspace | Isolated local project and mounts |
| Cloud subset delivery support or runtime mirror access | Cloud/GitHub administration | Strictly scoped cloud worker files and Git access |

Never supply token values in chat. Existing valid store-scoped connections should be reused after their identity and scope are verified. An empty token environment variable does not prove GitHub authentication is missing; cloud Git access may be supplied through its HTTPS proxy.

## References

- [Codex app projects and local workflows](https://developers.openai.com/codex/app)
- [Codex configuration](https://developers.openai.com/codex/config-basic)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md)
- [Official Codex configuration schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json)
- [Official MCP OAuth storage implementation](https://github.com/openai/codex/blob/main/codex-rs/rmcp-client/src/oauth.rs)

Use the installed client's supported settings. No per-project account-binding capability is assumed by these instructions.
