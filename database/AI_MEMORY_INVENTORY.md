# PROJECT INVENTORY: Indian Career Intelligence Knowledge Graph Generator

## ROOT PATH
C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project

## DIRECTORY TREE

Base-India-Career-Project/
|--- career_graph_output/                 (V2 output - 10 files, 11KB-133KB each)
|--- career_graph_output_v3/              (V3 output - 10 files, 153B-54MB each)
|--- venv_career/                         (Python virtual environment)
|--- __pycache__/                         (Python bytecode cache)
|--- career_generator_v3.py               (FINAL V3 SCRIPT - 2024 lines, 140KB)
|--- deepseek_python_20260718_b8e969.py   (V2 script - 1172 lines, 52KB)
|--- deepseek_python_20260718_2bd39f.py   (V1 script - legacy, 126KB)
|--- deepseek_text_prompt.txt             (Original prompt - 17KB, 167 lines)
|--- career_checkpoint.json               (V2 checkpoint - 12KB)
|--- career_checkpoint_v3.json            (V3 checkpoint - 12KB)
|--- career_graph_output.zip              (V2 archive - 42KB)
|--- career_graph_output_v3.zip           (V3 archive - 1.6MB)
|--- validate.py                          (V2 validation script)
|--- *.py                                 (Build helper scripts, prefixed with _)
|--- AI_MEMORY_INVENTORY.md               (THIS FILE)

## FILE BY FILE INVENTORY

### 1. PRODUCTION SCRIPTS

**career_generator_v3.py** (FINAL - USE THIS)
  Size: 140,598 bytes / 2,024 lines
  Type: Python 3 script
  Role: Knowledge graph generator for Indian career ecosystem
  Output: 200,000 career paths, 1,023 nodes, 456 edges
  Dependencies: pyyaml, pybloom-live (optional), standard library
  Key classes: GeneratorConfig, Node, Edge, DeduplicationTracker, CheckpointManager,
    MultiFormatWriter, NodeFactory, EdgeBuilder, TransitionValidator, Taxonomies,
    CareerPathGenerator, CareerGraphGenerator
  Features: Multi-format output (JSONL, JSON, CSV, YAML, TXT), Bloom filter dedup,
    resumable checkpoints, deterministic UUID generation, 140+ seed starting points

**deepseek_python_20260718_b8e969.py** (V2 script)
  Size: 52,802 bytes / 1,172 lines
  Type: Python 3 script
  Role: Earlier version of career graph generator
  Output: 189 nodes, 99 edges, ~131 career paths
  Limitations: Small taxonomy (23 UG, 8 PG, 18 exams, 35 jobs, 20 skills, 32 companies,
    27 industries), low branch probability (0.3), only 5 seed titles

**deepseek_python_20260718_2bd39f.py** (V1 script - legacy/backup)
  Size: 126,467 bytes
  Type: Python 3 script
  Role: Earlier prototype version

### 2. PROMPT FILE

**deepseek_text_prompt.txt**
  Size: 17,014 bytes / 167 lines
  Content: Two-part prompt instructing AI to:
    Part 1: Run and validate existing V2 script
    Part 2: Expand to V3 with 200,000+ career paths by expanding taxonomy (500+ jobs,
      80+ exams, 200+ education entries, 200+ certs, 200+ companies, 50+ industries),
      enhancing branching logic, fixing type override bug, adding node write-on-create

### 3. CHECKPOINT FILES

**career_checkpoint.json**
  Size: 11,879 bytes
  State: V2 generator state at completion (131 paths)

**career_checkpoint_v3.json**
  Size: 11,877 bytes
  State: V3 generator state at 200,000 paths

### 4. OUTPUT DIRECTORIES

#### career_graph_output/ (V2 - 10 files)

