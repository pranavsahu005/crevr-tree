#!/usr/bin/env python3
"""
Indian Career Intelligence Platform - Knowledge Graph Generator
Production-grade, resumable, deterministic, duplicate-safe generator.
Generates nodes, edges, and full career directions as a directed graph.
"""

import json
import csv
import hashlib
import logging
import os
import random
import sys
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from itertools import product, chain
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import yaml  # requires PyYAML

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("CareerGraphGen")


# ===========================================================================
# Enums and Constants
# ===========================================================================
class NodeType(str, Enum):
    EDUCATION = "education"
    CERTIFICATION = "certification"
    EXAM = "exam"
    JOB_ROLE = "job_role"
    SKILL = "skill"
    TOOL = "tool"
    INDUSTRY = "industry"
    COMPANY = "company"
    CAREER_PATH = "career_path"  # composite node


class EdgeType(str, Enum):
    NEXT_STEP = "next_step"  # linear progression
    BRANCH = "branch"  # diverging path
    REQUIRES_SKILL = "requires_skill"
    RECOMMENDS_CERTIFICATION = "recommends_certification"
    CAN_WORK_AT = "can_work_at"
    LEADS_TO = "leads_to"  # for career path to role
    ENRICHES = "enriches"  # skill to role enhancement


class EducationLevel(str, Enum):
    SCHOOL = "school"
    DIPLOMA = "diploma"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"
    POST_DOC = "post_doc"


class CareerLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    CXO = "cxo"
    FOUNDER = "founder"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
@dataclass
class GeneratorConfig:
    """Central configuration controlling generation scope and performance."""

    output_dir: str = "./output"
    checkpoint_file: str = "./checkpoint.json"
    formats: List[str] = field(
        default_factory=lambda: ["jsonl", "json", "csv", "yaml", "txt"]
    )
    # Generation limits (None = unlimited, but constrained by taxonomies)
    max_total_paths: int = 200_000  # maximum distinct career paths
    max_nodes: int = 5_000_000
    max_edges: int = 10_000_000
    random_seed: int = 42
    branch_probability: float = 0.3  # probability of branching at each step
    max_path_length: int = 12  # number of steps in a career path
    duplicate_detection_method: str = (
        "bloom"  # 'set' (in-memory), 'bloom' (memory efficient)
    )
    bloom_filter_capacity: int = 10_000_000
    bloom_filter_error_rate: float = 0.001
    resume: bool = True
    log_interval: int = 10000  # log progress every N items
    batch_size: int = 1000  # flush files every N items


