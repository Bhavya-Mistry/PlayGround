import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Custom Transformers (MUST BE THE SAME AS IN train_model.py) ---
# These are crucial for the Streamlit app to correctly preprocess user input
# using the transformers fitted during model training.

class TextListTransformer(BaseEstimator, TransformerMixin):
    """
    Transforms a column of comma-separated strings (or lists) into a single
    space-separated string, suitable for TF-IDF vectorization.
    Handles potential NaN values by treating them as empty strings.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Fill NaN values with empty string before joining, then replace ", " with " "
        return X[self.column].fillna('').apply(lambda x: str(x).replace(", ", " ")).values.astype(str)

class NumericColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Selects a specific numerical column from the DataFrame and returns it
    as a 2D array, which is required by scikit-learn transformers like StandardScaler.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.column]]

class CategoricalColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Selects a specific categorical column from the DataFrame and returns it
    as a 2D array, suitable for OneHotEncoder.
    """
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.column]]

# --- Configuration ---
st.set_page_config(layout="wide", page_title="AI-Powered Career Navigator")

# --- Load Pre-trained Model and Preprocessors ---
# The paths are relative to where streamlit_app.py is run
try:
    mlb = joblib.load('models/mlb.pkl')
    model_pipeline = joblib.load('models/model_pipeline.pkl')
    # NEW: Load pre-computed student embeddings and Sentence-BERT model
    student_embeddings = np.load('models/student_embeddings.npy')
    # Re-instantiate SentenceTransformer. It will download if not cached locally.
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load the original DataFrame to map back to original data for semantic explanations
    df_original = pd.read_csv('data/synthetic_career_data.csv')
    # Make sure to re-process lists in df_original for semantic lookup if you want to display them
    for col in ["Interest_Areas", "Soft_Skills", "Programming_Languages", "Tools_and_Techstack",
                "Current_Certifications", "Extracurricular_Interests", "Favourite_Subjects",
                "Problem_Solving_Style", "Recommended_Career"]:
        df_original[col] = df_original[col].apply(lambda x: [item.strip() for item in str(x).split(', ')] if pd.notna(x) and x != '' else [])


    st.success("Models and preprocessors loaded successfully!")
except FileNotFoundError:
    st.error("Model or embedding files not found! Please ensure you have run "
             "`synthetic_dataset_generator.py` and then `train_model.py` "
             "to create the necessary files in the `data/` and `models/` directories.")
    st.info("Check the folder structure: `models/mlb.pkl`, `models/model_pipeline.pkl`, "
            "and `models/student_embeddings.npy` should exist.")
    st.stop() # Stop the app if model isn't loaded

# --- Helper Functions ---

def predict_career_paths(user_data_df, model, mlb_transformer):
    """
    Makes a prediction using the trained model and returns human-readable career paths
    with their confidence scores. It returns the top 3 most probable careers.
    """
    # Get probabilities for each output classifier.
    # This returns a list where each element is an array of shape (n_samples, 2),
    # representing probabilities for [class_0, class_1] for that specific output label.
    raw_probas_list = model.predict_proba(user_data_df)

    # For each output (career), extract the probability of the positive class (index 1).
    # Since user_data_df has only one sample, we take [0][1] for each probability array.
    # This results in a 1D array of probabilities, one for each career class.
    prediction_proba_for_each_career = np.array([proba[0][1] for proba in raw_probas_list])

    # Get top 3 predictions based on probability
    top_indices = np.argsort(prediction_proba_for_each_career)[::-1][:3] # Sort descending, take top 3

    # Map these indices back to the actual career labels and their probabilities
    top_careers = mlb_transformer.classes_[top_indices]
    top_probabilities = prediction_proba_for_each_career[top_indices]

    # Return a list of tuples: (career_name, probability)
    return list(zip(top_careers, top_probabilities))

def get_combined_text_from_user_input(user_data):
    """Combines all text-based inputs into a single string for semantic embedding."""
    all_text = []
    # Ensure all values are lists before extending
    all_text.extend(user_data.get('Interest_Areas', []))
    all_text.extend(user_data.get('Soft_Skills', []))
    all_text.extend(user_data.get('Programming_Languages', []))
    all_text.extend(user_data.get('Tools_and_Techstack', []))
    all_text.extend(user_data.get('Current_Certifications', []))
    all_text.extend(user_data.get('Extracurricular_Interests', []))
    all_text.extend(user_data.get('Favourite_Subjects', []))
    all_text.extend(user_data.get('Problem_Solving_Style', []))
    # Filter out empty strings or non-string items that might creep in
    return ' '.join(filter(lambda x: isinstance(x, str) and x.strip() != '', all_text))

