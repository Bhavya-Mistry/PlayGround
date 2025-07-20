import streamlit as st
from .resume_parser import parse_resume
from .gemini_handler import get_gemini_response
from .prompts import build_ats_prompt

def run():
    # st.set_page_config(page_title="Smart ATS Resume Evaluator", layout="centered")
    st.title("📄 Smart ATS Resume Evaluator (Offline + Free)")

    uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
    job_role = st.text_input("Target Job Role", value="Software Engineer")

    if uploaded_file and st.button("Evaluate"):
        with st.spinner("Reading your resume..."):
            resume_text = parse_resume(uploaded_file)

        if resume_text.startswith("Unsupported"):
            st.error(resume_text)
        else:
            st.subheader("📃 Extracted Resume Text")
            st.text_area("Preview", resume_text, height=250)

            with st.spinner("Sending to Gemini for evaluation..."):
                prompt = build_ats_prompt(resume_text, job_role)
                result = get_gemini_response(prompt)

            st.subheader("✅ ATS Evaluation")
            st.markdown(result)

# Call the app
if __name__ == "__main__":
    run()
