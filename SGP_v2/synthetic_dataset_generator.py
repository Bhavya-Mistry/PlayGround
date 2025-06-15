import pandas as pd
import numpy as np
import random
from collections import Counter
import os # Import os for directory creation

# Define a list of possible values for text/list columns
interest_areas_options = [
    "Web Development", "Mobile App Development", "Data Science", "Machine Learning",
    "Artificial Intelligence", "Cloud Computing", "Cybersecurity", "Networking",
    "Embedded Systems", "Robotics", "Game Development", "UI/UX Design",
    "Project Management", "Technical Writing", "DevOps", "Blockchain",
    "Bioinformatics", "Quantum Computing", "Finance Technology", "Digital Marketing",
    "IoT", "Computer Vision", "Natural Language Processing", "Big Data",
    "Ethical Hacking", "Consulting", "Entrepreneurship"
]

soft_skills_options = [
    "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
    "Adaptability", "Time Management", "Creativity", "Leadership",
    "Decision Making", "Emotional Intelligence", "Conflict Resolution",
    "Networking", "Presentation Skills", "Negotiation", "Empathy"
]

programming_languages_options = [
    "Python", "Java", "C++", "JavaScript", "C#", "Go", "Rust", "Swift",
    "Kotlin", "PHP", "Ruby", "TypeScript", "SQL", "R", "Dart"
]

tools_techstack_options = [
    "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "React", "Angular",
    "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", "TensorFlow", "PyTorch",
    "Scikit-learn", "Pandas", "NumPy", "MongoDB", "PostgreSQL", "MySQL",
    "Figma", "Sketch", "Adobe XD", "Unity", "Unreal Engine", "Jira", "Confluence",
    "Tableau", "Power BI", "Spark", "Hadoop", "Kafka", "Salesforce", "Android Studio",
    "Xcode", "VS Code", "Jupyter Notebook", "Postman", "Terraform", "Ansible",
    "Jenkins", "CircleCI", "GitLab CI/CD", "Selenium", "Jest", "Cypress"
]

certifications_options = [
    "AWS Certified Cloud Practitioner", "Google Cloud Associate Cloud Engineer",
    "Microsoft Certified Azure Fundamentals", "CompTIA Security+",
    "Certified Ethical Hacker (CEH)", "Cisco CCNA", "Project Management Professional (PMP)",
    "Google Data Analytics Certificate", "IBM Data Science Professional Certificate",
    "Deep Learning Specialization (Coursera)", "Machine Learning (Stanford/Coursera)",
    "Frontend Development Libraries (freeCodeCamp)", "Backend Development (Node.js)",
    "Responsive Web Design (freeCodeCamp)", "Docker Certified Associate",
    "Kubernetes Certified Administrator (CKA)", "Certified ScrumMaster (CSM)",
    "Tableau Desktop Specialist", "Salesforce Certified Administrator",
    "Microsoft Certified: Power BI Data Analyst Associate"
]

extracurricular_interests_options = [
    "Coding Clubs", "Hackathons", "Robotics Competitions", "Debate Clubs",
    "Sports", "Volunteering", "Music", "Photography", "Gaming",
    "Entrepreneurship Clubs", "Community Service", "Student Government",
    "Technical Writing", "Blogging", "Podcast creation", "Graphic Design"
]

favourite_subjects_options = [
    "Data Structures and Algorithms", "Operating Systems", "Database Management Systems",
    "Computer Networks", "Software Engineering", "Artificial Intelligence",
    "Machine Learning", "Linear Algebra", "Calculus", "Probability and Statistics",
    "Physics", "Chemistry", "Biology", "Economics", "Psychology",
    "Discrete Mathematics", "Object-Oriented Programming", "Web Technologies",
    "Cloud Computing", "Cyber Security"
]

problem_solving_style_options = [
    "Analytical", "Creative", "Systematic", "Intuitive", "Collaborative",
    "Data-driven", "Experimental", "Logical", "Pragmatic", "Innovative"
]

career_options = [
    "Software Developer (Backend)", "Software Developer (Frontend)", "Data Scientist",
    "Machine Learning Engineer", "DevOps Engineer", "Cloud Engineer",
    "Cybersecurity Analyst", "UI/UX Designer", "Product Manager", "Project Manager",
    "Research Intern (AI/ML)", "MS in Computer Science", "MS in Data Science",
    "Network Engineer", "Embedded Systems Engineer", "Game Developer",
    "Business Analyst", "Technical Consultant", "Database Administrator",
    "Quality Assurance Engineer", "Solutions Architect", "Full Stack Developer",
    "Research Intern (General)", "Ph.D. Candidate", "Technical Writer",
    "Mobile Developer (Android)", "Mobile Developer (iOS)", "Blockchain Developer",
    "Big Data Engineer", "AI Ethicist"
]

# Function to generate a list of random items from a given options list
def generate_list_items(options, min_items, max_items):
    num_items = random.randint(min_items, max_items)
    return random.sample(options, min(num_items, len(options)))

# Number of synthetic student profiles to generate
num_students = 1000

data = []

