import express from 'express';
import cors from 'cors';
import { dbQuery, initializeDatabase } from './db.js';
import { parseCareerPaths, getFullTreeAsSteps, getCareerSubtree, getTreeStats, getRootBranches, searchPathsByKeyword, clearCache } from './careerPathsParser.js';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Initialize database tables on server start
initializeDatabase().catch(err => {
  console.error('[CrevrTree Server] Database initialization failed:', err);
});

// Helper to parse JSON fields from database rows
function parseStepRow(row) {
  return {
    id: row.id,
    roadmap_id: row.roadmap_id,
    name: row.name,
    desc: row.desc_content || row.desc,
    official: typeof row.official === 'string' ? JSON.parse(row.official) : row.official,
    resources: typeof row.resources === 'string' ? JSON.parse(row.resources) : row.resources,
    checklist: typeof row.checklist === 'string' ? JSON.parse(row.checklist) : row.checklist,
    parent: row.parent || null,
    coords: typeof row.coords === 'string' ? JSON.parse(row.coords) : row.coords,
    salary: row.salary || undefined,
    companies: typeof row.companies === 'string' ? JSON.parse(row.companies) : row.companies,
    colleges: typeof row.colleges === 'string' ? JSON.parse(row.colleges) : row.colleges,
    entranceExams: typeof row.entranceExams === 'string' ? JSON.parse(row.entranceExams) : (row.entranceexams ? (typeof row.entranceexams === 'string' ? JSON.parse(row.entranceexams) : row.entranceexams) : [])
  };
}

function parseNodeRow(row) {
  return {
    node_id: row.node_id,
    node_type: row.node_type,
    title: row.title,
    description: row.description,
    category: row.category,
    difficulty: row.difficulty,
    education_level: row.education_level,
    career_level: row.career_level,
    estimated_duration_months: row.estimated_duration_months,
    salary_band_inr: row.salary_band_inr,
    growth_score: row.growth_score,
    demand_score: row.demand_score,
    automation_risk: row.automation_risk,
    ai_impact: row.ai_impact,
    remote_work_potential: row.remote_work_potential,
    global_opportunity: row.global_opportunity,
    government_opportunity: row.government_opportunity,
    private_opportunity: row.private_opportunity,
    freelance_opportunity: row.freelance_opportunity,
    entrepreneurship_opportunity: row.entrepreneurship_opportunity,
    prerequisites: typeof row.prerequisites === 'string' ? JSON.parse(row.prerequisites) : row.prerequisites,
    skills_required: typeof row.skills_required === 'string' ? JSON.parse(row.skills_required) : row.skills_required,
    skills_gained: typeof row.skills_gained === 'string' ? JSON.parse(row.skills_gained) : row.skills_gained,
    recommended_certifications: typeof row.recommended_certifications === 'string' ? JSON.parse(row.recommended_certifications) : row.recommended_certifications,
    metadata: typeof row.metadata === 'string' ? JSON.parse(row.metadata) : row.metadata
  };
}

// Category extraction helper
function getCategory(node) {
  const c = (node.category || '').toLowerCase();
  const t = (node.title || '').toLowerCase();
  const combined = `${c} ${t}`;
  if (combined.includes('med') || combined.includes('nurse') || combined.includes('doctor') || combined.includes('bams') || combined.includes('bds') || combined.includes('mbbs') || combined.includes('pharm')) return 'medical';
  if (combined.includes('govt') || combined.includes('police') || combined.includes('upsc') || combined.includes('civil') || combined.includes('ssc') || combined.includes('ias') || combined.includes('ips') || combined.includes('ifs') || combined.includes('psu') || combined.includes('rail')) return 'government';
  if (combined.includes('bus') || combined.includes('start') || combined.includes('entre') || combined.includes('farm') || combined.includes('shop') || combined.includes('store') || combined.includes('retail')) return 'business';
  if (combined.includes('fin') || combined.includes('audit') || combined.includes('bank') || combined.includes('tax') || combined.includes('ca ') || combined.includes('account')) return 'finance';
  if (combined.includes('tech') || combined.includes('soft') || combined.includes('ai') || combined.includes('code') || combined.includes('computer') || combined.includes('programming') || combined.includes('devops')) return 'tech';
  return 'education';
}

