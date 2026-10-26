---
title: Pricing and plans
description: The plans, what each includes, and the limits that apply. The source of truth for packaging.
---

<!-- If the code holds a machine-readable catalog (for example config/plans.yaml, an entitlements module, or billing-provider product IDs), that catalog is the source of truth: name it here, and derive the tables below from it (generate them, or update them in the same commit as any catalog change; the code wins on disagreement). Every change to prices, plans, or limits needs a decision record. -->

## Plans

| Feature key | <Free> | <Pro> | <Team> |
|---|---|---|---|
| `<feature_key>` | <limit or included> | <limit or included> | <limit or included> |

## Limits and quotas

What happens when a customer reaches each limit.

## Add-ons

Anything bought separately from a plan.

## Availability

Keep three states apart: available in the product, included in a customer's plan, and enabled for rollout.

## Billing mapping

Which billing-provider product or price ID maps to each plan.

## History

- YYYY-MM-DD: <change> ([NNNN](../decisions/NNNN-<title>.md))
