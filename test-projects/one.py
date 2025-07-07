import csv
import random

# Provided options lists
interest_areas_options = [
    "Web Development", "Mobile App Development", "Frontend Development", "Backend Development", "Full Stack Development",
    "Game Development", "Embedded Systems", "Data Science", "Machine Learning", "Artificial Intelligence", "Deep Learning",
    "Natural Language Processing", "Computer Vision", "Big Data", "Cloud Computing", "DevOps",
    "Site Reliability Engineering (SRE)", "Platform Engineering", "Cybersecurity", "Ethical Hacking", "Networking",
    "Software Engineering", "Quality Assurance / Testing", "Database Engineering", "Systems Programming",
    "Academic Research", "Quantum Computing", "Bioinformatics", "Product Management", "Project Management",
    "Business Analysis", "Entrepreneurship", "Consulting", "UI/UX Design", "Technical Writing",
    "Human Computer Interaction", "Design Systems", "Digital Marketing", "Finance Technology", "IoT (Internet of Things)",
    "Education Technology"
]

soft_skills_options = [
    "Communication", "Teamwork", "Collaboration", "Presentation Skills", "Active Listening", "Problem Solving",
    "Critical Thinking", "Creative Thinking", "Innovative Thinking", "Adaptability", "Time Management", "Multitasking",
    "Attention to Detail", "Work Ethic", "Leadership", "Decision Making", "Strategic Thinking", "Accountability",
    "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Resilience", "Analytical Thinking",
    "Business Communication", "Customer Focus", "Planning and Organization", "Goal-Oriented Mindset"
]

programming_languages_options = [
    "Python", "Java", "C++", "C#", "JavaScript", "Go", "Rust", "PHP", "Ruby", "TypeScript", "HTML", "CSS",
    "Kotlin", "Swift", "Dart", "SQL", "R", "MATLAB", "Shell (Bash)", "PowerShell", "Scala", "Julia", "Haskell", "Lisp", "Assembly"
]

tools_techstack_options = [
    "Git", "GitHub", "Bitbucket", "Jira", "Confluence", "Docker", "Podman", "Kubernetes", "Helm", "Terraform", "Ansible",
    "Jenkins", "CircleCI", "GitLab CI/CD", "AWS", "Azure", "GCP", "React", "Angular", "Vue.js", "Node.js", "Django",
    "Flask", "Spring Boot", "Express.js", "Laravel", "Android Studio", "Xcode", "Flutter", "React Native",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Jupyter Notebook", "Google Colab", "Weights & Biases",
    "MongoDB", "PostgreSQL", "MySQL", "Spark", "Hadoop", "Kafka", "Airflow", "DBT", "Tableau", "Power BI", "Looker",
    "Figma", "Sketch", "Adobe XD", "Canva", "InVision", "Unity", "Unreal Engine", "Postman", "Swagger", "Insomnia",
    "Selenium", "Jest", "Cypress", "Mocha", "JUnit", "Pytest", "Prometheus", "Grafana", "ELK Stack", "VS Code",
    "IntelliJ IDEA", "PyCharm"
]

certifications_options = [
    "AWS Certified Cloud Practitioner", "Google Cloud Associate Cloud Engineer", "Microsoft Certified Azure Fundamentals",
    "AWS Certified Security Specialty", "Microsoft Certified: Azure AI Engineer", "CompTIA Security+",
    "Certified Ethical Hacker (CEH)", "Cisco CCNA", "Offensive Security Certified Professional (OSCP)",
    "Google Data Analytics Certificate", "IBM Data Science Professional Certificate", "Deep Learning Specialization (Coursera)",
    "Machine Learning (Stanford/Coursera)", "Microsoft Certified: Power BI Data Analyst Associate",
    "Microsoft Certified: SQL Associate", "Frontend Development Libraries (freeCodeCamp)", "Backend Development (Node.js)",
    "Responsive Web Design (freeCodeCamp)", "Android Developer Certification (Google)", "iOS App Development with Swift (Apple)",
    "Oracle Certified Java Programmer", "PCEP – Certified Entry-Level Python Programmer", "Google UX Design Certificate",
    "Docker Certified Associate", "Kubernetes Certified Administrator (CKA)", "Linux Foundation Certified Kubernetes Admin",
    "HashiCorp Certified: Terraform Associate", "ISTQB Foundation Level", "Project Management Professional (PMP)",
    "Certified ScrumMaster (CSM)", "SAFe Agilist Certification", "Salesforce Certified Administrator", "Tableau Desktop Specialist"
]

