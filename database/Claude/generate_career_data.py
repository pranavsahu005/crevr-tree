"""
CREVR-TREE | Indian Career Intelligence Data Generator
=======================================================
Run: python generate_career_data.py
Output: career_data.json  +  career_data.txt
No external dependencies — pure Python 3.8+

HOW IT WORKS:
  - Every career path is a dict with: id, title, category, description,
    steps (ordered list of nodes), branches (alternate routes), skills,
    resources (free), salary_range, companies, govt_bodies
  - txt output = human-readable, can be pasted into Antigravity/AI tools
  - json output = used by your React/Next.js front-end directly
"""

import json
import os
import textwrap
from datetime import datetime

# ─────────────────────────────────────────────
#  RAW CAREER PATH DEFINITIONS
#  Each path = one complete career tree branch
#  Add more paths by appending to CAREER_PATHS
# ─────────────────────────────────────────────

CAREER_PATHS = [

    # ══════════════════════════════════════════
    #  TECHNOLOGY & ENGINEERING
    # ══════════════════════════════════════════

    {
        "id": "tech_software_jee",
        "title": "Software Engineer (JEE Route)",
        "category": "Technology",
        "subcategory": "Software Development",
        "description": "India's most competitive engineering path. JEE → IIT/NIT → Top tech roles in India and globally.",
        "difficulty": "High",
        "demand": "Very High",
        "automation_risk": "Medium",
        "remote_potential": "Very High",
        "steps": [
            {"level": 1, "stage": "School (Class 6–10)", "action": "Build strong Maths & Science base. Olympiads (NSO, IMO) are a bonus."},
            {"level": 2, "stage": "Class 11–12 (PCM)", "action": "Join JEE coaching (Allen, Resonance, Aakash or free: Unacademy, PW). Focus: Physics, Chemistry, Maths."},
            {"level": 3, "stage": "JEE Main + Advanced", "action": "JEE Main (NTA) → JEE Advanced (IIT). Score determines IIT/NIT/IIIT/State college."},
            {"level": 4, "stage": "B.Tech (4 years)", "action": "CSE / IT / ECE preferred. Focus on DSA, projects, open source from Year 1."},
            {"level": 5, "stage": "Internships (Year 2–4)", "action": "Target Google, Microsoft, Flipkart, startups. Use LinkedIn, Internshala, AngelList."},
            {"level": 6, "stage": "Entry Role (0–2 yrs)", "action": "Junior Software Engineer / SDE-1. Salary: ₹6–25 LPA depending on company."},
            {"level": 7, "stage": "Mid Level (2–5 yrs)", "action": "SDE-2 / Software Engineer II. Own features, mentor juniors. ₹20–50 LPA."},
            {"level": 8, "stage": "Senior (5–8 yrs)", "action": "Senior SDE / Staff Engineer. System design, architecture ownership. ₹40–1.2 Cr."},
            {"level": 9, "stage": "Lead / Principal (8–12 yrs)", "action": "Tech Lead / Principal Engineer. Cross-team impact. ₹80 L–2 Cr+."},
            {"level": 10, "stage": "Management Track", "action": "Engineering Manager → Director of Engineering → VP Eng → CTO."},
            {"level": 11, "stage": "Entrepreneurship", "action": "Found a startup. Use network from IIT/NIT. Apply to YC, Sequoia Surge, Accel India."},
        ],
        "branches": [
            {"from_step": 4, "title": "Data Science / AI/ML Track", "path": "B.Tech → ML internship → Data Scientist → ML Engineer → AI Researcher / MLE at FAANG"},
            {"from_step": 4, "title": "Product Management", "path": "B.Tech → PM intern → Associate PM → PM → Senior PM → Group PM → CPO"},
            {"from_step": 6, "title": "MBA Route", "path": "2 yrs SDE → IIM MBA → Product/Strategy/Consulting roles"},
            {"from_step": 4, "title": "Government / UPSC", "path": "B.Tech → UPSC prep → IAS/IPS/IFS (tech background helps in policy roles)"},
            {"from_step": 4, "title": "Research / PhD", "path": "B.Tech → GATE → M.Tech/MS → PhD (IISc, CMU, Stanford) → Research Scientist"},
            {"from_step": 6, "title": "Freelancing / Remote", "path": "2 yrs experience → Toptal / Upwork / direct clients → ₹1–5L/month possible"},
        ],
        "skills_required": ["Data Structures & Algorithms", "System Design", "Python / Java / C++", "Git", "SQL", "Problem Solving", "Communication"],
        "skills_to_build": ["Cloud (AWS/GCP/Azure)", "Docker & Kubernetes", "React / Node.js", "Machine Learning basics", "Leadership"],
        "certifications": [
            {"name": "AWS Certified Developer", "platform": "AWS", "free": False, "cost": "~$150"},
            {"name": "Google Cloud Professional", "platform": "Google", "free": False, "cost": "~$200"},
            {"name": "Meta Front-End Developer Certificate", "platform": "Coursera", "free": False, "cost": "~₹3000/mo", "audit": True},
        ],
        "free_resources": [
            {"name": "CS50 by Harvard", "url": "https://cs50.harvard.edu/x/", "type": "Course"},
            {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "Course"},
            {"name": "NPTEL Programming Courses", "url": "https://nptel.ac.in/", "type": "Course"},
            {"name": "Striver's DSA Sheet", "url": "https://takeuforward.org/strivers-a2z-dsa-course/", "type": "Practice"},
            {"name": "Physics Wallah (JEE Prep)", "url": "https://www.pw.live/", "type": "Exam Prep"},
        ],
        "salary_range": {"entry": "₹6–25 LPA", "mid": "₹20–50 LPA", "senior": "₹40 L–1.5 Cr", "executive": "₹1 Cr+"},
        "companies": {
            "product": ["Google India", "Microsoft India", "Amazon India", "Flipkart", "Meesho", "Razorpay", "CRED", "Zepto", "PhonePe"],
            "service": ["TCS", "Infosys", "Wipro", "HCL Technologies", "Tech Mahindra", "Cognizant"],
            "startups": ["Postman", "BrowserStack", "Chargebee", "Freshworks", "Zoho"],
            "research": ["IISc", "TCS Research", "Microsoft Research India", "Google Research India"],
        },
        "govt_opportunities": ["DRDO Scientist", "ISRO Scientist/Engineer", "C-DAC", "NIC (National Informatics Centre)", "ECIL"],
        "exam_path": "JEE Main → JEE Advanced → JOSAA Counselling",
        "timeline": "12–14 years from Class 6 to Senior Engineer",
    },

    {
        "id": "tech_software_bca_mca",
        "title": "Software Engineer (BCA/MCA Route)",
        "category": "Technology",
        "subcategory": "Software Development",
        "description": "Non-engineering route to software careers. More accessible, still leads to strong tech roles.",
        "difficulty": "Medium",
        "demand": "High",
        "automation_risk": "Medium",
        "remote_potential": "Very High",
        "steps": [
            {"level": 1, "stage": "Class 10 (PCM or Commerce with Maths)", "action": "Secure 60%+. Maths is essential for BCA admission."},
            {"level": 2, "stage": "Class 11–12", "action": "PCM or Commerce with Maths. Focus on Maths and Computer Science if available."},
            {"level": 3, "stage": "BCA (3 years)", "action": "Bachelor of Computer Applications. Learn: C, Java, Python, DBMS, Networking, Web Dev. CGPA matters for MCA/placements."},
            {"level": 4, "stage": "Skill Building (parallel)", "action": "During BCA: build projects, contribute to GitHub, get Internshala internships, complete 1–2 certifications."},
            {"level": 5, "stage": "MCA (2 years) — Optional but Recommended", "action": "Master of Computer Applications. NIMCET exam for top NITs. Alternatively: direct job after BCA at service companies."},
            {"level": 6, "stage": "Entry Role", "action": "Junior Developer / Software Trainee. ₹3–8 LPA at service companies, ₹8–18 LPA at product companies with strong skills."},
            {"level": 7, "stage": "Mid Level (3–5 yrs)", "action": "Software Developer / Module Lead. ₹12–30 LPA."},
            {"level": 8, "stage": "Senior (5+ yrs)", "action": "Senior Developer / Tech Lead. ₹25–60 LPA."},
        ],
        "branches": [
            {"from_step": 3, "title": "Government Job Route", "path": "BCA → SSC CGL / Bank PO / State Govt IT exam → Govt IT Officer"},
            {"from_step": 3, "title": "Teaching", "path": "BCA → MCA → B.Ed or direct → School/College CS Teacher → Professor"},
            {"from_step": 5, "title": "MBA", "path": "MCA → CAT/MAT → MBA → IT Manager / Business Analyst"},
            {"from_step": 6, "title": "Freelancing", "path": "2 yrs exp → Upwork/Fiverr → Web development freelancer → ₹50K–2L/month"},
            {"from_step": 3, "title": "Startup", "path": "BCA + strong skills → Co-found tech startup → Apply to startup accelerators"},
        ],
        "skills_required": ["Programming (Python/Java)", "Web Development (HTML/CSS/JS)", "DBMS/SQL", "Problem Solving"],
        "skills_to_build": ["React / Angular", "Node.js / Django", "Cloud basics", "DSA", "System Design"],
        "free_resources": [
            {"name": "NPTEL MCA Preparation", "url": "https://nptel.ac.in/", "type": "Course"},
            {"name": "The Odin Project", "url": "https://www.theodinproject.com/", "type": "Full Stack Course"},
            {"name": "W3Schools", "url": "https://www.w3schools.com/", "type": "Reference"},
            {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "Course"},
            {"name": "NIMCET Preparation - YouTube PW", "url": "https://www.youtube.com/@PhysicsWallah", "type": "Exam Prep"},
        ],
        "salary_range": {"entry": "₹3–8 LPA", "mid": "₹12–30 LPA", "senior": "₹25–60 LPA"},
        "companies": {
            "service": ["TCS", "Infosys", "Wipro", "Capgemini", "Mphasis", "Hexaware"],
            "product": ["Zoho", "Freshworks", "Juspay", "Swiggy", "Ola"],
            "startups": ["Local/regional tech startups", "Ed-tech companies"],
        },
        "govt_opportunities": ["SSC CGL (Computer Post)", "Bank IT Officer", "State NIC Jobs", "NIELIT"],
        "exam_path": "BCA Entrance (various) → NIMCET (for NIT MCA)",
        "timeline": "5–7 years from Class 12 to stable mid-level role",
    },

    {
        "id": "tech_data_science",
        "title": "Data Scientist / ML Engineer",
        "category": "Technology",
        "subcategory": "AI & Data",
        "description": "One of India's fastest growing fields. Combines statistics, programming and business to extract insights from data.",
        "difficulty": "High",
        "demand": "Very High",
        "automation_risk": "Low",
        "remote_potential": "Very High",
        "steps": [
            {"level": 1, "stage": "Education Foundation", "action": "B.Tech/B.Sc in CS, Maths, Statistics, or Physics. OR BCA/MCA. Strong Maths (Stats, Linear Algebra, Calculus) is non-negotiable."},
            {"level": 2, "stage": "Core Skills", "action": "Python (NumPy, Pandas, Scikit-learn, Matplotlib), SQL, Statistics, ML fundamentals. Take Kaggle courses — all free."},
            {"level": 3, "stage": "Build Portfolio", "action": "3–5 Kaggle competitions (get a bronze/silver medal). 2–3 end-to-end ML projects on GitHub. 1 data blog on Medium/Substack."},
            {"level": 4, "stage": "Specialization", "action": "Choose: NLP / Computer Vision / Time Series / Recommendation Systems / LLM Engineering."},
            {"level": 5, "stage": "Entry Role (0–2 yrs)", "action": "Data Analyst → Junior Data Scientist. ₹5–15 LPA. Focus on real business problems."},
            {"level": 6, "stage": "Mid Level (2–4 yrs)", "action": "Data Scientist / ML Engineer. Build and deploy models in production. ₹15–40 LPA."},
            {"level": 7, "stage": "Senior (4–7 yrs)", "action": "Senior DS / Senior MLE. Own ML systems end-to-end. ₹35–80 LPA."},
            {"level": 8, "stage": "Lead / Principal", "action": "Staff MLE / Principal Data Scientist / Head of AI. ₹80 L – 2 Cr+."},
        ],
        "branches": [
            {"from_step": 4, "title": "AI Research", "path": "Senior DS → PhD at IISc/CMU/Stanford → Research Scientist at DeepMind, Google Brain, Microsoft Research"},
            {"from_step": 4, "title": "MLOps / Platform", "path": "ML Eng → MLOps → ML Platform Engineer. Build infra for ML models at scale."},
            {"from_step": 6, "title": "Product Analytics", "path": "DS → Product Analyst → Product Manager (Data PM) → CPO"},
            {"from_step": 2, "title": "Business Intelligence", "path": "SQL + Tableau/PowerBI → BI Analyst → BI Manager → Data Director"},
            {"from_step": 5, "title": "Freelance / Consulting", "path": "2 yrs exp → Freelance Data Consulting → ₹1–5L/month for enterprise clients"},
        ],
        "skills_required": ["Python", "SQL", "Statistics & Probability", "Machine Learning (Scikit-learn)", "Data Visualization", "Pandas/NumPy"],
        "skills_to_build": ["Deep Learning (TensorFlow/PyTorch)", "Cloud ML (AWS SageMaker/GCP Vertex AI)", "MLflow", "Docker", "Spark for Big Data"],
        "certifications": [
            {"name": "Google Data Analytics Certificate", "platform": "Coursera", "free": False, "audit": True},
            {"name": "Deep Learning Specialization", "platform": "Coursera (Andrew Ng)", "free": False, "audit": True},
            {"name": "Kaggle ML Courses", "platform": "Kaggle", "free": True},
        ],
        "free_resources": [
            {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn", "type": "Course"},
            {"name": "fast.ai", "url": "https://www.fast.ai/", "type": "Course"},
            {"name": "StatQuest (YouTube)", "url": "https://www.youtube.com/@statquest", "type": "Video"},
            {"name": "NPTEL Data Science", "url": "https://nptel.ac.in/", "type": "Course"},
            {"name": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "Course"},
        ],
        "salary_range": {"entry": "₹5–15 LPA", "mid": "₹15–40 LPA", "senior": "₹40–80 LPA", "executive": "₹80 L – 2 Cr+"},
        "companies": {
            "product": ["Google India", "Microsoft", "Amazon", "Flipkart", "Swiggy", "Meesho", "Paytm", "PhonePe", "CRED"],
            "analytics": ["Mu Sigma", "Tiger Analytics", "Fractal Analytics", "LatentView Analytics", "TheMathCompany"],
            "startups": ["Sarvam AI", "Krutrim", "Ola Krutrim", "Yellow.ai", "Haptik"],
        },
        "govt_opportunities": ["DRDO (AI Division)", "ISRO (Space Data)", "NITI Aayog Data Roles", "Ministry of Electronics (AI Mission)"],
        "exam_path": "GATE (CS/DS) for M.Tech in Data Science at IITs/NITs",
        "timeline": "3–5 years to first solid DS role from graduation",
    },

    {
        "id": "tech_cybersecurity",
        "title": "Cybersecurity Engineer",
        "category": "Technology",
        "subcategory": "Cybersecurity",
        "description": "Protecting India's digital infrastructure. Massive demand from banks, IT companies, government, and startups.",
        "difficulty": "High",
        "demand": "Very High",
        "automation_risk": "Low",
        "remote_potential": "High",
        "steps": [
            {"level": 1, "stage": "Education", "action": "B.Tech CSE/IT or BCA. Some enter via Diploma + certifications. Networking basics (TCP/IP, OSI) are must-know."},
            {"level": 2, "stage": "Fundamentals", "action": "Linux, Networking, Scripting (Python/Bash), Operating Systems. TryHackMe + HackTheBox for hands-on practice. Both free tiers available."},
            {"level": 3, "stage": "Specialize", "action": "Choose: Ethical Hacking / SOC Analyst / AppSec / Cloud Security / Malware Analysis / VAPT."},
            {"level": 4, "stage": "Certifications", "action": "CEH (basic), CompTIA Security+ (globally recognized), OSCP (gold standard for penetration testing)."},
            {"level": 5, "stage": "Entry Role (0–2 yrs)", "action": "SOC Analyst / Junior Penetration Tester / Security Analyst. ₹4–12 LPA."},
            {"level": 6, "stage": "Mid Level (2–5 yrs)", "action": "Penetration Tester / Security Engineer / VAPT Specialist. ₹12–30 LPA."},
            {"level": 7, "stage": "Senior (5–8 yrs)", "action": "Senior Security Engineer / Red Team Lead / AppSec Lead. ₹30–70 LPA."},
            {"level": 8, "stage": "Leadership", "action": "CISO / Head of Cybersecurity / Security Director. ₹60 L – 2 Cr+."},
        ],
        "branches": [
            {"from_step": 3, "title": "Bug Bounty", "path": "Skills → Bug Bounty (HackerOne, Bugcrowd) → ₹50K–10L per finding → Freelance security researcher"},
            {"from_step": 5, "title": "Govt / Defense Security", "path": "Security exp → CERT-In / NCIIPC / DRDO Cyber Division / Indian Army Cyber Corps"},
            {"from_step": 3, "title": "Cloud Security", "path": "Security + AWS/Azure → Cloud Security Engineer → Cloud CISO → ₹80L+"},
            {"from_step": 6, "title": "Consulting", "path": "Senior sec eng → Independent consultant → Security audit for banks, startups → ₹5–20L/month"},
        ],
        "skills_required": ["Linux", "Networking (TCP/IP)", "Python/Bash Scripting", "Web Security (OWASP Top 10)", "Vulnerability Assessment"],
        "skills_to_build": ["Cloud Security", "DevSecOps", "Threat Intelligence", "Forensics", "Reverse Engineering"],
        "free_resources": [
            {"name": "TryHackMe", "url": "https://tryhackme.com/", "type": "Hands-on Labs"},
            {"name": "HackTheBox (Free Tier)", "url": "https://www.hackthebox.com/", "type": "Hands-on Labs"},
            {"name": "OWASP", "url": "https://owasp.org/", "type": "Reference"},
            {"name": "Cybersecurity & Infrastructure Security Agency resources", "url": "https://www.cisa.gov/free-cybersecurity-services-and-tools", "type": "Free Tools"},
            {"name": "TCM Security (YouTube)", "url": "https://www.youtube.com/@TCMSecurityAcademy", "type": "Video"},
        ],
        "salary_range": {"entry": "₹4–12 LPA", "mid": "₹12–30 LPA", "senior": "₹30–70 LPA", "executive": "₹60 L – 2 Cr+"},
        "companies": {
            "product": ["Quick Heal", "Seqrite", "Lucideus (now Safe Security)", "Innefu Labs", "Sequretek"],
            "service": ["TCS Cyber Security", "Infosys InfoSec", "Wipro CyberSec", "PwC India", "Deloitte India"],
            "global": ["Palo Alto Networks", "CrowdStrike", "Check Point", "Fortinet"],
        },
        "govt_opportunities": ["CERT-In", "NCIIPC", "Indian Army Cyber Corps", "DRDO CAIR", "NIC Security Team"],
        "exam_path": "CEH (EC-Council) → CompTIA Security+ → OSCP for penetration testing",
        "timeline": "2–4 years to first security role with right certifications",
    },

    # ══════════════════════════════════════════
    #  MEDICAL & HEALTHCARE
    # ══════════════════════════════════════════

    {
        "id": "medical_mbbs",
        "title": "Doctor (MBBS + Specialization)",
        "category": "Healthcare",
        "subcategory": "Medical",
        "description": "India's most respected professional path. NEET is the gateway to all government and private medical colleges.",
        "difficulty": "Very High",
        "demand": "Very High",
        "automation_risk": "Very Low",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Class 6–10", "action": "Build strong Biology, Chemistry, Physics base. Score 90%+ in Science."},
            {"level": 2, "stage": "Class 11–12 (PCB)", "action": "Physics, Chemistry, Biology. NEET coaching mandatory. Free resources: Unacademy, PW. Paid: Aakash, Allen."},
            {"level": 3, "stage": "NEET UG", "action": "National Eligibility cum Entrance Test. 720 marks. Government college: 600+ required for good colleges. Held annually by NTA."},
            {"level": 4, "stage": "MBBS (5.5 years)", "action": "4.5 years academics + 1 year rotating internship. Government colleges: ₹10K–1.5L/yr fees. Private: ₹10–25L/yr."},
            {"level": 5, "stage": "MBBS Internship (1 yr)", "action": "Mandatory clinical rotation across all departments. Stipend: ₹8K–25K/month."},
            {"level": 6, "stage": "NEXT / NEET PG (choose specialization)", "action": "Previously MCI exam, now NEXT. Gives access to MD/MS programs. Rank determines branch and college."},
            {"level": 7, "stage": "MD / MS (3 years)", "action": "Specialization. MD: medicine branches (Dermatology, Psychiatry, Radiology, etc). MS: surgery branches (Ortho, Ophthalmology, ENT, General Surgery)."},
            {"level": 8, "stage": "Super Specialization — DM / MCh", "action": "2–3 years. DM: Cardiology, Nephrology, Neurology. MCh: Cardiac Surgery, Neurosurgery, Plastic Surgery."},
            {"level": 9, "stage": "Practice", "action": "Govt hospital (service + salary), Private hospital (higher pay), Own clinic/nursing home (entrepreneurial)."},
            {"level": 10, "stage": "Career Peak", "action": "Senior Consultant / HOD / Professor + HOD / Medical Director / Hospital Chain Owner."},
        ],
        "branches": [
            {"from_step": 4, "title": "Dermatology + Cosmetology", "path": "MBBS → MD Dermatology → Cosmetic Dermatologist → Own clinic → ₹5–50L/month possible"},
            {"from_step": 4, "title": "Psychiatry", "path": "MBBS → MD Psychiatry → Mental health hospitals, private practice → Huge demand post-COVID"},
            {"from_step": 4, "title": "Radiology / AI in Medicine", "path": "MBBS → MD Radiology → Tele-radiology (remote, very high pay) → AI Radiology tools collaboration"},
            {"from_step": 4, "title": "Medical Education", "path": "MBBS → MD → DNB/Teaching post → Professor → Dean → College Principal"},
            {"from_step": 4, "title": "Healthcare Administration", "path": "MBBS → MBA Hospital Management → CEO of hospital chain → Health startup founder"},
            {"from_step": 4, "title": "Public Health / UPSC", "path": "MBBS → MD Community Medicine → WHO/UNICEF → IAS (Medical Officer route through UPSC)"},
            {"from_step": 7, "title": "Cardiology", "path": "MBBS → MD Medicine → DM Cardiology → Interventional Cardiologist → ₹1–5 Cr/yr"},
            {"from_step": 7, "title": "Orthopaedics", "path": "MBBS → MS Orthopaedics → Sports Medicine / Joint Replacement Specialist → High demand"},
            {"from_step": 7, "title": "Ophthalmology", "path": "MBBS → MS Ophthalmology → LASIK/Cataract surgeon → Retina specialist → Own eye hospital"},
        ],
        "skills_required": ["Biology", "Chemistry", "Clinical Skills", "Patient Communication", "Diagnostic Reasoning"],
        "skills_to_build": ["Research (publications)", "Healthcare Management", "Telemedicine", "Medical AI tools", "Leadership"],
        "free_resources": [
            {"name": "Physics Wallah NEET", "url": "https://www.pw.live/", "type": "Exam Prep"},
            {"name": "Unacademy NEET (Free Content)", "url": "https://unacademy.com/", "type": "Exam Prep"},
            {"name": "NCERT Biology/Chemistry/Physics", "url": "https://ncert.nic.in/", "type": "Textbooks"},
            {"name": "NMC (National Medical Commission)", "url": "https://www.nmc.org.in/", "type": "Regulatory"},
            {"name": "AIIMS OPD Teaching Videos (YouTube)", "url": "https://www.youtube.com/@aiimsofficial", "type": "Learning"},
        ],
        "salary_range": {
            "internship": "₹8K–25K/month (stipend)",
            "junior_doctor": "₹60K–1.5 LPM",
            "specialist": "₹2–8 LPM",
            "super_specialist": "₹5–40 LPM",
            "own_practice": "Unlimited",
        },
        "companies": {
            "government": ["AIIMS", "PGI Chandigarh", "State Medical Colleges", "ESIC Hospitals", "Railway Hospitals"],
            "private": ["Apollo Hospitals", "Fortis Healthcare", "Manipal Hospitals", "Max Healthcare", "Medanta"],
            "research": ["ICMR", "DBT", "AIIMS Research Division"],
        },
        "govt_opportunities": ["UPSC Medical Officer", "State PSC Medical Posts", "ESIC/ECHS", "Armed Forces Medical Services", "Railway Medical Services"],
        "exam_path": "NEET UG → MBBS → NEXT/NEET PG → MD/MS → DM/MCh (optional)",
        "timeline": "13–15 years from Class 11 to becoming a full specialist",
    },

    {
        "id": "medical_pharmacy",
        "title": "Pharmacist / Pharmaceutical Career",
        "category": "Healthcare",
        "subcategory": "Pharmacy",
        "description": "India is the world's pharmacy. Huge opportunities in pharma companies, R&D, regulatory affairs, and hospital pharmacy.",
        "difficulty": "Medium-High",
        "demand": "High",
        "automation_risk": "Medium",
        "remote_potential": "Medium",
        "steps": [
            {"level": 1, "stage": "Class 11–12 (PCB or PCM)", "action": "Physics, Chemistry mandatory. Biology preferred. Score 60%+."},
            {"level": 2, "stage": "D.Pharm (2 years) OR B.Pharm (4 years)", "action": "D.Pharm: direct pharmacy practice. B.Pharm: opens R&D, industry, and further education doors."},
            {"level": 3, "stage": "Registration", "action": "Register with State Pharmacy Council to practice. Required to open pharmacy or work in hospital."},
            {"level": 4, "stage": "Entry Roles", "action": "Retail Pharmacist / Hospital Pharmacist / Quality Control Analyst / Medical Representative. ₹2–6 LPA."},
            {"level": 5, "stage": "M.Pharm (2 years)", "action": "Specialization: Pharmaceutics, Pharmacology, Pharmacognosy, Pharm Analysis, Drug Regulatory Affairs."},
            {"level": 6, "stage": "Industry Roles (Post M.Pharm)", "action": "R&D Scientist / Regulatory Affairs Officer / Quality Assurance Manager / Clinical Research Associate. ₹6–20 LPA."},
            {"level": 7, "stage": "Senior Industry Roles", "action": "Senior R&D / RA Manager / Plant Head / VP Regulatory. ₹20–60 LPA."},
            {"level": 8, "stage": "Own Pharmacy / Franchise", "action": "Open retail pharmacy (₹5–15L investment) or franchise (Apollo Pharmacy, MedPlus, 1mg). ₹30K–3L/month profit."},
        ],
        "branches": [
            {"from_step": 5, "title": "Clinical Research", "path": "M.Pharm → CCRP certification → Clinical Research Associate → CRA Manager → Clinical Director → ₹20–80 LPA"},
            {"from_step": 5, "title": "Regulatory Affairs", "path": "M.Pharm (DRA) → RA Officer → RA Manager → Head of Regulatory Affairs at pharma company"},
            {"from_step": 5, "title": "PhD / Research", "path": "M.Pharm → PhD → Professor + Researcher → CSIR/DBT Scientist"},
            {"from_step": 4, "title": "Medical Representative → Sales Leader", "path": "MR → Senior MR → Area Manager → Zone Manager → National Sales Head → ₹80L+"},
            {"from_step": 3, "title": "Own Pharmacy Business", "path": "D.Pharm + Registration → Retail pharmacy → Wholesale dealership → Distribution chain"},
        ],
        "free_resources": [
            {"name": "NPTEL Pharmaceutical Sciences", "url": "https://nptel.ac.in/", "type": "Course"},
            {"name": "Pharmapedia India (YouTube)", "url": "https://www.youtube.com/@pharmapediaindia", "type": "Video"},
            {"name": "PCI (Pharmacy Council of India)", "url": "https://www.pci.nic.in/", "type": "Regulatory"},
        ],
        "salary_range": {"entry": "₹2–6 LPA", "mid": "₹8–20 LPA", "senior": "₹20–60 LPA", "own_business": "Variable"},
        "companies": {
            "pharma": ["Sun Pharma", "Dr Reddy's", "Cipla", "Lupin", "Aurobindo Pharma", "Biocon", "Glenmark", "Torrent Pharma"],
            "retail": ["Apollo Pharmacy", "MedPlus", "Netmeds", "1mg", "PharmEasy"],
            "hospital": ["Apollo", "Fortis", "Max", "AIIMS Pharmacy"],
        },
        "govt_opportunities": ["ESIC Pharmacist", "Railways Pharmacist", "State Health Department", "CGHS Pharmacist", "Armed Forces Pharmacist"],
        "exam_path": "GPAT (for M.Pharm admission at NITs/Universities) | State CET for B.Pharm",
        "timeline": "4–6 years to stable industry role",
    },

    # ══════════════════════════════════════════
    #  GOVERNMENT & CIVIL SERVICES
    # ══════════════════════════════════════════

    {
        "id": "govt_upsc_ias",
        "title": "IAS / IPS / IFS (UPSC Civil Services)",
        "category": "Government",
        "subcategory": "Civil Services",
        "description": "The most prestigious government career in India. Enormous power, prestige, and service to nation. Long preparation but life-changing outcome.",
        "difficulty": "Extremely High",
        "demand": "Always High (limited seats ~900/year)",
        "automation_risk": "Very Low",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Graduation (Any Stream)", "action": "UPSC requires graduation in any subject. Many toppers: Engineering / Law / Humanities. Focus on reading habit, current affairs from Day 1."},
            {"level": 2, "stage": "Know the Exam", "action": "3 stages: Prelims (objective) → Mains (written) → Interview (Personality Test). Total: ~2 years of serious preparation for most."},
            {"level": 3, "stage": "Prelims Preparation", "action": "NCERT Class 6–12 (all subjects) → Standard books (Laxmikanth, Spectrum, G.C. Leong) → 5–10 years previous papers → Current affairs daily (The Hindu/Indian Express)."},
            {"level": 4, "stage": "Prelims (Stage 1)", "action": "2 papers: GS (General Studies) + CSAT. 200 marks each. CSAT is qualifying only (33%). GS score decides cut-off."},
            {"level": 5, "stage": "Mains (Stage 2)", "action": "9 papers: Essay + GS 1/2/3/4 + Optional Subject (2 papers) + Language papers. 1750 marks. Writing quality matters enormously."},
            {"level": 6, "stage": "Interview (Stage 3)", "action": "Personality Test (275 marks). Board of UPSC members. Tests character, leadership, awareness, communication."},
            {"level": 7, "stage": "Training (Post Selection)", "action": "IAS: LBSNAA Mussoorie. IPS: SVP NPA Hyderabad. IFS: FSOI + Lal Bahadur Shastri National Academy."},
            {"level": 8, "stage": "Posting & Career", "action": "SDM → DM/Collector → Secretary → Chief Secretary (State) | Under Secretary → Joint Secretary → Additional Secretary → Secretary (Centre) | Ambassador (IFS)"},
        ],
        "branches": [
            {"from_step": 1, "title": "IAS (Indian Administrative Service)", "path": "State cadre → District Collector → Commissioner → Secretary → Chief Secretary. India's most powerful administrative role."},
            {"from_step": 1, "title": "IPS (Indian Police Service)", "path": "SP → DIG → IG → DGP. Lead police forces, CBI, IB, NSG."},
            {"from_step": 1, "title": "IFS (Indian Foreign Service)", "path": "Third Secretary → Second Secretary → First Secretary → Counsellor → Ambassador/High Commissioner. Represent India globally."},
            {"from_step": 1, "title": "IRS (Indian Revenue Service)", "path": "Income Tax / Customs → Commissioner → Chief Commissioner. High earnings potential in service."},
            {"from_step": 1, "title": "After 1–2 Failed Attempts", "path": "State PSC (PCS/KAS/MPPSC etc) → State administrative services. Equivalent dignity, slightly lower national scope."},
        ],
        "skills_required": ["Current Affairs", "Essay Writing", "Optional Subject Depth", "Answer Writing", "Mental Stamina"],
        "skills_to_build": ["Leadership", "Public Speaking", "Decision Making", "Crisis Management", "Language Skills (Hindi + regional)"],
        "free_resources": [
            {"name": "UPSC Official Site", "url": "https://upsc.gov.in/", "type": "Official"},
            {"name": "Drishti IAS (Free)", "url": "https://www.drishtiias.com/", "type": "Study Material"},
            {"name": "Vision IAS Free Resources", "url": "https://www.visionias.in/", "type": "Study Material"},
            {"name": "NCERT Books (Free PDF)", "url": "https://ncert.nic.in/textbook.php", "type": "Books"},
            {"name": "The Hindu ePaper (Subsidized for students)", "url": "https://www.thehindu.com/", "type": "Current Affairs"},
            {"name": "Unacademy UPSC (Free Lectures)", "url": "https://unacademy.com/", "type": "Video Lectures"},
            {"name": "StudyIQ IAS (YouTube)", "url": "https://www.youtube.com/@StudyIQ", "type": "Video"},
        ],
        "salary_range": {
            "training": "₹56,100/month (7th Pay Commission Level 10)",
            "sdm_dm": "₹56,100–₹1,31,100/month + perks",
            "secretary": "₹1,44,200 + DA + perks (housing, car, staff, etc)",
            "total_package": "Equivalent to ₹30–50 LPA when all benefits counted",
        },
        "govt_opportunities": ["IAS", "IPS", "IFS", "IRS", "IRAS", "IDAS", "IES", "IRTS", "IIS"],
        "exam_path": "UPSC Prelims (June) → Mains (September) → Interview (March–May) → Results (May)",
        "timeline": "1–4 years of dedicated preparation after graduation. Max 6 attempts (General), 9 (OBC), Unlimited (SC/ST)",
    },

    {
        "id": "govt_bank_finance",
        "title": "Banking & Finance Government Career",
        "category": "Government",
        "subcategory": "Banking",
        "description": "PSU banks, RBI, SEBI — stable, respected, pensioned careers with good work-life balance.",
        "difficulty": "Medium-High",
        "demand": "Very High",
        "automation_risk": "Medium",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Education", "action": "Graduation in any stream. Commerce/Maths background helps but not mandatory. 60% marks preferred."},
            {"level": 2, "stage": "Choose Your Target", "action": "IBPS PO (Bank PO) / IBPS Clerk / SBI PO / SBI Clerk / RBI Grade B / RBI Assistant / SEBI Grade A / NABARD Grade A."},
            {"level": 3, "stage": "Prepare", "action": "Quantitative Aptitude, Reasoning, English, Banking Awareness, Computer. Mains adds Data Analysis, General/Economy/Banking Awareness essay."},
            {"level": 4, "stage": "IBPS PO / SBI PO (Entry Level Management)", "action": "Join as Probationary Officer. Training period 2 years. Posted anywhere in India."},
            {"level": 5, "stage": "Growth Path (PO Route)", "action": "PO → Officer Scale 1 → Officer Scale 2 (Branch Manager) → Scale 3 → AGM → DGM → GM → ED → MD/CEO"},
            {"level": 6, "stage": "RBI Grade B (Elite Route)", "action": "Phase 1 + Phase 2 (very tough). Posted at RBI offices. ₹35,150/month + perks. Path: Grade B → C → D (Executive Director) → Deputy Governor → Governor."},
        ],
        "branches": [
            {"from_step": 2, "title": "SEBI Grade A", "path": "Graduation → SEBI exam → Securities market regulation → Senior Officer → Executive Director → Chairman"},
            {"from_step": 2, "title": "NABARD Grade A", "path": "Agriculture/Rural development banking → Rural lending focus → ₹28,150+"},
            {"from_step": 4, "title": "Private Banking", "path": "1–2 yrs PSU bank → HDFC/ICICI/Axis/Kotak → Better salary, faster growth, tougher targets"},
            {"from_step": 4, "title": "Finance / CA Route", "path": "Banking + CA = powerful combo → Big 4 / Investment Banking / CFO track"},
            {"from_step": 2, "title": "Insurance Sector", "path": "LIC AAO / IRDA / GIC / New India Assurance → Insurance officer career"},
        ],
        "free_resources": [
            {"name": "IBPS Official", "url": "https://www.ibps.in/", "type": "Official"},
            {"name": "Oliveboard (Free Mocks)", "url": "https://www.oliveboard.in/", "type": "Mock Tests"},
            {"name": "Adda247 (YouTube + Free Content)", "url": "https://www.adda247.com/", "type": "Prep"},
            {"name": "Testbook (Free Tests)", "url": "https://testbook.com/", "type": "Mock Tests"},
            {"name": "RBI Grade B Prep - PW", "url": "https://www.pw.live/", "type": "Exam Prep"},
        ],
        "salary_range": {
            "ibps_clerk": "₹11,765–31,540/month + DA + HRA",
            "ibps_po": "₹23,700–42,020/month + allowances",
            "rbi_grade_b": "₹35,150/month + ₹1500 grade pay + perks",
            "sebi_grade_a": "₹28,150/month + perks",
            "total_ctc": "IBPS PO total ~₹7–9 LPA | RBI Grade B ~₹14–16 LPA with perks",
        },
        "companies": {
            "banks": ["SBI", "PNB", "Bank of Baroda", "Canara Bank", "Union Bank", "HDFC Bank (private)", "ICICI Bank (private)"],
            "regulators": ["RBI", "SEBI", "NABARD", "SIDBI", "EXIM Bank", "NHB"],
        },
        "exam_path": "IBPS PO: Prelims → Mains → Interview | SBI PO: Phase 1 → Phase 2 → GD+PI | RBI Grade B: Phase 1 → Phase 2 → Interview",
        "timeline": "6–18 months preparation for first crack. Most crack in 1–2 attempts.",
    },

    # ══════════════════════════════════════════
    #  ENGINEERING (NON-CS)
    # ══════════════════════════════════════════

    {
        "id": "engineering_civil",
        "title": "Civil Engineer",
        "category": "Engineering",
        "subcategory": "Civil Engineering",
        "description": "Building India's infrastructure: roads, bridges, dams, airports, smart cities, metro systems.",
        "difficulty": "Medium-High",
        "demand": "High",
        "automation_risk": "Low-Medium",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Class 11–12 (PCM)", "action": "Focus on Maths and Physics. JEE Mains for admission to NITs/IITs/Govt colleges. State entrance for state colleges."},
            {"level": 2, "stage": "B.Tech / B.E. Civil Engineering (4 years)", "action": "Structures, Geotechnical, Transportation, Environmental, Construction Management, Hydraulics. Internship on construction site is essential."},
            {"level": 3, "stage": "Licensure", "action": "Register with Institute of Engineers India (IEI). Get AMIE or pursue Graduate Engineer from state."},
            {"level": 4, "stage": "Entry Roles (0–3 yrs)", "action": "Site Engineer / Junior Engineer / Structural Engineer / Quality Engineer. ₹3–8 LPA."},
            {"level": 5, "stage": "Mid Level (3–7 yrs)", "action": "Project Engineer / Senior Site Engineer / Design Engineer. ₹8–18 LPA."},
            {"level": 6, "stage": "Senior Level (7–12 yrs)", "action": "Project Manager / Senior Design Engineer / DGM Civil. ₹18–40 LPA."},
            {"level": 7, "stage": "Leadership", "action": "General Manager / VP Infrastructure / Director Projects. ₹40–80 LPA."},
            {"level": 8, "stage": "Own Business", "action": "Civil Contractor → Construction firm → Infrastructure company → Real estate developer."},
        ],
        "branches": [
            {"from_step": 2, "title": "GATE → M.Tech → DRDO/ISRO/Govt R&D", "path": "B.Tech → GATE Civil → M.Tech (IIT/NIT) → Scientist/Researcher/Professor"},
            {"from_step": 2, "title": "Government Jobs (SSC JE / State JE)", "path": "B.Tech/Diploma → SSC JE / State PWD JE → Junior Engineer → Assistant Engineer → Executive Engineer"},
            {"from_step": 2, "title": "UPSC ESE (Engineering Services Exam)", "path": "B.Tech → UPSC ESE → Assistant Executive Engineer in Central Govt → ₹56,100+ + perks"},
            {"from_step": 4, "title": "Real Estate / Construction Business", "path": "Site exp → Civil contractor license → Own firm → Real estate developer"},
            {"from_step": 4, "title": "Structural Consulting", "path": "Structural eng exp → Independent consulting firm → High value projects → ₹50L–2Cr+"},
            {"from_step": 2, "title": "Urban Planning / Smart Cities", "path": "B.Tech → M.Plan or M.Tech Urban → Smart City Mission roles → RERA / Town Planning"},
        ],
        "free_resources": [
            {"name": "NPTEL Civil Engineering", "url": "https://nptel.ac.in/", "type": "Course"},
            {"name": "SSC JE Official", "url": "https://ssc.nic.in/", "type": "Govt Exam"},
            {"name": "GATE CE Prep - Made Easy YouTube", "url": "https://www.youtube.com/@MadeEasyPrimeOfficial", "type": "Exam Prep"},
            {"name": "AutoCAD Free Trial + Tutorials", "url": "https://www.autodesk.com/", "type": "Software"},
        ],
        "salary_range": {"entry": "₹3–8 LPA", "mid": "₹8–18 LPA", "senior": "₹18–40 LPA", "leadership": "₹40–80 LPA"},
        "companies": {
            "infrastructure": ["L&T Construction", "DLF", "Shapoorji Pallonji", "Gammon India", "AFCONS Infrastructure"],
            "govt": ["NHAI", "RITES", "IRCON", "CPWD", "NBCC", "HPCL Civil Wing"],
            "consulting": ["AECOM India", "Jacobs India", "Mott MacDonald India"],
        },
        "govt_opportunities": ["PWD (State)", "NHAI", "Railways Civil Dept", "UPSC ESE", "SSC JE", "CPWD", "Smart Cities Mission"],
        "exam_path": "JEE Mains → B.Tech → GATE/SSC JE/UPSC ESE",
        "timeline": "4–6 years to first job; 10–15 years to leadership",
    },

    # ══════════════════════════════════════════
    #  BUSINESS & COMMERCE
    # ══════════════════════════════════════════

    {
        "id": "commerce_ca",
        "title": "Chartered Accountant (CA)",
        "category": "Finance & Commerce",
        "subcategory": "Accounting & Audit",
        "description": "India's most respected finance credential. CA opens doors to Big 4, CFO roles, IND AS, FEMA, taxation, and more.",
        "difficulty": "Very High",
        "demand": "Very High",
        "automation_risk": "Medium (AI assists but doesn't replace)",
        "remote_potential": "Medium",
        "steps": [
            {"level": 1, "stage": "Class 11–12 (Commerce)", "action": "Accounts, Economics, Business Studies, Maths. Score 60%+. PCM students also eligible."},
            {"level": 2, "stage": "CA Foundation", "action": "Register with ICAI after Class 12. 4 papers: Accounts, Law, Maths/Stats, Economics. Pass both groups (200 marks each)."},
            {"level": 3, "stage": "CA Intermediate", "action": "8 papers in 2 groups. Accounts, Law, Costing, Taxation, Advanced Accounts, Audit, Financial Management, IT/SM. Pass both groups."},
            {"level": 4, "stage": "Articleship (3 years)", "action": "Mandatory practical training under a CA firm. Small firms: tax + audit work. Big 4 (Deloitte/PwC/EY/KPMG): industry exposure, better placement."},
            {"level": 5, "stage": "CA Final", "action": "8 papers: 2 groups. FR, SFM, Audit, Law, Costing + 3 electives (Risk, Global FR, Economics for Finance, etc). Toughest CA exam."},
            {"level": 6, "stage": "Membership (ACA)", "action": "Associate Chartered Accountant. Can practice independently or join industry."},
            {"level": 7, "stage": "Entry Roles", "action": "Big 4 (₹7–12 LPA) / Mid-firms (₹5–8 LPA) / Industry (₹8–15 LPA) / Own practice."},
            {"level": 8, "stage": "Growth", "action": "Senior Associate → Manager → Senior Manager → Director / Partner at firms. OR CFO track in industry."},
        ],
        "branches": [
            {"from_step": 6, "title": "Big 4 Career", "path": "Articleship at Big 4 → Associate → Senior → Manager → Senior Manager → Director → Partner → ₹1–5 Cr+ as Partner"},
            {"from_step": 6, "title": "CFO Track", "path": "CA → Industry (Finance Manager) → Finance Controller → VP Finance → CFO. ₹80L–5Cr at large corporates."},
            {"from_step": 6, "title": "Investment Banking", "path": "CA + CFA → I-banking at Goldman Sachs India/Morgan Stanley/Axis Capital → ₹40L–1.5 Cr+"},
            {"from_step": 6, "title": "Own Practice", "path": "CA → Setup practice → Taxation + Audit clients → Grow firm → Partner with CAs → ₹5L–1Cr+/month possible"},
            {"from_step": 6, "title": "ICAI International", "path": "ACA → ACCA (UK) → CPA (USA) → International finance career at MNCs"},
            {"from_step": 3, "title": "CS (Company Secretary) Combo", "path": "CA Foundation + CS Foundation simultaneously → Both qualifications → Powerful legal+finance combo"},
        ],
        "free_resources": [
            {"name": "ICAI Official Study Material", "url": "https://www.icai.org/", "type": "Official Study Material"},
            {"name": "CA Foundation Free Videos - Unacademy", "url": "https://unacademy.com/", "type": "Video Lectures"},
            {"name": "ICAI Virtual Classes (Free for students)", "url": "https://www.icai.org/post/virtual-classes", "type": "Free Classes"},
            {"name": "VG Learning Destination (YouTube)", "url": "https://www.youtube.com/@VGLearningDestination", "type": "Video"},
        ],
        "salary_range": {
            "fresher_ca": "₹7–18 LPA",
            "big4_manager": "₹25–50 LPA",
            "big4_director": "₹60L–1.2 Cr",
            "big4_partner": "₹1.5–5 Cr+",
            "cfo_large_corp": "₹80L–5 Cr",
            "own_practice": "₹5L–50L+/year (variable)",
        },
        "companies": {
            "big4": ["Deloitte India", "PricewaterhouseCoopers (PwC) India", "Ernst & Young (EY) India", "KPMG India"],
            "indian_firms": ["Grant Thornton", "S.R. Batliboi", "Lodha & Co", "Walker Chandiok"],
            "corporates": ["Reliance Industries", "Tata Group Finance", "Infosys Finance", "HDFC Bank Treasury"],
        },
        "govt_opportunities": ["CAG (Comptroller & Auditor General)", "SFIO", "SEBI", "Income Tax Department", "Company Law Board"],
        "exam_path": "CA Foundation → CA Intermediate → Articleship (3 yrs) → CA Final → ACA/FCA",
        "timeline": "5–6 years minimum. Some take 7–8 years. Average attempt rate: 2–3 per paper.",
    },

    {
        "id": "business_mba",
        "title": "MBA / Business Management",
        "category": "Business",
        "subcategory": "Management",
        "description": "MBA from IIM is a game-changer. Even tier-2 MBA opens leadership, consulting, marketing, and finance doors.",
        "difficulty": "Medium-High",
        "demand": "Very High",
        "automation_risk": "Low",
        "remote_potential": "Medium",
        "steps": [
            {"level": 1, "stage": "Graduation", "action": "Any bachelor's degree with 50%+. Work experience of 1–3 years significantly boosts CAT score value and IIM calls."},
            {"level": 2, "stage": "Work Experience (Recommended)", "action": "1–3 years work exp before MBA. IIMs prefer: 24–36 months. Freshers join but have lower salary leverage."},
            {"level": 3, "stage": "Entrance Exam", "action": "CAT (IIMs) → Scores used by 100+ colleges. Also: XAT (XLRI), SNAP (Symbiosis), MAT, CMAT, NMAT, GMAT (international/ISB)."},
            {"level": 4, "stage": "MBA Program (2 years)", "action": "Year 1: Core (Finance, Marketing, HR, Operations, Strategy, Quant). Year 2: Specialization + Summer Internship (crucial for placement)."},
            {"level": 5, "stage": "Summer Internship (After Year 1)", "action": "2-month internship. IIM-A/B/C: McKinsey, BCG, Bain, Goldman Sachs, etc. Stipend: ₹1–5L/month. Most convert to PPO (Pre-Placement Offer)."},
            {"level": 6, "stage": "Placement (Post MBA)", "action": "IIM A/B/C: ₹25–90 LPA average. Consulting, Finance, FMCG, Tech are top hirers. Tier-2: ₹8–20 LPA."},
            {"level": 7, "stage": "MBA Career Tracks", "action": "Consulting / Finance (IB, PE, VC) / Marketing / General Management / Operations / Entrepreneurship."},
        ],
        "branches": [
            {"from_step": 6, "title": "Management Consulting", "path": "IIM + Consulting intern → McKinsey/BCG/Bain → Associate → Engagement Manager → Principal → Partner → ₹1–5 Cr+"},
            {"from_step": 6, "title": "Investment Banking", "path": "IIM Finance → Goldman/JPMorgan/Axis Capital → Analyst → Associate → VP → MD → ₹1–3 Cr+"},
            {"from_step": 6, "title": "FMCG Marketing", "path": "MBA Marketing → HUL/P&G/Nestlé/Marico → Brand Manager → Marketing Director → CMO"},
            {"from_step": 6, "title": "VC / PE", "path": "MBA + 3 yrs experience → VC firm (Sequoia/Nexus/Elevation) → Investment Analyst → Partner → Run fund"},
            {"from_step": 6, "title": "Startup Founder", "path": "IIM degree + network → Co-found startup → Seed funding from IIM alumni → Scale"},
            {"from_step": 3, "title": "ISB (Hyderabad)", "path": "5+ yrs work exp → GMAT 700+ → ISB 1-year MBA → ₹20–50 LPA post-MBA. Top for experienced professionals."},
        ],
        "free_resources": [
            {"name": "CAT Official", "url": "https://iimcat.ac.in/", "type": "Official"},
            {"name": "2IIM CAT Prep (Free + Paid)", "url": "https://www.2iim.com/", "type": "Prep"},
            {"name": "Career Launcher Free Resources", "url": "https://www.careerlauncher.com/", "type": "Prep"},
            {"name": "IIMA Podcast / YouTube", "url": "https://www.youtube.com/@IIMAhmedabad", "type": "Learning"},
            {"name": "HBS Online Free Courses", "url": "https://online.hbs.edu/subjects/free-online-business-courses/", "type": "Course"},
        ],
        "salary_range": {
            "iim_abc_fresher": "₹25–90 LPA",
            "iim_abc_5yrs_exp": "₹60L–1.5 Cr+",
            "tier2_mba": "₹8–20 LPA",
            "consulting_partner": "₹2–10 Cr+",
            "corporate_ceo": "₹5–50 Cr+",
        },
        "companies": {
            "consulting": ["McKinsey & Company", "BCG", "Bain & Company", "Deloitte Consulting", "EY Parthenon", "Kearney"],
            "finance": ["Goldman Sachs India", "Morgan Stanley India", "Axis Capital", "Kotak Investment Banking"],
            "fmcg": ["HUL", "P&G India", "Nestlé India", "Marico", "Dabur", "ITC"],
            "tech": ["Google India (Strategy)", "Amazon (Business roles)", "Microsoft", "Flipkart (Strategy/Operations)"],
        },
        "exam_path": "CAT (Nov) → GD/PI (Jan–Mar) → Results (Apr–May)",
        "timeline": "2 years MBA + 1 year work before = 3 years to transformed career",
    },

    # ══════════════════════════════════════════
    #  LOCAL BUSINESS PATHS (UNIQUE TO CREVR-TREE)
    # ══════════════════════════════════════════

    {
        "id": "business_retail_shop",
        "title": "Retail Business / Dukaan Setup (Indian Context)",
        "category": "Business",
        "subcategory": "Local Business",
        "description": "Start a local shop, grocery, medical store, electronics shop, or franchise. India's retail sector = ₹80 lakh crore market.",
        "difficulty": "Low-Medium",
        "demand": "Always",
        "automation_risk": "Low",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Business Idea Validation", "action": "Identify demand in your locality. Talk to 20 potential customers. Check competition. Low competition + high need = good."},
            {"level": 2, "stage": "Legal Registration", "action": "Shop and Establishment Act registration at local Municipal Corporation (₹500–2000, varies by state). Simple process, usually same day."},
            {"level": 3, "stage": "GST Registration (if turnover > ₹20L/yr)", "action": "GST Portal: gst.gov.in → Free registration → Takes 3–7 working days. Need PAN + Aadhaar + Bank account + Shop address proof."},
            {"level": 4, "stage": "FSSAI License (Food businesses)", "action": "If selling any food item → FSSAI Basic license (₹100/yr) at fssai.gov.in. State license for larger operations. Required by law."},
            {"level": 5, "stage": "Udyam Registration (MSME)", "action": "Register at udyamregistration.gov.in → Free → Unlocks: MSME loans at 8–12% interest, govt tenders, priority credit, subsidies."},
            {"level": 6, "stage": "Bank Account & Business Finance", "action": "Current account at any bank. MUDRA Loan (Shishu: up to ₹50K, Kishor: ₹50K–5L, Tarun: ₹5L–10L) from PM MUDRA Yojana — no collateral."},
            {"level": 7, "stage": "Source Products", "action": "For FMCG: Local distributor/stockist contact. For electronics: Wholesale markets (Nehru Place Delhi, SP Road Bangalore, Lamington Rd Mumbai). For pharma: C&F agent."},
            {"level": 8, "stage": "Digital Presence", "action": "Google Business Profile (free) → WhatsApp Business (free) → Meesho/JioMart seller for online orders → Get listed on Swiggy Instamart / Zepto (for grocery)."},
            {"level": 9, "stage": "Growth", "action": "Expand inventory → Hire helper → Open second outlet → Become area distributor → Franchise model."},
        ],
        "branches": [
            {"from_step": 3, "title": "Medical/Pharma Store", "path": "D.Pharm license needed → Drug License from state → FSSAI for supplements → Become franchise of Apollo/MedPlus or independent"},
            {"from_step": 5, "title": "Franchise Business", "path": "MSME + capital → Contact: Amul (₹2–5L inv), DTDC Courier, Jio Point, PM Jan Aushadhi (medical store)"},
            {"from_step": 6, "title": "E-Commerce Seller", "path": "Products → Amazon/Flipkart seller registration → Start selling online → GST required → Scale to ₹10L+/month"},
            {"from_step": 1, "title": "Agri-Based Business", "path": "Farm / Food processing → FPO registration → PM Formalisation support → APEDA registration for exports"},
        ],
        "govt_schemes": [
            {"name": "PM MUDRA Yojana", "url": "https://www.mudra.org.in/", "benefit": "Collateral-free loan up to ₹10 lakh"},
            {"name": "PM SVANidhi", "url": "https://pmsvanidhi.mohua.gov.in/", "benefit": "₹10K–50K microloan for street vendors"},
            {"name": "Udyam Registration", "url": "https://udyamregistration.gov.in/", "benefit": "Free MSME certificate, unlocks schemes"},
            {"name": "Stand-Up India Scheme", "url": "https://www.standupmitra.in/", "benefit": "₹10L–1Cr loan for SC/ST/Women entrepreneurs"},
            {"name": "Startup India", "url": "https://www.startupindia.gov.in/", "benefit": "Tax benefits, IPR support, fund access for startups"},
            {"name": "GeM Portal", "url": "https://gem.gov.in/", "benefit": "Sell to government directly — huge buyer base"},
        ],
        "free_resources": [
            {"name": "GST Official Portal", "url": "https://www.gst.gov.in/", "type": "Govt Portal"},
            {"name": "Ministry of MSME", "url": "https://msme.gov.in/", "type": "Schemes & Support"},
            {"name": "FSSAI Registration", "url": "https://foscos.fssai.gov.in/", "type": "Food License"},
            {"name": "Google Business Profile", "url": "https://business.google.com/", "type": "Free Digital Presence"},
            {"name": "Startup India Hub", "url": "https://www.startupindia.gov.in/", "type": "Resources & Mentorship"},
        ],
        "salary_range": {
            "small_shop": "₹15K–50K/month profit",
            "growing_shop": "₹50K–2L/month",
            "franchise_chain": "₹2L–10L/month",
            "distributor": "₹5L–50L/month (volume based)",
        },
        "timeline": "Can start within 1–2 weeks of registration. Profitable in 3–12 months.",
    },

    # ══════════════════════════════════════════
    #  LAW
    # ══════════════════════════════════════════

    {
        "id": "law_llb",
        "title": "Lawyer / Legal Career (LLB)",
        "category": "Law",
        "subcategory": "Legal Practice",
        "description": "Law is the backbone of democracy and business. India has 1.7M+ lawyers with growing demand in corporate law, litigation, IPR, and human rights.",
        "difficulty": "Medium-High",
        "demand": "High",
        "automation_risk": "Low-Medium",
        "remote_potential": "Medium",
        "steps": [
            {"level": 1, "stage": "After 12th (CLAT Route)", "action": "5-year integrated BA.LLB / BBA.LLB / BSc.LLB via CLAT / AILET / LSAT India. National Law Universities are top tier."},
            {"level": 2, "stage": "OR After Graduation (3-year LLB)", "action": "Any graduation + 3-year LLB. Slower but available to all streams. Delhi University, Symbiosis, Amity are popular."},
            {"level": 3, "stage": "Bar Council Enrollment", "action": "Pass State Bar Council exam → Enroll as Advocate. Required to practice in courts."},
            {"level": 4, "stage": "Internships (During Study)", "action": "Court internship with senior advocate + Law firm internship. Both crucial. Apply to AZB, Cyril Amarchand, Shardul Amarchand, Khaitan."},
            {"level": 5, "stage": "Entry Roles", "action": "Junior Advocate (₹10K–50K/month initially — grows fast) / Law firm Associate (₹6–15 LPA) / Corporate Legal (₹8–20 LPA) / Judicial Services."},
            {"level": 6, "stage": "Growth", "action": "Associate → Senior Associate → Partner at law firm. OR Court advocate → Senior Advocate designation. OR Corporate: Legal Manager → General Counsel → CLO."},
        ],
        "branches": [
            {"from_step": 4, "title": "Corporate Law", "path": "Law firm internship → Associate at AZB/Cyril Amarchand/Khaitan → Senior Associate → Partner → ₹2–10 Cr+ as Partner"},
            {"from_step": 4, "title": "Litigation", "path": "Junior under senior advocate → District Court → High Court → Supreme Court → Senior Advocate designation (prestigious, by SC committee)"},
            {"from_step": 2, "title": "Judicial Services", "path": "LLB + state Judicial Service exam → Civil Judge / JMFC → District Judge → High Court Judge → Supreme Court Judge"},
            {"from_step": 4, "title": "IPR / Patent Law", "path": "LLB + Science background → Patent Agent exam (CGPDTM) → Patent Law firm → IP Head at tech company"},
            {"from_step": 4, "title": "Legal Tech / LegalOps", "path": "LLB + Tech skills → Legal Tech startup → Contract management tools → CLM role at tech company → High growth area"},
            {"from_step": 2, "title": "UPSC Route", "path": "LLB → UPSC Law Optional → IAS/IPS → Legal regulatory roles → Indian Legal Service"},
        ],
        "free_resources": [
            {"name": "CLAT Official", "url": "https://consortiumofnlus.ac.in/", "type": "Exam Info"},
            {"name": "Bar and Bench (Legal News)", "url": "https://www.barandbench.com/", "type": "Legal News"},
            {"name": "SCC Online (Student Access via College)", "url": "https://www.scconline.com/", "type": "Case Law Database"},
            {"name": "Indian Kanoon (Free Case Law)", "url": "https://indiankanoon.org/", "type": "Free Legal Resource"},
            {"name": "NALSAR / NLU YouTube Lectures", "url": "https://www.youtube.com/", "type": "Video Lectures"},
        ],
        "salary_range": {
            "fresher_court": "₹10K–30K/month (grows significantly with experience)",
            "law_firm_associate": "₹6–15 LPA",
            "senior_associate": "₹20–50 LPA",
            "partner": "₹80L–5 Cr+",
            "inhouse_counsel": "₹15–60 LPA",
            "gc_clo": "₹1–5 Cr",
        },
        "companies": {
            "top_firms": ["AZB & Partners", "Cyril Amarchand Mangaldas", "Shardul Amarchand Mangaldas", "Khaitan & Co", "JSA Advocates", "Trilegal"],
            "inhouse": ["Reliance Legal", "Tata Legal", "Infosys Legal", "HDFC Bank Legal"],
            "govt": ["Ministry of Law", "Attorney General's Office", "Solicitor General", "Law Commission"],
        },
        "exam_path": "CLAT (for 5-yr integrated) OR State Judicial Service Exam (after LLB)",
        "timeline": "5–8 years to stable career. Court litigation takes 10–15 years to be well-established.",
    },

    # ══════════════════════════════════════════
    #  CREATIVE & MEDIA
    # ══════════════════════════════════════════

    {
        "id": "creative_design_uiux",
        "title": "UI/UX Designer / Product Designer",
        "category": "Creative",
        "subcategory": "Design",
        "description": "Design the apps and websites Indians use daily. Booming demand from startups and tech companies. Portfolio > degree.",
        "difficulty": "Medium",
        "demand": "Very High",
        "automation_risk": "Low (AI assists, not replaces)",
        "remote_potential": "Very High",
        "steps": [
            {"level": 1, "stage": "Foundation", "action": "Any degree helps but not required. Start learning Figma (free) today. No gatekeeping in design — portfolio is everything."},
            {"level": 2, "stage": "Core Skills", "action": "Figma (must), User Research, Wireframing, Prototyping, Design Thinking, Usability Testing, Visual Design basics."},
            {"level": 3, "stage": "Build Portfolio", "action": "3–5 case studies. Include: Problem → Research → Sketches → Wireframes → Final Design → Results. Add to Behance/Dribbble."},
            {"level": 4, "stage": "Specialize", "action": "Choose: Mobile App Design / Web Design / SaaS Product / Fintech UI / Healthcare UX / Gaming UI."},
            {"level": 5, "stage": "Entry Role (0–2 yrs)", "action": "Junior UI/UX Designer / Product Design Intern → Designer. ₹4–12 LPA."},
            {"level": 6, "stage": "Mid Level (2–4 yrs)", "action": "UI/UX Designer / Senior Designer. Own features. ₹12–30 LPA."},
            {"level": 7, "stage": "Senior / Lead (4–7 yrs)", "action": "Senior Designer / Design Lead / UX Architect. ₹30–70 LPA."},
            {"level": 8, "stage": "Leadership", "action": "Principal Designer / Head of Design / VP Design / Chief Design Officer. ₹70L–2 Cr+."},
        ],
        "branches": [
            {"from_step": 3, "title": "Freelancing", "path": "Portfolio → Upwork/Fiverr/Toptal → International clients → ₹1–5L/month. Very viable early."},
            {"from_step": 6, "title": "Product Management", "path": "Senior Designer → Transition to PM. Design background = huge PM advantage. → ₹30–80 LPA"},
            {"from_step": 4, "title": "Design Systems", "path": "Design System Specialist → DesignOps → ₹50L+ at large tech companies"},
            {"from_step": 4, "title": "UX Research", "path": "UX Researcher → Senior Researcher → Head of Research → ₹40–80 LPA"},
            {"from_step": 3, "title": "Motion Design / Video", "path": "UI/UX + After Effects → Motion Designer → Marketing agencies / startups → ₹8–25 LPA"},
        ],
        "free_resources": [
            {"name": "Figma (Free Plan)", "url": "https://www.figma.com/", "type": "Tool"},
            {"name": "Google UX Design Certificate (Audit Free)", "url": "https://www.coursera.org/professional-certificates/google-ux-design", "type": "Course"},
            {"name": "DesignWithAryan (YouTube Hindi)", "url": "https://www.youtube.com/@DesignWithAryan", "type": "Video"},
            {"name": "Laws of UX", "url": "https://lawsofux.com/", "type": "Reference"},
            {"name": "Behance (Portfolio)", "url": "https://www.behance.net/", "type": "Portfolio"},
            {"name": "Dribbble (Portfolio)", "url": "https://dribbble.com/", "type": "Portfolio"},
        ],
        "salary_range": {"entry": "₹4–12 LPA", "mid": "₹12–30 LPA", "senior": "₹30–70 LPA", "leadership": "₹70L–2 Cr+"},
        "companies": {
            "product": ["Swiggy", "Zomato", "PhonePe", "CRED", "Meesho", "Razorpay", "Groww", "Zerodha"],
            "service": ["Infosys Design Studio", "Wipro Design", "Accenture Song", "Frog Design"],
            "startups": ["Vokal", "Bounce", "Vedantu", "Doubtnut"],
        },
        "exam_path": "No mandatory exam. NID / IDC IIT for formal design degree. Portfolio is passport.",
        "timeline": "6 months–2 years to first design job with strong portfolio",
    },

    # ══════════════════════════════════════════
    #  AGRICULTURE
    # ══════════════════════════════════════════

    {
        "id": "agri_career",
        "title": "Agriculture / AgriTech Career",
        "category": "Agriculture",
        "subcategory": "Farming & AgriTech",
        "description": "India is an agrarian economy. Modern agriculture + AgriTech = massive opportunity. From farming to agri-startups to government roles.",
        "difficulty": "Low-Medium",
        "demand": "High",
        "automation_risk": "Medium",
        "remote_potential": "Low",
        "steps": [
            {"level": 1, "stage": "Education Options", "action": "B.Sc Agriculture (4 yrs via ICAR-AIEEA or state exams) OR B.Tech AgriTech/Food Tech OR Diploma in Agriculture (2 yrs, state level)."},
            {"level": 2, "stage": "Core Knowledge", "action": "Soil science, Crop science, Agronomy, Plant pathology, Agricultural economics. Hands-on farm experience is essential."},
            {"level": 3, "stage": "Career Paths", "action": "Govt agriculture officer, agri input company, AgriTech startup, farming entrepreneur, cooperative sector, export/import, teaching."},
            {"level": 4, "stage": "Government Jobs", "action": "Agriculture Officer (State PSC) / NABARD Officer / FCI (Food Corporation of India) / IARI Scientist / Agricultural Scientist (ICAR) / Block Agriculture Officer."},
            {"level": 5, "stage": "AgriTech Sector", "action": "Work at agri-startups: drone services, precision farming, soil testing, farmer advisory apps, agri e-commerce."},
            {"level": 6, "stage": "Entrepreneurship", "action": "Organic farming / Poly house / Mushroom cultivation / Apiculture / Dairy / Agro-processing unit — all supported by PM schemes."},
        ],
        "branches": [
            {"from_step": 2, "title": "ICAR Scientist", "path": "B.Sc Agri → M.Sc Agri → PhD → ICAR JRF/SRF → Scientist → Senior Scientist → Principal Scientist"},
            {"from_step": 2, "title": "Agri Business", "path": "B.Sc Agri → MBA Agribusiness (MANAGE Hyderabad) → Agri input company / commodity trading / export house"},
            {"from_step": 2, "title": "AgriTech Startup", "path": "B.Sc/B.Tech → Agri startup (Ninjacart, DeHaat, AgroStar, Fasal) → Tech + Agri = high growth"},
            {"from_step": 1, "title": "FPO Formation", "path": "Farmer + degree → Form Farmer Producer Organization → Collectivize 300+ farmers → PM FPO scheme (₹15L+ support) → Market linkage"},
        ],
        "govt_schemes": [
            {"name": "PM-KISAN", "url": "https://pmkisan.gov.in/", "benefit": "₹6000/year direct to farmer accounts"},
            {"name": "PMFBY (Crop Insurance)", "url": "https://pmfby.gov.in/", "benefit": "Subsidized crop insurance"},
            {"name": "PM Kisan Sampada Yojana", "url": "https://www.mofpi.gov.in/", "benefit": "Food processing unit subsidy"},
            {"name": "NABARD Schemes", "url": "https://www.nabard.org/", "benefit": "Farm loans, FPO support, agri infra fund"},
            {"name": "Soil Health Card", "url": "https://soilhealth.dac.gov.in/", "benefit": "Free soil testing for farmers"},
        ],
        "free_resources": [
            {"name": "ICAR e-Krishi Shiksha", "url": "https://ecourses.icar.gov.in/", "type": "Free Agri Courses"},
            {"name": "MANAGE Hyderabad", "url": "https://www.manage.gov.in/", "type": "Agri Management Training"},
            {"name": "Kisan Suvidha App", "url": "https://play.google.com/store/apps/details?id=in.gov.kisansuvidha", "type": "Govt App"},
            {"name": "NABARD (Farmer Portal)", "url": "https://www.nabard.org/", "type": "Schemes & Finance"},
        ],
        "salary_range": {
            "govt_agri_officer": "₹3.5–8 LPA",
            "agritech_startup": "₹4–15 LPA",
            "research_scientist": "₹6–20 LPA",
            "own_farming": "Variable (₹2L–₹20L+/acre depending on crop)",
        },
        "companies": {
            "agritech": ["Ninjacart", "DeHaat", "AgroStar", "Fasal", "Cropin", "BigHaat", "Waycool"],
            "input_companies": ["Bayer CropScience India", "Syngenta India", "UPL", "Coromandel International", "PI Industries"],
            "govt": ["FCI", "NAFED", "ICAR Institutes", "State Agriculture Depts", "NABARD"],
        },
        "exam_path": "ICAR AIEEA (UG) → B.Sc Agri | ICAR JRF → Research | State PSC → Agri Officer",
        "timeline": "4 years B.Sc + 1-2 years to stable career",
    },

]


