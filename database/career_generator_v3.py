#!/usr/bin/env python3
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
        rs = list(random.getstate())
        if len(rs) >= 2 and isinstance(rs[1], tuple):
            rs[1] = list(rs[1])
        self.state.update({"generated_nodes_count": nc,"generated_edges_count": ec,"path_counter": pc,"random_state": rs})
        if not tracker._is_bloom: self.state["dedup_signatures"] = list(getattr(tracker, "_set", set()))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path,"w") as f: json.dump(self.state, f, default=str, indent=2)
    def load(self, tracker: DeduplicationTracker) -> Tuple[int, int, int]:
        if self.path.exists():
            with open(self.path) as f: self.state = json.load(f)
            rs_raw = self.state["random_state"]
            rs_list = list(rs_raw)
            if len(rs_list) >= 2 and isinstance(rs_list[1], list):
                rs_list[1] = tuple(rs_list[1])
            random.setstate(tuple(rs_list))
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


    JOB_ROLES = OrderedDict([
        # === IT / Software Engineering ===
        ("Junior Software Engineer", {"level": CareerLevel.JUNIOR, "domain": "IT", "salary": "3-6 LPA"}),
        ("Software Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-15 LPA"}),
        ("Senior Software Engineer", {"level": CareerLevel.SENIOR, "domain": "IT", "salary": "15-30 LPA"}),
        ("Tech Lead", {"level": CareerLevel.LEAD, "domain": "IT", "salary": "25-45 LPA"}),
        ("Engineering Manager", {"level": CareerLevel.MANAGER, "domain": "IT", "salary": "35-60 LPA"}),
        ("Director of Engineering", {"level": CareerLevel.DIRECTOR, "domain": "IT", "salary": "60-90 LPA"}),
        ("VP Engineering", {"level": CareerLevel.VP, "domain": "IT", "salary": "90 LPA-1.5 Cr"}),
        ("CTO", {"level": CareerLevel.CXO, "domain": "IT", "salary": "1.5 Cr+"}),
        ("Frontend Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-14 LPA"}),
        ("Backend Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "7-18 LPA"}),
        ("Full Stack Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "8-20 LPA"}),
        ("Mobile App Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "7-16 LPA"}),
        ("Blockchain Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "10-30 LPA"}),
        ("DevOps Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "10-25 LPA"}),
        ("Site Reliability Engineer", {"level": CareerLevel.SENIOR, "domain": "IT", "salary": "15-35 LPA"}),
        ("Cloud Architect", {"level": CareerLevel.LEAD, "domain": "IT", "salary": "30-60 LPA"}),
        ("System Administrator", {"level": CareerLevel.ENTRY, "domain": "IT", "salary": "3-7 LPA"}),
        ("Network Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "4-10 LPA"}),
        ("Security Analyst", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-15 LPA"}),
        ("QA Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "4-10 LPA"}),
        ("Test Automation Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-14 LPA"}),
        ("Release Manager", {"level": CareerLevel.SENIOR, "domain": "IT", "salary": "15-30 LPA"}),
        ("Scrum Master", {"level": CareerLevel.MID, "domain": "IT", "salary": "12-25 LPA"}),
        ("Technical Writer", {"level": CareerLevel.ENTRY, "domain": "IT", "salary": "3-8 LPA"}),
        ("IT Support Engineer", {"level": CareerLevel.ENTRY, "domain": "IT", "salary": "2-5 LPA"}),
        ("IT Manager", {"level": CareerLevel.MANAGER, "domain": "IT", "salary": "15-30 LPA"}),
        ("Database Administrator", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-15 LPA"}),
        ("Game Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "5-18 LPA"}),
        ("AR/VR Developer", {"level": CareerLevel.MID, "domain": "IT", "salary": "8-20 LPA"}),
        ("IoT Engineer", {"level": CareerLevel.MID, "domain": "IT", "salary": "6-15 LPA"}),

        # === Data / AI ===
        ("Data Analyst", {"level": CareerLevel.ENTRY, "domain": "Data", "salary": "4-9 LPA"}),
        ("Data Scientist", {"level": CareerLevel.MID, "domain": "Data", "salary": "10-25 LPA"}),
        ("Senior Data Scientist", {"level": CareerLevel.SENIOR, "domain": "Data", "salary": "20-40 LPA"}),
        ("ML Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "10-28 LPA"}),
        ("MLOps Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "12-30 LPA"}),
        ("AI Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "12-30 LPA"}),
        ("AI Research Scientist", {"level": CareerLevel.SENIOR, "domain": "Data", "salary": "20-50 LPA"}),
        ("Data Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "8-20 LPA"}),
        ("Big Data Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "10-25 LPA"}),
        ("BI Analyst", {"level": CareerLevel.MID, "domain": "Data", "salary": "6-14 LPA"}),
        ("NLP Specialist", {"level": CareerLevel.MID, "domain": "Data", "salary": "12-30 LPA"}),
        ("Computer Vision Engineer", {"level": CareerLevel.MID, "domain": "Data", "salary": "12-30 LPA"}),
        ("Robotics Engineer", {"level": CareerLevel.MID, "domain": "Robotics", "salary": "8-20 LPA"}),
        ("AI Ethicist", {"level": CareerLevel.SENIOR, "domain": "Data", "salary": "15-35 LPA"}),

        # === Mechanical / Core Engineering ===
        ("Junior Engineer (Mech)", {"level": CareerLevel.ENTRY, "domain": "Mechanical", "salary": "2.5-5 LPA"}),
        ("Mechanical Engineer", {"level": CareerLevel.MID, "domain": "Mechanical", "salary": "4-10 LPA"}),
        ("Senior Mechanical Engineer", {"level": CareerLevel.SENIOR, "domain": "Mechanical", "salary": "10-20 LPA"}),
        ("Lead Mechanical Engineer", {"level": CareerLevel.LEAD, "domain": "Mechanical", "salary": "18-30 LPA"}),
        ("Mechanical Manager", {"level": CareerLevel.MANAGER, "domain": "Mechanical", "salary": "20-35 LPA"}),
        ("Chief Engineer", {"level": CareerLevel.DIRECTOR, "domain": "Mechanical", "salary": "30-50 LPA"}),
        ("Plant Head", {"level": CareerLevel.VP, "domain": "Mechanical", "salary": "40-70 LPA"}),
        ("Design Engineer (Mech)", {"level": CareerLevel.MID, "domain": "Mechanical", "salary": "4-9 LPA"}),
        ("Production Engineer", {"level": CareerLevel.ENTRY, "domain": "Mechanical", "salary": "3-6 LPA"}),
        ("Quality Engineer", {"level": CareerLevel.MID, "domain": "Mechanical", "salary": "3-8 LPA"}),
        ("Maintenance Engineer", {"level": CareerLevel.MID, "domain": "Mechanical", "salary": "3-7 LPA"}),
        ("CAD/CAM Engineer", {"level": CareerLevel.MID, "domain": "Mechanical", "salary": "4-10 LPA"}),

        # === Civil / Infrastructure ===
        ("Junior Engineer (Civil)", {"level": CareerLevel.ENTRY, "domain": "Civil", "salary": "2.5-5 LPA"}),
        ("Civil Engineer", {"level": CareerLevel.MID, "domain": "Civil", "salary": "4-10 LPA"}),
        ("Senior Civil Engineer", {"level": CareerLevel.SENIOR, "domain": "Civil", "salary": "10-20 LPA"}),
        ("Site Engineer", {"level": CareerLevel.ENTRY, "domain": "Civil", "salary": "2.5-5 LPA"}),
        ("Structural Engineer", {"level": CareerLevel.MID, "domain": "Civil", "salary": "5-15 LPA"}),
        ("Project Manager (Civil)", {"level": CareerLevel.MANAGER, "domain": "Civil", "salary": "12-25 LPA"}),
        ("Urban Planner", {"level": CareerLevel.MID, "domain": "Civil", "salary": "5-12 LPA"}),

        # === Electrical / Electronics ===
        ("Electrical Engineer", {"level": CareerLevel.MID, "domain": "Electrical", "salary": "4-10 LPA"}),
        ("Electronics Engineer", {"level": CareerLevel.MID, "domain": "Electronics", "salary": "4-10 LPA"}),
        ("Embedded Systems Engineer", {"level": CareerLevel.MID, "domain": "Electronics", "salary": "5-15 LPA"}),
        ("VLSI Design Engineer", {"level": CareerLevel.MID, "domain": "Electronics", "salary": "8-20 LPA"}),
        ("Power Systems Engineer", {"level": CareerLevel.MID, "domain": "Electrical", "salary": "5-12 LPA"}),
        ("Instrumentation Engineer", {"level": CareerLevel.MID, "domain": "Electrical", "salary": "4-10 LPA"}),

        # === Automobile ===
        ("Automobile Engineer", {"level": CareerLevel.MID, "domain": "Automobile", "salary": "4-10 LPA"}),
        ("Senior Automobile Engineer", {"level": CareerLevel.SENIOR, "domain": "Automobile", "salary": "10-18 LPA"}),

        # === Aerospace / Marine ===
        ("Aerospace Engineer", {"level": CareerLevel.MID, "domain": "Aerospace", "salary": "6-15 LPA"}),
        ("Marine Engineer", {"level": CareerLevel.MID, "domain": "Marine", "salary": "6-12 LPA"}),

        # === Chemical / Pharma / Biotech ===
        ("Chemical Engineer", {"level": CareerLevel.MID, "domain": "Chemical", "salary": "4-10 LPA"}),
        ("Petroleum Engineer", {"level": CareerLevel.MID, "domain": "Petroleum", "salary": "8-25 LPA"}),
        ("Mining Engineer", {"level": CareerLevel.MID, "domain": "Mining", "salary": "5-15 LPA"}),
        ("Biotechnologist", {"level": CareerLevel.MID, "domain": "Biotech", "salary": "4-10 LPA"}),
        ("Food Technologist", {"level": CareerLevel.MID, "domain": "Food", "salary": "3-8 LPA"}),

        # === Medicine / Healthcare ===
        ("Medical Officer", {"level": CareerLevel.ENTRY, "domain": "Healthcare", "salary": "8-15 LPA"}),
        ("General Physician", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "12-25 LPA"}),
        ("Specialist Doctor", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "20-50 LPA"}),
        ("Surgeon", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "25-60 LPA"}),
        ("Cardiologist", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "30-80 LPA"}),
        ("Pediatrician", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "12-25 LPA"}),
        ("Dermatologist", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "20-50 LPA"}),
        ("Orthopedic Surgeon", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "30-70 LPA"}),
        ("Gynecologist", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "20-50 LPA"}),
        ("Ophthalmologist", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "12-30 LPA"}),
        ("Anesthesiologist", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "20-50 LPA"}),
        ("Radiologist", {"level": CareerLevel.SENIOR, "domain": "Healthcare", "salary": "20-45 LPA"}),
        ("Pathologist", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "10-25 LPA"}),
        ("Dentist", {"level": CareerLevel.ENTRY, "domain": "Dental", "salary": "3-8 LPA"}),
        ("Oral Surgeon", {"level": CareerLevel.SENIOR, "domain": "Dental", "salary": "10-25 LPA"}),
        ("Pharmacist", {"level": CareerLevel.ENTRY, "domain": "Pharmacy", "salary": "2-5 LPA"}),
        ("Drug Inspector", {"level": CareerLevel.MID, "domain": "Pharmacy", "salary": "5-12 LPA"}),
        ("Staff Nurse", {"level": CareerLevel.ENTRY, "domain": "Healthcare", "salary": "2-5 LPA"}),
        ("Nursing Supervisor", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "4-8 LPA"}),
        ("Ayurvedic Doctor", {"level": CareerLevel.ENTRY, "domain": "Ayurveda", "salary": "3-8 LPA"}),
        ("Homeopathic Doctor", {"level": CareerLevel.ENTRY, "domain": "Homeopathy", "salary": "3-7 LPA"}),
        ("Physiotherapist", {"level": CareerLevel.ENTRY, "domain": "Healthcare", "salary": "3-7 LPA"}),

        # === Banking / Finance / Insurance ===
        ("Probationary Officer", {"level": CareerLevel.ENTRY, "domain": "Banking", "salary": "5-10 LPA"}),
        ("Bank Manager", {"level": CareerLevel.MID, "domain": "Banking", "salary": "10-20 LPA"}),
        ("Branch Manager", {"level": CareerLevel.MANAGER, "domain": "Banking", "salary": "12-25 LPA"}),
        ("Relationship Manager", {"level": CareerLevel.MID, "domain": "Banking", "salary": "5-12 LPA"}),
        ("Credit Analyst", {"level": CareerLevel.MID, "domain": "Finance", "salary": "6-15 LPA"}),
        ("Financial Analyst", {"level": CareerLevel.MID, "domain": "Finance", "salary": "5-14 LPA"}),
        ("Equity Research Analyst", {"level": CareerLevel.MID, "domain": "Finance", "salary": "6-18 LPA"}),
        ("Investment Banker", {"level": CareerLevel.SENIOR, "domain": "Finance", "salary": "20-50 LPA"}),
        ("Wealth Manager", {"level": CareerLevel.MID, "domain": "Finance", "salary": "8-20 LPA"}),
        ("Treasury Manager", {"level": CareerLevel.MANAGER, "domain": "Finance", "salary": "15-30 LPA"}),
        ("Compliance Officer", {"level": CareerLevel.MID, "domain": "Finance", "salary": "6-15 LPA"}),
        ("Internal Auditor", {"level": CareerLevel.MID, "domain": "Finance", "salary": "5-12 LPA"}),
        ("Tax Consultant", {"level": CareerLevel.MID, "domain": "Finance", "salary": "5-14 LPA"}),
        ("Investment Advisor", {"level": CareerLevel.MID, "domain": "Finance", "salary": "6-18 LPA"}),
        ("Insurance Underwriter", {"level": CareerLevel.MID, "domain": "Insurance", "salary": "4-10 LPA"}),
        ("Actuary", {"level": CareerLevel.SENIOR, "domain": "Insurance", "salary": "15-40 LPA"}),
        ("Risk Manager", {"level": CareerLevel.SENIOR, "domain": "Finance", "salary": "15-35 LPA"}),

        # === Accounting / Audit ===
        ("Accountant", {"level": CareerLevel.ENTRY, "domain": "Accounting", "salary": "2-5 LPA"}),
        ("Senior Accountant", {"level": CareerLevel.MID, "domain": "Accounting", "salary": "5-10 LPA"}),
        ("Chartered Accountant", {"level": CareerLevel.SENIOR, "domain": "Accounting", "salary": "8-30 LPA"}),
        ("Company Secretary", {"level": CareerLevel.MID, "domain": "Corporate", "salary": "6-18 LPA"}),
        ("Cost Accountant", {"level": CareerLevel.MID, "domain": "Accounting", "salary": "4-10 LPA"}),

        # === Law / Legal ===
        ("Lawyer", {"level": CareerLevel.ENTRY, "domain": "Legal", "salary": "3-10 LPA"}),
        ("Legal Advisor", {"level": CareerLevel.MID, "domain": "Legal", "salary": "8-20 LPA"}),
        ("Corporate Lawyer", {"level": CareerLevel.MID, "domain": "Legal", "salary": "10-30 LPA"}),
        ("Public Prosecutor", {"level": CareerLevel.MID, "domain": "Legal", "salary": "6-15 LPA"}),
        ("Judge", {"level": CareerLevel.SENIOR, "domain": "Legal", "salary": "15-40 LPA"}),
        ("Legal Consultant", {"level": CareerLevel.MID, "domain": "Legal", "salary": "10-25 LPA"}),

        # === Management / Consulting ===
        ("Business Analyst", {"level": CareerLevel.ENTRY, "domain": "Consulting", "salary": "5-12 LPA"}),
        ("Senior Business Analyst", {"level": CareerLevel.MID, "domain": "Consulting", "salary": "10-20 LPA"}),
        ("Product Manager", {"level": CareerLevel.MID, "domain": "Product", "salary": "15-35 LPA"}),
        ("Senior Product Manager", {"level": CareerLevel.SENIOR, "domain": "Product", "salary": "30-55 LPA"}),
        ("Consultant", {"level": CareerLevel.SENIOR, "domain": "Consulting", "salary": "12-30 LPA"}),
        ("Management Consultant", {"level": CareerLevel.SENIOR, "domain": "Consulting", "salary": "15-40 LPA"}),
        ("Project Manager", {"level": CareerLevel.MANAGER, "domain": "Mgmt", "salary": "12-30 LPA"}),
        ("Program Manager", {"level": CareerLevel.SENIOR, "domain": "Mgmt", "salary": "20-40 LPA"}),
        ("Operations Manager", {"level": CareerLevel.MANAGER, "domain": "Operations", "salary": "10-25 LPA"}),

        # === Marketing / Sales ===
        ("Marketing Executive", {"level": CareerLevel.ENTRY, "domain": "Marketing", "salary": "3-6 LPA"}),
        ("Marketing Manager", {"level": CareerLevel.MANAGER, "domain": "Marketing", "salary": "10-25 LPA"}),
        ("Digital Marketing Specialist", {"level": CareerLevel.MID, "domain": "Marketing", "salary": "4-10 LPA"}),
        ("SEO Specialist", {"level": CareerLevel.ENTRY, "domain": "Marketing", "salary": "3-7 LPA"}),
        ("Brand Manager", {"level": CareerLevel.MANAGER, "domain": "Marketing", "salary": "12-28 LPA"}),
        ("Sales Executive", {"level": CareerLevel.ENTRY, "domain": "Sales", "salary": "2-5 LPA"}),
        ("Sales Manager", {"level": CareerLevel.MANAGER, "domain": "Sales", "salary": "8-20 LPA"}),
        ("Business Development Executive", {"level": CareerLevel.ENTRY, "domain": "Sales", "salary": "3-6 LPA"}),
        ("PR Executive", {"level": CareerLevel.ENTRY, "domain": "Media", "salary": "3-7 LPA"}),
        ("Social Media Manager", {"level": CareerLevel.MID, "domain": "Marketing", "salary": "4-10 LPA"}),
        ("Content Writer", {"level": CareerLevel.ENTRY, "domain": "Media", "salary": "2-6 LPA"}),
        ("Copywriter", {"level": CareerLevel.MID, "domain": "Media", "salary": "4-10 LPA"}),

        # === HR ===
        ("HR Executive", {"level": CareerLevel.ENTRY, "domain": "HR", "salary": "3-6 LPA"}),
        ("HR Manager", {"level": CareerLevel.MANAGER, "domain": "HR", "salary": "10-22 LPA"}),
        ("Talent Acquisition Specialist", {"level": CareerLevel.MID, "domain": "HR", "salary": "4-10 LPA"}),
        ("HR Business Partner", {"level": CareerLevel.MID, "domain": "HR", "salary": "8-18 LPA"}),
        ("Training & Development Manager", {"level": CareerLevel.MANAGER, "domain": "HR", "salary": "10-20 LPA"}),

        # === Supply Chain / Logistics ===
        ("Supply Chain Analyst", {"level": CareerLevel.ENTRY, "domain": "SupplyChain", "salary": "3-7 LPA"}),
        ("Supply Chain Manager", {"level": CareerLevel.MANAGER, "domain": "SupplyChain", "salary": "10-25 LPA"}),
        ("Logistics Coordinator", {"level": CareerLevel.ENTRY, "domain": "Logistics", "salary": "2.5-5 LPA"}),
        ("Logistics Manager", {"level": CareerLevel.MANAGER, "domain": "Logistics", "salary": "8-20 LPA"}),
        ("Warehouse Manager", {"level": CareerLevel.MANAGER, "domain": "Logistics", "salary": "5-12 LPA"}),
        ("Procurement Manager", {"level": CareerLevel.MANAGER, "domain": "SupplyChain", "salary": "8-18 LPA"}),

        # === Agriculture / Food ===
        ("Agriculture Officer", {"level": CareerLevel.ENTRY, "domain": "Agriculture", "salary": "3-6 LPA"}),
        ("Agricultural Scientist", {"level": CareerLevel.MID, "domain": "Agriculture", "salary": "5-15 LPA"}),
        ("Horticulturist", {"level": CareerLevel.MID, "domain": "Agriculture", "salary": "3-8 LPA"}),
        ("Food Processing Manager", {"level": CareerLevel.MANAGER, "domain": "Food", "salary": "6-15 LPA"}),

        # === Government / Civil Services ===
        ("IAS Officer", {"level": CareerLevel.MID, "domain": "Govt", "salary": "8-25 LPA"}),
        ("IPS Officer", {"level": CareerLevel.MID, "domain": "Govt", "salary": "8-25 LPA"}),
        ("IFS Officer", {"level": CareerLevel.MID, "domain": "Govt", "salary": "8-25 LPA"}),
        ("IRS Officer", {"level": CareerLevel.MID, "domain": "Govt", "salary": "8-25 LPA"}),
        ("SDM", {"level": CareerLevel.MID, "domain": "Govt", "salary": "8-20 LPA"}),
        ("DM", {"level": CareerLevel.SENIOR, "domain": "Govt", "salary": "15-30 LPA"}),
        ("Commissioner", {"level": CareerLevel.SENIOR, "domain": "Govt", "salary": "20-40 LPA"}),
        ("Chief Secretary", {"level": CareerLevel.CXO, "domain": "Govt", "salary": "25-50 LPA"}),
        ("Section Officer", {"level": CareerLevel.ENTRY, "domain": "Govt", "salary": "5-10 LPA"}),
        ("Patwari", {"level": CareerLevel.ENTRY, "domain": "Govt", "salary": "3-6 LPA"}),
        ("Tehsildar", {"level": CareerLevel.MID, "domain": "Govt", "salary": "5-12 LPA"}),
        ("Block Development Officer", {"level": CareerLevel.MID, "domain": "Govt", "salary": "6-15 LPA"}),
        ("Police Constable", {"level": CareerLevel.ENTRY, "domain": "Police", "salary": "3-6 LPA"}),
        ("Sub-Inspector", {"level": CareerLevel.MID, "domain": "Police", "salary": "5-12 LPA"}),
        ("DSP", {"level": CareerLevel.MID, "domain": "Police", "salary": "8-18 LPA"}),
        ("SP", {"level": CareerLevel.SENIOR, "domain": "Police", "salary": "12-25 LPA"}),
        ("DIG", {"level": CareerLevel.SENIOR, "domain": "Police", "salary": "18-35 LPA"}),
        ("IG", {"level": CareerLevel.SENIOR, "domain": "Police", "salary": "22-40 LPA"}),
        ("DGP", {"level": CareerLevel.CXO, "domain": "Police", "salary": "30-50 LPA"}),

        # === PSU / Defence ===
        ("PSU Engineer", {"level": CareerLevel.MID, "domain": "PSU", "salary": "7-20 LPA"}),
        ("PSU Manager", {"level": CareerLevel.MANAGER, "domain": "PSU", "salary": "12-30 LPA"}),
        ("PSU Executive Director", {"level": CareerLevel.CXO, "domain": "PSU", "salary": "30-60 LPA"}),
        ("Army Officer", {"level": CareerLevel.MID, "domain": "Defence", "salary": "8-20 LPA"}),
        ("Navy Officer", {"level": CareerLevel.MID, "domain": "Defence", "salary": "8-20 LPA"}),
        ("Air Force Officer", {"level": CareerLevel.MID, "domain": "Defence", "salary": "8-20 LPA"}),

        # === Teaching / Academia ===
        ("School Teacher", {"level": CareerLevel.ENTRY, "domain": "Education", "salary": "2-5 LPA"}),
        ("College Lecturer", {"level": CareerLevel.ENTRY, "domain": "Education", "salary": "3-7 LPA"}),
        ("Assistant Professor", {"level": CareerLevel.MID, "domain": "Education", "salary": "5-12 LPA"}),
        ("Associate Professor", {"level": CareerLevel.SENIOR, "domain": "Education", "salary": "10-20 LPA"}),
        ("Professor", {"level": CareerLevel.SENIOR, "domain": "Education", "salary": "15-30 LPA"}),
        ("Dean", {"level": CareerLevel.CXO, "domain": "Education", "salary": "25-50 LPA"}),
        ("Research Scientist", {"level": CareerLevel.MID, "domain": "Research", "salary": "6-18 LPA"}),
        ("Research Assistant", {"level": CareerLevel.ENTRY, "domain": "Research", "salary": "3-6 LPA"}),
        ("Lab Technician", {"level": CareerLevel.ENTRY, "domain": "Healthcare", "salary": "2-4 LPA"}),
        ("Librarian", {"level": CareerLevel.ENTRY, "domain": "Education", "salary": "2-5 LPA"}),

        # === Media / Entertainment ===
        ("Journalist", {"level": CareerLevel.ENTRY, "domain": "Media", "salary": "3-8 LPA"}),
        ("Senior Journalist", {"level": CareerLevel.MID, "domain": "Media", "salary": "8-18 LPA"}),
        ("Editor", {"level": CareerLevel.SENIOR, "domain": "Media", "salary": "10-25 LPA"}),
        ("Photojournalist", {"level": CareerLevel.MID, "domain": "Media", "salary": "4-10 LPA"}),
        ("Film Director", {"level": CareerLevel.SENIOR, "domain": "Media", "salary": "10-50 LPA"}),
        ("Video Editor", {"level": CareerLevel.ENTRY, "domain": "Media", "salary": "3-8 LPA"}),
        ("Animator", {"level": CareerLevel.MID, "domain": "Media", "salary": "4-12 LPA"}),
        ("VFX Artist", {"level": CareerLevel.MID, "domain": "Media", "salary": "5-15 LPA"}),
        ("Radio Jockey", {"level": CareerLevel.ENTRY, "domain": "Media", "salary": "3-8 LPA"}),

        # === Design / Creative ===
        ("Graphic Designer", {"level": CareerLevel.ENTRY, "domain": "Design", "salary": "2-6 LPA"}),
        ("Senior Graphic Designer", {"level": CareerLevel.MID, "domain": "Design", "salary": "5-12 LPA"}),
        ("UI/UX Designer", {"level": CareerLevel.MID, "domain": "Design", "salary": "5-15 LPA"}),
        ("UX Researcher", {"level": CareerLevel.MID, "domain": "Design", "salary": "6-14 LPA"}),
        ("Fashion Designer", {"level": CareerLevel.MID, "domain": "Fashion", "salary": "4-12 LPA"}),
        ("Interior Designer", {"level": CareerLevel.MID, "domain": "Design", "salary": "4-12 LPA"}),
        ("Architect", {"level": CareerLevel.MID, "domain": "Architecture", "salary": "4-12 LPA"}),

        # === Hospitality / Tourism ===
        ("Hotel Manager", {"level": CareerLevel.MANAGER, "domain": "Hospitality", "salary": "6-18 LPA"}),
        ("Chef", {"level": CareerLevel.MID, "domain": "Hospitality", "salary": "4-15 LPA"}),
        ("Travel Agent", {"level": CareerLevel.ENTRY, "domain": "Tourism", "salary": "2-5 LPA"}),
        ("Tour Guide", {"level": CareerLevel.ENTRY, "domain": "Tourism", "salary": "2-4 LPA"}),
        ("Event Manager", {"level": CareerLevel.MID, "domain": "Events", "salary": "4-12 LPA"}),

        # === Sports / Fitness ===
        ("Sports Coach", {"level": CareerLevel.MID, "domain": "Sports", "salary": "4-15 LPA"}),
        ("Sports Analyst", {"level": CareerLevel.MID, "domain": "Sports", "salary": "5-15 LPA"}),
        ("Fitness Trainer", {"level": CareerLevel.ENTRY, "domain": "Fitness", "salary": "2-6 LPA"}),
        ("Yoga Instructor", {"level": CareerLevel.ENTRY, "domain": "Wellness", "salary": "2-6 LPA"}),
        ("Nutritionist", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "3-8 LPA"}),

        # === Social Work / NGO ===
        ("Social Worker", {"level": CareerLevel.ENTRY, "domain": "NGO", "salary": "2-5 LPA"}),
        ("NGO Manager", {"level": CareerLevel.MANAGER, "domain": "NGO", "salary": "5-12 LPA"}),
        ("Rural Development Officer", {"level": CareerLevel.MID, "domain": "NGO", "salary": "4-8 LPA"}),

        # === Entrepreneurship / Freelance ===
        ("Entrepreneur", {"level": CareerLevel.FOUNDER, "domain": "Startup", "salary": "0-1 Cr+"}),
        ("Freelancer", {"level": CareerLevel.FOUNDER, "domain": "Freelance", "salary": "3-30 LPA"}),
        ("Startup Founder", {"level": CareerLevel.FOUNDER, "domain": "Startup", "salary": "0-2 Cr+"}),

        # === E-commerce / Retail ===
        ("E-commerce Manager", {"level": CareerLevel.MANAGER, "domain": "Ecommerce", "salary": "8-20 LPA"}),
        ("Category Manager", {"level": CareerLevel.MID, "domain": "Ecommerce", "salary": "8-20 LPA"}),
        ("Retail Store Manager", {"level": CareerLevel.MANAGER, "domain": "Retail", "salary": "4-10 LPA"}),
        ("Merchandiser", {"level": CareerLevel.ENTRY, "domain": "Retail", "salary": "3-6 LPA"}),
        ("Buyer", {"level": CareerLevel.MID, "domain": "Retail", "salary": "5-12 LPA"}),

        # === Energy / Renewable ===
        ("Solar Energy Engineer", {"level": CareerLevel.MID, "domain": "Energy", "salary": "5-12 LPA"}),
        ("Wind Energy Engineer", {"level": CareerLevel.MID, "domain": "Energy", "salary": "6-14 LPA"}),
        ("Energy Auditor", {"level": CareerLevel.MID, "domain": "Energy", "salary": "4-10 LPA"}),

        # === Mining / Metallurgy ===
        ("Mining Engineer", {"level": CareerLevel.MID, "domain": "Mining", "salary": "6-15 LPA"}),
        ("Metallurgical Engineer", {"level": CareerLevel.MID, "domain": "Metallurgy", "salary": "5-12 LPA"}),

        # === ITI / Vocational ===
        ("Electrician", {"level": CareerLevel.ENTRY, "domain": "Electrical", "salary": "2-5 LPA"}),
        ("Plumber", {"level": CareerLevel.ENTRY, "domain": "Plumbing", "salary": "2-5 LPA"}),
        ("Welder", {"level": CareerLevel.ENTRY, "domain": "Fabrication", "salary": "2-4 LPA"}),
        ("Carpenter", {"level": CareerLevel.ENTRY, "domain": "Woodwork", "salary": "2-5 LPA"}),
        ("CNC Operator", {"level": CareerLevel.ENTRY, "domain": "Manufacturing", "salary": "2-4 LPA"}),
        ("Fitter", {"level": CareerLevel.ENTRY, "domain": "Mechanical", "salary": "2-5 LPA"}),
        ("HVAC Technician", {"level": CareerLevel.ENTRY, "domain": "Electrical", "salary": "2-5 LPA"}),
        ("Solar Technician", {"level": CareerLevel.ENTRY, "domain": "Energy", "salary": "2-5 LPA"}),

        # === Miscellaneous ===
        ("Pilot", {"level": CareerLevel.SENIOR, "domain": "Aviation", "salary": "15-50 LPA"}),
        ("Flight Attendant", {"level": CareerLevel.ENTRY, "domain": "Aviation", "salary": "5-12 LPA"}),
        ("Merchant Navy Officer", {"level": CareerLevel.MID, "domain": "Marine", "salary": "8-25 LPA"}),
        ("Counselor", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "3-8 LPA"}),
        ("Psychologist", {"level": CareerLevel.MID, "domain": "Healthcare", "salary": "5-15 LPA"}),
        ("Economist", {"level": CareerLevel.MID, "domain": "Finance", "salary": "6-18 LPA"}),
        ("Policy Analyst", {"level": CareerLevel.MID, "domain": "Govt", "salary": "5-15 LPA"}),
        ("Data Entry Operator", {"level": CareerLevel.ENTRY, "domain": "IT", "salary": "1.5-3 LPA"}),
        ("Receptionist", {"level": CareerLevel.ENTRY, "domain": "Admin", "salary": "1.5-3 LPA"}),
        ("Admin Manager", {"level": CareerLevel.MANAGER, "domain": "Admin", "salary": "5-12 LPA"}),
    ])


    SKILLS = OrderedDict([
        ("Python", {"type": "programming"}), ("Java", {"type": "programming"}), ("C++", {"type": "programming"}),
        ("JavaScript", {"type": "programming"}), ("TypeScript", {"type": "programming"}), ("C#", {"type": "programming"}),
        ("Ruby", {"type": "programming"}), ("Go", {"type": "programming"}), ("Rust", {"type": "programming"}),
        ("Swift", {"type": "programming"}), ("Kotlin", {"type": "programming"}), ("PHP", {"type": "programming"}),
        ("R", {"type": "programming"}), ("MATLAB", {"type": "programming"}), ("SQL", {"type": "database"}),
        ("NoSQL", {"type": "database"}), ("MongoDB", {"type": "database"}), ("PostgreSQL", {"type": "database"}),
        ("MySQL", {"type": "database"}), ("Oracle DB", {"type": "database"}), ("Redis", {"type": "database"}),
        ("AWS", {"type": "cloud"}), ("Azure", {"type": "cloud"}), ("GCP", {"type": "cloud"}),
        ("Docker", {"type": "devops"}), ("Kubernetes", {"type": "devops"}), ("Terraform", {"type": "devops"}),
        ("Ansible", {"type": "devops"}), ("Jenkins", {"type": "devops"}), ("CI/CD", {"type": "devops"}),
        ("Git", {"type": "devops"}), ("Linux", {"type": "system"}), ("Machine Learning", {"type": "ai"}),
        ("Deep Learning", {"type": "ai"}), ("NLP", {"type": "ai"}), ("Computer Vision", {"type": "ai"}),
        ("TensorFlow", {"type": "ai"}), ("PyTorch", {"type": "ai"}), ("Scikit-learn", {"type": "ai"}),
        ("Data Analysis", {"type": "data"}), ("Data Visualization", {"type": "data"}), ("Tableau", {"type": "data"}),
        ("Power BI", {"type": "data"}), ("Excel", {"type": "office"}), ("PowerPoint", {"type": "office"}),
        ("Word", {"type": "office"}), ("Communication", {"type": "soft"}), ("Leadership", {"type": "soft"}),
        ("Problem Solving", {"type": "soft"}), ("Critical Thinking", {"type": "soft"}),
        ("Teamwork", {"type": "soft"}), ("Time Management", {"type": "soft"}), ("Public Speaking", {"type": "soft"}),
        ("Negotiation", {"type": "soft"}), ("Financial Modeling", {"type": "finance"}),
        ("Financial Analysis", {"type": "finance"}), ("Investment Analysis", {"type": "finance"}),
        ("Risk Management", {"type": "finance"}), ("Tally ERP 9", {"type": "accounting"}),
        ("QuickBooks", {"type": "accounting"}), ("GST", {"type": "tax"}), ("Income Tax", {"type": "tax"}),
        ("Ind AS", {"type": "accounting"}), ("IFRS", {"type": "accounting"}), ("SAP HANA", {"type": "erp"}),
        ("SAP FICO", {"type": "erp"}), ("SAP MM", {"type": "erp"}), ("SAP SD", {"type": "erp"}),
        ("Salesforce", {"type": "crm"}), ("HubSpot", {"type": "crm"}), ("Zoho", {"type": "crm"}),
        ("Adobe Photoshop", {"type": "design"}), ("Illustrator", {"type": "design"}), ("Premiere Pro", {"type": "design"}),
        ("Figma", {"type": "design"}), ("Sketch", {"type": "design"}), ("Blender", {"type": "design"}),
        ("AutoCAD", {"type": "cad"}), ("SolidWorks", {"type": "cad"}), ("CATIA", {"type": "cad"}),
        ("ANSYS", {"type": "simulation"}), ("Unity", {"type": "gamedev"}), ("Unreal Engine", {"type": "gamedev"}),
        ("PLC", {"type": "automation"}), ("SCADA", {"type": "automation"}), ("DCS", {"type": "automation"}),
        ("Medical Coding", {"type": "healthcare"}), ("Medical Billing", {"type": "healthcare"}),
        ("HIPAA", {"type": "healthcare"}), ("GDPR", {"type": "compliance"}), ("Criminal Law", {"type": "legal"}),
        ("Civil Law", {"type": "legal"}), ("Constitutional Law", {"type": "legal"}),
        ("Contract Drafting", {"type": "legal"}), ("Moot Court", {"type": "legal"}),
        ("Client Counseling", {"type": "legal"}), ("Digital Marketing", {"type": "marketing"}),
        ("SEO", {"type": "marketing"}), ("SEM", {"type": "marketing"}), ("Social Media Marketing", {"type": "marketing"}),
        ("Content Marketing", {"type": "marketing"}), ("Email Marketing", {"type": "marketing"}),
        ("Google Analytics", {"type": "marketing"}), ("Project Management", {"type": "mgmt"}),
        ("Agile", {"type": "mgmt"}), ("Scrum", {"type": "mgmt"}), ("Six Sigma", {"type": "quality"}),
        ("Lean Manufacturing", {"type": "quality"}), ("TPM", {"type": "quality"}), ("Kaizen", {"type": "quality"}),
    ])
    CERTIFICATIONS = OrderedDict([
        ("AWS Certified Solutions Architect", {"domain": "Cloud"}),
        ("AWS Certified Developer", {"domain": "Cloud"}),
        ("AWS Certified SysOps", {"domain": "Cloud"}),
        ("AWS Machine Learning Specialty", {"domain": "AI/ML"}),
        ("Microsoft Azure Administrator", {"domain": "Cloud"}),
        ("Microsoft Azure AI Engineer", {"domain": "AI/ML"}),
        ("Google Cloud Architect", {"domain": "Cloud"}),
        ("Google Professional Data Engineer", {"domain": "Data"}),
        ("Google ML Engineer", {"domain": "AI/ML"}),
        ("Certified Kubernetes Administrator", {"domain": "DevOps"}),
        ("Docker Certified Associate", {"domain": "DevOps"}),
        ("Terraform Associate", {"domain": "DevOps"}),
        ("CISSP", {"domain": "Security"}),
        ("CISA", {"domain": "Security"}),
        ("CISM", {"domain": "Security"}),
        ("CompTIA Security+", {"domain": "Security"}),
        ("CompTIA CySA+", {"domain": "Security"}),
        ("CompTIA PenTest+", {"domain": "Security"}),
        ("CEH", {"domain": "Security"}),
        ("OSCP", {"domain": "Security"}),
        ("GIAC Certifications", {"domain": "Security"}),
        ("CRISC", {"domain": "Risk"}),
        ("COBIT", {"domain": "Governance"}),
        ("NIST Framework", {"domain": "Security"}),
        ("ISO 27001 Lead Auditor", {"domain": "Security"}),
        ("ISO 31000", {"domain": "Risk"}),
        ("PMP", {"domain": "ProjectMgmt"}),
        ("PMI-ACP", {"domain": "Agile"}),
        ("PMI-RMP", {"domain": "Risk"}),
        ("PMI-SP", {"domain": "Scheduling"}),
        ("PRINCE2", {"domain": "ProjectMgmt"}),
        ("Certified Scrum Master", {"domain": "Agile"}),
        ("SAFe Agilist", {"domain": "Agile"}),
        ("ITIL Foundation", {"domain": "ITSM"}),
        ("ITIL 4 Managing Professional", {"domain": "ITSM"}),
        ("ISTQB", {"domain": "Testing"}),
        ("Certified Selenium Tester", {"domain": "Testing"}),
        ("Oracle Certified Java Programmer", {"domain": "Programming"}),
        ("Oracle Certified Professional", {"domain": "Database"}),
        ("Cisco CCNA", {"domain": "Networking"}),
        ("Cisco CCNP", {"domain": "Networking"}),
        ("Cisco DevNet", {"domain": "Networking"}),
        ("Red Hat RHCE", {"domain": "Linux"}),
        ("Red Hat RHCSA", {"domain": "Linux"}),
        ("Salesforce Administrator", {"domain": "CRM"}),
        ("Salesforce Developer", {"domain": "CRM"}),
        ("HubSpot Certified", {"domain": "Marketing"}),
        ("Google Analytics Individual Qualification", {"domain": "Marketing"}),
        ("Google Ads Certification", {"domain": "Marketing"}),
        ("Facebook Blueprint", {"domain": "Marketing"}),
        ("Adobe Certified Expert", {"domain": "Design"}),
        ("Autodesk Certified Professional", {"domain": "CAD"}),
        ("Chartered Accountant (CA)", {"domain": "Accounting"}),
        ("Company Secretary (CS)", {"domain": "Corporate"}),
        ("Cost & Management Accountant (CMA)", {"domain": "Accounting"}),
        ("CFA", {"domain": "Finance"}),
        ("FRM", {"domain": "Risk"}),
        ("CFP", {"domain": "Finance"}),
        ("NISM Certifications", {"domain": "Finance"}),
        ("IFRS Certificate", {"domain": "Accounting"}),
        ("Certified Internal Auditor", {"domain": "Audit"}),
        ("NEBOSH", {"domain": "Safety"}),
        ("IOSH", {"domain": "Safety"}),
        ("HACCP", {"domain": "Food"}),
        ("FSSC 22000", {"domain": "Food"}),
        ("SOX Compliance", {"domain": "Compliance"}),
        ("AML Certification", {"domain": "Compliance"}),
        ("KYC Certification", {"domain": "Compliance"}),
        ("Six Sigma Green Belt", {"domain": "Quality"}),
        ("Six Sigma Black Belt", {"domain": "Quality"}),
        ("Lean Certification", {"domain": "Quality"}),
        ("TPM Certification", {"domain": "Quality"}),
        ("NPTEL Certifications", {"domain": "Academics"}),
        ("Coursera Specializations", {"domain": "Academics"}),
        ("Harvard edX Certificates", {"domain": "Academics"}),
    ])
    COMPANIES = OrderedDict([
        # Indian IT Services
        ("TCS", {"type": "IT Services", "indian": True}),
        ("Infosys", {"type": "IT Services", "indian": True}),
        ("Wipro", {"type": "IT Services", "indian": True}),
        ("HCL", {"type": "IT Services", "indian": True}),
        ("Tech Mahindra", {"type": "IT Services", "indian": True}),
        ("LTI Mindtree", {"type": "IT Services", "indian": True}),
        ("Mphasis", {"type": "IT Services", "indian": True}),
        ("Hexaware", {"type": "IT Services", "indian": True}),
        ("Persistent Systems", {"type": "IT Services", "indian": True}),
        ("Cognizant", {"type": "IT Services", "indian": True}),
        # MNC Tech
        ("Google India", {"type": "Product", "indian": False}),
        ("Microsoft India", {"type": "Product", "indian": False}),
        ("Amazon India", {"type": "Ecommerce", "indian": False}),
        ("Meta India", {"type": "Product", "indian": False}),
        ("Apple India", {"type": "Product", "indian": False}),
        ("Netflix India", {"type": "Media", "indian": False}),
        ("Uber India", {"type": "Product", "indian": False}),
        ("Adobe India", {"type": "Product", "indian": False}),
        ("Oracle India", {"type": "Product", "indian": False}),
        ("IBM India", {"type": "IT Services", "indian": False}),
        ("SAP India", {"type": "Product", "indian": False}),
        ("Salesforce India", {"type": "Product", "indian": False}),
        ("VMware India", {"type": "Product", "indian": False}),
        # Indian Startups / Product
        ("Flipkart", {"type": "Ecommerce", "indian": True}),
        ("Zomato", {"type": "FoodTech", "indian": True}),
        ("Swiggy", {"type": "FoodTech", "indian": True}),
        ("Paytm", {"type": "FinTech", "indian": True}),
        ("PhonePe", {"type": "FinTech", "indian": True}),
        ("Razorpay", {"type": "FinTech", "indian": True}),
        ("CRED", {"type": "FinTech", "indian": True}),
        ("Groww", {"type": "FinTech", "indian": True}),
        ("Zerodha", {"type": "FinTech", "indian": True}),
        ("Upstox", {"type": "FinTech", "indian": True}),
        ("Ola", {"type": "Mobility", "indian": True}),
        ("Rapido", {"type": "Mobility", "indian": True}),
        ("BharatPe", {"type": "FinTech", "indian": True}),
        ("Slice", {"type": "FinTech", "indian": True}),
        ("Cars24", {"type": "Ecommerce", "indian": True}),
        ("Spinny", {"type": "Ecommerce", "indian": True}),
        ("DealShare", {"type": "Ecommerce", "indian": True}),
        ("Meesho", {"type": "Ecommerce", "indian": True}),
        ("Nykaa", {"type": "Ecommerce", "indian": True}),
        ("Byju's", {"type": "EdTech", "indian": True}),
        ("Unacademy", {"type": "EdTech", "indian": True}),
        ("UpGrad", {"type": "EdTech", "indian": True}),
        ("Vedantu", {"type": "EdTech", "indian": True}),
        ("Physics Wallah", {"type": "EdTech", "indian": True}),
        ("Ola Electric", {"type": "EV", "indian": True}),
        ("Ather Energy", {"type": "EV", "indian": True}),
        ("OYO", {"type": "Hospitality", "indian": True}),
        ("MakeMyTrip", {"type": "Travel", "indian": True}),
        ("Urban Company", {"type": "Services", "indian": True}),
        ("Dunzo", {"type": "Logistics", "indian": True}),
        ("Delhivery", {"type": "Logistics", "indian": True}),
        ("Shadowfax", {"type": "Logistics", "indian": True}),
        ("Porter", {"type": "Logistics", "indian": True}),
        ("Licious", {"type": "FoodTech", "indian": True}),
        ("BigBasket", {"type": "Ecommerce", "indian": True}),
        ("Blinkit", {"type": "QuickCommerce", "indian": True}),
        ("Zepto", {"type": "QuickCommerce", "indian": True}),
        # Indian Corporates
        ("Reliance Industries", {"type": "Conglomerate", "indian": True}),
        ("Tata Group", {"type": "Conglomerate", "indian": True}),
        ("Adani Group", {"type": "Conglomerate", "indian": True}),
        ("Tata Motors", {"type": "Automobile", "indian": True}),
        ("Mahindra & Mahindra", {"type": "Automobile", "indian": True}),
        ("Maruti Suzuki", {"type": "Automobile", "indian": True}),
        ("Bajaj Auto", {"type": "Automobile", "indian": True}),
        ("TVS Motor", {"type": "Automobile", "indian": True}),
        ("L&T", {"type": "Infrastructure", "indian": True}),
        ("Godrej Group", {"type": "Conglomerate", "indian": True}),
        ("Bajaj Group", {"type": "Conglomerate", "indian": True}),
        ("Aditya Birla Group", {"type": "Conglomerate", "indian": True}),
        ("Mahindra Group", {"type": "Conglomerate", "indian": True}),
        ("RPG Group", {"type": "Conglomerate", "indian": True}),
        ("Murugappa Group", {"type": "Conglomerate", "indian": True}),
        # PSUs
        ("ONGC", {"type": "PSU"}),
        ("Indian Oil", {"type": "PSU"}),
        ("BHEL", {"type": "PSU"}),
        ("GAIL", {"type": "PSU"}),
        ("NTPC", {"type": "PSU"}),
        ("NHPC", {"type": "PSU"}),
        ("THDC", {"type": "PSU"}),
        ("SJVN", {"type": "PSU"}),
        ("IRCTC", {"type": "PSU"}),
        ("CONCOR", {"type": "PSU"}),
        ("Coal India", {"type": "PSU"}),
        ("SAIL", {"type": "PSU"}),
        ("HAL", {"type": "PSU"}),
        ("BEL", {"type": "PSU"}),
        ("ISRO", {"type": "Space"}),
        ("DRDO", {"type": "Defence Research"}),
        # Banks / Financial
        ("SBI", {"type": "PSU Bank"}),
        ("HDFC Bank", {"type": "Private Bank"}),
        ("ICICI Bank", {"type": "Private Bank"}),
        ("Axis Bank", {"type": "Private Bank"}),
        ("Kotak Mahindra Bank", {"type": "Private Bank"}),
        ("Yes Bank", {"type": "Private Bank"}),
        ("RBI", {"type": "Central Bank"}),
        ("NABARD", {"type": "Development Bank"}),
        ("SEBI", {"type": "Regulator"}),
        ("LIC", {"type": "Insurance"}),
        ("HDFC Life", {"type": "Insurance"}),
        ("ICICI Prudential", {"type": "Insurance"}),
        # MNC Industrial
        ("Siemens India", {"type": "Industrial", "indian": False}),
        ("ABB India", {"type": "Industrial", "indian": False}),
        ("Schneider Electric India", {"type": "Industrial", "indian": False}),
        ("Honeywell India", {"type": "Industrial", "indian": False}),
        ("GE India", {"type": "Industrial", "indian": False}),
        ("Philips India", {"type": "Healthcare", "indian": False}),
        ("Bosch India", {"type": "Automotive", "indian": False}),
        ("Hitachi India", {"type": "Industrial", "indian": False}),
        ("Panasonic India", {"type": "Consumer", "indian": False}),
        ("Sony India", {"type": "Consumer", "indian": False}),
        ("Samsung India", {"type": "Consumer", "indian": False}),
        ("LG India", {"type": "Consumer", "indian": False}),
        # Pharma
        ("Sun Pharma", {"type": "Pharma", "indian": True}),
        ("Dr Reddy's Labs", {"type": "Pharma", "indian": True}),
        ("Cipla", {"type": "Pharma", "indian": True}),
        ("Lupin", {"type": "Pharma", "indian": True}),
        ("Aurobindo Pharma", {"type": "Pharma", "indian": True}),
        ("Pfizer India", {"type": "Pharma", "indian": False}),
        ("Novartis India", {"type": "Pharma", "indian": False}),
        ("GSK India", {"type": "Pharma", "indian": False}),
        ("Sanofi India", {"type": "Pharma", "indian": False}),
        ("Johnson & Johnson India", {"type": "Healthcare", "indian": False}),
        # Healthcare
        ("AIIMS", {"type": "Healthcare"}),
        ("Apollo Hospitals", {"type": "Healthcare", "indian": True}),
        ("Fortis Healthcare", {"type": "Healthcare", "indian": True}),
        ("Max Healthcare", {"type": "Healthcare", "indian": True}),
        ("Narayana Health", {"type": "Healthcare", "indian": True}),
        ("Medanta Medicity", {"type": "Healthcare", "indian": True}),
        # Education
        ("IITs", {"type": "Education"}),
        ("IIMs", {"type": "Education"}),
        ("AIIMS Delhi", {"type": "Education"}),
        ("NITs", {"type": "Education"}),
        ("IISc", {"type": "Education"}),
        ("Delhi University", {"type": "Education"}),
        ("JNU", {"type": "Education"}),
        ("BITS Pilani", {"type": "Education"}),
        ("VIT", {"type": "Education"}),
        ("SRM", {"type": "Education"}),
        ("Amity University", {"type": "Education"}),
    ])
    INDUSTRIES = [
        "Information Technology", "Software Services", "IT Services", "Product",
        "Banking", "Financial Services", "Insurance", "FinTech", "InsurTech",
        "Healthcare", "Pharmaceuticals", "Medical Devices", "HealthTech",
        "Automobile", "Auto Components", "Electric Vehicles",
        "Manufacturing", "Industrial Automation", "3D Printing", "Robotics",
        "Construction", "Infrastructure", "Real Estate", "PropTech",
        "Retail", "E-commerce", "Quick Commerce", "D2C",
        "Telecom", "Media & Entertainment", "OTT", "Gaming",
        "Education", "EdTech", "E-learning",
        "Government", "Defence", "Public Sector",
        "Agriculture", "AgriTech", "Dairy", "Poultry", "Fisheries", "Food Processing",
        "Energy", "Oil & Gas", "Renewable Energy", "Solar", "Wind", "Nuclear",
        "Aerospace", "SpaceTech", "Aviation",
        "Semiconductor", "Electronics", "Consumer Electronics",
        "Cyber Security", "Cloud Computing", "Data Analytics",
        "Artificial Intelligence", "Machine Learning", "Blockchain",
        "Chemical", "Petrochemicals", "Cement", "Steel", "Aluminum",
        "Textile", "Fashion", "Apparel",
        "Paper & Pulp", "Packaging", "Plastics", "Glass",
        "Hospitality", "Tourism", "Travel",
        "Logistics", "Supply Chain", "Warehousing",
        "Mining", "Metallurgy", "Ceramic",
        "Legal", "Law Firm", "Corporate Legal",
        "Consulting", "Management Consulting", "Strategy",
        "Marketing", "Advertising", "PR",
        "HR", "Recruitment", "Staffing",
        "NGO", "Social Impact", "Rural Development",
        "Sports", "Fitness", "Wellness",
        "Climate Tech", "Waste Management", "Water Treatment",
        "Biotechnology", "Nanotechnology",
        "Printing & Publishing",
        "Security & Surveillance",
        "Facilities Management",
        "Architecture & Design",
    ]
    LEARNING_RESOURCES = [
        "NPTEL", "Coursera", "edX", "Udemy", "Udacity", "Pluralsight",
        "LinkedIn Learning", "Khan Academy", "MIT OpenCourseWare",
        "Ekeeda", "Made Easy", "Ace Academy", "Gateforum",
        "IMS", "T.I.M.E.", "Career Launcher", "Mahesh Tutorials",
        "Allen", "Aakash Institute", "Resonance", "Vibrant Academy",
        "Chahal Academy", "Vision IAS", "Insights IAS",
        "Unacademy", "Physics Wallah", "Byju's", "Vedantu",
        "Simplilearn", "Great Learning", "UpGrad", "Jio Institute",
        "W3Schools", "MDN Web Docs", "GeeksforGeeks", "Stack Overflow",
        "YouTube Tutorials", "freeCodeCamp", "The Odin Project",
        "Codecademy", "DataCamp", "Kaggle", "Analytics Vidhya",
        "Todoist", "Coding Ninjas", "Scaler Academy",
        "Pepcoding", "Apna College", "Love Babbar",
    ]


    @classmethod
    def get_all_education_nodes(cls) -> List[Dict]:
        nodes = []
        for name, info in cls.SCHOOL_STREAMS.items():
            nodes.append({"title": name, "education_level": EducationLevel.SCHOOL, "_node_type": NodeType.EDUCATION, **info})
        for name, info in cls.ITI_TRADES.items():
            nodes.append({"title": name, "education_level": EducationLevel.DIPLOMA, "_node_type": NodeType.EDUCATION, **info})
        for name, info in cls.DIPLOMAS.items():
            nodes.append({"title": name, "education_level": EducationLevel.DIPLOMA, "_node_type": NodeType.EDUCATION, **info})
        for name, info in cls.UNDERGRAD_DEGREES.items():
            nodes.append({"title": name, "education_level": EducationLevel.UNDERGRADUATE, "_node_type": NodeType.EDUCATION, **info})
        for name, info in cls.POSTGRAD_DEGREES.items():
            nodes.append({"title": name, "education_level": EducationLevel.POSTGRADUATE, "_node_type": NodeType.EDUCATION, **info})
        for name, info in cls.DOCTORATES.items():
            nodes.append({"title": name, "education_level": EducationLevel.DOCTORATE, "_node_type": NodeType.EDUCATION, **info})
        return nodes

    @classmethod
    def get_all_exam_nodes(cls) -> List[Dict]:
        return [{"title": n, "_node_type": NodeType.EXAM} for n in cls.EXAMS]

    @classmethod
    def get_all_job_role_nodes(cls) -> List[Dict]:
        return [{"title": n, "_node_type": NodeType.JOB_ROLE, **i} for n, i in cls.JOB_ROLES.items()]

    @classmethod
    def get_all_skill_nodes(cls) -> List[Dict]:
        return [{"title": n, "_node_type": NodeType.SKILL, **i} for n, i in cls.SKILLS.items()]

    @classmethod
    def get_all_company_nodes(cls) -> List[Dict]:
        return [{"title": n, "_node_type": NodeType.COMPANY, **i} for n, i in cls.COMPANIES.items()]

    @classmethod
    def get_all_industry_nodes(cls) -> List[Dict]:
        return [{"title": i, "_node_type": NodeType.INDUSTRY} for i in cls.INDUSTRIES]

    @classmethod
    def get_all_certification_nodes(cls) -> List[Dict]:
        return [{"title": n, "_node_type": NodeType.CERTIFICATION, **i} for n, i in cls.CERTIFICATIONS.items()]