extracurricular_interests_options = [
    "Coding Clubs", "Hackathons", "Robotics Competitions", "Online Coding Contests", "Open Source Contributions",
    "Tech Meetups", "AR/VR Projects", "Entrepreneurship Clubs", "Startup Ideation Events", "Innovation Challenges",
    "Teaching/TA Work", "Mentorship Programs", "Workshop Hosting", "Club Leadership Roles", "Event Management",
    "Student Government", "Debate Clubs", "Public Speaking", "Case Competitions", "Technical Writing", "Blogging",
    "Podcast Creation", "Graphic Design", "Video Editing", "3D Modeling", "UI/UX Projects", "Animation Design",
    "Volunteering", "Community Service", "Sports", "Music", "Photography", "Gaming"
]

favourite_subjects_options = [
    "Data Structures and Algorithms", "Operating Systems", "Database Management Systems", "Computer Networks",
    "Object-Oriented Programming", "Software Engineering", "Discrete Mathematics", "Compiler Design", "Theory of Computation",
    "Digital Logic Design", "Computer Architecture", "Machine Learning", "Artificial Intelligence", "Probability and Statistics",
    "Linear Algebra", "Calculus", "Data Mining", "Big Data Analytics", "Web Technologies", "Mobile Application Development",
    "User Interface Design", "Human Computer Interaction", "Cloud Computing", "Cyber Security", "Ethical Hacking",
    "Cryptography", "Information Security", "Distributed Systems", "Cloud Infrastructure", "Virtualization and Containers",
    "Natural Language Processing", "Computer Vision", "Robotics", "IoT (Internet of Things)", "Blockchain",
    "Quantum Computing", "Bioinformatics", "Project Management", "Business Intelligence", "Technical Communication",
    "Entrepreneurship", "Physics", "Chemistry", "Biology", "Economics", "Psychology", "Sociology"
]

problem_solving_style_options = [
    "Analytical", "Logical", "Creative", "Innovative", "Systematic", "Data-driven", "Intuitive", "Experimental",
    "Pragmatic", "Collaborative", "User-Centered", "Strategic", "Big Picture Thinker", "Result-Oriented", "Detail-Oriented"
]

recommended_career_options = [
    "Software Developer (Backend)", "Software Developer (Frontend)", "Full Stack Developer",
    "Mobile Developer (Android)", "Mobile Developer (iOS)", "Game Developer",
    "AR/VR Developer", "Blockchain Developer",
    "Data Scientist", "Machine Learning Engineer", "AI Prompt Engineer",
    "Big Data Engineer", "MLOps Engineer", "AI Ethicist", "Data Engineer",
    "DevOps Engineer", "Cloud Engineer", "Solutions Architect",
    "Platform Engineer", "Systems Engineer",
    "Cybersecurity Analyst", "Security Engineer",
    "Quality Assurance Engineer", "Software Test Automation Engineer",
    "Research Intern (AI/ML)", "Research Intern (General)",
    "MS in Computer Science", "MS in Data Science", "Ph.D. Candidate",
    "UI/UX Designer", "Product Manager", "Project Manager",
    "Technical Writer", "Technical Consultant", "Technical Program Manager (TPM)",
    "Business Analyst", "Database Administrator",
    "Network Engineer", "Embedded Systems Engineer", "IoT Engineer",
    "Bioinformatics Engineer"
]

