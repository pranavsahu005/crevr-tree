# CREVRTREE — Career Direction Intelligence Platform

## Overview

CrevrTree is an interactive career direction platform for Indian students and professionals. It visualizes education-to-employment paths as living tree diagrams — making career guidance accessible, visual, and free for everyone from a 10th-standard student in a village to a 45-year-old shopkeeper.

## Core Architecture

```
User → Search → Category → Roadmap → Tree (node canvas) → Node Detail (resources)
```

Two independent but complementary engines:

### 1. Knowledge Graph Engine (Python — offline)
- **Location:** `database/career_generator_v3.py`
- **Output:** 200,000 career paths, 1,023 nodes, 456 edges
- **Node types:** education (220), job_role (260), company (154), skill (124), industry (110), exam (78), certification (75)
- **Edge types:** branch (295), next_step (55), requires_skill (56), can_work_at (50)
- **Output formats:** JSON, JSONL, CSV, YAML, TXT

### 2. Interactive Frontend (React 19 + TypeScript + Vite + Tailwind CSS 4)
- **Location:** `Crevt-Tree-Ai_Studio-main/`
- **12 curated roadmaps** spanning 6 categories
- **Cultural Neobrutalist** design theme — warm cream/white backgrounds, bold borders, Playfair Display headings, Inter body
- **Offline-first:** All progress stored in localStorage
- **Responsive:** Desktop SVG bezier-curve tree → Mobile vertical checklist

## Data Model

### Types (`src/types.ts`)

```typescript
interface Step {
  id: string;
  name: string;
  desc: string;
  official?: OfficialLink;       // Direct govt/institutional portal
  resources?: Resource[];        // Free PDFs, videos, courses
  checklist?: string[];          // Eligibility requirements
  parent: string | null;         // Tree parent reference
  coords: { x: number; y: number }; // SVG position (0-100%)
  salary?: string;               // Expected compensation
  companies?: string[];          // Target employers
  colleges?: string[];           // Top institutions
  entranceExams?: string[];      // Relevant exams
}

interface Roadmap {
  id: string;
  name: string;
  category: 'medical' | 'education' | 'government' | 'business' | 'finance' | 'tech';
  tagline: string;
  steps: Step[];
}
```

### 6 Category Color System

| Category | Primary | Secondary | Hex Pair |
|---|---|---|---|
| Medical | `--medical-primary` | `#FFE0E6` | Rose |
| Education | `--education-primary` | `#D9FFFB` | Teal |
| Government | `--govt-primary` | `#FFEBD1` | Amber |
| Business | `--business-primary` | `#DFFFEA` | Emerald |
| Finance | `--finance-primary` | `#E6E1FF` | Violet |
| Technology | `--tech-primary` | `#DFF3FF` | Sky |

### Node States (visual halos)
- **Locked/Future:** Light green halo (`--leaf-light #E9FFC7`)
- **Current/Active:** Bright green glow + subtle pulse (`--leaf-bright #ABFF2E`)
- **Completed:** Deep green solid ring + leaf-checkmark icon (`--leaf-deep #43FF2E`)

## Current Roadmaps (12)

| # | ID | Name | Category | Steps |
|---|---|---|---|---|
| 1 | `ai-engineer` | AI & Machine Learning Engineer | tech | 5 |
| 2 | `doctor` | Medical Doctor (MBBS) | medical | 5 |
| 3 | `ias-officer` | UPSC Civil Services (IAS) | government | 5 |
| 4 | `startup-founder` | Startup Founder / Entrepreneur | business | 5 |
| 5 | `chartered-accountant` | Chartered Accountant (CA) | finance | 4 |
| 6 | `bca-btech` | Computer Science (BCA/BTech) | education | 5 |
| 7 | `software-engineer` | Full Stack Developer | tech | 5 |
| 8 | `nurse` | Registered Nurse (B.Sc Nursing) | medical | 4 |
| 9 | `police-sub-inspector` | Police Sub-Inspector (SI) | government | 4 |
| 10 | `organic-farmer-agritech` | Organic Farming & Agritech | business | 5 |
| 11 | `bank-po` | Bank Probationary Officer (IBPS/SBI PO) | finance | 4 |
| 12 | `cuet-ug` | CUET UG College Entrance | education | 4 |

## Frontend Component Architecture

### App.tsx — 4 SPA Views
1. **Home** — Hero with search bar, 4 category doors ("Four Doors"), How It Works, FAQ
2. **Category** — Filtered grid of roadmap cards by category
3. **Tree** — Interactive canvas (desktop SVG / mobile checklist) + Inspector panel
4. **About** — Vision, problem/solution, tech stack, ecosystem