nodes.jsonl     132.5 KB  189 lines  (6 node types)
edges.jsonl      32.1 KB   99 lines  (4 edge types)
nodes.json      132.7 KB  191 lines  (valid JSON array)
edges.json       32.8 KB  101 lines  (valid JSON array)
nodes.csv        29.9 KB  190 rows   (headers: node_id,node_type,title,...)
edges.csv        10.5 KB  100 rows   (headers: source_id,destination_id,...)
nodes.yaml      130.5 KB            (valid YAML)
edges.yaml       32.1 KB            (valid YAML)
career_paths.txt 14.0 KB  262 lines (~131 paths with --- separators)
generation_stats.json  (NOT PRESENT in V2 output)

#### career_graph_output_v3/ (V3 - 10 files, 54.45 MB total)

nodes.jsonl     687.5 KB  1,021 entries  (7 node types present)
edges.jsonl     151.8 KB    456 entries  (4 edge types)
nodes.json      686.5 KB  1,023 lines    (valid JSON array)
edges.json      151.4 KB    458 lines    (valid JSON array)
nodes.csv       675.6 KB  1,022 rows     (CSV with headers)
edges.csv        47.8 KB    457 rows     (CSV with headers)
nodes.yaml      155.8 KB                (valid YAML)
edges.yaml       53.1 KB                (valid YAML)
career_paths.txt 54.0 MB  400,000 lines (200,000 paths, each separated by ---)
generation_stats.json  153 bytes         (JSON stats object)

V3 OUTPUT NODE BREAKDOWN:
  education:      220 nodes (from taxonomy)
  job_role:       260 nodes (from taxonomy)
  company:        154 nodes (from taxonomy)
  skill:          124 nodes (from taxonomy)
  industry:       110 nodes (from taxonomy)
  exam:            78 nodes (from taxonomy)
  certification:   75 nodes (from taxonomy)
  Total:        1,023 nodes

V3 OUTPUT EDGE BREAKDOWN:
  branch:         295 edges
  next_step:       55 edges
  requires_skill:  56 edges
  can_work_at:     50 edges
  Total:          456 edges

### 5. ARCHIVES

career_graph_output.zip     (V2 output)         42 KB
career_graph_output_v3.zip  (V3 output)        1.6 MB  (54 MB uncompressed)

### 6. BUILD HELPER SCRIPTS (all prefixed with _)

_write_v3.py        38.3 KB  Generated prefix (base classes + TransitionValidator)
_write_v3_p2.py     27.2 KB  Generated JOB_ROLES taxonomy section
_write_v3_p3.py     19.4 KB  Generated SKILLS, CERTIFICATIONS, COMPANIES, INDUSTRIES,
                              LEARNING_RESOURCES
_write_generator.py 47.8 KB  Generated Taxonomies methods, CareerPathGenerator,
                              CareerGraphGenerator class + main()
_assemble.py        15.6 KB  Assembly script (failed attempt - indentation issue)
_assemble_final.py   2.1 KB  Final assembly script that concatenates all parts
_run_test.py         2.7 KB  Test runner (original - has checkpoint monkey-patch)
_run_v3.py           1.5 KB  V3 runner with configurable path count
_validate.py         5.2 KB  Validation script for V3 output

### 7. INTERMEDIATE BUILD FILES

taxonomies_part.py   27.0 KB  Taxonomies class with SCHOOL_STREAMS, ITI_TRADES,
                              DIPLOMAS, UNDERGRAD_DEGREES, POSTGRAD_DEGREES,
                              DOCTORATES, EXAMS
jobroles_part.py     27.1 KB  JOB_ROLES OrderedDict (258 job roles)
rest_taxonomies.py   19.4 KB  SKILLS, CERTIFICATIONS, COMPANIES, INDUSTRIES,
                              LEARNING_RESOURCES OrderedDicts
generator_logic.py   48.3 KB  Taxonomies methods, CareerPathGenerator (progression
                              chains, exam-to-education map, job-to-education map,
                              job lateral map), CareerGraphGenerator (main generation
                              loop, education_next/exam_next/job_role_next/
                              certification_next/enrichment methods), main()

## TAXONOMY DATA (embedded in career_generator_v3.py)