# Helper function to select multiple items and format as string
def select_multiple(options, max_items=3, can_be_empty=False):
    if can_be_empty and random.random() < 0.1: # 10% chance of being empty
        return ""
    count = random.randint(1, max_items)
    return ", ".join(random.sample(options, min(count, len(options))))

# Skill Affinities (Simplified for brevity in this step, will be expanded)
# This is a placeholder and will be more detailed in the actual generation logic
career_skill_map = {
    "Software Developer (Backend)": {
        "interests": ["Backend Development", "Software Engineering", "Database Engineering"],
        "langs": ["Python", "Java", "Go", "C#", "Ruby", "SQL"],
        "tools": ["Git", "Docker", "Kubernetes", "AWS", "PostgreSQL", "MySQL", "MongoDB", "Spring Boot", "Django", "Flask", "Node.js", "Jenkins"],
        "certs": ["AWS Certified Cloud Practitioner", "Oracle Certified Java Programmer", "Microsoft Certified: SQL Associate", "Backend Development (Node.js)"],
        "subjects": ["Data Structures and Algorithms", "Object-Oriented Programming", "Database Management Systems", "Operating Systems", "Software Engineering"],
        "problem_solving": ["Logical", "Systematic", "Problem Solving"]
    },
    "Software Developer (Frontend)": {
        "interests": ["Frontend Development", "Web Development", "UI/UX Design"],
        "langs": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "tools": ["Git", "React", "Angular", "Vue.js", "Node.js", "VS Code", "Figma", "Webpack"], # Added Webpack
        "certs": ["Responsive Web Design (freeCodeCamp)", "Frontend Development Libraries (freeCodeCamp)"],
        "subjects": ["Web Technologies", "User Interface Design", "Human Computer Interaction", "Data Structures and Algorithms"],
        "problem_solving": ["Creative", "User-Centered", "Detail-Oriented"]
    },
    "Full Stack Developer": {
        "interests": ["Full Stack Development", "Web Development", "Backend Development", "Frontend Development"],
        "langs": ["JavaScript", "Python", "Java", "TypeScript", "SQL", "HTML", "CSS"],
        "tools": ["Git", "Docker", "React", "Node.js", "Django", "Spring Boot", "AWS", "MongoDB", "PostgreSQL", "VS Code"],
        "certs": ["AWS Certified Cloud Practitioner", "Responsive Web Design (freeCodeCamp)", "Backend Development (Node.js)"],
        "subjects": ["Web Technologies", "Data Structures and Algorithms", "Database Management Systems", "Software Engineering"],
        "problem_solving": ["Problem Solving", "Systematic", "Adaptability"]
    },
    "Mobile Developer (Android)": {
        "interests": ["Mobile App Development"],
        "langs": ["Kotlin", "Java", "C++"],
        "tools": ["Android Studio", "Git", "Firebase", "Gradle"], # Added Firebase, Gradle
        "certs": ["Android Developer Certification (Google)"],
        "subjects": ["Mobile Application Development", "Object-Oriented Programming", "Software Engineering"],
        "problem_solving": ["Problem Solving", "User-Centered", "Innovative Thinking"]
    },
    "Mobile Developer (iOS)": {
        "interests": ["Mobile App Development"],
        "langs": ["Swift", "Objective-C"], # Added Objective-C
        "tools": ["Xcode", "Git", "SwiftUI", "UIKit", "Core Data"], # Added SwiftUI, UIKit, Core Data
        "certs": ["iOS App Development with Swift (Apple)"],
        "subjects": ["Mobile Application Development", "Object-Oriented Programming", "Software Engineering"],
        "problem_solving": ["Problem Solving", "User-Centered", "Detail-Oriented"]
    },
    "Data Scientist": {
        "interests": ["Data Science", "Machine Learning", "Artificial Intelligence", "Big Data"],
        "langs": ["Python", "R", "SQL"],
        "tools": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Jupyter Notebook", "Spark", "Tableau", "Git", "AWS", "GCP"],
        "certs": ["IBM Data Science Professional Certificate", "Machine Learning (Stanford/Coursera)", "Google Data Analytics Certificate", "Deep Learning Specialization (Coursera)"],
        "subjects": ["Machine Learning", "Probability and Statistics", "Data Mining", "Big Data Analytics", "Linear Algebra", "Data Structures and Algorithms"],
        "problem_solving": ["Data-driven", "Analytical", "Critical Thinking", "Experimental"]
    },
    "Machine Learning Engineer": {
        "interests": ["Machine Learning", "Artificial Intelligence", "Deep Learning", "Data Science"],
        "langs": ["Python", "C++", "R", "SQL"],
        "tools": ["TensorFlow", "PyTorch", "Scikit-learn", "Kubernetes", "Docker", "AWS", "GCP", "MLflow", "Airflow", "Git"], # Added MLflow, Airflow
        "certs": ["Deep Learning Specialization (Coursera)", "Machine Learning (Stanford/Coursera)", "Microsoft Certified: Azure AI Engineer", "AWS Certified Machine Learning - Specialty"], # Added AWS ML Specialty
        "subjects": ["Machine Learning", "Deep Learning", "Artificial Intelligence", "Linear Algebra", "Probability and Statistics", "Software Engineering"],
        "problem_solving": ["Analytical", "Problem Solving", "Innovative Thinking", "Systematic"]
    },
    "DevOps Engineer": {
        "interests": ["DevOps", "Cloud Computing", "Site Reliability Engineering (SRE)", "Automation"], # Added Automation
        "langs": ["Python", "Shell (Bash)", "Go", "PowerShell"],
        "tools": ["Docker", "Kubernetes", "Jenkins", "Git", "Terraform", "Ansible", "AWS", "Azure", "GCP", "Prometheus", "Grafana", "ELK Stack"],
        "certs": ["AWS Certified Cloud Practitioner", "Docker Certified Associate", "Kubernetes Certified Administrator (CKA)", "HashiCorp Certified: Terraform Associate"],
        "subjects": ["Cloud Computing", "Operating Systems", "Computer Networks", "Virtualization and Containers", "Distributed Systems"],
        "problem_solving": ["Systematic", "Problem Solving", "Resilience", "Automation Mindset"] # Added Automation Mindset
    },
    "Cloud Engineer": {
        "interests": ["Cloud Computing", "DevOps", "Networking", "Infrastructure"], # Added Infrastructure
        "langs": ["Python", "Shell (Bash)", "Go"],
        "tools": ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "Docker", "Ansible", "Git"],
        "certs": ["AWS Certified Cloud Practitioner", "Google Cloud Associate Cloud Engineer", "Microsoft Certified Azure Fundamentals", "AWS Certified Solutions Architect - Associate"], # Added AWS SA Associate
        "subjects": ["Cloud Computing", "Computer Networks", "Operating Systems", "Distributed Systems", "Security"], # Added Security
        "problem_solving": ["Systematic", "Problem Solving", "Strategic Thinking"]
    },
    "UI/UX Designer": {
        "interests": ["UI/UX Design", "Human Computer Interaction", "Design Systems", "Frontend Development"],
        "langs": ["HTML", "CSS"], # Often useful for prototyping
        "tools": ["Figma", "Sketch", "Adobe XD", "InVision", "Canva", "Zeplin"], # Added Zeplin
        "certs": ["Google UX Design Certificate"],
        "subjects": ["User Interface Design", "Human Computer Interaction", "Psychology", "Web Technologies", "Graphic Design"], # Added Graphic Design
        "problem_solving": ["Creative", "User-Centered", "Empathy", "Innovative Thinking", "Detail-Oriented"]
    },
    # Add more mappings for other careers to ensure coverage and variety
    # For brevity, I'll create a generic fallback for careers not explicitly mapped here during generation.
}

