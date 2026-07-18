#!/usr/bin/env python3
"""
Indian Career Intelligence Platform - Knowledge Graph Generator v2.0
Production-grade, resumable, deterministic, duplicate-safe generator.
Generates millions of structured career direction nodes and edges as a directed graph.

Architecture:
    - Taxonomies: Ground-truth curated data for Indian education, exams, roles, skills, etc.
    - NodeFactory: Deterministic node creation with unique IDs.
    - EdgeBuilder: Builds typed relationships between nodes.
    - TransitionValidator: Realism constraints preventing impossible career moves.
    - CareerGraphGenerator: Procedural graph expansion with branching, enrichment, and
      streaming multi-format output.
    - DeduplicationTracker: Bloom filter or set-based dedup.
    - CheckpointManager: Resumable state via JSON.
    - MultiFormatWriter: Simultaneous JSONL, JSON, CSV, YAML, TXT output.

Usage:
    python career_graph_generator.py

Requirements:
    pip install pyyaml pybloom-live
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import math
import os
import random
import sys
import time
import uuid
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from itertools import chain, combinations, cycle, islice, permutations, product
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

import yaml

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-24s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)
logger = logging.getLogger("CareerGraphGen")


# ============================================================================
# Enums
# ============================================================================
class NodeType(str, Enum):
    EDUCATION = "education"
    CERTIFICATION = "certification"
    EXAM = "exam"
    JOB_ROLE = "job_role"
    SKILL = "skill"
    TOOL = "tool"
    INDUSTRY = "industry"
    COMPANY = "company"
    CAREER_PATH = "career_path"
    INTERNSHIP = "internship"
    PROJECT = "project"
    LEARNING_RESOURCE = "learning_resource"


class EdgeType(str, Enum):
    NEXT_STEP = "next_step"
    BRANCH = "branch"
    LATERAL = "lateral"
    REQUIRES_SKILL = "requires_skill"
    GAINS_SKILL = "gains_skill"
    RECOMMENDS_CERTIFICATION = "recommends_certification"
    CAN_WORK_AT = "can_work_at"
    LEADS_TO = "leads_to"
    ENRICHES = "enriches"
    PREREQUISITE = "prerequisite"
    SPECIALIZES_INTO = "specializes_into"
    PROMOTES_TO = "promotes_to"
    TRANSITIONS_TO = "transitions_to"
    FREELANCE_PATH = "freelance_path"
    ENTREPRENEURSHIP_PATH = "entrepreneurship_path"
    TEACHING_PATH = "teaching_path"
    RESEARCH_PATH = "research_path"
    CONSULTING_PATH = "consulting_path"
    GOVERNMENT_PATH = "government_path"
    REMOTE_PATH = "remote_path"
    INTERNATIONAL_PATH = "international_path"


class EducationLevel(str, Enum):
    SCHOOL = "school"
    DIPLOMA = "diploma"
    CERTIFICATE = "certificate"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"
    POST_DOC = "post_doc"
    PROFESSIONAL = "professional"


class CareerLevel(str, Enum):
    STUDENT = "student"
    INTERN = "intern"
    TRAINEE = "trainee"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    MANAGER = "manager"
    SENIOR_MANAGER = "senior_manager"
    DIRECTOR = "director"
    VP = "vp"
    CXO = "cxo"
    FOUNDER = "founder"
    INDEPENDENT = "independent"


class Sector(str, Enum):
    GOVERNMENT = "government"
    PRIVATE = "private"
    PUBLIC_SECTOR = "public_sector"
    STARTUP = "startup"
    FREELANCE = "freelance"
    CONSULTING = "consulting"
    NGO = "ngo"
    RESEARCH = "research"
    ACADEMIA = "academia"
    DEFENCE = "defence"
    INTERNATIONAL = "international"


class Difficulty(IntEnum):
    TRIVIAL = 1
    EASY = 2
    MODERATE = 3
    CHALLENGING = 4
    HARD = 5
    VERY_HARD = 6
    EXTREME = 7
    ELITE = 8
    LEGENDARY = 9
    IMPOSSIBLE = 10


# ============================================================================
# Configuration
# ============================================================================
@dataclass
class GeneratorConfig:
    """Central configuration controlling generation scope and performance."""

    # Output
    output_dir: str = "./career_graph_output"
    checkpoint_file: str = "./career_checkpoint.json"
    stats_file: str = "./generation_stats.json"
    formats: List[str] = field(
        default_factory=lambda: ["jsonl", "json", "csv", "yaml", "txt"]
    )

    # Generation limits
    max_total_paths: int = 200_000
    max_nodes: int = 5_000_000
    max_edges: int = 10_000_000
    max_path_length: int = 14
    max_branches_per_node: int = 6

    # Randomness
    random_seed: int = 42
    branch_probability: float = 0.35
    lateral_transition_probability: float = 0.15
    enrichment_density: float = 0.7  # fraction of nodes that get full enrichment

    # Deduplication
    duplicate_detection_method: str = "bloom"
    bloom_filter_capacity: int = 10_000_000
    bloom_filter_error_rate: float = 0.0001

    # Resumability
    resume: bool = True
    checkpoint_interval: int = 5_000
    log_interval: int = 10_000
    batch_size: int = 500


# ============================================================================
# Deterministic ID Utilities
# ============================================================================
def deterministic_uuid(seed_string: str) -> str:
    """Generate deterministic UUID v5 based on seed string (DNS namespace)."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_string))


def content_hash(*args: str) -> str:
    """Create a consistent SHA-256 hash for deduplication."""
    return hashlib.sha256("|".join(args).encode("utf-8")).hexdigest()


def short_hash(*args: str) -> str:
    """Shorter hash for display purposes."""
    return content_hash(*args)[:16]


# ============================================================================
# Node Data Class
# ============================================================================
@dataclass
class Node:
    """A vertex in the knowledge graph with rich metadata."""

    node_id: str
    node_type: NodeType
    title: str
    description: str = ""
    category: str = ""
    sub_category: str = ""
    difficulty: int = 3
    education_level: Optional[str] = None
    career_level: Optional[str] = None
    sector: Optional[str] = None
    industry: str = ""
    domain: str = ""
    prerequisites: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    skills_gained: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    recommended_certifications: List[str] = field(default_factory=list)
    estimated_duration_months: Optional[int] = None
    typical_salary_band_inr: str = ""
    entry_salary_inr: str = ""
    senior_salary_inr: str = ""
    growth_score: float = 0.0
    demand_score: float = 0.0
    future_relevance_score: float = 0.0
    automation_risk: float = 0.0
    ai_impact_score: float = 0.0
    remote_work_potential: float = 0.0
    global_opportunity: float = 0.0
    government_opportunity: float = 0.0
    private_opportunity: float = 0.0
    public_sector_opportunity: float = 0.0
    freelance_opportunity: float = 0.0
    entrepreneurship_opportunity: float = 0.0
    women_participation_score: float = 0.0
    rural_accessibility: float = 0.0
    typical_age_range: str = ""
    geographic_hubs: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        return content_hash(
            f"{self.node_type.value}|{self.title.strip().lower()}|{self.education_level or ''}|{self.career_level or ''}|{self.industry}"
        )

    def short_signature(self) -> str:
        return f"{self.node_type.value[:3]}:{self.title[:50]}"


@dataclass
class Edge:
    """A directed relationship between two nodes."""

    edge_id: str = ""
    source_id: str = ""
    destination_id: str = ""
    relationship_type: EdgeType = EdgeType.NEXT_STEP
    label: str = ""
    required_skills: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    required_certifications: List[str] = field(default_factory=list)
    estimated_time_months: Optional[int] = None
    transition_difficulty: int = 3
    probability: float = 0.5
    confidence: float = 0.8
    typical_age_when_transitioned: str = ""
    success_stories: int = 0
    failure_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        return content_hash(
            f"{self.source_id}|{self.destination_id}|{self.relationship_type.value}"
        )

    def __post_init__(self):
        if not self.edge_id:
            self.edge_id = deterministic_uuid(self.signature())