### Key Components
- **TreeCanvas.tsx** — SVG tree with bezier-curve connectors, color-coded by category. Mobile: vertical stacked checklist
- **TreeNode.tsx** — Interactive milestone card with neobrutalist styling, category colors, state halos
- **InspectorPanel.tsx** — Tabbed detail panel: Official Portals → Free Material → Checklist → Career Metrics
- **Navbar.tsx** — Sticky nav with brand, category links, search, mobile hamburger
- **Footer.tsx** — 4-column ecosystem footer

### State Management
- **localStorage key:** `crevrtree_completed_nodes` (Record<stepId, boolean>)
- **Toast notifications:** Custom floating toast, auto-dismiss at 4s
- **No login required** — fully anonymous

## Knowledge Graph (Python Engine)

### Taxonomy Scope
- 84 UG degrees, 65 PG degrees, 14 PhD fields, 25 ITI trades, 24 diplomas
- 79 exams (JEE, NEET, UPSC, GATE, CAT, CLAT, IBPS, etc.)
- 258 job roles across 32 categories
- 110 skills, 75 certifications, 142 companies, 110 industries

### Generation Pipeline
```
Taxonomies → NodeFactory (UUID) → CareerPathGenerator → MultiFormatWriter
         ↕                              ↕
  DeduplicationTracker        CheckpointManager (resumable)
```

### Edge Patterns
- Education→Education (progression): 10th→11th→12th
- Education→Exam: 12th PCM→JEE Main
- Exam→Education: cleared exam→college admission
- Education→Job_Role: degree→direct job
- Job_Role→Job_Role: promotion/lateral
- Job_Role→Exam: upskilling
- Certification→Job_Role: cert leads to role
- Skill→Job_Role: enrichment (requires_skill)
- Job_Role→Company: employment (can_work_at)

## Future / Phase 2 (Planned)

**Career Guidance Intelligence Engine** (`database/claude_code_py_prompt_Phase2.md`):
- Rule-based recommendation engine (no external APIs)
- 100+ user profile inputs (education, skills, interests, location)
- Predicts: best/alternative/emerging careers, skill gaps, salary potential
- Confidence scoring with explainability
- Offline, deterministic, ML-ready architecture

## How to Add a New Roadmap

1. Open `Crevt-Tree-Ai_Studio-main/src/data.ts`
2. Add a new `Roadmap` object to `ROADMAPS_DATABASE` array
3. Assign a unique `id`, proper `category`, and `tagline`
4. Define `steps` with each having: `id`, `name`, `desc`, `official` link, `resources`, `checklist`, `parent`, `coords`
5. Ensure step IDs follow a consistent prefix pattern
6. The tree renders automatically — no UI changes needed

## Design Tokens Reference

### Neutral Palette
| Token | Value | Usage |
|---|---|---|
| `--cream` | `#FCFAF7` | Page background |
| `--warm-white` | `#FFFFFF` | Card background |
| `--earth-brown` | `#2D2D2D` | Primary text |
| `--soft-brown` | `#6B7280` | Secondary text |
| `--border-soft` | `#E5E7EB` | Borders |
| `--honey-amber` | `#F59E0B` | Primary accent |
| `--honey-amber-dark` | `#D97706` | Hover state |

### Typography
- **Headings:** Playfair Display (serif) — weights 700/800
- **Body:** Inter (sans-serif) — weights 400/500/600/700
- **Metadata:** JetBrains Mono (monospace)

## Runtime Configuration

```bash
# Frontend (Crevt-Tree-Ai_Studio-main/)
npm run dev     # Vite dev server
npm run build   # Production build

# Python Knowledge Graph (database/)
python career_generator_v3.py          # Generate 200K paths
python _validate.py                    # Validate output
python _run_v3.py                      # Configurable runner
```

## File Map

```
Base-India-Career-Project/
├── CAREER_DIRECTION.md                    ← This file
├── Resources/
│   └── crevr_tree_design.md              ← Design system & UI spec
├── database/
│   ├── career_generator_v3.py            ← Production knowledge graph engine
│   ├── claude_code_py_prompt_Phase2.md   ← Phase 2 recommendation engine prompt
│   ├── AI_MEMORY_INVENTORY.md            ← Complete project inventory
│   └── career_graph_output_v3/           ← Generated graph (200K paths)
├── components/                           ← Hexatom palette tool (shadcn/ui)
└── Crevt-Tree-Ai_Studio-main/
    ├── src/
    │   ├── App.tsx                       ← Main app with SPA routing
    │   ├── data.ts                       ← 12 curated roadmap datasets
    │   ├── types.ts                      ← TypeScript interfaces
    │   ├── index.css                     ← Theme tokens & Tailwind
    │   └── components/
    │       ├── TreeCanvas.tsx            ← SVG tree / mobile checklist
    │       ├── TreeNode.tsx              ← Interactive node card
    │       ├── InspectorPanel.tsx        ← Tabbed detail panel
    │       ├── Navbar.tsx                ← Navigation
    │       └── Footer.tsx               ← Footer
    └── package.json
```