# Ensure all recommended careers have at least a basic entry in the map
for career in recommended_career_options:
    if career not in career_skill_map:
        career_skill_map[career] = {
            "interests": random.sample(interest_areas_options, k=min(len(interest_areas_options), 2)), # Generic interests
            "langs": random.sample(programming_languages_options, k=min(len(programming_languages_options),1 if random.random() < 0.7 else 0) ), # Some roles might not require coding
            "tools": random.sample(tools_techstack_options, k=min(len(tools_techstack_options),2)),
            "certs": random.sample(certifications_options, k=min(len(certifications_options),1)) if random.random() > 0.3 else [], # 30% chance of no certs
            "subjects": random.sample(favourite_subjects_options, k=min(len(favourite_subjects_options),2)),
            "problem_solving": random.sample(problem_solving_style_options, k=min(len(problem_solving_style_options),2))
        }


def generate_row(recommended_career):
    profile = career_skill_map.get(recommended_career, career_skill_map[random.choice(list(career_skill_map.keys()))]) # Fallback to a random profile if not found

    # Interest Areas: 1-3, biased towards profile
    num_interests = random.randint(1, 3)
    interests = set(random.sample(profile["interests"], min(len(profile["interests"]), random.randint(1,2))))
    while len(interests) < num_interests and len(interest_areas_options) > len(interests) :
        interests.add(random.choice(interest_areas_options))
    
    # Soft Skills: 3-5, mostly generic but can add specific ones
    soft_skills = select_multiple(soft_skills_options, max_items=5)
    if not soft_skills: soft_skills = random.choice(soft_skills_options) # Ensure at least one

    # Programming Languages: 0-4, biased by profile
    num_langs = random.randint(0, 4)
    if recommended_career in ["UI/UX Designer", "Product Manager", "Project Manager", "Business Analyst", "Technical Writer", "AI Ethicist"]: # Roles less likely to code heavily
        num_langs = random.randint(0,2)
    
    langs = set()
    if num_langs > 0:
        langs.update(random.sample(profile["langs"], min(len(profile["langs"]), random.randint(0, len(profile["langs"]))))) # take some from profile
        while len(langs) < num_langs and len(programming_languages_options) > len(langs):
            candidate_lang = random.choice(programming_languages_options)
            if candidate_lang not in langs:
                langs.add(candidate_lang)
    
    # Tools & Techstack: 2-6, biased by profile
    num_tools = random.randint(2,6)
    tools = set(random.sample(profile["tools"], min(len(profile["tools"]), random.randint(1,3))))
    while len(tools) < num_tools and len(tools_techstack_options) > len(tools):
        tools.add(random.choice(tools_techstack_options))

    # Certifications: 0-3, biased by profile
    num_certs = random.randint(0,3)
    certs = set()
    if num_certs > 0 and profile.get("certs"):
        certs.update(random.sample(profile["certs"], min(len(profile["certs"]), random.randint(0,len(profile["certs"])))))
    while len(certs) < num_certs and len(certifications_options) > len(certs):
        candidate_cert = random.choice(certifications_options)
        if candidate_cert not in certs: # Avoid duplicates
            certs.add(candidate_cert)
            
    # Extracurricular Interests: 1-4, generic
    extracurricular = select_multiple(extracurricular_interests_options, max_items=4, can_be_empty=True)

    # Favourite Subjects: 2-4, biased by profile
    num_subjects = random.randint(2,4)
    subjects = set(random.sample(profile["subjects"], min(len(profile["subjects"]), random.randint(1,2))))
    while len(subjects) < num_subjects and len(favourite_subjects_options) > len(subjects):
        subjects.add(random.choice(favourite_subjects_options))

    # Problem Solving Style: 1-2, biased by profile
    num_problem_styles = random.randint(1,2)
    problem_styles = set(random.sample(profile["problem_solving"], min(len(profile["problem_solving"]),1)))
    while len(problem_styles) < num_problem_styles and len(problem_solving_style_options) > len(problem_styles):
        problem_styles.add(random.choice(problem_solving_style_options))

    # Additional fields from sample
    preferred_work_style = random.choice(["Remote", "Hybrid", "On-site"])
    cgpa = round(random.uniform(6.0, 9.9), 1)
    wants_to_go_for_masters = random.choice([True, False])
    # If wants masters, more likely interested in research. Especially for research roles.
    if recommended_career in ["MS in Computer Science", "MS in Data Science", "Ph.D. Candidate", "Research Intern (AI/ML)", "Research Intern (General)"]:
        interested_in_research = True
        wants_to_go_for_masters = True # Usually true for these
    elif wants_to_go_for_masters:
        interested_in_research = random.choices([True, False], weights=[0.6, 0.4], k=1)[0]
    else:
        interested_in_research = random.choices([True, False], weights=[0.2, 0.8], k=1)[0]
        
    current_projects_count = random.randint(0, 8)
    internship_experience = random.randint(0, 4)


    return {
        "Interest_Areas": ", ".join(list(interests)),
        "Preferred_Work_Style": preferred_work_style,
        "CGPA": cgpa,
        "Soft_Skills": soft_skills,
        "Programming_Languages": ", ".join(list(langs)) if langs else "",
        "Tools_Techstack": ", ".join(list(tools)),
        "Certifications": ", ".join(list(certs)) if certs else "",
        "Wants_to_Go_for_Masters": wants_to_go_for_masters,
        "Interested_in_Research": interested_in_research,
        "Current_Projects_Count": current_projects_count,
        "Extracurricular_Interests": extracurricular,
        "Favourite_Subjects": ", ".join(list(subjects)),
        "Internship_Experience": internship_experience,
        "Problem_Solving_Style": ", ".join(list(problem_styles)),
        "Recommended_Career": recommended_career
    }