Category              Count
-------------------   -----
SCHOOL_STREAMS           8  (10th, 11th Science/Commerce/Arts, 12th PCM/PCB/Commerce/Arts)
ITI_TRADES              25  (Electrician, Fitter, Welder, Plumber, Carpenter, Painter,
                              Machinist, Turner, COPA, Electronics, Refrigeration,
                              Diesel Mechanic, Motor Mechanic, Solar Technician,
                              CNC Operator, Agriculture Machinery, Wireman, Surveyor,
                              Draftsman Civil, Draftsman Mechanical, Horticulture,
                              Food Processing, Textile, Foundry, Leather Goods)
DIPLOMAS                 24  (Computer, Mechanical, Civil, Electrical, EC, Chemical,
                              Automobile, IT, Mining, Petroleum, Food Technology,
                              Aeronautical, Marine, Hotel Management, Fashion Design,
                              Interior Design, Pharmacy, Medical Lab Tech, Radiology,
                              Event Management, Journalism, Film Making, Graphic Design,
                              Fire & Safety)
UNDERGRAD_DEGREES        84  (29 Engineering B.Tech, 1 B.Pharma, 20 B.Sc, 8 B.Com,
                              9 BBA, 6 BCA, 15 BA, 4 LLB variants, MBBS, BDS, BAMS,
                              BHMS, B.Arch)
POSTGRAD_DEGREES         65  (12 M.Tech, 15 M.Sc, MCA, 14 MBA + specializations,
                              M.Com, 8 MA, LLM, 6 MD, 4 MS, M.Pharma, M.Arch,
                              M.Plan, M.Lib.Sc)
DOCTORATES               14  (PhD in CS, Physics, Chemistry, Math, Economics,
                              Management, Biotech, Mechanical, Electrical, Medicine,
                              Law, Psychology, Agriculture, Pharmacy)
EXAMS                    79  (Engineering: JEE Main/Advanced, BITSAT, VITEEE, SRMJEEE,
                              COMEDK, MHT CET, KCET, AP EAMCET, TS EAMCET, GUJCET,
                              OJEE, BCECE, WBJEE, CUET, MET, NPAT, SET, MUCMET;
                              Medical: NEET, NEET PG, AIIMS, JIPMER, MCAT, USMLE, PLAB;
                              Management: CAT, XAT, SNAP, NMAT, IIFT, CMAT, MAT, GMAT;
                              Postgrad: GATE; Civil Services: UPSC CSE, CAPF, EPFO,
                              State PSC; Staff Selection: SSC CGL, JE, CHSL;
                              Banking: IBPS PO/Clerk/SO, SBI PO/Clerk, RBI Grade B/
                              Assistant, NABARD, SEBI; Insurance: LIC AAO, NICL AO;
                              Railway: RRB NTPC, ALP, Technician; Law: CLAT, AILET,
                              LSAT; CA/CS: CA Foundation, CS Foundation, CMA Foundation;
                              Design: NIFT, NID DAT, CEED; Academic: UGC NET;
                              International: GRE, IELTS, TOEFL, PTE, OET;
                              Others: NCHM JEE, DU JAT, FTII, SRFTI, CTET, DSSSB,
                              KVS, NVS)
JOB_ROLES                258  (IT/Software: 32 roles; Data/AI: 14; Mechanical: 12;
                              Civil: 7; Electrical/Electronics: 6; Automobile: 2;
                              Aerospace/Marine: 2; Chemical/Pharma/Biotech: 5;
                              Medicine/Healthcare: 22; Banking/Finance/Insurance: 18;
                              Accounting/Audit: 5; Law/Legal: 5; Management/Consulting: 9;
                              Marketing/Sales: 12; HR: 5; Supply Chain/Logistics: 7;
                              Agriculture/Food: 4; Government/Civil Services: 15;
                              Police: 7; PSU/Defence: 5; Teaching/Academia: 10;
                              Media/Entertainment: 9; Design/Creative: 7;
                              Hospitality/Tourism: 5; Sports/Fitness: 5;
                              Social Work/NGO: 3; Entrepreneurship: 3;
                              E-commerce/Retail: 5; Energy/Renewable: 3;
                              Mining/Metallurgy: 2; ITI/Vocational: 8;
                              Miscellaneous: 10)