class CareerPathGenerator:
    PROGRESSION_CHAINS = {
        "IT": ["Junior Software Engineer", "Software Engineer", "Senior Software Engineer", "Tech Lead", "Engineering Manager", "Director of Engineering", "VP Engineering", "CTO"],
        "Data": ["Data Analyst", "Data Scientist", "Senior Data Scientist", "AI Research Scientist"],
        "ML": ["Data Analyst", "ML Engineer", "AI Research Scientist"],
        "Mech": ["Junior Engineer (Mech)", "Mechanical Engineer", "Senior Mechanical Engineer", "Lead Mechanical Engineer", "Mechanical Manager", "Chief Engineer", "Plant Head"],
        "Civil": ["Junior Engineer (Civil)", "Civil Engineer", "Senior Civil Engineer", "Project Manager (Civil)"],
        "Elec": ["Electrical Engineer", "Power Systems Engineer"],
        "Auto": ["Automobile Engineer", "Senior Automobile Engineer"],
        "Banking": ["Probationary Officer", "Bank Manager", "Branch Manager"],
        "Acct": ["Accountant", "Senior Accountant", "Chartered Accountant"],
        "Mktg": ["Marketing Executive", "Marketing Manager", "Brand Manager"],
        "HR": ["HR Executive", "HR Manager", "HR Business Partner"],
        "Med": ["Medical Officer", "General Physician", "Specialist Doctor"],
        "Govt": ["Section Officer", "IAS Officer", "SDM", "DM", "Commissioner", "Chief Secretary"],
        "Police": ["Police Constable", "Sub-Inspector", "DSP", "SP", "DIG", "IG", "DGP"],
        "Legal": ["Lawyer", "Corporate Lawyer", "Judge"],
        "Design": ["Graphic Designer", "Senior Graphic Designer", "UI/UX Designer"],
        "Media": ["Journalist", "Senior Journalist", "Editor"],
        "Academia": ["Assistant Professor", "Associate Professor", "Professor", "Dean"],
        "SupplyChain": ["Supply Chain Analyst", "Supply Chain Manager"],
        "Sales": ["Sales Executive", "Sales Manager"],
        "Ecom": ["E-commerce Manager", "Category Manager"],
    }

    # Which exams lead to which programs/jobs
    EXAM_TO_EDUCATION = {
        "JEE Main": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Civil", "B.Tech Electrical", "B.Tech Electronics & Comm", "B.Tech Automobile", "B.Tech Chemical", "B.Tech Aerospace"],
        "JEE Advanced": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Electrical", "B.Tech Aerospace"],
        "BITSAT": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Electrical"],
        "VITEEE": ["B.Tech Computer Science", "B.Tech Mechanical"],
        "SRMJEEE": ["B.Tech Computer Science", "B.Tech Electronics & Comm"],
        "COMEDK": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Civil"],
        "MHT CET": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Civil"],
        "KCET": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Civil"],
        "AP EAMCET": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Civil"],
        "TS EAMCET": ["B.Tech Computer Science", "B.Tech Mechanical"],
        "GUJCET": ["B.Tech Computer Science", "B.Tech Mechanical"],
        "WBJEE": ["B.Tech Computer Science", "B.Tech Mechanical", "B.Tech Electrical"],
        "CUET": ["B.Com", "BA Economics", "BA English", "BA Political Science", "BA Psychology", "B.Sc Computer Science", "B.Sc Physics", "B.Sc Mathematics"],
        "NEET": ["MBBS", "BDS", "BAMS", "BHMS"],
        "NEET PG": ["MD Medicine", "MD Pediatrics", "MD Gynecology", "MD Radiology", "MD Anesthesia", "MD Dermatology", "MS General Surgery", "MS Orthopedics", "MS Ophthalmology", "MS ENT"],
        "CAT": ["MBA", "MBA Finance", "MBA Marketing", "MBA HR", "MBA Business Analytics", "MBA Operations", "MBA Healthcare", "MBA Supply Chain"],
        "XAT": ["MBA", "MBA HR", "MBA Business Analytics"],
        "SNAP": ["MBA", "MBA Finance"],
        "NMAT": ["MBA", "MBA Marketing"],
        "CMAT": ["MBA", "MBA Finance"],
        "GATE": ["M.Tech CSE", "M.Tech Data Science", "M.Tech AI/ML", "M.Tech VLSI", "M.Tech Structural", "M.Tech Thermal", "M.Tech Automotive", "M.Tech Biomedical", "M.Tech Renewable Energy"],
        "UPSC CSE": ["IAS Officer", "IPS Officer", "IFS Officer", "IRS Officer"],
        "UPSC CAPF": ["IPS Officer", "DSP"],
        "SSC CGL": ["Section Officer", "Auditor"],
        "IBPS PO": ["Probationary Officer"],
        "SBI PO": ["Probationary Officer"],
        "RBI Grade B": ["Bank Manager"],
        "CLAT": ["BBA LLB", "B.Com LLB", "B.Sc LLB", "LLB (3-year)"],
        "AILET": ["BBA LLB", "LLB (3-year)"],
        "LSAT": ["LLB (3-year)"],
        "CA Foundation": ["Chartered Accountant"],
        "CS Foundation": ["Company Secretary"],
        "CMA Foundation": ["Cost Accountant"],
        "NIFT": ["B.Sc Fashion Technology"],
        "NID DAT": ["Diploma in Interior Design", "Diploma in Graphic Design"],
        "UGC NET": ["Assistant Professor", "Research Scientist"],
        "GRE": ["M.Tech CSE", "M.Sc Computer Science", "MS General Surgery"],
        "GMAT": ["MBA", "MBA Finance"],
        "IELTS": ["MS General Surgery", "MBA"],
        "NCHM JEE": ["Diploma in Hotel Management"],
        "CTET": ["School Teacher"],
        "DSSSB": ["School Teacher"],
    }

    # Job role -> further education or exams (upskilling transitions)
    JOB_TO_EDUCATION = {
        "Software Engineer": [("M.Tech CSE", 0.3), ("MBA", 0.2), ("GATE", 0.3), ("M.Sc Data Science", 0.2)],
        "Senior Software Engineer": [("MBA", 0.3), ("M.Tech CSE", 0.2), ("Entrepreneur", 0.15)],
        "Data Analyst": [("M.Sc Data Science", 0.4), ("MBA Business Analytics", 0.2), ("Data Scientist", 0.3)],
        "Data Scientist": [("MBA Business Analytics", 0.2), ("AI Research Scientist", 0.3)],
        "ML Engineer": [("M.Tech AI/ML", 0.3), ("AI Research Scientist", 0.3)],
        "Mechanical Engineer": [("M.Tech Thermal", 0.3), ("MBA", 0.2), ("GATE", 0.3)],
        "Civil Engineer": [("M.Tech Structural", 0.3), ("MBA", 0.2), ("GATE", 0.3)],
        "Electrical Engineer": [("M.Tech VLSI", 0.2), ("MBA", 0.2), ("GATE", 0.3)],
        "Accountant": [("CA Foundation", 0.4), ("CMA Foundation", 0.2), ("M.Com", 0.2)],
        "Chartered Accountant": [("MBA Finance", 0.3), ("CFA", 0.2)],
        "Medical Officer": [("NEET PG", 0.6), ("MD Medicine", 0.3)],
        "General Physician": [("MD Medicine", 0.4), ("MD Cardiology", 0.2)],
        "Bank Manager": [("MBA", 0.3), ("RBI Grade B", 0.2)],
        "Marketing Executive": [("MBA Marketing", 0.4)],
        "HR Executive": [("MBA HR", 0.4)],
        "Lawyer": [("LLM", 0.3), ("UPSC CSE", 0.2)],
        "Journalist": [("MA Mass Comm", 0.3)],
        "School Teacher": [("UGC NET", 0.4), ("M.Ed", 0.3)],
        "Assistant Professor": [("PhD Computer Science", 0.4), ("UGC NET", 0.3)],
        "Graphic Designer": [("NID DAT", 0.3)],
    }

    # Lateral moves between job roles
    JOB_LATERAL = {
        "Software Engineer": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer", "Data Analyst", "QA Engineer"],
        "Frontend Developer": ["Full Stack Developer", "UI/UX Designer"],
        "Backend Developer": ["Full Stack Developer", "DevOps Engineer"],
        "Full Stack Developer": ["Tech Lead", "Software Engineer"],
        "Data Analyst": ["Business Analyst", "Data Scientist", "BI Analyst"],
        "Data Scientist": ["ML Engineer", "AI Engineer", "Data Engineer"],
        "ML Engineer": ["Data Scientist", "AI Engineer", "AI Research Scientist"],
        "Mechanical Engineer": ["Design Engineer (Mech)", "Production Engineer", "Quality Engineer"],
        "Civil Engineer": ["Site Engineer", "Structural Engineer", "Project Manager (Civil)"],
        "Electrical Engineer": ["Power Systems Engineer", "Instrumentation Engineer"],
        "Accountant": ["Financial Analyst", "Tax Consultant", "Internal Auditor"],
        "Marketing Executive": ["Digital Marketing Specialist", "Content Writer", "Brand Manager"],
        "HR Executive": ["Talent Acquisition Specialist", "Training & Development Manager"],
        "Medical Officer": ["General Physician", "Public Health Officer"],
        "Bank Manager": ["Relationship Manager", "Branch Manager"],
        "Police Constable": ["Sub-Inspector"],
        "Sub-Inspector": ["DSP"],
        "Lawyer": ["Legal Advisor", "Corporate Lawyer", "Public Prosecutor"],
        "Graphic Designer": ["UI/UX Designer", "Senior Graphic Designer"],
        "Hotel Manager": ["Event Manager", "Restaurant Manager"],
        "Chef": ["Hotel Manager"],
    }