// Helper to enrich a node with comprehensive links and metadata
function enrichNodeDetails(node, nodes, edges) {
  const title = node.title || '';
  const category = getCategory(node);
  
  const parseList = (val) => {
    if (!val) return [];
    if (typeof val === 'string') {
      try { return JSON.parse(val); } catch (e) { return [val]; }
    }
    return val;
  };

  const prerequisites = parseList(node.prerequisites);
  const skills_required = parseList(node.skills_required);
  const skills_gained = parseList(node.skills_gained);
  const recommended_certifications = parseList(node.recommended_certifications);
  
  const metadata = typeof node.metadata === 'string' ? JSON.parse(node.metadata || '{}') : (node.metadata || {});
  const companies = parseList(metadata.companies || node.companies);
  const colleges = parseList(metadata.colleges || node.colleges);
  const entranceExams = parseList(metadata.entranceExams || node.entranceExams || node.entranceexams);

  const outgoing = edges.filter(e => e.source_id === node.node_id);
  
  const futOpps = [];
  const relCareers = [];
  
  outgoing.forEach(e => {
    const dest = nodes.find(n => n.node_id === e.destination_id);
    if (dest) {
      futOpps.push({ id: dest.node_id, title: dest.title, type: dest.node_type });
    }
  });

  const peers = nodes.filter(n => n.node_type === node.node_type && getCategory(n) === category && n.node_id !== node.node_id);
  peers.slice(0, 3).forEach(p => {
    relCareers.push({ id: p.node_id, title: p.title });
  });

  const resources = [];
  const officialLinks = { label: '', url: '' };
  const govLinks = { label: '', url: '' };
  const docsLinks = { label: '', url: '' };

  const isGov = category === 'government' || title.toLowerCase().includes('upsc') || title.toLowerCase().includes('ssc') || title.toLowerCase().includes('ias') || title.toLowerCase().includes('ips') || title.toLowerCase().includes('officer') || title.toLowerCase().includes('exam') || title.toLowerCase().includes('railway') || title.toLowerCase().includes('defence') || title.toLowerCase().includes('police');
  const isTech = category === 'tech' || title.toLowerCase().includes('tech') || title.toLowerCase().includes('engineer') || title.toLowerCase().includes('developer') || title.toLowerCase().includes('code') || title.toLowerCase().includes('data') || title.toLowerCase().includes('design');
  const isMed = category === 'medical' || title.toLowerCase().includes('doctor') || title.toLowerCase().includes('nurse') || title.toLowerCase().includes('mbbs') || title.toLowerCase().includes('neet') || title.toLowerCase().includes('pharma');
  const isFin = category === 'finance' || title.toLowerCase().includes('account') || title.toLowerCase().includes('ca') || title.toLowerCase().includes('bank') || title.toLowerCase().includes('finance');

  if (isGov) {
    officialLinks.label = 'UPSC / SSC Central Portal';
    officialLinks.url = 'https://upsc.gov.in';
    govLinks.label = 'National Career Service Portal';
    govLinks.url = 'https://ncs.gov.in';
    docsLinks.label = 'Official Recruitment Notification';
    docsLinks.url = 'https://india.gov.in';
  } else if (isTech) {
    officialLinks.label = 'GitHub - Project Hub';
    officialLinks.url = 'https://github.com';
    govLinks.label = 'Ministry of Electronics & IT';
    govLinks.url = 'https://meity.gov.in';
    docsLinks.label = 'Developer Reference & Docs';
    docsLinks.url = 'https://developer.mozilla.org';
  } else if (isMed) {
    officialLinks.label = 'National Testing Agency (NTA)';
    officialLinks.url = 'https://neet.nta.nic.in';
    govLinks.label = 'Ministry of Health & Family Welfare';
    govLinks.url = 'https://mohfw.gov.in';
    docsLinks.label = 'Medical Council of India Reference';
    docsLinks.url = 'https://nmc.org.in';
  } else if (isFin) {
    officialLinks.label = 'Institute of Chartered Accountants (ICAI)';
    officialLinks.url = 'https://icai.org';
    govLinks.label = 'Ministry of Finance';
    govLinks.url = 'https://finmin.nic.in';
    docsLinks.label = 'Income Tax Department Portals';
    docsLinks.url = 'https://incometaxindia.gov.in';
  } else {
    officialLinks.label = 'Ministry of Education Portal';
    officialLinks.url = 'https://education.gov.in';
    govLinks.label = 'Swayam Central Portal';
    govLinks.url = 'https://swayam.gov.in';
    docsLinks.label = 'NCERT Direct Textbook Hub';
    docsLinks.url = 'https://ncert.nic.in';
  }

  if (title.toLowerCase().includes('neet')) {
    officialLinks.label = 'NTA NEET UG Registration';
    officialLinks.url = 'https://neet.nta.nic.in';
  } else if (title.toLowerCase().includes('jee')) {
    officialLinks.label = 'NTA JEE Main Registration';
    officialLinks.url = 'https://jeemain.nta.ac.in';
  } else if (title.toLowerCase().includes('upsc')) {
    officialLinks.label = 'UPSC Online Applications';
    officialLinks.url = 'https://upsconline.nic.in';
  } else if (title.toLowerCase().includes('gate')) {
    officialLinks.label = 'GATE Official Online Portal';
    officialLinks.url = 'https://gate.iitk.ac.in';
  }

  if (isTech) {
    resources.push({ type: 'pdf', label: 'Interactive Programming & DSA Notes PDF', url: 'https://raw.githubusercontent.com/jwasham/coding-interview-university/main/README.md' });
    resources.push({ type: 'video', label: 'Complete Web Development Course on YouTube', url: 'https://www.youtube.com/playlist?list=PLu0W_9lII9agq5Tr1K3JdBvYBiCode464' });
    resources.push({ type: 'course', label: 'IIT Madras Swayam Computer Science Lectures', url: 'https://swayam.gov.in' });
    resources.push({ type: 'doc', label: 'Full Interactive Practice Links (LeetCode & Hackerrank)', url: 'https://leetcode.com' });
    resources.push({ type: 'pdf', label: 'Reference Book: Clean Code Handbook', url: 'https://archive.org' });
    resources.push({ type: 'doc', label: 'Downloadable Sample Starter Code Templates', url: 'https://github.com' });
  } else if (isGov) {
    resources.push({ type: 'pdf', label: 'NCERT Indian Constitution & Polity PDF', url: 'https://ncert.nic.in/textbook.php' });
    resources.push({ type: 'video', label: 'Polity Lectures Series by M. Laxmikanth on YouTube', url: 'https://www.youtube.com' });
    resources.push({ type: 'course', label: 'Free UPSC Daily Current Affairs Series', url: 'https://www.studyiq.com' });
    resources.push({ type: 'doc', label: 'Free Mock Test Papers & Question Banks', url: 'https://mrunal.org' });
    resources.push({ type: 'pdf', label: 'Economic Survey of India Summary Notes', url: 'https://www.budgetindia.gov.in' });
    resources.push({ type: 'doc', label: 'Syllabus & Exam Pattern Details Download', url: 'https://upsc.gov.in' });
  } else if (isMed) {
    resources.push({ type: 'pdf', label: 'NCERT Chemistry & Biology Textbook PDFs', url: 'https://ncert.nic.in/textbook.php' });
    resources.push({ type: 'video', label: 'NEET Physics One-Shot Revision Playlists', url: 'https://www.youtube.com' });
    resources.push({ type: 'course', label: 'Free Biology Crash Course Modules', url: 'https://www.khanacademy.org' });
    resources.push({ type: 'doc', label: 'Mock Test Series & Past year NEET solved keys', url: 'https://www.allen.ac.in' });
    resources.push({ type: 'pdf', label: 'Medical Anatomy Notes by Dr. Najeeb', url: 'https://www.drnajeeblectures.com' });
    resources.push({ type: 'doc', label: 'ICMR Health Guidelines & Syllabus', url: 'https://icmr.gov.in' });
  } else if (isFin) {
    resources.push({ type: 'pdf', label: 'ICAI Study Material & Practice Manual PDFs', url: 'https://www.icai.org/post.html?post_id=17822' });
    resources.push({ type: 'video', label: 'CA Foundation Direct Tax Lectures on YouTube', url: 'https://www.youtube.com' });
    resources.push({ type: 'course', label: 'Free GST & Income Tax Return E-learning modules', url: 'https://www.incometax.gov.in' });
    resources.push({ type: 'doc', label: 'CA Past Exam Solved Sample Papers', url: 'https://www.icai.org' });
    resources.push({ type: 'pdf', label: 'Financial Accounting Textbook Study Notes', url: 'https://archive.org' });
    resources.push({ type: 'doc', label: 'Tax Return Offline Utilities Download', url: 'https://www.gst.gov.in' });
  } else {
    resources.push({ type: 'pdf', label: 'Core NCERT Standard Study Textbook PDF', url: 'https://ncert.nic.in' });
    resources.push({ type: 'video', label: 'Class Lectures & Foundations on YouTube', url: 'https://www.youtube.com' });
    resources.push({ type: 'course', label: 'Swayam National Educational Web Lectures', url: 'https://swayam.gov.in' });
    resources.push({ type: 'doc', label: 'Model Sample Practice Question Sheets', url: 'https://india.gov.in' });
    resources.push({ type: 'pdf', label: 'General Knowledge & Subject Notes PDF', url: 'https://archive.org' });
    resources.push({ type: 'doc', label: 'Admissions Guidelines & Checklists Download', url: 'https://education.gov.in' });
  }

  const checklist = skills_required.length > 0
    ? skills_required.map(s => `Master core skills: ${s}`)
    : ['Understand basic core concepts', 'Verify eligibility parameters', 'Prepare study planner timetable'];

  if (prerequisites.length > 0) {
    prerequisites.forEach(p => {
      checklist.unshift(`Pre-requisite criteria: Clear and understand ${p}`);
    });
  }

  const subTopics = [];
  if (skills_gained && skills_gained.length > 0) {
    skills_gained.forEach(s => subTopics.push({ label: s }));
  }
  if (skills_required && skills_required.length > 0) {
    skills_required.forEach(s => {
      if (!subTopics.some(t => t.label === s)) {
        subTopics.push({ label: s });
      }
    });
  }
  if (recommended_certifications && recommended_certifications.length > 0) {
    recommended_certifications.forEach(c => {
      if (!subTopics.some(t => t.label === c)) {
        subTopics.push({ label: `Cert: ${c}` });
      }
    });
  }
  if (subTopics.length === 0) {
    subTopics.push({ label: 'Core Principles' });
    subTopics.push({ label: 'Key Standards' });
    subTopics.push({ label: 'Practical Labs' });
  }

  let subTopicsTitle = 'Core Terminology';
  if (category === 'tech') subTopicsTitle = 'Concepts & Tools';
  else if (category === 'government') subTopicsTitle = 'Syllabus Focus';
  else if (category === 'medical') subTopicsTitle = 'Clinical Areas';
  else if (category === 'business') subTopicsTitle = 'Operational Milestones';
  else if (category === 'finance') subTopicsTitle = 'Audit & Regulation';

  return {
    id: node.node_id,
    name: title,
    desc: node.description || `${title} is a key milestone in this career path.`,
    short_desc: node.description ? (node.description.split('.')[0] + '.') : `${title} milestone.`,
    category: category,
    difficulty: node.difficulty || 1,
    duration: node.estimated_duration_months || 0,
    salary: node.salary_band_inr || undefined,
    prerequisites,
    skills_required,
    skills_gained,
    recommended_certifications,
    companies,
    colleges,
    entranceExams,
    future_opportunities: futOpps,
    related_careers: relCareers,
    official: officialLinks,
    gov_website: govLinks,
    documentation: docsLinks,
    resources,
    checklist,
    sub_topics: subTopics.slice(0, 8),
    sub_topics_title: subTopicsTitle
  };
}


