# Developer Documentation (DOCUMENTATION.md)

Welcome to the developer documentation for **CrevrTree**. This document provides an in-depth breakdown of the application architecture, data schemas, rendering mechanics, and styling configurations.

---

## 📂 Codebase File Structure

```
├── /src
│   ├── main.tsx                # Client-side entry point
│   ├── index.css               # Global CSS stylesheet & Tailwind configuration
│   ├── App.tsx                 # Main Application component & State coordinator
│   ├── types.ts                # TypeScript types, interfaces, and enums
│   ├── data.ts                 # Rich curriculum roadmap datasets (Indian Career paths)
│   └── /components
│       ├── Navbar.tsx          # Main header navigation
│       ├── Footer.tsx          # Informative footer & mission details
│       ├── TreeCanvas.tsx      # SVG connection canvas and 2D node map wrapper
│       ├── TreeNode.tsx        # Individual neubrutalist milestone card
│       └── InspectorPanel.tsx  # Tabbed interactive drawer for study materials
├── metadata.json               # App configuration & permissions
├── tsconfig.json               # TypeScript configuration
└── package.json                # Project dependencies and scripts
```

---

## 🛠️ Data Architecture (`src/types.ts` & `src/data.ts`)

### Roadmap Data Schema
Each roadmap consists of multiple checkpoints styled as hierarchical `Step` milestones:

```typescript
export interface Step {
  id: string;               // Unique milestone ID
  name: string;             // Display name (e.g., "UPSC Prelims Strategy")
  desc: string;             // Informative description
  parent?: string;          // Direct preceding step ID (creates the connection branch)
  coords: { x: number; y: number }; // Absolute % coordinates for desktop 2D canvas
  category: 'tech' | 'medical' | 'education' | 'government' | 'business' | 'finance';
  official?: {              // Recommended official enrollment/verification link
    label: string;
    url: string;
  };
  resources?: Array<{       // Publicly-sourced high quality study guides
    label: string;
    url: string;
    type: 'video' | 'book' | 'article';
  }>;
  checklist?: string[];     // Eligibility guidelines or checklist items
  salary?: string;          // Career projection metric
  companies?: string[];     // Direct hiring companies or entities
  colleges?: string[];      // Central academic institutions
  entranceExams?: string[]; // Mandatory central exams (e.g. JEE, NEET, GATE)
}

export interface Roadmap {
  id: string;
  title: string;
  desc: string;
  category: string;
  steps: Step[];
}
```

---

## 📐 SVG Render Mechanics (`src/components/TreeCanvas.tsx`)

The interactive 2D node map matches parent and child positions dynamically to draw bezier connector curves using custom SVG calculations:

1.  **Coordinate Mapping:** Steps define their location in normalized percentage-based coordinates `{ x, y }` relative to the parent tree canvas container.
2.  **Bezier Curve Calculations:**
    For each step that has a `parent` attribute:
    *   Locate the parent step coordinates (`x1, y1`) and child step coordinates (`x2, y2`).
    *   An offset is added to create organic S-curves:
        `const controlOffset = (y2 - y1) / 2.2;`
        `const d = "M ${x1} ${y1} C ${x1} ${y1 + controlOffset}, ${x2} ${y2 - controlOffset}, ${x2} ${y2}";`
3.  **Active Focus Detection:**
    *   **Completed Paths:** If both the parent node and the child node are flagged as complete by the user, the path is styled with a thick **emerald green line** (`#22C55E`).
    *   **Active/Focused Path:** If a parent is completed but the child is pending, or if either node is currently active, the line highlights in **sky blue** (`#0284C7`) to guide the student forward.
    *   **Future Paths:** Future steps render as soft, **dashed slate lines** (`#CBD5E1`) indicating locked pathways.

---

## 📱 Responsiveness & Adaptability

*   **Desktop Viewport:** Full canvas mode uses the SVG coordinates to render a structured, visual tree flow, allowing absolute free-roaming path exploration.
*   **Mobile Viewport:** On devices under `768px` wide, the tree canvas automatically switches to a stacked vertical single-column checklist view. The system renders sequential connector lines between milestones and formats cards in high-density tap targets.

---

## 💾 Local Browser Persistence

To respect the user's progress:
*   Student progress tracking (checkbox completions) are written directly to `localStorage` under `crevrtree_completed_nodes`.
*   This ensures that students can close their browsers and return later to find their progress intact, without requiring a remote database server.
