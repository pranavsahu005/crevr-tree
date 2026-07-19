import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Robust data directory resolution for local dev & Vercel
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

let cachedTree = null;
let cachedKeywordIndex = null;
let cacheStats = { totalPaths: 0, totalUniqueNodes: 0, rootCount: 0 };
let nodeCounter = 0;

export function parseCareerPaths() {
  if (cachedTree) return { tree: cachedTree, index: cachedKeywordIndex, stats: cacheStats };

  const dataDir = path.join(projectRoot, 'data_store');
  const treePath = path.join(dataDir, 'career_tree.json');
  const indexPath = path.join(dataDir, 'career_index.json');
  const statsPath = path.join(dataDir, 'career_stats.json');

  if (fs.existsSync(treePath) && fs.existsSync(indexPath) && fs.existsSync(statsPath)) {
    console.log('[CrevrTree CareerPaths] Loading pre-cached JSON files from data_store...');
    try {
      cachedTree = JSON.parse(fs.readFileSync(treePath, 'utf8'));
      cachedKeywordIndex = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
      cacheStats = JSON.parse(fs.readFileSync(statsPath, 'utf8'));
      return { tree: cachedTree, index: cachedKeywordIndex, stats: cacheStats };
    } catch (err) {
      console.error('[CrevrTree CareerPaths] Failed to load pre-cached JSON, falling back to text file...', err);
    }
  }

  const filePath = path.join(projectRoot, '..', 'database', 'career_graph_output_v3', 'career_paths.txt');
  if (!fs.existsSync(filePath)) {
    console.warn('[CrevrTree CareerPaths] career_paths.txt not found at', filePath);
    return { tree: [], index: {}, stats: cacheStats };
  }

  console.log('[CrevrTree CareerPaths] Parsing career_paths.txt (53MB, ~400K lines)...');
  const t0 = Date.now();

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  console.log(`[CrevrTree CareerPaths] Read ${lines.length} lines in ${Date.now() - t0}ms`);

  const rootNode = { id: 'root', name: 'India Career Paths (After 10th)', children: new Map(), pathCount: 0, depth: 0 };
  const keywordIndex = new Map();
  let totalPaths = 0;
  let totalUniqueNodes = 1;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed === '---') continue;

    const match = trimmed.match(/^Path\s*#?\d+:\s*(.+)$/);
    if (!match) continue;

    const steps = match[1].split(/\s*\u2192\s*/).map(s => s.trim()).filter(Boolean);
    if (steps.length === 0) continue;
    totalPaths++;

    let currentParent = rootNode;
    for (let depth = 0; depth < steps.length; depth++) {
      const stepName = steps[depth];
      if (!currentParent.children.has(stepName)) {
        nodeCounter++;
        const childNode = {
          id: `cp-${nodeCounter}`,
          name: stepName,
          children: new Map(),
          pathCount: 0,
          depth: depth + 1,
          parentId: currentParent.id
        };
        currentParent.children.set(stepName, childNode);
        totalUniqueNodes++;

        const keywords = stepName.toLowerCase().split(/\s+/).filter(w => w.length > 2);
        for (const kw of keywords) {
          if (!keywordIndex.has(kw)) keywordIndex.set(kw, new Set());
          keywordIndex.get(kw).add(childNode.id);
        }
      }
      currentParent = currentParent.children.get(stepName);
      currentParent.pathCount++;
    }
  }

  const convertNode = (node) => ({
    id: node.id,
    name: node.name,
    pathCount: node.pathCount,
    depth: node.depth,
    parentId: node.parentId || null,
    children: Array.from(node.children.values()).map(convertNode).sort((a, b) => b.pathCount - a.pathCount)
  });

  const tree = convertNode(rootNode);
  const index = {};
  for (const [kw, ids] of keywordIndex) {
    index[kw] = Array.from(ids).slice(0, 100);
  }

  cachedTree = tree;
  cachedKeywordIndex = index;
  cacheStats = { totalPaths, totalUniqueNodes, rootCount: rootNode.children.size, parseTimeMs: Date.now() - t0 };
  console.log(`[CrevrTree CareerPaths] Done: ${totalPaths} paths, ${totalUniqueNodes} unique nodes, ${rootNode.children.size} root branches in ${cacheStats.parseTimeMs}ms`);

  return { tree, index, stats: cacheStats };
}

export function getFullTreeAsSteps(maxDepth = 5, maxChildrenPerNode = 5) {
  const { tree } = parseCareerPaths();
  if (!tree) return [];

  const root = tree; // tree IS the root node object
  const steps = [];
  const visited = new Set();

  function traverse(node, parentStepId, depth) {
    if (depth > maxDepth || visited.has(node.id)) return;
    visited.add(node.id);

    const children = node.children || [];
    const visibleChildren = children.slice(0, maxChildrenPerNode);
    const hasMore = children.length > maxChildrenPerNode;

    steps.push({
      id: node.id,
      name: node.name,
      desc: getNodeDescription(node),
      parent: parentStepId,
      coords: { x: 50, y: 12 + depth * 20 },
      salary: undefined,
      companies: [],
      colleges: [],
      entranceExams: [],
      resources: [],
      checklist: [],
      sub_topics: visibleChildren.slice(0, 5).map(c => ({ label: c.name })),
      sub_topics_title: depth === 0 ? 'Career Directions' : 'Next Steps'
    });

    for (const child of visibleChildren) {
      traverse(child, node.id, depth + 1);
    }

    if (hasMore) {
      steps.push({
        id: `${node.id}-more`,
        name: `+${children.length - maxChildrenPerNode} more paths`,
        desc: `${children.length - maxChildrenPerNode} additional career paths branch from here. Search to find specific directions.`,
        parent: node.id,
        coords: { x: 50, y: 12 + (depth + 1) * 20 },
        salary: undefined, companies: [], colleges: [], entranceExams: [],
        resources: [], checklist: [], sub_topics: [], sub_topics_title: 'More'
      });
    }
  }

  traverse(root, null, 0);
  return steps;
}

