---
name: shopify-change
description: Prepare, validate, and record a Shopify change for one verified store.
---

# Shopify change workflow

Apply the store-context skill first. Read `playbooks/shopify-change.md` and the relevant store decisions. Describe the customer/business problem, exact target, and expected outcome.

Use a development theme or draft where supported. Preserve the previous state and define rollback. Run checks that exercise the changed journey and distinguish passing checks from unrun or blocked checks. Follow the repository's existing application tooling once actual theme/app source is present; do not invent a successful Shopify check.

Record meaningful changes under the selected store's `operations/`, using `templates/change-record.md` when available. Do not include secrets or customer-level records. Publishing, spending, price changes, campaign sending, deletion, and permission changes require authorization for that action. Verify the resulting state after an authorized operation.
