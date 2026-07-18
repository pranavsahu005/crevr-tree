# CREVRTREE — Design System & UI Build Spec
### (Paste this whole file into Base44 / Lovable as the build prompt)

---

## 0. What this document is

This is a **design + UX spec**, not a PRD. Your backend (Python + MySQL, JSON tree data) is already built. This document exists so an AI builder (Base44, Lovable, or a human) can generate the **UI only** — homepage + Career Direction tree viewer — and have it come out looking like one coherent product instead of a generic AI template.

Scope is deliberately **small and shippable by Monday**:

```
Search
  ↓
Category (Career / Business / Government / Education)
  ↓
Roadmap (one of ~12)
  ↓
Tree (node → node)
  ↓
Node detail (resources)
```

No login. No AI chat. No recommendation engine. Twelve roadmaps, one JSON tree schema, one admin panel (already scoped separately). The UI's only job is to make that tree feel alive, warm, and instantly understandable to a 16-year-old in a village and a 45-year-old shopkeeper at the same time.

---

## 1. Design Philosophy

**The metaphor is literal, not decorative.** This is not "a website with a tree icon." Every career/business/government path IS a tree: a seed (the starting decision), roots (prerequisites), a trunk (the core path), branches (choices), and leaves (outcomes/jobs). The UI should make a user feel like they're watching something grow, not scrolling a database.

Four non-negotiable rules:

1. **Warm, not dark.** No dark mode, no glassmorphism, no neon, no cyberpunk, no gaming aesthetic. Backgrounds are cream/warm-white. This must look like it belongs in a school, not a SaaS dashboard.
2. **Clarity beats decoration.** Every animation must help someone understand the tree faster, or it doesn't ship. No animation "because it looks cool."
3. **One visual identity per category.** Doctor trees are not the same color as Government trees. The user should recognize *what kind* of path they're looking at from color alone, before reading a single word.
4. **Zero jargon.** Copy is written for someone who has never used a "dashboard" or "flow" before. No "CTA," no "workflow," no "engine" language anywhere in the UI text itself.

**Signature element:** the tree itself — an organic, hand-drawn-feeling node-and-branch diagram (rounded connectors, leaf-shaped completion markers) that grows downward as you scroll, with each category rendered in its own living color. This is the one thing CREVRTREE is remembered for. Everything else on the page stays quiet so this can be the star.

---

## 2. Design Tokens

### 2.1 Color System

**Base / neutral palette** (used everywhere — background, text, cards):

| Token | Hex | Use |
|---|---|---|
| `--cream` | `#FFF8E7` | Page background |
| `--warm-white` | `#FFFDF8` | Card background |
| `--earth-brown` | `#6B4A2E` | Primary body text |
| `--soft-brown` | `#9C7B58` | Secondary text / captions |
| `--border-soft` | `#F0E4CC` | Card borders, dividers |
| `--honey-amber` | `#FFC020` | Primary accent (CTAs, active states) |
| `--honey-amber-dark` | `#E0A000` | Hover/pressed state of accent |