# --- Main script ---
NUM_ROWS = random.randint(5000, 7000)
OUTPUT_FILENAME = "generated_career_data.csv"

# Define header based on keys from generate_row and sample
header = [
    "Interest_Areas", "Preferred_Work_Style", "CGPA", "Soft_Skills", 
    "Programming_Languages", "Tools_Techstack", "Certifications", 
    "Wants_to_Go_for_Masters", "Interested_in_Research", "Current_Projects_Count", 
    "Extracurricular_Interests", "Favourite_Subjects", "Internship_Experience", 
    "Problem_Solving_Style", "Recommended_Career"
]

rows_data = []

# Ensure each recommended career option appears at least once
careers_to_cover = list(recommended_career_options) # Make a mutable copy
random.shuffle(careers_to_cover) # Shuffle to not have them all at the start in order

for career in careers_to_cover:
    if len(rows_data) < NUM_ROWS:
        rows_data.append(generate_row(career))
    else:
        break # Stop if NUM_ROWS is smaller than number of unique careers

# Generate remaining rows
while len(rows_data) < NUM_ROWS:
    recommended_career = random.choice(recommended_career_options)
    rows_data.append(generate_row(recommended_career))

# Write to CSV
with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows_data)

print(f"Successfully generated {len(rows_data)} rows into {OUTPUT_FILENAME}")