// 1. GET /api/roadmaps - Get all curated roadmaps
app.get('/api/roadmaps', async (req, res) => {
  try {
    const rows = await dbQuery('SELECT * FROM roadmaps');
    res.json(rows);
  } catch (err) {
    console.error('[API Error] Fetch roadmaps failed:', err);
    res.status(500).json({ error: 'Failed to fetch roadmaps' });
  }
});

// 2. GET /api/roadmaps/:id - Get a specific roadmap and its steps
app.get('/api/roadmaps/:id', async (req, res) => {
  try {
    const roadmapId = req.params.id;
    const roadmapRows = await dbQuery('SELECT * FROM roadmaps WHERE id = ?', [roadmapId]);
    if (roadmapRows.length === 0) {
      return res.status(404).json({ error: 'Roadmap not found' });
    }
    
    const stepsRows = await dbQuery('SELECT * FROM roadmap_steps WHERE roadmap_id = ?', [roadmapId]);
    const parsedSteps = stepsRows.map(parseStepRow);
    
    // Fetch all nodes and edges to perform merge-enrichment
    const allNodesRows = await dbQuery('SELECT * FROM nodes');
    const allEdgesRows = await dbQuery('SELECT * FROM edges');
    const nodes = allNodesRows.map(parseNodeRow);
    const edges = allEdgesRows.map(e => ({
      source_id: e.source_id,
      destination_id: e.destination_id,
      relationship_type: e.relationship_type,
      required_skills: typeof e.required_skills === 'string' ? JSON.parse(e.required_skills) : e.required_skills,
      optional_skills: typeof e.optional_skills === 'string' ? JSON.parse(e.optional_skills) : e.optional_skills,
      estimated_time_months: e.estimated_time_months,
      transition_difficulty: e.transition_difficulty,
      recommended_certifications: typeof e.recommended_certifications === 'string' ? JSON.parse(e.recommended_certifications) : e.recommended_certifications,
      probability: e.probability,
      confidence: e.confidence,
      metadata: typeof e.metadata === 'string' ? JSON.parse(e.metadata) : e.metadata
    }));

    const enrichedSteps = parsedSteps.map(step => {
      const matchingNode = nodes.find(n => 
        n.node_id === step.id || 
        n.title.toLowerCase() === step.name.toLowerCase()
      );
      
      if (matchingNode) {
        const enriched = enrichNodeDetails(matchingNode, nodes, edges);
        return {
          ...step,
          ...enriched,
          id: step.id,
          name: step.name,
          parent: step.parent,
          coords: step.coords
        };
      }
      return step;
    });
    
    // Sort steps to make sure parent steps are processed first
    const sortedSteps = [];
    const visited = new Set();
    
    const addStep = (step) => {
      if (visited.has(step.id)) return;
      if (step.parent && !visited.has(step.parent)) {
        const parent = enrichedSteps.find(s => s.id === step.parent);
        if (parent) addStep(parent);
      }
      visited.add(step.id);
      sortedSteps.push(step);
    };
    
    enrichedSteps.forEach(addStep);

    res.json({
      ...roadmapRows[0],
      steps: sortedSteps
    });
  } catch (err) {
    console.error('[API Error] Fetch roadmap details failed:', err);
    res.status(500).json({ error: 'Failed to fetch roadmap details' });
  }
});

