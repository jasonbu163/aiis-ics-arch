# AIIS ICS Architecture frontend design baseline

Chinese version: [DESIGN.zh-CN.md](DESIGN.zh-CN.md)

Use this baseline when designing or refactoring Core workspaces in `frontend-js`, including planning, acquisition, equipment status, and process monitoring. Keep the shell restrained, data readable, and controls accessible on desktop and narrow screens. Module-specific visuals can live within the content area. Apply this project baseline first and use the shared `frontend-ui` skill for general guidance. Reuse shared components and light and dark theme tokens. Accessibility, locale completeness, and API-contract fidelity remain release checks. [Theme and tokens](src/styles/theme.css)

## Page layout and workspace switching

Two-section and three-section layouts describe the vertical order within one main card.

| Main card | First section | Second section | Third section |
| --- | --- | --- | --- |
| Two sections | Title, optional card status, and whole-card actions | Main content | — |
| Three sections | Title, optional card status, and whole-card actions | Dedicated filters or tools | Main content |

- Choose by task. A view that opens directly to results uses two sections. Give a dedicated search, time-range, or analysis toolbar its own section when users need it. A compact toggle that changes how the same data is shown can stay in the current header or toolbar.
- Keep filter and content insets aligned. Place row actions next to their records and pagination after the results. Let tools wrap on narrow screens and allow wide tables to scroll horizontally.
- Add a compact switch card above the main card when the same page has at least two independent workspaces available to the current user and switching changes the main card as a unit. Update the relevant title, actions, tools, and content for the selected workspace. Show the main card directly when only one workspace is available. Either main-card layout can follow the switch card. Use `BaseCard` and the shared `card-action-segmented` control. [Main card](src/components/common/BaseCard.vue) · [Process configuration](src/app/monitor/views/observations/admin.vue)

## Card header, status, and actions

- Align the title and any help trigger left. Place a whole-card status on the right, immediately before the action group. Show it when supported by actual card-level facts. Keep record-level status in its row.
- Use one visible status summary with text and semantic color. A single status uses a static label. For multiple statuses, summarize the highest-priority item and add a chevron to reveal the details. Prioritize warnings over routine states. Use an opaque neutral theme surface, a thin border, a light shadow, a small “Status details” heading, and divided rows with readable names and values. Support hover, keyboard activation, and tap. Allow dismissal with Escape or an outside click or tap. Keep the summary and its details reachable when the header wraps.
- Use text labels by default for header actions, with Refresh last when present. Use the shared large `ActionButton` for header and toolbar actions, and the small `row` variant in a centered `row-actions` group for ordinary table row actions. The current theme uses 40px and 24px heights respectively. Use `table-actions` for page action groups. Primary actions use the theme’s primary fill, and secondary actions use its lower-emphasis style. [Shared ActionButton](src/components/common/ActionButton.vue) · [Theme styles](src/styles/theme.css)

## Tooltip

Use the themed Element Plus Tooltip for short explanations of a term, time convention, or action. Keep essential information visible in the workspace. Anchor title help at `bottom-start` and prefer `top` for short tool-button hints. Allow the floating layer to adjust to available space. Use a focusable, accessibly named trigger and support hover, keyboard focus, and touch access. Escape dismisses the tooltip. Verify the theme and placement in light and dark modes and on narrow screens. [Plan list title and tool-button help](src/app/plan/components/TaskPage.vue)

## Dialog layout

Use the shared `standard-form-dialog` shell and build the dialog in vertical sections.

| Dialog | First section | Second section | Third section | Fourth section |
| --- | --- | --- | --- | --- |
| Three sections | Title and optional dialog-wide actions | Form, details, or table | Footer | — |
| Four sections | Title and optional dialog-wide actions | Dedicated filters or tools | Form, details, or table | Footer |

- Align the title left and match the main-card title size and weight. The Core title reference is 16px, weight 590, with a 1.35 line height. Align dialog-wide actions right and put Refresh at the far right when present.
- Align the tool and content insets. Let long content scroll while the title and footer remain reachable. Right-align Cancel and Save in edit dialogs. Use only Close in read-only dialogs.
- Use four sections when a batch-edit or detail view needs a dedicated tool area. Preserve unsaved batch edits across filtering, pagination, and refresh. Cancel discards the draft without submitting it. Save follows the owning workflow’s rules.

The process-monitoring data-management dialogs for metric-column settings and record details provide local layout references. Both use 16px, weight 590, and a 1.35 line height through local styles. The generic `standard-form-dialog` title in the current theme is still 24px at weight 760. Apply the card-aligned title when creating or refactoring a dialog in an approved UI task. [Process record and metric-column dialogs](src/app/equipment/components/observations/RecordList.vue) · [Current generic dialog styles](src/styles/theme.css)
