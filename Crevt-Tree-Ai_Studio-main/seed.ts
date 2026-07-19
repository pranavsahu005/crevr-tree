import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ROADMAPS_DATABASE } from './src/data.ts';
import { dbQuery, initializeDatabase, dbType } from './db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runSeeder() {
  console.log('[CrevrTree Seeder] Starting database seeder...');
  
  // 1. Initialize tables first
  await initializeDatabase();

  // 2. Seed Curated Roadmaps
  console.log(`[CrevrTree Seeder] Seeding ${ROADMAPS_DATABASE.length} curated roadmaps...`);
  
  for (const roadmap of ROADMAPS_DATABASE) {
    try {
      console.log(`- Seeding roadmap: ${roadmap.name} (${roadmap.id})`);
      
      // Insert into roadmaps
      await dbQuery(
        'INSERT INTO roadmaps (id, name, category, tagline) VALUES (?, ?, ?, ?)',
        [roadmap.id, roadmap.name, roadmap.category, roadmap.tagline]
      );
      
      // Insert all steps of the roadmap
      for (const step of roadmap.steps) {
        await dbQuery(
          'INSERT INTO roadmap_steps (id, roadmap_id, name, desc_content, official, resources, checklist, parent, coords, salary, companies, colleges, entranceExams) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
          [
            step.id,
            roadmap.id,
            step.name,
            step.desc,
            step.official ? JSON.stringify(step.official) : null,
            step.resources ? JSON.stringify(step.resources) : '[]',
            step.checklist ? JSON.stringify(step.checklist) : '[]',
            step.parent,
            JSON.stringify(step.coords),
            step.salary || null,
            step.companies ? JSON.stringify(step.companies) : '[]',
            step.colleges ? JSON.stringify(step.colleges) : '[]',
            step.entranceExams ? JSON.stringify(step.entranceExams) : '[]'
          ]
        );
      }
    } catch (err) {
      console.error(`Error seeding roadmap ${roadmap.id}:`, err.message);
    }
  }

  // 3. Seed Knowledge Graph Nodes (if files exist)
  const nodesPath = path.join(__dirname, '..', 'database', 'career_graph_output_v3', 'nodes.json');
  if (fs.existsSync(nodesPath)) {
    console.log('[CrevrTree Seeder] Reading nodes.json for knowledge graph...');
    try {
      const nodesData = JSON.parse(fs.readFileSync(nodesPath, 'utf8'));
      console.log(`[CrevrTree Seeder] Seeding ${nodesData.length} knowledge graph nodes...`);
      
      // Batch inserts or individual inserts with try-catch
      let successCount = 0;
      for (const node of nodesData) {
        try {
          await dbQuery(
            `INSERT INTO nodes (
              node_id, node_type, title, description, category, difficulty,
              education_level, career_level, estimated_duration_months, salary_band_inr,
              growth_score, demand_score, automation_risk, ai_impact, remote_work_potential,
              global_opportunity, government_opportunity, private_opportunity, freelance_opportunity,
              entrepreneurship_opportunity, prerequisites, skills_required, skills_gained,
              recommended_certifications, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
              node.node_id,
              node.node_type || '',
              node.title || '',
              node.description || '',
              node.category || '',
              node.difficulty !== undefined ? node.difficulty : 1,
              node.education_level || null,
              node.career_level || null,
              node.estimated_duration_months !== undefined ? node.estimated_duration_months : null,
              node.salary_band_inr || '',
              node.growth_score !== undefined ? node.growth_score : 0.0,
              node.demand_score !== undefined ? node.demand_score : 0.0,
              node.automation_risk !== undefined ? node.automation_risk : 0.0,
              node.ai_impact !== undefined ? node.ai_impact : 0.0,
              node.remote_work_potential !== undefined ? node.remote_work_potential : 0.0,
              node.global_opportunity !== undefined ? node.global_opportunity : 0.0,
              node.government_opportunity !== undefined ? node.government_opportunity : 0.0,
              node.private_opportunity !== undefined ? node.private_opportunity : 0.0,
              node.freelance_opportunity !== undefined ? node.freelance_opportunity : 0.0,
              node.entrepreneurship_opportunity !== undefined ? node.entrepreneurship_opportunity : 0.0,
              node.prerequisites ? JSON.stringify(node.prerequisites) : '[]',
              node.skills_required ? JSON.stringify(node.skills_required) : '[]',
              node.skills_gained ? JSON.stringify(node.skills_gained) : '[]',
              node.recommended_certifications ? JSON.stringify(node.recommended_certifications) : '[]',
              node.metadata ? JSON.stringify(node.metadata) : '{}'
            ]
          );
          successCount++;
        } catch (e) {
          // Ignore duplicate node errors during reseeding
          if (!e.message.includes('UNIQUE') && !e.message.includes('Duplicate entry') && !e.message.includes('duplicate key')) {
            console.error(`Error inserting node ${node.title}:`, e.message);
          }
        }
      }
      console.log(`[CrevrTree Seeder] Successfully seeded ${successCount} nodes.`);
    } catch (err) {
      console.error('[CrevrTree Seeder] Error parsing nodes.json:', err.message);
    }
  } else {
    console.warn(`[CrevrTree Seeder] nodes.json not found at ${nodesPath}`);
  }

  // 4. Seed Knowledge Graph Edges (if files exist)
  const edgesPath = path.join(__dirname, '..', 'database', 'career_graph_output_v3', 'edges.json');
  if (fs.existsSync(edgesPath)) {
    console.log('[CrevrTree Seeder] Reading edges.json for knowledge graph...');
    try {
      const edgesData = JSON.parse(fs.readFileSync(edgesPath, 'utf8'));
      console.log(`[CrevrTree Seeder] Seeding ${edgesData.length} knowledge graph edges...`);
      
      let successCount = 0;
      for (const edge of edgesData) {
        try {
          await dbQuery(
            `INSERT INTO edges (
              source_id, destination_id, relationship_type, required_skills,
              optional_skills, estimated_time_months, transition_difficulty,
              recommended_certifications, probability, confidence, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
              edge.source_id,
              edge.destination_id,
              edge.relationship_type,
              edge.required_skills ? JSON.stringify(edge.required_skills) : '[]',
              edge.optional_skills ? JSON.stringify(edge.optional_skills) : '[]',
              edge.estimated_time_months !== undefined ? edge.estimated_time_months : null,
              edge.transition_difficulty !== undefined ? edge.transition_difficulty : 1,
              edge.recommended_certifications ? JSON.stringify(edge.recommended_certifications) : '[]',
              edge.probability !== undefined ? edge.probability : 0.5,
              edge.confidence !== undefined ? edge.confidence : 0.8,
              edge.metadata ? JSON.stringify(edge.metadata) : '{}'
            ]
          );
          successCount++;
        } catch (e) {
          if (!e.message.includes('UNIQUE') && !e.message.includes('Duplicate entry') && !e.message.includes('duplicate key') && !e.message.includes('PRIMARY')) {
            console.error(`Error inserting edge ${edge.source_id} -> ${edge.destination_id}:`, e.message);
          }
        }
      }
      console.log(`[CrevrTree Seeder] Successfully seeded ${successCount} edges.`);
    } catch (err) {
      console.error('[CrevrTree Seeder] Error parsing edges.json:', err.message);
    }
  } else {
    console.warn(`[CrevrTree Seeder] edges.json not found at ${edgesPath}`);
  }

  console.log('[CrevrTree Seeder] Seeding process complete!');
  process.exit(0);
}

runSeeder().catch(err => {
  console.error('[CrevrTree Seeder] Fatal error during seeding:', err);
  process.exit(1);
});
