import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

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

let dbType = 'json'; // Fallback by default
let client = null;

// Determine DB type based on env vars
const dbUrl = process.env.DATABASE_URL || '';
const mysqlUrl = process.env.MYSQL_URL || '';

if (dbUrl.startsWith('postgres://') || dbUrl.startsWith('postgresql://')) {
  dbType = 'postgres';
} else if (dbUrl.startsWith('mysql://') || mysqlUrl.startsWith('mysql://')) {
  dbType = 'mysql';
} else {
  dbType = 'sqlite';
}

console.log(`[CrevrTree DB] Auto-detected Database Type: ${dbType}`);

// Define the query execution function interface
let dbQuery = async (sql, params = []) => {
  throw new Error('Database not initialized');
};

// Initialize connection based on DB Type
if (dbType === 'postgres') {
  try {
    const pg = await import('pg');
    const { Pool } = pg.default || pg;
    const pool = new Pool({
      connectionString: dbUrl,
      ssl: dbUrl.includes('localhost') ? false : { rejectUnauthorized: false }
    });
    client = pool;
    
    dbQuery = async (sql, params = []) => {
      // Convert ? placeholders to $1, $2 for Postgres
      let pgSql = sql;
      let count = 1;
      while (pgSql.includes('?')) {
        pgSql = pgSql.replace('?', `$${count++}`);
      }
      const res = await pool.query(pgSql, params);
      return res.rows;
    };
    console.log('[CrevrTree DB] Connected to PostgreSQL pool.');
  } catch (err) {
    console.error('[CrevrTree DB] Failed to load pg module. Falling back to JSON.', err);
    dbType = 'json';
  }
}

if (dbType === 'mysql') {
  try {
    const mysql = await import('mysql2/promise');
    const pool = mysql.createPool(mysqlUrl || dbUrl);
    client = pool;
    
    dbQuery = async (sql, params = []) => {
      const [rows] = await pool.execute(sql, params);
      return rows;
    };
    console.log('[CrevrTree DB] Connected to MySQL pool.');
  } catch (err) {
    console.error('[CrevrTree DB] Failed to load mysql2 module. Falling back to JSON.', err);
    dbType = 'json';
  }
}

if (dbType === 'sqlite') {
  try {
    const sqlite3 = await import('sqlite3');
    const dbFile = path.join(projectRoot, 'database.sqlite');
    const db = new sqlite3.default.Database(dbFile);
    client = db;

    dbQuery = (sql, params = []) => {
      return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        });
      });
    };
    console.log(`[CrevrTree DB] Connected to SQLite database at ${dbFile}`);
  } catch (err) {
    console.warn('[CrevrTree DB] Failed to initialize SQLite database. Falling back to JSON file database.', err);
    dbType = 'json';
  }
}