**Category identity colors** (each roadmap is tagged with one of these; used for its tree's connectors, node fills, and section badge):

| Category | Primary | Secondary | Feel |
|---|---|---|---|
| Medical / Doctor | `#FF6B81` | `#FFE0E6` | Warm rose |
| Education / BCA / BTech | `#4ECDC4` | `#D9FFFB` | Sky teal |
| Government / IAS / Police | `#FF9F43` | `#FFEBD1` | Warm orange |
| Business / Startup / Shop | `#43C97E` | `#DFFFEA` | Leaf green |
| Finance / GST / MSME / Mudra | `#6C5CE7` | `#E6E1FF` | Soft violet |
| Technology / AI Engineer | `#2EAFFF` | `#DFF3FF` | Sky blue |

Rule: category color is used at **~10% opacity for backgrounds**, full strength only for connectors, active node rings, and small badges. Never full-strength as a large fill — this keeps the "warm, soft, crayon" feel instead of looking like a corporate brand color block.

**Tree-specific greens** (used only inside the tree canvas itself, regardless of category — these represent growth/progress, layered over the category color):

```
--leaf-light   #E9FFC7   (unvisited / future node halo)
--leaf-bright  #ABFF2E   (in-progress node halo)
--leaf-deep    #43FF2E   (completed node halo)
--leaf-dark    #476E0C   (connector line stroke)
```

### 2.2 Typography

Two families only:

- **Display (headings, node labels, hero text):** *Baloo 2* (Google Fonts) — rounded, friendly, has real personality without being childish. Weights 600/700.
- **Body (paragraphs, descriptions, buttons, resource tabs):** *Inter* — neutral, extremely readable at small sizes, works in Hindi-English mixed contexts.

Type scale (rem, mobile-first, desktop values in parentheses):

```
Display / Hero      2.25rem / 700   (3.5rem)
Display / Section   1.5rem / 700    (2rem)
Node label          1rem / 600      (1.125rem)
Body                1rem / 400      (1.0625rem)
Caption / meta       0.8125rem / 500
Button label         0.9375rem / 600
```

Line height: 1.5 for body, 1.2 for display. Letter-spacing: 0 everywhere (rounded fonts don't need tracking).

### 2.3 Spacing, Radius, Shadow

```
Spacing scale (px): 4, 8, 12, 16, 24, 32, 48, 64, 96
Radius:
  --radius-sm   8px   (badges, chips)
  --radius-md   16px  (buttons, inputs)
  --radius-lg   24px  (cards)
  --radius-full 999px (node circles, pills)
Shadow (soft only, no hard drop shadows):
  --shadow-card    0 4px 16px rgba(107, 74, 46, 0.08)
  --shadow-hover   0 8px 24px rgba(107, 74, 46, 0.14)
  --shadow-node    0 0 0 6px var(category-color at 12% opacity)  ← "glow" not shadow
```

Grid: 12-column on desktop (max content width 1200px), single column stacked on mobile, 24px gutters desktop / 16px mobile.

---

## 3. Component Library

### Buttons
- **Primary**: `--honey-amber` fill, `--earth-brown` text, `--radius-md`, subtle scale-up (1.03) + shadow-hover on tap/hover, 150ms ease-out.
- **Secondary**: transparent fill, 2px `--honey-amber` border, same text color.
- **Category button** (e.g. "Doctor," "IAS" on category select screen): white card, category-color left border (4px), category icon, grows a soft leaf-halo on hover.

### Inputs / Search
- Single search bar, pill-shaped (`--radius-full`), warm-white fill, soft-brown placeholder text, honey-amber focus ring. Icon: a simple magnifying glass, left-aligned. Placeholder copy: *"Search a career, business, or service…"*

### Cards
- Warm-white background, `--radius-lg`, `--shadow-card`, 24px internal padding. Hover: lift 2px + `--shadow-hover`, 150ms.

### Tree Nodes
- Circle or rounded-rect, `--radius-full` for milestone nodes, `--radius-md` for detail/resource nodes.
- Fill: warm-white. Ring: 3px category color.
- State halos (outer glow, 6px):
  - **Future/locked** → `--leaf-light`, 40% opacity, no ring animation
  - **Current/recommended** → `--leaf-bright`, pulses very subtly (scale 1→1.04→1, 2s loop, opacity-based not size-jarring)
  - **Completed** → `--leaf-deep` solid ring + small leaf-checkmark icon top-right of node
- Connector lines: hand-drawn feeling — use a slight bezier curve, not a straight line, 3px stroke, `--leaf-dark` at 60% opacity. On scroll-into-view, the line "grows" from parent to child (stroke-dashoffset animation, 400ms ease-out) — this is the one animation allowed to feel like "growth."

### Badges / Category chips
- Small pill, category-color background at 15% opacity, category-color text, `--radius-sm`.

### Tabs (node detail panel)
- Underline-style tabs, not boxed. Active tab: honey-amber underline + `--earth-brown` bold text. Inactive: soft-brown, no underline.

---

## 4. Homepage — Section by Section

**Section 1 — Hero**
- Cream background. Left (or top on mobile): headline in Display/Hero — *"India's Career, Business & Government Path — In One Tree."* Subhead in body text, one sentence, explaining in plain words: *"Search anything — becoming a doctor, opening a shop, applying for a passport — and see the exact path, step by step."*
- Right (or below on mobile): the signature visual — a single animated tree silhouette rendered in soft multi-color branches (one branch per category color), gently swaying (CSS transform rotate ±1deg, 6s ease-in-out infinite — barely perceptible, never distracting).
- Below headline: the single search bar (see Component Library). This is the primary action of the entire homepage — everything else is secondary.
- No login button anywhere. No account icon.

**Section 2 — Four Doors** (Career / Business / Government / Education)
- Four large cards in a row (desktop) / stacked (mobile), each with: category icon, category color left-border, one-line description, small preview of 2-3 example roadmaps as text chips (e.g. Career card shows "Doctor," "AI Engineer," "IAS" chips). Clicking a card goes to the Category page (a filtered list of roadmap cards, not a new design — reuse card component).

**Section 3 — How It Works** (3 steps, since it IS a real sequence — numbered markers are justified here)
1. **Search or pick a path** — type what you want to become, or pick from a category.
2. **See the whole tree** — every step, from where you are now to where it leads, in one screen.
3. **Open any step** — get the official link, a free PDF, a video, and a checklist — no searching YouTube.
- Each step: small icon + 2-line copy. No stock illustration, no filler graphic — the icons should be simple line icons matching the tree/leaf visual language.

**Section 4 — Why This Exists**
- Short honest paragraph, in the product's own voice, not marketing voice: explains the real problem (information overload, not lack of information) in 2-3 sentences. No testimonials (there are none yet — don't fake them).

**Section 5 — FAQ**
- 4-5 real questions a first-time student/shopkeeper would ask: "Is this free?", "Do I need to sign in?", "Is this only for tech careers?", "How is this different from YouTube?" Accordion style, honey-amber chevron, soft-brown body text.

**Section 6 — Footer**
- Minimal: logo wordmark, one line tagline, links (About, Career Direction, Business, Government, Education), no social icons unless they actually exist. Cream-on-slightly-darker-cream background (`--border-soft` as footer bg) to close the page softly, not a hard black footer.

---

## 5. Category Page

Simple grid of roadmap cards filtered by the selected category (Career / Business / Government / Education). Each card: roadmap name, category-color accent, one-line description ("From class 10 to becoming a doctor"), small step-count badge ("14 steps"). Click → opens the Tree page for that roadmap.

Include a secondary filter row above the grid: chips for sub-tags if useful (e.g. under Career: "Medical," "Engineering," "Government Jobs") — but only if your JSON data actually supports tags. If not scoped for Monday, skip filters entirely and ship the plain grid; do not fake a filter that doesn't filter anything.

---

## 6. Tree Page (Career Direction) — Core Screen

This is the product. Get this right and everything else is secondary.

**Layout**
- Top: breadcrumb (`Home / Career / Doctor`), roadmap title in Display/Section, one-line description, category badge.
- Below: the tree canvas.
- **Desktop**: tree flows top-to-bottom in a single centered column, generous vertical spacing (64-96px between node tiers), branches fan out left/right symmetrically when a node has 2+ children (like `MBBS → MD` and `MBBS → Research` and `MBBS → Army Doctor` branching from one point). No horizontal scrolling — the canvas width is fixed to viewport, branches compress inward if there are more than 3 at one tier.
- **Mobile**: strictly vertical, single column, no side-branching fan-out — instead, when a node has multiple children, they stack directly below it as a small indented list with a "this step leads to 3 paths" label, each tappable. No pinch-zoom, no pan gesture required — the whole point is that a phone user never needs horizontal scroll or a minimap.
- No minimap, no zoom controls for V1. If the tree is long, the page simply scrolls vertically — this is fine and expected (a "long readable path" is the intended feel, like reading a family tree top to bottom).

**Node interaction**
- Tap/click a node → it expands in place (accordion-style) OR opens a bottom-sheet on mobile / side panel on desktop showing node detail (see Section 7). Prefer bottom-sheet/side-panel — it keeps the tree itself stable and always visible, so the user never loses their place.
- Node expand/open animation: 200ms ease-out scale + fade. No spinner needed at this size.

**Node states** (visual halos as defined in Component Library):
- Locked/future, current/recommended, completed. There is no login, so "completed" is **user-marked** via a simple checkbox inside the node detail panel, stored locally (localStorage is fine here since there's no account system) — this still gives the satisfying "my tree is growing" feeling without needing auth.

---

## 7. Node Detail Panel

Opens as a bottom-sheet (mobile) or right-side panel (desktop, ~380px wide, tree canvas stays visible on the left). Contains tabs, in this order:

1. **Overview** — plain-language 2-3 sentence explanation of this step.
2. **Official Website** — direct link, opens in new tab, labeled by the actual institution name (e.g. "NEET Official Site — nta.ac.in"), never just "Official Website" as a generic label.
3. **Free Resources** — bulleted list: free PDF, free YouTube playlist, free course — each with source name and a direct link. Never say "resource," name the actual thing ("NCERT Biology Class 11 PDF").
4. **Checklist** — a small tappable checklist of concrete requirements for this step (e.g. for NEET: "Age 17+", "Passed PCB in 12th", "Registered on NTA portal"). Checking items is local-only, purely for the user's own tracking.
5. **Mark as done** — single button at the bottom of the panel, toggles the node's completed state on the tree.

Copy voice for this whole panel: written as if a knowledgeable senior/relative is explaining it, not as system documentation. Active voice, no filler ("Here you can find..." → just state the thing).

---

## 8. Responsive Rules

- Mobile-first. Breakpoints: 480px (large phone), 768px (tablet), 1024px (desktop), 1280px (max content width).
- No element should ever require horizontal scrolling on any breakpoint — this includes the tree.
- Tap targets minimum 44x44px on mobile.
- Font sizes never drop below 15px effective on mobile body text.
- Category cards: 4-column desktop grid → 2-column tablet → 1-column mobile stack.
- Search bar is always the first interactive element on screen at every breakpoint, never buried below a hero image.

---

## 9. States

- **Loading**: skeleton shapes matching the card/node shape (rounded rects in `--border-soft`, subtle shimmer left-to-right, 1.2s loop). Never a generic spinner on the tree canvas — use tree-shaped skeletons (a faint gray branch outline) so the loading state still feels on-brand.
- **Empty** (e.g. search with no results): friendly, direct copy — *"Nothing found for '[query]' yet. Try Doctor, IAS, or Startup."* — plus quick-link chips to the 12 seeded roadmaps. Never a bare "No results."
- **Error**: plain language, states what happened and what to do — *"This page didn't load. Refresh, or go back home."* No apologetic tone, no technical error codes shown to the user.

---

## 10. Animation Principles (the whole list — do not add more)

1. Tree connector lines "grow" (stroke-draw) into view on scroll — the one signature motion.
2. Hero tree silhouette sways very subtly, always, ambient.
3. Node hover/tap: 150-200ms scale + halo brighten.
4. Node detail panel: slide/fade in, 200ms.
5. Button press: scale 1.03 + shadow, 150ms.
6. Accordion/FAQ: height auto-animate, 200ms.

That's it. No parallax, no confetti, no page-transition wipes, no cursor-follow effects. Respect `prefers-reduced-motion` — disable #1 and #2 for users who have it set.

---

## 11. Accessibility Baseline

- Color is never the only signal for node state — always pair halo color with an icon (lock icon / clock icon / leaf-checkmark icon).
- All interactive elements have visible keyboard focus rings (2px honey-amber-dark outline, offset 2px).
- Contrast: body text (`--earth-brown` on `--cream`) meets AA at minimum; verify category-color-on-white badge text meets AA (darken category color for text use if needed, keep full saturation only for rings/fills).
- All tabs/accordions are keyboard-navigable (arrow keys / enter).

---

## 12. Data Shape (for reference only — backend already owns this)

The UI should render straight from a JSON tree like:

```json
{
  "id": "mbbs",
  "name": "MBBS",
  "category": "medical",
  "description": "...",
  "resources": {
    "official": {"label": "NEET Official Site", "url": "..."},
    "free": [{"type": "pdf", "label": "...", "url": "..."}],
    "checklist": ["Age 17+", "Passed PCB in 12th"]
  },
  "children": ["md", "research", "army-doctor"]
}
```

UI should not assume fixed depth or fixed branch count — render recursively so new roadmaps added via the admin panel work automatically without UI changes.

---

## 13. How to use this with Base44 / Lovable

Paste this entire file as-is into the builder as your instructions. If the tool asks you to break the request into steps, build in this order and confirm each looks right before moving to the next:

1. Design tokens + component library (Sections 2-3) as a base theme.
2. Homepage (Section 4).
3. Category page (Section 5).
4. Tree page + node detail panel (Sections 6-7) — this is the hardest and most important; give it the most iteration.
5. Responsive pass + states + accessibility (Sections 8-11).

Keep every roadmap's category color wired to the token table in Section 2.1 — do not let the builder invent its own palette per page.