// 3. GET /api/nodes - Search knowledge graph nodes
app.get('/api/nodes', async (req, res) => {
  try {
    const search = req.query.search || '';
    if (!search) {
      return res.json([]);
    }
    
    const queryStr = `%${search}%`;
    const rows = await dbQuery(
      'SELECT * FROM nodes WHERE title LIKE ? OR description LIKE ? LIMIT 50',
      [queryStr, queryStr]
    );
    res.json(rows.map(parseNodeRow));
  } catch (err) {
    console.error('[API Error] Search nodes failed:', err);
    res.status(500).json({ error: 'Failed to search nodes' });
  }
});

// 4. GET /api/nodes/:id/tree - Dynamically generate a tree starting from a specific node
app.get('/api/nodes/:id/tree', async (req, res) => {
  try {
    const targetNodeId = req.params.id;
    
    // Fetch all nodes and edges to build graph in memory
    const allNodesRows = await dbQuery('SELECT * FROM nodes');
    const allEdgesRows = await dbQuery('SELECT * FROM edges');
    
    const nodes = allNodesRows.map(parseNodeRow);
    const edges = allEdgesRows.map(e => ({
      source_id: e.source_id,
      destination_id: e.destination_id,
      relationship_type: e.relationship_type,
      required_skills: typeof e.required_skills === 'string' ? JSON.parse(e.required_skills) : e.required_skills,
      optional_skills: typeof e.optional_skills === 'string' ? JSON.parse(e.optional_skills) : e.optional_skills,
      estimated_time_months: e.estimated_time_months,
      transition_difficulty: e.transition_difficulty,
      recommended_certifications: typeof e.recommended_certifications === 'string' ? JSON.parse(e.recommended_certifications) : e.recommended_certifications,
      probability: e.probability,
      confidence: e.confidence,
      metadata: typeof e.metadata === 'string' ? JSON.parse(e.metadata) : e.metadata
    }));
    
    const targetNode = nodes.find(n => n.node_id === targetNodeId);
    if (!targetNode) {
      return res.status(404).json({ error: 'Node not found in knowledge graph' });
    }
    
    // Traversal strategy:
    // 1. Trace backwards to find a root starting node (e.g. 10th or 12th PCM, or the closest node with no incoming edges)
    // 2. Perform a BFS from that starting node downstream to gather paths, stopping after target node is covered and limit step count to ~8 for readability.
    
    // Build graph links
    const incoming = {};
    const outgoing = {};
    edges.forEach(e => {
      if (!outgoing[e.source_id]) outgoing[e.source_id] = [];
      outgoing[e.source_id].push(e.destination_id);
      
      if (!incoming[e.destination_id]) incoming[e.destination_id] = [];
      incoming[e.destination_id].push(e.source_id);
    });
    
    // Find ancestors (find paths going backward from target)
    const ancestors = new Set();
    const findAncestors = (id, depth = 0) => {
      if (depth > 6 || ancestors.has(id)) return;
      ancestors.add(id);
      const parents = incoming[id] || [];
      parents.forEach(p => findAncestors(p, depth + 1));
    };
    findAncestors(targetNodeId);
    
    // Select the best starting root node among ancestors:
    // Prefer school/basic education node (e.g., nodes starting with "10th", "12th") or any node with no incoming edges.
    let rootId = targetNodeId;
    let rootNode = targetNode;
    
    for (const aId of ancestors) {
      const node = nodes.find(n => n.node_id === aId);
      if (node) {
        const isRootEducation = node.education_level === 'school' || node.title.toLowerCase().startsWith('10th') || node.title.toLowerCase().startsWith('12th');
        const hasNoIncoming = !incoming[aId] || incoming[aId].length === 0;
        
        if (isRootEducation) {
          rootId = aId;
          rootNode = node;
          break; // Preferred choice found
        } else if (hasNoIncoming) {
          rootId = aId;
          rootNode = node;
        }
      }
    }
    
    // Perform BFS downstream from rootId, but only include nodes that are:
    // A) Ancestors of targetNode (leads to the target) OR
    // B) Direct children/descendants of targetNode (progressions after target)
    const treeNodeIds = new Set();
    const treeEdges = [];
    
    // Collect paths from root to target
    const pathsToTarget = [];
    const queue = [[rootId]];
    while (queue.length > 0) {
      const path = queue.shift();
      const last = path[path.length - 1];
      if (last === targetNodeId) {
        pathsToTarget.push(path);
        if (pathsToTarget.length > 5) break; // limit path variations
        continue;
      }
      const children = outgoing[last] || [];
      children.forEach(child => {
        if (!path.includes(child)) {
          queue.push([...path, child]);
        }
      });
    }
    
    // Add all nodes in paths to target
    pathsToTarget.forEach(path => {
      path.forEach(id => treeNodeIds.add(id));
      for (let i = 0; i < path.length - 1; i++) {
        const e = edges.find(ed => ed.source_id === path[i] && ed.destination_id === path[i+1]);
        if (e && !treeEdges.some(te => te.source_id === e.source_id && te.destination_id === e.destination_id)) {
          treeEdges.push(e);
        }
      }
    });
    
    // Add descendants of targetNode (up to 2 levels down)
    const collectDescendants = (id, currentDepth) => {
      if (currentDepth >= 2) return;
      const children = outgoing[id] || [];
      children.forEach(childId => {
        treeNodeIds.add(childId);
        const e = edges.find(ed => ed.source_id === id && ed.destination_id === childId);
        if (e && !treeEdges.some(te => te.source_id === e.source_id && te.destination_id === e.destination_id)) {
          treeEdges.push(e);
        }
        collectDescendants(childId, currentDepth + 1);
      });
    };
    collectDescendants(targetNodeId, 0);
    
    // Always include target node and root node
    treeNodeIds.add(rootId);
    treeNodeIds.add(targetNodeId);
    
    // Ensure all edges between selected nodes are added
    edges.forEach(e => {
      if (treeNodeIds.has(e.source_id) && treeNodeIds.has(e.destination_id)) {
        if (!treeEdges.some(te => te.source_id === e.source_id && te.destination_id === e.destination_id)) {
          treeEdges.push(e);
        }
      }
    });
    
    // Build layered layout coordinates
    const layers = {};
    const nodeDepths = {};
    
    // BFS to calculate depths starting from rootId
    const bfsQueue = [{ id: rootId, depth: 0 }];
    const visitedBfs = new Set([rootId]);
    
    while (bfsQueue.length > 0) {
      const { id, depth } = bfsQueue.shift();
      nodeDepths[id] = depth;
      
      const children = treeEdges.filter(e => e.source_id === id).map(e => e.destination_id);
      children.forEach(childId => {
        if (!visitedBfs.has(childId)) {
          visitedBfs.add(childId);
          bfsQueue.push({ id: childId, depth: depth + 1 });
        }
      });
    }
    
    // Fill layers map
    Object.keys(nodeDepths).forEach(id => {
      const depth = nodeDepths[id];
      if (!layers[depth]) layers[depth] = [];
      layers[depth].push(id);
    });
    
    // Map back to steps with coords
    const steps = [];
    const categoryMapping = {
      'medical': 'medical',
      'education': 'education',
      'government': 'government',
      'business': 'business',
      'finance': 'finance',
      'tech': 'tech'
    };
    
    const getCategory = (node) => {
      const c = (node.category || '').toLowerCase();
      if (c.includes('med') || c.includes('nurse') || c.includes('doctor')) return 'medical';
      if (c.includes('govt') || c.includes('police') || c.includes('upsc') || c.includes('civil')) return 'government';
      if (c.includes('bus') || c.includes('start') || c.includes('entre')) return 'business';
      if (c.includes('fin') || c.includes('audit') || c.includes('bank')) return 'finance';
      if (c.includes('tech') || c.includes('soft') || c.includes('ai') || c.includes('code')) return 'tech';
      return 'education';
    };
    
    const treeCategory = getCategory(targetNode);
    
    Object.keys(layers).forEach(depthStr => {
      const depth = parseInt(depthStr);
      const layerNodes = layers[depth];
      const y = 12 + depth * 22; // spread dynamically vertically
      
      layerNodes.forEach((id, idx) => {
        const node = nodes.find(n => n.node_id === id);
        if (!node) return;
        
        const x = layerNodes.length === 1 
          ? 50 
          : 15 + (idx / (layerNodes.length - 1)) * 70; // distribute horizontally
          
        const parentEdge = treeEdges.find(e => e.destination_id === id && nodeDepths[e.source_id] < depth);
        
        const enriched = enrichNodeDetails(node, nodes, edges);
        steps.push({
          ...enriched,
          parent: parentEdge ? parentEdge.source_id : null,
          coords: { x: Math.round(x), y: Math.round(y) }
        });
      });
    });

    res.json({
      id: `dynamic-${targetNode.node_id}`,
      name: `${targetNode.title} Pathway`,
      category: treeCategory,
      tagline: `Dynamically generated direction mapping the path to becoming or mastering: ${targetNode.title}`,
      steps
    });
  } catch (err) {
    console.error('[API Error] Generate dynamic tree failed:', err);
    res.status(500).json({ error: 'Failed to generate dynamic layout tree' });
  }
});

