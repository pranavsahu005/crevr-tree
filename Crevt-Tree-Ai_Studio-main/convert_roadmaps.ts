import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ROADMAPS_DATABASE } from './src/data.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function convert() {
  console.log('[Roadmap Converter] Starting roadmap conversion...');
  
  // Ensure public/data directory exists
  const publicDataDir = path.join(__dirname, 'public', 'data');
  if (!fs.existsSync(publicDataDir)) {
    fs.mkdirSync(publicDataDir, { recursive: true });
  }

  // Iterate over all roadmaps in data.ts
  for (const roadmap of ROADMAPS_DATABASE) {
    console.log(`- Converting roadmap: ${roadmap.name} (${roadmap.id})`);

    const convertedNodes = roadmap.steps.map((step, idx) => {
      // Find children: other steps in this roadmap that have this step as parent
      const children = roadmap.steps
        .filter(s => s.parent === step.id)
        .map(s => s.id);

      // Map sub-topics: use checklist items or colleges/companies as chips
      const subTopics = [];
      
      // If checklist items exist, add them as subtopic chips
      if (step.checklist && step.checklist.length > 0) {
        step.checklist.forEach(item => {
          subTopics.push({ label: item });
        });
      }

      // Add entrance exams or colleges if available
      if (step.entranceExams && step.entranceExams.length > 0) {
        step.entranceExams.forEach(exam => {
          subTopics.push({ label: `Exam: ${exam}` });
        });
      }
      
      if (step.colleges && step.colleges.length > 0) {
        step.colleges.forEach(college => {
          subTopics.push({ label: `Hub: ${college}` });
        });
      }

      // Fallback subtopic if empty
      if (subTopics.length === 0) {
        subTopics.push({ label: `Introduction to ${step.name}` });
        subTopics.push({ label: `Core Principles` });
      }

      // Compute tier (depth level) - fallback to idx + 1 if not calculable
      let tier = 1;
      let currParent = step.parent;
      while (currParent) {
        tier++;
        const p = roadmap.steps.find(s => s.id === currParent);
        currParent = p ? p.parent : null;
      }

      return {
        id: step.id,
        label: step.name,
        tier: tier,
        children: children,
        detail: {
          overview: step.desc,
          official: step.official || null,
          free_resources: step.resources ? step.resources.map(r => ({
            type: r.type,
            label: r.label,
            url: r.url
          })) : [],
          checklist: step.checklist || [],
          salary: step.salary || null,
          companies: step.companies || [],
          colleges: step.colleges || []
        },
        sub_topics: subTopics.slice(0, 4) // Limit to max 4 chips for visual layout
      };
    });

    const roadmapData = {
      id: roadmap.id,
      name: roadmap.name,
      category: roadmap.category,
      description: roadmap.tagline,
      nodes: convertedNodes
    };

    // Save to public/data/:id.json
    const outputPath = path.join(publicDataDir, `${roadmap.id}.json`);
    fs.writeFileSync(outputPath, JSON.stringify(roadmapData, null, 2), 'utf8');
    console.log(`  Saved converted JSON to: ${outputPath}`);
  }

  // Also save a index list of all roadmaps for the home/category screen
  const indexData = ROADMAPS_DATABASE.map(r => ({
    id: r.id,
    name: r.name,
    category: r.category,
    tagline: r.tagline,
    stepCount: r.steps.length
  }));
  
  fs.writeFileSync(
    path.join(publicDataDir, 'index.json'), 
    JSON.stringify(indexData, null, 2), 
    'utf8'
  );
  console.log('[Roadmap Converter] Conversion complete!');
}

convert().catch(err => {
  console.error('[Roadmap Converter] Conversion failed:', err);
});
