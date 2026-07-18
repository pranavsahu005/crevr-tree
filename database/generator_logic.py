
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


def _get_progression_chain(self, title: str) -> List[str]:
    for chain in self.PROGRESSION_CHAINS.values():
        if title in chain:
            idx = chain.index(title)
            return chain[idx+1:]
    return []

def _get_next_in_progression(self, title: str) -> Optional[str]:
    for chain in self.PROGRESSION_CHAINS.values():
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
            "ITI Electrician", "ITI Fitter", "ITI COPA", "ITI Welder", "ITI CNC Operator",
            "ITI Diesel Mechanic", "ITI Solar Technician", "ITI Electronics",
            "Diploma in Computer Engineering", "Diploma in Mechanical Engineering",
            "Diploma in Civil Engineering", "Diploma in Electrical Engineering",
            "Diploma in Hotel Management", "Diploma in Fashion Design",
            "12th PCM", "12th PCB", "12th Commerce", "12th Arts",
        ]

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
        # Always follow main path + 1-3 branches with high probability
        selected_branches = []
        for b in branches:
            if random.random() < self.config.branch_probability:
                selected_branches.append(b)
                if len(selected_branches) >= 2:  # Max 2-3 branches
                    break

        self._process_transition(current_node, main, depth, visited_path)

        for branch_option in selected_branches:
            if self.path_counter >= self.config.max_total_paths: break
            self._process_transition(current_node, branch_option, depth, visited_path)

    def _process_transition(self, current_node: Node, option: Tuple, depth: int, visited_path: List[str]):
        dest_type, dest_title, edge_type, edge_kwargs = option
        if dest_title in visited_path:
            return
        dest_node = self._get_or_create_node(dest_title, dest_type)
        if not self.validator.is_valid_transition(current_node.node_type, dest_type, current_node.title, dest_title):
            return

        edge = self._add_edge(current_node, dest_node, edge_type, **edge_kwargs)
        if edge and self.writer:
            self.writer.write_edge(edge)

        new_path = visited_path + [dest_title]
        if dest_type == NodeType.JOB_ROLE or dest_type == NodeType.CERTIFICATION or depth >= self.config.max_path_length - 1:
            self.path_counter += 1
            path_str = " \u2192 ".join(new_path)
            if self.writer:
                self.writer.write_path_text(f"Path #{self.path_counter}: {path_str}")
            if self.path_counter % self.config.log_interval == 0:
                logger.info(f"Generated {self.path_counter} paths, {self.generated_nodes}N, {self.generated_edges}E")
                self.checkpoint_mgr.save(self.dedup, self.generated_nodes, self.generated_edges, self.path_counter)
            if dest_type == NodeType.JOB_ROLE:
                return  # Stop at job role (terminal)

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
        next_role = CareerPathGenerator._get_next_in_progression(self, title)
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
