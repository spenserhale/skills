---
name: wp-components
description: WordPress Gutenberg UI component library reference — available components, usage patterns, and categories for building block editor interfaces.
---

# WordPress Gutenberg Components

A skill for working with the `@wordpress/components` package — the shared UI component library used across the WordPress block editor and dashboard.

## When to use

Activate this skill when the user asks to:

- Build or modify Gutenberg blocks that need UI controls
- Choose the right WordPress component for a specific UI pattern
- Use inspector controls, toolbars, or settings panels in blocks
- Work with forms, modals, popovers, or navigation in the block editor

## Latest Docs

- **Storybook (interactive examples):** https://wordpress.github.io/gutenberg/?path=/docs/components-introduction--docs
- **Developer handbook:** https://developer.wordpress.org/block-editor/reference-guides/components/
- **Package setup guide:** https://developer.wordpress.org/block-editor/reference-guides/packages/packages-components/
- **Source & changelog:** https://github.com/WordPress/gutenberg/tree/trunk/packages/components

## Installation & Setup

```bash
npm install @wordpress/components --save
```

The package requires an ES2015+ environment. If your build target doesn't support this, include the polyfill from `@wordpress/babel-preset-default`.

Components are also available globally as `wp.components` when working within the WordPress admin.

### CSS Styles

**Within WordPress** — add `wp-components` as a dependency of your plugin's stylesheet:

```php
wp_enqueue_style( 'my-plugin-style', plugins_url( 'style.css', __FILE__ ), array( 'wp-components' ) );
```

**Outside WordPress** — import the stylesheet directly:

```js
import '@wordpress/components/build-style/style.css';
```

An RTL version is available at `@wordpress/components/build-style/style-rtl.css`.

### Basic Usage

```jsx
import { Button, TextControl } from '@wordpress/components';

export default function MyButton() {
    return <Button variant="primary">Click Me!</Button>;
}
```

```jsx
// When using in a block's edit function
import { InspectorControls } from '@wordpress/block-editor';
import { PanelBody, ToggleControl } from '@wordpress/components';
```

### TypeScript

Extract component prop types using `React.ComponentProps`:

```tsx
import type { ComponentProps } from 'react';
import { Button } from '@wordpress/components';

export default function MyButton( props: ComponentProps< typeof Button > ) {
    return <Button { ...props }>Click Me!</Button>;
}
```

### Popover Slot Setup

To control where popovers render in the DOM, wrap your app with `SlotFillProvider` and include a `Popover.Slot`:

```jsx
import { SlotFillProvider, Popover } from '@wordpress/components';

function App() {
    return (
        <SlotFillProvider>
            { /* Your components */ }
            <Popover.Slot />
        </SlotFillProvider>
    );
}
```

---

## Component Reference Files

Detailed offline references for each component are in the `references/` directory (e.g., `references/button.md`). Each file contains the full upstream README with props, usage examples, and design guidelines plus frontmatter with permalink URLs to fetch the latest docs when needed.

To update a reference: fetch the latest from `https://raw.githubusercontent.com/WordPress/gutenberg/trunk/packages/components/src/{component-dir}/README.md`.

## Component Index

Components are organized by category below. For full details on any component, read its reference file.

### Form Inputs

| Component | Description |
|-----------|-------------|
| `TextControl` | Single-line text input with label |
| `TextareaControl` | Multi-line text input |
| `NumberControl` | Numeric input with increment/decrement |
| `InputControl` | Low-level input with prefix/suffix slot support |
| `SelectControl` | Dropdown select menu |
| `CustomSelectControl` | Styled dropdown with custom option rendering |
| `ComboboxControl` | Searchable dropdown (select + autocomplete) |
| `CheckboxControl` | Single checkbox with label |
| `RadioControl` | Radio button group |
| `ToggleControl` | On/off switch toggle |
| `ToggleGroupControl` | Segmented button group for mutually exclusive options |
| `RangeControl` | Slider with optional number input |
| `FormTokenField` | Tag/token input for multiple values |
| `FormToggle` | Standalone toggle switch (no label) |
| `FormFileUpload` | File upload button |
| `SearchControl` | Search input with clear button |
| `Autocomplete` | Inline autocomplete suggestions (e.g., slash commands) |

### Color & Gradients

| Component | Description |
|-----------|-------------|
| `ColorPalette` | Grid of color swatches with custom color option |
| `ColorPicker` | Full color picker with hex/rgb/hsl inputs |
| `ColorIndicator` | Small circular color swatch preview |
| `GradientPicker` | Gradient editor with stop controls |
| `CustomGradientPicker` | Advanced gradient builder with type switching |
| `DuotonePicker` | Two-tone color filter picker |
| `DuotoneSwatch` | Preview swatch for a duotone filter |

