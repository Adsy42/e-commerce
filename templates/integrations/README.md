# Shared integrations, separate authenticated instances

Put reusable integration code, documented installation steps, and reviewed permission lists here. Pin actual tools and versions after selecting providers. A template is not an installed or authenticated integration.

Each store's `store.json` declares the required service identity and secret variable names. Provision an independent connection in that store's runtime. Never place a store token in a shared file or let a worker supply an arbitrary tenant to an administrator credential.

For a provider spanning several stores, use separate service identities or a server-side gateway that fixes the permitted tenant/account per credential and rejects mismatches. The gateway must enforce the restriction; a prompt does not.

## Codex MCP example

`codex-mcp.example.toml` documents supported configuration keys. It is deliberately outside `.codex/` and has an invalid example URL so it cannot accidentally activate a connection. Render a complete runtime configuration only after choosing and verifying the MCP server.

The runtime must also exclude inherited/global MCP servers, plugins, apps, browser sessions, and credential files from other stores. Adding one scoped server to an existing globally configured Codex instance does not accomplish that.