# ─────────────────────────────────────────────
#  METADATA
# ─────────────────────────────────────────────

PLATFORM_METADATA = {
    "platform": "Crevr-Tree",
    "version": "1.0.0",
    "description": "Indian Career Intelligence Platform — Career Direction Dataset",
    "generated_at": datetime.now().isoformat(),
    "total_paths": len(CAREER_PATHS),
    "categories": list(set(p["category"] for p in CAREER_PATHS)),
    "purpose": "Power career tree visualization and AI recommendation engine",
    "context": "India-first. Covers education, govt exams, business, healthcare, technology, law, agriculture.",
}


# ─────────────────────────────────────────────
#  EXPORTERS
# ─────────────────────────────────────────────

def export_json(career_paths, metadata, output_path="career_data.json"):
    """Export structured JSON for React/Next.js front-end consumption."""
    payload = {
        "metadata": metadata,
        "career_paths": career_paths,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON exported → {output_path}  ({os.path.getsize(output_path)//1024} KB)")


def format_path_as_text(path: dict) -> str:
    """Convert one career path dict → clean readable text block."""
    lines = []
    sep = "═" * 70
    thin = "─" * 70

    lines.append(sep)
    lines.append(f"CAREER PATH: {path['title'].upper()}")
    lines.append(f"ID: {path['id']}")
    lines.append(f"Category: {path['category']} → {path['subcategory']}")
    lines.append(f"Difficulty: {path['difficulty']}  |  Demand: {path['demand']}")
    lines.append(f"Automation Risk: {path['automation_risk']}  |  Remote Potential: {path['remote_potential']}")
    lines.append("")
    lines.append(f"DESCRIPTION:")
    lines.append(textwrap.fill(path['description'], width=70))
    lines.append("")

    # Steps
    lines.append(thin)
    lines.append("CAREER STEPS (LINEAR PATH):")
    lines.append(thin)
    for step in path.get("steps", []):
        lines.append(f"  STEP {step['level']}: {step['stage']}")
        lines.append(f"    → {step['action']}")
        lines.append("")

    # Branches
    if path.get("branches"):
        lines.append(thin)
        lines.append("BRANCH PATHS (ALTERNATE ROUTES FROM THIS CAREER):")
        lines.append(thin)
        for branch in path["branches"]:
            lines.append(f"  [From Step {branch['from_step']}] {branch['title']}")
            lines.append(f"    → {branch['path']}")
            lines.append("")

    # Skills
    if path.get("skills_required"):
        lines.append(thin)
        lines.append("SKILLS REQUIRED:")
        lines.append("  " + " | ".join(path["skills_required"]))
        lines.append("")

    if path.get("skills_to_build"):
        lines.append("SKILLS TO BUILD NEXT:")
        lines.append("  " + " | ".join(path["skills_to_build"]))
        lines.append("")

    # Free Resources
    if path.get("free_resources"):
        lines.append(thin)
        lines.append("FREE LEARNING RESOURCES:")
        for res in path["free_resources"]:
            lines.append(f"  [{res['type']}] {res['name']}")
            lines.append(f"    URL: {res['url']}")
        lines.append("")

    # Govt Schemes (for business/agri paths)
    if path.get("govt_schemes"):
        lines.append(thin)
        lines.append("GOVERNMENT SCHEMES & SUPPORT:")
        for scheme in path["govt_schemes"]:
            lines.append(f"  {scheme['name']}: {scheme['benefit']}")
            lines.append(f"    URL: {scheme['url']}")
        lines.append("")

    # Salary
    if path.get("salary_range"):
        lines.append(thin)
        lines.append("SALARY RANGE:")
        for level, amount in path["salary_range"].items():
            lines.append(f"  {level.replace('_', ' ').title()}: {amount}")
        lines.append("")

    # Companies
    if path.get("companies"):
        lines.append(thin)
        lines.append("KEY EMPLOYERS:")
        for sector, cos in path["companies"].items():
            lines.append(f"  {sector.title()}: {', '.join(cos)}")
        lines.append("")

    # Govt opportunities
    if path.get("govt_opportunities"):
        lines.append(thin)
        lines.append("GOVERNMENT OPPORTUNITIES:")
        lines.append("  " + " | ".join(path["govt_opportunities"]))
        lines.append("")

    # Exam path & timeline
    if path.get("exam_path"):
        lines.append(thin)
        lines.append(f"EXAM PATH: {path['exam_path']}")

    if path.get("timeline"):
        lines.append(f"TIMELINE: {path['timeline']}")

    lines.append(sep)
    lines.append("")

    return "\n".join(lines)


def export_txt(career_paths, metadata, output_path="career_data.txt"):
    """Export human-readable TXT — perfect for pasting into Antigravity or any AI tool."""
    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write("=" * 70 + "\n")
        f.write("CREVR-TREE: INDIAN CAREER INTELLIGENCE DATASET\n")
        f.write(f"Generated: {metadata['generated_at']}\n")
        f.write(f"Total Career Paths: {metadata['total_paths']}\n")
        f.write(f"Categories: {', '.join(metadata['categories'])}\n")
        f.write("=" * 70 + "\n\n")

        f.write("HOW TO USE THIS FILE:\n")
        f.write("  - Each CAREER PATH block contains a complete career journey\n")
        f.write("  - Steps = linear progression from entry to peak\n")
        f.write("  - Branches = alternate routes diverging from the main path\n")
        f.write("  - Free Resources = no-cost learning materials\n")
        f.write("  - Govt Schemes = free government support programs\n\n")
        f.write("=" * 70 + "\n\n")

        # Each path
        for path in career_paths:
            f.write(format_path_as_text(path))

        # Index
        f.write("\n" + "=" * 70 + "\n")
        f.write("CAREER PATH INDEX\n")
        f.write("=" * 70 + "\n")
        for i, path in enumerate(career_paths, 1):
            f.write(f"  {i:02d}. [{path['id']}] {path['title']} ({path['category']})\n")

    print(f"  ✓ TXT exported  → {output_path}  ({os.path.getsize(output_path)//1024} KB)")


def export_index_json(career_paths, output_path="career_index.json"):
    """Export a lightweight index for fast search/filter in the front-end."""
    index = []
    for path in career_paths:
        index.append({
            "id": path["id"],
            "title": path["title"],
            "category": path["category"],
            "subcategory": path["subcategory"],
            "difficulty": path["difficulty"],
            "demand": path["demand"],
            "automation_risk": path["automation_risk"],
            "remote_potential": path["remote_potential"],
            "step_count": len(path.get("steps", [])),
            "branch_count": len(path.get("branches", [])),
            "has_govt_schemes": bool(path.get("govt_schemes")),
            "has_free_resources": bool(path.get("free_resources")),
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Index JSON    → {output_path}  ({os.path.getsize(output_path)//1024} KB)")


# ─────────────────────────────────────────────
#  VALIDATION
# ─────────────────────────────────────────────

def validate_paths(career_paths):
    """Basic integrity checks on all career paths."""
    errors = []
    ids_seen = set()

    for path in career_paths:
        pid = path.get("id", "MISSING_ID")

        if pid in ids_seen:
            errors.append(f"Duplicate ID: {pid}")
        ids_seen.add(pid)

        if not path.get("title"):
            errors.append(f"[{pid}] Missing title")
        if not path.get("steps"):
            errors.append(f"[{pid}] No steps defined")
        if not path.get("category"):
            errors.append(f"[{pid}] Missing category")
        if not path.get("free_resources"):
            errors.append(f"[{pid}] No free resources (every path should have at least one)")

    if errors:
        print(f"\n  ⚠ VALIDATION WARNINGS ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
    else:
        print(f"  ✓ All {len(career_paths)} paths passed validation")

    return len(errors) == 0


# ─────────────────────────────────────────────
#  STATS
# ─────────────────────────────────────────────

def print_stats(career_paths):
    """Print dataset statistics."""
    total_steps = sum(len(p.get("steps", [])) for p in career_paths)
    total_branches = sum(len(p.get("branches", [])) for p in career_paths)
    total_resources = sum(len(p.get("free_resources", [])) for p in career_paths)
    categories = {}
    for p in career_paths:
        categories[p["category"]] = categories.get(p["category"], 0) + 1

    print("\n  📊 DATASET STATISTICS")
    print(f"     Career Paths  : {len(career_paths)}")
    print(f"     Total Steps   : {total_steps}")
    print(f"     Total Branches: {total_branches}")
    print(f"     Free Resources: {total_resources}")
    print(f"     Categories    :")
    for cat, count in sorted(categories.items()):
        print(f"       - {cat}: {count} path(s)")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    print("\n" + "═" * 70)
    print("  CREVR-TREE | Indian Career Intelligence Data Generator")
    print("  Running generation pipeline...")
    print("═" * 70 + "\n")

    # Step 1: Validate
    print("[ Step 1 ] Validating career paths...")
    validate_paths(CAREER_PATHS)

    # Step 2: Stats
    print("\n[ Step 2 ] Computing statistics...")
    print_stats(CAREER_PATHS)

    # Step 3: Export
    print("\n[ Step 3 ] Exporting data files...")
    export_json(CAREER_PATHS, PLATFORM_METADATA, "career_data.json")
    export_txt(CAREER_PATHS, PLATFORM_METADATA, "career_data.txt")
    export_index_json(CAREER_PATHS, "career_index.json")

    print("\n" + "═" * 70)
    print("  ✅  GENERATION COMPLETE")
    print("  Files created:")
    print("    • career_data.json   — Full structured data (for React/API)")
    print("    • career_data.txt    — Human-readable (for Antigravity/AI tools)")
    print("    • career_index.json  — Lightweight index (for search & filter UI)")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