### Date & Time

| Component | Description |
|-----------|-------------|
| `DatePicker` | Calendar-based date picker |
| `DateTimePicker` | Combined date and time picker |
| `TimePicker` | Time-only picker |

### Layout & Spacing

| Component | Description |
|-----------|-------------|
| `Flex` | CSS flexbox container |
| `FlexItem` | Child of `Flex` |
| `FlexBlock` | `FlexItem` that fills available space |
| `HStack` | Horizontal flex layout (shorthand) |
| `VStack` | Vertical flex layout (shorthand) |
| `Grid` | CSS grid container |
| `Spacer` | Adds spacing between elements |
| `Divider` | Visual separator line |

### Typography

| Component | Description |
|-----------|-------------|
| `Heading` | Semantic heading (h1–h6) with size presets |
| `Text` | Text element with typography props |
| `Truncate` | Truncates overflowing text with ellipsis |
| `TextHighlight` | Highlights matching text within a string |
| `FontSizePicker` | Font size selector with presets and custom input |

### Containers & Surfaces

| Component | Description |
|-----------|-------------|
| `Card` | Bordered content container |
| `CardHeader` | Header area for `Card` |
| `CardBody` | Body content area for `Card` |
| `CardFooter` | Footer area for `Card` |
| `CardDivider` | Divider within a `Card` |
| `CardMedia` | Media area within a `Card` |
| `Panel` | Collapsible section container |
| `PanelBody` | Collapsible body within a `Panel` |
| `PanelHeader` | Header for a `Panel` |
| `PanelRow` | Row layout within a `Panel` |
| `Surface` | Background surface with elevation support |
| `Elevation` | Applies box-shadow elevation to a surface |

### Buttons & Actions

| Component | Description |
|-----------|-------------|
| `Button` | Primary action element (primary, secondary, tertiary, link variants) |
| `ButtonGroup` | Groups related buttons together |
| `ExternalLink` | Link that opens in a new tab with external icon |
| `Dropdown` | Button that reveals a popover on click |
| `DropdownMenu` | Button with a menu of actions |

### Feedback & Status

| Component | Description |
|-----------|-------------|
| `Notice` | Informational banner (success, warning, error, info) |
| `NoticeList` | Renders a list of `Notice` components |
| `Snackbar` | Temporary toast notification |
| `SnackbarList` | Renders a list of `Snackbar` components |
| `Spinner` | Loading spinner indicator |
| `ProgressBar` | Horizontal progress bar |
| `Tip` | Informational tip with lightbulb icon |

### Overlays & Dialogs

| Component | Description |
|-----------|-------------|
| `Modal` | Dialog overlay with title, close button, and focus trap |
| `ConfirmDialog` | Simple yes/no confirmation modal |
| `Popover` | Floating content anchored to a reference element |
| `Guide` | Multi-step onboarding modal |
| `GuidePage` | Single page within a `Guide` |
| `Tooltip` | Hover/focus tooltip for additional context |

### Navigation

| Component | Description |
|-----------|-------------|
| `TabPanel` | Tabbed content switcher |
| `NavigatorProvider` | Client-side screen navigation context |
| `NavigatorScreen` | Screen within a `NavigatorProvider` |
| `NavigatorButton` | Navigates to a `NavigatorScreen` |
| `NavigatorBackButton` | Navigates back in the navigator stack |
| `NavigableMenu` | Keyboard-navigable menu (arrow keys) |
| `MenuGroup` | Groups related menu items |
| `MenuItem` | Single item in a menu |
| `MenuItemsChoice` | Radio-like selectable menu items |

### Toolbar

| Component | Description |
|-----------|-------------|
| `Toolbar` | Horizontal toolbar container |
| `ToolbarButton` | Button within a `Toolbar` |
| `ToolbarGroup` | Groups related toolbar items |
| `ToolbarItem` | Generic item within a `Toolbar` |
| `ToolbarDropdownMenu` | Dropdown menu within a `Toolbar` |

### Dimension & Spacing Controls

| Component | Description |
|-----------|-------------|
| `BoxControl` | Linked/unlinked inputs for top/right/bottom/left values |
| `BorderControl` | Single border editor (width, style, color) |
| `BorderBoxControl` | Editor for all four sides of a border |
| `UnitControl` | Numeric input with unit dropdown (px, em, rem, %) |
| `AnglePickerControl` | Circular angle picker (0–360°) |
| `FocalPointPicker` | Image focal point selector |
| `AlignmentMatrixControl` | 3×3 grid for selecting alignment position |

### Tools Panel