// 5. GET /api/career-paths/stats - Get career paths statistics
app.get('/api/career-paths/stats', async (req, res) => {
  try {
    const result = await parseCareerPaths();
    res.json(result.stats);
  } catch (err) {
    console.error('[API Error] Career paths stats failed:', err);
    res.status(500).json({ error: 'Failed to load career paths stats' });
  }
});

// 6. GET /api/career-paths/branches - Get root-level career branches
app.get('/api/career-paths/branches', async (req, res) => {
  try {
    await parseCareerPaths();
    const branches = getRootBranches();
    res.json(branches);
  } catch (err) {
    console.error('[API Error] Career paths branches failed:', err);
    res.status(500).json({ error: 'Failed to load career path branches' });
  }
});

// 7. GET /api/career-paths/tree - Get full career tree as Steps format for TreeCanvas
app.get('/api/career-paths/tree', async (req, res) => {
  try {
    const parsed = await parseCareerPaths();
    const maxDepth = parseInt(req.query.depth) || 5;
    const maxChildren = parseInt(req.query.children) || 5;
    const steps = getFullTreeAsSteps(maxDepth, maxChildren);
    res.json({
      id: 'all-career-paths',
      name: 'India Career Paths Directory',
      category: 'education',
      tagline: `Complete career pathway tree — ${parsed.stats.totalPaths} paths mapped from 10th grade to final career destinations across India.`,
      steps
    });
  } catch (err) {
    console.error('[API Error] Career paths tree failed:', err);
    res.status(500).json({ error: 'Failed to load career paths tree' });
  }
});

