#!/usr/bin/env python3
"""Helper: generates career_generator_v3.py"""
import os

d = r'C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project'

prefix = r'''#!/usr/bin/env python3
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
'''

print("Prefix length:", len(prefix))

# Now write taxonomies separately
edu = '''
class Taxonomies:
    SCHOOL_STREAMS = OrderedDict([
        ("10th", {"level": EducationLevel.SCHOOL, "next": ["11th Science","11th Commerce","11th Arts","Vocational Course"]}),
        ("11th Science", {"level": EducationLevel.SCHOOL, "stream": "Science"}),
        ("11th Commerce", {"level": EducationLevel.SCHOOL, "stream": "Commerce"}),
        ("11th Arts", {"level": EducationLevel.SCHOOL, "stream": "Arts"}),
        ("12th PCM", {"level": EducationLevel.SCHOOL, "stream": "Science"}),
        ("12th PCB", {"level": EducationLevel.SCHOOL, "stream": "Science"}),
        ("12th Commerce", {"level": EducationLevel.SCHOOL, "stream": "Commerce"}),
        ("12th Arts", {"level": EducationLevel.SCHOOL, "stream": "Arts"}),
    ])
    ITI_TRADES = OrderedDict([
        ("ITI Electrician", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Electrical"}),
        ("ITI Fitter", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Mechanical"}),
        ("ITI Welder", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Fabrication"}),
        ("ITI Plumber", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Plumbing"}),
        ("ITI Carpenter", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Woodwork"}),
        ("ITI Painter", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Painting"}),
        ("ITI Machinist", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Machining"}),
        ("ITI Turner", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Turning"}),
        ("ITI COPA", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Computer"}),
        ("ITI Electronics", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Electronics"}),
        ("ITI Refrigeration", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Refrigeration"}),
        ("ITI Diesel Mechanic", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Automobile"}),
        ("ITI Motor Mechanic", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Automobile"}),
        ("ITI Solar Technician", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Renewable"}),
        ("ITI CNC Operator", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Manufacturing"}),
        ("ITI Agriculture Machinery", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Agri"}),
        ("ITI Wireman", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Electrical"}),
        ("ITI Surveyor", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Civil"}),
        ("ITI Draftsman Civil", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Civil"}),
        ("ITI Draftsman Mechanical", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Mechanical"}),
        ("ITI Horticulture", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Agriculture"}),
        ("ITI Food Processing", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Food"}),
        ("ITI Textile", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Textile"}),
        ("ITI Foundry", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Foundry"}),
        ("ITI Leather Goods", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Leather"}),
    ])
    DIPLOMAS = OrderedDict([
        ("Diploma in Computer Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "CS"}),
        ("Diploma in Mechanical Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Mechanical"}),
        ("Diploma in Civil Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Civil"}),
        ("Diploma in Electrical Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Electrical"}),
        ("Diploma in Electronics & Comm", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "EC"}),
        ("Diploma in Chemical Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Chemical"}),
        ("Diploma in Automobile Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Automobile"}),
        ("Diploma in IT", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "IT"}),
        ("Diploma in Mining Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Mining"}),
        ("Diploma in Petroleum Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Petroleum"}),
        ("Diploma in Food Technology", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Food"}),
        ("Diploma in Aeronautical Engg", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Aero"}),
        ("Diploma in Marine Engineering", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Marine"}),
        ("Diploma in Hotel Management", {"level": EducationLevel.DIPLOMA, "duration": 3, "field": "Hospitality"}),
        ("Diploma in Fashion Design", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Fashion"}),
        ("Diploma in Interior Design", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Design"}),
        ("Diploma in Pharmacy", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Pharmacy"}),
        ("Diploma in Medical Lab Tech", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Healthcare"}),
        ("Diploma in Radiology", {"level": EducationLevel.DIPLOMA, "duration": 2, "field": "Healthcare"}),
        ("Diploma in Event Management", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Mgmt"}),
        ("Diploma in Journalism", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Media"}),
        ("Diploma in Film Making", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Media"}),
        ("Diploma in Graphic Design", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Design"}),
        ("Diploma in Fire & Safety", {"level": EducationLevel.DIPLOMA, "duration": 1, "field": "Safety"}),
    ])
    UNDERGRAD_DEGREES = OrderedDict([
        ("B.Tech Computer Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech CSE AI/ML", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech CSE Data Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Cyber Security", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Electronics & Comm", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Electrical", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Mechanical", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Civil", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Automobile", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Aerospace", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Chemical", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Biotechnology", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Instrumentation", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Production", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Industrial", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Textile", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Energy", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Nanotechnology", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Mechatronics", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Metallurgical", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Mining", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Petroleum", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Marine", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Ceramic", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Tech Food Technology", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"}),
        ("B.Pharma", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Pharmacy"}),
        ("B.Sc Computer Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc IT", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Data Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Mathematics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Physics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Chemistry", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Biology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Biotechnology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Microbiology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Environmental Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Statistics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Actuarial Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Aviation", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Nautical Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Nursing", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Healthcare"}),
        ("B.Sc Agriculture", {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Agriculture"}),
        ("B.Sc Forensic Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"}),
        ("B.Sc Nutrition", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Healthcare"}),
        ("B.Sc Visual Comm", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Media"}),
        ("B.Sc Fashion Technology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Fashion"}),
        ("B.Com", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("B.Com (Hons)", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("B.Com Banking & Insurance", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("B.Com Financial Markets", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("B.Com Taxation", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("B.Com International Business", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"}),
        ("BBA", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Business Analytics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Digital Marketing", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Logistics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Healthcare Mgmt", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Entrepreneurship", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Retail Mgmt", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BBA Finance", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Mgmt"}),
        ("BCA", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "CompApp"}),
        ("BCA Cloud Computing", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "CompApp"}),
        ("BCA Cyber Security", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "CompApp"}),
        ("BCA Data Analytics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "CompApp"}),
        ("BCA AI", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "CompApp"}),
        ("BA Economics", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA English", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA History", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA Political Science", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA Sociology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA Psychology", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA Public Admin", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BA Journalism", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Media"}),
        ("BA Mass Comm", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Media"}),
        ("BA Liberal Arts", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"}),
        ("BBA LLB", {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Law"}),
        ("B.Com LLB", {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Law"}),
        ("B.Sc LLB", {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Law"}),
        ("LLB (3-year)", {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Law"}),
        ("MBBS", {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Medicine"}),
        ("BDS", {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Dental"}),
        ("BAMS", {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Ayurveda"}),
        ("BHMS", {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Homeopathy"}),
        ("B.Arch", {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Architecture"}),
    ])
    POSTGRAD_DEGREES = OrderedDict([
        ("M.Tech CSE", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Data Science", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech AI/ML", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Cyber Security", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech VLSI", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Structural", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Thermal", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Automotive", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Biomedical", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Renewable Energy", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Industrial IoT", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Tech Robotics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Engineering"}),
        ("M.Sc Data Science", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Computer Science", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Physics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Chemistry", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Mathematics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Biotechnology", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Microbiology", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Environmental Science", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Astrophysics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Bioinformatics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Food Technology", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Nanoscience", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Forensic Science", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Science"}),
        ("M.Sc Agriculture", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Agriculture"}),
        ("M.Sc Nursing", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Healthcare"}),
        ("MCA", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "CompApp"}),
        ("MBA", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Finance", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Marketing", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA HR", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Operations", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Business Analytics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Healthcare", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Rural Mgmt", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Agribusiness", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Hospitality", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Sports Mgmt", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Digital Transformation", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("MBA Supply Chain", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Mgmt"}),
        ("M.Com", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Commerce"}),
        ("MA Economics", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("MA English", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("MA Sociology", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("MA Psychology", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("MA Public Admin", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("MA Journalism", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Media"}),
        ("MA Mass Comm", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Media"}),
        ("MA Social Work", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Arts"}),
        ("LLM", {"level": EducationLevel.POSTGRADUATE, "duration": 1, "field": "Law"}),
        ("MD Medicine", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MD Pediatrics", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MD Gynecology", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MD Radiology", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MD Anesthesia", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MD Dermatology", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MS General Surgery", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MS Orthopedics", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MS Ophthalmology", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("MS ENT", {"level": EducationLevel.POSTGRADUATE, "duration": 3, "field": "Medicine"}),
        ("M.Pharma", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Pharmacy"}),
        ("M.Arch", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Architecture"}),
        ("M.Plan", {"level": EducationLevel.POSTGRADUATE, "duration": 2, "field": "Planning"}),
        ("M.Lib.Sc", {"level": EducationLevel.POSTGRADUATE, "duration": 1, "field": "Library"}),
    ])
    DOCTORATES = OrderedDict([
        ("PhD Computer Science", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Engineering"}),
        ("PhD Physics", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Science"}),
        ("PhD Chemistry", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Science"}),
        ("PhD Mathematics", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Science"}),
        ("PhD Economics", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Arts"}),
        ("PhD Management", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Mgmt"}),
        ("PhD Biotechnology", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Science"}),
        ("PhD Mechanical", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Engineering"}),
        ("PhD Electrical", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Engineering"}),
        ("PhD Medicine", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Medicine"}),
        ("PhD Law", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Law"}),
        ("PhD Psychology", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Arts"}),
        ("PhD Agriculture", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Agriculture"}),
        ("PhD Pharmacy", {"level": EducationLevel.DOCTORATE, "duration": 5, "field": "Pharmacy"}),
    ])
    EXAMS = OrderedDict([
        ("JEE Main", {"exam_type": "engineering_entrance"}),
        ("JEE Advanced", {"exam_type": "engineering_entrance"}),
        ("BITSAT", {"exam_type": "engineering_entrance"}),
        ("VITEEE", {"exam_type": "engineering_entrance"}),
        ("SRMJEEE", {"exam_type": "engineering_entrance"}),
        ("COMEDK", {"exam_type": "engineering_entrance"}),
        ("MHT CET", {"exam_type": "state_engg"}),
        ("KCET", {"exam_type": "state_engg"}),
        ("AP EAMCET", {"exam_type": "state_engg"}),
        ("TS EAMCET", {"exam_type": "state_engg"}),
        ("GUJCET", {"exam_type": "state_engg"}),
        ("OJEE", {"exam_type": "state_engg"}),
        ("BCECE", {"exam_type": "state_engg"}),
        ("WBJEE", {"exam_type": "state_engg"}),
        ("CUET", {"exam_type": "university_entrance"}),
        ("MET", {"exam_type": "university_entrance"}),
        ("NPAT", {"exam_type": "university_entrance"}),
        ("SET", {"exam_type": "university_entrance"}),
        ("MUCMET", {"exam_type": "university_entrance"}),
        ("NEET", {"exam_type": "medical_entrance"}),
        ("NEET PG", {"exam_type": "medical_postgrad"}),
        ("AIIMS", {"exam_type": "medical_entrance"}),
        ("JIPMER", {"exam_type": "medical_entrance"}),
        ("MCAT", {"exam_type": "international_medical"}),
        ("USMLE", {"exam_type": "international_medical"}),
        ("PLAB", {"exam_type": "international_medical"}),
        ("CAT", {"exam_type": "management_entrance"}),
        ("XAT", {"exam_type": "management_entrance"}),
        ("SNAP", {"exam_type": "management_entrance"}),
        ("NMAT", {"exam_type": "management_entrance"}),
        ("IIFT", {"exam_type": "management_entrance"}),
        ("CMAT", {"exam_type": "management_entrance"}),
        ("MAT", {"exam_type": "management_entrance"}),
        ("GMAT", {"exam_type": "international_mba"}),
        ("GATE", {"exam_type": "engineering_postgrad"}),
        ("UPSC CSE", {"exam_type": "civil_services"}),
        ("UPSC CAPF", {"exam_type": "civil_services"}),
        ("UPSC EPFO", {"exam_type": "civil_services"}),
        ("State PSC", {"exam_type": "state_civil_services"}),
        ("SSC CGL", {"exam_type": "staff_selection"}),
        ("SSC JE", {"exam_type": "staff_selection"}),
        ("SSC CHSL", {"exam_type": "staff_selection"}),
        ("IBPS PO", {"exam_type": "banking"}),
        ("IBPS Clerk", {"exam_type": "banking"}),
        ("IBPS SO", {"exam_type": "banking"}),
        ("SBI PO", {"exam_type": "banking"}),
        ("SBI Clerk", {"exam_type": "banking"}),
        ("RBI Grade B", {"exam_type": "banking"}),
        ("RBI Assistant", {"exam_type": "banking"}),
        ("NABARD Grade A", {"exam_type": "banking"}),
        ("SEBI Grade A", {"exam_type": "finance"}),
        ("LIC AAO", {"exam_type": "insurance"}),
        ("NICL AO", {"exam_type": "insurance"}),
        ("RRB NTPC", {"exam_type": "railway"}),
        ("RRB ALP", {"exam_type": "railway"}),
        ("RRB Technician", {"exam_type": "railway"}),
        ("CLAT", {"exam_type": "law_entrance"}),
        ("AILET", {"exam_type": "law_entrance"}),
        ("LSAT", {"exam_type": "law_entrance"}),
        ("CA Foundation", {"exam_type": "ca_entrance"}),
        ("CS Foundation", {"exam_type": "cs_entrance"}),
        ("CMA Foundation", {"exam_type": "cma_entrance"}),
        ("NIFT", {"exam_type": "design_entrance"}),
        ("NID DAT", {"exam_type": "design_entrance"}),
        ("CEED", {"exam_type": "design_postgrad"}),
        ("UGC NET", {"exam_type": "academic"}),
        ("GRE", {"exam_type": "international_ms"}),
        ("IELTS", {"exam_type": "english_proficiency"}),
        ("TOEFL", {"exam_type": "english_proficiency"}),
        ("PTE", {"exam_type": "english_proficiency"}),
        ("OET", {"exam_type": "english_proficiency"}),
        ("NCHM JEE", {"exam_type": "hotel_entrance"}),
        ("DU JAT", {"exam_type": "university_entrance"}),
        ("FTII Entrance", {"exam_type": "film_entrance"}),
        ("SRFTI", {"exam_type": "film_entrance"}),
        ("CTET", {"exam_type": "teaching"}),
        ("DSSSB", {"exam_type": "teaching"}),
        ("KVS", {"exam_type": "teaching"}),
        ("NVS", {"exam_type": "teaching"}),
    ])
'''

print("Edu taxonomy length:", len(edu))

with open(os.path.join(d, 'taxonomies_part.py'), 'w', encoding='utf-8') as f:
    f.write(edu)

print("Taxonomies written")