# ============================================================================
# Taxonomies — Ground Truth for Indian Career Ecosystem
# ============================================================================
class Taxonomies:
    """
    Curated, research-grade taxonomy of the Indian education, exam,
    certification, role, skill, company, and industry ecosystems.
    Every entry reflects real options available in India.
    """

    # ── School Streams ────────────────────────────────────────────────
    SCHOOL_STREAMS: ClassVar[Dict[str, Dict]] = {
        "10th Standard": {
            "level": EducationLevel.SCHOOL,
            "next": [
                "11th Science (PCM)",
                "11th Science (PCB)",
                "11th Commerce",
                "11th Arts/Humanities",
                "ITI Electrician",
                "ITI Fitter",
                "ITI Welder",
                "Diploma in Mechanical Engineering",
                "Diploma in Civil Engineering",
                "Diploma in Computer Science",
                "Diploma in Electrical Engineering",
                "Diploma in Electronics & Communication",
            ],
        },
        "11th Science (PCM)": {
            "level": EducationLevel.SCHOOL,
            "subjects": ["Physics", "Chemistry", "Mathematics", "English", "CS/PE"],
        },
        "11th Science (PCB)": {
            "level": EducationLevel.SCHOOL,
            "subjects": ["Physics", "Chemistry", "Biology", "English", "Biotechnology/PE"],
        },
        "11th Commerce": {
            "level": EducationLevel.SCHOOL,
            "subjects": ["Accountancy", "Business Studies", "Economics", "English", "Mathematics/Informatics"],
        },
        "11th Arts/Humanities": {
            "level": EducationLevel.SCHOOL,
            "subjects": ["History", "Political Science", "Sociology", "English", "Economics/Psychology"],
        },
        "12th PCM": {
            "level": EducationLevel.SCHOOL,
            "exams": ["JEE Main", "JEE Advanced", "BITSAT", "VITEEE", "SRMJEEE", "COMEDK", "MHT CET", "WBJEE", "UPSEE"],
        },
        "12th PCB": {
            "level": EducationLevel.SCHOOL,
            "exams": ["NEET UG", "AIIMS", "JIPMER", "State PMT", "ICAR AIEEA"],
        },
        "12th Commerce": {
            "level": EducationLevel.SCHOOL,
            "exams": ["CA Foundation", "CS Foundation", "CMA Foundation", "CUET", "IPMAT"],
        },
        "12th Arts/Humanities": {
            "level": EducationLevel.SCHOOL,
            "exams": ["CLAT", "AILET", "NIFT Entrance", "NID DAT", "UCEED", "CUET"],
        },
    }

    # ── ITI Trades ────────────────────────────────────────────────────
    ITI_TRADES: ClassVar[List[str]] = [
        "ITI Electrician",
        "ITI Fitter",
        "ITI Welder",
        "ITI Machinist",
        "ITI Turner",
        "ITI Mechanic (Motor Vehicle)",
        "ITI Diesel Mechanic",
        "ITI Plumber",
        "ITI Carpenter",
        "ITI Wireman",
        "ITI COPA",
        "ITI Stenographer",
        "ITI Draughtsman (Civil)",
        "ITI Draughtsman (Mechanical)",
        "ITI Electronic Mechanic",
        "ITI Instrument Mechanic",
        "ITI Refrigeration & AC",
        "ITI Surveyor",
    ]

    # ── Diploma Programmes ────────────────────────────────────────────
    DIPLOMA_PROGRAMMES: ClassVar[List[str]] = [
        "Diploma in Mechanical Engineering",
        "Diploma in Civil Engineering",
        "Diploma in Computer Science & Engineering",
        "Diploma in Electrical Engineering",
        "Diploma in Electronics & Communication Engineering",
        "Diploma in Automobile Engineering",
        "Diploma in Chemical Engineering",
        "Diploma in Textile Engineering",
        "Diploma in Mining Engineering",
        "Diploma in Metallurgical Engineering",
        "Diploma in Agricultural Engineering",
        "Diploma in Food Technology",
        "Diploma in Plastic Technology",
        "Diploma in Printing Technology",
        "Diploma in Interior Design",
        "Diploma in Fashion Design",
        "Diploma in Hotel Management",
        "Diploma in Pharmacy",
        "Diploma in Medical Lab Technology (DMLT)",
        "Diploma in Radiography",
        "Diploma in Nursing (GNM)",
        "Diploma in Elementary Education (D.El.Ed)",
    ]

    # ── Undergraduate Degrees ─────────────────────────────────────────
    UNDERGRAD_DEGREES: ClassVar[Dict[str, Dict]] = {
        # Engineering
        "B.Tech Computer Science & Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Computer Science",
            "entrance_exams": ["JEE Main", "JEE Advanced", "BITSAT", "VITEEE", "SRMJEEE"],
            "avg_fee_range": "4-20 Lakhs",
        },
        "B.Tech Information Technology": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Information Technology",
        },
        "B.Tech Electronics & Communication": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Electronics",
        },
        "B.Tech Electrical Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Electrical",
        },
        "B.Tech Mechanical Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Mechanical",
        },
        "B.Tech Civil Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Civil",
        },
        "B.Tech Chemical Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Chemical",
        },
        "B.Tech Aerospace Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Aerospace",
        },
        "B.Tech Biotechnology": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Biotechnology",
        },
        "B.Tech Agricultural Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Agriculture",
        },
        "B.Tech Artificial Intelligence & ML": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "AI/ML",
        },
        "B.Tech Data Science": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Data Science",
        },
        "B.Tech Robotics": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Robotics",
        },
        "B.Tech Petroleum Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Petroleum",
        },
        "B.Tech Textile Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Textile",
        },
        "B.Tech Mining Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Mining",
        },
        "B.Tech Metallurgical Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Metallurgy",
        },
        "B.Tech Environmental Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Environment",
        },
        "B.Tech Marine Engineering": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Marine",
        },
        "B.Tech Food Technology": {
            "duration_years": 4,
            "domain": "Engineering",
            "field": "Food Tech",
        },
        # Sciences
        "B.Sc Physics": {"duration_years": 3, "domain": "Science", "field": "Physics"},
        "B.Sc Chemistry": {"duration_years": 3, "domain": "Science", "field": "Chemistry"},
        "B.Sc Mathematics": {"duration_years": 3, "domain": "Science", "field": "Mathematics"},
        "B.Sc Statistics": {"duration_years": 3, "domain": "Science", "field": "Statistics"},
        "B.Sc Computer Science": {"duration_years": 3, "domain": "Science", "field": "CS"},
        "B.Sc Information Technology": {"duration_years": 3, "domain": "Science", "field": "IT"},
        "B.Sc Biotechnology": {"duration_years": 3, "domain": "Science", "field": "Biotech"},
        "B.Sc Microbiology": {"duration_years": 3, "domain": "Science", "field": "Microbiology"},
        "B.Sc Biochemistry": {"duration_years": 3, "domain": "Science", "field": "Biochemistry"},
        "B.Sc Environmental Science": {"duration_years": 3, "domain": "Science", "field": "Environment"},
        "B.Sc Geology": {"duration_years": 3, "domain": "Science", "field": "Geology"},
        "B.Sc Agriculture": {"duration_years": 4, "domain": "Science", "field": "Agriculture"},
        "B.Sc Nursing": {"duration_years": 4, "domain": "Science", "field": "Nursing"},
        "B.Sc Hospitality & Hotel Administration": {"duration_years": 3, "domain": "Science", "field": "Hospitality"},
        "B.Sc Animation & Multimedia": {"duration_years": 3, "domain": "Science", "field": "Animation"},
        "B.Sc Forensic Science": {"duration_years": 3, "domain": "Science", "field": "Forensic"},
        # Commerce & Management
        "B.Com": {"duration_years": 3, "domain": "Commerce", "field": "General"},
        "B.Com (Hons)": {"duration_years": 3, "domain": "Commerce", "field": "Honours"},
        "B.Com (Accounting & Finance)": {"duration_years": 3, "domain": "Commerce", "field": "Accounting"},
        "BBA": {"duration_years": 3, "domain": "Management", "field": "General"},
        "BBA (Finance)": {"duration_years": 3, "domain": "Management", "field": "Finance"},
        "BBA (Marketing)": {"duration_years": 3, "domain": "Management", "field": "Marketing"},
        "BBA (HR)": {"duration_years": 3, "domain": "Management", "field": "HR"},
        "BBA (International Business)": {"duration_years": 3, "domain": "Management", "field": "IB"},
        "BMS": {"duration_years": 3, "domain": "Management", "field": "Management Studies"},
        "BBA LLB": {"duration_years": 5, "domain": "Law", "field": "Integrated Law"},
        # Computer Applications
        "BCA": {"duration_years": 3, "domain": "Computer Applications", "field": "General"},
        "BCA (Data Science)": {"duration_years": 3, "domain": "Computer Applications", "field": "Data Science"},
        "BCA (AI & ML)": {"duration_years": 3, "domain": "Computer Applications", "field": "AI/ML"},
        # Arts & Humanities
        "BA Economics": {"duration_years": 3, "domain": "Arts", "field": "Economics"},
        "BA English": {"duration_years": 3, "domain": "Arts", "field": "English"},
        "BA Political Science": {"duration_years": 3, "domain": "Arts", "field": "Pol Science"},
        "BA History": {"duration_years": 3, "domain": "Arts", "field": "History"},
        "BA Sociology": {"duration_years": 3, "domain": "Arts", "field": "Sociology"},
        "BA Psychology": {"duration_years": 3, "domain": "Arts", "field": "Psychology"},
        "BA Geography": {"duration_years": 3, "domain": "Arts", "field": "Geography"},
        "BA Journalism & Mass Communication": {"duration_years": 3, "domain": "Arts", "field": "Journalism"},
        "BA LLB": {"duration_years": 5, "domain": "Law", "field": "Integrated Law"},
        "BA Fine Arts": {"duration_years": 3, "domain": "Arts", "field": "Fine Arts"},
        # Professional
        "MBBS": {"duration_years": 5.5, "domain": "Medicine", "field": "Allopathy"},
        "BDS": {"duration_years": 5, "domain": "Medicine", "field": "Dental"},
        "BAMS": {"duration_years": 5.5, "domain": "Medicine", "field": "Ayurveda"},
        "BHMS": {"duration_years": 5.5, "domain": "Medicine", "field": "Homeopathy"},
        "BUMS": {"duration_years": 5.5, "domain": "Medicine", "field": "Unani"},
        "B.Pharma": {"duration_years": 4, "domain": "Pharmacy", "field": "General"},
        "B.Arch": {"duration_years": 5, "domain": "Architecture", "field": "General"},
        "B.Des": {"duration_years": 4, "domain": "Design", "field": "General"},
        "BFA": {"duration_years": 4, "domain": "Fine Arts", "field": "General"},
        "BPT (Physiotherapy)": {"duration_years": 4.5, "domain": "Healthcare", "field": "Physiotherapy"},
        "BOT (Occupational Therapy)": {"duration_years": 4.5, "domain": "Healthcare", "field": "Occupational Therapy"},
        "BVSc & AH": {"duration_years": 5.5, "domain": "Veterinary", "field": "Veterinary Science"},
        "LLB": {"duration_years": 3, "domain": "Law", "field": "Law"},
        "B.Ed": {"duration_years": 2, "domain": "Education", "field": "Teaching"},
        "B.Sc LLB": {"duration_years": 5, "domain": "Law", "field": "Integrated Law"},
    }

    # ── Postgraduate Degrees ──────────────────────────────────────────
    POSTGRAD_DEGREES: ClassVar[Dict[str, Dict]] = {
        "M.Tech CSE": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech VLSI Design": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech Structural Engineering": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech Thermal Engineering": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech Power Systems": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech AI & ML": {"duration_years": 2, "domain": "Engineering"},
        "M.Tech Robotics": {"duration_years": 2, "domain": "Engineering"},
        "M.Sc Data Science": {"duration_years": 2, "domain": "Science"},
        "M.Sc Artificial Intelligence": {"duration_years": 2, "domain": "Science"},
        "M.Sc Physics": {"duration_years": 2, "domain": "Science"},
        "M.Sc Chemistry": {"duration_years": 2, "domain": "Science"},
        "M.Sc Mathematics": {"duration_years": 2, "domain": "Science"},
        "M.Sc Statistics": {"duration_years": 2, "domain": "Science"},
        "M.Sc Biotechnology": {"duration_years": 2, "domain": "Science"},
        "MCA": {"duration_years": 2, "domain": "Computer Applications"},
        "MBA": {"duration_years": 2, "domain": "Management"},
        "MBA Finance": {"duration_years": 2, "domain": "Management"},
        "MBA Marketing": {"duration_years": 2, "domain": "Management"},
        "MBA HR": {"duration_years": 2, "domain": "Management"},
        "MBA Operations": {"duration_years": 2, "domain": "Management"},
        "MBA Business Analytics": {"duration_years": 2, "domain": "Management"},
        "MBA Entrepreneurship": {"duration_years": 2, "domain": "Management"},
        "M.Com": {"duration_years": 2, "domain": "Commerce"},
        "MA Economics": {"duration_years": 2, "domain": "Arts"},
        "MA English": {"duration_years": 2, "domain": "Arts"},
        "MA Psychology": {"duration_years": 2, "domain": "Arts"},
        "MA Political Science": {"duration_years": 2, "domain": "Arts"},
        "MA Sociology": {"duration_years": 2, "domain": "Arts"},
        "MA Journalism": {"duration_years": 2, "domain": "Arts"},
        "MA Public Administration": {"duration_years": 2, "domain": "Arts"},
        "M.Pharma": {"duration_years": 2, "domain": "Pharmacy"},
        "MD General Medicine": {"duration_years": 3, "domain": "Medicine"},
        "MD Pediatrics": {"duration_years": 3, "domain": "Medicine"},
        "MD Radiology": {"duration_years": 3, "domain": "Medicine"},
        "MS General Surgery": {"duration_years": 3, "domain": "Medicine"},
        "MS Orthopedics": {"duration_years": 3, "domain": "Medicine"},
        "M.Arch": {"duration_years": 2, "domain": "Architecture"},
        "M.Des": {"duration_years": 2, "domain": "Design"},
        "LLM": {"duration_years": 1, "domain": "Law"},
        "M.Ed": {"duration_years": 2, "domain": "Education"},
        "MPT": {"duration_years": 2, "domain": "Healthcare"},
        "PhD": {"duration_years": 5, "domain": "Research"},
        "Post Doc": {"duration_years": 2, "domain": "Research"},
    }

    # ── Competitive & Entrance Exams ──────────────────────────────────
    EXAMS: ClassVar[Dict[str, Dict]] = {
        # Engineering
        "JEE Main": {"category": "engineering_ug", "conducted_by": "NTA", "attempts_per_year": 2},
        "JEE Advanced": {"category": "engineering_ug", "conducted_by": "IIT", "attempts_per_year": 1},
        "BITSAT": {"category": "engineering_ug", "conducted_by": "BITS Pilani", "attempts_per_year": 1},
        "VITEEE": {"category": "engineering_ug", "conducted_by": "VIT", "attempts_per_year": 1},
        "SRMJEEE": {"category": "engineering_ug", "conducted_by": "SRM", "attempts_per_year": 1},
        "COMEDK": {"category": "engineering_ug", "conducted_by": "COMEDK", "attempts_per_year": 1},
        "MHT CET": {"category": "engineering_ug", "conducted_by": "Maharashtra State", "attempts_per_year": 1},
        "WBJEE": {"category": "engineering_ug", "conducted_by": "West Bengal", "attempts_per_year": 1},
        # Medical
        "NEET UG": {"category": "medical_ug", "conducted_by": "NTA", "attempts_per_year": 1},
        "AIIMS PG": {"category": "medical_pg", "conducted_by": "AIIMS", "attempts_per_year": 2},
        "NEET PG": {"category": "medical_pg", "conducted_by": "NBE", "attempts_per_year": 1},
        "NIMHANS PG": {"category": "medical_pg", "conducted_by": "NIMHANS", "attempts_per_year": 1},
        # Management
        "CAT": {"category": "management", "conducted_by": "IIMs", "attempts_per_year": 1},
        "XAT": {"category": "management", "conducted_by": "XLRI", "attempts_per_year": 1},
        "NMAT": {"category": "management", "conducted_by": "NMIMS", "attempts_per_year": 1},
        "SNAP": {"category": "management", "conducted_by": "Symbiosis", "attempts_per_year": 1},
        "CMAT": {"category": "management", "conducted_by": "NTA", "attempts_per_year": 1},
        "GMAT": {"category": "management_international", "conducted_by": "GMAC", "attempts_per_year": "multiple"},
        "IPMAT": {"category": "management_ug", "conducted_by": "IIM Indore", "attempts_per_year": 1},
        # Engineering PG
        "GATE": {"category": "engineering_pg", "conducted_by": "IITs", "attempts_per_year": 1},
        "ESE": {"category": "engineering_services", "conducted_by": "UPSC", "attempts_per_year": 1},
        # Civil Services
        "UPSC CSE": {"category": "civil_services", "conducted_by": "UPSC", "attempts_per_year": 1},
        "UPSC IFS": {"category": "forest_services", "conducted_by": "UPSC", "attempts_per_year": 1},
        "SSC CGL": {"category": "government_jobs", "conducted_by": "SSC", "attempts_per_year": 1},
        "SSC CHSL": {"category": "government_jobs", "conducted_by": "SSC", "attempts_per_year": 1},
        "SSC MTS": {"category": "government_jobs", "conducted_by": "SSC", "attempts_per_year": 1},
        "IBPS PO": {"category": "banking", "conducted_by": "IBPS", "attempts_per_year": 1},
        "IBPS Clerk": {"category": "banking", "conducted_by": "IBPS", "attempts_per_year": 1},
        "SBI PO": {"category": "banking", "conducted_by": "SBI", "attempts_per_year": 1},
        "SBI Clerk": {"category": "banking", "conducted_by": "SBI", "attempts_per_year": 1},
        "RBI Grade B": {"category": "banking", "conducted_by": "RBI", "attempts_per_year": 1},
        "RRB NTPC": {"category": "railways", "conducted_by": "RRB", "attempts_per_year": 1},
        "RRB Group D": {"category": "railways", "conducted_by": "RRB", "attempts_per_year": 1},
        "RRB JE": {"category": "railways", "conducted_by": "RRB", "attempts_per_year": 1},
        "DRDO CEPTAM": {"category": "defence_research", "conducted_by": "DRDO", "attempts_per_year": 1},
        "ISRO Scientist": {"category": "space", "conducted_by": "ISRO", "attempts_per_year": 1},
        "BARC OCES": {"category": "nuclear", "conducted_by": "BARC", "attempts_per_year": 1},
        "CDS": {"category": "defence", "conducted_by": "UPSC", "attempts_per_year": 2},
        "NDA": {"category": "defence", "conducted_by": "UPSC", "attempts_per_year": 2},
        "AFCAT": {"category": "airforce", "conducted_by": "IAF", "attempts_per_year": 2},
        "INET": {"category": "navy", "conducted_by": "Indian Navy", "attempts_per_year": 1},
        # Law
        "CLAT": {"category": "law_ug", "conducted_by": "NLUs", "attempts_per_year": 1},
        "AILET": {"category": "law_ug", "conducted_by": "NLU Delhi", "attempts_per_year": 1},
        "LSAT India": {"category": "law_ug", "conducted_by": "LSAC", "attempts_per_year": 1},
        "AIBE": {"category": "law_bar", "conducted_by": "BCI", "attempts_per_year": 1},
        # Design & Architecture
        "NIFT Entrance": {"category": "design", "conducted_by": "NIFT", "attempts_per_year": 1},
        "NID DAT": {"category": "design", "conducted_by": "NID", "attempts_per_year": 1},
        "UCEED": {"category": "design_ug", "conducted_by": "IITs", "attempts_per_year": 1},
        "CEED": {"category": "design_pg", "conducted_by": "IITs", "attempts_per_year": 1},
        "NATA": {"category": "architecture", "conducted_by": "COA", "attempts_per_year": 2},
        # Professional
        "CA Foundation": {"category": "chartered_accountancy", "conducted_by": "ICAI", "attempts_per_year": 2},
        "CA Intermediate": {"category": "chartered_accountancy", "conducted_by": "ICAI", "attempts_per_year": 2},
        "CA Final": {"category": "chartered_accountancy", "conducted_by": "ICAI", "attempts_per_year": 2},
        "CS Foundation": {"category": "company_secretary", "conducted_by": "ICSI", "attempts_per_year": 2},
        "CMA Foundation": {"category": "cost_accountancy", "conducted_by": "ICMAI", "attempts_per_year": 2},
        "CFA Level 1": {"category": "finance_international", "conducted_by": "CFA Institute", "attempts_per_year": 2},
        "FRM": {"category": "risk_management", "conducted_by": "GARP", "attempts_per_year": 2},
        # Academic
        "UGC NET": {"category": "academic", "conducted_by": "NTA", "attempts_per_year": 2},
        "CSIR NET": {"category": "research", "conducted_by": "NTA", "attempts_per_year": 2},
        "GATE": {"category": "engineering_pg", "conducted_by": "IITs", "attempts_per_year": 1},
        "JEST": {"category": "research_physics", "conducted_by": "TIFR", "attempts_per_year": 1},
        "TIFR GS": {"category": "research", "conducted_by": "TIFR", "attempts_per_year": 1},
        "IIT JAM": {"category": "science_pg", "conducted_by": "IITs", "attempts_per_year": 1},
        # Language
        "IELTS": {"category": "english_proficiency", "conducted_by": "British Council", "attempts_per_year": "multiple"},
        "TOEFL": {"category": "english_proficiency", "conducted_by": "ETS", "attempts_per_year": "multiple"},
        "GRE": {"category": "international_ms", "conducted_by": "ETS", "attempts_per_year": "multiple"},
    }

    # ── Certifications ────────────────────────────────────────────────
    CERTIFICATIONS: ClassVar[List[str]] = [
        # IT & Cloud
        "AWS Solutions Architect Associate",
        "AWS Developer Associate",
        "AWS SysOps Administrator",
        "Azure Administrator (AZ-104)",
        "Azure Solutions Architect (AZ-305)",
        "GCP Professional Cloud Architect",
        "Google Associate Cloud Engineer",
        "Certified Kubernetes Administrator (CKA)",
        "Certified Kubernetes Application Developer (CKAD)",
        "Docker Certified Associate",
        "HashiCorp Certified Terraform Associate",
        "Red Hat Certified Engineer (RHCE)",
        "CompTIA A+",
        "CompTIA Network+",
        "CompTIA Security+",
        "Cisco CCNA",
        "Cisco CCNP",
        "VMware VCP",
        # Cyber Security
        "Certified Ethical Hacker (CEH)",
        "CISSP",
        "CISA",
        "CISM",
        "CompTIA Security+",
        "OSCP",
        "ISO 27001 Lead Auditor",
        # Data & AI
        "Google Professional Data Engineer",
        "AWS Certified Data Analytics",
        "Databricks Certified Data Engineer",
        "Microsoft Certified: Azure Data Scientist",
        "TensorFlow Developer Certificate",
        "NVIDIA DLI Certificate",
        "Certified Analytics Professional (CAP)",
        # Project Management
        "PMP",
        "PRINCE2",
        "Certified Scrum Master (CSM)",
        "SAFe Agilist",
        "PMI-ACP",
        "CAPM",
        # Quality & Process
        "Six Sigma Green Belt",
        "Six Sigma Black Belt",
        "Lean Six Sigma",
        "ISO 9001 Lead Auditor",
        "ITIL 4 Foundation",
        # Finance
        "CFA",
        "FRM",
        "CPA",
        "ACCA",
        "CMA (US)",
        "Financial Modeling & Valuation Analyst (FMVA)",
        "NISM Series Certifications",
        "NCFM Modules",
        # Digital Marketing
        "Google Digital Marketing Certification",
        "Google Analytics Certification",
        "HubSpot Content Marketing",
        "Facebook Blueprint",
        # Indian Government Certifications
        "NIELIT O Level",
        "NIELIT A Level",
        "NIELIT B Level",
        "NIELIT C Level",
        "DOEACC CCC",
        # Healthcare
        "BLS (Basic Life Support)",
        "ACLS",
        "PALS",
        "ICAI Certificate Course on ICDS",
        "Nursing Registration",
    ]

    # ── Job Roles (hierarchical) ──────────────────────────────────────
    JOB_ROLES: ClassVar[Dict[str, Dict]] = {
        # ── Software Engineering ──
        "Software Engineering Intern": {"level": CareerLevel.INTERN, "domain": "IT", "salary_band": "1-3 LPA"},
        "Junior Software Engineer": {"level": CareerLevel.JUNIOR, "domain": "IT", "salary_band": "3-6 LPA"},
        "Software Engineer": {"level": CareerLevel.MID, "domain": "IT", "salary_band": "6-15 LPA"},
        "Senior Software Engineer": {"level": CareerLevel.SENIOR, "domain": "IT", "salary_band": "15-30 LPA"},
        "Staff Software Engineer": {"level": CareerLevel.PRINCIPAL, "domain": "IT", "salary_band": "30-50 LPA"},
        "Tech Lead": {"level": CareerLevel.LEAD, "domain": "IT", "salary_band": "25-45 LPA"},
        "Engineering Manager": {"level": CareerLevel.MANAGER, "domain": "IT", "salary_band": "35-60 LPA"},
        "Senior Engineering Manager": {"level": CareerLevel.SENIOR_MANAGER, "domain": "IT", "salary_band": "50-80 LPA"},
        "Director of Engineering": {"level": CareerLevel.DIRECTOR, "domain": "IT", "salary_band": "70 LPA - 1.2 Cr"},
        "VP Engineering": {"level": CareerLevel.VP, "domain": "IT", "salary_band": "1-2 Cr"},
        "CTO": {"level": CareerLevel.CXO, "domain": "IT", "salary_band": "1.5-5 Cr"},
        # ── Data & AI ──
        "Data Analyst Intern": {"level": CareerLevel.INTERN, "domain": "Data", "salary_band": "1-2 LPA"},
        "Junior Data Analyst": {"level": CareerLevel.JUNIOR, "domain": "Data", "salary_band": "3-6 LPA"},
        "Data Analyst": {"level": CareerLevel.MID, "domain": "Data", "salary_band": "6-12 LPA"},
        "Senior Data Analyst": {"level": CareerLevel.SENIOR, "domain": "Data", "salary_band": "12-20 LPA"},
        "Data Scientist": {"level": CareerLevel.MID, "domain": "Data", "salary_band": "10-20 LPA"},
        "Senior Data Scientist": {"level": CareerLevel.SENIOR, "domain": "Data", "salary_band": "20-40 LPA"},
        "ML Engineer": {"level": CareerLevel.MID, "domain": "AI/ML", "salary_band": "12-25 LPA"},
        "Senior ML Engineer": {"level": CareerLevel.SENIOR, "domain": "AI/ML", "salary_band": "25-45 LPA"},
        "AI Research Scientist": {"level": CareerLevel.SENIOR, "domain": "AI/ML", "salary_band": "20-50 LPA"},
        "Data Engineering Manager": {"level": CareerLevel.MANAGER, "domain": "Data", "salary_band": "35-60 LPA"},
        "Chief Data Officer": {"level": CareerLevel.CXO, "domain": "Data", "salary_band": "80 LPA - 2 Cr"},
        # ── Cloud & DevOps ──
        "Cloud Support Engineer": {"level": CareerLevel.JUNIOR, "domain": "Cloud", "salary_band": "4-8 LPA"},
        "Cloud Engineer": {"level": CareerLevel.MID, "domain": "Cloud", "salary_band": "8-18 LPA"},
        "Senior Cloud Engineer": {"level": CareerLevel.SENIOR, "domain": "Cloud", "salary_band": "18-35 LPA"},
        "Cloud Architect": {"level": CareerLevel.SENIOR, "domain": "Cloud", "salary_band": "25-50 LPA"},
        "DevOps Engineer": {"level": CareerLevel.MID, "domain": "DevOps", "salary_band": "8-18 LPA"},
        "Senior DevOps Engineer": {"level": CareerLevel.SENIOR, "domain": "DevOps", "salary_band": "18-35 LPA"},
        "DevOps Architect": {"level": CareerLevel.SENIOR, "domain": "DevOps", "salary_band": "25-45 LPA"},
        "Site Reliability Engineer (SRE)": {"level": CareerLevel.MID, "domain": "SRE", "salary_band": "10-22 LPA"},
        "Platform Engineer": {"level": CareerLevel.MID, "domain": "Platform", "salary_band": "12-25 LPA"},
        # ── Cyber Security ──
        "Security Analyst": {"level": CareerLevel.JUNIOR, "domain": "Cybersecurity", "salary_band": "4-8 LPA"},
        "Security Engineer": {"level": CareerLevel.MID, "domain": "Cybersecurity", "salary_band": "8-18 LPA"},
        "Senior Security Engineer": {"level": CareerLevel.SENIOR, "domain": "Cybersecurity", "salary_band": "18-35 LPA"},
        "Security Architect": {"level": CareerLevel.SENIOR, "domain": "Cybersecurity", "salary_band": "25-50 LPA"},
        "Penetration Tester": {"level": CareerLevel.MID, "domain": "Cybersecurity", "salary_band": "8-20 LPA"},
        "CISO": {"level": CareerLevel.CXO, "domain": "Cybersecurity", "salary_band": "60 LPA - 1.5 Cr"},
        # ── Product Management ──
        "Associate Product Manager": {"level": CareerLevel.JUNIOR, "domain": "Product", "salary_band": "6-12 LPA"},
        "Product Manager": {"level": CareerLevel.MID, "domain": "Product", "salary_band": "15-30 LPA"},
        "Senior Product Manager": {"level": CareerLevel.SENIOR, "domain": "Product", "salary_band": "25-45 LPA"},
        "Director of Product": {"level": CareerLevel.DIRECTOR, "domain": "Product", "salary_band": "50-80 LPA"},
        "VP Product": {"level": CareerLevel.VP, "domain": "Product", "salary_band": "80 LPA - 1.5 Cr"},
        "CPO": {"level": CareerLevel.CXO, "domain": "Product", "salary_band": "1-3 Cr"},
        # ── Design ──
        "UI Designer": {"level": CareerLevel.JUNIOR, "domain": "Design", "salary_band": "3-6 LPA"},
        "UX Designer": {"level": CareerLevel.MID, "domain": "Design", "salary_band": "6-15 LPA"},
        "Senior UX Designer": {"level": CareerLevel.SENIOR, "domain": "Design", "salary_band": "15-28 LPA"},
        "Product Designer": {"level": CareerLevel.MID, "domain": "Design", "salary_band": "10-22 LPA"},
        "Design Manager": {"level": CareerLevel.MANAGER, "domain": "Design", "salary_band": "25-45 LPA"},
        "Design Director": {"level": CareerLevel.DIRECTOR, "domain": "Design", "salary_band": "45-70 LPA"},
        # ── Business & Finance ──
        "Business Analyst": {"level": CareerLevel.JUNIOR, "domain": "Business", "salary_band": "4-8 LPA"},
        "Senior Business Analyst": {"level": CareerLevel.MID, "domain": "Business", "salary_band": "8-18 LPA"},
        "Management Consultant": {"level": CareerLevel.MID, "domain": "Consulting", "salary_band": "12-25 LPA"},
        "Strategy Consultant": {"level": CareerLevel.SENIOR, "domain": "Consulting", "salary_band": "20-40 LPA"},
        "Financial Analyst": {"level": CareerLevel.JUNIOR, "domain": "Finance", "salary_band": "4-8 LPA"},
        "Investment Banker": {"level": CareerLevel.MID, "domain": "Finance", "salary_band": "15-35 LPA"},
        "Chartered Accountant": {"level": CareerLevel.MID, "domain": "Finance", "salary_band": "8-20 LPA"},
        "Company Secretary": {"level": CareerLevel.MID, "domain": "Legal", "salary_band": "6-15 LPA"},
        "Cost Accountant": {"level": CareerLevel.MID, "domain": "Finance", "salary_band": "5-12 LPA"},
        "Risk Manager": {"level": CareerLevel.MID, "domain": "Finance", "salary_band": "10-22 LPA"},
        "CFO": {"level": CareerLevel.CXO, "domain": "Finance", "salary_band": "60 LPA - 2 Cr"},
        # ── Marketing & Sales ──
        "Marketing Executive": {"level": CareerLevel.ENTRY, "domain": "Marketing", "salary_band": "2-5 LPA"},
        "Marketing Manager": {"level": CareerLevel.MID, "domain": "Marketing", "salary_band": "8-18 LPA"},
        "Digital Marketing Specialist": {"level": CareerLevel.JUNIOR, "domain": "Marketing", "salary_band": "3-7 LPA"},
        "SEO Specialist": {"level": CareerLevel.JUNIOR, "domain": "Marketing", "salary_band": "3-6 LPA"},
        "Growth Manager": {"level": CareerLevel.MID, "domain": "Marketing", "salary_band": "12-25 LPA"},
        "VP Marketing": {"level": CareerLevel.VP, "domain": "Marketing", "salary_band": "50-90 LPA"},
        "Sales Executive": {"level": CareerLevel.ENTRY, "domain": "Sales", "salary_band": "2-5 LPA"},
        "Sales Manager": {"level": CareerLevel.MID, "domain": "Sales", "salary_band": "8-18 LPA"},
        "Regional Sales Head": {"level": CareerLevel.SENIOR, "domain": "Sales", "salary_band": "18-35 LPA"},
        "VP Sales": {"level": CareerLevel.VP, "domain": "Sales", "salary_band": "40-80 LPA"},
        # ── Human Resources ──
        "HR Executive": {"level": CareerLevel.ENTRY, "domain": "HR", "salary_band": "2-4 LPA"},
        "HR Manager": {"level": CareerLevel.MID, "domain": "HR", "salary_band": "6-15 LPA"},
        "HR Business Partner": {"level": CareerLevel.SENIOR, "domain": "HR", "salary_band": "12-25 LPA"},
        "VP HR": {"level": CareerLevel.VP, "domain": "HR", "salary_band": "40-70 LPA"},
        # ── Operations & Supply Chain ──
        "Operations Executive": {"level": CareerLevel.ENTRY, "domain": "Operations", "salary_band": "2-4 LPA"},
        "Operations Manager": {"level": CareerLevel.MID, "domain": "Operations", "salary_band": "8-18 LPA"},
        "Supply Chain Analyst": {"level": CareerLevel.JUNIOR, "domain": "Supply Chain", "salary_band": "3-6 LPA"},
        "Supply Chain Manager": {"level": CareerLevel.MID, "domain": "Supply Chain", "salary_band": "10-22 LPA"},
        "Logistics Manager": {"level": CareerLevel.MID, "domain": "Logistics", "salary_band": "6-15 LPA"},
        "COO": {"level": CareerLevel.CXO, "domain": "Operations", "salary_band": "60 LPA - 2 Cr"},
        # ── Government & Civil Services ──
        "IAS Officer": {"level": CareerLevel.ENTRY, "domain": "Civil Services", "salary_band": "8-15 LPA"},
        "IPS Officer": {"level": CareerLevel.ENTRY, "domain": "Police", "salary_band": "8-15 LPA"},
        "IFS Officer": {"level": CareerLevel.ENTRY, "domain": "Foreign Service", "salary_band": "10-18 LPA"},
        "IRS Officer": {"level": CareerLevel.ENTRY, "domain": "Revenue", "salary_band": "8-15 LPA"},
        "District Magistrate": {"level": CareerLevel.MID, "domain": "Civil Services", "salary_band": "12-20 LPA"},
        "Joint Secretary": {"level": CareerLevel.SENIOR, "domain": "Civil Services", "salary_band": "18-25 LPA"},
        "Cabinet Secretary": {"level": CareerLevel.CXO, "domain": "Civil Services", "salary_band": "25 LPA"},
        "SSC CGL Officer": {"level": CareerLevel.ENTRY, "domain": "Government", "salary_band": "5-8 LPA"},
        "Bank PO": {"level": CareerLevel.ENTRY, "domain": "Banking", "salary_band": "5-8 LPA"},
        "Bank Manager": {"level": CareerLevel.MID, "domain": "Banking", "salary_band": "10-18 LPA"},
        "RBI Grade B Officer": {"level": CareerLevel.ENTRY, "domain": "Banking", "salary_band": "10-15 LPA"},
        # ── Defence ──
        "Indian Army Officer": {"level": CareerLevel.ENTRY, "domain": "Defence", "salary_band": "7-12 LPA"},
        "Indian Navy Officer": {"level": CareerLevel.ENTRY, "domain": "Defence", "salary_band": "7-12 LPA"},
        "Indian Air Force Officer": {"level": CareerLevel.ENTRY, "domain": "Defence", "salary_band": "7-12 LPA"},
        "Defence Scientist (DRDO)": {"level": CareerLevel.MID, "domain": "Defence Research", "salary_band": "10-18 LPA"},
        "ISRO Scientist": {"level": CareerLevel.MID, "domain": "Space", "salary_band": "12-20 LPA"},
        # ── Healthcare ──
        "Medical Officer": {"level": CareerLevel.ENTRY, "domain": "Medicine", "salary_band": "6-12 LPA"},
        "General Physician": {"level": CareerLevel.MID, "domain": "Medicine", "salary_band": "8-20 LPA"},
        "Surgeon": {"level": CareerLevel.SENIOR, "domain": "Medicine", "salary_band": "15-40 LPA"},
        "Cardiologist": {"level": CareerLevel.SENIOR, "domain": "Medicine", "salary_band": "20-50 LPA"},
        "Pediatrician": {"level": CareerLevel.MID, "domain": "Medicine", "salary_band": "10-25 LPA"},
        "Radiologist": {"level": CareerLevel.MID, "domain": "Medicine", "salary_band": "15-35 LPA"},
        "Dentist": {"level": CareerLevel.MID, "domain": "Dental", "salary_band": "5-15 LPA"},
        "Pharmacist": {"level": CareerLevel.ENTRY, "domain": "Pharmacy", "salary_band": "2-5 LPA"},
        "Nurse": {"level": CareerLevel.ENTRY, "domain": "Nursing", "salary_band": "2-5 LPA"},
        "Physiotherapist": {"level": CareerLevel.ENTRY, "domain": "Healthcare", "salary_band": "3-6 LPA"},
        # ── Legal ──
        "Junior Advocate": {"level": CareerLevel.ENTRY, "domain": "Law", "salary_band": "2-5 LPA"},
        "Advocate": {"level": CareerLevel.MID, "domain": "Law", "salary_band": "5-15 LPA"},
        "Senior Advocate": {"level": CareerLevel.SENIOR, "domain": "Law", "salary_band": "15-40 LPA"},
        "Judge": {"level": CareerLevel.SENIOR, "domain": "Judiciary", "salary_band": "12-25 LPA"},
        "Corporate Lawyer": {"level": CareerLevel.MID, "domain": "Law", "salary_band": "8-20 LPA"},
        # ── Architecture & Construction ──
        "Junior Architect": {"level": CareerLevel.JUNIOR, "domain": "Architecture", "salary_band": "3-5 LPA"},
        "Architect": {"level": CareerLevel.MID, "domain": "Architecture", "salary_band": "5-12 LPA"},
        "Senior Architect": {"level": CareerLevel.SENIOR, "domain": "Architecture", "salary_band": "12-25 LPA"},
        "Civil Engineer": {"level": CareerLevel.JUNIOR, "domain": "Civil", "salary_band": "3-6 LPA"},
        "Senior Civil Engineer": {"level": CareerLevel.MID, "domain": "Civil", "salary_band": "6-15 LPA"},
        "Structural Engineer": {"level": CareerLevel.MID, "domain": "Civil", "salary_band": "8-18 LPA"},
        "Project Manager (Construction)": {"level": CareerLevel.MANAGER, "domain": "Construction", "salary_band": "12-25 LPA"},
        # ── Mechanical & Manufacturing ──
        "Mechanical Engineer": {"level": CareerLevel.JUNIOR, "domain": "Mechanical", "salary_band": "3-6 LPA"},
        "Senior Mechanical Engineer": {"level": CareerLevel.MID, "domain": "Mechanical", "salary_band": "6-15 LPA"},
        "Design Engineer": {"level": CareerLevel.MID, "domain": "Mechanical", "salary_band": "5-12 LPA"},
        "Production Manager": {"level": CareerLevel.MANAGER, "domain": "Manufacturing", "salary_band": "10-22 LPA"},
        "Quality Engineer": {"level": CareerLevel.JUNIOR, "domain": "Quality", "salary_band": "3-6 LPA"},
        "Quality Manager": {"level": CareerLevel.MANAGER, "domain": "Quality", "salary_band": "10-20 LPA"},
        # ── Electrical & Electronics ──
        "Electrical Engineer": {"level": CareerLevel.JUNIOR, "domain": "Electrical", "salary_band": "3-6 LPA"},
        "Senior Electrical Engineer": {"level": CareerLevel.MID, "domain": "Electrical", "salary_band": "6-15 LPA"},
        "Electronics Engineer": {"level": CareerLevel.JUNIOR, "domain": "Electronics", "salary_band": "3-6 LPA"},
        "VLSI Design Engineer": {"level": CareerLevel.MID, "domain": "Semiconductor", "salary_band": "8-20 LPA"},
        "Embedded Systems Engineer": {"level": CareerLevel.MID, "domain": "Electronics", "salary_band": "5-15 LPA"},
        # ── Agriculture ──
        "Agricultural Officer": {"level": CareerLevel.ENTRY, "domain": "Agriculture", "salary_band": "4-7 LPA"},
        "Agricultural Scientist": {"level": CareerLevel.MID, "domain": "Agriculture", "salary_band": "6-12 LPA"},
        "Food Technologist": {"level": CareerLevel.JUNIOR, "domain": "Food Tech", "salary_band": "3-6 LPA"},
        # ── Education & Academia ──
        "School Teacher": {"level": CareerLevel.ENTRY, "domain": "Education", "salary_band": "2-5 LPA"},
        "Assistant Professor": {"level": CareerLevel.ENTRY, "domain": "Academia", "salary_band": "5-8 LPA"},
        "Associate Professor": {"level": CareerLevel.MID, "domain": "Academia", "salary_band": "8-15 LPA"},
        "Professor": {"level": CareerLevel.SENIOR, "domain": "Academia", "salary_band": "12-25 LPA"},
        "Research Scholar": {"level": CareerLevel.ENTRY, "domain": "Research", "salary_band": "3-5 LPA"},
        "Research Scientist": {"level": CareerLevel.MID, "domain": "Research", "salary_band": "6-15 LPA"},
        # ── Media & Creative ──
        "Journalist": {"level": CareerLevel.ENTRY, "domain": "Media", "salary_band": "2-5 LPA"},
        "Senior Journalist": {"level": CareerLevel.MID, "domain": "Media", "salary_band": "5-15 LPA"},
        "Content Writer": {"level": CareerLevel.ENTRY, "domain": "Content", "salary_band": "2-4 LPA"},
        "Content Strategist": {"level": CareerLevel.MID, "domain": "Content", "salary_band": "5-12 LPA"},
        "Graphic Designer": {"level": CareerLevel.ENTRY, "domain": "Design", "salary_band": "2-5 LPA"},
        "Animator": {"level": CareerLevel.JUNIOR, "domain": "Animation", "salary_band": "3-7 LPA"},
        "Video Editor": {"level": CareerLevel.JUNIOR, "domain": "Media", "salary_band": "2-6 LPA"},
        # ── Hospitality ──
        "Hotel Management Trainee": {"level": CareerLevel.TRAINEE, "domain": "Hospitality", "salary_band": "2-4 LPA"},
        "Chef": {"level": CareerLevel.MID, "domain": "Hospitality", "salary_band": "4-12 LPA"},
        "Restaurant Manager": {"level": CareerLevel.MID, "domain": "Hospitality", "salary_band": "5-12 LPA"},
        # ── Telecom ──
        "Telecom Engineer": {"level": CareerLevel.JUNIOR, "domain": "Telecom", "salary_band": "3-6 LPA"},
        "Network Engineer": {"level": CareerLevel.MID, "domain": "Telecom", "salary_band": "5-12 LPA"},
        # ── Renewable Energy ──
        "Solar Energy Engineer": {"level": CareerLevel.JUNIOR, "domain": "Renewable Energy", "salary_band": "3-7 LPA"},
        "Wind Energy Engineer": {"level": CareerLevel.JUNIOR, "domain": "Renewable Energy", "salary_band": "3-7 LPA"},
        "Energy Auditor": {"level": CareerLevel.MID, "domain": "Energy", "salary_band": "5-12 LPA"},
        # ── Gaming ──
        "Game Developer": {"level": CareerLevel.JUNIOR, "domain": "Gaming", "salary_band": "3-8 LPA"},
        "Game Designer": {"level": CareerLevel.MID, "domain": "Gaming", "salary_band": "5-15 LPA"},
        # ── Freelance / Independent ──
        "Freelance Developer": {"level": CareerLevel.INDEPENDENT, "domain": "IT", "salary_band": "varies"},
        "Freelance Designer": {"level": CareerLevel.INDEPENDENT, "domain": "Design", "salary_band": "varies"},
        "Freelance Writer": {"level": CareerLevel.INDEPENDENT, "domain": "Content", "salary_band": "varies"},
        "Freelance Consultant": {"level": CareerLevel.INDEPENDENT, "domain": "Consulting", "salary_band": "varies"},
        "Entrepreneur / Founder": {"level": CareerLevel.FOUNDER, "domain": "Entrepreneurship", "salary_band": "varies"},
        "Startup Co-founder": {"level": CareerLevel.FOUNDER, "domain": "Entrepreneurship", "salary_band": "varies"},
        "Independent Consultant": {"level": CareerLevel.INDEPENDENT, "domain": "Consulting", "salary_band": "varies"},
    }

    # ── Skills Taxonomy ───────────────────────────────────────────────
    SKILLS: ClassVar[Dict[str, Dict]] = {
        # Programming Languages
        "Python": {"category": "Programming Language", "difficulty": 3, "demand": 95},
        "Java": {"category": "Programming Language", "difficulty": 4, "demand": 85},
        "C++": {"category": "Programming Language", "difficulty": 5, "demand": 70},
        "C": {"category": "Programming Language", "difficulty": 4, "demand": 60},
        "JavaScript": {"category": "Programming Language", "difficulty": 3, "demand": 92},
        "TypeScript": {"category": "Programming Language", "difficulty": 3, "demand": 88},
        "Go": {"category": "Programming Language", "difficulty": 3, "demand": 75},
        "Rust": {"category": "Programming Language", "difficulty": 6, "demand": 60},
        "Kotlin": {"category": "Programming Language", "difficulty": 4, "demand": 65},
        "Swift": {"category": "Programming Language", "difficulty": 4, "demand": 55},
        "R": {"category": "Programming Language", "difficulty": 3, "demand": 50},
        "MATLAB": {"category": "Programming Language", "difficulty": 3, "demand": 40},
        "Scala": {"category": "Programming Language", "difficulty": 5, "demand": 35},
        "PHP": {"category": "Programming Language", "difficulty": 2, "demand": 45},
        "Ruby": {"category": "Programming Language", "difficulty": 3, "demand": 30},
        # Web & Frameworks
        "React": {"category": "Frontend Framework", "difficulty": 4, "demand": 90},
        "Angular": {"category": "Frontend Framework", "difficulty": 5, "demand": 70},
        "Vue.js": {"category": "Frontend Framework", "difficulty": 3, "demand": 55},
        "Node.js": {"category": "Backend Framework", "difficulty": 3, "demand": 88},
        "Django": {"category": "Backend Framework", "difficulty": 3, "demand": 72},
        "Flask": {"category": "Backend Framework", "difficulty": 2, "demand": 60},
        "Spring Boot": {"category": "Backend Framework", "difficulty": 5, "demand": 75},
        ".NET": {"category": "Backend Framework", "difficulty": 4, "demand": 60},
        "Laravel": {"category": "Backend Framework", "difficulty": 3, "demand": 40},
        # Database & Storage
        "SQL": {"category": "Database", "difficulty": 2, "demand": 95},
        "PostgreSQL": {"category": "Database", "difficulty": 3, "demand": 80},
        "MySQL": {"category": "Database", "difficulty": 2, "demand": 85},
        "MongoDB": {"category": "Database", "difficulty": 3, "demand": 78},
        "Redis": {"category": "Database", "difficulty": 3, "demand": 65},
        "Elasticsearch": {"category": "Database", "difficulty": 4, "demand": 60},
        "Cassandra": {"category": "Database", "difficulty": 4, "demand": 40},
        "Oracle DB": {"category": "Database", "difficulty": 4, "demand": 55},
        # Cloud & DevOps
        "AWS": {"category": "Cloud Platform", "difficulty": 4, "demand": 95},
        "Microsoft Azure": {"category": "Cloud Platform", "difficulty": 4, "demand": 85},
        "Google Cloud Platform": {"category": "Cloud Platform", "difficulty": 4, "demand": 75},
        "Docker": {"category": "Containerization", "difficulty": 3, "demand": 90},
        "Kubernetes": {"category": "Orchestration", "difficulty": 6, "demand": 88},
        "Terraform": {"category": "IaC", "difficulty": 4, "demand": 80},
        "Ansible": {"category": "Configuration Mgmt", "difficulty": 3, "demand": 65},
        "Jenkins": {"category": "CI/CD", "difficulty": 3, "demand": 70},
        "GitHub Actions": {"category": "CI/CD", "difficulty": 2, "demand": 78},
        "GitLab CI": {"category": "CI/CD", "difficulty": 3, "demand": 60},
        "Prometheus": {"category": "Monitoring", "difficulty": 4, "demand": 65},
        "Grafana": {"category": "Monitoring", "difficulty": 2, "demand": 70},
        # Data Science & AI
        "Machine Learning": {"category": "AI/ML", "difficulty": 6, "demand": 92},
        "Deep Learning": {"category": "AI/ML", "difficulty": 7, "demand": 85},
        "NLP": {"category": "AI/ML", "difficulty": 6, "demand": 78},
        "Computer Vision": {"category": "AI/ML", "difficulty": 7, "demand": 70},
        "TensorFlow": {"category": "ML Framework", "difficulty": 5, "demand": 75},
        "PyTorch": {"category": "ML Framework", "difficulty": 5, "demand": 80},
        "Scikit-learn": {"category": "ML Framework", "difficulty": 3, "demand": 85},
        "Pandas": {"category": "Data Analysis", "difficulty": 2, "demand": 90},
        "NumPy": {"category": "Data Analysis", "difficulty": 3, "demand": 88},
        "Apache Spark": {"category": "Big Data", "difficulty": 5, "demand": 65},
        "Apache Kafka": {"category": "Data Streaming", "difficulty": 4, "demand": 60},
        "Hadoop": {"category": "Big Data", "difficulty": 4, "demand": 45},
        "Tableau": {"category": "BI Tool", "difficulty": 2, "demand": 70},
        "Power BI": {"category": "BI Tool", "difficulty": 2, "demand": 78},
        # Cyber Security
        "Ethical Hacking": {"category": "Security", "difficulty": 6, "demand": 75},
        "Penetration Testing": {"category": "Security", "difficulty": 6, "demand": 72},
        "Network Security": {"category": "Security", "difficulty": 5, "demand": 78},
        "Cloud Security": {"category": "Security", "difficulty": 5, "demand": 80},
        "Cryptography": {"category": "Security", "difficulty": 7, "demand": 55},
        "SIEM": {"category": "Security", "difficulty": 4, "demand": 65},
        # Soft Skills
        "Communication": {"category": "Soft Skill", "difficulty": 2, "demand": 98},
        "Leadership": {"category": "Soft Skill", "difficulty": 5, "demand": 90},
        "Problem Solving": {"category": "Soft Skill", "difficulty": 4, "demand": 95},
        "Critical Thinking": {"category": "Soft Skill", "difficulty": 4, "demand": 92},
        "Team Management": {"category": "Soft Skill", "difficulty": 4, "demand": 88},
        "Negotiation": {"category": "Soft Skill", "difficulty": 4, "demand": 82},
        "Time Management": {"category": "Soft Skill", "difficulty": 3, "demand": 90},
        "Emotional Intelligence": {"category": "Soft Skill", "difficulty": 4, "demand": 85},
        "Presentation Skills": {"category": "Soft Skill", "difficulty": 3, "demand": 88},
        "Stakeholder Management": {"category": "Soft Skill", "difficulty": 5, "demand": 80},
        # Business Skills
        "Financial Modeling": {"category": "Business", "difficulty": 5, "demand": 70},
        "Financial Analysis": {"category": "Business", "difficulty": 4, "demand": 78},
        "Accounting": {"category": "Business", "difficulty": 3, "demand": 72},
        "Taxation": {"category": "Business", "difficulty": 5, "demand": 65},
        "Auditing": {"category": "Business", "difficulty": 5, "demand": 60},
        "Business Strategy": {"category": "Business", "difficulty": 5, "demand": 75},
        "Market Research": {"category": "Business", "difficulty": 3, "demand": 70},
        "Digital Marketing": {"category": "Business", "difficulty": 3, "demand": 82},
        "SEO": {"category": "Business", "difficulty": 3, "demand": 72},
        "SEM": {"category": "Business", "difficulty": 3, "demand": 68},
        "Supply Chain Management": {"category": "Business", "difficulty": 4, "demand": 70},
        "Project Management": {"category": "Business", "difficulty": 4, "demand": 88},
        "Agile Methodology": {"category": "Business", "difficulty": 3, "demand": 85},
        "Scrum": {"category": "Business", "difficulty": 3, "demand": 82},
        # Domain Specific
        "AutoCAD": {"category": "Engineering Tool", "difficulty": 3, "demand": 60},
        "SolidWorks": {"category": "Engineering Tool", "difficulty": 4, "demand": 55},
        "ANSYS": {"category": "Engineering Tool", "difficulty": 6, "demand": 45},
        "Revit": {"category": "Engineering Tool", "difficulty": 4, "demand": 50},
        "MATLAB Simulink": {"category": "Engineering Tool", "difficulty": 5, "demand": 40},
        "PLC Programming": {"category": "Industrial Automation", "difficulty": 4, "demand": 55},
        "SCADA": {"category": "Industrial Automation", "difficulty": 4, "demand": 50},
        "Tally": {"category": "Accounting Software", "difficulty": 2, "demand": 60},
        "SAP": {"category": "ERP", "difficulty": 5, "demand": 65},
        "Oracle ERP": {"category": "ERP", "difficulty": 5, "demand": 50},
        "Excel Advanced": {"category": "Productivity", "difficulty": 2, "demand": 90},
        # Legal Skills
        "Contract Law": {"category": "Legal", "difficulty": 5, "demand": 65},
        "Corporate Law": {"category": "Legal", "difficulty": 5, "demand": 68},
        "IP Law": {"category": "Legal", "difficulty": 6, "demand": 50},
        "Litigation": {"category": "Legal", "difficulty": 6, "demand": 55},
        # Medical Skills
        "Clinical Diagnosis": {"category": "Medical", "difficulty": 7, "demand": 85},
        "Surgical Skills": {"category": "Medical", "difficulty": 9, "demand": 75},
        "Patient Care": {"category": "Medical", "difficulty": 4, "demand": 90},
        "Radiology Interpretation": {"category": "Medical", "difficulty": 7, "demand": 78},
        "Emergency Medicine": {"category": "Medical", "difficulty": 8, "demand": 82},
    }

    # ── Companies (Indian + MNCs with Indian presence) ────────────────
    COMPANIES: ClassVar[Dict[str, Dict]] = {
        # IT Services
        "Tata Consultancy Services (TCS)": {"sector": "IT Services", "type": "Indian MNC", "employees": "600K+"},
        "Infosys": {"sector": "IT Services", "type": "Indian MNC", "employees": "300K+"},
        "Wipro": {"sector": "IT Services", "type": "Indian MNC", "employees": "250K+"},
        "HCL Technologies": {"sector": "IT Services", "type": "Indian MNC", "employees": "200K+"},
        "Tech Mahindra": {"sector": "IT Services", "type": "Indian MNC", "employees": "150K+"},
        "LTI Mindtree": {"sector": "IT Services", "type": "Indian MNC", "employees": "80K+"},
        "Mphasis": {"sector": "IT Services", "type": "Indian MNC", "employees": "30K+"},
        "Coforge": {"sector": "IT Services", "type": "Indian MNC", "employees": "25K+"},
        "Persistent Systems": {"sector": "IT Services", "type": "Indian MNC", "employees": "20K+"},
        # Global Tech (India offices)
        "Google India": {"sector": "Technology", "type": "MNC", "employees": "10K+ (India)"},
        "Microsoft India": {"sector": "Technology", "type": "MNC", "employees": "20K+ (India)"},
        "Amazon India": {"sector": "E-commerce/Cloud", "type": "MNC", "employees": "100K+ (India)"},
        "Apple India": {"sector": "Technology", "type": "MNC", "employees": "3K+ (India)"},
        "Meta India": {"sector": "Technology", "type": "MNC", "employees": "2K+ (India)"},
        "Netflix India": {"sector": "Entertainment", "type": "MNC", "employees": "500+ (India)"},
        "Uber India": {"sector": "Technology", "type": "MNC", "employees": "5K+ (India)"},
        "Salesforce India": {"sector": "Technology", "type": "MNC", "employees": "10K+ (India)"},
        "Adobe India": {"sector": "Technology", "type": "MNC", "employees": "7K+ (India)"},
        "Oracle India": {"sector": "Technology", "type": "MNC", "employees": "40K+ (India)"},
        "SAP Labs India": {"sector": "Technology", "type": "MNC", "employees": "12K+ (India)"},
        "Intel India": {"sector": "Semiconductor", "type": "MNC", "employees": "14K+ (India)"},
        "Samsung India": {"sector": "Technology", "type": "MNC", "employees": "70K+ (India)"},
        "Cisco India": {"sector": "Networking", "type": "MNC", "employees": "10K+ (India)"},
        "Dell Technologies India": {"sector": "Technology", "type": "MNC", "employees": "25K+ (India)"},
        "HP India": {"sector": "Technology", "type": "MNC", "employees": "10K+ (India)"},
        "IBM India": {"sector": "Technology", "type": "MNC", "employees": "100K+ (India)"},
        "Accenture India": {"sector": "Consulting", "type": "MNC", "employees": "300K+ (India)"},
        "Deloitte India": {"sector": "Consulting", "type": "MNC", "employees": "50K+ (India)"},
        "KPMG India": {"sector": "Consulting", "type": "MNC", "employees": "30K+ (India)"},
        "EY India": {"sector": "Consulting", "type": "MNC", "employees": "50K+ (India)"},
        "PwC India": {"sector": "Consulting", "type": "MNC", "employees": "40K+ (India)"},
        "McKinsey India": {"sector": "Consulting", "type": "MNC", "employees": "5K+ (India)"},
        "BCG India": {"sector": "Consulting", "type": "MNC", "employees": "4K+ (India)"},
        "Bain India": {"sector": "Consulting", "type": "MNC", "employees": "3K+ (India)"},
        # Indian Startups / Unicorns
        "Flipkart": {"sector": "E-commerce", "type": "Indian Unicorn", "employees": "20K+"},
        "Zomato": {"sector": "Food Tech", "type": "Indian Unicorn", "employees": "5K+"},
        "Swiggy": {"sector": "Food Tech", "type": "Indian Unicorn", "employees": "5K+"},
        "Ola": {"sector": "Mobility", "type": "Indian Unicorn", "employees": "10K+"},
        "Paytm": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "10K+"},
        "PhonePe": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "5K+"},
        "Razorpay": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "3K+"},
        "CRED": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "1K+"},
        "BYJU'S": {"sector": "EdTech", "type": "Indian Unicorn", "employees": "15K+"},
        "Unacademy": {"sector": "EdTech", "type": "Indian Unicorn", "employees": "3K+"},
        "Dream11": {"sector": "Gaming", "type": "Indian Unicorn", "employees": "1K+"},
        "Nykaa": {"sector": "E-commerce", "type": "Indian Unicorn", "employees": "3K+"},
        "Lenskart": {"sector": "E-commerce", "type": "Indian Unicorn", "employees": "5K+"},
        "Zerodha": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "1K+"},
        "Groww": {"sector": "Fintech", "type": "Indian Unicorn", "employees": "1K+"},
        "Meesho": {"sector": "E-commerce", "type": "Indian Unicorn", "employees": "2K+"},
        # Large Indian Corporates
        "Reliance Industries": {"sector": "Conglomerate", "type": "Indian MNC", "employees": "300K+"},
        "Adani Group": {"sector": "Conglomerate", "type": "Indian MNC", "employees": "30K+"},
        "Tata Group": {"sector": "Conglomerate", "type": "Indian MNC", "employees": "900K+"},
        "Mahindra & Mahindra": {"sector": "Automobile", "type": "Indian MNC", "employees": "40K+"},
        "Maruti Suzuki": {"sector": "Automobile", "type": "Joint Venture", "employees": "30K+"},
        "Tata Motors": {"sector": "Automobile", "type": "Indian MNC", "employees": "50K+"},
        "Hero MotoCorp": {"sector": "Automobile", "type": "Indian MNC", "employees": "8K+"},
        "Bajaj Auto": {"sector": "Automobile", "type": "Indian MNC", "employees": "15K+"},
        "Larsen & Toubro (L&T)": {"sector": "Construction & Engineering", "type": "Indian MNC", "employees": "50K+"},
        "Aditya Birla Group": {"sector": "Conglomerate", "type": "Indian MNC", "employees": "140K+"},
        "Godrej Group": {"sector": "Conglomerate", "type": "Indian MNC", "employees": "30K+"},
        "ITC Limited": {"sector": "FMCG", "type": "Indian MNC", "employees": "36K+"},
        "Hindustan Unilever": {"sector": "FMCG", "type": "Subsidiary MNC", "employees": "20K+"},
        "Nestlé India": {"sector": "FMCG", "type": "Subsidiary MNC", "employees": "8K+"},
        "Asian Paints": {"sector": "Paints", "type": "Indian MNC", "employees": "7K+"},
        "Berger Paints": {"sector": "Paints", "type": "Indian MNC", "employees": "4K+"},
        "Cipla": {"sector": "Pharma", "type": "Indian MNC", "employees": "25K+"},
        "Sun Pharma": {"sector": "Pharma", "type": "Indian MNC", "employees": "35K+"},
        "Dr. Reddy's": {"sector": "Pharma", "type": "Indian MNC", "employees": "20K+"},
        "Biocon": {"sector": "Biopharma", "type": "Indian MNC", "employees": "12K+"},
        "Apollo Hospitals": {"sector": "Healthcare", "type": "Indian MNC", "employees": "60K+"},
        "Fortis Healthcare": {"sector": "Healthcare", "type": "Indian MNC", "employees": "20K+"},
        "Max Healthcare": {"sector": "Healthcare", "type": "Indian MNC", "employees": "15K+"},
        # PSUs
        "ONGC": {"sector": "Oil & Gas", "type": "PSU", "employees": "30K+"},
        "Indian Oil Corporation": {"sector": "Oil & Gas", "type": "PSU", "employees": "30K+"},
        "Bharat Petroleum": {"sector": "Oil & Gas", "type": "PSU", "employees": "9K+"},
        "GAIL": {"sector": "Gas", "type": "PSU", "employees": "5K+"},
        "NTPC": {"sector": "Power", "type": "PSU", "employees": "20K+"},
        "Power Grid Corporation": {"sector": "Power", "type": "PSU", "employees": "8K+"},
        "BHEL": {"sector": "Heavy Engineering", "type": "PSU", "employees": "30K+"},
        "SAIL": {"sector": "Steel", "type": "PSU", "employees": "60K+"},
        "Coal India": {"sector": "Mining", "type": "PSU", "employees": "250K+"},
        "HAL": {"sector": "Aerospace", "type": "PSU", "employees": "30K+"},
        "BEL": {"sector": "Electronics", "type": "PSU", "employees": "10K+"},
        "DRDO": {"sector": "Defence Research", "type": "Government", "employees": "30K+"},
        "ISRO": {"sector": "Space", "type": "Government", "employees": "17K+"},
        "BARC": {"sector": "Nuclear", "type": "Government", "employees": "10K+"},
        # Banks
        "State Bank of India (SBI)": {"sector": "Banking", "type": "PSU", "employees": "250K+"},
        "Punjab National Bank": {"sector": "Banking", "type": "PSU", "employees": "100K+"},
        "Bank of Baroda": {"sector": "Banking", "type": "PSU", "employees": "85K+"},
        "HDFC Bank": {"sector": "Banking", "type": "Private", "employees": "150K+"},
        "ICICI Bank": {"sector": "Banking", "type": "Private", "employees": "130K+"},
        "Axis Bank": {"sector": "Banking", "type": "Private", "employees": "85K+"},
        "Kotak Mahindra Bank": {"sector": "Banking", "type": "Private", "employees": "70K+"},
        "Reserve Bank of India (RBI)": {"sector": "Central Banking", "type": "Government", "employees": "15K+"},
        # Insurance
        "LIC of India": {"sector": "Insurance", "type": "PSU", "employees": "100K+"},
        "ICICI Prudential": {"sector": "Insurance", "type": "Private", "employees": "20K+"},
        # Telecom
        "Reliance Jio": {"sector": "Telecom", "type": "Indian MNC", "employees": "50K+"},
        "Bharti Airtel": {"sector": "Telecom", "type": "Indian MNC", "employees": "25K+"},
        "Vodafone Idea": {"sector": "Telecom", "type": "Joint Venture", "employees": "10K+"},
        "BSNL": {"sector": "Telecom", "type": "PSU", "employees": "60K+"},
    }

    # ── Industries ────────────────────────────────────────────────────
    INDUSTRIES: ClassVar[List[Dict]] = [
        {"name": "Information Technology", "growth_rate": 8.5, "employment_millions": 5.4},
        {"name": "Software Services", "growth_rate": 9.2, "employment_millions": 3.2},
        {"name": "Banking & Financial Services", "growth_rate": 6.5, "employment_millions": 3.8},
        {"name": "Insurance", "growth_rate": 5.8, "employment_millions": 1.5},
        {"name": "Healthcare & Pharmaceuticals", "growth_rate": 12.0, "employment_millions": 6.0},
        {"name": "Automobile", "growth_rate": 7.0, "employment_millions": 4.5},
        {"name": "Manufacturing", "growth_rate": 5.5, "employment_millions": 15.0},
        {"name": "Construction & Infrastructure", "growth_rate": 8.0, "employment_millions": 50.0},
        {"name": "Retail & E-commerce", "growth_rate": 15.0, "employment_millions": 8.0},
        {"name": "Telecommunications", "growth_rate": 6.0, "employment_millions": 2.5},
        {"name": "Media & Entertainment", "growth_rate": 10.0, "employment_millions": 2.0},
        {"name": "Education & EdTech", "growth_rate": 8.0, "employment_millions": 10.0},
        {"name": "Government & Public Sector", "growth_rate": 3.0, "employment_millions": 18.0},
        {"name": "Defence & Aerospace", "growth_rate": 5.0, "employment_millions": 2.5},
        {"name": "Agriculture & Agritech", "growth_rate": 4.5, "employment_millions": 200.0},
        {"name": "Energy & Renewables", "growth_rate": 12.0, "employment_millions": 3.0},
        {"name": "Oil & Gas", "growth_rate": 3.5, "employment_millions": 1.5},
        {"name": "Semiconductor & Electronics", "growth_rate": 18.0, "employment_millions": 0.5},
        {"name": "Gaming & Animation", "growth_rate": 20.0, "employment_millions": 0.3},
        {"name": "Cyber Security", "growth_rate": 22.0, "employment_millions": 0.2},
        {"name": "Cloud Computing", "growth_rate": 25.0, "employment_millions": 0.8},
        {"name": "Artificial Intelligence & ML", "growth_rate": 30.0, "employment_millions": 0.4},
        {"name": "Logistics & Supply Chain", "growth_rate": 8.5, "employment_millions": 6.0},
        {"name": "Hospitality & Tourism", "growth_rate": 7.0, "employment_millions": 8.0},
        {"name": "Textile & Apparel", "growth_rate": 4.0, "employment_millions": 45.0},
        {"name": "Food Processing", "growth_rate": 9.0, "employment_millions": 5.0},
        {"name": "Legal Services", "growth_rate": 6.5, "employment_millions": 1.5},
    ]

    # ── Geographic Hubs (Indian cities for specific industries) ───────
    INDUSTRY_HUBS: ClassVar[Dict[str, List[str]]] = {
        "Information Technology": ["Bengaluru", "Hyderabad", "Pune", "Chennai", "NCR", "Mumbai"],
        "Banking & Financial Services": ["Mumbai", "Bengaluru", "Chennai", "Pune", "Kolkata"],
        "Automobile": ["Chennai", "Pune", "Gurugram", "Ahmedabad", "Sanand"],
        "Pharmaceuticals": ["Hyderabad", "Ahmedabad", "Mumbai", "Bengaluru", "Visakhapatnam"],
        "Aerospace & Defence": ["Bengaluru", "Hyderabad", "Nagpur", "Chennai"],
        "Semiconductor": ["Bengaluru", "Noida", "Hyderabad", "Ahmedabad"],
        "Gaming": ["Bengaluru", "Mumbai", "Hyderabad", "Pune"],
        "Textile": ["Tirupur", "Ludhiana", "Surat", "Coimbatore", "Panipat"],
        "Manufacturing": ["Pune", "Chennai", "Ahmedabad", "Coimbatore", "NCR"],
        "Construction": ["Mumbai", "Bengaluru", "NCR", "Hyderabad", "Pune"],
    }

    # ── Learning Resources ────────────────────────────────────────────
    LEARNING_PLATFORMS: ClassVar[List[str]] = [
        "NPTEL",
        "Swayam",
        "Coursera",
        "edX",
        "Udemy",
        "UpGrad",
        "Great Learning",
        "Simplilearn",
        "Internshala Trainings",
        "LinkedIn Learning",
        "Pluralsight",
        "A Cloud Guru",
        "Khan Academy",
        "Unacademy",
        "BYJU'S Exam Prep",
        "Testbook",
        "Gradeup",
        "Physics Wallah",
        "Vedantu",
        "Codecademy",
        "freeCodeCamp",
        "HackerRank",
        "LeetCode",
        "GeeksforGeeks",
    ]

    # ── Salary reference bands (INR LPA) by career level ──────────────
    SALARY_REFERENCE: ClassVar[Dict[CareerLevel, str]] = {
        CareerLevel.INTERN: "0.5-3 LPA",
        CareerLevel.TRAINEE: "1-4 LPA",
        CareerLevel.ENTRY: "2-6 LPA",
        CareerLevel.JUNIOR: "3-8 LPA",
        CareerLevel.MID: "6-20 LPA",
        CareerLevel.SENIOR: "15-35 LPA",
        CareerLevel.LEAD: "20-45 LPA",
        CareerLevel.PRINCIPAL: "30-60 LPA",
        CareerLevel.MANAGER: "25-50 LPA",
        CareerLevel.SENIOR_MANAGER: "40-70 LPA",
        CareerLevel.DIRECTOR: "50 LPA - 1 Cr",
        CareerLevel.VP: "70 LPA - 1.5 Cr",
        CareerLevel.CXO: "1 Cr - 5 Cr+",
        CareerLevel.FOUNDER: "Variable",
        CareerLevel.INDEPENDENT: "Variable",
    }

    # ── Stream-to-Degree mapping (realistic) ──────────────────────────
    STREAM_TO_DEGREES: ClassVar[Dict[str, List[str]]] = {
        "12th PCM": [
            "B.Tech Computer Science & Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Electrical Engineering",
            "B.Tech Electronics & Communication",
            "B.Tech Aerospace Engineering",
            "B.Tech Chemical Engineering",
            "B.Arch",
            "B.Sc Physics",
            "B.Sc Mathematics",
            "B.Sc Chemistry",
            "B.Sc Computer Science",
            "BCA",
            "BBA",
        ],
        "12th PCB": [
            "MBBS",
            "BDS",
            "BAMS",
            "BHMS",
            "B.Pharma",
            "B.Sc Nursing",
            "B.Sc Biotechnology",
            "B.Sc Microbiology",
            "B.Sc Biochemistry",
            "B.Sc Agriculture",
            "BPT (Physiotherapy)",
        ],
        "12th Commerce": [
            "B.Com (Hons)",
            "B.Com (Accounting & Finance)",
            "BBA",
            "BBA (Finance)",
            "BBA (Marketing)",
            "BMS",
            "BA Economics",
            "BCA",
        ],
        "12th Arts/Humanities": [
            "BA Economics",
            "BA English",
            "BA Political Science",
            "BA History",
            "BA Sociology",
            "BA Psychology",
            "BA Journalism & Mass Communication",
            "BA Fine Arts",
            "BA LLB",
            "B.Des",
            "BFA",
            "BBA",
        ],
    }

    @classmethod
    def get_all_nodes_as_dicts(cls) -> List[Dict[str, Any]]:
        """Yield all taxonomy entries as node dictionaries."""
        nodes: List[Dict[str, Any]] = []

        # School streams
        for name, info in cls.SCHOOL_STREAMS.items():
            nodes.append({"title": name, "node_type": NodeType.EDUCATION, "education_level": EducationLevel.SCHOOL.value, **info})

        # ITI
        for name in cls.ITI_TRADES:
            nodes.append({"title": name, "node_type": NodeType.EDUCATION, "education_level": EducationLevel.CERTIFICATE.value})

        # Diplomas
        for name in cls.DIPLOMA_PROGRAMMES:
            nodes.append({"title": name, "node_type": NodeType.EDUCATION, "education_level": EducationLevel.DIPLOMA.value})

        # Undergraduate
        for name, info in cls.UNDERGRAD_DEGREES.items():
            nodes.append({"title": name, "node_type": NodeType.EDUCATION, "education_level": EducationLevel.UNDERGRADUATE.value, **info})

        # Postgraduate
        for name, info in cls.POSTGRAD_DEGREES.items():
            nodes.append({"title": name, "node_type": NodeType.EDUCATION, "education_level": EducationLevel.POSTGRADUATE.value, **info})

        # Exams
        for name, info in cls.EXAMS.items():
            nodes.append({"title": name, "node_type": NodeType.EXAM, **info})

        # Certifications
        for name in cls.CERTIFICATIONS:
            nodes.append({"title": name, "node_type": NodeType.CERTIFICATION})

        # Job Roles
        for name, info in cls.JOB_ROLES.items():
            nodes.append({"title": name, "node_type": NodeType.JOB_ROLE, "career_level": info.get("level", CareerLevel.MID).value if info.get("level") else None, **info})

        # Skills
        for name, info in cls.SKILLS.items():
            nodes.append({"title": name, "node_type": NodeType.SKILL, **info})

        # Companies
        for name, info in cls.COMPANIES.items():
            nodes.append({"title": name, "node_type": NodeType.COMPANY, **info})

        # Industries
        for ind in cls.INDUSTRIES:
            nodes.append({"title": ind["name"], "node_type": NodeType.INDUSTRY, **ind})

        # Learning platforms
        for name in cls.LEARNING_PLATFORMS:
            nodes.append({"title": name, "node_type": NodeType.LEARNING_RESOURCE})

        return nodes


