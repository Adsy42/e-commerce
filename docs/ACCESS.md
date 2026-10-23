# Store access and isolation

This repository is the canonical source for shared Shopify practices and each store's non-secret material. Its directory layout organizes work; access is enforced by the runtime and the services that accept credentials. The selected model is strict isolation between store workers.

## Control workspace and store workers

| Workspace | Files and Git access | Credentials | Role |
| --- | --- | --- | --- |
| Control/admin | Full monorepo, its history, and an appropriately scoped GitHub connection | Repository automation only; no standing collection of every store's operating credentials | Maintain shared guidance, create store projections, review and integrate changes |
| Noureli worker | An exported copy of shared guidance and `stores/Noureli`, with no parent checkout, `.git`, other stores, or host home mount | Only Noureli credentials or Noureli-bound broker routes | Operate and develop Noureli |
| Other store worker | The same shared guidance plus that store's material only | Only that store's credentials or routes | Operate and develop that store |

Run each worker in a separate OS user/container or equivalent isolated cloud identity. A separate folder or Codex project inside a container that can read the entire monorepo does not meet this model. A working directory and a write sandbox do not by themselves limit read access. Avoid host filesystem mounts, shared writable authentication directories, access to the container engine socket, and broad inherited environment variables.

The current onboarding workspace contains the canonical checkout. It is a control workspace, not a proven isolated store worker. Repository documentation cannot automatically change its mounts, preloaded tools, account connections, or credential scope.

## Project shared material without exposing the monorepo

The trusted control process should produce a store worker directory containing only:

- Approved root instructions, shared skills, playbooks, and required reusable tooling.
- `stores/Noureli/` and its non-secret runtime configuration.
- A provenance record naming the source commit, store identifier, and projection format version.

Create this export from a known source commit, explicitly select paths, and reject symlinks or generated files that expose anything outside the selected paths. Do not mount the source checkout into the worker. Do not copy `.git`, Git credential helpers, repository tokens, local secret files, customer/order exports, or other stores' data. An export is safer than a sparse checkout for this boundary: a checkout can retain Git history or the credentials needed to fetch excluded files.

Workers return a patch or a bundle of changed allowed files to the control process. The control process checks paths, rejects symlinks and unexpected files, runs validation, and commits the result to the canonical monorepo. Workers do not need a credential that reads or writes the full repository. Shared guidance changes return through the control workflow rather than granting a worker broader access.

## Bind every integration to one store

| Integration surface | Required enforcement | Configuration recorded in Git |
| --- | --- | --- |
| Shopify | An app installation/token scoped to Noureli and only the required Shopify permissions | Expected permanent `*.myshopify.com` domain, intended shop identity, API version, required scopes, secret binding names |
| Email, analytics, ads, support, fulfillment, and other services | A dedicated account/service identity, or a broker that rejects requests outside Noureli's tenant/account/resource IDs | Expected account IDs, tenant IDs, resource IDs, allowed operations, binding names |
| MCP server | Noureli-specific identity and credential store; server or broker enforces the allowed destination and tenant | Server name, transport configuration, expected account and enabled tools; no token values |
| Hosted plugin/app | Provider connection demonstrably limited to Noureli; otherwise unavailable in the worker | Connection requirement and verification procedure, without claiming project-level OAuth isolation |
| Browser automation | Isolated browser profile/session containing only Noureli access | Expected admin domain and identity checks |

The same integration software can run for every store. Its credentials, sessions, OAuth registrations where required, and account/resource namespaces must be separate. A server label such as `shopify_noureli` makes mistakes easier to spot; the accepting service or broker must enforce the boundary even if a request supplies another store's ID.

Hosted plugins can use a connection tied to a user or workspace. Do not assume a repository file or Codex project changes that connection. Disable or omit any broad connection from the worker; if the platform cannot limit it to one store, use a store-scoped MCP/service route instead or a separate supported account boundary. Restricting tool names helps reduce capability but cannot narrow an otherwise broad token to a tenant.

## Credentials and Codex state

Keep credentials in secure environment settings, an OS secret manager, or a supported credential broker. Git contains names and requirements only. Do not commit access tokens, OAuth refresh tokens, `.env` files containing secrets, browser profiles, authenticated logs, raw customer/order exports, or Codex state directories.

A separate `CODEX_HOME` can separate CLI configuration and file-backed state. It is not the isolation boundary: the default MCP OAuth backend can use an OS keyring shared by processes with the same user identity. Use separate OS/container identities and isolated secret stores, or supported broker-backed authentication. Do not copy a general-purpose Codex home into worker images.

## Identity preflight

Before enabling operational tools, perform read-only checks using the worker's actual connection:

1. Read Shopify's shop identity and compare its permanent domain and, when known, shop ID to the store configuration.
2. For every other connected service, resolve the authenticated identity and allowed tenant/account/resource IDs; compare them with the configured IDs.
3. Confirm required permissions and confirm broader account access is excluded by provider permissions or broker policy. Listing only the expected account is not proof that a broad token cannot access others.
4. Fail closed on a missing identity, mismatch, or unverified connection. Recheck after a login, token rotation, account change, or switching runtime.

Use a separate test tenant or a broker policy test to demonstrate that an out-of-scope request is rejected. Do not probe another production store. Record only non-secret identity and validation results; redact credentials and customer data.

## Setup checklist

| Step | Owner | Evidence before marking complete |
| --- | --- | --- |
| Identify Noureli | Store owner | Permanent Shopify domain and non-secret service/account list recorded |
| Create runtime identity | Host/cloud administrator | Separate OS/container/cloud worker with only the approved projection mounted |
| Bind integrations | Store owner or service administrator | Store-only permissions or enforced broker routes; values supplied through secure settings |
| Limit Codex tools and plugins | Codex administrator | Worker-visible tools and connections inspected; broad inherited connections unavailable |
| Run preflight | Store worker | Actual read-only identity checks match expected store/account IDs |
| Verify isolation | Administrator | Filesystem/credential boundary checked and controlled out-of-scope test rejected |
| Exercise development workflow | Store worker | Required commands and representative functional checks pass with store-scoped access |
| Integrate results | Control process | Allowed-path review, validation, commit, and successful push to the canonical repository |

Until the runtime boundary and credentials are provisioned and checked, this repository specifies the intended access policy; it does not establish that strict isolation is active.

## References

- [Codex configuration](https://developers.openai.com/codex/config-basic)
- [Codex MCP configuration](https://developers.openai.com/codex/mcp)
- [Codex AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md)
- [Official Codex configuration schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json)
- [Official MCP OAuth storage implementation](https://github.com/openai/codex/blob/main/codex-rs/rmcp-client/src/oauth.rs)

Configuration support changes with Codex versions. Validate the installed client's schema/help before adding settings. The isolation model above does not depend on a particular profile flag or on an undocumented project setting.
