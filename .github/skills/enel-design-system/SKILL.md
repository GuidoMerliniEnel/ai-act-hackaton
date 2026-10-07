---
name: enel-design-system
description: 'Enel Design System theme for the EnerGuard Zensical documentation site. Use when modifying colors, typography, layout, dark mode, or theme overrides. Triggers on "change theme colors", "update dark mode", "fix styling", "adjust typography", or "modify Zensical theme".'
---

# Enel Design System — Zensical Theme

Adapted from the [Enel GICT Reference Architectures](https://github.com/ENEL-GICT-PTG/reference_architectures)
skill of the same name.

## Scope

- Theme config: `zensical.toml` — `[project.theme]` section
- CSS overrides: `docs/stylesheets/extra.css`
- Logo and favicon: `docs/assets/images/`
- Template overrides: `overrides/`

## Color Tokens

| Token               | Hex       | Usage                         |
| ------------------- | --------- | ----------------------------- |
| `--enel-primary`    | `#d3135a` | Magenta — primary brand color |
| `--enel-secondary`  | `#0047cc` | Ocean blue — accent / links   |
| `--enel-dark-ocean` | `#003eb3` | Darker ocean shade            |
| `--enel-dark-green` | `#008c5a` | Dark green                    |
| `--enel-green`      | `#55be5a` | Green                         |
| `--enel-light-blue` | `#41b9e6` | Light blue (dark-mode links)  |
| `--enel-black`      | `#0e141a` | Tabs bar, footer              |
| `--enel-smoke`      | `#667790` | Muted text                    |
| `--enel-dark-snow`  | `#c2cddd` | Borders, dividers             |
| `--enel-snow`       | `#eff2f7` | Light backgrounds             |
| `--enel-orange`     | `#ff5a0f` | Warning accent                |
| `--enel-yellow`     | `#ffc82c` | Highlight                     |
| `--enel-red`        | `#eb0a00` | Error                         |
| `--enel-success`    | `#13ce66` | Success                       |

## Oversight Level Colors

Used in docs for the routing matrix, consistent with the dashboard:

| Level | Token            |
| ----- | ---------------- |
| HIC   | `--enel-red`     |
| HITL  | `--enel-orange`  |
| HOTL  | `--enel-success` |

## Rules

- Always use `--enel-*` custom properties; hardcode hex values only in the `:root` token block.
- Light scheme selector `[data-md-color-scheme="enel"]`, dark `[data-md-color-scheme="slate"]`.
- `primary = "custom"` and `accent = "custom"` in `zensical.toml`: colors come from CSS.
- Tabs bar: `background-color: var(--enel-black)`, white text, `!important` on hover/active.
- Font: Inter for text (web substitute for the proprietary Roobert), Roboto Mono for code.
- Keep WCAG 2.1 AA contrast (OP36 4.7).