// 8. GET /api/career-paths/search - Search career paths by keyword
app.get('/api/career-paths/search', async (req, res) => {
  try {
    await parseCareerPaths();
    const q = req.query.q || '';
    if (!q) return res.json([]);
    const results = searchPathsByKeyword(q);
    res.json(results);
  } catch (err) {
    console.error('[API Error] Career paths search failed:', err);
    res.status(500).json({ error: 'Failed to search career paths' });
  }
});

// 9. GET /api/career-paths/:keyword/tree - Get subtree for a specific career keyword
app.get('/api/career-paths/:keyword/tree', async (req, res) => {
  try {
    await parseCareerPaths();
    const keyword = decodeURIComponent(req.params.keyword);
    const maxDepth = parseInt(req.query.depth) || 6;
    const steps = getCareerSubtree(keyword, maxDepth);
    
    if (steps.length === 0) {
      return res.status(404).json({ error: `No career paths found for "${keyword}"` });
    }
    
    res.json({
      id: `career-path-${keyword.toLowerCase().replace(/\s+/g, '-')}`,
      name: `${keyword} Career Pathway`,
      category: getCategoryFromKeyword(keyword),
      tagline: `Career direction mapping for ${keyword} — from education foundations to career milestones.`,
      steps
    });
  } catch (err) {
    console.error('[API Error] Career path subtree failed:', err);
    res.status(500).json({ error: 'Failed to load career path subtree' });
  }
});