SKILLS                   110  (Programming: 18; Database: 7; Cloud: 3; DevOps: 8;
                              System: 1; AI/ML: 8; Data: 5; Office: 3; Soft: 8;
                              Finance: 3; Accounting: 2; Tax: 2; ERP: 5; CRM: 3;
                              Design: 5; CAD: 3; Simulation: 1; GameDev: 2;
                              Automation: 3; Healthcare: 3; Compliance: 1;
                              Legal: 6; Marketing: 9; Mgmt: 6; Quality: 4)
CERTIFICATIONS            75  (Cloud: 7; Security: 10; DevOps: 3; ProjectMgmt: 8;
                              ITSM: 2; Testing: 2; Programming/Database: 3;
                              Networking: 3; Linux: 2; CRM/Marketing: 6;
                              Design/CAD: 2; Accounting/Finance: 10; Audit: 1;
                              Safety: 2; Food: 2; Compliance: 3; Quality: 4;
                              Academic: 3)
COMPANIES                142  (IT Services: 10; MNC Tech: 14; Indian Startups: 43;
                              Indian Corporates: 15; PSUs: 16; Banks/Financial: 12;
                              MNC Industrial: 12; Pharma: 10; Healthcare: 6;
                              Education: 9)
INDUSTRIES               110  (IT, Software, Banking, Finance, Healthcare, Pharma,
                              Automobile, Manufacturing, Construction, Retail,
                              Ecommerce, Telecom, Media, Education, Government,
                              Agriculture, Energy, Aerospace, AND 80+ MORE)
LEARNING_RESOURCES        49  (NPTEL, Coursera, edX, Udemy, Indian coaching: Allen,
                              Aakash, Resonance, Made Easy, ACE Academy, etc.)

## V2 vs V3 COMPARISON

Metric                V2             V3            Change
------                --             --            ------
Script lines          1,172          2,024         +852 lines (1.7x)
Script size           52.8 KB        140.6 KB      +87.8 KB (2.7x)
Education nodes       46             220           +174 (4.8x)
Exam nodes            18             78            +60 (4.3x)
Job role nodes        45             260           +215 (5.8x)
Skill nodes           22             124           +102 (5.6x)
Company nodes         32             154           +122 (4.8x)
Industry nodes        27             110           +83 (4.1x)
Certification nodes   N/A            75            NEW
Total paths           ~131           200,000       +1526x
Total nodes           189            1,023         +834 (5.4x)
Total edges           99             456           +357 (4.6x)
Output size           ~420 KB        54.45 MB      +130x
Seeds                 5              140+          +28x
Branch probability    0.3            0.7           +0.4
Max path length       12             16            +4
Cycle detection       entire path    last 4 steps  relaxed
Type field bug        present        fixed         (_node_type instead of type)
Node writes           on init only   immediate     write-on-create

## KEY FIXES APPLIED IN V3

1. TYPE OVERRIDE BUG: Original Taxonomies used "type" key in dicts which conflicted
   with NodeType enum. Fixed by renaming to "_node_type" in taxonomy dicts and
   NodeFactory.create reads from "_node_type".
2. MISSING NODE WRITES: Nodes created dynamically during path generation were not
   written to output files. Fixed by writing immediately upon creation in
   _get_or_create_node.
3. CHECKPOINT SERIALIZATION: random.getstate() returns tuple(tuple(float,...)) but
   json.dump converts inner tuple to list. On load, list needs conversion back to
   tuple for random.setstate(). Fixed in both save() and load().
4. CYCLE DETECTION: Original blocked any revisiting of same node in entire path.
   Changed to only block revisits within last 4 steps, enabling more diverse paths.
