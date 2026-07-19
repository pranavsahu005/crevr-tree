import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Robust path resolution helper
const getProjectRoot = () => {
  const cwd = process.cwd();
  if (fs.existsSync(path.join(cwd, 'Crevt-Tree-Ai_Studio-main', 'data_store'))) {
    return path.join(cwd, 'Crevt-Tree-Ai_Studio-main');
  }
  if (fs.existsSync(path.join(cwd, 'data_store'))) {
    return cwd;
  }
  return __dirname;
};

const projectRoot = getProjectRoot();
const databaseDir = path.join(projectRoot, '..', 'database');
const claudeDataPath = path.join(databaseDir, 'Claude', 'career_data.json');

console.log(`[CrevrTree Compiler] Reading Claude data from: ${claudeDataPath}`);

if (!fs.existsSync(claudeDataPath)) {
  console.error(`Error: Claude dataset not found at ${claudeDataPath}`);
  process.exit(1);
}

const rawData = JSON.parse(fs.readFileSync(claudeDataPath, 'utf8'));
const paths = rawData.career_paths;

const categoryMap = {
  'Technology': 'tech',
  'Healthcare': 'medical',
  'Government': 'government',
  'Business': 'business',
  'Finance & Commerce': 'finance',
  'Engineering': 'tech',
  'Law': 'government',
  'Creative': 'tech',
  'Agriculture': 'business'
};

const roadmaps = [];
const allSteps = [];
const nodes = [];
const edges = [];
const txtPaths = [];

for (const p of paths) {
  const category = categoryMap[p.category] || 'education';
  
  // 1. Generate Roadmap main record
  const roadmap = {
    id: p.id,
    name: p.title,
    category: category,
    tagline: p.description,
    steps: []
  };

  // 2. Generate steps seq names for career_paths.txt
  const stepsSeqNames = p.steps.map(s => s.stage);
  txtPaths.push(`Path #${txtPaths.length + 1}: ${stepsSeqNames.join(' \u2192 ')}`);

  // 3. Process Steps
  for (let idx = 0; idx < p.steps.length; idx++) {
    const s = p.steps[idx];
    const stepId = `${p.id}-${s.level}`;
    let parentId = s.level > 1 ? `${p.id}-${s.level - 1}` : null;
    
    // Automatically generate branching/fanning coords & parent connections
    let x = 50;
    let y = 10;

    if (idx === 0) {
      x = 50;
      y = 10;
      parentId = null;
    } else if (idx === 1) {
      x = 50;
      y = 25;
      parentId = `${p.id}-1`;
    } else if (idx === 2) {
      x = 30; // Left branch
      y = 45;
      parentId = `${p.id}-2`;
    } else if (idx === 3) {
      x = 70; // Right branch
      y = 45;
      parentId = `${p.id}-2`;
    } else if (idx === 4) {
      x = 50; // Merge center
      y = 68;
      parentId = `${p.id}-3`;
      edges.push({
        source_id: `${p.id}-4`,
        destination_id: stepId,
        relationship_type: 'prerequisite'
      });
    } else if (idx === 5) {
      x = 30; // Left branch 2
      y = 90;
      parentId = `${p.id}-5`;
    } else if (idx === 6) {
      x = 70; // Right branch 2
      y = 90;
      parentId = `${p.id}-5`;
    } else if (idx === 7) {
      x = 50; // Merge center 2
      y = 112;
      parentId = `${p.id}-6`;
      edges.push({
        source_id: `${p.id}-7`,
        destination_id: stepId,
        relationship_type: 'prerequisite'
      });
    } else {
      // Linear peak extension (Level 9+)
      x = 50;
      y = 112 + (idx - 7) * 22;
      parentId = `${p.id}-${idx}`;
    }

    // Determine salary string
    let salary = null;
    if (s.level >= 5) {
      if (s.level === 5 || s.level === 6) salary = p.salary_range.entry || null;
      else if (s.level === 7) salary = p.salary_range.mid || null;
      else if (s.level === 8) salary = p.salary_range.senior || null;
      else salary = p.salary_range.executive || null;
    }

    // Determine companies list
    let companies = [];
    if (p.companies) {
      companies = [
        ...(p.companies.product || []),
        ...(p.companies.service || []),
        ...(p.companies.startups || [])
      ].slice(0, 5);
    }

    // Determine resources
    const resources = (p.free_resources || []).map((r, rIdx) => ({
      type: (r.type || 'course').toLowerCase(),
      label: r.name,
      url: r.url
    })).slice(0, 3);

    // Determine checklist
    const skillsRequired = p.skills_required || [];
    const skillsToBuild = p.skills_to_build || [];
    const checklist = [
      `Understand ${skillsRequired[idx % skillsRequired.length] || 'fundamentals'}`,
      `Practice ${skillsToBuild[idx % skillsToBuild.length] || 'core concepts'}`,
      `Complete stage milestones`
    ];

    // Determine official portal
    const official = {
      label: p.exam_path ? p.exam_path.split('\u2192')[0].trim() : 'Official Guide',
      url: p.free_resources && p.free_resources[0] ? p.free_resources[0].url : 'https://india.gov.in'
    };

    const stepObj = {
      id: stepId,
      name: s.stage,
      desc: s.action,
      official: official,
      resources: resources,
      checklist: checklist,
      parent: parentId,
      coords: {
        x: x,
        y: y
      },
      salary: salary,
      companies: companies,
      colleges: p.colleges || [],
      entranceExams: p.exam_path ? [p.exam_path.split('\u2192')[0].trim()] : []
    };

    roadmap.steps.push(stepObj);
    allSteps.push({ ...stepObj, roadmap_id: p.id });

    // Generate Knowledge Graph node
    const difficultyNum = p.difficulty === 'Very High' ? 5 : p.difficulty === 'High' ? 4 : 3;
    nodes.push({
      node_id: stepId,
      node_type: 'milestone',
      title: s.stage,
      description: s.action,
      category: category,
      difficulty: difficultyNum,
      estimated_duration_months: 6,
      salary_band_inr: salary || '',
      growth_score: 8.5,
      demand_score: 9.0,
      automation_risk: 0.3,
      ai_impact: 0.4,
      remote_work_potential: p.remote_potential === 'Very High' ? 0.9 : p.remote_potential === 'High' ? 0.7 : 0.4,
      global_opportunity: 0.8,
      government_opportunity: category === 'government' ? 1.0 : 0.2,
      private_opportunity: category !== 'government' ? 1.0 : 0.1,
      freelance_opportunity: p.remote_potential === 'Very High' ? 0.8 : 0.3,
      entrepreneurship_opportunity: 0.7,
      prerequisites: parentId ? [parentId] : [],
      skills_required: p.skills_required || [],
      skills_gained: p.skills_to_build || [],
      recommended_certifications: (p.certifications || []).map(c => c.name),
      metadata: {}
    });

    // Generate Edge connection
    if (parentId) {
      edges.push({
        source_id: parentId,
        destination_id: stepId,
        relationship_type: 'prerequisite'
      });
    }
  }

  roadmaps.push(roadmap);
}