for _ in range(num_students):
    # Generate random values for each column
    cgpa = round(random.uniform(6.0, 10.0), 2)
    current_projects_count = random.randint(0, 5)
    expected_salary_range = round(random.uniform(4.0, 20.0), 2) # in Lakhs per annum

    preferred_work_style = random.choice(["Independent", "Collaborative", "Hybrid"])
    wants_to_go_for_masters = random.choice(["yes", "no", "maybe"])
    interested_in_research = random.choice(["yes", "no", "maybe"])
    internship_experience = random.choice([True, False])
    team_vs_solo_preference = random.choice(["Team-oriented", "Solo-focused", "Flexible"])

    # Generate lists for text/list columns
    interest_areas = generate_list_items(interest_areas_options, 2, 5)
    soft_skills = generate_list_items(soft_skills_options, 3, 6)
    programming_languages = generate_list_items(programming_languages_options, 1, 4)
    tools_techstack = generate_list_items(tools_techstack_options, 2, 7)
    current_certifications = generate_list_items(certifications_options, 0, 3)
    extracurricular_interests = generate_list_items(extracurricular_interests_options, 1, 3)
    favourite_subjects = generate_list_items(favourite_subjects_options, 2, 4)
    problem_solving_style = generate_list_items(problem_solving_style_options, 1, 3)

    # Generate 2-3 recommended career options based on some simple rules
    recommended_careers = []
    # Rule 1: High CGPA, research interest -> MS/Research
    if cgpa >= 8.5 and interested_in_research == "yes":
        if "Artificial Intelligence" in interest_areas or "Machine Learning" in interest_areas:
            recommended_careers.append("MS in Data Science")
            recommended_careers.append("Research Intern (AI/ML)")
        else:
            recommended_careers.append("MS in Computer Science")
            recommended_careers.append("Research Intern (General)")
    # Rule 2: Web dev interests + relevant tech -> Software Developer
    if any(item in ["Web Development", "Mobile App Development"] for item in interest_areas) and \
       any(item in ["React", "Angular", "Node.js", "Django", "Flask", "Spring Boot"] for item in tools_techstack):
        recommended_careers.append(random.choice(["Software Developer (Frontend)", "Software Developer (Backend)", "Full Stack Developer"]))
    # Rule 3: Data/ML interests + relevant tech -> Data Scientist/ML Engineer
    if any(item in ["Data Science", "Machine Learning", "Artificial Intelligence", "Big Data"] for item in interest_areas) and \
       any(item in ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "Spark"] for item in tools_techstack):
        recommended_careers.append(random.choice(["Data Scientist", "Machine Learning Engineer", "Big Data Engineer"]))
    # Rule 4: UI/UX interests -> UI/UX Designer
    if "UI/UX Design" in interest_areas and any(item in ["Figma", "Sketch", "Adobe XD"] for item in tools_techstack):
        recommended_careers.append("UI/UX Designer")
    # Rule 5: Project Management/Leadership skills -> Product/Project Manager
    if any(skill in soft_skills for skill in ["Leadership", "Decision Making", "Time Management"]) and \
       any(item in ["Jira", "Confluence", "PMP"] for item in tools_techstack + certifications_options):
        recommended_careers.append(random.choice(["Product Manager", "Project Manager"]))
    # Rule 6: Cybersecurity interests -> Cybersecurity Analyst
    if "Cybersecurity" in interest_areas or "Ethical Hacking" in interest_areas or "CompTIA Security+" in certifications_options:
        recommended_careers.append("Cybersecurity Analyst")
    # Rule 7: DevOps/Cloud interests -> DevOps/Cloud Engineer
    if any(item in ["DevOps", "Cloud Computing"] for item in interest_areas) and \
       any(item in ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins"] for item in tools_techstack):
        recommended_careers.append(random.choice(["DevOps Engineer", "Cloud Engineer"]))
    # Add a general career if not enough specific ones were recommended
    while len(recommended_careers) < 2:
        recommended_careers.append(random.choice(career_options))
        recommended_careers = list(set(recommended_careers)) # Ensure unique
    recommended_careers = random.sample(recommended_careers, min(len(recommended_careers), 3))


    data.append({
        "Interest_Areas": interest_areas,
        "Preferred_Work_Style": preferred_work_style,
        "CGPA": cgpa,
        "Soft_Skills": soft_skills,
        "Programming_Languages": programming_languages,
        "Tools_and_Techstack": tools_techstack,
        "Current_Certifications": current_certifications,
        "Wants_to_Go_for_Masters": wants_to_go_for_masters,
        "Interested_in_Research": interested_in_research,
        "Current_Projects_Count": current_projects_count,
        "Extracurricular_Interests": extracurricular_interests,
        "Favourite_Subjects": favourite_subjects,
        "Internship_Experience": internship_experience,
        "Expected_Salary_Range": expected_salary_range,
        "Problem_Solving_Style": problem_solving_style,
        "Team_vs_Solo_Preference": team_vs_solo_preference,
        "Recommended_Career": recommended_careers # This will be a list of careers
    })

df = pd.DataFrame(data)

# Ensure the 'data' directory exists
os.makedirs('data', exist_ok=True)

# Convert lists to comma-separated strings for CSV compatibility and easier handling later
for col in ["Interest_Areas", "Soft_Skills", "Programming_Languages", "Tools_and_Techstack",
            "Current_Certifications", "Extracurricular_Interests", "Favourite_Subjects",
            "Problem_Solving_Style", "Recommended_Career"]:
    df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

# Display a sample of the generated data
print("Generated Synthetic Dataset Sample:")
print(df.head())

# Save the dataset to a CSV file inside the 'data' directory
csv_file_path = "data/synthetic_career_data.csv"
df.to_csv(csv_file_path, index=False)
print(f"\nSynthetic dataset saved to {csv_file_path}")