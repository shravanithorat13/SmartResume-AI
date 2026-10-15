
import re
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    import PyPDF2
except: PyPDF2=None
try:
    from docx import Document
except: Document=None

st.set_page_config(page_title="SmartResume AI", page_icon="🧠", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#f8fafc,#eef2ff)}
.hero{padding:38px;border-radius:25px;background:linear-gradient(120deg,#111827,#4338ca,#0f766e);color:white;box-shadow:0 15px 40px #0002}
.hero h1{font-size:46px;margin:0}.hero p{font-size:18px;opacity:.9}
.card{padding:20px;border:1px solid #e2e8f0;border-radius:18px;background:white;box-shadow:0 8px 25px #0000000b}
</style>
""",unsafe_allow_html=True)

SKILLS=["python","java","c++","javascript","typescript","sql","mysql","postgresql","mongodb","html","css","react","node.js","django","flask","fastapi","machine learning","deep learning","data science","pandas","numpy","scikit-learn","tensorflow","pytorch","nlp","computer vision","power bi","tableau","excel","git","github","aws","azure","docker","kubernetes","linux","rest api","communication","leadership"]

def text_of(f):
    n=f.name.lower()
    if n.endswith(".pdf") and PyPDF2:
        return "\n".join(p.extract_text() or "" for p in PyPDF2.PdfReader(f).pages)
    if n.endswith(".docx") and Document:
        return "\n".join(p.text for p in Document(f).paragraphs)
    if n.endswith(".txt"): return f.read().decode("utf8","ignore")
    return ""
def skills(t):
    t=re.sub(r"\s+"," ",t.lower())
    return sorted({s for s in SKILLS if re.search(r"(?<!\w)"+re.escape(s)+r"(?!\w)",t)})
def match(a,b):
    v=TfidfVectorizer(stop_words="english",ngram_range=(1,2)); m=v.fit_transform([a,b])
    return round(float(cosine_similarity(m[0:1],m[1:2])[0][0])*100,1)

if "page" not in st.session_state: st.session_state.page="Home"
with st.sidebar:
    st.markdown("## 🧠 SmartResume AI")
    st.caption("Intelligent Resume Screening")
    page=st.radio("MENU",["Home","Screen Resumes","Analytics"])
    st.divider()
    st.markdown("### ✨ Smart Tools")
    st.caption("Resume Parsing")
    st.caption("AI Match Scoring")
    st.caption("Skill Detection")
    st.caption("Candidate Ranking")
    st.divider()
    st.caption("© ShravaniThorat_13")

if page=="Home":
    st.markdown('<div class="hero"><h1>SmartResume AI 🚀</h1><p>Transform resumes into intelligent candidate insights — faster, smarter and beautifully.</p></div>',unsafe_allow_html=True)
    st.write("")
    a,b,c,d=st.columns(4)
    a.metric("⚡ AI Screening","Fast")
    b.metric("🎯 Match Score","0–100%")
    c.metric("📄 File Types","PDF / DOCX / TXT")
    d.metric("🏆 Ranking","Automatic")
    st.markdown("### ✨ Intelligent Recruitment Toolkit")
    cols=st.columns(3)
    items=[("📄","Smart Resume Parser","Extract candidate information from uploaded resumes."),
           ("🎯","AI Job Matching","Compare every resume against your job description."),
           ("🧠","Skill Intelligence","Detect relevant technical and professional skills."),
           ("🏆","Candidate Ranking","Automatically identify the strongest matches."),
           ("📊","Hiring Analytics","Explore scores and compare candidates visually."),
           ("⬇️","Report Export","Download a clean screening report as CSV.")]
    for i,(ic,t,d) in enumerate(items):
        cols[i%3].markdown(f'<div class="card"><h2>{ic}</h2><h4>{t}</h4><p>{d}</p></div>',unsafe_allow_html=True)
    st.write("")
    st.info("👈 Select **Screen Resumes** from the menu to start your AI screening.")

elif page=="Screen Resumes":
    st.markdown("## 🎯 AI Resume Screening")
    st.caption("Turn a job description and multiple resumes into a ranked candidate shortlist.")
    job=st.text_area("📌 Job Description",height=170,placeholder="Paste the complete job description here...")
    files=st.file_uploader("📤 Upload Candidate Resumes",["pdf","docx","txt"],accept_multiple_files=True)
    threshold=st.slider("🎚️ Shortlist threshold",0,100,40,5)
    if st.button("🚀 Analyze & Rank Candidates",use_container_width=True,type="primary"):
        if not job.strip() or not files: st.error("Add a job description and at least one resume.")
        else:
            out=[]
            for f in files:
                t=text_of(f); s=match(t,job); sk=skills(t)
                out.append({"Candidate":f.name,"Match Score":s,"Skills":", ".join(sk) or "None detected","Status":"✅ Shortlisted" if s>=threshold else "Review"})
            st.session_state.results=sorted(out,key=lambda x:x["Match Score"],reverse=True)
            st.success(f"Analysis complete — {len(out)} candidates screened.")
    if "results" in st.session_state:
        st.markdown("### 🏆 Candidate Leaderboard")
        for i,r in enumerate(st.session_state.results,1):
            with st.container(border=True):
                x,y,z=st.columns([.7,2.4,1.3])
                x.markdown(f"## #{i}")
                y.markdown(f"**{r['Candidate']}**  \n{r['Status']}  \n*{r['Skills']}*")
                z.metric("Match",f"{r['Match Score']}%")
                st.progress(min(r["Match Score"]/100,1))
        df=pd.DataFrame(st.session_state.results)
        st.download_button("⬇️ Download Screening Report",df.to_csv(index=False),"SmartResume_Report.csv","text/csv",use_container_width=True)

else:
    st.markdown("## 📊 Hiring Analytics")
    if "results" not in st.session_state: st.info("Run a screening first to unlock analytics.")
    else:
        df=pd.DataFrame(st.session_state.results)
        a,b,c=st.columns(3)
        a.metric("👥 Candidates",len(df)); b.metric("📈 Average Score",f"{df['Match Score'].mean():.1f}%"); c.metric("🥇 Top Candidate",f"{df['Match Score'].max():.1f}%")
        st.markdown("### Match Score Comparison")
        st.bar_chart(df.set_index("Candidate")["Match Score"])
        st.dataframe(df,use_container_width=True,hide_index=True)