| Component | Description |
|-----------|-------------|
| `ToolsPanel` | Container for block support controls with reset functionality |
| `ToolsPanelItem` | Individual control within a `ToolsPanel` |

### Data & Trees

| Component | Description |
|-----------|-------------|
| `TreeSelect` | Hierarchical dropdown select (e.g., category trees) |
| `TreeGrid` | Accessible tree table with keyboard navigation |
| `TreeGridRow` | Row within a `TreeGrid` |
| `TreeGridCell` | Cell within a `TreeGridRow` |
| `TreeGridItem` | Focusable item within a `TreeGridCell` |
| `QueryControls` | Pre-built controls for post query parameters |

### Drag & Drop

| Component | Description |
|-----------|-------------|
| `Draggable` | Makes an element draggable |
| `DropZone` | Drop target area for drag-and-drop |

### Utility & Misc

| Component | Description |
|-----------|-------------|
| `SlotFillProvider` | Context provider for the SlotFill system |
| `Slot` | Renders content inserted via matching `Fill` |
| `Fill` | Inserts content into a matching `Slot` |
| `Animate` | Wraps children with CSS animation |
| `Disabled` | Disables all interactive children |
| `ResponsiveWrapper` | Maintains aspect ratio for responsive elements |
| `ResizableBox` | Resizable container with drag handles |
| `SandBox` | Renders content in a sandboxed iframe |
| `ScrollLock` | Prevents body scrolling while mounted |
| `FocusableIframe` | Iframe that participates in focus management |
| `Icon` | Renders an SVG icon (from `@wordpress/icons` or custom) |
| `Dashicon` | Legacy Dashicon font icon (prefer `Icon`) |
| `Placeholder` | Block placeholder UI for initial setup state |
| `BaseControl` | Wraps a control with label, help text, and ID generation |
| `VisuallyHidden` | Hides content visually but keeps it accessible to screen readers |
| `Composite` | Accessible composite widget (roving tabindex) |
| `CompositeGroup` | Group within a `Composite` |
| `CompositeItem` | Focusable item within a `Composite` |
| `View` | Polymorphic base component (renders any HTML element) |

### Higher-Order Components & Hooks

| Export | Description |
|--------|-------------|
| `withNotices` | HOC that injects notice creation functions |
| `withFocusReturn` | HOC that returns focus to the previous element on unmount |
| `withFocusOutside` | HOC that detects clicks/focus outside a component |
| `withConstrainedTabbing` | HOC that traps tab key within a container |
| `withFallbackStyles` | HOC for computing styles from rendered DOM |
| `withFilters` | HOC that applies WordPress hook filters to a component |
| `withSpokenMessages` | HOC that adds ARIA live region announcements |
| `navigateRegions` | HOC for region-based keyboard navigation |
| `useNavigator` | Hook for programmatic navigator navigation |

---

## Common Patterns

### Inspector sidebar controls

```jsx
import { InspectorControls } from '@wordpress/block-editor';
import { PanelBody, RangeControl, ToggleControl } from '@wordpress/components';

function Edit({ attributes, setAttributes }) {
    return (
        <>
            <InspectorControls>
                <PanelBody title="Settings">
                    <RangeControl
                        label="Columns"
                        value={attributes.columns}
                        onChange={(columns) => setAttributes({ columns })}
                        min={1}
                        max={6}
                    />
                    <ToggleControl
                        label="Show title"
                        checked={attributes.showTitle}
                        onChange={(showTitle) => setAttributes({ showTitle })}
                    />
                </PanelBody>
            </InspectorControls>
            {/* block content */}
        </>
    );
}
```

### Block toolbar controls

```jsx
import { BlockControls } from '@wordpress/block-editor';
import { ToolbarGroup, ToolbarButton } from '@wordpress/components';
import { edit, trash } from '@wordpress/icons';

<BlockControls>
    <ToolbarGroup>
        <ToolbarButton icon={edit} label="Edit" onClick={handleEdit} />
        <ToolbarButton icon={trash} label="Delete" onClick={handleDelete} />
    </ToolbarGroup>
</BlockControls>
```

### Confirmation dialog

```jsx
import { useState } from '@wordpress/element';
import { Button, ConfirmDialog } from '@wordpress/components';

const [isOpen, setIsOpen] = useState(false);

<Button variant="tertiary" isDestructive onClick={() => setIsOpen(true)}>
    Delete
</Button>
{isOpen && (
    <ConfirmDialog
        onConfirm={() => { handleDelete(); setIsOpen(false); }}
        onCancel={() => setIsOpen(false)}
    >
        Are you sure you want to delete this item?
    </ConfirmDialog>
)}
```