# ============================================================================
# Deduplication Tracker
# ============================================================================
class DeduplicationTracker:
    """
    Tracks generated signatures to prevent duplicates.
    Supports in-memory set or Bloom filter (via pybloom_live).
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self._count = 0
        if config.duplicate_detection_method == "bloom":
            try:
                from pybloom_live import BloomFilter
                self.filter: Any = BloomFilter(
                    capacity=config.bloom_filter_capacity,
                    error_rate=config.bloom_filter_error_rate,
                )
                self._is_bloom = True
                logger.info(f"Using Bloom filter (capacity={config.bloom_filter_capacity})")
            except ImportError:
                logger.warning("pybloom_live not installed, using in-memory set for deduplication")
                self._is_bloom = False
                self._set: Set[str] = set()
        else:
            self._is_bloom = False
            self._set = set()

    def add(self, signature: str) -> None:
        if self._is_bloom:
            self.filter.add(signature)
        else:
            self._set.add(signature)
        self._count += 1

    def exists(self, signature: str) -> bool:
        if self._is_bloom:
            return signature in self.filter
        return signature in self._set

    def estimated_size(self) -> int:
        if self._is_bloom:
            return len(self.filter)
        return len(self._set)

    @property
    def added_count(self) -> int:
        return self._count


# ============================================================================
# Checkpoint Manager
# ============================================================================
class CheckpointManager:
    """Saves and loads generation state for resumability."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.state: Dict[str, Any] = {
            "node_count": 0,
            "edge_count": 0,
            "path_count": 0,
            "random_state": None,
            "timestamp": "",
            "version": "2.0",
        }

    def save(self, node_count: int, edge_count: int, path_count: int) -> None:
        self.state["node_count"] = node_count
        self.state["edge_count"] = edge_count
        self.state["path_count"] = path_count
        self.state["random_state"] = random.getstate()
        self.state["timestamp"] = datetime.now().isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.state, f, default=str, indent=2)
        logger.debug(f"Checkpoint → {self.path}")

    def load(self) -> Tuple[int, int, int]:
        """Returns (node_count, edge_count, path_count). Restores RNG state."""
        if self.path.exists():
            with open(self.path, "r") as f:
                self.state = json.load(f)
            if self.state.get("random_state"):
                random.setstate(tuple(self.state["random_state"]))
            nc, ec, pc = self.state["node_count"], self.state["edge_count"], self.state["path_count"]
            logger.info(f"Resumed: {nc} nodes, {ec} edges, {pc} paths")
            return nc, ec, pc
        return 0, 0, 0