// Fallback JSON-file database implementation if binary installation fails or isn't needed
if (dbType === 'json') {
  const dataDir = path.join(projectRoot, 'data_store');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  const getFilePath = (table) => path.join(dataDir, `${table}.json`);
  const readData = (table) => {
    const filePath = getFilePath(table);
    if (!fs.existsSync(filePath)) return [];
    try {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch {
      return [];
    }
  };
  const writeData = (table, data) => {
    fs.writeFileSync(getFilePath(table), JSON.stringify(data, null, 2), 'utf8');
  };

  dbQuery = async (sql, params = []) => {
    const cleanedSql = sql.trim().replace(/\s+/g, ' ').toLowerCase();

    // Replicate basic operations needed for roadmap & node queries
    if (cleanedSql.startsWith('create table')) {
      return [];
    }

    if (cleanedSql.startsWith('insert into roadmaps')) {
      const data = readData('roadmaps');
      // INSERT INTO roadmaps (id, name, category, tagline) VALUES (?, ?, ?, ?)
      const [id, name, category, tagline] = params;
      const index = data.findIndex(r => r.id === id);
      const newRow = { id, name, category, tagline };
      if (index >= 0) data[index] = newRow;
      else data.push(newRow);
      writeData('roadmaps', data);
      return [];
    }

    if (cleanedSql.startsWith('insert into roadmap_steps')) {
      const data = readData('roadmap_steps');
      const [id, roadmap_id, name, desc, official, resources, checklist, parent, coords, salary, companies, colleges, entranceExams] = params;
      const index = data.findIndex(s => s.id === id);
      const newRow = { 
        id, roadmap_id, name, desc, 
        official: JSON.parse(official || 'null'), 
        resources: JSON.parse(resources || '[]'), 
        checklist: JSON.parse(checklist || '[]'), 
        parent, 
        coords: JSON.parse(coords || '{"x": 50, "y": 50}'), 
        salary, 
        companies: JSON.parse(companies || '[]'), 
        colleges: JSON.parse(colleges || '[]'), 
        entranceExams: JSON.parse(entranceExams || '[]')
      };
      if (index >= 0) data[index] = newRow;
      else data.push(newRow);
      writeData('roadmap_steps', data);
      return [];
    }

    if (cleanedSql.startsWith('insert into nodes')) {
      const data = readData('nodes');
      const [
        node_id, node_type, title, description, category, difficulty,
        education_level, career_level, estimated_duration_months, salary_band_inr,
        growth_score, demand_score, automation_risk, ai_impact, remote_work_potential,
        global_opportunity, government_opportunity, private_opportunity, freelance_opportunity,
        entrepreneurship_opportunity, prerequisites, skills_required, skills_gained,
        recommended_certifications, metadata
      ] = params;
      const index = data.findIndex(n => n.node_id === node_id);
      const newRow = {
        node_id, node_type, title, description, category, difficulty: Number(difficulty),
        education_level, career_level, estimated_duration_months: estimated_duration_months ? Number(estimated_duration_months) : null,
        salary_band_inr, growth_score: Number(growth_score), demand_score: Number(demand_score),
        automation_risk: Number(automation_risk), ai_impact: Number(ai_impact),
        remote_work_potential: Number(remote_work_potential), global_opportunity: Number(global_opportunity),
        government_opportunity: Number(government_opportunity), private_opportunity: Number(private_opportunity),
        freelance_opportunity: Number(freelance_opportunity), entrepreneurship_opportunity: Number(entrepreneurship_opportunity),
        prerequisites: JSON.parse(prerequisites || '[]'),
        skills_required: JSON.parse(skills_required || '[]'),
        skills_gained: JSON.parse(skills_gained || '[]'),
        recommended_certifications: JSON.parse(recommended_certifications || '[]'),
        metadata: JSON.parse(metadata || '{}')
      };
      if (index >= 0) data[index] = newRow;
      else data.push(newRow);
      writeData('nodes', data);
      return [];
    }

    if (cleanedSql.startsWith('insert into edges')) {
      const data = readData('edges');
      const [
        source_id, destination_id, relationship_type, required_skills,
        optional_skills, estimated_time_months, transition_difficulty,
        recommended_certifications, probability, confidence, metadata
      ] = params;
      const index = data.findIndex(e => e.source_id === source_id && e.destination_id === destination_id && e.relationship_type === relationship_type);
      const newRow = {
        source_id, destination_id, relationship_type,
        required_skills: JSON.parse(required_skills || '[]'),
        optional_skills: JSON.parse(optional_skills || '[]'),
        estimated_time_months: estimated_time_months ? Number(estimated_time_months) : null,
        transition_difficulty: Number(transition_difficulty),
        recommended_certifications: JSON.parse(recommended_certifications || '[]'),
        probability: Number(probability),
        confidence: Number(confidence),
        metadata: JSON.parse(metadata || '{}')
      };
      if (index >= 0) data[index] = newRow;
      else data.push(newRow);
      writeData('edges', data);
      return [];
    }

    if (cleanedSql.includes('select * from roadmaps') && !cleanedSql.includes('where')) {
      return readData('roadmaps');
    }

    if (cleanedSql.includes('select * from roadmaps') && cleanedSql.includes('where id =')) {
      const id = params[0];
      return readData('roadmaps').filter(r => r.id === id);
    }

    if (cleanedSql.includes('select * from roadmap_steps') && cleanedSql.includes('where roadmap_id =')) {
      const roadmap_id = params[0];
      const steps = readData('roadmap_steps').filter(s => s.roadmap_id === roadmap_id);
      
      // Map JSON structures back to string for database-like consistency
      return steps.map(s => ({
        ...s,
        official: JSON.stringify(s.official),
        resources: JSON.stringify(s.resources),
        checklist: JSON.stringify(s.checklist),
        coords: JSON.stringify(s.coords),
        companies: JSON.stringify(s.companies),
        colleges: JSON.stringify(s.colleges),
        entranceexams: JSON.stringify(s.entranceExams)
      }));
    }

    if (cleanedSql.includes('select * from nodes') && !cleanedSql.includes('where')) {
      const nodes = readData('nodes');
      return nodes.map(n => ({
        ...n,
        prerequisites: JSON.stringify(n.prerequisites),
        skills_required: JSON.stringify(n.skills_required),
        skills_gained: JSON.stringify(n.skills_gained),
        recommended_certifications: JSON.stringify(n.recommended_certifications),
        metadata: JSON.stringify(n.metadata)
      }));
    }

    if (cleanedSql.includes('select * from nodes') && (cleanedSql.includes('where title like') || cleanedSql.includes('or description like'))) {
      // Simple text search
      const searchTerm = params[0].replace(/%/g, '').toLowerCase();
      const nodes = readData('nodes').filter(n => 
        n.title.toLowerCase().includes(searchTerm) || 
        n.description.toLowerCase().includes(searchTerm)
      );
      return nodes.map(n => ({
        ...n,
        prerequisites: JSON.stringify(n.prerequisites),
        skills_required: JSON.stringify(n.skills_required),
        skills_gained: JSON.stringify(n.skills_gained),
        recommended_certifications: JSON.stringify(n.recommended_certifications),
        metadata: JSON.stringify(n.metadata)
      }));
    }

    if (cleanedSql.includes('select * from nodes') && cleanedSql.includes('where node_id =')) {
      const node_id = params[0];
      const nodes = readData('nodes').filter(n => n.node_id === node_id);
      return nodes.map(n => ({
        ...n,
        prerequisites: JSON.stringify(n.prerequisites),
        skills_required: JSON.stringify(n.skills_required),
        skills_gained: JSON.stringify(n.skills_gained),
        recommended_certifications: JSON.stringify(n.recommended_certifications),
        metadata: JSON.stringify(n.metadata)
      }));
    }

    if (cleanedSql.includes('select * from edges') && cleanedSql.includes('where source_id =') || cleanedSql.includes('destination_id =')) {
      const edges = readData('edges');
      return edges.map(e => ({
        ...e,
        required_skills: JSON.stringify(e.required_skills),
        optional_skills: JSON.stringify(e.optional_skills),
        recommended_certifications: JSON.stringify(e.recommended_certifications),
        metadata: JSON.stringify(e.metadata)
      }));
    }

    if (cleanedSql.includes('select * from edges')) {
      const edges = readData('edges');
      return edges.map(e => ({
        ...e,
        required_skills: JSON.stringify(e.required_skills),
        optional_skills: JSON.stringify(e.optional_skills),
        recommended_certifications: JSON.stringify(e.recommended_certifications),
        metadata: JSON.stringify(e.metadata)
      }));
    }

    return [];
  };
}

// Function to run database setup (create tables)
export async function initializeDatabase() {
  console.log('[CrevrTree DB] Initializing tables...');

  // SQLite and local schemas
  const isPostgres = dbType === 'postgres';
  const textType = isPostgres ? 'TEXT' : 'TEXT';
  const realType = isPostgres ? 'DOUBLE PRECISION' : 'REAL';

  const schema = [
    `CREATE TABLE IF NOT EXISTS roadmaps (
      id VARCHAR(255) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      category VARCHAR(255) NOT NULL,
      tagline VARCHAR(500) NOT NULL
    )`,

    `CREATE TABLE IF NOT EXISTS roadmap_steps (
      id VARCHAR(255) PRIMARY KEY,
      roadmap_id VARCHAR(255) NOT NULL,
      name VARCHAR(255) NOT NULL,
      desc_content TEXT NOT NULL,
      official ${textType},
      resources ${textType},
      checklist ${textType},
      parent VARCHAR(255),
      coords ${textType} NOT NULL,
      salary VARCHAR(255),
      companies ${textType},
      colleges ${textType},
      entranceExams ${textType}
    )`,

    `CREATE TABLE IF NOT EXISTS nodes (
      node_id VARCHAR(255) PRIMARY KEY,
      node_type VARCHAR(255) NOT NULL,
      title VARCHAR(255) NOT NULL,
      description TEXT,
      category VARCHAR(255),
      difficulty INTEGER,
      education_level VARCHAR(255),
      career_level VARCHAR(255),
      estimated_duration_months INTEGER,
      salary_band_inr VARCHAR(255),
      growth_score ${realType},
      demand_score ${realType},
      automation_risk ${realType},
      ai_impact ${realType},
      remote_work_potential ${realType},
      global_opportunity ${realType},
      government_opportunity ${realType},
      private_opportunity ${realType},
      freelance_opportunity ${realType},
      entrepreneurship_opportunity ${realType},
      prerequisites ${textType},
      skills_required ${textType},
      skills_gained ${textType},
      recommended_certifications ${textType},
      metadata ${textType}
    )`,

    `CREATE TABLE IF NOT EXISTS edges (
      source_id VARCHAR(255) NOT NULL,
      destination_id VARCHAR(255) NOT NULL,
      relationship_type VARCHAR(255) NOT NULL,
      required_skills ${textType},
      optional_skills ${textType},
      estimated_time_months INTEGER,
      transition_difficulty INTEGER,
      recommended_certifications ${textType},
      probability ${realType},
      confidence ${realType},
      metadata ${textType},
      PRIMARY KEY (source_id, destination_id, relationship_type)
    )`
  ];

  for (const query of schema) {
    try {
      await dbQuery(query);
    } catch (err) {
      console.error('[CrevrTree DB] Error executing initialization query:', err.message);
    }
  }

  console.log('[CrevrTree DB] Table initialization complete.');
}

// Export database type and client query
export { dbType, dbQuery };
