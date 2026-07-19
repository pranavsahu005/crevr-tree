# 🌳 CrevrTree

**CrevrTree** is a beautifully structured, offline-first career, exam, and business directory designed specifically to combat information overload for Indian students. Built with a bold, distinctive **Cultural Neobrutalist** theme, it organizes complex pathways (such as UPSC Civil Services, JEE/NEET entries, Tech careers, and Government Exams) into simple, structured milestones, complete with official portals, free resources, and checklist trackers.

---

## 🚀 Key Features

*   🎯 **Curated Roadmap Directory:** Seamlessly switch between diverse Indian tracks like Software Engineering, UPSC Civil Services, High-Growth Startups, Defense Entries, and Medical Careers.
*   🗺️ **Interactive SVG Tree Canvas:** Visualizes dependencies and milestone relationships using elegant, dynamic Bezier paths that color-code based on your progress.
*   📂 **Official Portals & Free Materials:** Connects students directly with official sites (e.g., UPSC, NTA) and verified free textbooks/video series to bypass paywalled, commercialized training.
*   💾 **Persistent Progress Engine:** Students can check off completed milestones with progress saved automatically via local storage.
*   📱 **Adaptive Mobile Support:** Automatically switches from a 2D desktop node network to a dense, vertical single-column mobile checklist layout.

---

## 🎨 Cultural Neobrutalist Styling

CrevrTree breaks away from default, generic web gradients to embrace a bespoke, tactile aesthetic:
*   **The Grid:** White canvas styled with a fine vintage `#EAE6E1` dot grid texture.
*   **Ink-Outlines:** Solid `border-2 border-[#2D2D2D]` borders on all elements.
*   **Tactile Flat Shadows:** Bold `#2D2D2D` drop-shadows that displace slightly on hover.
*   **High-Contrast Indicators:** Completed nodes glow in warm, satisfying greens, while active priorities are highlighted in custom sky blue.

---

## 🛠️ Built With

*   **React 18 & TypeScript:** Scalable, type-safe interactive components.
*   **Vite:** Instant compilation and ultra-fast dev servers.
*   **Tailwind CSS:** Modern, responsive utility styling.
*   **Lucide Icons:** Highly clean, consistent open-source iconography.

---

## 📂 Project Navigation

*   [`/src/data.ts`](src/data.ts): Contains the complete curriculum, roadmap categories, links, and study materials.
*   [`/src/components/TreeCanvas.tsx`](src/components/TreeCanvas.tsx): Powers the custom SVG connection algorithms.
*   [`/src/components/TreeNode.tsx`](src/components/TreeNode.tsx): Individual interactive milestone nodes.
*   [`/src/components/InspectorPanel.tsx`](src/components/InspectorPanel.tsx): Dynamic tabbed explorer showing eligibility and study details.
*   [`/AGENTS.md`](AGENTS.md): Preserves design and style guidelines for AI development sessions.
*   [`/DOCUMENTATION.md`](DOCUMENTATION.md): Complete architecture manual for developers.
