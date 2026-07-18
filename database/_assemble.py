#!/usr/bin/env python3
"""Assemble career_generator_v3.py from parts"""
import os

d = r'C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project'

# The base prefix
prefix = '''#!/usr/bin/env python3
"""Indian Career Intelligence Knowledge Graph Generator V3 - Massively Expanded."""
import json, csv, hashlib, logging, os, random, sys, time, uuid
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from itertools import product, chain
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Optional, Set, Tuple, Union
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("CareerGraphGenV3")

class NodeType(str, Enum):
    EDUCATION = "education"; CERTIFICATION = "certification"; EXAM = "exam"
    JOB_ROLE = "job_role"; SKILL = "skill"; TOOL = "tool"; INDUSTRY = "industry"; COMPANY = "company"; CAREER_PATH = "career_path"

class EdgeType(str, Enum):
    NEXT_STEP = "next_step"; BRANCH = "branch"; REQUIRES_SKILL = "requires_skill"
    RECOMMENDS_CERTIFICATION = "recommends_certification"; CAN_WORK_AT = "can_work_at"; LEADS_TO = "leads_to"; ENRICHES = "enriches"

class EducationLevel(str, Enum):
    SCHOOL = "school"; DIPLOMA = "diploma"; UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"; DOCTORATE = "doctorate"; POST_DOC = "post_doc"

class CareerLevel(str, Enum):
    ENTRY = "entry"; JUNIOR = "junior"; MID = "mid"; SENIOR = "senior"
    LEAD = "lead"; MANAGER = "manager"; DIRECTOR = "director"; VP = "vp"; CXO = "cxo"; FOUNDER = "founder"

@dataclass
class GeneratorConfig:
    output_dir: str = "./output"; checkpoint_file: str = "./checkpoint.json"
    formats: List[str] = field(default_factory=lambda: ["jsonl","json","csv","yaml","txt"])
    max_total_paths: int = 500; max_nodes: int = 500000; max_edges: int = 1000000
    random_seed: int = 42; branch_probability: float = 0.7; max_path_length: int = 16
    duplicate_detection_method: str = "bloom"
    bloom_filter_capacity: int = 10000000; bloom_filter_error_rate: float = 0.001
    resume: bool = True; log_interval: int = 10000; batch_size: int = 1000

def deterministic_uuid(seed_string: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_string))

def content_hash(*args: str) -> str:
    return hashlib.sha256("|".join(args).encode("utf-8")).hexdigest()

@dataclass
class Node:
    node_id: str; node_type: NodeType; title: str
    description: str = ""; category: str = ""; difficulty: int = 1
    education_level: Optional[EducationLevel] = None; career_level: Optional[CareerLevel] = None
    industry: str = ""; prerequisites: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list); skills_gained: List[str] = field(default_factory=list)
    recommended_certifications: List[str] = field(default_factory=list)
    estimated_duration_months: Optional[int] = None; salary_band_inr: str = ""
    growth_score: float = 0.0; demand_score: float = 0.0; automation_risk: float = 0.0
    ai_impact: float = 0.0; remote_work_potential: float = 0.0; global_opportunity: float = 0.0
    government_opportunity: float = 0.0; private_opportunity: float = 0.0
    freelance_opportunity: float = 0.0; entrepreneurship_opportunity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    def signature(self) -> str:
        return content_hash(f"{self.node_type.value}|{self.title}|{self.education_level or ''}|{self.career_level or ''}|{self.industry}")

@dataclass
class Edge:
    source_id: str; destination_id: str; relationship_type: EdgeType
    required_skills: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    estimated_time_months: Optional[int] = None; transition_difficulty: int = 1
    recommended_certifications: List[str] = field(default_factory=list)
    probability: float = 0.5; confidence: float = 0.8; metadata: Dict[str, Any] = field(default_factory=dict)
    def signature(self) -> str:
        return content_hash(f"{self.source_id}|{self.destination_id}|{self.relationship_type.value}")

class DeduplicationTracker:
    def __init__(self, config: GeneratorConfig):
        self.config = config
        if config.duplicate_detection_method == "bloom":
            try:
                from pybloom_live import BloomFilter
                self.filter = BloomFilter(capacity=config.bloom_filter_capacity, error_rate=config.bloom_filter_error_rate)
                self._is_bloom = True
            except ImportError:
                logger.warning("pybloom_live not available, using set")
                self._is_bloom = False; self._set: Set[str] = set()
        else:
            self._is_bloom = False; self._set = set()
    def add(self, sig: str) -> None:
        if self._is_bloom: self.filter.add(sig)
        else: self._set.add(sig)
    def exists(self, sig: str) -> bool:
        return sig in self.filter if self._is_bloom else sig in self._set
    def size(self) -> int:
        return len(self.filter) if self._is_bloom else len(self._set)

class CheckpointManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.state: Dict[str, Any] = {"generated_nodes_count": 0,"generated_edges_count": 0,"path_counter": 0,"random_state": random.getstate(),"dedup_signatures": []}
    def save(self, tracker: DeduplicationTracker, nc: int, ec: int, pc: int) -> None:
        self.state.update({"generated_nodes_count": nc,"generated_edges_count": ec,"path_counter": pc,"random_state": random.getstate()})
        if not tracker._is_bloom: self.state["dedup_signatures"] = list(tracker._set)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path,"w") as f: json.dump(self.state, f, default=str, indent=2)
    def load(self, tracker: DeduplicationTracker) -> Tuple[int, int, int]:
        if self.path.exists():
            with open(self.path) as f: self.state = json.load(f)
            random.setstate(tuple(self.state["random_state"]))
            if not tracker._is_bloom:
                for s in self.state.get("dedup_signatures",[]): tracker.add(s)
            logger.info(f"Resumed: {self.state['generated_nodes_count']}N {self.state['generated_edges_count']}E path#{self.state['path_counter']}")
            return (self.state["generated_nodes_count"],self.state["generated_edges_count"],self.state["path_counter"])
        return 0,0,0

class MultiFormatWriter:
    def __init__(self, output_dir: str, formats: List[str]):
        self.output_dir = Path(output_dir); self.output_dir.mkdir(parents=True, exist_ok=True)
        self.formats = formats; self.handles: Dict[str, Any] = {}; self._init_files()
    def _init_files(self):
        if "jsonl" in self.formats:
            self.handles["nodes_jsonl"] = open(self.output_dir/"nodes.jsonl","a",encoding="utf-8")
            self.handles["edges_jsonl"] = open(self.output_dir/"edges.jsonl","a",encoding="utf-8")
        if "csv" in self.formats:
            self.handles["nodes_csv"] = open(self.output_dir/"nodes.csv","a",newline="",encoding="utf-8")
            self.handles["edges_csv"] = open(self.output_dir/"edges.csv","a",newline="",encoding="utf-8")
            self._csv_writers = {}
        if "yaml" in self.formats:
            self.handles["nodes_yaml"] = open(self.output_dir/"nodes.yaml","a",encoding="utf-8")
            self.handles["edges_yaml"] = open(self.output_dir/"edges.yaml","a",encoding="utf-8")
        if "json" in self.formats:
            self.handles["nodes_json"] = open(self.output_dir/"nodes.json","a",encoding="utf-8")
            self.handles["edges_json"] = open(self.output_dir/"edges.json","a",encoding="utf-8")
            self._json_first_node = self._json_first_edge = True
            self.handles["nodes_json"].write("[\n"); self.handles["edges_json"].write("[\n")
        if "txt" in self.formats:
            self.handles["career_paths_txt"] = open(self.output_dir/"career_paths.txt","a",encoding="utf-8")
    def write_node(self, node: Node) -> None:
        nd = asdict(node); nd["node_type"] = node.node_type.value
        nd["education_level"] = node.education_level.value if node.education_level else None
        nd["career_level"] = node.career_level.value if node.career_level else None
        if "jsonl" in self.formats: self.handles["nodes_jsonl"].write(json.dumps(nd,ensure_ascii=False)+"\n")
        if "csv" in self.formats: self._get_csv_writer("nodes_csv",list(nd.keys())).writerow(nd)
        if "yaml" in self.formats: yaml.dump([nd],self.handles["nodes_yaml"],allow_unicode=True,default_flow_style=False)
        if "json" in self.formats:
            if not self._json_first_node: self.handles["nodes_json"].write(",\n")
            else: self._json_first_node = False
            json.dump(nd,self.handles["nodes_json"],ensure_ascii=False)
    def write_edge(self, edge: Edge) -> None:
        ed = asdict(edge); ed["relationship_type"] = edge.relationship_type.value
        if "jsonl" in self.formats: self.handles["edges_jsonl"].write(json.dumps(ed,ensure_ascii=False)+"\n")
        if "csv" in self.formats: self._get_csv_writer("edges_csv",list(ed.keys())).writerow(ed)
        if "yaml" in self.formats: yaml.dump([ed],self.handles["edges_yaml"],allow_unicode=True,default_flow_style=False)
        if "json" in self.formats:
            if not self._json_first_edge: self.handles["edges_json"].write(",\n")
            else: self._json_first_edge = False
            json.dump(ed,self.handles["edges_json"],ensure_ascii=False)
    def write_path_text(self, text: str) -> None:
        if "txt" in self.formats: self.handles["career_paths_txt"].write(text+"\n---\n")
    def _get_csv_writer(self, key: str, fields: List[str]):
        if key not in self._csv_writers:
            w = csv.DictWriter(self.handles[key],fieldnames=fields,extrasaction="ignore")
            if self.handles[key].tell() == 0: w.writeheader()
            self._csv_writers[key] = w
        return self._csv_writers[key]
    def finalize(self):
        if "json" in self.formats:
            self.handles["nodes_json"].write("\n]\n"); self.handles["edges_json"].write("\n]\n")
        for h in self.handles.values():
            if hasattr(h,"close"): h.close()
        logger.info("Output files finalized.")

class NodeFactory:
    @staticmethod
    def create(info: Dict) -> Node:
        title = info["title"]; nt = info["_node_type"]
        el = info.get("education_level"); cl = info.get("career_level")
        nid = deterministic_uuid(f"{nt.value}:{title}")
        return Node(node_id=nid, node_type=nt, title=title,
            description=info.get("description",f"{title} - Career Node"),
            category=info.get("category",""), education_level=el, career_level=cl,
            industry=info.get("industry",""), prerequisites=info.get("prerequisites",[]),
            skills_required=info.get("skills_required",[]), skills_gained=info.get("skills_gained",[]),
            recommended_certifications=info.get("recommended_certifications",[]),
            estimated_duration_months=info.get("duration")*12 if "duration" in info else None,
            salary_band_inr=info.get("salary",""), metadata=info.get("metadata",{}))

class EdgeBuilder:
    @staticmethod
    def connect(src: Node, dst: Node, rt: EdgeType, **kw) -> Edge:
        return Edge(source_id=src.node_id, destination_id=dst.node_id, relationship_type=rt, **kw)

class TransitionValidator:
    EDUCATION_TO_ROLE = {
        "MBBS": ["Medical Officer", "General Physician", "Specialist Doctor", "Surgeon"],
        "BDS": ["Dentist", "Oral Surgeon"],
        "B.Tech Computer Science": ["Software Engineer", "Data Analyst", "ML Engineer"],
        "B.Tech CSE AI/ML": ["ML Engineer", "AI Engineer"],
        "B.Tech CSE Data Science": ["Data Scientist", "Data Analyst"],
        "B.Tech Cyber Security": ["Cyber Security Analyst"],
        "B.Tech Electronics & Comm": ["Electronics Engineer", "Embedded Systems Engineer"],
        "B.Tech Electrical": ["Electrical Engineer"],
        "B.Tech Mechanical": ["Mechanical Engineer", "Design Engineer (Mech)"],
        "B.Tech Civil": ["Civil Engineer", "Site Engineer"],
        "B.Tech Automobile": ["Automobile Engineer"],
        "B.Tech Aerospace": ["Aerospace Engineer"],
        "B.Tech Chemical": ["Chemical Engineer"],
        "B.Tech Biotechnology": ["Biotechnologist"],
        "B.Tech Production": ["Production Engineer"],
        "B.Tech Industrial": ["Industrial Engineer"],
        "B.Tech Textile": ["Textile Engineer"],
        "B.Tech Food Technology": ["Food Technologist"],
        "B.Tech Mining": ["Mining Engineer"],
        "B.Tech Petroleum": ["Petroleum Engineer"],
        "B.Tech Marine": ["Marine Engineer"],
        "B.Pharma": ["Pharmacist", "Drug Inspector"],
        "B.Sc Computer Science": ["Software Engineer", "System Administrator"],
        "B.Sc IT": ["IT Support Engineer"],
        "B.Sc Data Science": ["Data Analyst", "Data Scientist"],
        "B.Sc Mathematics": ["Data Analyst", "Actuary"],
        "B.Sc Physics": ["Research Assistant", "Data Analyst"],
        "B.Sc Chemistry": ["Lab Technician", "Chemist"],
        "B.Sc Biotechnology": ["Lab Technician", "Research Assistant"],
        "B.Sc Nursing": ["Staff Nurse", "Nursing Supervisor"],
        "B.Sc Agriculture": ["Agriculture Officer"],
        "B.Com": ["Accountant", "Financial Analyst"],
        "BBA": ["Business Analyst", "Marketing Executive"],
        "BCA": ["Junior Software Engineer", "System Administrator"],
        "BA Economics": ["Economist", "Data Analyst"],
        "BA Political Science": ["Policy Analyst"],
        "BA Psychology": ["Counselor", "HR Executive"],
        "BA Journalism": ["Journalist", "Content Writer"],
        "BA Mass Comm": ["PR Executive", "Journalist"],
        "BBA LLB": ["Lawyer", "Legal Advisor"],
        "B.Com LLB": ["Lawyer"],
        "B.Sc LLB": ["Lawyer"],
        "LLB (3-year)": ["Lawyer", "Legal Advisor"],
        "B.Arch": ["Architect"],
        "BHMS": ["Homeopathic Doctor"],
        "BAMS": ["Ayurvedic Doctor"],
    }
    @staticmethod
    def is_valid_transition(st: NodeType, dt: NodeType, stitle: str, dtitle: str) -> bool:
        if st == NodeType.EDUCATION and dt == NodeType.JOB_ROLE:
            allowed = TransitionValidator.EDUCATION_TO_ROLE.get(stitle, [])
            return dtitle in allowed if allowed else True
        if st == NodeType.JOB_ROLE and dt == NodeType.JOB_ROLE:
            for chain in CareerPathGenerator.PROGRESSION_CHAINS.values():
                if stitle in chain and dtitle in chain: return True
            laterals = CareerPathGenerator.JOB_LATERAL.get(stitle, [])
            if dtitle in laterals: return True
            return True
        return True
'''

    parts = [prefix]
    part_files = [
        "taxonomies_part.py",
        "jobroles_part.py",
        "rest_taxonomies.py",
        "generator_logic.py",
    ]

    out_path = os.path.join(d, "career_generator_v3.py")
    total_size = 0
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(prefix)
        total_size += len(prefix)
        for pf in part_files:
            pf_path = os.path.join(d, pf)
            if os.path.exists(pf_path):
                with open(pf_path, "r", encoding="utf-8") as f:
                    content = f.read()
                out.write("\n")
                out.write(content)
                total_size += len(content) + 1
                print(f"Added {pf}: {len(content)} bytes")
            else:
                print(f"WARNING: {pf} not found!")

    print(f"\nTotal file size: {total_size} bytes")
    print(f"Written to: {out_path}")

if __name__ == "__main__":
    print("Assembling career_generator_v3.py...")
