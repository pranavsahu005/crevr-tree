# AI Agent Guidelines (AGENTS.md)

This file contains crucial instructions, style rules, and design philosophies for **CrevrTree**. It is automatically loaded by the AI assistant system to maintain design continuity, codebase integrity, and UI excellence.

---

## 🎨 Visual Identity & Theme: Cultural Neobrutalism

CrevrTree uses a signature **High-Contrast Neobrutalist** visual language merged with a clean, warm cultural palette. Do not degrade these visual specifications in future edits.

### 1. Typography Pairings
*   **Headings / Display:** `"Playfair Display"`, serif — elegant, authoritative, and organic.
*   **Interface Sans:** `"Inter"`, sans-serif — clean, highly legible, modern.
*   **Technical / Status Data:** `"JetBrains Mono"`, monospace — for milestone indices, statistics, tags, and status labels.

### 2. Core Color Palette
*   **Dark Contrast:** `#2D2D2D` (Ink/Charcoal) — used for all borders, prominent text, and thick drop-shadows.
*   **Background Canvas:** `#FFFFFF` (White) layered with a clean `#EAE6E1` dot grid backdrop:
    `bg-[radial-gradient(#EAE6E1_1.5px,transparent_1.5px)] [background-size:24px_24px]`.
*   **Borders:** Always use heavy, visible solid borders of `#2D2D2D` with width `border-2`.
*   **Neobrutalist Flat Shadows:**
    *   Container shadows: `shadow-[4px_4px_0px_0px_#2D2D2D]`
    *   Hover displacement: `hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[3px_3px_0px_0px_#2D2D2D]`
    *   Small buttons / badges: `shadow-[2px_2px_0px_0px_#2D2D2D]`

### 3. Connector Path Colors & Styles (SVG Canvas)
*   **Completed Branches:** Thick green paths (`#22C55E`, stroke-width: `4.5px`) representing mastered tracks.
*   **Current/Focus Path:** Active, glowing sky-blue branches (`#0284C7`, stroke-width: `4.5px`) guiding the student's next step.
*   **Locked Future Tracks:** Soft slate dashed paths (`#CBD5E1`, stroke-width: `2.5px`, stroke-dasharray: `5 4`) representing potential paths ahead.

---

## 🏗️ Code Architecture Rules

### 1. Component Modularity
Keep files lightweight and separated into dedicated modules to avoid hitting LLM token limits during edits:
*   `src/types.ts`: Global static TypeScript definitions and interfaces.
*   `src/data.ts`: Career data schemas and Indian specific roadmap directions.
*   `src/components/TreeCanvas.tsx`: Renders the SVG line connections and manages absolute 2D placement.
*   `src/components/TreeNode.tsx`: Interactive milestone cards representing curriculum steps.
*   `src/components/InspectorPanel.tsx`: Dynamic tabbed viewer presenting official portals, free books, and eligibility checklists.
*   `src/components/Navbar.tsx` & `src/components/Footer.tsx`: Core shell layouts.

### 2. State Management Guidelines
*   **Roadmap Selection:** Tracked at root (`App.tsx`) to trigger immediate recalculations of the 2D tree.
*   **Active Selection:** Tracked via `selectedStepId` — highlights corresponding path connections and opens inspector tabs.
*   **Durable Progress Engine:** User milestone completion is persisted via browser local storage (`completedNodes`) to preserve student accomplishments.

---

## 🛑 Strict Scope Boundaries

*   **No Unsolicited API Integrations:** Avoid adding unrequested third-party packages or server-side calls.
*   **Responsive Execution:** Ensure full vertical single-column stacked layout support is activated automatically on small screens, bypassing the absolute coordinate SVG layout which is preserved on desktop.
*   **Literal, Human UI Labels:** Avoid overly dramatic names (e.g. use "Milestone Index", "Interactive Node Inspector" and "CrevrTree" rather than sci-fi telemetry names).
