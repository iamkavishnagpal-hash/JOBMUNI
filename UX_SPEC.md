# JOBMUNI — UX & Design System Specification

## 1. Visual Design Philosophy & Aesthetic Identity
**JOBMUNI** embodies a refined, minimal, high-density enterprise aesthetic inspired by Linear, Vercel, Stripe, and Notion:
- **Tone**: Serious, calm, authoritative, intelligent, global enterprise.
- **Palette**: Obsidian Executive Theme.
  - Deep Canvas: `#090A0F`
  - Elevated Cards: `#12151F`
  - Subtle Borders: `#1E2333`
  - Accents: Emerald `#10B981` (High Fit / Verified), Indigo `#6366F1` (Action / Navigation), Amber `#F59E0B` (Approval Gate / Warnings).
- **Typography**:
  - Primary UI & Prose: `Inter`
  - Metrics, Data Scores & Code: `JetBrains Mono`

---

## 2. Multi-Viewport Responsive Matrix

JOBMUNI is engineered **Mobile-First** and strictly tested across all standard viewport tiers with **0px horizontal overflow**:

| Viewport Tier | Width | Target Form Factor | Layout Behavior |
| :--- | :--- | :--- | :--- |
| **Micro-Mobile** | `320px` | Ultra-compact phones (iPhone SE 1st gen) | Single column, compact badges, bottom navigation bar, full-screen modals. |
| **Standard Mobile**| `375px` | Standard phones (iPhone Mini / SE 2nd gen) | 2-column metric cards, sticky bottom action bar, card padding `p-4`. |
| **Modern Mobile** | `390px` | Flagship phones (iPhone 14/15/16) | High-contrast touch targets ($\ge 44\text{px}$), swipeable lists. |
| **Tablet** | `768px` | iPad Portrait / Surface | Multi-column grid, compact collapsible sidebar. |
| **Laptop** | `1440px`| MacBook Pro / Ultra-wide | Full desktop sidebar, split-pane detail views, data tables. |
| **Large Desktop** | `1920px`| Full HD Monitors | Expanded data density, multi-panel analytics and Kanban. |

---

## 3. Mobile Navigation & Touch Invariants

- **Desktop**: Left fixed sidebar (`AppSidebar`) with clear section grouping, version tag, and background worker status pulse.
- **Mobile**: Sticky bottom navigation bar (`MobileNavBar`) providing 1-tap thumb access to:
  1. `Dashboard` (Executive cockpit)
  2. `Radar` (Active opportunities)
  3. `CRM` (Recruiters)
  4. `Approvals` (Level 2 human gate)
  5. `Settings` (Config & algorithms)
- **Touch Target Standard**: Every interactive element (buttons, toggles, sliders, chips) has a minimum touch bounding box of $44 \times 44\text{px}$.

---

## 4. State & Feedback Design

Every data-driven view explicitly implements 5 distinct states:
1. **Default**: Rich, readable data rows with transparent scores and badges.
2. **Empty State**: Intentional, professional empty states with clear explanations and immediate call-to-action buttons (e.g. "No active applications yet. Ingest a job to get started.").
3. **Loading State**: Subtle skeleton placeholders; zero layout shifts.
4. **Error State**: Non-blocking toast alerts with retry capabilities and human-readable diagnostic messages.
5. **Approval Staged State**: Unambiguous visual differentiation for pending outbound actions awaiting user sign-off.