// Helper to determine category from keyword
function getCategoryFromKeyword(keyword) {
  const kw = keyword.toLowerCase();
  if (kw.includes('doctor') || kw.includes('medical') || kw.includes('nurse') || kw.includes('mbbs') || kw.includes('pharma') || kw.includes('bds') || kw.includes('bams')) return 'medical';
  if (kw.includes('ias') || kw.includes('ips') || kw.includes('upsc') || kw.includes('police') || kw.includes('ssc') || kw.includes('government') || kw.includes('govt') || kw.includes('railway') || kw.includes('defence')) return 'government';
  if (kw.includes('startup') || kw.includes('business') || kw.includes('farm') || kw.includes('shop') || kw.includes('entrepreneur')) return 'business';
  if (kw.includes('ca ') || kw.includes('chartered') || kw.includes('bank') || kw.includes('finance') || kw.includes('account')) return 'finance';
  if (kw.includes('engineer') || kw.includes('software') || kw.includes('ai ') || kw.includes('developer') || kw.includes('code') || kw.includes('computer') || kw.includes('tech')) return 'tech';
  return 'education';
}

// Serve frontend assets in production
const clientDist = './dist';
app.use(express.static(clientDist));

// Fallback all non-api routes to React index.html for SPA routing
app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api')) {
    return next();
  }
  res.sendFile('index.html', { root: clientDist }, (err) => {
    if (err) {
      res.status(200).send("CrevrTree API Server is running. Frontend static files build pending.");
    }
  });
});

app.listen(PORT, () => {
  console.log(`[CrevrTree Server] Running on port ${PORT}`);
});

export default app;