# ===========================================================================
# Unique ID & Hash Management
# ===========================================================================
def deterministic_uuid(seed_string: str) -> str:
    """Generate deterministic UUID v5 based on a seed string (namespace DNS)."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_string))


def content_hash(*args: str) -> str:
    """Create a consistent hash for deduplication."""
    return hashlib.sha256("|".join(args).encode("utf-8")).hexdigest()


# ===========================================================================
# Node & Edge Data Classes
# ===========================================================================
@dataclass
class Node:
    """A node in the knowledge graph."""

    node_id: str
    node_type: NodeType
    title: str
    description: str = ""
    category: str = ""
    difficulty: int = 1  # 1-10
    education_level: Optional[EducationLevel] = None
    career_level: Optional[CareerLevel] = None
    industry: str = ""
    prerequisites: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    skills_gained: List[str] = field(default_factory=list)
    recommended_certifications: List[str] = field(default_factory=list)
    estimated_duration_months: Optional[int] = None
    future_opportunities: List[str] = field(default_factory=list)
    salary_band_inr: str = ""  # e.g., "3-6 LPA"
    growth_score: float = 0.0  # 0-100
    demand_score: float = 0.0
    automation_risk: float = 0.0  # 0-1
    ai_impact: float = 0.0  # -1 to 1
    remote_work_potential: float = 0.0
    global_opportunity: float = 0.0
    government_opportunity: float = 0.0
    private_opportunity: float = 0.0
    freelance_opportunity: float = 0.0
    entrepreneurship_opportunity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        """Unique content signature for deduplication."""
        base = f"{self.node_type.value}|{self.title}|{self.education_level or ''}|{self.career_level or ''}|{self.industry}"
        return content_hash(base)


@dataclass
class Edge:
    """A directed relationship between two nodes."""

    source_id: str
    destination_id: str
    relationship_type: EdgeType
    required_skills: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    estimated_time_months: Optional[int] = None
    transition_difficulty: int = 1  # 1-10
    recommended_certifications: List[str] = field(default_factory=list)
    probability: float = 0.5
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        return content_hash(
            f"{self.source_id}|{self.destination_id}|{self.relationship_type.value}"
        )


# ===========================================================================
# Taxonomies (Indian Career Ecosystem Ground Truth)
# ===========================================================================
class Taxonomies:
    """
    Curated set of Indian education streams, exams, roles, skills, companies.
    Used as building blocks for graph generation.
    """

    # ---- School Education ----
    SCHOOL_STREAMS = {
        "10th": {"level": EducationLevel.SCHOOL, "next": ["11th Science", "11th Commerce", "11th Arts", "ITI", "Diploma"]},
        "11th Science": {"level": EducationLevel.SCHOOL, "stream": "Science", "subjects": ["Physics", "Chemistry", "Mathematics/Biology"]},
        "11th Commerce": {"level": EducationLevel.SCHOOL, "stream": "Commerce", "subjects": ["Accountancy", "Business Studies", "Economics"]},
        "11th Arts": {"level": EducationLevel.SCHOOL, "stream": "Arts", "subjects": ["History", "Political Science", "Sociology"]},
        "12th PCM": {"level": EducationLevel.SCHOOL, "stream": "Science", "next_exams": ["JEE Main", "JEE Advanced", "BITSAT", "VITEEE", "SRMJEEE", "COMEDK", "State Engg Exams"]},
        "12th PCB": {"level": EducationLevel.SCHOOL, "stream": "Science", "next_exams": ["NEET", "AIIMS", "JIPMER", "State Medical Exams"]},
        "12th Commerce": {"level": EducationLevel.SCHOOL, "stream": "Commerce", "next_exams": ["CA Foundation", "CS Foundation", "CMA Foundation"]},
        "12th Arts": {"level": EducationLevel.SCHOOL, "stream": "Arts", "next_exams": ["CLAT", "AILET", "NIFT", "NID", "UPSC (after degree)"]},
    }

    # ---- Undergraduate Degrees ----
    UNDERGRAD_DEGREES = {
        "B.Tech CSE": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Tech ECE": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Tech Mechanical": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Tech Civil": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Tech Electrical": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Tech AI/ML": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Engineering"},
        "B.Sc Physics": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"},
        "B.Sc Chemistry": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"},
        "B.Sc Mathematics": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"},
        "B.Sc Computer Science": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Science"},
        "B.Com": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"},
        "B.Com (Hons)": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Commerce"},
        "BBA": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Management"},
        "BCA": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Computer Applications"},
        "BA Economics": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"},
        "BA English": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"},
        "BA Political Science": {"level": EducationLevel.UNDERGRADUATE, "duration": 3, "field": "Arts"},
        "B.Arch": {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Architecture"},
        "MBBS": {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Medicine"},
        "BDS": {"level": EducationLevel.UNDERGRADUATE, "duration": 5, "field": "Dental"},
        "B.Pharma": {"level": EducationLevel.UNDERGRADUATE, "duration": 4, "field": "Pharmacy"},
        "BHMS": {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Homeopathy"},
        "BAMS": {"level": EducationLevel.UNDERGRADUATE, "duration": 5.5, "field": "Ayurveda"},
    }

    # ---- Postgraduate ----
    POSTGRAD_DEGREES = {
        "M.Tech CSE": {"level": EducationLevel.POSTGRADUATE, "duration": 2},
        "M.Tech VLSI": {},
        "M.Sc Data Science": {},
        "MCA": {"duration": 2},
        "MBA": {"specializations": ["Finance", "Marketing", "HR", "Operations", "IT", "Business Analytics"]},
        "M.Com": {},
        "MA Economics": {},
        "MD": {"field": "Medicine"},
        "MS": {"field": "Surgery"},
        "M.Pharma": {},
    }

    # ---- Competitive Exams ----
    EXAMS = {
        "JEE Main": {"type": "engineering_entrance"},
        "JEE Advanced": {},
        "NEET": {"type": "medical_entrance"},
        "CAT": {"type": "management_entrance"},
        "GATE": {"type": "engineering_postgrad"},
        "UPSC CSE": {"type": "civil_services"},
        "SSC CGL": {},
        "IBPS PO": {},
        "SBI PO": {},
        "RRB NTPC": {},
        "CLAT": {"type": "law_entrance"},
        "NIFT": {"type": "design_entrance"},
        "CEED": {},
        "UGC NET": {"type": "academic"},
        "GMAT": {"type": "international_mba"},
        "GRE": {"type": "international_ms"},
        "IELTS": {"type": "english_proficiency"},
        "TOEFL": {},
    }

    # ---- Job Roles (Hierarchical) ----
    JOB_ROLES = {
        # Software Engineering
        "Junior Software Engineer": {"level": CareerLevel.JUNIOR, "industry": "IT", "salary": "3-6 LPA"},
        "Software Engineer": {"level": CareerLevel.MID, "salary": "6-12 LPA"},
        "Senior Software Engineer": {"level": CareerLevel.SENIOR, "salary": "12-25 LPA"},
        "Tech Lead": {"level": CareerLevel.LEAD, "salary": "20-35 LPA"},
        "Engineering Manager": {"level": CareerLevel.MANAGER, "salary": "30-50 LPA"},
        "Director Engineering": {"level": CareerLevel.DIRECTOR, "salary": "50-80 LPA"},
        "VP Engineering": {"level": CareerLevel.VP, "salary": "80 LPA - 1.5 Cr"},
        "CTO": {"level": CareerLevel.CXO, "salary": "1 Cr+"},
        # Data Roles
        "Data Analyst": {"level": CareerLevel.ENTRY},
        "Data Scientist": {"level": CareerLevel.MID},
        "ML Engineer": {},
        "AI Research Scientist": {},
        # Civil Services
        "IAS Officer": {},
        "IPS Officer": {},
        "IFS Officer": {},
        "IRS Officer": {},
        # Banking
        "Probationary Officer": {},
        "Bank Manager": {},
        # Healthcare
        "Medical Officer": {},
        "Surgeon": {},
        "General Physician": {},
        "Cardiologist": {},
        # Others
        "Chartered Accountant": {},
        "Company Secretary": {},
        "Cost Accountant": {},
        "Lawyer": {},
        "Judge": {},
        "Architect": {},
        "Graphic Designer": {},
        "UI/UX Designer": {},
        "Product Manager": {},
        "Business Analyst": {},
        "Marketing Manager": {},
        "HR Manager": {},
        "Supply Chain Manager": {},
        "Professor": {},
        "Research Scientist": {},
        "Entrepreneur": {},
        "Freelancer": {},
        "Consultant": {},
    }

    # ---- Skills ----
    SKILLS = {
        "Python": {"type": "programming"},
        "Java": {},
        "C++": {},
        "JavaScript": {},
        "SQL": {},
        "AWS": {"type": "cloud"},
        "Azure": {},
        "GCP": {},
        "Docker": {},
        "Kubernetes": {},
        "Machine Learning": {},
        "Deep Learning": {},
        "NLP": {},
        "Data Analysis": {},
        "Excel": {},
        "Financial Modeling": {},
        "Communication": {"type": "soft"},
        "Leadership": {"type": "soft"},
        "Problem Solving": {},
        "Critical Thinking": {},
    }

    # ---- Companies (Indian + MNC) ----
    COMPANIES = {
        "TCS": {"type": "IT Services", "indian": True},
        "Infosys": {},
        "Wipro": {},
        "HCL": {},
        "Tech Mahindra": {},
        "Google India": {"type": "Product"},
        "Microsoft India": {},
        "Amazon India": {},
        "Flipkart": {},
        "Ola": {},
        "Zomato": {},
        "Swiggy": {},
        "Paytm": {},
        "Byju's": {},
        "Reliance Jio": {},
        "Adani Group": {},
        "Tata Motors": {},
        "Mahindra & Mahindra": {},
        "L&T": {},
        "BHEL": {"type": "PSU"},
        "ONGC": {"type": "PSU"},
        "Indian Oil": {"type": "PSU"},
        "SBI": {"type": "PSU Bank"},
        "HDFC Bank": {},
        "ICICI Bank": {},
        "ISRO": {"type": "Space"},
        "DRDO": {"type": "Defence Research"},
        "AIIMS": {"type": "Healthcare"},
        "Apollo Hospitals": {},
        "Fortis": {},
        "IITs": {"type": "Education"},
        "IIMs": {},
    }

    # ---- Industries ----
    INDUSTRIES = [
        "Information Technology",
        "Software Services",
        "Banking",
        "Financial Services",
        "Insurance",
        "Healthcare",
        "Pharmaceuticals",
        "Automobile",
        "Manufacturing",
        "Construction",
        "Retail",
        "E-commerce",
        "Telecom",
        "Media & Entertainment",
        "Education",
        "Government",
        "Defence",
        "Agriculture",
        "Energy",
        "Aerospace",
        "Semiconductor",
        "Gaming",
        "Cyber Security",
        "Cloud Computing",
        "Artificial Intelligence",
        "Renewable Energy",
    ]

    @classmethod
    def get_all_education_nodes(cls) -> List[Dict]:
        nodes = []
        for name, info in cls.SCHOOL_STREAMS.items():
            nodes.append({"title": name, "education_level": EducationLevel.SCHOOL, **info, "type": NodeType.EDUCATION})
        for name, info in cls.UNDERGRAD_DEGREES.items():
            nodes.append({"title": name, "education_level": EducationLevel.UNDERGRADUATE, **info, "type": NodeType.EDUCATION})
        for name, info in cls.POSTGRAD_DEGREES.items():
            nodes.append({"title": name, "education_level": EducationLevel.POSTGRADUATE, **info, "type": NodeType.EDUCATION})
        # Diplomas
        diplomas = ["Diploma in Mechanical", "Diploma in Civil", "Diploma in CS", "Diploma in Electrical", "Diploma in EC"]
        for d in diplomas:
            nodes.append({"title": d, "education_level": EducationLevel.DIPLOMA, "type": NodeType.EDUCATION})
        return nodes

    @classmethod
    def get_all_exam_nodes(cls) -> List[Dict]:
        return [{"title": name, **info, "type": NodeType.EXAM} for name, info in cls.EXAMS.items()]

    @classmethod
    def get_all_job_role_nodes(cls) -> List[Dict]:
        return [{"title": name, **info, "type": NodeType.JOB_ROLE} for name, info in cls.JOB_ROLES.items()]

    @classmethod
    def get_all_skill_nodes(cls) -> List[Dict]:
        return [{"title": name, **info, "type": NodeType.SKILL} for name, info in cls.SKILLS.items()]

    @classmethod
    def get_all_company_nodes(cls) -> List[Dict]:
        return [{"title": name, **info, "type": NodeType.COMPANY} for name, info in cls.COMPANIES.items()]

    @classmethod
    def get_all_industry_nodes(cls) -> List[Dict]:
        return [{"title": ind, "type": NodeType.INDUSTRY} for ind in cls.INDUSTRIES]


# ===========================================================================
# Deduplication Tracker
# ===========================================================================
class DeduplicationTracker:
    """Tracks generated signatures to prevent duplicates. Supports in-memory set or Bloom filter."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        if config.duplicate_detection_method == "bloom":
            try:
                from pybloom_live import BloomFilter  # type: ignore
                self.filter = BloomFilter(
                    capacity=config.bloom_filter_capacity,
                    error_rate=config.bloom_filter_error_rate,
                )
                self._is_bloom = True
            except ImportError:
                logger.warning("pybloom_live not installed, falling back to in-memory set")
                self._is_bloom = False
                self._set: Set[str] = set()
        else:
            self._is_bloom = False
            self._set = set()

    def add(self, signature: str) -> None:
        if self._is_bloom:
            self.filter.add(signature)  # type: ignore
        else:
            self._set.add(signature)

    def exists(self, signature: str) -> bool:
        if self._is_bloom:
            return signature in self.filter  # type: ignore
        else:
            return signature in self._set

    def size(self) -> int:
        if self._is_bloom:
            return len(self.filter)  # type: ignore
        return len(self._set)


