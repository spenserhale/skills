---
name: outlook-web-rules
description: Read, audit, create, or edit Outlook web inbox rules through a signed-in browser. Use when the user mentions Outlook.com rules, mail filters, automatic deletion or filing, duplicate rules, rule order, or settings/mail/rules. Not for Outlook desktop, Gmail filters, mailbox cleanup without rules, or Microsoft Graph code.
---

# Outlook Web Rules

Use focused browser observations and semantic controls. Default new filters to **From exact email address AND Subject includes a specific phrase**, then the requested action, especially for deletion.

## Defaults and scope

- Missing sender, subject phrase, or action: ask only for missing values. Do not invent them or silently broaden a delete rule to sender-only, domain-only, or all messages. Honor an explicit user override of the two-condition preference.
- Use `From`, not `Sender address includes`, for an exact sender. Use `Subject includes`, not `Subject or body includes`, for a subject requirement.
- Separate condition rows are AND. Multiple chips in one keyword condition are alternatives (OR), not additional AND requirements. Keep a multiword phrase in one chip.
- Use `Delete` for requested ordinary deletion. `Permanent delete` is a distinct action; never substitute it. Follow the active browser's confirmation policy for consequential actions.
- Creating a rule applies to future messages. Leave `Run rule now` unchecked unless the user requested applying it to existing mail. Do not trigger the identically named menu action while inspecting.
- New-rule default: `Stop processing more rules` checked. Keep it for terminal delete filters; consider later rules for filing/tagging. Preserve an existing rule's setting unless asked to change it.
- A request to inspect the UI or create this skill does not authorize saving test rules or changing existing rules. Probe an unsaved draft, then `Discard`.

## Connect and observe cheaply

1. Use the user-requested browser/extension and signed-in tab. Otherwise use the environment's preferred browser. Follow its setup documentation once; retain browser and tab bindings.
2. Open `https://outlook.live.com/mail/options/mail/rules` only if the tab is not already there. For work/school accounts use their existing Outlook host and the visible Settings > Mail > Rules path.
3. Take one initial semantic snapshot. Scope subsequent reads to `Inbox rules`, the selected rule, or the editor; avoid dumping the underlying inbox. Use AX diffs or a filtered DOM snapshot, not repeated full trees/screenshots.
4. Batch known independent field actions, then inspect the resulting state. Observe after opening menus or changing editor structure before choosing new controls. No fixed sleeps or guessed IDs.

Read [browser recipes](references/browser-recipes.md) only when translating these steps into browser-extension calls or recovering ambiguous selectors.

## Read and find duplicates

1. Use `Search rules by name` for a known rule name or useful name fragment. This search does **not** search condition values. For a sender-wide audit, get a compact name/order/enabled inventory, then expand relevant candidates; inspect all rules only when coverage requires it.
2. In the observed DOM, rows have role `menuitem` and names `List item <name>, <position> of <total>`. Scope `Expand rule`, `More actions`, and switches to the exact row. AX may call these “List item”; that is not a DOM `listitem` role.
3. Expand only candidates. Read the sibling summary for conditions, actions, exceptions, and stop-processing. If exact fields are unclear, open the editor, read, and `Discard`.
4. Record `position | name | enabled | conditions | actions | exceptions | stop`. A checked switch labeled `Disable rule` means the rule is enabled; the label names the offered action.
5. Compare actual predicates, actions, exceptions, enabled state, and order effects. Similar names are not proof of duplicates. Report broken destination-folder warnings without silently repairing them.

## Create

1. Check likely existing rules before adding; skip an already equivalent rule. Ask if its configuration conflicts with the requested behavior.
2. Click `Add rule`; fill `Name your rule` with a searchable name, e.g. `Delete | alerts@example.com | Weekly digest`.
3. Open `Select a conditional`; choose `From`. Fill `Select senders for this condition`; press Enter and verify the exact address is a committed chip.
4. Click `Add another condition`; choose `Subject includes` in the new condition combobox. Fill `Enter words to look for`; press Enter and verify `Remove <phrase>` chip appears. Verify both rows are present.
5. Open `Select a action`; choose the requested action. For `Move to`/`Copy to`, select and verify the actual destination folder. Add only requested actions/exceptions.
6. Check committed values, action, exceptions, stop-processing, and unchecked `Run rule now`. If saving is authorized, click `Save` once; otherwise leave a reviewable draft.
7. Find the saved rule, expand it, and verify actual conditions/action/enabled/order. A successful click alone is not proof. On uncertain save, inspect the list before retrying to avoid duplicates.

## Edit

1. Identify the exact rule by name **and configuration**. Same-name rows occur; use position from the current snapshot and sender/subject/action to disambiguate. Ask only if they cannot distinguish the intended target.
2. Record the current fields, exceptions, enabled state, order, and stop-processing before editing. Open `Edit rule: <name>` from its expansion, or its scoped `More actions` > `Edit rule` menu.
3. Change only requested fields. Keyword inputs append chips: replacing a subject requires removing the old `Remove <phrase>` chip, entering the replacement, and pressing Enter. Do not remove the whole condition row accidentally. Sender chips use their own remove control; inspect it before use.
4. Preserve other conditions, chips, actions, exceptions, stop-processing, enabled state, and relative order. Leave `Run rule now` off unless requested.
5. Save once; re-expand and verify the changed predicate and preserved settings. Re-resolve row positions after save/reorder. Inspect list/editor on validation errors instead of repeating clicks.

## Finish

Report only requested rule details or changes, using `From X AND Subject includes “Y”: Z`. Mention unresolved conflicts or broken destinations. Follow browser proof-of-work requirements for saved changes; never export private mailbox contents into this skill or its examples.
