#!/usr/bin/env python3
"""Helper: generates job roles, skills, companies, industries, resources and main logic"""
import os

d = r'C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project'

part2 = '''
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
'''

print(f"Job roles part length: {len(part2)}")

with open(os.path.join(d, 'jobroles_part.py'), 'w', encoding='utf-8') as f:
    f.write(part2)
print("Job roles written")