# ============================================================================
# Multi-Format Streaming Writer
# ============================================================================
class MultiFormatWriter:
    """
    Incrementally writes nodes and edges to JSONL, JSON (streaming array),
    CSV, YAML (document stream), and human-readable TXT.
    """

    def __init__(self, output_dir: str, formats: List[str]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.formats = formats
        self._handles: Dict[str, Any] = {}
        self._csv_writers: Dict[str, csv.DictWriter] = {}
        self._json_first: Dict[str, bool] = {}
        self._init()

    def _init(self):
        if "jsonl" in self.formats:
            self._handles["nodes_jsonl"] = open(self.output_dir / "nodes.jsonl", "a", encoding="utf-8")
            self._handles["edges_jsonl"] = open(self.output_dir / "edges.jsonl", "a", encoding="utf-8")
        if "csv" in self.formats:
            self._handles["nodes_csv"] = open(self.output_dir / "nodes.csv", "a", newline="", encoding="utf-8")
            self._handles["edges_csv"] = open(self.output_dir / "edges.csv", "a", newline="", encoding="utf-8")
        if "yaml" in self.formats:
            self._handles["nodes_yaml"] = open(self.output_dir / "nodes.yaml", "a", encoding="utf-8")
            self._handles["edges_yaml"] = open(self.output_dir / "edges.yaml", "a", encoding="utf-8")
        if "json" in self.formats:
            self._handles["nodes_json"] = open(self.output_dir / "nodes.json", "a", encoding="utf-8")
            self._handles["edges_json"] = open(self.output_dir / "edges.json", "a", encoding="utf-8")
            for key in ["nodes_json", "edges_json"]:
                self._json_first[key] = True
                self._handles[key].write("[\n")
        if "txt" in self.formats:
            self._handles["paths_txt"] = open(self.output_dir / "career_paths.txt", "a", encoding="utf-8")

    def write_node(self, node: Node) -> None:
        d = asdict(node)
        d["node_type"] = node.node_type.value
        # JSONL
        if "jsonl" in self.formats:
            self._handles["nodes_jsonl"].write(json.dumps(d, ensure_ascii=False) + "\n")
        # CSV
        if "csv" in self.formats:
            writer = self._csv_writer("nodes_csv", d)
            writer.writerow(d)
        # YAML
        if "yaml" in self.formats:
            yaml.dump([d], self._handles["nodes_yaml"], allow_unicode=True, default_flow_style=False)
        # JSON
        if "json" in self.formats:
            h = self._handles["nodes_json"]
            if not self._json_first["nodes_json"]:
                h.write(",\n")
            else:
                self._json_first["nodes_json"] = False
            json.dump(d, h, ensure_ascii=False)

    def write_edge(self, edge: Edge) -> None:
        d = asdict(edge)
        d["relationship_type"] = edge.relationship_type.value
        if "jsonl" in self.formats:
            self._handles["edges_jsonl"].write(json.dumps(d, ensure_ascii=False) + "\n")
        if "csv" in self.formats:
            writer = self._csv_writer("edges_csv", d)
            writer.writerow(d)
        if "yaml" in self.formats:
            yaml.dump([d], self._handles["edges_yaml"], allow_unicode=True, default_flow_style=False)
        if "json" in self.formats:
            h = self._handles["edges_json"]
            if not self._json_first["edges_json"]:
                h.write(",\n")
            else:
                self._json_first["edges_json"] = False
            json.dump(d, h, ensure_ascii=False)

    def write_path_text(self, text: str) -> None:
        if "txt" in self.formats:
            self._handles["paths_txt"].write(text + "\n---\n")

    def _csv_writer(self, key: str, sample: Dict) -> csv.DictWriter:
        if key not in self._csv_writers:
            h = self._handles[key]
            writer = csv.DictWriter(h, fieldnames=list(sample.keys()), extrasaction="ignore")
            if h.tell() == 0:
                writer.writeheader()
            self._csv_writers[key] = writer
        return self._csv_writers[key]

    def close(self):
        if "json" in self.formats:
            for key in ["nodes_json", "edges_json"]:
                self._handles[key].write("\n]\n")
        for h in self._handles.values():
            try:
                h.close()
            except Exception:
                pass
        logger.info("Output files closed.")


# ============================================================================
# Node & Edge Factories
# ============================================================================
class NodeFactory:
    """Creates Node objects from taxonomy dicts with deterministic UUIDs."""

    @staticmethod
    def from_dict(info: Dict[str, Any]) -> Node:
        title = info.pop("title")
        node_type = info.pop("node_type", NodeType.EDUCATION)
        if isinstance(node_type, str):
            node_type = NodeType(node_type)
        node_id = deterministic_uuid(f"{node_type.value}:{title.strip().lower()}")

        # Map known fields
        edu_level = info.pop("education_level", None)
        if edu_level and isinstance(edu_level, str):
            edu_level = EducationLevel(edu_level)

        career_level = info.pop("career_level", None)
        if career_level and isinstance(career_level, str):
            career_level = CareerLevel(career_level)

        return Node(
            node_id=node_id,
            node_type=node_type,
            title=title,
            description=info.pop("description", f"{title} — Indian Career Graph Node"),
            category=info.pop("category", ""),
            education_level=edu_level.value if edu_level else None,
            career_level=career_level.value if career_level else None,
            industry=info.pop("sector", info.pop("industry", "")),
            domain=info.pop("domain", info.pop("field", "")),
            estimated_duration_months=int(info.pop("duration_years", 0) * 12) if "duration_years" in info else None,
            typical_salary_band_inr=info.pop("salary_band", info.pop("salary", "")),
            metadata=info,
        )


class EdgeBuilder:
    """Creates Edge instances between two nodes."""

    @staticmethod
    def connect(
        source: Node,
        destination: Node,
        rel_type: EdgeType,
        label: str = "",
        **kwargs,
    ) -> Edge:
        sig = f"{source.node_id}|{destination.node_id}|{rel_type.value}"
        return Edge(
            edge_id=deterministic_uuid(sig),
            source_id=source.node_id,
            destination_id=destination.node_id,
            relationship_type=rel_type,
            label=label or f"{source.title} → {destination.title}",
            **kwargs,
        )


# ============================================================================
# Transition Validator
# ============================================================================
class TransitionValidator:
    """
    Validates career transitions against realistic constraints.
    Prevents cross-domain impossible transitions.
    """

    # Education domain → allowed job domains
    DOMAIN_COMPATIBILITY: ClassVar[Dict[str, Set[str]]] = {
        "Engineering": {"IT", "Manufacturing", "Construction", "Energy", "Automobile", "Telecom", "Aerospace", "Electronics"},
        "Computer Science": {"IT", "Data", "AI/ML", "Cloud", "DevOps", "Cybersecurity", "Gaming", "Product"},
        "Medicine": {"Medicine", "Healthcare", "Research"},
        "Commerce": {"Finance", "Banking", "Accounting", "Business", "Consulting"},
        "Management": {"Business", "Finance", "Marketing", "HR", "Operations", "Product", "Consulting"},
        "Law": {"Law", "Legal", "Judiciary", "Corporate Governance"},
        "Arts": {"Media", "Content", "Design", "Education", "Civil Services"},
        "Science": {"Research", "Data", "Education", "Pharma", "Healthcare"},
        "Agriculture": {"Agriculture", "Food Tech", "Research"},
        "Pharmacy": {"Pharma", "Healthcare"},
        "Architecture": {"Architecture", "Construction", "Design"},
        "Design": {"Design", "Media", "Gaming", "IT"},
        "Education": {"Education", "Academia", "Content"},
        "Defence": {"Defence", "Government", "Security"},
    }

    @staticmethod
    def is_valid(source_domain: str, dest_domain: str) -> bool:
        """Check if transitioning from one domain to another is realistic."""
        if not source_domain or not dest_domain:
            return True  # allow if domain unknown
        if source_domain == dest_domain:
            return True
        allowed = TransitionValidator.DOMAIN_COMPATIBILITY.get(source_domain, set())
        return dest_domain in allowed or source_domain == "" or dest_domain == ""

    @staticmethod
    def education_roles_for_degree(degree_title: str) -> List[str]:
        """Map a degree title to plausible job role titles."""
        mapping = {
            "B.Tech Computer Science & Engineering": ["Software Engineer", "Cloud Engineer", "Data Analyst"],
            "B.Tech Mechanical Engineering": ["Mechanical Engineer", "Design Engineer"],
            "B.Tech Civil Engineering": ["Civil Engineer", "Structural Engineer"],
            "B.Tech Electrical Engineering": ["Electrical Engineer"],
            "B.Tech Electronics & Communication": ["Electronics Engineer", "Embedded Systems Engineer", "VLSI Design Engineer"],
            "MBBS": ["Medical Officer", "General Physician"],
            "BDS": ["Dentist"],
            "B.Pharma": ["Pharmacist"],
            "B.Arch": ["Junior Architect", "Architect"],
            "B.Com (Hons)": ["Accountant", "Financial Analyst"],
            "BBA": ["Business Analyst", "Marketing Executive", "HR Executive"],
            "BCA": ["Junior Software Engineer", "Software Engineer"],
            "BA LLB": ["Junior Advocate", "Corporate Lawyer"],
            "LLB": ["Junior Advocate"],
            "B.Sc Nursing": ["Nurse"],
            "B.Sc Agriculture": ["Agricultural Officer"],
            "BPT (Physiotherapy)": ["Physiotherapist"],
        }
        return mapping.get(degree_title, [])


# ============================================================================
# Main Career Graph Generator
# ============================================================================
class CareerGraphGenerator:
    """
    Generates the Indian Career Knowledge Graph.
    Expands from seed nodes, builds realistic branching paths,
    attaches enrichment edges, and streams to disk.
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        random.seed(config.random_seed)

        self.dedup = DeduplicationTracker(config)
        self.checkpoint = CheckpointManager(config.checkpoint_file)
        self.validator = TransitionValidator()

        # In-memory caches (limited; most data streamed)
        self._node_cache: Dict[str, Node] = {}  # title → Node
        self._node_cache_by_id: Dict[str, Node] = {}  # id → Node

        # Counters
        self.node_count = 0
        self.edge_count = 0
        self.path_count = 0

        # Writer initialized in generate()
        self.writer: Optional[MultiFormatWriter] = None

        # Pre-seed all taxonomy nodes
        self._seed_taxonomy_nodes()

    def _seed_taxonomy_nodes(self):
        """Create and cache all taxonomy nodes."""
        for info_dict in Taxonomies.get_all_nodes_as_dicts():
            node = NodeFactory.from_dict(info_dict.copy())
            sig = node.signature()
            if not self.dedup.exists(sig):
                self.dedup.add(sig)
                self._node_cache[node.title] = node
                self._node_cache_by_id[node.node_id] = node
                self.node_count += 1

    def _get_node(self, title: str, node_type: NodeType = NodeType.EDUCATION, **extra) -> Optional[Node]:
        """Get cached node by title or create a new one."""
        if title in self._node_cache:
            return self._node_cache[title]
        info = {"title": title, "node_type": node_type, **extra}
        node = NodeFactory.from_dict(info)
        sig = node.signature()
        if not self.dedup.exists(sig):
            self.dedup.add(sig)
            self._node_cache[title] = node
            self._node_cache_by_id[node.node_id] = node
            self.node_count += 1
            return node
        # Should have been cached
        return self._node_cache.get(title)

    def _add_edge(
        self,
        src: Node,
        dst: Node,
        rel_type: EdgeType,
        label: str = "",
        **kwargs,
    ) -> Optional[Edge]:
        """Add a directed edge if non-duplicate."""
        edge = EdgeBuilder.connect(src, dst, rel_type, label, **kwargs)
        sig = edge.signature()
        if not self.dedup.exists(sig):
            self.dedup.add(sig)
            self.edge_count += 1
            return edge
        return None

    # ─── Path Expansion Logic ─────────────────────────────────────────
    def _education_next(self, edu_node: Node, depth: int) -> List[Tuple[NodeType, str, EdgeType, Dict]]:
        """Determine next steps after an education node."""
        options: List[Tuple[NodeType, str, EdgeType, Dict]] = []
        title = edu_node.title

        # 10th → streams, ITI, diplomas
        if title == "10th Standard":
            for s in Taxonomies.SCHOOL_STREAMS["10th Standard"]["next"]:
                options.append((NodeType.EDUCATION, s, EdgeType.NEXT_STEP, {}))
        # 11th → 12th
        elif "11th" in title:
            if "PCM" in title:
                options.append((NodeType.EDUCATION, "12th PCM", EdgeType.NEXT_STEP, {}))
            elif "PCB" in title:
                options.append((NodeType.EDUCATION, "12th PCB", EdgeType.NEXT_STEP, {}))
            elif "Commerce" in title:
                options.append((NodeType.EDUCATION, "12th Commerce", EdgeType.NEXT_STEP, {}))
            elif "Arts" in title or "Humanities" in title:
                options.append((NodeType.EDUCATION, "12th Arts/Humanities", EdgeType.NEXT_STEP, {}))
        # 12th → exams / degrees
        elif "12th" in title:
            exams = Taxonomies.SCHOOL_STREAMS.get(title, {}).get("exams", [])
            for exam in exams:
                options.append((NodeType.EXAM, exam, EdgeType.NEXT_STEP, {"probability": 0.7}))
            # Direct degree admission (some universities take 12th marks)
            stream_key = title
            degrees = Taxonomies.STREAM_TO_DEGREES.get(stream_key, [])
            for deg in degrees[:6]:  # limit to avoid explosion
                options.append((NodeType.EDUCATION, deg, EdgeType.BRANCH, {"probability": 0.3}))
        # ITI → jobs
        elif title.startswith("ITI"):
            options.append((NodeType.JOB_ROLE, "Junior Technician", EdgeType.NEXT_STEP, {}))
        # Diploma → jobs or lateral B.Tech
        elif title.startswith("Diploma"):
            if "Mechanical" in title:
                options.append((NodeType.JOB_ROLE, "Mechanical Engineer", EdgeType.NEXT_STEP, {}))
            elif "Civil" in title:
                options.append((NodeType.JOB_ROLE, "Civil Engineer", EdgeType.NEXT_STEP, {}))
            elif "Computer" in title:
                options.append((NodeType.JOB_ROLE, "Junior Software Engineer", EdgeType.NEXT_STEP, {}))
            elif "Electrical" in title:
                options.append((NodeType.JOB_ROLE, "Electrical Engineer", EdgeType.NEXT_STEP, {}))
            elif "Electronics" in title:
                options.append((NodeType.JOB_ROLE, "Electronics Engineer", EdgeType.NEXT_STEP, {}))
            # lateral entry to B.Tech
            options.append((NodeType.EDUCATION, "B.Tech Mechanical Engineering", EdgeType.BRANCH, {}))
            options.append((NodeType.EXAM, "SSC CGL", EdgeType.BRANCH, {}))
        # Undergraduate
        elif title in Taxonomies.UNDERGRAD_DEGREES:
            deg_info = Taxonomies.UNDERGRAD_DEGREES[title]
            domain = deg_info.get("domain", "")
            field = deg_info.get("field", "")

            # Direct job roles
            direct_roles = self.validator.education_roles_for_degree(title)
            for role in direct_roles[:3]:
                options.append((NodeType.JOB_ROLE, role, EdgeType.NEXT_STEP, {"probability": 0.6}))

            # Exams for PG or Govt
            if "Engineering" in domain or "Computer Science" in field:
                options.append((NodeType.EXAM, "GATE", EdgeType.BRANCH, {"probability": 0.4}))
                options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {"probability": 0.15}))
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {"probability": 0.1}))
                options.append((NodeType.EXAM, "SSC CGL", EdgeType.BRANCH, {"probability": 0.1}))
            elif "Medicine" in domain:
                options.append((NodeType.EXAM, "NEET PG", EdgeType.BRANCH, {"probability": 0.7}))
            elif "Commerce" in domain or "Management" in domain:
                options.append((NodeType.EXAM, "CAT", EdgeType.BRANCH, {"probability": 0.4}))
                options.append((NodeType.EXAM, "CA Intermediate", EdgeType.BRANCH, {"probability": 0.3}))
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {"probability": 0.15}))
            elif "Law" in domain:
                options.append((NodeType.EXAM, "AIBE", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {"probability": 0.2}))
            elif "Science" in domain:
                options.append((NodeType.EXAM, "IIT JAM", EdgeType.BRANCH, {"probability": 0.3}))
                options.append((NodeType.EXAM, "CSIR NET", EdgeType.BRANCH, {"probability": 0.2}))
            elif "Arts" in domain:
                options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {"probability": 0.25}))
                options.append((NodeType.EXAM, "UGC NET", EdgeType.BRANCH, {"probability": 0.2}))

            # PG degrees
            pg_map = {
                "B.Tech Computer Science & Engineering": ["M.Tech CSE", "M.Tech AI & ML", "MCA", "MBA", "M.Sc Data Science"],
                "B.Tech Mechanical Engineering": ["M.Tech Thermal Engineering", "MBA"],
                "B.Tech Civil Engineering": ["M.Tech Structural Engineering", "MBA"],
                "B.Sc Physics": ["M.Sc Physics", "M.Sc Data Science"],
                "B.Sc Chemistry": ["M.Sc Chemistry"],
                "B.Com (Hons)": ["M.Com", "MBA Finance"],
                "BBA": ["MBA", "MBA Marketing"],
                "BCA": ["MCA", "MBA"],
                "MBBS": ["MD General Medicine", "MS General Surgery"],
                "BA Economics": ["MA Economics", "MBA"],
                "BA LLB": ["LLM"],
            }
            pgs = pg_map.get(title, [])
            for pg in pgs[:3]:
                options.append((NodeType.EDUCATION, pg, EdgeType.BRANCH, {"probability": 0.3}))

        # Postgraduate
        elif title in Taxonomies.POSTGRAD_DEGREES:
            pg_info = Taxonomies.POSTGRAD_DEGREES[title]
            domain = pg_info.get("domain", "")
            if "Engineering" in domain:
                options.append((NodeType.JOB_ROLE, "Senior Engineer", EdgeType.NEXT_STEP, {}))
            elif title == "MCA":
                options.append((NodeType.JOB_ROLE, "Software Engineer", EdgeType.NEXT_STEP, {}))
            elif "MBA" in title:
                options.append((NodeType.JOB_ROLE, "Product Manager", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.JOB_ROLE, "Management Consultant", EdgeType.BRANCH, {}))
            elif title.startswith("MD"):
                options.append((NodeType.JOB_ROLE, "General Physician", EdgeType.NEXT_STEP, {}))
            elif title.startswith("MS"):
                options.append((NodeType.JOB_ROLE, "Surgeon", EdgeType.NEXT_STEP, {}))
            elif title == "M.Sc Data Science":
                options.append((NodeType.JOB_ROLE, "Data Scientist", EdgeType.NEXT_STEP, {}))
            elif title == "PhD":
                options.append((NodeType.JOB_ROLE, "Assistant Professor", EdgeType.NEXT_STEP, {}))
                options.append((NodeType.JOB_ROLE, "Research Scientist", EdgeType.BRANCH, {}))
            # Common branches
            options.append((NodeType.JOB_ROLE, "Entrepreneur / Founder", EdgeType.BRANCH, {"probability": 0.1}))
            options.append((NodeType.EXAM, "UPSC CSE", EdgeType.BRANCH, {"probability": 0.08}))

        return options

    def _exam_next(self, exam_node: Node) -> List[Tuple[NodeType, str, EdgeType, Dict]]:
        """Determine what follows an exam."""
        title = exam_node.title
        options = []

        exam_degree_map = {
            "JEE Main": ["B.Tech Computer Science & Engineering", "B.Tech Mechanical Engineering", "B.Tech Civil Engineering", "B.Tech Electrical Engineering", "B.Tech Electronics & Communication"],
            "JEE Advanced": ["B.Tech Computer Science & Engineering", "B.Tech Aerospace Engineering"],
            "NEET UG": ["MBBS", "BDS", "BAMS", "BHMS"],
            "GATE": ["M.Tech CSE", "M.Tech VLSI Design", "M.Tech Structural Engineering"],
            "CAT": ["MBA", "MBA Finance", "MBA Marketing"],
            "UPSC CSE": ["IAS Officer", "IPS Officer", "IFS Officer", "IRS Officer"],
            "SSC CGL": ["SSC CGL Officer"],
            "IBPS PO": ["Bank PO"],
            "SBI PO": ["Bank PO"],
            "CLAT": ["BA LLB", "LLB"],
            "NIFT Entrance": ["B.Des"],
            "CA Foundation": ["Chartered Accountant"],
            "NEET PG": ["MD General Medicine", "MS General Surgery"],
            "CDS": ["Indian Army Officer", "Indian Navy Officer", "Indian Air Force Officer"],
            "NDA": ["Indian Army Officer"],
            "ISRO Scientist": ["ISRO Scientist"],
            "UGC NET": ["Assistant Professor"],
            "RBI Grade B": ["RBI Grade B Officer"],
        }

        targets = exam_degree_map.get(title, [])
        for t in targets:
            ntype = NodeType.JOB_ROLE if any(
                t in Taxonomies.JOB_ROLES for _ in [1]
            ) else NodeType.EDUCATION
            # Determine type
            if t in Taxonomies.JOB_ROLES:
                ntype = NodeType.JOB_ROLE
            elif t in Taxonomies.UNDERGRAD_DEGREES or t in Taxonomies.POSTGRAD_DEGREES:
                ntype = NodeType.EDUCATION
            else:
                ntype = NodeType.JOB_ROLE  # default
            options.append((ntype, t, EdgeType.NEXT_STEP, {"probability": 0.8}))

        return options

    def _job_role_next(self, job_node: Node) -> List[Tuple[NodeType, str, EdgeType, Dict]]:
        """Define career progression from a job role."""
        title = job_node.title
        options = []

        # Hierarchical progression map
        progression: Dict[str, str] = {
            # Software
            "Software Engineering Intern": "Junior Software Engineer",
            "Junior Software Engineer": "Software Engineer",
            "Software Engineer": "Senior Software Engineer",
            "Senior Software Engineer": "Tech Lead",
            "Tech Lead": "Engineering Manager",
            "Engineering Manager": "Senior Engineering Manager",
            "Senior Engineering Manager": "Director of Engineering",
            "Director of Engineering": "VP Engineering",
            "VP Engineering": "CTO",
            # Data
            "Data Analyst Intern": "Junior Data Analyst",
            "Junior Data Analyst": "Data Analyst",
            "Data Analyst": "Senior Data Analyst",
            "Data Scientist": "Senior Data Scientist",
            "ML Engineer": "Senior ML Engineer",
            "Senior Data Scientist": "Data Engineering Manager",
            # Cloud
            "Cloud Support Engineer": "Cloud Engineer",
            "Cloud Engineer": "Senior Cloud Engineer",
            "Senior Cloud Engineer": "Cloud Architect",
            "DevOps Engineer": "Senior DevOps Engineer",
            "Senior DevOps Engineer": "DevOps Architect",
            # Security
            "Security Analyst": "Security Engineer",
            "Security Engineer": "Senior Security Engineer",
            "Senior Security Engineer": "Security Architect",
            "Security Architect": "CISO",
            # Product
            "Associate Product Manager": "Product Manager",
            "Product Manager": "Senior Product Manager",
            "Senior Product Manager": "Director of Product",
            "Director of Product": "VP Product",
            "VP Product": "CPO",
            # Design
            "UI Designer": "UX Designer",
            "UX Designer": "Senior UX Designer",
            "Senior UX Designer": "Design Manager",
            "Design Manager": "Design Director",
            # Business
            "Business Analyst": "Senior Business Analyst",
            "Senior Business Analyst": "Product Manager",
            "Financial Analyst": "Investment Banker",
            "Accountant": "Chartered Accountant",
            # Civil Services
            "IAS Officer": "District Magistrate",
            "District Magistrate": "Joint Secretary",
            "Joint Secretary": "Cabinet Secretary",
            # Banking
            "Bank PO": "Bank Manager",
            # Mechanical
            "Mechanical Engineer": "Senior Mechanical Engineer",
            "Senior Mechanical Engineer": "Production Manager",
            # Civil
            "Civil Engineer": "Senior Civil Engineer",
            "Senior Civil Engineer": "Project Manager (Construction)",
            # Electrical
            "Electrical Engineer": "Senior Electrical Engineer",
            # Electronics
            "Electronics Engineer": "Embedded Systems Engineer",
            "Embedded Systems Engineer": "VLSI Design Engineer",
            # Medical
            "Medical Officer": "General Physician",
            "General Physician": "Cardiologist",
            "Nurse": "Senior Nurse",
            # Legal
            "Junior Advocate": "Advocate",
            "Advocate": "Senior Advocate",
            "Corporate Lawyer": "Senior Advocate",
            # Architecture
            "Junior Architect": "Architect",
            "Architect": "Senior Architect",
            # Media
            "Journalist": "Senior Journalist",
            "Content Writer": "Content Strategist",
            # Education
            "School Teacher": "Assistant Professor",
            "Assistant Professor": "Associate Professor",
            "Associate Professor": "Professor",
            "Research Scholar": "Research Scientist",
        }

        if title in progression:
            next_title = progression[title]
            ntype = NodeType.JOB_ROLE
            options.append((ntype, next_title, EdgeType.NEXT_STEP, {"transition_difficulty": 4, "probability": 0.7}))

        # Lateral / branching options for mid-senior roles
        if "Senior" in title or "Lead" in title or "Manager" in title or "Director" in title:
            options.append((NodeType.JOB_ROLE, "Freelance Consultant", EdgeType.FREELANCE_PATH, {"probability": 0.1}))
            options.append((NodeType.JOB_ROLE, "Independent Consultant", EdgeType.CONSULTING_PATH, {"probability": 0.1}))
            options.append((NodeType.JOB_ROLE, "Entrepreneur / Founder", EdgeType.ENTREPRENEURSHIP_PATH, {"probability": 0.08}))
            options.append((NodeType.JOB_ROLE, "Assistant Professor", EdgeType.TEACHING_PATH, {"probability": 0.05}))

        # Government / Exam branch
        if "Senior" not in title and "Manager" not in title and "Director" not in title:
            options.append((NodeType.EXAM, "UPSC CSE", EdgeType.GOVERNMENT_PATH, {"probability": 0.06}))
            options.append((NodeType.EXAM, "SSC CGL", EdgeType.GOVERNMENT_PATH, {"probability": 0.08}))

        return options

    def _add_enrichment(self, node: Node):
        """Attach skills, companies, industries, certifications to a node."""
        if node.node_type != NodeType.JOB_ROLE:
            return

        title = node.title
        domain = node.domain if node.domain else self._infer_domain(title)

        # Skill mapping
        role_skills: Dict[str, List[str]] = {
            "Software Engineer": ["Python", "Java", "SQL", "Docker", "Git"],
            "Senior Software Engineer": ["Python", "Java", "AWS", "Kubernetes", "System Design"],
            "Data Scientist": ["Python", "Machine Learning", "SQL", "Pandas", "Statistics"],
            "ML Engineer": ["Python", "Deep Learning", "TensorFlow", "PyTorch", "MLOps"],
            "Cloud Engineer": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux"],
            "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "Terraform", "AWS"],
            "Security Engineer": ["Network Security", "Ethical Hacking", "SIEM", "Python"],
            "Product Manager": ["Product Strategy", "Agile Methodology", "Stakeholder Management", "Communication"],
            "Financial Analyst": ["Financial Modeling", "Excel Advanced", "Accounting"],
            "Mechanical Engineer": ["AutoCAD", "SolidWorks", "ANSYS"],
            "Civil Engineer": ["AutoCAD", "Structural Analysis", "Revit"],
            "Electrical Engineer": ["MATLAB Simulink", "PLC Programming", "SCADA"],
            "Medical Officer": ["Clinical Diagnosis", "Patient Care", "Communication"],
            "General Physician": ["Clinical Diagnosis", "Patient Care", "Pharmacology"],
            "IAS Officer": ["Public Policy", "Leadership", "Critical Thinking"],
            "Chartered Accountant": ["Accounting", "Taxation", "Auditing", "Financial Reporting"],
        }

        skills = role_skills.get(title, [])
        for sk in skills:
            sk_node = self._get_node(sk, NodeType.SKILL)
            if sk_node:
                edge = self._add_edge(sk_node, node, EdgeType.REQUIRES_SKILL)
                if edge and self.writer:
                    self.writer.write_edge(edge)

        # Company mapping
        role_companies: Dict[str, List[str]] = {
            "Software Engineer": ["Tata Consultancy Services (TCS)", "Infosys", "Google India", "Microsoft India", "Flipkart"],
            "Senior Software Engineer": ["Amazon India", "Microsoft India", "Flipkart", "Uber India", "Zerodha"],
            "Data Scientist": ["Amazon India", "Flipkart", "Zomato", "Swiggy", "Paytm"],
            "Cloud Engineer": ["AWS", "Microsoft India", "Google India", "Oracle India"],
            "Mechanical Engineer": ["Tata Motors", "Mahindra & Mahindra", "Larsen & Toubro (L&T)", "Maruti Suzuki"],
            "Civil Engineer": ["Larsen & Toubro (L&T)", "Adani Group", "Tata Group"],
            "Electrical Engineer": ["BHEL", "NTPC", "Power Grid Corporation", "Siemens India"],
            "IAS Officer": ["Government of India"],
            "Bank PO": ["State Bank of India (SBI)", "HDFC Bank", "ICICI Bank"],
            "Medical Officer": ["AIIMS", "Apollo Hospitals", "Fortis Healthcare"],
            "Chartered Accountant": ["Deloitte India", "EY India", "KPMG India", "PwC India"],
            "Product Manager": ["Flipkart", "Zomato", "CRED", "PhonePe", "Google India"],
        }
        companies = role_companies.get(title, [])
        for comp in companies[:4]:
            comp_node = self._get_node(comp, NodeType.COMPANY)
            if comp_node:
                edge = self._add_edge(node, comp_node, EdgeType.CAN_WORK_AT)
                if edge and self.writer:
                    self.writer.write_edge(edge)

        # Industry connection
        if domain:
            # Try to find matching industry node
            industry_map = {
                "IT": "Information Technology",
                "Data": "Artificial Intelligence & ML",
                "Cloud": "Cloud Computing",
                "DevOps": "Cloud Computing",
                "Cybersecurity": "Cyber Security",
                "Finance": "Banking & Financial Services",
                "Medicine": "Healthcare & Pharmaceuticals",
                "Mechanical": "Manufacturing",
                "Civil": "Construction & Infrastructure",
                "Electrical": "Energy & Renewables",
                "Electronics": "Semiconductor & Electronics",
                "Agriculture": "Agriculture & Agritech",
                "Law": "Legal Services",
                "Education": "Education & EdTech",
                "Media": "Media & Entertainment",
                "Gaming": "Gaming & Animation",
                "Telecom": "Telecommunications",
                "Hospitality": "Hospitality & Tourism",
                "Aerospace": "Defence & Aerospace",
                "Renewable Energy": "Energy & Renewables",
            }
            ind_name = industry_map.get(domain, "")
            if ind_name:
                ind_node = self._get_node(ind_name, NodeType.INDUSTRY)
                if ind_node:
                    edge = self._add_edge(node, ind_node, EdgeType.LEADS_TO)
                    if edge and self.writer:
                        self.writer.write_edge(edge)

    def _infer_domain(self, title: str) -> str:
        """Infer domain from job title."""
        for role, info in Taxonomies.JOB_ROLES.items():
            if role == title:
                return info.get("domain", "")
        return ""

    # ─── Recursive Expansion ──────────────────────────────────────────
    def _expand(self, current: Node, depth: int, visited: List[str]):
        """Recursively expand the graph from a node."""
        if (
            depth > self.config.max_path_length
            or self.path_count >= self.config.max_total_paths
            or self.node_count >= self.config.max_nodes
            or self.edge_count >= self.config.max_edges
        ):
            return

        # Determine next steps
        next_opts: List[Tuple[NodeType, str, EdgeType, Dict]] = []
        if current.node_type == NodeType.EDUCATION:
            next_opts = self._education_next(current, depth)
        elif current.node_type == NodeType.EXAM:
            next_opts = self._exam_next(current)
        elif current.node_type == NodeType.JOB_ROLE:
            next_opts = self._job_role_next(current)

        if not next_opts:
            return

        # Shuffle deterministically for variety
        random.shuffle(next_opts)

        # Pick primary path
        primary = next_opts[0]
        branches = next_opts[1 : self.config.max_branches_per_node] if random.random() < self.config.branch_probability else []

        # Process primary
        self._follow_edge(current, primary, depth, visited)

        # Process branches
        for branch in branches[: self.config.max_branches_per_node]:
            self._follow_edge(current, branch, depth, visited)

    def _follow_edge(
        self,
        src: Node,
        option: Tuple[NodeType, str, EdgeType, Dict],
        depth: int,
        visited: List[str],
    ):
        """Create destination node, edge, write, and recurse."""
        dest_type, dest_title, edge_type, edge_kwargs = option

        # Prevent immediate cycles
        if dest_title in visited[-3:]:
            return

        # Create/get destination node
        dest_node = self._get_node(dest_title, dest_type)
        if not dest_node:
            return

        # Domain validation
        src_domain = src.domain or self._infer_domain(src.title)
        dst_domain = dest_node.domain or self._infer_domain(dest_title)
        if not self.validator.is_valid(src_domain, dst_domain):
            return

        # Create edge
        edge = self._add_edge(src, dest_node, edge_type, **edge_kwargs)
        if edge and self.writer:
            self.writer.write_edge(edge)

        # Write dest node if newly added
        if self.writer:
            self.writer.write_node(dest_node)

        # Add enrichment for job roles
        if dest_node.node_type == NodeType.JOB_ROLE and random.random() < self.config.enrichment_density:
            self._add_enrichment(dest_node)

        # Record path
        new_visited = visited + [dest_title]
        if dest_type == NodeType.JOB_ROLE or depth >= self.config.max_path_length - 1:
            self.path_count += 1
            path_str = " → ".join(new_visited)
            if self.writer:
                self.writer.write_path_text(path_str)

            # Periodic checkpoint
            if self.path_count % self.config.checkpoint_interval == 0:
                self.checkpoint.save(self.node_count, self.edge_count, self.path_count)
                logger.info(
                    f"Progress: {self.path_count} paths | "
                    f"{self.node_count} nodes | {self.edge_count} edges"
                )

        # Recurse
        self._expand(dest_node, depth + 1, new_visited)

    # ─── Main Entry ───────────────────────────────────────────────────
    def generate(self):
        """Main generation orchestration."""
        self.writer = MultiFormatWriter(self.config.output_dir, self.config.formats)

        # Resume
        nc, ec, pc = self.checkpoint.load()
        if nc > 0:
            self.node_count = nc
            self.edge_count = ec
            self.path_count = pc
        else:
            # Write all cached nodes
            for node in self._node_cache.values():
                self.writer.write_node(node)

        # Seed nodes to start expansion
        seeds = [
            "10th Standard",
            "Diploma in Mechanical Engineering",
            "Diploma in Computer Science & Engineering",
            "Diploma in Civil Engineering",
            "Diploma in Electrical Engineering",
        ]

        for seed_title in seeds:
            seed_node = self._get_node(seed_title, NodeType.EDUCATION)
            if seed_node:
                self._expand(seed_node, depth=0, visited=[seed_title])
            if self.path_count >= self.config.max_total_paths:
                break
            if self.node_count >= self.config.max_nodes or self.edge_count >= self.config.max_edges:
                break

        # Generate some exam-seeded paths
        exam_seeds = ["UPSC CSE", "CAT", "GATE", "CA Foundation", "NEET UG", "CLAT"]
        for exam_seed in exam_seeds:
            exam_node = self._get_node(exam_seed, NodeType.EXAM)
            if exam_node:
                self._expand(exam_node, depth=0, visited=[exam_seed])
            if self.path_count >= self.config.max_total_paths:
                break

        # Finalize
        self.writer.close()
        self.checkpoint.save(self.node_count, self.edge_count, self.path_count)

        # Print statistics
        logger.info("=" * 60)
        logger.info(f"  Generation Complete")
        logger.info(f"  Total Career Paths: {self.path_count}")
        logger.info(f"  Total Nodes:        {self.node_count}")
        logger.info(f"  Total Edges:        {self.edge_count}")
        logger.info(f"  Output Directory:   {self.config.output_dir}")
        logger.info("=" * 60)

        # Write stats JSON
        stats = {
            "paths": self.path_count,
            "nodes": self.node_count,
            "edges": self.edge_count,
            "timestamp": datetime.now().isoformat(),
            "config": asdict(self.config),
        }
        with open(self.config.stats_file, "w") as f:
            json.dump(stats, f, indent=2)


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    config = GeneratorConfig(
        output_dir="./career_graph_output",
        checkpoint_file="./career_checkpoint.json",
        stats_file="./generation_stats.json",
        random_seed=42,
        max_total_paths=50000,
        max_nodes=2000000,
        max_edges=5000000,
        max_path_length=14,
        branch_probability=0.35,
        enrichment_density=0.6,
    )

    logger.info("Indian Career Intelligence Platform — Graph Generator v2.0")
    logger.info(f"Output: {config.output_dir}")
    logger.info(f"Max paths: {config.max_total_paths}")
    logger.info(f"Seed: {config.random_seed}")

    start = time.time()
    generator = CareerGraphGenerator(config)
    generator.generate()
    elapsed = time.time() - start
    logger.info(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")


if __name__ == "__main__":
    main()