// 4. Export files to data_store
const dataStoreDir = path.join(projectRoot, 'data_store');
if (!fs.existsSync(dataStoreDir)) {
  fs.mkdirSync(dataStoreDir, { recursive: true });
}

fs.writeFileSync(path.join(dataStoreDir, 'roadmaps.json'), JSON.stringify(roadmaps.map(r => ({
  id: r.id,
  name: r.name,
  category: r.category,
  tagline: r.tagline
})), null, 2), 'utf8');

fs.writeFileSync(path.join(dataStoreDir, 'roadmap_steps.json'), JSON.stringify(allSteps, null, 2), 'utf8');
fs.writeFileSync(path.join(dataStoreDir, 'nodes.json'), JSON.stringify(nodes, null, 2), 'utf8');
fs.writeFileSync(path.join(dataStoreDir, 'edges.json'), JSON.stringify(edges, null, 2), 'utf8');

console.log('✓ Successfully wrote data_store JSON files!');

// 5. Export to career_graph_output_v3
const v3Dir = path.join(databaseDir, 'career_graph_output_v3');
if (!fs.existsSync(v3Dir)) {
  fs.mkdirSync(v3Dir, { recursive: true });
}

fs.writeFileSync(path.join(v3Dir, 'career_paths.txt'), txtPaths.join('\n'), 'utf8');
fs.writeFileSync(path.join(v3Dir, 'nodes.json'), JSON.stringify(nodes, null, 2), 'utf8');
fs.writeFileSync(path.join(v3Dir, 'edges.json'), JSON.stringify(edges, null, 2), 'utf8');

console.log('✓ Successfully wrote career_graph_output_v3 files!');

// 6. Generate src/data.ts
const dataTsPath = path.join(projectRoot, 'src', 'data.ts');
const dataTsContent = `// Auto-generated curated roadmaps from Claude career_data.json
export interface Step {
  id: string;
  name: string;
  desc: string;
  official?: { label: string; url: string };
  resources?: { type: string; label: string; url: string }[];
  checklist?: string[];
  parent?: string | null;
  coords: { x: number; y: number };
  salary?: string | null;
  companies?: string[];
  colleges?: string[];
  entranceExams?: string[];
}

export interface Roadmap {
  id: string;
  name: string;
  category: 'tech' | 'medical' | 'government' | 'business' | 'finance' | 'education';
  tagline: string;
  steps: Step[];
}

export const ROADMAPS_DATABASE: Roadmap[] = ${JSON.stringify(roadmaps, null, 2)};
`;

fs.writeFileSync(dataTsPath, dataTsContent, 'utf8');
console.log('✓ Successfully wrote src/data.ts!');

console.log('[CrevrTree Compiler] Compilation Complete!');