export function getCareerSubtree(keyword, maxDepth = 6) {
  const { tree } = parseCareerPaths();
  const lowerKw = keyword.toLowerCase();

  function findBestMatch(nodes, parentPath = []) {
    let bestMatch = null;
    let bestScore = 0;
    const nodeArray = Array.isArray(nodes) ? nodes : [nodes];

    for (const node of nodeArray) {
      const nameLower = node.name.toLowerCase();
      let score = 0;
      if (nameLower === lowerKw) score = 100;
      else if (nameLower.startsWith(lowerKw)) score = 80;
      else if (nameLower.includes(lowerKw)) score = 60;
      else {
        const words = lowerKw.split(/\s+/);
        const nameWords = nameLower.split(/\s+/);
        const matchedWords = words.filter(w => nameWords.some(nw => nw.includes(w) || w.includes(nw)));
        score = (matchedWords.length / Math.max(words.length, 1)) * 50;
      }

      if (score > bestScore) {
        bestScore = score;
        bestMatch = { node, path: [...parentPath, node] };
      }

      if (node.children && node.children.length > 0) {
        const childMatch = findBestMatch(node.children, [...parentPath, node]);
        if (childMatch && childMatch.score > bestScore) {
          bestScore = childMatch.score;
          bestMatch = childMatch;
        }
      }
    }
    return bestMatch ? { ...bestMatch, score: bestScore } : null;
  }

  const match = findBestMatch(tree);
  if (!match || match.score < 10) return [];

  const steps = [];
  const visited = new Set();

  // Add ancestors (path from root to matched node)
  for (const ancestor of match.path) {
    if (!visited.has(ancestor.id)) {
      visited.add(ancestor.id);
      steps.push({
        id: ancestor.id,
        name: ancestor.name,
        desc: getNodeDescription(ancestor),
        parent: ancestor.parentId || null,
        coords: { x: 50, y: 12 + ancestor.depth * 20 },
        salary: undefined, companies: [], colleges: [], entranceExams: [],
        resources: [], checklist: [],
        sub_topics: [],
        sub_topics_title: 'Steps'
      });
    }
  }

  // Add children of the matched node
  const matchedNode = match.node;
  function addChildren(node, parentStepId, depth) {
    if (depth > maxDepth || !node.children) return;
    const visibleChildren = node.children.slice(0, 8);
    for (const child of visibleChildren) {
      if (!visited.has(child.id)) {
        visited.add(child.id);
        steps.push({
          id: child.id,
          name: child.name,
          desc: getNodeDescription(child),
          parent: parentStepId,
          coords: { x: 50, y: 12 + depth * 20 },
          salary: undefined, companies: [], colleges: [], entranceExams: [],
          resources: [], checklist: [],
          sub_topics: child.children ? child.children.slice(0, 3).map(c => ({ label: c.name })) : [],
          sub_topics_title: 'Next Steps'
        });
        addChildren(child, child.id, depth + 1);
      }
    }
  }

  addChildren(matchedNode, matchedNode.id, matchedNode.depth + 1);
  return steps;
}

export function searchPathsByKeyword(keyword) {
  const { tree } = parseCareerPaths();
  const lowerKw = keyword.toLowerCase();
  const results = [];

  function searchNode(node, path = []) {
    const currentPath = [...path, node];
    if (node.name.toLowerCase().includes(lowerKw)) {
      results.push({
        id: node.id,
        name: node.name,
        path: currentPath.map(n => n.name),
        depth: node.depth,
        childCount: node.children ? node.children.length : 0,
        pathCount: node.pathCount
      });
    }
    if (node.children) {
      for (const child of node.children) {
        if (results.length < 20) searchNode(child, currentPath);
      }
    }
  }

  if (tree) searchNode(tree);
  return results.slice(0, 20);
}

export function getTreeStats() {
  const { stats } = parseCareerPaths();
  return stats;
}

export function getRootBranches() {
  const { tree } = parseCareerPaths();
  if (!tree) return [];
  const root = tree; // tree IS the root node
  return (root.children || []).map(child => ({
    id: child.id,
    name: child.name,
    pathCount: child.pathCount,
    childCount: child.children ? child.children.length : 0
  })).sort((a, b) => b.pathCount - a.pathCount);
}

function getNodeDescription(node) {
  const childCount = node.children ? node.children.length : 0;
  if (node.depth === 0) return `India's comprehensive career directory — ${node.pathCount} career paths mapped from this starting point.`;
  if (childCount > 0) return `${node.name} opens up to ${childCount} different career directions. ${node.pathCount} students follow this pathway.`;
  return `${node.name} — a career destination in this pathway. ${node.pathCount} students reach this milestone.`;
}

export function clearCache() {
  cachedTree = null;
  cachedKeywordIndex = null;
  cacheStats = { totalPaths: 0, totalUniqueNodes: 0, rootCount: 0 };
  nodeCounter = 0;
}
