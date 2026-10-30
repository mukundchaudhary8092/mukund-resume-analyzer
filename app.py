import re
from io import BytesIO
from datetime import datetime
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="Mukund Chaudhary | Resume Analyzer", page_icon="📄", layout="wide")

ROLE_SKILLS = {
    "Python Developer": ["python", "sql", "git", "github", "oop", "data structures", "algorithms", "flask", "django", "fastapi", "rest api", "pandas", "numpy", "testing"],
    "Data Analyst": ["sql", "excel", "python", "pandas", "numpy", "power bi", "tableau", "statistics", "data visualization", "data cleaning", "dashboard", "matplotlib", "seaborn"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "express", "python", "django", "flask", "git", "github", "responsive design", "rest api", "sql"],
    "Machine Learning Engineer": ["python", "machine learning", "deep learning", "scikit-learn", "tensorflow", "pytorch", "pandas", "numpy", "sql", "statistics", "feature engineering", "model evaluation", "nlp", "computer vision"],
}

def extract_pdf_text(file):
    reader = PdfReader(BytesIO(file.getvalue()))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

def match_skills(text, skills):
    text = re.sub(r"\s+", " ", text.lower())
    found, missing = [], []
    for skill in skills:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        (found if re.search(pattern, text) else missing).append(skill)
    return found, missing

st.markdown("""
<div style="padding:22px;border-radius:14px;background:linear-gradient(110deg,#14213d,#263b60);color:white">
<div style="opacity:.8">PORTFOLIO PROJECT BY</div>
<div style="font-size:30px;font-weight:700">Mukund Chaudhary</div>
<div style="font-size:20px;margin-top:6px">📄 Resume Analyzer</div>
<div style="opacity:.9">Check resume keywords, find skill gaps, and get practical suggestions.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("About this project")
    st.write("Built with Python and Streamlit.")
    st.caption("No API key required. Your PDF is processed during this app session.")
    st.write("**Created by Mukund Chaudhary**")

c1, c2 = st.columns(2)
with c1:
    candidate = st.text_input("Your name", "Mukund Chaudhary")
    role = st.selectbox("Choose target role", list(ROLE_SKILLS))
with c2:
    pdf = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    st.caption("Text-based PDFs work best; scanned image-only PDFs may not extract.")

job = st.text_area("Optional: paste a job description", height=130,
                   placeholder="Paste the job description to include its keywords...")
if st.button("Analyze my resume", type="primary", use_container_width=True):
    if not pdf:
        st.error("Please upload your resume PDF first.")
        st.stop()
    try:
        resume = extract_pdf_text(pdf)
    except Exception as exc:
        st.error(f"Could not read this PDF: {exc}")
        st.stop()
    if len(resume) < 40:
        st.warning("Very little text was extracted. This may be a scanned PDF. Export it as a text-based PDF and try again.")
        st.stop()

    skills = list(ROLE_SKILLS[role])
    if job.strip():
        stop = {"the","and","for","with","you","your","our","are","will","have","has","this","that","from","years","year","work","role","job","team","who","what","all","can","not","their","about","into","must","able","using"}
        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", job.lower())
        skills = list(dict.fromkeys(skills + [w for w in words if w not in stop]))[:50]

    found, missing = match_skills(resume, skills)
    score = round(100 * len(found) / len(skills)) if skills else 0

    tips = []
    if missing:
        tips.append("Review missing keywords and include only skills you genuinely have.")
    if not re.search(r"\b(project|projects)\b", resume, re.I):
        tips.append("Add 2–3 relevant projects and describe your contribution.")
    if not re.search(r"\b(internship|experience|work experience)\b", resume, re.I):
        tips.append("If applicable, include internships, freelance work, volunteering, or practical experience.")
    if not re.search(r"\b(education|bachelor|degree|university|college)\b", resume, re.I):
        tips.append("Make your education details easy to find.")
    tips += ["Use clear headings and concise bullet points.", "Add measurable results where possible and proofread the final PDF."]

    st.divider()
    st.subheader("Your analysis")
    a, b, c = st.columns(3)
    a.metric("Keyword coverage", f"{score}%")
    b.metric("Keywords found", len(found))
    c.metric("Potential gaps", len(missing))
    st.progress(score / 100)
    st.info("This is a rule-based keyword coverage percentage, not an ATS score or a prediction of interview selection.")

    good, gap = st.columns(2)
    with good:
        st.markdown("#### ✅ Keywords found")
        st.write("\n".join("• " + x for x in found) if found else "No matching keywords detected.")
    with gap:
        st.markdown("#### 🔎 Potential missing keywords")
        st.write("\n".join("• " + x for x in missing) if missing else "No gaps in this keyword list.")
    st.markdown("#### 💡 Suggestions")
    for tip in tips:
        st.write("• " + tip)

    report = [
        "RESUME ANALYSIS REPORT", f"Candidate: {candidate}", f"Target role: {role}",
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        f"Keyword coverage: {score}/100", "", "KEYWORDS FOUND:",
        *(["- " + x for x in found] or ["- None detected"]), "", "POTENTIAL GAPS:",
        *(["- " + x for x in missing] or ["- None detected"]), "", "SUGGESTIONS:",
        *["- " + x for x in tips], "",
        "Note: Rule-based keyword check only. A keyword match does not prove proficiency."
    ]
    st.download_button("⬇️ Download analysis report", "\n".join(report),
                       file_name="mukund_resume_analysis_report.txt", mime="text/plain",
                       use_container_width=True)

st.divider()
st.caption("© Mukund Chaudhary | Resume Analyzer | Python + Streamlit")