def _get_next_in_progression(title: str) -> Optional[str]:
    for chain in CareerPathGenerator.PROGRESSION_CHAINS.values():
        if title in chain:
            idx = chain.index(title)
            if idx + 1 < len(chain):
                return chain[idx + 1]
    return None


class CareerGraphGenerator:
    def __init__(self, config: GeneratorConfig, taxonomies: Taxonomies, validator: TransitionValidator):
        self.config = config
        self.taxonomies = taxonomies
        self.validator = validator
        self.node_factory = NodeFactory()
        self.edge_builder = EdgeBuilder()
        self.dedup = DeduplicationTracker(config)
        self.checkpoint_mgr = CheckpointManager(config.checkpoint_file)
        self.writer: Optional[MultiFormatWriter] = None
        self.nodes_cache: Dict[str, Node] = {}
        self._written_nodes: Set[str] = set()
        self.generated_nodes = 0
        self.generated_edges = 0
        self.path_counter = 0
        self._initialize_base_nodes()

    def _initialize_base_nodes(self):
        all_node_dicts = chain(
            self.taxonomies.get_all_education_nodes(),
            self.taxonomies.get_all_exam_nodes(),
            self.taxonomies.get_all_job_role_nodes(),
            self.taxonomies.get_all_skill_nodes(),
            self.taxonomies.get_all_company_nodes(),
            self.taxonomies.get_all_industry_nodes(),
            self.taxonomies.get_all_certification_nodes(),
        )
        for info in all_node_dicts:
            node = self.node_factory.create(info)
            if not self.dedup.exists(node.signature()):
                self.dedup.add(node.signature())
                self.nodes_cache[node.title] = node
                self.generated_nodes += 1

    def _get_or_create_node(self, title: str, node_type: NodeType, **extra) -> Node:
        if title in self.nodes_cache:
            return self.nodes_cache[title]
        node_dict = {"title": title, "_node_type": node_type, **extra}
        node = self.node_factory.create(node_dict)
        sig = node.signature()
        if not self.dedup.exists(sig):
            self.dedup.add(sig)
            self.nodes_cache[title] = node
            self.generated_nodes += 1
            if self.writer and node.node_id not in self._written_nodes:
                self.writer.write_node(node)
                self._written_nodes.add(node.node_id)
            return node
        return self.nodes_cache[title]

    def _add_edge(self, source: Node, dest: Node, rel_type: EdgeType, **kwargs) -> Optional[Edge]:
        edge = self.edge_builder.connect(source, dest, rel_type, **kwargs)
        if not self.dedup.exists(edge.signature()):
            self.dedup.add(edge.signature())
            self.generated_edges += 1
            return edge
        return None

    def generate(self) -> None:
        self.writer = MultiFormatWriter(self.config.output_dir, self.config.formats)
        start_n, start_e, start_p = self.checkpoint_mgr.load(self.dedup)
        self.generated_nodes = start_n or self.generated_nodes
        self.generated_edges = start_e or self.generated_edges
        self.path_counter = start_p
        self._write_cached_nodes()

        seed_titles = [
            "10th",
        ] + list(Taxonomies.ITI_TRADES.keys()) + [
            "Diploma in Computer Engineering", "Diploma in Mechanical Engineering",
            "Diploma in Civil Engineering", "Diploma in Electrical Engineering",
            "Diploma in Electronics & Comm", "Diploma in Chemical Engineering",
            "Diploma in Automobile Engineering", "Diploma in IT",
            "Diploma in Mining Engineering", "Diploma in Petroleum Engineering",
            "Diploma in Food Technology", "Diploma in Aeronautical Engg",
            "Diploma in Marine Engineering", "Diploma in Hotel Management",
            "Diploma in Fashion Design", "Diploma in Interior Design",
            "Diploma in Pharmacy", "Diploma in Medical Lab Tech",
            "Diploma in Radiology", "Diploma in Event Management",
            "Diploma in Journalism", "Diploma in Film Making",
            "Diploma in Graphic Design", "Diploma in Fire & Safety",
            "12th PCM", "12th PCB", "12th Commerce", "12th Arts",
        ] + list(Taxonomies.UNDERGRAD_DEGREES.keys())

        for seed_title in seed_titles:
            seed_node = self._get_or_create_node(seed_title, NodeType.EDUCATION)
            if not seed_node:
                continue
            self._expand_from_node(seed_node, depth=0, visited_path=[seed_title])
            if self.path_counter >= self.config.max_total_paths: break
            if self.generated_nodes >= self.config.max_nodes or self.generated_edges >= self.config.max_edges: break

        self.writer.finalize()
        self.checkpoint_mgr.save(self.dedup, self.generated_nodes, self.generated_edges, self.path_counter)
        logger.info(f"Generation complete. Nodes: {self.generated_nodes}, Edges: {self.generated_edges}, Paths: {self.path_counter}")

    def _write_cached_nodes(self):
        for node in self.nodes_cache.values():
            if node.node_id not in self._written_nodes:
                self.writer.write_node(node)
                self._written_nodes.add(node.node_id)

    def _expand_from_node(self, current_node: Node, depth: int, visited_path: List[str]):
        if depth > self.config.max_path_length or self.path_counter >= self.config.max_total_paths:
            return
        if self.generated_nodes >= self.config.max_nodes or self.generated_edges >= self.config.max_edges:
            return

        next_options: List[Tuple[NodeType, str, EdgeType, Dict]] = []

        if current_node.node_type == NodeType.EDUCATION:
            next_options = self._education_next_steps(current_node)
        elif current_node.node_type == NodeType.EXAM:
            next_options = self._exam_next_steps(current_node)
        elif current_node.node_type == NodeType.JOB_ROLE:
            next_options = self._job_role_next_steps(current_node)
        elif current_node.node_type == NodeType.CERTIFICATION:
            next_options = self._certification_next_steps(current_node)

        self._add_enrichment_edges(current_node)

        if not next_options:
            return

        random.shuffle(next_options)

        main = next_options[0]
        branches = next_options[1:]
        selected_branches = []
        for b in branches[:8]:  # Consider up to 8 branches
            if random.random() < self.config.branch_probability:
                selected_branches.append(b)

        self._process_transition(current_node, main, depth, visited_path)

        for branch_option in selected_branches:
            if self.path_counter >= self.config.max_total_paths: break
            self._process_transition(current_node, branch_option, depth, visited_path)

    def _process_transition(self, current_node: Node, option: Tuple, depth: int, visited_path: List[str]):
        dest_type, dest_title, edge_type, edge_kwargs = option
        if dest_title in visited_path[-4:]:
            return
        dest_node = self._get_or_create_node(dest_title, dest_type)
        if not self.validator.is_valid_transition(current_node.node_type, dest_type, current_node.title, dest_title):
            return

        edge = self._add_edge(current_node, dest_node, edge_type, **edge_kwargs)
        if edge and self.writer:
            self.writer.write_edge(edge)

        new_path = visited_path + [dest_title]

        # Count as a path whenever we reach a job role or certification
        if dest_type == NodeType.JOB_ROLE:
            self.path_counter += 1
            path_str = " \u2192 ".join(new_path)
            if self.writer:
                self.writer.write_path_text(f"Path #{self.path_counter}: {path_str}")
            if self.path_counter % self.config.log_interval == 0:
                logger.info(f"Generated {self.path_counter} paths, {self.generated_nodes}N, {self.generated_edges}E")
                self.checkpoint_mgr.save(self.dedup, self.generated_nodes, self.generated_edges, self.path_counter)
            # Don't return - continue to progress further in career
        elif dest_type == NodeType.CERTIFICATION or depth >= self.config.max_path_length - 1:
            self.path_counter += 1
            path_str = " \u2192 ".join(new_path)
            if self.writer:
                self.writer.write_path_text(f"Path #{self.path_counter}: {path_str}")

        self._expand_from_node(dest_node, depth + 1, new_path)

    def _education_next_steps(self, edu_node: Node) -> List[Tuple]:
        options = []
        title = edu_node.title
        if title == "10th":
            for s in ["11th Science", "11th Commerce", "11th Arts"]:
                options.append((NodeType.EDUCATION, s, EdgeType.NEXT_STEP, {}))
            for iti in list(Taxonomies.ITI_TRADES.keys())[:8]:
                options.append((NodeType.EDUCATION, iti, EdgeType.BRANCH, {}))
            for dip in ["Diploma in Computer Engineering", "Diploma in Mechanical Engineering", "Diploma in Civil Engineering", "Diploma in Electrical Engineering"]:
                options.append((NodeType.EDUCATION, dip, EdgeType.BRANCH, {}))
        elif title.startswith("11th"):
            if "Science" in title:
                options.append((NodeType.EDUCATION, "12th PCM", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "12th PCB", EdgeType.BRANCH, {}))
            elif "Commerce" in title:
                options.append((NodeType.EDUCATION, "12th Commerce", EdgeType.NEXT_STEP, {}))
            elif "Arts" in title:
                options.append((NodeType.EDUCATION, "12th Arts", EdgeType.NEXT_STEP, {}))
        elif title == "12th PCM":
            for exam in ["JEE Main", "BITSAT", "VITEEE", "MHT CET", "KCET", "CUET", "COMEDK"]:
                options.append((NodeType.EXAM, exam, EdgeType.NEXT_STEP if exam == "JEE Main" else EdgeType.BRANCH, {}))
            for ug in ["B.Sc Computer Science", "B.Sc Physics", "B.Sc Mathematics", "BCA"]:
                options.append((NodeType.EDUCATION, ug, EdgeType.BRANCH, {}))
        elif title == "12th PCB":
            options.append((NodeType.EXAM, "NEET", EdgeType.NEXT_STEP, {}))
            for ug in ["B.Sc Biology", "B.Sc Biotechnology", "B.Sc Nursing", "B.Pharma"]:
                options.append((NodeType.EDUCATION, ug, EdgeType.BRANCH, {}))
        elif title == "12th Commerce":
            options.append((NodeType.EDUCATION, "B.Com", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "BBA", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CA Foundation", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CUET", EdgeType.BRANCH, {}))
        elif title == "12th Arts":
            options.append((NodeType.EDUCATION, "BA Economics", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "BA Political Science", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "BA Psychology", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CLAT", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CUET", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "BA Journalism", EdgeType.BRANCH, {}))
        elif title.startswith("ITI"):
            field_map = {"Electrician": "Electrical Engineer", "Fitter": "Mechanical Engineer", "Welder": "Fitter",
                         "COPA": "IT Support Engineer", "Electronics": "Electronics Engineer", "Diesel Mechanic": "Automobile Engineer",
                         "CNC Operator": "CNC Operator", "Solar Technician": "Solar Technician"}
            for iti_key, job in field_map.items():
                if iti_key in title:
                    options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                    break
            else:
                options.append((NodeType.JOB_ROLE, "Fitter", EdgeType.NEXT_STEP, {}))
            # Lateral to diploma
            for dip in ["Diploma in Mechanical Engineering", "Diploma in Computer Engineering"]:
                if "Electric" in title or "Wireman" in title:
                    options.append((NodeType.EDUCATION, "Diploma in Electrical Engineering", EdgeType.BRANCH, {}))
                    break
                elif "Fitter" in title or "CNC" in title or "Machinist" in title:
                    options.append((NodeType.EDUCATION, "Diploma in Mechanical Engineering", EdgeType.BRANCH, {}))
                    break
        elif "Diploma" in title:
            # Diploma -> job or lateral to B.Tech
            field_jobs = {"Mechanical": "Junior Engineer (Mech)", "Civil": "Junior Engineer (Civil)",
                          "Computer": "Junior Software Engineer", "CS": "Junior Software Engineer",
                          "Electrical": "Electrical Engineer", "EC": "Electronics Engineer",
                          "Hotel": "Hotel Manager", "Fashion": "Fashion Designer",
                          "Pharmacy": "Pharmacist", "Automobile": "Automobile Engineer"}
            for kw, job in field_jobs.items():
                if kw in title:
                    options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                    break
            # Lateral entry to B.Tech
            btech_map = {"Mechanical": "B.Tech Mechanical", "Civil": "B.Tech Civil",
                         "Computer": "B.Tech Computer Science", "CS": "B.Tech Computer Science",
                         "Electrical": "B.Tech Electrical", "EC": "B.Tech Electronics & Comm",
                         "Automobile": "B.Tech Automobile", "Chemical": "B.Tech Chemical"}
            for kw, btech in btech_map.items():
                if kw in title:
                    options.append((NodeType.EDUCATION, btech, EdgeType.BRANCH, {"transition_difficulty": 4}))
                    break
        elif title in Taxonomies.UNDERGRAD_DEGREES:
            field = Taxonomies.UNDERGRAD_DEGREES[title].get("field", "")
            # Job options based on degree
            if field == "Engineering":
                eng_jobs = {"Computer": "Software Engineer", "AI": "ML Engineer", "Data": "Data Scientist",
                           "Cyber": "Security Analyst", "Mechanical": "Mechanical Engineer",
                           "Civil": "Civil Engineer", "Electrical": "Electrical Engineer",
                           "Electronics": "Electronics Engineer", "Automobile": "Automobile Engineer",
                           "Aerospace": "Aerospace Engineer", "Chemical": "Chemical Engineer",
                           "Biotechnology": "Biotechnologist", "Production": "Production Engineer",
                           "Mining": "Mining Engineer", "Petroleum": "Petroleum Engineer",
                           "Marine": "Marine Engineer", "Food": "Food Technologist",
                           "Textile": "Textile Engineer", "Energy": "Solar Energy Engineer",
                           "Nanotechnology": "Research Scientist", "Mechatronics": "Mechanical Engineer",
                           "Metallurgical": "Metallurgical Engineer", "Ceramic": "Quality Engineer",
                           "Instrumentation": "Instrumentation Engineer"}
                for kw, job in eng_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        break
                if not any(o[1] in eng_jobs.values() for o in options):
                    options.append((NodeType.JOB_ROLE, "Software Engineer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EXAM, "GATE", EdgeType.BRANCH, {}))
                options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {}))
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "MBA", EdgeType.BRANCH, {}))
            elif field == "Science":
                sci_jobs = {"Computer": "Software Engineer", "Data": "Data Analyst", "Mathematics": "Data Analyst",
                           "Physics": "Research Assistant", "Chemistry": "Lab Technician",
                           "Biology": "Research Assistant", "Biotechnology": "Lab Technician",
                           "Microbiology": "Lab Technician", "Statistics": "Data Analyst",
                           "Nursing": "Staff Nurse", "Agriculture": "Agriculture Officer",
                           "Forensic": "Lab Technician"}
                for kw, job in sci_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        break
                options.append((NodeType.EDUCATION, "M.Sc Computer Science", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "MCA", EdgeType.BRANCH, {}))
            elif field == "Commerce":
                options.append((NodeType.JOB_ROLE, "Accountant", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EXAM, "CA Foundation", EdgeType.BRANCH, {}))
                options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "M.Com", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "MBA Finance", EdgeType.BRANCH, {}))
            elif field == "Mgmt":
                options.append((NodeType.JOB_ROLE, "Business Analyst", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "MBA", EdgeType.BRANCH, {}))
            elif field == "CompApp":
                options.append((NodeType.JOB_ROLE, "Junior Software Engineer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "MCA", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "M.Tech CSE", EdgeType.BRANCH, {}))
            elif field == "Medicine":
                options.append((NodeType.JOB_ROLE, "Medical Officer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.JOB_ROLE, "General Physician", EdgeType.BRANCH, {}))
                options.append((NodeType.EXAM, "NEET PG", EdgeType.BRANCH, {}))
            elif field == "Pharmacy":
                options.append((NodeType.JOB_ROLE, "Pharmacist", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "M.Pharma", EdgeType.BRANCH, {}))
            elif field == "Law":
                options.append((NodeType.JOB_ROLE, "Lawyer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EXAM, "CLAT", EdgeType.BRANCH, {}))
            elif field == "Arts":
                arts_jobs = {"Economics": "Economist", "Political": "Policy Analyst", "Psychology": "Counselor",
                            "Journalism": "Journalist", "Mass": "PR Executive", "English": "Content Writer",
                            "Public": "Policy Analyst"}
                for kw, job in arts_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        break
                options.append((NodeType.EDUCATION, "MA Economics", EdgeType.BRANCH, {}))
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
            elif field == "Media":
                options.append((NodeType.JOB_ROLE, "Journalist", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "MA Mass Comm", EdgeType.BRANCH, {}))
            elif field == "Design":
                options.append((NodeType.JOB_ROLE, "Graphic Designer", EdgeType.NEXT_STEP, {}))
            elif field == "Fashion":
                options.append((NodeType.JOB_ROLE, "Fashion Designer", EdgeType.NEXT_STEP, {}))
            elif field == "Dental":
                options.append((NodeType.JOB_ROLE, "Dentist", EdgeType.NEXT_STEP, {}))
            elif field == "Ayurveda":
                options.append((NodeType.JOB_ROLE, "Ayurvedic Doctor", EdgeType.NEXT_STEP, {}))
            elif field == "Homeopathy":
                options.append((NodeType.JOB_ROLE, "Homeopathic Doctor", EdgeType.NEXT_STEP, {}))
            elif field == "Architecture":
                options.append((NodeType.JOB_ROLE, "Architect", EdgeType.NEXT_STEP, {}))
            elif field == "Healthcare":
                options.append((NodeType.JOB_ROLE, "Staff Nurse", EdgeType.NEXT_STEP, {}))
            elif field == "Agriculture":
                options.append((NodeType.JOB_ROLE, "Agriculture Officer", EdgeType.NEXT_STEP, {}))
            # Common options
            if not options:
                options.append((NodeType.JOB_ROLE, "Business Analyst", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {}))
        elif title in Taxonomies.POSTGRAD_DEGREES:
            field = Taxonomies.POSTGRAD_DEGREES[title].get("field", "")
            if field == "Engineering":
                pg_jobs = {"CSE": "Senior Software Engineer", "Data": "Data Scientist", "AI": "ML Engineer",
                          "Cyber": "Security Analyst", "VLSI": "VLSI Design Engineer",
                          "Structural": "Structural Engineer", "Automotive": "Automobile Engineer",
                          "Robotics": "Robotics Engineer"}
                for kw, job in pg_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        break
                options.append((NodeType.EDUCATION, "PhD Computer Science", EdgeType.BRANCH, {}))
            elif field == "Mgmt" or title == "MBA" or "MBA" in title:
                mba_jobs = {"Finance": "Financial Analyst", "Marketing": "Marketing Manager", "HR": "HR Manager",
                           "Analytics": "Data Scientist", "Healthcare": "Hospital Manager",
                           "Rural": "Rural Development Officer", "Agribusiness": "Agriculture Officer",
                           "Hospitality": "Hotel Manager", "Sports": "Sports Analyst",
                           "Digital": "Digital Marketing Specialist", "Supply": "Supply Chain Manager"}
                found = False
                for kw, job in mba_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        found = True
                        break
                if not found and title == "MBA":
                    options.append((NodeType.JOB_ROLE, "Product Manager", EdgeType.NEXT_STEP, {}))
                    options.append((NodeType.JOB_ROLE, "Management Consultant", EdgeType.BRANCH, {}))
                    options.append((NodeType.JOB_ROLE, "Consultant", EdgeType.BRANCH, {}))
                options.append((NodeType.EDUCATION, "PhD Management", EdgeType.BRANCH, {}))
            elif field == "Science":
                sci_jobs = {"Computer": "Software Engineer", "Data": "Data Scientist", "Physics": "Research Scientist",
                           "Chemistry": "Research Scientist", "Mathematics": "Data Scientist",
                           "Biotechnology": "Research Scientist", "Food": "Food Technologist",
                           "Environmental": "Environmental Scientist", "Agriculture": "Agriculture Officer",
                           "Forensic": "Forensic Expert"}
                for kw, job in sci_jobs.items():
                    if kw in title:
                        options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {}))
                        break
                options.append((NodeType.EDUCATION, "PhD Physics", EdgeType.BRANCH, {}))
            elif field == "Medicine" or "MD" in title or "MS" in title:
                options.append((NodeType.JOB_ROLE, "Specialist Doctor", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.JOB_ROLE, "Consultant", EdgeType.BRANCH, {}))
            elif field == "Commerce":
                options.append((NodeType.JOB_ROLE, "Senior Accountant", EdgeType.NEXT_STEP, {}))
            elif field == "Arts":
                options.append((NodeType.JOB_ROLE, "Professor", EdgeType.NEXT_STEP, {}))
            elif field == "Media":
                options.append((NodeType.JOB_ROLE, "Senior Journalist", EdgeType.NEXT_STEP, {}))
            elif field == "Law":
                options.append((NodeType.JOB_ROLE, "Corporate Lawyer", EdgeType.NEXT_STEP, {}))
            elif title == "MCA":
                options.append((NodeType.JOB_ROLE, "Senior Software Engineer", EdgeType.NEXT_STEP, {}))
            elif field == "Pharmacy":
                options.append((NodeType.JOB_ROLE, "Drug Inspector", EdgeType.NEXT_STEP, {}))
            if not options:
                options.append((NodeType.JOB_ROLE, "Consultant", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.JOB_ROLE, "Entrepreneur", EdgeType.BRANCH, {}))
        elif title in Taxonomies.DOCTORATES:
            options.append((NodeType.JOB_ROLE, "Professor", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.JOB_ROLE, "Research Scientist", EdgeType.BRANCH, {}))
        return options

    def _exam_next_steps(self, exam_node: Node) -> List[Tuple]:
        options = []
        title = exam_node.title
        if title in CareerPathGenerator.EXAM_TO_EDUCATION:
            targets = CareerPathGenerator.EXAM_TO_EDUCATION[title]
            for i, t in enumerate(targets):
                et = EdgeType.NEXT_STEP if i == 0 else EdgeType.BRANCH
                if any(t in deg for deg in [Taxonomies.UNDERGRAD_DEGREES, Taxonomies.POSTGRAD_DEGREES]):
                    options.append((NodeType.EDUCATION, t, et, {}))
                else:
                    options.append((NodeType.JOB_ROLE, t, et, {}))
        # Generic: exams can lead to jobs too
        exam_job_map = {
            "UPSC CSE": [("IAS Officer", 0.4), ("IPS Officer", 0.3), ("IFS Officer", 0.15), ("IRS Officer", 0.15)],
            "UPSC CAPF": [("IPS Officer", 0.5), ("DSP", 0.5)],
            "SSC CGL": [("Section Officer", 0.6), ("Auditor", 0.4)],
            "IBPS PO": [("Probationary Officer", 1.0)],
            "SBI PO": [("Probationary Officer", 1.0)],
            "RBI Grade B": [("Bank Manager", 0.6), ("Relationship Manager", 0.4)],
            "GATE": [("PSU Engineer", 0.5), ("Senior Software Engineer", 0.2)],
            "UGC NET": [("Assistant Professor", 0.6), ("Research Scientist", 0.4)],
            "CTET": [("School Teacher", 1.0)],
            "CA Foundation": [("Chartered Accountant", 0.7), ("Accountant", 0.3)],
            "CS Foundation": [("Company Secretary", 1.0)],
            "CMA Foundation": [("Cost Accountant", 1.0)],
            "NIFT": [("Fashion Designer", 0.6), ("B.Sc Fashion Technology", 0.4)],
            "IELTS": [("Research Scientist", 0.5)],
            "TOEFL": [("Research Scientist", 0.5)],
            "GRE": [("Research Scientist", 0.5)],
            "GMAT": [("Product Manager", 0.5)],
        }
        if title in exam_job_map:
            for job, prob in exam_job_map[title]:
                options.append((NodeType.JOB_ROLE, job, EdgeType.BRANCH, {"probability": prob}))
        return options

    def _job_role_next_steps(self, job_node: Node) -> List[Tuple]:
        options = []
        title = job_node.title
        domain = Taxonomies.JOB_ROLES.get(title, {}).get("domain", "")

        # 1. Promotion/Progression
        next_role = _get_next_in_progression(title)
        if next_role:
            options.append((NodeType.JOB_ROLE, next_role, EdgeType.NEXT_STEP, {"transition_difficulty": 5}))

        # 2. Lateral moves
        if title in CareerPathGenerator.JOB_LATERAL:
            for lateral in CareerPathGenerator.JOB_LATERAL[title]:
                options.append((NodeType.JOB_ROLE, lateral, EdgeType.BRANCH, {"transition_difficulty": 3}))

        # 3. Upskilling via education/exams
        if title in CareerPathGenerator.JOB_TO_EDUCATION:
            for edu_target, prob in CareerPathGenerator.JOB_TO_EDUCATION[title]:
                if edu_target in Taxonomies.EXAMS:
                    options.append((NodeType.EXAM, edu_target, EdgeType.BRANCH, {"probability": prob}))
                elif "PhD" in edu_target or "M." in edu_target or "MBA" in edu_target or "B." in edu_target or "MA" in edu_target or "LLM" in edu_target or "M.Com" in edu_target:
                    options.append((NodeType.EDUCATION, edu_target, EdgeType.BRANCH, {"probability": prob}))
                elif edu_target in Taxonomies.CERTIFICATIONS:
                    options.append((NodeType.CERTIFICATION, edu_target, EdgeType.BRANCH, {"probability": prob}))
                else:
                    options.append((NodeType.EDUCATION, edu_target, EdgeType.BRANCH, {"probability": prob}))

        # 4. Entrepreneurship/freelance after some experience
        level = Taxonomies.JOB_ROLES.get(title, {}).get("level", "")
        if level in (CareerLevel.MID, CareerLevel.SENIOR, CareerLevel.LEAD, CareerLevel.MANAGER):
            options.append((NodeType.JOB_ROLE, "Entrepreneur", EdgeType.BRANCH, {"transition_difficulty": 8}))
            options.append((NodeType.JOB_ROLE, "Freelancer", EdgeType.BRANCH, {"transition_difficulty": 4}))
            options.append((NodeType.JOB_ROLE, "Consultant", EdgeType.BRANCH, {"transition_difficulty": 5}))

        # 5. Government exams
        if domain not in ("Govt", "Police", "Defence"):
            if random.random() < 0.3:
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
            if random.random() < 0.2:
                options.append((NodeType.EXAM, "SSC CGL", EdgeType.BRANCH, {}))

        return options

    def _certification_next_steps(self, cert_node: Node) -> List[Tuple]:
        cert_job_map = {
            "Chartered Accountant (CA)": [("Chartered Accountant", 0.9), ("Financial Analyst", 0.1)],
            "Company Secretary (CS)": [("Company Secretary", 0.9)],
            "Cost & Management Accountant (CMA)": [("Cost Accountant", 0.9)],
            "PMP": [("Project Manager", 0.7), ("Program Manager", 0.3)],
            "AWS Certified Solutions Architect": [("Cloud Architect", 0.7), ("DevOps Engineer", 0.3)],
            "AWS Certified Developer": [("Software Engineer", 0.5), ("Backend Developer", 0.5)],
            "CISSP": [("Security Analyst", 0.6), ("Cyber Security Analyst", 0.4)],
            "CEH": [("Security Analyst", 0.7)],
            "ITIL Foundation": [("IT Manager", 0.5)],
            "CFA": [("Investment Banker", 0.4), ("Equity Research Analyst", 0.3), ("Wealth Manager", 0.3)],
            "FRM": [("Risk Manager", 0.7)],
            "Six Sigma Green Belt": [("Quality Engineer", 0.5), ("Operations Manager", 0.3)],
            "Six Sigma Black Belt": [("Quality Engineer", 0.3), ("Operations Manager", 0.4)],
            "NEBOSH": [("Safety Officer", 0.7)],
            "Cisco CCNA": [("Network Engineer", 0.7)],
            "Cisco CCNP": [("Network Engineer", 0.5), ("IT Manager", 0.3)],
            "Certified Scrum Master": [("Scrum Master", 0.7), ("Project Manager", 0.3)],
            "Google Professional Data Engineer": [("Data Engineer", 0.5), ("Data Scientist", 0.3)],
            "Salesforce Administrator": [("CRM Consultant", 0.5)],
        }
        options = []
        title = cert_node.title
        if title in cert_job_map:
            for job, prob in cert_job_map[title]:
                options.append((NodeType.JOB_ROLE, job, EdgeType.NEXT_STEP, {"probability": prob}))
        return options

    def _add_enrichment_edges(self, node: Node):
        if node.node_type == NodeType.JOB_ROLE:
            role_skills_map = {
                "Software Engineer": ["Python", "Java", "SQL", "AWS", "Docker"],
                "Senior Software Engineer": ["Python", "Java", "System Design", "AWS", "Kubernetes"],
                "Frontend Developer": ["JavaScript", "TypeScript", "React", "Figma"],
                "Backend Developer": ["Python", "Java", "SQL", "AWS", "Docker"],
                "Data Scientist": ["Python", "Machine Learning", "SQL", "Deep Learning"],
                "Data Analyst": ["SQL", "Excel", "Python", "Tableau", "Power BI"],
                "ML Engineer": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Docker"],
                "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Jenkins", "Linux"],
                "Mechanical Engineer": ["AutoCAD", "SolidWorks", "CATIA", "ANSYS"],
                "Civil Engineer": ["AutoCAD", "STAAD Pro"],
                "Electrical Engineer": ["PLC", "SCADA", "AutoCAD"],
                "Accountant": ["Tally ERP 9", "Excel", "GST", "QuickBooks"],
                "Chartered Accountant": ["Excel", "Financial Modeling", "GST", "Income Tax", "Ind AS"],
                "Marketing Manager": ["Digital Marketing", "SEO", "Google Analytics", "Leadership"],
                "HR Manager": ["Communication", "Leadership", "Excel", "Employment Law"],
                "Medical Officer": ["Clinical Knowledge", "Communication", "Patient Care"],
                "Lawyer": ["Criminal Law", "Civil Law", "Contract Drafting", "Legal Research"],
                "Project Manager": ["Project Management", "Agile", "Scrum", "Leadership"],
                "Graphic Designer": ["Adobe Photoshop", "Illustrator", "Figma"],
                "UI/UX Designer": ["Figma", "Adobe XD", "Sketch", "User Research"],
                "Journalist": ["Writing", "Communication", "Research", "Video Editing"],
                "Chef": ["Food Production", "HACCP", "Menu Planning"],
                "Sales Manager": ["Communication", "Negotiation", "CRM", "Leadership"],
                "Supply Chain Manager": ["Logistics", "SAP MM", "Excel", "Inventory Management"],
                "Business Analyst": ["Excel", "SQL", "Tableau", "Communication"],
                "Product Manager": ["Product Strategy", "Analytics", "Agile", "User Research"],
                "Entrepreneur": ["Leadership", "Problem Solving", "Financial Modeling", "Communication"],
                "IAS Officer": ["Leadership", "Public Policy", "Administration", "Communication"],
                "School Teacher": ["Communication", "Classroom Management", "Subject Knowledge"],
                "Professor": ["Research", "Publication", "Teaching", "Subject Expertise"],
                "Architect": ["AutoCAD", "SketchUp", "Building Design"],
                "Fashion Designer": ["Fashion Illustration", "Pattern Making", "Textile Knowledge"],
                "Data Engineer": ["Python", "SQL", "AWS", "Spark", "Kafka"],
                "Cyber Security Analyst": ["Network Security", "Python", "Linux", "Ethical Hacking"],
                "Robotics Engineer": ["Python", "C++", "ROS", "PLC", "Computer Vision"],
            }
            skills = role_skills_map.get(node.title, [])
            for skill_name in skills:
                skill_node = self._get_or_create_node(skill_name, NodeType.SKILL)
                edge = self._add_edge(skill_node, node, EdgeType.REQUIRES_SKILL)
                if edge and self.writer:
                    self.writer.write_edge(edge)

            typical_companies = {
                "Software Engineer": ["TCS", "Infosys", "Google India", "Microsoft India", "Flipkart", "Amazon India", "Wipro"],
                "Senior Software Engineer": ["Google India", "Microsoft India", "Amazon India", "Flipkart"],
                "Data Scientist": ["Amazon India", "Flipkart", "Zomato", "Swiggy", "Google India"],
                "Mechanical Engineer": ["Tata Motors", "Mahindra & Mahindra", "L&T", "BHEL"],
                "Civil Engineer": ["L&T", "Adani Group", "Shapoorji Pallonji"],
                "Electrical Engineer": ["BHEL", "Siemens India", "ABB India", "Schneider Electric"],
                "Accountant": ["TCS", "HDFC Bank", "ICICI Bank", "KPMG", "EY"],
                "Chartered Accountant": ["KPMG", "EY", "Deloitte", "PwC", "SBI", "HDFC Bank"],
                "Medical Officer": ["AIIMS", "Apollo Hospitals", "Fortis", "Max Healthcare"],
                "Lawyer": ["AZB & Partners", "Khaitan & Co", "Shardul Amarchand", "Trilegal"],
                "Marketing Manager": ["Unilever", "P&G", "Google India", "Meta India", "Tata Group"],
                "HR Manager": ["TCS", "Infosys", "Google India", "Microsoft India"],
                "Graphic Designer": ["Zomato", "Swiggy", "Nykaa", "Ogilvy"],
                "Product Manager": ["Google India", "Microsoft India", "Amazon India", "Flipkart"],
                "Consultant": ["McKinsey", "BCG", "Bain", "Deloitte", "KPMG", "EY"],
                "Bank Manager": ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank"],
                "IAS Officer": ["Government of India", "State Government"],
                "Professor": ["IITs", "IIMs", "Delhi University", "NITs", "BITS Pilani"],
                "Business Analyst": ["TCS", "Infosys", "Amazon India", "Deloitte"],
                "Data Engineer": ["Amazon India", "Flipkart", "Swiggy", "Zomato"],
            }
            companies = typical_companies.get(node.title, [])
            for comp_name in companies:
                comp_node = self._get_or_create_node(comp_name, NodeType.COMPANY)
                edge = self._add_edge(node, comp_node, EdgeType.CAN_WORK_AT)
                if edge and self.writer:
                    self.writer.write_edge(edge)


def main():
    config = GeneratorConfig(
        output_dir="./career_graph_output_v3",
        checkpoint_file="./career_checkpoint_v3.json",
        random_seed=42,
        max_total_paths=500,
        max_nodes=500000,
        max_edges=1000000,
    )
    random.seed(config.random_seed)

    taxonomies = Taxonomies()
    validator = TransitionValidator()

    generator = CareerGraphGenerator(config, taxonomies, validator)
    generator.generate()

    stats = {
        "total_nodes": generator.generated_nodes,
        "total_edges": generator.generated_edges,
        "total_paths": generator.path_counter,
        "generated_at": str(datetime.now()),
        "config": asdict(config),
    }
    stats_path = Path(config.output_dir) / "generation_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)
    logger.info(f"Stats saved to {stats_path}")


if __name__ == "__main__":
    main()
