import streamlit as st
import os
import tempfile
import shutil
import json
from sentence_transformers import SentenceTransformer, util
import csv
import ast
from collections import defaultdict
import google.generativeai as genai
from neo4j import GraphDatabase
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")


# --- Custom Pastel Gradient CSS (disesuaikan dengan main.py dan dipercantik) ---
st.markdown('''
    <style>
    /* Global light mode background dengan gradient biru muda */
    body, .stApp {
        background: linear-gradient(135deg, #f2f6f9 0%, #d4eaf7 100%) !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .stApp {
        background: linear-gradient(120deg, #f2f6f9 0%, #d4eaf7 100%) !important;
    }
    
    /* Header (Streamlit's default header) */
    header, .css-18e3th9, .css-1d391kg, .css-1v0mbdj, .css-1dp5vir {
        background: transparent !important;
    }

    /* Main content block styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-radius: 18px;
        box-shadow: 0 4px 32px 0 rgba(160, 160, 200, 0.10); /* Shadow lebih light untuk light mode */
        background: rgba(255,255,255,0.7) !important; /* Background putih transparan */
        padding-left: 3rem; /* Tambah padding biar lebih lega */
        padding-right: 3rem;
        border: none !important; /* Hapus border yang tadi di dark mode */
        /* max-width: 1000px !important;*/
    }

    
    /* --- STYLING UNTUK SKILL TAGS/CHIPS --- */
    .skills-container {
        display: flex; /* Menggunakan flexbox untuk layout tags */
        flex-wrap: wrap; /* Memungkinkan tags untuk wrap ke baris baru */
        gap: 0.5em; /* Jarak antar tags */
        margin-top: 0.5em;
        padding: 0.8em; /* Padding di sekitar grup tags */
        background-color: rgba(255,255,255,0.7); /* Background soft untuk container tags */
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(160, 160, 200, 0.1);
        border: 1px solid #e0e7ff; /* Border lembut */
    }

    .skill-tag {
        background-color: #a1c4fd; /* Warna biru pastel untuk tag */
        color: #355; /* Warna teks tag */
        border-radius: 5px; /* Sudut sedikit membulat */
        padding: 0.4em 0.8em; /* Padding internal tag */
        font-size: 0.9em;
        font-weight: 500;
        white-space: nowrap; /* Mencegah teks skill pecah baris */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Sedikit shadow */
        transition: background-color 0.2s ease-in-out;
    }

    .skill-tag:hover {
        background-color: #8bb4fa; /* Warna sedikit lebih gelap saat hover */
        cursor: default; /* Kursor default */
    }
    /* --- AKHIR STYLING SKILL TAGS --- */

    /* Sidebar styling */
    .st-emotion-cache-10pw50 ul { /* Target sidebar navigation */
        background-color: rgba(255,255,255,0.9) !important; /* Light background untuk sidebar */
        border-radius: 10px; /* Opsional: sedikit border-radius */
    }
    .st-emotion-cache-10pw50 ul li a { /* Sidebar links */
        color: #333 !important; /* Dark text for sidebar links */
    }
    .st-emotion-cache-10pw50 ul li a:hover {
        background-color: #e0e7ff !important; /* Hover effect */
        color: #333 !important;
    }
    .st-emotion-cache-16txtl3 { /* Sidebar header/title */
        color: #6c63ff !important; /* Warna ungu seperti sebelumnya */
    }

    /* Button styling (biru solid yang konsisten) */
    .stButton > button {
        background-color: #1877f2 !important; /* Solid blue, mirip tombol "Selengkapnya" */
        color: #ffffff !important; /* White text */
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6em 1.5em !important; /* Sesuaikan padding horizontal */
        font-size: 1.1em !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.3) !important; /* Shadow lebih jelas */
        transition: 0.2s !important;
        white-space: normal !important; /* Izinkan teks melengkung ke baris baru */
        word-break: break-word !important; /* Pastikan kata panjang juga pecah */
        min-height: 3.5em !important; /* Atur tinggi minimum agar seragam */
        display: flex !important; /* Gunakan flexbox untuk alignment teks */
        align-items: center !important; /* Vertically center the text */
        justify-content: center !important; /* Horizontally center the text */
        text-align: center !important; /* Pastikan teks di tengah */
        width: 100% !important; /* Paksa tombol mengisi lebar kolom */
    }
    .stButton > button:hover {
        background-color: #1256b4 !important; /* Darker blue on hover */
        color: #ffffff !important;
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.4) !important;
    }

    /* Input fields styling (stTextInput, stTextArea, dll) */
    .stTextInput, .stTextArea {
        background: rgba(255,255,255,0.9) !important; /* Agak lebih solid putih */
        border-radius: 10px !important;
        border: 1px solid #c0d9ff !important; /* Border yang match dengan tema */
        box-shadow: 0 2px 8px 0 rgba(160, 160, 200, 0.08);
    }
    
    /* STYLING UNTUK ST.FILE_UPLOADER */
    .stFileUploader {
        border-radius: 10px !important;
        border: 1px solid #c0d9ff !important; /* Border senada dengan tema */
        box-shadow: 0 2px 8px 0 rgba(160, 160, 200, 0.08);
        background: rgba(255,255,255,0.9) !important; /* Background putih transparan */
        padding: 10px; /* Sedikit padding internal */
    }
    .stFileUploader > div:first-child > div {
        background-color: transparent !important;
        border: 2px dashed #a1c4fd !important;
        border-radius: 10px !important;
        padding: 20px !important;
        color: #666 !important;
    }
    .stFileUploader label p {
        color: #555 !important;
        font-weight: 500;
    }
    .stFileUploader > div:first-child > div > div > p {
        color: #777 !important;
    }
    .stFileUploader > div:first-child > div > div > small {
        color: #888 !important;
    }
    .stFileUploader button {
        background-color: #1877f2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5em 1.5em !important;
        font-size: 0.95em !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: 0.2s !important;
    }
    .stFileUploader button:hover {
        background-color: #1256b4 !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.3) !important;
    }
    /* AKHIR STYLING UNTUK ST.FILE_UPLOADER */


    /* Alert/Info/Success/Warning/Error boxes */
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
        background: linear-gradient(90deg, #e0e7ff 0%, #f8fafc 100%) !important; /* Light gradient untuk alerts */
        color: #333 !important; /* Dark text */
        border: 1px solid #c0d9ff !important; /* Light border */
    }

    /* Markdown headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #6c63ff !important; /* Warna ungu yang konsisten */
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    /* Regular Markdown text color */
    .stMarkdown {
        color: #333333 !important; /* Text gelap agar terbaca */
    }

    /* --- REKOMENDASI CARD STYLING BARU DENGAN PROGRESS BAR --- */
    .recommendation-card {
        /* Background lebih halus dan transparan dengan sedikit gradient */
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,248,255,0.95) 100%) !important;
        border-radius: 18px !important; /* Sedikit lebih membulat */
        padding: 1.8em !important; /* Padding lebih lega lagi */
        margin-bottom: 1.5em !important; /* Jarak antar card lebih santai */
        /* Shadow lebih menonjol, halus, dan sedikit menyebar */
        box-shadow: 0 8px 30px 0 rgba(100, 100, 150, 0.18) !important;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important; /* Animasi smooth */
        border-left: 8px solid #5B9FF9 !important; /* Garis warna di samping, tebal dan ungu konsisten */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .recommendation-card:hover {
        /* Shadow lebih tebal dan menyebar saat hover */
        box-shadow: 0 16px 50px 0 rgba(100, 100, 150, 0.35) !important;
        transform: translateY(-7px) !important; /* Efek melayang lebih tinggi saat hover */
        background: linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(240,240,255,1) 100%) !important; /* Lebih terang saat hover */
    }
    .recommendation-card b { /* Judul pekerjaan */
        color: #333 !important; /* Warna teks judul lebih gelap agar lebih terbaca */
        font-size: 1.3em !important; /* Ukuran font judul sedikit lebih besar */
        margin-bottom: 0.6em !important; /* Jarak antara judul dan skor */
    }
    .recommendation-card .score-label { /* Label "Skor Kemiripan" */
        color: #666 !important; /* Warna teks label sedikit lebih gelap */
        font-size: 1em !important; /* Ukuran font label sedikit lebih besar */
        margin-top: 0.8em !important;
        margin-bottom: 0.6em !important; /* Jarak ke progress bar */
    }

    /* --- CUSTOM PROGRESS BAR STYLING --- */
    .progress-container {
        width: 100%;
        /* Background bar progress yang lebih lembut dengan sedikit gradient */
        background: linear-gradient(90deg, #e8eaf6 0%, #f0f0f0 100%) !important;
        border-radius: 8px !important; /* Sudut lebih bulat, senada dengan card */
        overflow: hidden;
        height: 25px !important; /* Tinggi bar progress disesuaikan, lebih ramping */
        margin-top: 8px !important; /* Jarak dari label skor */
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.15) !important; /* Inner shadow lebih jelas */
    }

    .progress-bar {
        height: 100%;
        /* Gradient warna untuk progress (tetap hijau, tapi bisa disesuaikan) */
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 8px !important; /* Sudut bar sesuai container-nya */
        transition: width 0.5s ease-in-out;
        text-align: right;
        color: white;
        font-size: 0.8em !important; /* Ukuran font skor lebih kecil agar pas */
        line-height: 25px !important; /* Vertically center text sesuai tinggi bar */
        padding-right: 8px !important; /* Padding kanan lebih besar */
        font-weight: bold !important;
        box-sizing: border-box;
    }
    /* Warna progress bar jika skor rendah, sedang, tinggi (Gradient lebih konsisten) */
    .progress-bar.low {
        background: linear-gradient(90deg, #FFC107 0%, #FFD54F 100%) !important; /* Kuning-oranye yang lebih soft */
    }
    .progress-bar.medium {
        background: linear-gradient(90deg, #2196F3 0%, #64B5F6 100%) !important; /* Biru yang konsisten */
    }
    .progress-bar.high {
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%) !important; /* Hijau yang konsisten */
    }
    /* --- AKHIR CUSTOM PROGRESS BAR STYLING --- */

    
    /* Subheader (for "Top 5 Rekomendasi Pekerjaan") */
    .stSubheader {
        color: #43A047 !important; /* Warna hijau, bisa disesuaikan kalau mau konsisten ungu */
        font-weight: 600 !important;
    }

    /* Spinner color */
    .stSpinner > div > div {
        color: #6c63ff !important; /* Warna spinner mengikuti tema ungu */
    }

    /* Element spacing */
    .element-container {
        padding-top: 10px;
    }

    </style>
''', unsafe_allow_html=True)