# Example of how to expand career_skill_map (this part is for illustration, the script above uses a more generic fill)
# This would be manually curated for best results
additional_career_mappings = {
    "Game Developer": {
        "interests": ["Game Development", "Software Engineering"],
        "langs": ["C++", "C#", "JavaScript"],
        "tools": ["Unity", "Unreal Engine", "Git", "Blender"], # Added Blender
        "certs": [], # Specific game dev certs are less common as general ones
        "subjects": ["Data Structures and Algorithms", "Object-Oriented Programming", "Computer Graphics", "Physics"], # Added Graphics, Physics
        "problem_solving": ["Creative", "Problem Solving", "Innovative Thinking"]
    },
    "Cybersecurity Analyst": {
        "interests": ["Cybersecurity", "Ethical Hacking", "Networking"],
        "langs": ["Python", "Shell (Bash)", "PowerShell"],
        "tools": ["Wireshark", "Nmap", "Metasploit", "Kali Linux", "SIEM tools", "Git"], # Added Nmap, Metasploit, SIEM
        "certs": ["CompTIA Security+", "Certified Ethical Hacker (CEH)", "Cisco CCNA", "GIAC Security Essentials (GSEC)"], # Added GSEC
        "subjects": ["Cyber Security", "Computer Networks", "Operating Systems", "Cryptography"],
        "problem_solving": ["Analytical", "Critical Thinking", "Attention to Detail", "Systematic"]
    },
     "AI Prompt Engineer": {
        "interests": ["Artificial Intelligence", "Natural Language Processing", "Machine Learning", "Content Creation"],
        "langs": ["Python"], # Often for scripting or using APIs
        "tools": ["Jupyter Notebook", "Git", "Large Language Model APIs (OpenAI, Hugging Face)", "Prompt Engineering Tools"],
        "certs": ["Machine Learning (Stanford/Coursera)", "Deep Learning Specialization (Coursera)"], # Relevant foundational knowledge
        "subjects": ["Artificial Intelligence", "Natural Language Processing", "Linguistics", "Psychology", "Creative Writing"],
        "problem_solving": ["Creative", "Innovative Thinking", "Analytical", "Detail-Oriented", "Iterative"]
    },
    "AI Ethicist": {
        "interests": ["Artificial Intelligence", "Ethics in AI", "Sociology of Technology", "Public Policy"],
        "langs": [], # Not primarily a coding role
        "tools": ["Research Databases", "Survey Tools", "Presentation Software"],
        "certs": [], # Specialized ethics certs are emerging
        "subjects": ["Artificial Intelligence", "Ethics", "Sociology", "Law", "Philosophy", "Public Policy"],
        "problem_solving": ["Critical Thinking", "Analytical", "Strategic Thinking", "Communication", "Empathy"]
    },
    "MS in Computer Science": { # This is more of a goal/status
        "interests": random.sample(interest_areas_options, k=3), # Broad interests
        "langs": random.sample(programming_languages_options, k=3), # Foundational languages
        "tools": ["Git", "VS Code", "Jupyter Notebook"] + random.sample(tools_techstack_options, k=2),
        "certs": random.sample(certifications_options, k=1) if random.random() > 0.5 else [],
        "subjects": ["Data Structures and Algorithms", "Theory of Computation", "Operating Systems"] + random.sample(favourite_subjects_options, k=2),
        "problem_solving": ["Analytical", "Logical", "Problem Solving", "Research-Oriented"]
    },
     "Ph.D. Candidate": {
        "interests": ["Academic Research"] + random.sample(interest_areas_options, k=2), # Specialization
        "langs": ["Python", "R", "MATLAB", "Julia"] + random.sample(programming_languages_options, k=1), # Research-focused
        "tools": ["Git", "LaTeX", "Jupyter Notebook", "Specific research software"] + random.sample(tools_techstack_options, k=1),
        "certs": [], # Certs less focus, papers/research more
        "subjects": ["Specialized Research Area", "Advanced Algorithms", "Statistics", "Theory of Computation"],
        "problem_solving": ["Analytical", "Critical Thinking", "Innovative Thinking", "Research-Oriented", "Resilience"]
    },
}

# This is just a print to show how one might merge - the script itself has a simpler fill for unmapped careers.
# For a real implementation, one would integrate this more deeply into the career_skill_map initialization.
# print("Example of how more specific mappings could be added:", additional_career_mappings["Game Developer"])

# (The script already has a mechanism to provide default random values for careers not in the initial map)
# The `career_skill_map.update(additional_career_mappings)` could be used if these were to be strictly used.
# However, the current script's fill for missing careers is more dynamic for ensuring all careers are processed.

print(f"Completed generating {OUTPUT_FILENAME}")