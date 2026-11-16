# Pattern rules for setup and settings

Each rule says what to look for, why it matters, and the shape of the fix. "House" marks a preference of this skill's owner that goes further than the cited guidance.

## Contents

- States to review
- Prerequisites and unavailable controls
- The setup card
- Getting there and back
- Detection and defaults
- Multi-step setup
- Feedback
- Words
- Sources

## States to review

Open each of these before judging a screen. The builder's own profile usually sits in the fourth and never shows the first two.

1. Nothing set up (first run, empty lists).
2. A prerequisite is missing: something this screen needs is configured somewhere else.
3. Partly set up: the prerequisite exists and the choice has not been made.
4. Working.
5. Failed: an error, offline, permission refused.
6. Undone: the prerequisite was removed after things worked.

## Prerequisites and unavailable controls

- **A section whose controls all depend on a missing prerequisite shows one setup card in their place** (house, after NN/g's "do not default to totally empty states" and "link directly to the steps"). A panel of controls that cannot work reads as broken, and each one needs its own explanation.
- **One control among working ones is unavailable: keep it visible, say why beside it, and give the way to unlock it.** A bare disabled control gives no reason, and a native `disabled` element leaves the tab order, so keyboard and screen-reader users never reach an explanation attached to it. Prefer a focusable control with `aria-disabled` and visible reason text. Hide a control only when the user has no need to know the feature exists.
- **Nothing looks usable that is not.** Check for: a dropdown with one option, an editable field beside text saying it has no effect, a toggle that flips itself back, a button that does nothing until something else is filled in. Each one costs the user an action and teaches them the screen is unreliable.
- **A warning never sits beside a control that contradicts it.** If the row cannot work, the row does not offer its control.
- **Dependent settings read as dependent.** Put the parent first and the children under it, and show the children only when the parent makes them meaningful. GOV.UK advises keeping conditionally revealed content to a single simple question.

## The setup card

Contents, in this order (Carbon and Atlassian both ask for what it is, why it is empty, and a next step, with one primary action):

```
Connect a password manager to use Logins            what is missing, in the user's words
Logins lets agents sign in to websites with your    what this section does once it works
saved passwords and keep the ones they create.
Found Lockbox on this computer (dana@example.com).  what was detected, if anything
[ Set up Lockbox ]                                   one primary action
Opens Secrets, where connections are kept for       where the button leads and why,
every feature, and brings you back here.            said as what the button does
```

- **The button is the only route the card gives.** "It is set up under Secrets" reads as an instruction, and a careful reader will go there by hand and miss everything the button prepares. Say where the button leads, after the button.
- The button's label says what will happen next. "Connect" on a button that only navigates overpromises.
- The card replaces the controls. It is not a banner above them.
- Leave out jokes, illustrations that push the action below the fold, and links to unrelated areas.

## Getting there and back

- **A route written in a sentence becomes a control.** "Add a provider in Settings > Secrets" makes the user find Secrets, find the form, and remember why they came. The control goes to the exact place: the right section, the form open, the relevant option already chosen (NN/g: link directly to the steps that complete the task).
- **The destination knows why the user arrived.** Say so on arrival ("Setting up Logins") and label the finishing action with the return ("Connect and go back to Logins").
- **Finishing returns the user to where they started, now working** (house). The original section shows its controls with the new thing already selected and a line confirming the feature works. Cancelling returns too.
- **The fix is offered where the user looks.** If walkers went to screen A and the control lives on screen B, put the control or a link to it on A instead of teaching users to go to B.

## Detection and defaults

- **Detect before asking** (house; the cited guidance covers reusing earlier answers, not environment detection). Candidates: an installed tool or signed-in account on the machine, an OS setting, a value already entered elsewhere in the product, the only item in a list. Show what was found and let the user change it. A value the product already knows is never typed again.
- **Preselect the value most users want when it is predictable and safe.** A default tells the user what is expected and most people keep it (NN/g, "The Power of Defaults").
- **Require an explicit choice when a wrong default is costly or hard to undo:** anything that spends money, shares data, grants access, or deletes.
- **First in the list is not a default.** Alphabetical order puts the wrong option forward as often as not.
- **A default must not contradict the control that enables it.** "Automatic backups: on" with "Schedule: manually" lets the user believe they are finished.
- **When there is exactly one valid choice, make it.** A newly connected account that is the only candidate gets selected.

## Multi-step setup

- **Three or more dependent steps, or steps in more than one place, get a guided flow started from where the user already is** (house, after NN/g on wizards: suited to infrequent setup, novice users, and steps that depend on each other).
- In the flow: name the steps up front and mark the current one, allow going back without losing entries, let the user leave and resume, prefill everything detected, and end on the working state with a confirmation.
- **Independent settings stay a plain page.** A wizard over unrelated options slows everyone, and repeat users need a direct route.
- **A short checklist with status and a button per item** is the lighter option when the steps are few and can be done in any order.
- **Ask only for what is needed, and mark what is optional.** Every extra field raises the perceived effort.
- Keep progressive disclosure to two levels. A third level is a sign the content needs regrouping.

## Feedback

- **Every action answers where the user acted:** what changed and whether it took. Individual settings apply at once (Microsoft's app settings guidance); a group of related fields gets an explicit save and a visible saved state.
- **A refusal names what is missing and offers the way to it.** "Check your settings" sends the user hunting. "Choose a destination" with the field marked, or "Set a passphrase" with a button, does not.
- **Completion is stated.** When a multi-part setup becomes whole, say that the feature now works, at the place the user started.
- **A message that no longer applies goes away** when its cause is fixed, including when it is fixed on another screen.

## Words

- **Labels use the user's words for the outcome**, not the implementation's nouns. A row title is a decision the user can make; a fragment that only makes sense after reading the help is not.
- **Anything required to proceed is carried by a heading, a label, or a control.** Helper text is for nuance. Most users never read it, so a step that appears only there is a step most users never see.
- **Options state what will happen** ("Ask me on this Mac", "Refuse the request"), and a term the user may not know is defined once, where it first appears.
- **One idea per sentence of help.** A paragraph that packs the rule, the exception, the mechanism, and a recommendation gets skipped whole.

## Sources

- NN/g, "Designing Empty States in Complex Applications": https://www.nngroup.com/articles/empty-state-interface-design/
- Carbon Design System, "Empty states": https://carbondesignsystem.com/patterns/empty-states-pattern/
- Atlassian Design System, "Empty state": https://atlassian.design/components/empty-state/usage
- Smashing Magazine, "Usability Pitfalls of Disabled Buttons": https://smashingmagazine.com/2021/08/frustrating-design-patterns-disabled-buttons/
- Adrian Roselli, "Don't Disable Form Controls": https://adrianroselli.com/2024/02/dont-disable-form-controls.html
- NN/g, "Button States: Communicate Interaction": https://www.nngroup.com/articles/button-states-communicate-interaction/
- GOV.UK Design System, "Radios" (conditional reveal): https://design-system.service.gov.uk/components/radios/
- NN/g, "The Power of Defaults": https://www.nngroup.com/articles/the-power-of-defaults/
- NN/g, "Wizards: Definition and Design Recommendations": https://www.nngroup.com/articles/wizards/
- NN/g, "Progressive Disclosure": https://www.nngroup.com/articles/progressive-disclosure/
- NN/g, "4 Principles to Reduce Cognitive Load in Forms": https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/
- Microsoft, "Guidelines for app settings": https://learn.microsoft.com/en-us/windows/apps/design/app-settings/guidelines-for-app-settings
- NN/g, "10 Usability Heuristics": https://www.nngroup.com/articles/ten-usability-heuristics/
- NN/g, "Severity Ratings for Usability Problems": https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/