def find_similar_profiles(user_embedding, all_student_embeddings, original_df, num_similar=2):
    """
    Finds the most semantically similar student profiles from the training data.
    Returns their original career paths and a brief summary.
    """
    similarities = cosine_similarity(user_embedding.reshape(1, -1), all_student_embeddings)[0]
    # Get indices of top similar profiles, excluding self-similarity if the user profile was in training data (not here)
    top_indices = np.argsort(similarities)[::-1][:num_similar]

    similar_profiles_info = []
    for idx in top_indices:
        profile_data = original_df.iloc[idx]
        similar_profiles_info.append({
            "careers": profile_data['Recommended_Career'], # This is already a list due to df_original loading
            "cgpa": profile_data['CGPA'],
            "projects": profile_data['Current_Projects_Count'],
            "similarity_score": similarities[idx]
        })
    return similar_profiles_info

# --- Streamlit UI ---

st.title("🎓 AI-Powered Career Navigator")
st.markdown("---")
st.markdown("Welcome, future engineer! 🚀")
st.markdown("This tool helps 1st and 2nd-year college students explore potential career paths "
            "based on their interests, skills, and academic profile. "
            "Fill in the details below to get personalized recommendations.")
st.markdown("---")

# --- User Input Form ---
st.header("Your Profile Details")
with st.form("career_input_form"):
    col1, col2 = st.columns(2) # Use columns for better layout

    with col1:
        st.subheader("Academic & Work Preferences")
        cgpa = st.slider("CGPA (on a scale of 10)", 0.0, 10.0, 7.5, 0.1, help="Your academic performance.")
        current_projects_count = st.number_input("Number of Personal/Academic Projects Completed", min_value=0, max_value=20, value=2, help="Projects demonstrate practical application of skills.")
        expected_salary_range = st.number_input("Expected Salary Range (in Lakhs per annum, e.g., 7.0 for 7 LPA)", min_value=0.0, max_value=50.0, value=7.0, step=0.5, help="What salary bracket are you aiming for?")
        internship_experience = st.radio("Do you have Internship Experience?", (True, False), index=1, help="Any prior industry exposure?")
        wants_to_go_for_masters = st.radio("Do you envision pursuing Masters (M.S./M.Tech) after your Bachelor's?", ("yes", "no", "maybe"), index=1, help="Your long-term academic aspirations.")
        interested_in_research = st.radio("Are you interested in Research (academic or industry-based)?", ("yes", "no", "maybe"), index=1, help="Do you enjoy exploring new concepts and contributing to knowledge?")
        preferred_work_style = st.selectbox("Preferred Work Style", ["Independent", "Collaborative", "Hybrid"], help="Do you prefer working alone, in teams, or a mix?")
        team_vs_solo_preference = st.selectbox("Team vs. Solo Project Preference", ["Team-oriented", "Solo-focused", "Flexible"], help="When working on projects, do you prefer team settings or working alone?")


    with col2:
        st.subheader("Skills & Interests")
        # Define options for multiselects - keep these consistent with synthetic_dataset_generator.py
        interest_areas_options = [
            "Web Development", "Mobile App Development", "Data Science", "Machine Learning",
            "Artificial Intelligence", "Cloud Computing", "Cybersecurity", "Networking",
            "Embedded Systems", "Robotics", "Game Development", "UI/UX Design",
            "Project Management", "Technical Writing", "DevOps", "Blockchain",
            "Bioinformatics", "Quantum Computing", "Finance Technology", "Digital Marketing",
            "IoT", "Computer Vision", "Natural Language Processing", "Big Data",
            "Ethical Hacking", "Consulting", "Entrepreneurship"
        ]
        interest_areas = st.multiselect("Select your top Interest Areas (2-5 options recommended)", interest_areas_options, default=["Data Science", "Machine Learning"], help="What technical domains genuinely excite you?")

        soft_skills_options = [
            "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
            "Adaptability", "Time Management", "Creativity", "Leadership",
            "Decision Making", "Emotional Intelligence", "Conflict Resolution",
            "Networking", "Presentation Skills", "Negotiation", "Empathy"
        ]
        soft_skills = st.multiselect("Select your strongest Soft Skills (3-6 options recommended)", soft_skills_options, default=["Problem Solving", "Teamwork"], help="Interpersonal and personal attributes important for career success.")

        programming_languages_options = [
            "Python", "Java", "C++", "JavaScript", "C#", "Go", "Rust", "Swift",
            "Kotlin", "PHP", "Ruby", "TypeScript", "SQL", "R", "Dart"
        ]
        programming_languages = st.multiselect("Select Programming Languages you are familiar with", programming_languages_options, default=["Python"], help="Which coding languages do you know?")

        tools_techstack_options = [
            "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "React", "Angular",
            "Vue.js", "Node.js", "Django", "Flask", "Spring Boot", "TensorFlow", "PyTorch",
            "Scikit-learn", "Pandas", "NumPy", "MongoDB", "PostgreSQL", "MySQL",
            "Figma", "Sketch", "Adobe XD", "Unity", "Unreal Engine", "Jira", "Confluence",
            "Tableau", "Power BI", "Spark", "Hadoop", "Kafka", "Salesforce", "Android Studio",
            "Xcode", "VS Code", "Jupyter Notebook", "Postman", "Terraform", "Ansible",
            "Jenkins", "CircleCI", "GitLab CI/CD", "Selenium", "Jest", "Cypress"
        ]
        tools_techstack = st.multiselect("Select Tools and Technologies you have experience with", tools_techstack_options, default=["Pandas", "Scikit-learn"], help="Software, frameworks, or platforms you've used.")

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
        current_certifications = st.multiselect("Any Current Certifications?", certifications_options, help="Official certifications you've obtained.")

        extracurricular_interests_options = [
            "Coding Clubs", "Hackathons", "Robotics Competitions", "Debate Clubs",
            "Sports", "Volunteering", "Music", "Photography", "Gaming",
            "Entrepreneurship Clubs", "Community Service", "Student Government",
            "Technical Writing", "Blogging", "Podcast creation", "Graphic Design"
        ]
        extracurricular_interests = st.multiselect("Extracurricular Interests/Activities", extracurricular_interests_options, help="Activities outside academics that you are passionate about.")

        favourite_subjects_options = [
            "Data Structures and Algorithms", "Operating Systems", "Database Management Systems",
            "Computer Networks", "Software Engineering", "Artificial Intelligence",
            "Machine Learning", "Linear Algebra", "Calculus", "Probability and Statistics",
            "Physics", "Chemistry", "Biology", "Economics", "Psychology",
            "Discrete Mathematics", "Object-Oriented Programming", "Web Technologies",
            "Cloud Computing", "Cyber Security"
        ]
        favourite_subjects = st.multiselect("Favourite Subjects in College", favourite_subjects_options, help="Subjects you enjoy learning or excel in.")

        problem_solving_style_options = [
            "Analytical", "Creative", "Systematic", "Intuitive", "Collaborative",
            "Data-driven", "Experimental", "Logical", "Pragmatic", "Innovative"
        ]
        problem_solving_style = st.multiselect("Problem Solving Style", problem_solving_style_options, default=["Analytical"], help="How do you typically approach and solve problems?")

    st.markdown("---")
    submitted = st.form_submit_button("✨ Find My Career Path!")

    if submitted:
        # Create a DataFrame from user input
        # Note: For the ML model, these are converted to comma-separated strings inside the dataframe.
        # For semantic search, we use the actual lists passed to `get_combined_text_from_user_input`.
        user_data_for_df = {
            "Interest_Areas": ", ".join(interest_areas),
            "Preferred_Work_Style": preferred_work_style,
            "CGPA": cgpa,
            "Soft_Skills": ", ".join(soft_skills),
            "Programming_Languages": ", ".join(programming_languages),
            "Tools_and_Techstack": ", ".join(tools_techstack),
            "Current_Certifications": ", ".join(current_certifications),
            "Wants_to_Go_for_Masters": wants_to_go_for_masters,
            "Interested_in_Research": interested_in_research,
            "Current_Projects_Count": current_projects_count,
            "Extracurricular_Interests": ", ".join(extracurricular_interests),
            "Favourite_Subjects": ", ".join(favourite_subjects),
            "Internship_Experience": internship_experience,
            "Expected_Salary_Range": expected_salary_range,
            "Problem_Solving_Style": ", ".join(problem_solving_style),
            "Team_vs_Solo_Preference": team_vs_solo_preference,
        }
        user_df_for_model = pd.DataFrame([user_data_for_df])

        st.subheader("Your Top Career Recommendations:")
        if 'model_pipeline' in locals() and 'mlb' in locals() and 'sentence_model' in locals():
            with st.spinner("Analyzing your profile and generating recommendations..."):
                recommended_paths_with_probs = predict_career_paths(user_df_for_model, model_pipeline, mlb)

                # Generate combined text for the user's current input for semantic search
                user_combined_text_for_embedding = get_combined_text_from_user_input({
                    "Interest_Areas": interest_areas, "Soft_Skills": soft_skills,
                    "Programming_Languages": programming_languages, "Tools_and_Techstack": tools_techstack,
                    "Current_Certifications": current_certifications, "Extracurricular_Interests": extracurricular_interests,
                    "Favourite_Subjects": favourite_subjects, "Problem_Solving_Style": problem_solving_style
                })
                # Generate embedding for the user's profile
                user_embedding = sentence_model.encode([user_combined_text_for_embedding])[0]
                # Find similar profiles from the pre-computed embeddings
                similar_profiles = find_similar_profiles(user_embedding, student_embeddings, df_original, num_similar=2)


            if recommended_paths_with_probs:
                for i, (career, prob) in enumerate(recommended_paths_with_probs):
                    st.success(f"**{i+1}. {career}** (Confidence: {prob*100:.2f}%)")
                    st.markdown(f"") # Small space

                    # --- Explanation ---
                    st.markdown(f"**Why {career}?**")
                    explanation_points = []

                    career_lower = career.lower()

                    if "data scientist" in career_lower or "machine learning engineer" in career_lower or "big data engineer" in career_lower:
                        if any(i_area in interest_areas for i_area in ["Data Science", "Machine Learning", "Artificial Intelligence", "Big Data"]):
                            explanation_points.append(f"- Your strong interest in **Data Science/ML/AI** domains is a key driver.")
                        if "Python" in programming_languages: explanation_points.append(f"- Your proficiency in **Python** is highly valuable for data roles.")
                        if any(tool in tools_techstack for tool in ["Scikit-learn", "TensorFlow", "PyTorch", "Pandas", "Spark"]): explanation_points.append(f"- Your experience with tools like **{', '.join(set(tools_techstack).intersection(['Scikit-learn', 'TensorFlow', 'PyTorch', 'Pandas', 'Spark']))}** directly supports this path.")
                        if cgpa >= 8.0: explanation_points.append(f"- Your strong academic record (CGPA {cgpa}) provides a solid analytical foundation.")
                        if "Analytical" in problem_solving_style: explanation_points.append(f"- Your **Analytical** problem-solving style aligns well with data-driven roles.")
                        if "Probability and Statistics" in favourite_subjects: explanation_points.append(f"- Your interest in **Probability and Statistics** is a foundational strength.")

                    elif "software developer" in career_lower or "full stack developer" in career_lower or "mobile developer" in career_lower:
                        if any(i_area in interest_areas for i_area in ["Web Development", "Mobile App Development", "Game Development"]):
                            explanation_points.append(f"- Your keen interest in **{', '.join(set(interest_areas).intersection(['Web Development', 'Mobile App Development', 'Game Development']))}** is a strong indicator.")
                        if any(lang in programming_languages for lang in ["Java", "Python", "JavaScript", "C++", "C#", "Kotlin", "Swift"]): explanation_points.append(f"- Your skills in languages like **{', '.join(set(programming_languages).intersection(['Java', 'Python', 'JavaScript', 'C++', 'C#', 'Kotlin', 'Swift']))}** are essential for development.")
                        if any(tool in tools_techstack for tool in ["React", "Angular", "Node.js", "Django", "Flask", "Spring Boot", "Android Studio", "Xcode", "Unity", "Unreal Engine"]): explanation_points.append(f"- Your familiarity with frameworks/tools like **{', '.join(set(tools_techstack).intersection(['React', 'Node.js', 'Spring Boot', 'Android Studio']))}** is a great asset.")
                        if current_projects_count >= 2: explanation_points.append(f"- Your {current_projects_count} projects demonstrate practical development experience.")
                        if "Data Structures and Algorithms" in favourite_subjects: explanation_points.append(f"- Your strong grasp of **Data Structures and Algorithms** is fundamental for coding roles.")

                    elif "ui/ux designer" in career_lower:
                        if "UI/UX Design" in interest_areas: explanation_points.append(f"- Your primary interest in **UI/UX Design** directly matches this role.")
                        if any(skill in soft_skills for skill in ["Creativity", "Communication", "Empathy"]): explanation_points.append(f"- Your **Creativity** and **Communication** skills are highly valued in design.")
                        if any(tool in tools_techstack for tool in ["Figma", "Sketch", "Adobe XD"]): explanation_points.append(f"- Your experience with design tools like **{', '.join(set(tools_techstack).intersection(['Figma', 'Adobe XD']))}** is a direct fit.")
                        if "Collaborative" in preferred_work_style: explanation_points.append(f"- Your **Collaborative** work style is ideal for team-based design projects.")
                        if "Graphic Design" in extracurricular_interests: explanation_points.append(f"- Your extracurricular interest in **Graphic Design** provides a creative edge.")

                    elif "ms in computer science" in career_lower or "ms in data science" in career_lower or "ph.d. candidate" in career_lower or "research intern" in career_lower:
                        if wants_to_go_for_masters == "yes": explanation_points.append(f"- Your stated desire to pursue **Masters** perfectly aligns with this academic path.")
                        if interested_in_research == "yes": explanation_points.append(f"- Your strong interest in **Research** is a key indicator for higher studies.")
                        if cgpa >= 8.5: explanation_points.append(f"- Your excellent academic record (CGPA {cgpa}) is a significant advantage for graduate programs.")
                        if current_projects_count >= 3: explanation_points.append(f"- Your {current_projects_count} projects, especially if research-oriented, strengthen your application.")
                        if "Research Intern (AI/ML)" in career and ("Artificial Intelligence" in interest_areas or "Machine Learning" in interest_areas): explanation_points.append(f"- Your specific interest in **AI/ML** makes research in these areas a great fit.")

                    elif "product manager" in career_lower or "project manager" in career_lower or "business analyst" in career_lower:
                        if any(skill in soft_skills for skill in ["Leadership", "Decision Making", "Communication", "Problem Solving", "Time Management"]):
                            explanation_points.append(f"- Your strong **Leadership, Decision Making, and Communication** skills are critical for these roles.")
                        if any(cert in current_certifications for cert in ["Project Management Professional (PMP)", "Certified ScrumMaster (CSM)"]): explanation_points.append(f"- Your **Project Management certifications** provide a formal foundation.")
                        if "Collaborative" in preferred_work_style: explanation_points.append(f"- Your **Collaborative** work style is ideal for guiding teams.")
                        if "Entrepreneurship Clubs" in extracurricular_interests: explanation_points.append(f"- Your involvement in **Entrepreneurship Clubs** shows initiative and strategic thinking.")

                    elif "devops engineer" in career_lower or "cloud engineer" in career_lower:
                        if any(i_area in interest_areas for i_area in ["DevOps", "Cloud Computing"]):
                            explanation_points.append(f"- Your strong interest in **DevOps and Cloud Computing** is highly relevant.")
                        if any(tool in tools_techstack for tool in ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins"]): explanation_points.append(f"- Your experience with **{', '.join(set(tools_techstack).intersection(['Docker', 'Kubernetes', 'AWS', 'Azure', 'Jenkins']))}** directly applies to this field.")
                        if any(lang in programming_languages for lang in ["Python", "Go", "Bash"]): explanation_points.append(f"- Proficiency in scripting languages like **Python** or **Go** is beneficial.")
                        if "Operating Systems" in favourite_subjects or "Computer Networks" in favourite_subjects: explanation_points.append(f"- Your foundational knowledge in **Operating Systems and Networking** is a solid base.")

                    if not explanation_points:
                        explanation_points.append("- Based on a comprehensive analysis of your diverse skills and interests.")
                        explanation_points.append("- Consider exploring various aspects of your profile as some of your inputs are generic.")

                    for point in explanation_points:
                        st.markdown(point)

                    # NEW: Add semantic similarity explanation
                    st.markdown("**How your profile compares to others:**")
                    if similar_profiles:
                        for sp in similar_profiles:
                            st.markdown(f"- Your profile is **{sp['similarity_score']:.2f}** similar to students who pursued careers like **{', '.join(sp['careers'])}**. "
                                        f"They often had a CGPA around {sp['cgpa']:.1f} and completed about {sp['projects']} projects.")
                    else:
                        st.markdown("- Could not find highly similar profiles in our dataset for comparison.")


                    # --- Suggested Resources ---
                    st.markdown(f"**Resources to help you explore {career}:**")
                    if "data scientist" in career_lower or "machine learning engineer" in career_lower or "big data engineer" in career_lower:
                        st.markdown("- **Courses:** Coursera's 'Deep Learning Specialization' (Andrew Ng), IBM Data Science Professional Certificate.")
                        st.markdown("- **Certifications:** Google Data Analytics Certificate, AWS Certified Machine Learning – Specialty.")
                        st.markdown("- **Platforms:** Kaggle (for competitions), Medium/Towards Data Science (for articles and tutorials).")
                        st.markdown("- **Practice:** Work on real-world datasets, build end-to-end ML projects.")
                    elif "software developer" in career_lower or "full stack developer" in career_lower or "mobile developer" in career_lower:
                        st.markdown("- **Courses:** freeCodeCamp, Udemy/Coursera courses on specific frameworks (e.g., React, Node.js, Spring Boot, Android Development).")
                        st.markdown("- **Certifications:** Microsoft Certified: Azure Developer Associate, AWS Certified Developer – Associate.")
                        st.markdown("- **Platforms:** LeetCode/HackerRank (for coding practice), GitHub (for open-source contributions and portfolio).")
                        st.markdown("- **Projects:** Build personal projects, contribute to open-source, participate in hackathons.")
                    elif "ui/ux designer" in career_lower:
                        st.markdown("- **Courses:** Google UX Design Professional Certificate, Interaction Design Foundation.")
                        st.markdown("- **Tools:** Master design tools like Figma, Adobe XD, Sketch.")
                        st.markdown("- **Communities:** Dribbble, Behance (for portfolio inspiration and sharing work).")
                        st.markdown("- **Practice:** Conduct user research, create wireframes, prototypes, and user flows for various apps/websites.")
                    elif "ms in computer science" in career_lower or "ms in data science" in career_lower or "ph.d. candidate" in career_lower or "research intern" in career_lower:
                        st.markdown("- **Preparation:** Prepare for GRE/GATE exams (if required), build strong academic projects with research components.")
                        st.markdown("- **Guidance:** Connect with professors, alumni, and university career services for application strategies and research opportunities.")
                        st.markdown("- **Resources:** Explore university research labs, faculty publications, and attend academic conferences.")
                        st.markdown("- **Skills:** Strengthen your analytical, writing, and presentation skills.")
                    elif "product manager" in career_lower or "project manager" in career_lower or "business analyst" in career_lower:
                        st.markdown("- **Courses:** Product Management courses on Coursera/Udemy, certifications like CSM (Certified ScrumMaster).")
                        st.markdown("- **Skills:** Focus on developing leadership, communication, strategic thinking, and analytical skills.")
                        st.markdown("- **Experience:** Seek out opportunities to lead projects, even small ones, or join relevant student organizations.")
                        st.markdown("- **Resources:** Read books on product management, follow industry blogs (e.g., Product Hunt, Aha!).")
                    elif "devops engineer" in career_lower or "cloud engineer" in career_lower:
                        st.markdown("- **Courses:** Cloud provider certifications (AWS Certified Cloud Practitioner/Solutions Architect, Azure Fundamentals), DevOps courses.")
                        st.markdown("- **Tools:** Hands-on practice with Docker, Kubernetes, Terraform, Jenkins, Git.")
                        st.markdown("- **Skills:** Learn scripting (Python, Bash), networking fundamentals, and automation principles.")
                        st.markdown("- **Projects:** Set up CI/CD pipelines, deploy applications to cloud platforms.")
                    else:
                        st.markdown("- Further research on **{career}** on platforms like LinkedIn, Glassdoor, and specific company career pages to understand role requirements and growth paths.")
                    st.markdown("---")
            else:
                st.info("No clear career paths could be recommended based on your input. Please try adjusting your details or selecting more specific interests/skills to help the model learn.")
        else:
            st.warning("Model and/or semantic search components are not loaded. Please ensure `train_model.py` was run successfully.")

st.sidebar.markdown("---")
st.sidebar.info("This AI-Powered Career Navigator is designed to provide guidance and suggestions. "
                "Always combine these recommendations with personal introspection, mentorship, and further research.")
st.sidebar.write("Developed with ❤️ by Your Name/Team Name")
st.sidebar.markdown("---")