# --- Load model semantic MiniLM ---
@st.cache_resource
def load_model():
    try:
        return SentenceTransformer('paraphrase-MiniLM-L6-v2')
    except Exception as e:
        st.error(f"Gagal memuat model SentenceTransformer: {e}. Pastikan Anda memiliki koneksi internet atau model sudah diunduh.")
        return None

model = load_model()

# --- Load job data from CSV ---
def load_job_data(job_csv_path):
    job_data = {}
    if os.path.exists(job_csv_path):
        with open(job_csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                position = row.get("position_title")
                required_skills_str = row.get("required_skills", "[]")
                try:
                    skills = ast.literal_eval(required_skills_str)
                    if isinstance(skills, list):
                        skills = [s.strip().lower() for s in skills if s and s.strip()]
                    else:
                        skills = []
                except Exception:
                    skills = []
                if position:
                    job_data[position] = {"required_skills": skills}
    else:
        st.error(f"File job requirement tidak ditemukan di: {job_csv_path}")
    return job_data

job_csv_path = os.path.join(os.path.dirname(__file__), "jobRequirement.csv")
job_data = load_job_data(job_csv_path)

# --- Extract text from PDF/DOCX ---
def extract_text(file_path):
    import pdfplumber
    from docx import Document
    ext = os.path.splitext(file_path)[-1].lower()
    text = ""
    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif ext == ".docx":
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            st.warning(f"Format file tidak didukung: {ext}. Hanya PDF dan DOCX yang didukung.")
            return ""
        return text if text else ""
    except Exception as e:
        st.error(f"Gagal mengekstrak teks dari file {os.path.basename(file_path)}: {e}")
        return ""

# --- Gemini API Key (replace with your key or use env var) ---
API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBtNixliDZyFJS_xmp1i1jp5AfCQyHVozs')
if API_KEY == 'YOUR_GEMINI_API_KEY':
    st.warning("GOOGLE_API_KEY environment variable not set. Please set it for Gemini extraction.")
else:
    genai.configure(api_key=API_KEY)

# --- Gemini NER extraction (from CVExtraction.ipynb) ---
def extract_ner_from_cv(text, prompt_template):
    if not text or len(text.strip()) < 50:
        return {"error": "Teks CV terlalu pendek atau tidak valid untuk diproses."}
    if "{text}" not in prompt_template:
        st.warning("Prompt template tidak mengandung placeholder '{text}'. Teks CV tidak akan disertakan!")
    final_prompt = prompt_template.format(text=text)
    try:
        

        model_gemini = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model_gemini.generate_content(final_prompt)
        response_text = response.text.strip()
        
        json_block = None
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            if json_end != -1:
                json_block = response_text[json_start:json_end].strip()
        
        if json_block is None and "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            if json_end != -1:
                json_block = response_text[json_start:json_end].strip()
        
        if json_block is None:
            json_block = response_text
        
        json_block = json_block.replace('kurwal(', '{').replace(')', '}')
        
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        return {"error": f"Struktur JSON dari model tidak valid: {e}", "raw_response": response_text}
    except Exception as e:
        return {"error": f"Terjadi kesalahan API Gemini: {e}", "raw_response": response.text if 'response' in locals() else "Tidak ada objek respons"}

# --- Prompt for Gemini extraction ---
cv_extraction_prompt = '''
Ekstrak semua informasi penting dari CV di bawah ini dan ubah ke dalam format JSON standar berikut. Hasilkan hanya JSON valid yang dimulai dengan json dan diakhiri dengan . Jangan tambahkan teks lain di luar blok JSON.

Jika ada bagian yang tidak tersedia, cukup gunakan string kosong atau array kosong.

Format standar:
dari sini kurung kurawal akan ditandai dengan 'kurwal()'
json
  kurwal(
    "name": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "location": "",
    "education": [
      kurwal(
        "institution": "",
        "degree": "",
        "major": "",
        "start_date": "",
        "end_date": "",
        "gpa": ""
      )
    ],
    "experience": [
      kurwal(
        "organization": "",
        "role": "",
        "start_date": "",
        "end_date": "",
        "description": ""
      )
    ],
    "awards": [
      kurwal(
        "name": "",
        "start_date": "",
        "end_date": "",
        "description": ""
      )
    ],
    "certifications": [
      kurwal(
        "name": "",
        "start_date": "",
        "end_date": "",
        "modules": [""]
      )
    ],
    "skills": kurwal(
      "languages": [""],
      "software": [""],
      "other": [""]
    )
  )
Ini CV-nya: {text}

---

Instruksi:

 Jika ada bagian yang kosong (misalnya, awards atau certifications tidak ada), cukup hilangkan bagian tersebut dari JSON yang dihasilkan.

Jika ada informasi yang tidak lengkap (misalnya, ada bagian education yang tidak memiliki gpa), tetap masukkan bagian tersebut dengan nilai kosong untuk yang hilang.

Untuk pendidikan (misal "Bachelor of Science" vs "Sarjana Sains")

Untuk skills (misal "Python" vs "python programming" vs "Programming in Python")

Untuk roles/experience yang beda cara nulis tapi sama arti ("Software Engineer" vs "Engineer, Software Development")

Translate semua ke bahasa inggris ya
'''

# --- Semantic similarity ---
def calculate_semantic_similarity(skill_list1, skill_list2):
    if not skill_list1 or not skill_list2 or model is None:
        return 0.0
    text1 = ', '.join(skill_list1)
    text2 = ', '.join(skill_list2)
    try:
        emb1 = model.encode(text1, convert_to_tensor=True)
        emb2 = model.encode(text2, convert_to_tensor=True)
        score = util.pytorch_cos_sim(emb1, emb2).item()
        return score
    except Exception as e:
        st.warning(f"Gagal menghitung similaritas semantik: {e}. Mengembalikan skor 0.0.")
        return 0.0

# --- Neo4j Functions ---
def get_neo4j_driver(uri, username, password):
    try:
        return GraphDatabase.driver(uri, auth=(username, password))
    except Exception as e:
        st.error(f"Gagal terhubung ke Neo4j: {e}. Pastikan Neo4j berjalan dan kredensial benar.")
        return None

def insert_cv_to_neo4j(cv_data, uri, username, password):
    driver = get_neo4j_driver(uri, username, password)
    if not driver:
        return

    def insert_cv(tx, data):
        email = data.get("email")
        if not email:
            st.warning("Email tidak ditemukan di data CV, tidak dapat memasukkan ke Neo4j.")
            return

        tx.run("MATCH (p:Person {email: $email}) DETACH DELETE p", email=email)

        tx.run("""
            MERGE (p:Person {email: $email})
            SET p.name = $name,
                p.phone = $phone,
                p.linkedin = $linkedin,
                p.location = $location
        """, email=email,
               name=data.get("name", ""),
               phone=data.get("phone", ""),
               linkedin=data.get("linkedin", ""),
               location=data.get("location", ""))

        for edu in data.get("education", []):
            if any(edu.values()):
                tx.run("""
                    MERGE (e:Education {
                        institution: $institution,
                        degree: $degree,
                        major: $major
                    })
                    SET e.start_date = $start_date,
                        e.end_date = $end_date,
                        e.gpa = $gpa
                    MERGE (p:Person {email: $email})
                    MERGE (p)-[:HAS_EDUCATION]->(e)
                """, institution=edu.get("institution", ""), degree=edu.get("degree", ""),
                       major=edu.get("major", ""), start_date=edu.get("start_date", ""),
                       end_date=edu.get("end_date", ""), gpa=edu.get("gpa", ""), email=email)

        for exp in data.get("experience", []):
            if any(exp.values()):
                tx.run("""
                    MERGE (x:Experience {
                        organization: $organization,
                        role: $role,
                        start_date: $start_date,
                        end_date: $end_date
                    })
                    SET x.description = $description
                    MERGE (p:Person {email: $email})
                    MERGE (p)-[:HAS_EXPERIENCE]->(x)
                """, organization=exp.get("organization", ""), role=exp.get("role", ""),
                       start_date=exp.get("start_date", ""), end_date=exp.get("end_date", ""),
                       description=exp.get("description", ""), email=email)
        
        for award in data.get("awards", []):
            if any(award.values()):
                tx.run("""
                    MERGE (a:Award {name: $name})
                    SET a.start_date = $start_date, a.end_date = $end_date, a.description = $description
                    MERGE (p:Person {email: $email})
                    MERGE (p)-[:RECEIVED_AWARD]->(a)
                """, name=award.get("name", ""), start_date=award.get("start_date", ""),
                       end_date=award.get("end_date", ""), description=award.get("description", ""), email=email)

        for cert in data.get("certifications", []):
            if any(cert.values()):
                tx.run("""
                    MERGE (c:Certification {name: $name})
                    SET c.start_date = $start_date, c.end_date = $end_date
                    MERGE (p:Person {email: $email})
                    MERGE (p)-[:HAS_CERTIFICATION]->(c)
                """, name=cert.get("name", ""), start_date=cert.get("start_date", ""),
                       end_date=cert.get("end_date", ""), email=email)

        skills_data = data.get("skills", {})
        for category, skills_list in skills_data.items():
            if isinstance(skills_list, list):
                for skill in skills_list:
                    skill_name = skill.strip()
                    if skill_name:
                        tx.run("""
                            MERGE (s:Skill {name: $skill_name})
                            MERGE (p:Person {email: $email})
                            MERGE (p)-[:HAS_SKILL {category: $category}]->(s)
                        """, skill_name=skill_name, email=email, category=category)

    with driver.session() as session:
        session.write_transaction(insert_cv, cv_data)
    driver.close()

def insert_jobs_to_neo4j(job_csv_path, uri, username, password):
    driver = get_neo4j_driver(uri, username, password)
    if not driver:
        return
    
    try:
        data = pd.read_csv(job_csv_path, sep=';')
        data['required_skills'] = data['required_skills'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

        def insert_data(tx, position, skills):
            tx.run("""
                MERGE (p:Position {name: $position})
                WITH p
                UNWIND $skills AS skill_name
                    MERGE (s:Skill {name: skill_name})
                    MERGE (p)-[:REQUIRES]->(s)
            """, position=position, skills=skills)

        with driver.session() as session:
            for _, row in data.iterrows():
                position = row['position_title']
                skills = row['required_skills']
                if position and skills:
                    session.write_transaction(insert_data, position, skills)
    except Exception as e:
        st.error(f"Gagal memasukkan data pekerjaan ke Neo4j: {e}")
    finally:
        driver.close()

def delete_cv_from_neo4j(email, uri, username, password):
    driver = get_neo4j_driver(uri, username, password)
    if not driver:
        return
    def delete_person(tx, email):
        tx.run("""
            MATCH (p:Person {email: $email})
            DETACH DELETE p
        """, email=email)
    try:
        with driver.session() as session:
            session.write_transaction(delete_person, email)
    except Exception as e:
        st.warning(f"Gagal menghapus data CV dari Neo4j: {e}")
    finally:
        driver.close()

def visualize_cv_and_jobs(email, top_jobs, uri, username, password):
    driver = get_neo4j_driver(uri, username, password)
    if not driver:
        return None

    # Background grafik tetap light grey untuk kanvas bersih
    net = Network(height="650px", width="100%", notebook=False, directed=True, bgcolor="#f9f9f9") 
    
    options_dict = {
        "nodes": {
            "borderWidth": 2, #/* Default border width */
            "borderWidthSelected": 6, #/* Border lebih tebal saat dipilih */
            "shadow": {
                "enabled": True,
                "color": "rgba(0,0,0,0.2)", #/* Shadow nodes lebih halus dan jelas */
                "size": 15,
                "x": 5,
                "y": 5
            },
            "font": {"size": 16, "color": "#333", "face": "Segoe UI, sans-serif", "strokeWidth": 0, "align": "center"}, #/* Font lebih bersih dan terpusat */
            "shape": "dot", #/* Bentuk default dot, akan di-override */
            "scaling": { #/* Scaling node berdasarkan koneksi */
                "min": 20,
                "max": 50,
                "label": {
                    "enabled": True,
                    "min": 12,
                    "max": 20,
                    "maxVisible": 30,
                    "drawThreshold": 5
                }
            },
            "physics": {
                "enabled": False
            }
        },
        "edges": {
            "shadow": {
                "enabled": True,
                "color": "rgba(0,0,0,0.1)", #/* Shadow edges lebih halus */
                "size": 8,
                "x": 2,
                "y": 2
            },
            "smooth": {
                "type": "dynamic",#/* Smoothness edges dinamis dan natural */
                "forceDirection": "none",
                "roundness": 0.6 #/* Lebih melengkung */
            },
            "font": {"size": 12, "color": "#777", "face": "Segoe UI, sans-serif", "align": "middle", "strokeWidth": 0}, #/* Font edges lebih bersih */
            "color": {"inherit": "from"}, #/* Warna edge diwarisi dari node, lalu di-override */
            "width": 2 #/* Lebar edge default */
        },
        "physics": {
            "enabled": False #/* Pastikan physics mati untuk layout yang stabil */
        },
        "interaction": {
            "hover": True,
            "hoverConnectedEdges": False,
            "selectConnectedEdges": False,
            "zoomView": True,
            "navigationButtons": True #/* Tambahkan tombol navigasi zoom/pan */
        },
        "layout": {
            "improvedLayout": True, #/* Optimasi layout */
            "randomSeed": 42 #/* Biar layoutnya konsisten setiap kali di-load */
        }
    }
    net.set_options(json.dumps(options_dict))

    with driver.session() as session:
        person_result = session.run("""
            MATCH (p:Person {email: $email})
            OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
            RETURN p, collect(s.name) as skills
        """, email=email)
        person_record = person_result.single()

        if not person_record:
            driver.close()
            st.warning("Data CV tidak ditemukan di Neo4j untuk visualisasi.")
            return None
        
        person_node = person_record["p"]
        person_skills = person_record["skills"]
        
        # Node CV (Person) - Warna ungu utama, bentuk berbeda
        net.add_node(person_node["email"], label=person_node.get("name", person_node["email"]), 
                     color={"background": "#6c63ff", "border": "#4A43DB", "highlight": "#9C27B0"}, # Ungu kuat
                     shape="diamond", # Bentuk diamond (permata)
                     size=40, borderWidth=4, # Ukuran lebih besar
                     font={"color": "white", "size": 18, "face": "Segoe UI, sans-serif", "strokeWidth": 1.2, "strokeColor": "rgba(0,0,0,1)"}) # Font putih
        
        cv_skill_set = set()
        for skill in person_skills:
            if skill:
                cv_skill_set.add(skill.lower())
                # Skill CV - Warna biru pastel, bentuk elips
                net.add_node(f"skill_cv_{skill.lower()}", label=skill, 
                             color={"background": "#A6C1EE", "border": "#819ED9", "highlight": "#76A2E8"}, # Biru soft
                             shape="ellipse", # Bentuk elips
                             size=30, borderWidth=2,
                             font={"color": "#333", "size": 14, "face": "Segoe UI, sans-serif"})
                # Edge HAS_SKILL - Warna abu-abu kebiruan lembut
                net.add_edge(person_node["email"], f"skill_cv_{skill.lower()}", 
                             label="HAS_SKILL", color={"color": "#B0C4DE", "highlight": "#9FB5D6"}, width=1.5,
                             font={"color": "#666", "size": 10})
        
        for job in top_jobs:
            job_title = job["position_title"]
            job_node_id = f"job_{job_title}"
            # Node Posisi Pekerjaan - Warna hijau cerah, bentuk kotak
            net.add_node(job_node_id, label=job_title, 
                         color={"background": "#7ED957", "border": "#5CB837", "highlight": "#90EE90"}, # Hijau modern
                         shape="box", # Bentuk kotak
                         size=35, borderWidth=3,
                         font={"color": "white", "size": 16, "face": "Segoe UI, sans-serif"})
            
            job_result = session.run("""
                MATCH (p:Position {name: $job_title})-[:REQUIRES]->(s:Skill)
                RETURN collect(s.name) as req_skills
            """, job_title=job_title)
            
            job_result_record = job_result.single()
            job_skills = job_result_record["req_skills"] if job_result_record and "req_skills" in job_result_record else []

            for skill in job_skills:
                if skill:
                    skill_lower = skill.lower()
                    if skill_lower in cv_skill_set:
                        # Edge REQUIRES (skill di CV) - Warna abu-abu kebiruan lembut
                        net.add_edge(job_node_id, f"skill_cv_{skill_lower}", 
                                     label="REQUIRES", color={"color": "#B0C4DE", "highlight": "#9FB5D6"}, width=1.5,
                                     font={"color": "#666", "size": 10})
                    else:
                        # Skill Pekerjaan (tidak di CV) - Warna oranye hangat, bentuk kotak bulat
                        net.add_node(f"jobskill_{job_title}_{skill_lower}", label=skill, 
                                     color={"background": "#FFBF69", "border": "#E89D3C", "highlight": "#FFD700"}, # Oranye hangat
                                     shape="box", physics=False, # Bentuk kotak, matikan physics untuk node ini
                                     size=28, borderWidth=2,
                                     font={"color": "#444", "size": 12, "face": "Segoe UI, sans-serif"})
                        # Edge REQUIRES (skill tidak di CV) - Warna abu-abu kebiruan lembut
                        net.add_edge(job_node_id, f"jobskill_{job_title}_{skill_lower}", 
                                     label="REQUIRES", color={"color": "#B0C4DE", "highlight": "#9FB5D6"}, width=1.5,
                                     font={"color": "#666", "size": 10})
            
            # Edge Kedekatan (Similarity) - Warna merah cerah untuk kekuatan match
            net.add_edge(person_node["email"], job_node_id, 
                         color={"color": "#FF6B6B", "highlight": "#FF8E8E"}, # Merah cerah
                         width=4, label=f"{job['similarity_score']:.2f}", arrows="to", # Lebar lebih tebal
                         font={"color": "#FF6B6B", "size": 16, "face": "Segoe UI, sans-serif", "bold": True}) # Font lebih besar dan bold
    driver.close()
    return net.generate_html()

# --- Neo4j config ---
NEO4J_URI = "neo4j+s://c35fc5da.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASS = "DtFW_eYmECQqYGwf7SLFqC7CwKiA2kbIgtw3EACGKdo"

# --- Auto insert jobRequirement.csv to Neo4j ONCE per session ---
if "jobs_inserted" not in st.session_state:
    try:
        driver_check = get_neo4j_driver(NEO4J_URI, NEO4J_USER, NEO4J_PASS)
        if driver_check:
            with driver_check.session() as session_check:
                result = session_check.run("MATCH (p:Position) RETURN count(p) as count").single()
                if result and result["count"] > 0:
                    st.session_state.jobs_inserted = True
                else:
                    insert_jobs_to_neo4j(job_csv_path, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
                    st.session_state.jobs_inserted = True
            driver_check.close()
    except Exception as e:
        st.warning(f"Gagal auto-masukkan atau cek data pekerjaan di Neo4j: {e}")

# Inisialisasi session state untuk halaman ini
if "step" not in st.session_state:
    st.session_state.step = 1
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None
if "cv_skills" not in st.session_state:
    st.session_state.cv_skills = None
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = None
if "extracted_cv_email" not in st.session_state:
    st.session_state.extracted_cv_email = None

def reset_session_state():
    if st.session_state.get("uploaded_file_path") and os.path.exists(st.session_state.uploaded_file_path):
        try:
            os.remove(st.session_state.uploaded_file_path)
        except Exception as e:
            st.warning(f"Gagal menghapus file CV sementara: {e}")
    if st.session_state.get("temp_dir") and os.path.exists(st.session_state.temp_dir):
        try:
            shutil.rmtree(st.session_state.temp_dir)
        except Exception as e:
            st.warning(f"Failed to delete temporary directory: {e}")
    
    if st.session_state.get("extracted_cv_email"):
        try:
            delete_cv_from_neo4j(st.session_state.extracted_cv_email, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
            st.success(f"CV data ({st.session_state.extracted_cv_email}) has been successfully deleted from Neo4j.")
        except Exception as e:
            st.warning(f"Failed to delete old CV data from Neo4j: {e}")

    st.session_state.step = 1
    st.session_state.recommendations = None
    st.session_state.uploaded_file_path = None
    st.session_state.cv_skills = None
    st.session_state.temp_dir = None
    st.session_state.extracted_cv_email = None

# --- Main app logic for this page ---
def app():
    st.title("CV Job Recommendation System") 
    st.markdown("Upload your ATS-friendly CV (PDF or DOCX) to receive personalized job recommendations!")

    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        col_img, col_uploader = st.columns([1, 2])

        with col_img:
            # --- PERBAIKAN DI SINI: Menggunakan st.image() dan kolom mini untuk centering ---
            st.markdown("<div style='height: 3em;'></div>", unsafe_allow_html=True) # Jarak dari atas

            # Buat 3 kolom mini di dalam col_img untuk menengahkan gambar 150px
            spacer_left_img, center_img_col, spacer_right_img = st.columns([1, 2, 1]) 
            # Rasio [1,2,1] ini kira-kira akan membuat kolom tengah 2/4 (50%) dari col_img.
            # Kalau gambar 150px di 50% lebar kolom, harusnya cukup center. Sesuaikan rasio kalau perlu.

            with center_img_col:
                st.image("images/upload_9628231.png", # PATH GAMBAR LO YANG BENA
                         width=450) # Ukuran gambar, sesuaikan

            st.markdown(
                """
                <div style='text-align: center; color: #555; margin-top: 1em;'>
                    💡 <b>Tip:</b> <b>Please upload an <span style="color:#1877f2;">ATS-friendly CV</span> (no complex tables, columns, or graphics) for optimal extraction and accurate recommendations.</b>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_uploader:
            st.subheader("Upload Your CV")
            uploaded_file = st.file_uploader("Choose your CV file (PDF or DOCX)", type=["pdf", "docx"], key="cv_uploader")
            
            # --- TAMBAHAN INI: Placeholder untuk Status Indikator ---
            status_placeholder = st.empty() # Placeholder untuk pesan status
            progress_bar_placeholder = st.empty() # Placeholder untuk progress bar
            # --- AKHIR TAMBAHAN ---

            if uploaded_file is not None:
                # Ini logika untuk menyimpan file sementara
                # Pastikan direktori temp selalu bersih
                if st.session_state.get("temp_dir") and os.path.exists(st.session_state.temp_dir):
                    shutil.rmtree(st.session_state.temp_dir)
                temp_dir = tempfile.mkdtemp()
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.uploaded_file_path = temp_file_path
                st.session_state.temp_dir = temp_dir
                status_placeholder.info(f"File '{uploaded_file.name}' uploaded successfully. Ready for extraction!") # Update status
                

                st.markdown("<div style='height: 1em'></div>", unsafe_allow_html=True)
                if st.button("CV Extraction", use_container_width=True):
                    if not os.path.exists(temp_file_path):
                        status_placeholder.error("CV file not found or failed to save temporarily.")
                    else:
                        # --- Perubahan di sini: Update Status dan Progress Bar ---
                        progress_status = progress_bar_placeholder.progress(0)
                        
                        status_placeholder.info("Extracting text from CV... (1/3)")
                        progress_status.progress(25)
                        text = extract_text(temp_file_path)
                        
                        if not text:
                            status_placeholder.error("Failed to extract text from the CV file. Make sure the file is not empty or corrupted.")
                            progress_status.empty() # Kosongkan progress bar jika ada error
                        else:
                            status_placeholder.info("Extracting information with Gemini... (2/3)")
                            progress_status.progress(50)
                            ner_result = extract_ner_from_cv(text, cv_extraction_prompt)
                            
                            if "error" in ner_result:
                                status_placeholder.error(f"CV information extraction failed: {ner_result.get('error')}")
                                if "raw_response" in ner_result:
                                    status_placeholder.warning("Please try again or check your CV format.")
                                progress_status.empty() # Kosongkan progress bar jika ada error
                            else:
                                status_placeholder.info("Inserting data into Neo4j database... (3/3)")
                                progress_status.progress(75)
                                extracted_email = ner_result.get("email")
                                if not extracted_email:
                                    status_placeholder.warning("Email not detected from CV. Visualization in Neo4j may not be optimal or unable to store unique data.")
                                    # Continue the process, treat this as a non-fatal error
                                    try:
                                        insert_cv_to_neo4j(ner_result, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
                                        status_placeholder.success("CV extraction & data storage successful!")
                                    except Exception as e:
                                        status_placeholder.error(f"Failed to insert CV data into Neo4j: {e}")
                                else:
                                    st.session_state.extracted_cv_email = extracted_email
                                    try:
                                        delete_cv_from_neo4j(extracted_email, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
                                        insert_cv_to_neo4j(ner_result, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
                                        status_placeholder.success("CV extraction & data successfully inserted/updated into Neo4j!")
                                    except Exception as e:
                                        status_placeholder.error(f"Failed to insert CV data into Neo4j: {e}")

                                st.session_state.cv_skills = []
                                skills_dict = ner_result.get("skills", {})
                                for category, skills_list in skills_dict.items():
                                    if isinstance(skills_list, list):
                                        st.session_state.cv_skills.extend([s.strip().lower() for s in skills_list if s and s.strip()])
                                
                                if not st.session_state.cv_skills:
                                    status_placeholder.warning("No skills were detected from your CV. Job recommendations may not be accurate.")

                                progress_status.progress(100) # Selesai
                                # Kosongkan status dan progress bar setelah selesai
                                status_placeholder.empty()
                                progress_bar_placeholder.empty()

                                st.session_state.step = 2
                                st.rerun()
                        # --- Akhir Perubahan Status dan Progress Bar ---
            else:
                # Pesan default ketika belum ada file diupload
                status_placeholder.info("Please upload your CV file to start the extraction process.")
                progress_bar_placeholder.empty() # Pastikan progress bar kosong


    elif st.session_state.step == 2:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.subheader("Detected Skills & Recommendation")
            st.markdown("Here are the **main skills detected** from your CV:")
            if st.session_state.cv_skills:
                # Buat string HTML untuk semua skill tags
                skills_html = ""
                for skill in st.session_state.cv_skills:
                    skills_html += f"<span class='skill-tag'>{skill.title()}</span>" # .title() biar huruf depannya kapital

                st.markdown(f"<div class='skills-container'>{skills_html}</div>", unsafe_allow_html=True)
            else:
                st.warning("No skills detected from the CV. Recommendations may not appear.")
            # --- AKHIR PERUBAHAN ---
            
            st.markdown("<div style='height: 1em'></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 1em'></div>", unsafe_allow_html=True)
            
            colA, colB = st.columns(2)
            with colA:
                # Tombol ini tidak pakai use_container_width=True agar CSS width: 100% di .stButton > button bekerja
                if st.button("Get Job Recommendations"):
                    if not st.session_state.cv_skills:
                        st.warning("No skills detected from your CV, unable to provide recommendations.")
                    elif not job_data:
                        st.error("Job data not loaded. Please try reloading the application.")
                    elif model is None:
                        st.error("Semantic similarity model failed to load. Recommendations cannot be processed.")
                    else:
                        user_skills = st.session_state.cv_skills
                        recommendations = []
                        with st.spinner("Searching for job recommendations..."):
                            for job_title, job_info in job_data.items():
                                req_skills = job_info.get("required_skills", [])
                                sim_score = calculate_semantic_similarity(user_skills, req_skills)
                                if sim_score >= 0.5:
                                    recommendations.append({
                                        "position_title": job_title,
                                        "similarity_score": sim_score
                                    })
                            recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
                            st.session_state.recommendations = recommendations[:5]
                        
                        st.success("Job recommendations calculated successfully.")
                        st.session_state.step = 3
                        st.rerun()
            with colB:
                # Tombol ini juga tidak pakai use_container_width=True
                if st.button("Analyze Another CV"):
                    reset_session_state()
                    st.rerun()

    elif st.session_state.step == 3:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.subheader("Top 5 Job Recommendations for You")
            if st.session_state.recommendations:
                if not st.session_state.recommendations:
                    st.info("No suitable job recommendations found based on your CV (similarity score below 0.5).")
                else:
                    for i, rec in enumerate(st.session_state.recommendations, 1):
                        # --- Perubahan di sini: Menggunakan HTML kustom untuk card dan progress bar ---
                        score_percentage = int(rec['similarity_score'] * 100) # Konversi ke persen
                        # Tentukan kelas warna berdasarkan skor
                        progress_color_class = ""
                        if score_percentage < 60:
                            progress_color_class = "low"
                        elif score_percentage < 80:
                            progress_color_class = "medium"
                        else:
                            progress_color_class = "high"

                        st.markdown(f"""
                            <div class='recommendation-card'>
                                <b>{i}. {rec['position_title']}</b>
                                <div class='progress-container'>
                                    <div class='progress-bar {progress_color_class}' style='width: {score_percentage}%;'>
                                        {score_percentage}%
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        # --- Akhir perubahan ---
                    
                    st.markdown("---")
                    st.subheader("Visualization of CV & Job Relationships")

                    if st.session_state.extracted_cv_email:
                        with st.spinner("Generating graph visualization..."):
                            try:
                                html_graph = visualize_cv_and_jobs(st.session_state.extracted_cv_email, st.session_state.recommendations, NEO4J_URI, NEO4J_USER, NEO4J_PASS)
                                if html_graph:
                                    components.html(html_graph, height=325, width=1200, scrolling=True)
                                else:
                                    st.warning("Failed to generate graph visualization. Check logs or Neo4j connection.")
                            except Exception as e:
                                st.error(f"An error occurred while displaying the graph visualization: {e}")
                    else:
                        st.warning("CV email not detected, graph visualization cannot be created.")
            else:
                st.info("No suitable recommendations found.")
            
            st.markdown("<div style='height: 1em'></div>", unsafe_allow_html=True)
            if st.button("Analyze Another CV", use_container_width=True):  # This button returns to step 1
                reset_session_state()
                st.rerun()

# Panggil fungsi app() agar kode di halaman ini dieksekusi saat diakses
if __name__ == '__main__':
    app()