# ===========================================================================
# Checkpoint Manager
# ===========================================================================
class CheckpointManager:
    """Manages resumable state using a JSON checkpoint file."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.state: Dict[str, Any] = {
            "generated_nodes_count": 0,
            "generated_edges_count": 0,
            "path_counter": 0,
            "random_state": random.getstate(),
            "dedup_signatures": [],
        }

    def save(self, tracker: DeduplicationTracker, node_count: int, edge_count: int, path_counter: int) -> None:
        """Persist current state."""
        self.state["generated_nodes_count"] = node_count
        self.state["generated_edges_count"] = edge_count
        self.state["path_counter"] = path_counter
        self.state["random_state"] = random.getstate()
        if not tracker._is_bloom:
            # save only if set, not bloom (bloom can't be serialized simply)
            self.state["dedup_signatures"] = list(tracker._set) if hasattr(tracker, "_set") else []
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.state, f, default=str, indent=2)
        logger.debug(f"Checkpoint saved to {self.path}")

    def load(self, tracker: DeduplicationTracker) -> Tuple[int, int, int]:
        """Restore state if exists. Returns (node_count, edge_count, path_counter)."""
        if self.path.exists():
            with open(self.path, "r") as f:
                self.state = json.load(f)
            random.setstate(tuple(self.state["random_state"]))
            if not tracker._is_bloom and "dedup_signatures" in self.state:
                for sig in self.state["dedup_signatures"]:
                    tracker.add(sig)
            logger.info(f"Resumed from checkpoint: {self.state['generated_nodes_count']} nodes, "
                        f"{self.state['generated_edges_count']} edges, path #{self.state['path_counter']}")
            return (
                self.state["generated_nodes_count"],
                self.state["generated_edges_count"],
                self.state["path_counter"],
            )
        return 0, 0, 0


# ===========================================================================
# Multi-Format Streaming Writer
# ===========================================================================
class MultiFormatWriter:
    """Writes nodes and edges to multiple formats incrementally."""

    def __init__(self, output_dir: str, formats: List[str]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.formats = formats
        self.handles: Dict[str, Any] = {}
        self._init_files()

    def _init_files(self):
        """Open all required file handles."""
        if "jsonl" in self.formats:
            self.handles["nodes_jsonl"] = open(self.output_dir / "nodes.jsonl", "a", encoding="utf-8")
            self.handles["edges_jsonl"] = open(self.output_dir / "edges.jsonl", "a", encoding="utf-8")
        if "csv" in self.formats:
            self.handles["nodes_csv"] = open(self.output_dir / "nodes.csv", "a", newline="", encoding="utf-8")
            self.handles["edges_csv"] = open(self.output_dir / "edges.csv", "a", newline="", encoding="utf-8")
            self._csv_writers = {}
        if "yaml" in self.formats:
            # YAML streaming via documents
            self.handles["nodes_yaml"] = open(self.output_dir / "nodes.yaml", "a", encoding="utf-8")
            self.handles["edges_yaml"] = open(self.output_dir / "edges.yaml", "a", encoding="utf-8")
            self._yaml_documents_written = 0
        # JSON will be written as large array at finalization (or using jsonl and later merged)
        # We'll collect JSON data in memory? To avoid RAM, we'll build JSON from JSONL post-generation.
        # For large scale, we can use streaming JSON array with manual separator.
        if "json" in self.formats:
            self.handles["nodes_json"] = open(self.output_dir / "nodes.json", "a", encoding="utf-8")
            self.handles["edges_json"] = open(self.output_dir / "edges.json", "a", encoding="utf-8")
            self._json_first_node = True
            self._json_first_edge = True
            # Start array
            self.handles["nodes_json"].write("[\n")
            self.handles["edges_json"].write("[\n")
        if "txt" in self.formats:
            self.handles["career_paths_txt"] = open(self.output_dir / "career_paths.txt", "a", encoding="utf-8")

    def write_node(self, node: Node) -> None:
        """Write node to all configured formats."""
        node_dict = asdict(node)
        node_dict["node_type"] = node.node_type.value
        node_dict["education_level"] = node.education_level.value if node.education_level else None
        node_dict["career_level"] = node.career_level.value if node.career_level else None
        # JSONL
        if "jsonl" in self.formats:
            self.handles["nodes_jsonl"].write(json.dumps(node_dict, ensure_ascii=False) + "\n")
        # CSV
        if "csv" in self.formats:
            writer = self._get_csv_writer("nodes_csv", list(node_dict.keys()))
            writer.writerow(node_dict)
        # YAML (append document)
        if "yaml" in self.formats:
            yaml.dump([node_dict], self.handles["nodes_yaml"], allow_unicode=True, default_flow_style=False)
        # JSON (streaming array)
        if "json" in self.formats:
            if not self._json_first_node:
                self.handles["nodes_json"].write(",\n")
            else:
                self._json_first_node = False
            json.dump(node_dict, self.handles["nodes_json"], ensure_ascii=False)

    def write_edge(self, edge: Edge) -> None:
        """Write edge to all formats."""
        edge_dict = asdict(edge)
        edge_dict["relationship_type"] = edge.relationship_type.value
        if "jsonl" in self.formats:
            self.handles["edges_jsonl"].write(json.dumps(edge_dict, ensure_ascii=False) + "\n")
        if "csv" in self.formats:
            writer = self._get_csv_writer("edges_csv", list(edge_dict.keys()))
            writer.writerow(edge_dict)
        if "yaml" in self.formats:
            yaml.dump([edge_dict], self.handles["edges_yaml"], allow_unicode=True, default_flow_style=False)
        if "json" in self.formats:
            if not self._json_first_edge:
                self.handles["edges_json"].write(",\n")
            else:
                self._json_first_edge = False
            json.dump(edge_dict, self.handles["edges_json"], ensure_ascii=False)

    def write_career_path_text(self, path_description: str) -> None:
        if "txt" in self.formats:
            self.handles["career_paths_txt"].write(path_description + "\n---\n")

    def _get_csv_writer(self, key: str, fieldnames: List[str]):
        if key not in self._csv_writers:
            writer = csv.DictWriter(self.handles[key], fieldnames=fieldnames, extrasaction="ignore")
            # Write header only if file is empty
            if self.handles[key].tell() == 0:
                writer.writeheader()
            self._csv_writers[key] = writer
        return self._csv_writers[key]

    def finalize(self):
        """Close all files and finalize JSON arrays."""
        if "json" in self.formats:
            self.handles["nodes_json"].write("\n]\n")
            self.handles["edges_json"].write("\n]\n")
        for handle in self.handles.values():
            if hasattr(handle, "close"):
                handle.close()
        logger.info("All output files finalized.")


# ===========================================================================
# Graph Node Factory & Edge Builder
# ===========================================================================
class NodeFactory:
    """Creates nodes from taxonomies ensuring deterministic IDs."""

    @staticmethod
    def create(node_info: Dict) -> Node:
        title = node_info["title"]
        node_type = node_info["type"]
        edu_level = node_info.get("education_level")
        career_level = node_info.get("career_level")
        # Deterministic ID based on title + type
        node_id = deterministic_uuid(f"{node_type.value}:{title}")
        return Node(
            node_id=node_id,
            node_type=node_type,
            title=title,
            description=node_info.get("description", f"{title} - Indian Career Node"),
            category=node_info.get("category", ""),
            education_level=edu_level,
            career_level=career_level,
            industry=node_info.get("industry", ""),
            prerequisites=node_info.get("prerequisites", []),
            skills_required=node_info.get("skills_required", []),
            skills_gained=node_info.get("skills_gained", []),
            recommended_certifications=node_info.get("recommended_certifications", []),
            estimated_duration_months=node_info.get("duration") * 12 if "duration" in node_info else None,
            salary_band_inr=node_info.get("salary", ""),
            metadata=node_info.get("metadata", {}),
        )


class EdgeBuilder:
    """Creates edges between two nodes."""

    @staticmethod
    def connect(
        source: Node,
        destination: Node,
        rel_type: EdgeType,
        **kwargs,
    ) -> Edge:
        return Edge(
            source_id=source.node_id,
            destination_id=destination.node_id,
            relationship_type=rel_type,
            **kwargs,
        )


# ===========================================================================
# Transition Validation Matrix (Realistic Career Moves)
# ===========================================================================
class TransitionValidator:
    """
    Ensures career transitions are logically valid.
    Prevents impossible paths like MBBS -> Mechanical Engineer.
    """

    # Map of education node titles to allowed next job roles categories
    EDUCATION_TO_ROLE_MAP = {
        "MBBS": ["Medical Officer", "General Physician", "Surgeon", "Cardiologist", "Medical Researcher"],
        "B.Tech CSE": ["Software Engineer", "Data Scientist", "ML Engineer"],
        "B.Tech Mechanical": ["Mechanical Engineer", "Design Engineer", "Production Manager"],
        "B.Tech Civil": ["Civil Engineer", "Site Engineer", "Structural Engineer"],
        "BCA": ["Software Engineer", "System Administrator"],
        "BBA": ["Business Analyst", "Marketing Executive", "HR Executive"],
        "B.Com": ["Accountant", "Financial Analyst", "Bank PO"],
        "B.Sc Physics": ["Research Assistant", "Data Analyst"],
        "B.Arch": ["Architect", "Urban Planner"],
    }

    @staticmethod
    def is_valid_transition(source_type: NodeType, dest_type: NodeType, source_title: str, dest_title: str) -> bool:
        """Return True if transition is realistically possible."""
        # General rules
        if source_type == NodeType.EDUCATION and dest_type == NodeType.JOB_ROLE:
            allowed_roles = TransitionValidator.EDUCATION_TO_ROLE_MAP.get(source_title, [])
            if allowed_roles:
                return dest_title in allowed_roles
            # If degree not in map, allow if logical by field match (heuristic)
            # e.g., B.Sc Chemistry -> Chemist, but we don't have all roles defined
            return True  # fallback to generic permissive for now, but we'll restrict later
        if source_type == NodeType.JOB_ROLE and dest_type == NodeType.JOB_ROLE:
            # Allow level progression within same domain; block cross-domain?
            # For simplicity, allow only if industry matches. We'll enforce in generator.
            return True
        # Education to education: allow progression if level increments
        if source_type == NodeType.EDUCATION and dest_type == NodeType.EDUCATION:
            return True
        return True  # default permissive for other combos


# ===========================================================================
# Career Path Generator (Graph Builder)
# ===========================================================================
class CareerGraphGenerator:
    """
    Generates career paths as directed graph sequences, respecting realism,
    branching, and producing unique paths.
    """

    def __init__(self, config: GeneratorConfig, taxonomies: Taxonomies, validator: TransitionValidator):
        self.config = config
        self.taxonomies = taxonomies
        self.validator = validator
        self.node_factory = NodeFactory()
        self.edge_builder = EdgeBuilder()
        self.dedup = DeduplicationTracker(config)
        self.checkpoint_mgr = CheckpointManager(config.checkpoint_file)
        self.writer: Optional[MultiFormatWriter] = None

        # Pre-built node caches (title -> Node)
        self.nodes_cache: Dict[str, Node] = {}
        # Track which nodes have been written to output
        self._written_nodes: Set[str] = set()
        # Counter
        self.generated_nodes = 0
        self.generated_edges = 0
        self.path_counter = 0

        # Pre-seed all base taxonomy nodes into cache (deduplicated)
        self._initialize_base_nodes()

    def _initialize_base_nodes(self):
        """Create nodes for all taxonomies and cache them."""
        all_node_dicts = chain(
            self.taxonomies.get_all_education_nodes(),
            self.taxonomies.get_all_exam_nodes(),
            self.taxonomies.get_all_job_role_nodes(),
            self.taxonomies.get_all_skill_nodes(),
            self.taxonomies.get_all_company_nodes(),
            self.taxonomies.get_all_industry_nodes(),
        )
        for info in all_node_dicts:
            node = self.node_factory.create(info)
            if not self.dedup.exists(node.signature()):
                self.dedup.add(node.signature())
                self.nodes_cache[node.title] = node
                self.generated_nodes += 1

    def _get_or_create_node(self, title: str, node_type: NodeType, **extra) -> Node:
        """Retrieve from cache or create a new node."""
        if title in self.nodes_cache:
            return self.nodes_cache[title]
        # Attempt to create
        node_dict = {"title": title, "type": node_type, **extra}
        node = self.node_factory.create(node_dict)
        sig = node.signature()
        if not self.dedup.exists(sig):
            self.dedup.add(sig)
            self.nodes_cache[title] = node
            self.generated_nodes += 1
            # Write newly created node immediately
            if self.writer and node.node_id not in self._written_nodes:
                self.writer.write_node(node)
                self._written_nodes.add(node.node_id)
            return node
        else:
            # Should find in cache by title (title unique per type in taxonomy)
            # If not, something inconsistent.
            logger.warning(f"Node {title} dedup conflict, retrieving from cache by title")
            return self.nodes_cache[title]

    def _add_edge(self, source: Node, dest: Node, rel_type: EdgeType, **kwargs) -> Optional[Edge]:
        """Create edge if valid and non-duplicate."""
        edge = self.edge_builder.connect(source, dest, rel_type, **kwargs)
        if not self.dedup.exists(edge.signature()):
            self.dedup.add(edge.signature())
            self.generated_edges += 1
            return edge
        return None

    def generate(self) -> None:
        """Main generation loop."""
        self.writer = MultiFormatWriter(self.config.output_dir, self.config.formats)

        # Resume if configured
        start_nodes_count, start_edges_count, start_path_counter = self.checkpoint_mgr.load(self.dedup)
        self.generated_nodes = start_nodes_count or self.generated_nodes
        self.generated_edges = start_edges_count or self.generated_edges
        self.path_counter = start_path_counter

        # Pre-write base nodes to files if resuming from zero? We need to write all cached nodes.
        # We'll write all cached nodes at beginning to ensure they're in output.
        self._write_cached_nodes()

        # Generate paths starting from school education (10th) and also diplomas.
        # We'll define path seeds: list of starting nodes (titles)
        seed_titles = [
            "10th",
            "Diploma in Mechanical",
            "Diploma in CS",
            "Diploma in Civil",
            "Diploma in Electrical",
        ]
        # For each seed, expand graph using recursive branching.
        for seed_title in seed_titles:
            seed_node = self._get_or_create_node(seed_title, NodeType.EDUCATION)
            if not seed_node:
                continue
            self._expand_from_node(seed_node, depth=0, visited_path=[])

            # Check limits
            if self.path_counter >= self.config.max_total_paths:
                break
            if self.generated_nodes >= self.config.max_nodes or self.generated_edges >= self.config.max_edges:
                break

        # Finalize output
        self.writer.finalize()
        self.checkpoint_mgr.save(self.dedup, self.generated_nodes, self.generated_edges, self.path_counter)
        logger.info(f"Generation complete. Nodes: {self.generated_nodes}, Edges: {self.generated_edges}, Paths: {self.path_counter}")

    def _write_cached_nodes(self):
        """Write all currently cached nodes to output files."""
        for node in self.nodes_cache.values():
            self.writer.write_node(node)  # type: ignore
            self._written_nodes.add(node.node_id)

    def _expand_from_node(self, current_node: Node, depth: int, visited_path: List[str]):
        """
        Recursively build career paths from a node.
        Applies branching logic and adds edges/nodes.
        """
        if depth > self.config.max_path_length or self.path_counter >= self.config.max_total_paths:
            return
        if self.generated_nodes >= self.config.max_nodes or self.generated_edges >= self.config.max_edges:
            return

        # Determine possible next steps based on current node type
        next_options: List[Tuple[NodeType, str, EdgeType, Dict]] = []  # (dest type, dest title, edge type, edge kwargs)

        if current_node.node_type == NodeType.EDUCATION:
            next_options = self._education_next_steps(current_node)
        elif current_node.node_type == NodeType.EXAM:
            next_options = self._exam_next_steps(current_node)
        elif current_node.node_type == NodeType.JOB_ROLE:
            next_options = self._job_role_next_steps(current_node)
        elif current_node.node_type == NodeType.CERTIFICATION:
            next_options = self._certification_next_steps(current_node)
        # Skills/Companies/Industries are added as enrichment edges, not main path flow.
        # We'll add enrichment edges (REQUIRES_SKILL, CAN_WORK_AT) dynamically.

        # Add enrichment edges: skills required for job roles, companies etc.
        self._add_enrichment_edges(current_node)

        if not next_options:
            return

        # For branching, we may take multiple options probabilistically.
        # Deterministic but variety via random with seed.
        random.shuffle(next_options)  # deterministic shuffle for variety but reproducible

        # Always take first option (main path), and maybe branch to others.
        main = next_options[0]
        branches = next_options[1:] if random.random() < self.config.branch_probability else []

        # Process main path
        self._process_transition(current_node, main, depth, visited_path)

        # Process branches
        for branch_option in branches:
            if self.path_counter >= self.config.max_total_paths:
                break
            self._process_transition(current_node, branch_option, depth, visited_path)

    def _process_transition(self, current_node: Node, option: Tuple, depth: int, visited_path: List[str]):
        """Create destination node, edge, record path, and continue expansion."""
        dest_type, dest_title, edge_type, edge_kwargs = option
        # Prevent cycles (same node in path)
        if dest_title in visited_path:
            return
        dest_node = self._get_or_create_node(dest_title, dest_type)
        # Validate
        if not self.validator.is_valid_transition(current_node.node_type, dest_type, current_node.title, dest_title):
            return

        edge = self._add_edge(current_node, dest_node, edge_type, **edge_kwargs)
        if edge:
            self.writer.write_edge(edge)  # type: ignore

        # Record path text if we reached a job role or final level
        new_path = visited_path + [dest_title]
        if dest_type == NodeType.JOB_ROLE or depth == self.config.max_path_length:
            self.path_counter += 1
            path_str = " → ".join(new_path)
            self.writer.write_career_path_text(f"Path #{self.path_counter}: {path_str}")

            # Periodic checkpoint
            if self.path_counter % self.config.log_interval == 0:
                logger.info(f"Generated {self.path_counter} paths, {self.generated_nodes} nodes, {self.generated_edges} edges")
                self.checkpoint_mgr.save(self.dedup, self.generated_nodes, self.generated_edges, self.path_counter)

        # Continue expanding from destination
        self._expand_from_node(dest_node, depth + 1, new_path)

    def _education_next_steps(self, edu_node: Node) -> List[Tuple]:
        """Generate possible next steps after an education node."""
        options = []
        title = edu_node.title
        # After 10th -> 11th streams, ITI, Diploma
        if title == "10th":
            for stream in ["11th Science", "11th Commerce", "11th Arts"]:
                options.append((NodeType.EDUCATION, stream, EdgeType.NEXT_STEP, {}))
            for dip in ["Diploma in Mechanical", "Diploma in Civil", "Diploma in CS", "Diploma in Electrical"]:
                options.append((NodeType.EDUCATION, dip, EdgeType.BRANCH, {}))
        # After 11th -> 12th
        elif title.startswith("11th"):
            if "Science" in title:
                options.append((NodeType.EDUCATION, "12th PCM", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "12th PCB", EdgeType.BRANCH, {}))
            elif "Commerce" in title:
                options.append((NodeType.EDUCATION, "12th Commerce", EdgeType.NEXT_STEP, {}))
            elif "Arts" in title:
                options.append((NodeType.EDUCATION, "12th Arts", EdgeType.NEXT_STEP, {}))
        # After 12th PCM -> Engineering exams or B.Sc
        elif title == "12th PCM":
            options.append((NodeType.EXAM, "JEE Main", EdgeType.NEXT_STEP, {"probability": 0.8}))
            options.append((NodeType.EXAM, "BITSAT", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "B.Sc Physics", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "B.Sc Mathematics", EdgeType.BRANCH, {}))
        elif title == "12th PCB":
            options.append((NodeType.EXAM, "NEET", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "B.Sc Chemistry", EdgeType.BRANCH, {}))
        elif title == "12th Commerce":
            options.append((NodeType.EDUCATION, "B.Com", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "BBA", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CA Foundation", EdgeType.BRANCH, {}))
        elif title == "12th Arts":
            options.append((NodeType.EDUCATION, "BA Economics", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "BA Political Science", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "CLAT", EdgeType.BRANCH, {}))
        # Diploma -> Job or lateral to B.Tech
        elif "Diploma" in title:
            if "Mechanical" in title:
                options.append((NodeType.JOB_ROLE, "Junior Engineer (Mech)", EdgeType.NEXT_STEP, {}))
            elif "Civil" in title:
                options.append((NodeType.JOB_ROLE, "Junior Engineer (Civil)", EdgeType.NEXT_STEP, {}))
            elif "CS" in title:
                options.append((NodeType.JOB_ROLE, "Junior Software Engineer", EdgeType.NEXT_STEP, {}))
            # Lateral entry to B.Tech
            options.append((NodeType.EDUCATION, "B.Tech Mechanical", EdgeType.BRANCH, {}))
        # Undergraduate -> jobs, higher exams, PG
        elif title in self.taxonomies.UNDERGRAD_DEGREES:
            field = self.taxonomies.UNDERGRAD_DEGREES[title].get("field", "")
            if "Engineering" in field:
                if "CSE" in title or "CS" in title or "AI" in title:
                    options.append((NodeType.JOB_ROLE, "Software Engineer", EdgeType.NEXT_STEP, {}))
                    options.append((NodeType.EXAM, "GATE", EdgeType.BRANCH, {}))
                    options.append((NodeType.EDUCATION, "M.Tech CSE", EdgeType.BRANCH, {}))
                    options.append((NodeType.EDUCATION, "MBA", EdgeType.BRANCH, {}))
                elif "Mechanical" in title:
                    options.append((NodeType.JOB_ROLE, "Mechanical Engineer", EdgeType.NEXT_STEP, {}))
                elif "Civil" in title:
                    options.append((NodeType.JOB_ROLE, "Civil Engineer", EdgeType.NEXT_STEP, {}))
                elif "Electrical" in title:
                    options.append((NodeType.JOB_ROLE, "Electrical Engineer", EdgeType.NEXT_STEP, {}))
                # Common: PSUs via GATE, UPSC
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
            elif field == "Science":
                options.append((NodeType.EDUCATION, "M.Sc Data Science", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.JOB_ROLE, "Research Assistant", EdgeType.BRANCH, {}))
            elif field == "Commerce":
                options.append((NodeType.JOB_ROLE, "Accountant", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "M.Com", EdgeType.BRANCH, {}))
            elif field == "Management":
                options.append((NodeType.JOB_ROLE, "Business Analyst", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "MBA", EdgeType.BRANCH, {}))
            elif field == "Computer Applications":
                options.append((NodeType.JOB_ROLE, "Software Engineer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "MCA", EdgeType.BRANCH, {}))
            elif field == "Medicine":
                options.append((NodeType.JOB_ROLE, "Medical Officer", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EDUCATION, "MD", EdgeType.BRANCH, {}))
            elif field == "Pharmacy":
                options.append((NodeType.JOB_ROLE, "Pharmacist", EdgeType.NEXT_STEP, {}))
            # Generic exam options
            options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {}))  # MBA
            options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
        # Postgraduate -> advanced jobs, PhD
        elif title in self.taxonomies.POSTGRAD_DEGREES:
            if "M.Tech" in title:
                options.append((NodeType.JOB_ROLE, "Senior Engineer", EdgeType.NEXT_STEP, {}))
            elif title == "MCA":
                options.append((NodeType.JOB_ROLE, "Software Engineer", EdgeType.NEXT_STEP, {}))
            elif title == "MBA":
                options.append((NodeType.JOB_ROLE, "Product Manager", EdgeType.NEXT_STEP, {}))
            elif title == "MD":
                options.append((NodeType.JOB_ROLE, "Cardiologist", EdgeType.NEXT_STEP, {}))
        return options

    def _exam_next_steps(self, exam_node: Node) -> List[Tuple]:
        title = exam_node.title
        options = []
        if title == "JEE Main":
            options.append((NodeType.EDUCATION, "B.Tech CSE", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "B.Tech ECE", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "B.Tech Mechanical", EdgeType.BRANCH, {}))
        elif title == "NEET":
            options.append((NodeType.EDUCATION, "MBBS", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.EDUCATION, "BDS", EdgeType.BRANCH, {}))
            options.append((NodeType.EDUCATION, "BAMS", EdgeType.BRANCH, {}))
        elif title == "GATE":
            options.append((NodeType.EDUCATION, "M.Tech CSE", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.JOB_ROLE, "PSU Engineer", EdgeType.BRANCH, {}))
        elif title == "CAT":
            options.append((NodeType.EDUCATION, "MBA", EdgeType.NEXT_STEP, {}))
        elif title == "UPSC CSE":
            options.append((NodeType.JOB_ROLE, "IAS Officer", EdgeType.NEXT_STEP, {}))
            options.append((NodeType.JOB_ROLE, "IPS Officer", EdgeType.BRANCH, {}))
        elif title == "CLAT":
            options.append((NodeType.EDUCATION, "LLB", EdgeType.NEXT_STEP, {}))
        elif title == "CA Foundation":
            options.append((NodeType.CERTIFICATION, "Chartered Accountant", EdgeType.NEXT_STEP, {}))
        return options

    def _job_role_next_steps(self, job_node: Node) -> List[Tuple]:
        title = job_node.title
        options = []
        # Define progression hierarchy
        progression = {
            "Junior Software Engineer": "Software Engineer",
            "Software Engineer": "Senior Software Engineer",
            "Senior Software Engineer": "Tech Lead",
            "Tech Lead": "Engineering Manager",
            "Engineering Manager": "Director Engineering",
            "Director Engineering": "VP Engineering",
            "VP Engineering": "CTO",
            "CTO": "Entrepreneur",
            "Data Analyst": "Data Scientist",
            "Data Scientist": "ML Engineer",
            "ML Engineer": "AI Research Scientist",
            "Medical Officer": "General Physician",
            "General Physician": "Cardiologist",
            "Mechanical Engineer": "Senior Mechanical Engineer",
            "Civil Engineer": "Senior Civil Engineer",
            "Accountant": "Chartered Accountant",
            "Business Analyst": "Product Manager",
            "IAS Officer": "Cabinet Secretary",
        }
        if title in progression:
            next_title = progression[title]
            options.append((NodeType.JOB_ROLE, next_title, EdgeType.NEXT_STEP, {"transition_difficulty": 5}))
        # Branch to entrepreneurship, consulting, freelancing after senior level
        if "Senior" in title or "Manager" in title or "Lead" in title:
            options.append((NodeType.JOB_ROLE, "Freelancer", EdgeType.BRANCH, {}))
            options.append((NodeType.JOB_ROLE, "Consultant", EdgeType.BRANCH, {}))
            options.append((NodeType.JOB_ROLE, "Entrepreneur", EdgeType.BRANCH, {}))
        # Add exam options for govt jobs
        options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {}))
        options.append((NodeType.EXAM, "SSC CGL", EdgeType.BRANCH, {}))
        return options

    def _certification_next_steps(self, cert_node: Node) -> List[Tuple]:
        return []  # Certifications lead to job roles, already handled.

    def _add_enrichment_edges(self, node: Node):
        """Add edges for skills required, companies that hire for the role, etc."""
        # If job role, connect to required skills and typical companies
        if node.node_type == NodeType.JOB_ROLE:
            role_skills_map = {
                "Software Engineer": ["Python", "Java", "SQL", "AWS"],
                "Data Scientist": ["Python", "Machine Learning", "SQL"],
                "Accountant": ["Excel", "Tally", "Financial Modeling"],
                "Medical Officer": ["Clinical Knowledge", "Communication"],
                "IAS Officer": ["Leadership", "Public Policy"],
            }
            skills = role_skills_map.get(node.title, [])
            for skill_name in skills:
                skill_node = self._get_or_create_node(skill_name, NodeType.SKILL)
                edge = self._add_edge(skill_node, node, EdgeType.REQUIRES_SKILL)
                if edge:
                    self.writer.write_edge(edge)  # type: ignore
            # Companies
            typical_companies = {
                "Software Engineer": ["TCS", "Infosys", "Google India", "Microsoft India", "Flipkart"],
                "Data Scientist": ["Amazon India", "Flipkart", "Zomato"],
                "Mechanical Engineer": ["Tata Motors", "Mahindra & Mahindra", "L&T"],
            }
            companies = typical_companies.get(node.title, [])
            for comp_name in companies:
                comp_node = self._get_or_create_node(comp_name, NodeType.COMPANY)
                edge = self._add_edge(node, comp_node, EdgeType.CAN_WORK_AT)
                if edge:
                    self.writer.write_edge(edge)  # type: ignore


# ===========================================================================
# Main Orchestrator
# ===========================================================================
def main():
    config = GeneratorConfig(
        output_dir="./career_graph_output",
        checkpoint_file="./career_checkpoint.json",
        random_seed=42,
        max_total_paths=20000,  # for demonstration, increase for production
        max_nodes=500000,
        max_edges=1000000,
    )
    random.seed(config.random_seed)

    taxonomies = Taxonomies()
    validator = TransitionValidator()

    generator = CareerGraphGenerator(config, taxonomies, validator)
    generator.generate()


if __name__ == "__main__":
    main()