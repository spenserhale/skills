# Browser extension recipes

Observed in Outlook.com on 2026-10-07. Labels are lookup hints: confirm them in the live page. Use the browser API documented by the current harness; these examples use the `cua_repl` extension's `tab.playwright` surface. Do not install standalone Playwright or attach a second browser session.

## Compact inspection

After initial setup, retain `tab`. Full DOM snapshots include the obscured inbox; return only the rules section when needed:

```javascript
const p = tab.playwright;
const rules = p.getByRole('group', {name: 'Inbox rules', exact: true});
const snapshot = await p.domSnapshot();
nodeRepl.write(snapshot.split('group "Inbox rules"')[1]?.split('- complementary:')[0]);
```

If that marker is absent, inspect current state rather than interpreting an empty slice as an empty rule list. The split is an output filter, not an interaction locator. Popup menus may occur outside the group; read their scoped menu or option labels separately.

Search and enumerate compactly:

```javascript
await p.getByPlaceholder('Search rules by name', {exact: true}).fill('Cloudflare');
nodeRepl.write(await rules.getByRole('menuitem').evaluateAll(rows => rows.map(el => {
  const toggle = el.querySelector('[role="switch"]');
  return {row: el.getAttribute('aria-label'), enabled:
    toggle?.getAttribute('aria-checked') === null ? toggle?.checked :
    toggle?.getAttribute('aria-checked') === 'true'};
})));
```

`evaluate`/`evaluateAll` are read-only DOM inspections. Do not read hidden application state, credentials, network traffic, or internal Outlook APIs.

Use a full row name from the current snapshot:

```javascript
const row = p.getByRole('menuitem', {name: observedRowName, exact: true});
await row.getByRole('button', {name: 'Expand rule', exact: true}).click();
nodeRepl.write(await row.evaluate(el => el.parentElement.innerText));
```

The summary and named Edit/Delete buttons are siblings of the menuitem, outside `row`. Do not scope these to `row`. An outer `tabpanel` also contains all nested rule panels; `getByRole('tabpanel').filter({has: row})` can match both outer and inner panels, causing strict-mode ambiguity. Use the exact named edit button when unique, or `row` > `More actions` > menu `Edit rule`.

For several already identified rows, batch expansions and return one compact summary per row. Never reuse an AX numeric index after a state change. DOM locators re-resolve, but row positions can change after saving or reordering.

## Editor field mechanics

```javascript
await p.getByRole('textbox', {name: 'Name your rule', exact: true}).fill(ruleName);
await p.getByRole('combobox', {name: 'Select a conditional', exact: true}).click();
// Observe menu before selecting From.
await p.getByRole('option', {name: 'From', exact: true}).click();
// Observe editor: sender is contenteditable, not a textbox.
const sender = p.getByLabel('Select senders for this condition', {exact: true});
await sender.fill(senderAddress);
await sender.press('Enter');
```

After `Add another condition`, the observed second combobox may show `And...`; both condition comboboxes share `Select a conditional`. Use `.nth(1)` only after the current snapshot confirms From first and the new row second. Choose exact option `Subject includes`, then:

```javascript
const subject = p.getByRole('textbox', {name: 'Enter words to look for', exact: true});
await subject.fill(subjectPhrase);
await subject.press('Enter');
```

With multiple keyword conditions, that textbox label repeats. Scope to the observed condition container or use the index justified by the current editor order. Never use `.first()` to suppress ambiguity. A committed phrase appears as button `Remove <phrase>`; an empty input after Enter is expected.

Action combobox label is exactly `Select a action` (UI grammar). Select exact option `Delete` to avoid `Permanent delete`. Actions observed: Move to, Copy to, Delete, Pin to top, Permanent delete, mark/category/flag operations, Forward to, Forward as attachment, Redirect to. Discover extra fields after selecting an action rather than guessing their labels.

New drafts show `Stop processing more rules` checked. `Run rule now` appears after the draft becomes complete, unchecked. Save becomes enabled only after valid name/condition/action. `Discard` returns to the list without saving.

## Recovery

- AX dropdown can report expanded without listing options; use a focused DOM snapshot or option read. If collapsed after click, inspect and retarget before retrying.
- Scope `clear` buttons: Settings search and rule search both expose them. Filling rule search with `''` avoids ambiguity.
- Scope `More actions` to the exact row; its menu contains Run rule now, Edit rule, Delete rule, and move commands. Do not invoke a mutation while inspecting.
- For read-only probes, discard drafts and restore the previous search/expansion state. Leave user-owned tabs open.
