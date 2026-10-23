# Noureli configuration

`../store.json` is the public identity and connection-requirement manifest. Add non-secret provider account IDs, app choices, feature settings, and reviewed scope requirements here as services are selected.

It is a declaration, not an access-control engine. Actual connection configuration and credentials belong only in the isolated runtime. Shared MCP examples live under root `templates/integrations/`. Do not place an automatically activated `.codex/config.toml` in this administrative checkout with broad store access.
