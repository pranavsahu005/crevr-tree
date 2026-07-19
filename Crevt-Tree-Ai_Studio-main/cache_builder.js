import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseCareerPaths, clearCache } from './careerPathsParser.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dataDir = path.join(__dirname, 'data_store');
const treePath = path.join(dataDir, 'career_tree.json');
const indexPath = path.join(dataDir, 'career_index.json');
const statsPath = path.join(dataDir, 'career_stats.json');

// Delete old cache files first to force dynamic parsing from the new career_paths.txt
try {
  if (fs.existsSync(treePath)) fs.unlinkSync(treePath);
  if (fs.existsSync(indexPath)) fs.unlinkSync(indexPath);
  if (fs.existsSync(statsPath)) fs.unlinkSync(statsPath);
  console.log('Deleted old cache files.');
} catch (e) {
  console.warn('Could not delete old cache files:', e.message);
}

clearCache();

// Parse career paths from newly compiled career_paths.txt
console.log('Generating new cache from career_paths.txt...');
const { tree, index, stats } = parseCareerPaths();

// Write new cache files
fs.writeFileSync(treePath, JSON.stringify(tree, null, 2), 'utf8');
fs.writeFileSync(indexPath, JSON.stringify(index, null, 2), 'utf8');
fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2), 'utf8');

console.log('✓ New cache files generated successfully!');
console.log('Tree nodes count:', stats.totalUniqueNodes);
console.log('Paths count:', stats.totalPaths);