5. BRANCH LIMITING: Original limited to max 2 branch paths. Changed to consider
   up to 8 branch options with branch_probability=0.7.
6. SEED EXPANSION: Original had 5 seeds (10th + 4 diplomas). Expanded to 140+
   seeds including all ITI trades, all diplomas, all school streams, all undergrad
   degrees.

## GENERATION WORKFLOW

1. Build taxonomy -> all node dicts (education, exam, job_role, skill, company,
   industry, certification)
2. Create Node objects for each with deterministic UUIDs
3. Track signatures in DeduplicationTracker (Bloom filter for memory efficiency)
4. Save checkpoint periodically (counts + random state)
5. For each seed title (140+ starting points):
   a. Call _expand_from_node recursively
   b. Determine next steps based on current node type (education/exam/job_role/cert)
   c. Shuffle options, take main path + probabilistic branches
   d. Create destination nodes on demand, write immediately
   e. Count and write path text when reaching job_role or cert
   f. Continue expanding from destination (don't stop at job roles)
6. Add enrichment edges (requires_skill, can_work_at) dynamically
7. Write all formats concurrently via MultiFormatWriter
8. Finalize: close JSON arrays, close all file handles
9. Save generation_stats.json

## DATA FLOW GRAPH

Prompt file (deepseek_text_prompt.txt)
  -> V2 Script (deepseek_python_20260718_b8e969.py)
    -> V2 Output (career_graph_output/): 131 paths, 189 nodes, 99 edges
  -> V3 Build Helpers (_write_v3*.py, _write_generator.py)
    -> Intermediate build parts (taxonomies_part.py, jobroles_part.py,
       rest_taxonomies.py, generator_logic.py)
    -> _assemble_final.py concatenates into career_generator_v3.py
  -> V3 Script (career_generator_v3.py)
    -> _run_v3.py executes with max_total_paths=200000
    -> V3 Output (career_graph_output_v3/): 200,000 paths, 1,023 nodes, 456 edges
    -> Archive (career_graph_output_v3.zip)
  -> Validation (_validate.py) checks:
       - All 10 output files exist
       - JSON/JSONL validity
       - CSV/YAML validity
       - No duplicate node IDs
       - Edge referential integrity (all source/dest exist)
       - Sample nodes random check

## GENERATOR CONFIGURATION PARAMETERS

GeneratorConfig:
  output_dir                = "./career_graph_output_v3"
  checkpoint_file           = "./career_checkpoint_v3.json"
  formats                   = ["jsonl", "json", "csv", "yaml", "txt"]
  max_total_paths           = 200000
  max_nodes                 = 500000
  max_edges                 = 1000000
  random_seed               = 42
  branch_probability        = 0.7
  max_path_length           = 16
  duplicate_detection_method = "bloom"
  bloom_filter_capacity     = 10000000
  bloom_filter_error_rate   = 0.001
  resume                    = True
  log_interval              = 10000
  batch_size                = 1000

## COMPLETE NODE TYPE ENUM

NodeType:
  EDUCATION       = "education"       (220 nodes in output)
  CERTIFICATION   = "certification"   (75 nodes in output)
  EXAM            = "exam"            (78 nodes in output)
  JOB_ROLE        = "job_role"        (260 nodes in output)
  SKILL           = "skill"           (124 nodes in output)
  TOOL            = "tool"            (0 nodes in output - unused)
  INDUSTRY        = "industry"        (110 nodes in output)
  COMPANY         = "company"         (154 nodes in output)
  CAREER_PATH     = "career_path"     (0 nodes in output - unused)

## COMPLETE EDGE TYPE ENUM

EdgeType:
  NEXT_STEP                 = "next_step"           (55 edges)
  BRANCH                    = "branch"              (295 edges)
  REQUIRES_SKILL            = "requires_skill"       (56 edges - skill->job)
  RECOMMENDS_CERTIFICATION  = "recommends_certification" (unused in output)
  CAN_WORK_AT               = "can_work_at"         (50 edges - job->company)
  LEADS_TO                  = "leads_to"            (unused in output)
  ENRICHES                  = "enriches"            (unused in output)

## EDGE GENERATION PATTERNS

Education -> Education via NEXT_STEP (school progression: 10th->11th->12th)
Education -> Education via BRANCH (alternative streams: science/commerce/arts)
Education -> Exam via NEXT_STEP (12th PCM->JEE Main)
Education -> Exam via BRANCH (alternative entrance exams)
Education -> Job_Role via NEXT_STEP (degree->direct job)
Exam -> Education via NEXT_STEP (cleared exam->college admission)
Exam -> Job_Role via NEXT_STEP (UPSC CSE->IAS Officer)
Exam -> Job_Role via BRANCH (alternative services)
Job_Role -> Job_Role via NEXT_STEP (promotion/progression)
Job_Role -> Job_Role via BRANCH (lateral move)
Job_Role -> Exam via BRANCH (upskilling for govt exams)
Job_Role -> Education via BRANCH (GATE/MBA/PhD)
Job_Role -> Certification via BRANCH (CA/CS/PMP/etc)
Certification -> Job_Role via NEXT_STEP (cert->role certification leads to)
Skill -> Job_Role via REQUIRES_SKILL (enrichment)
Job_Role -> Company via CAN_WORK_AT (enrichment)

## WHERE TO FIND WHAT

What                                File/Path
-----                               ---------
Final generator script              career_generator_v3.py
V2 generator script                 deepseek_python_20260718_b8e969.py
V1 generator script                 deepseek_python_20260718_2bd39f.py
Original prompt                     deepseek_text_prompt.txt
V3 output (all formats)             career_graph_output_v3/
V2 output (all formats)             career_graph_output/
V3 output archive                   career_graph_output_v3.zip
V2 output archive                   career_graph_output.zip
V3 checkpoint                       career_checkpoint_v3.json
V2 checkpoint                       career_checkpoint.json
Validation script (V3)              _validate.py
V3 runner script                    _run_v3.py
Build assembly script               _assemble_final.py
Build intermediate: Taxonomies      taxonomies_part.py
Build intermediate: Job Roles       jobroles_part.py
Build intermediate: Skills/etc      rest_taxonomies.py
Build intermediate: Generator logic generator_logic.py
Build helpers                       _write_v3.py, _write_v3_p2.py, _write_v3_p3.py,
                                    _write_generator.py, _assemble.py
Validated output stats              generation_stats.json (in output dir)
Python virtual env                  venv_career/

## ORIGINAL PROBLEM AND SOLUTION

PROBLEM: V2 script produced only 131 career paths from 189 nodes despite
max_total_paths=20000. Root causes:
  - Small taxonomy (23 UG, 10 PG, 18 exams, 35 jobs)
  - Low branch probability (0.3)
  - Only 5 seed starting points
  - Cycle prevention blocked entire path revisits
  - Paths terminated at job roles
  - type field in taxonomy dicts conflicted with NodeType enum

SOLUTION: V3 script produces 200,000 career paths from 1,023 nodes:
  - Massively expanded taxonomy (84 UG, 65 PG, 79 exams, 258 jobs, 110 skills,
    75 certs, 142 companies, 110 industries)
  - Branch probability raised to 0.7
  - 140+ seed starting points (all ITI trades, all diplomas, all UG degrees)
  - Cycle detection relaxed (last 4 steps only)
  - Paths continue through job progressions (don't stop)
  - type override bug fixed (_node_type)
  - Write-on-create for dynamic nodes
  - Checkpoint serialization fixed for random state

## ACCURACY NOTE

The generated data is based on realistic Indian career transitions but is
synthetic. Not all real-world nuances are captured. The taxonomy covers major
Indian education streams, competitive exams, job roles, companies, and
industries but is not exhaustive. Career path feasibility is validated through
TransitionValidator which maps degrees to allowed job roles and progression
chains.
