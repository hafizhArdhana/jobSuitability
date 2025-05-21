import streamlit as st

st.set_page_config(
    page_title="CV-Based Job Recommendation System",  # Page title in English
    layout="centered",  # Keep centered layout for the homepage
    initial_sidebar_state="collapsed"  # Sidebar stays collapsed by default
)

# --- Custom Pastel Gradient CSS (diperbarui untuk background biru muda) ---
st.markdown('''
    <style>
    /* Global light mode background dengan gradient biru muda */
    body, .stApp {
        background: linear-gradient(135deg, #f2f6f9 0%, #d4eaf7 100%) !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    /* Ini .stApp yang kedua, buat memastikan kalau ada overrides, tetap pakai gradient ini */
    .stApp {
        background: linear-gradient(120deg, #f2f6f9 0%, #d4eaf7 100%) !important;
    }
    
    /* Header (Streamlit's default header) */
    header, .css-18e3th9, .css-1d391kg, .css-1v0mbdj, .css-1dp5vir {
        background: transparent !important; /* Biar transparan, ikut background body */
    }

    /* Main content block styling */
    .block-container {
        padding-top: 3rem; /* Padding atas lebih besar */
        padding-bottom: 3rem; /* Padding bawah lebih besar */
        border-radius: 20px; /* Lebih membulat */
        box-shadow: 0 8px 40px 0 rgba(160, 160, 200, 0.18); /* Shadow lebih menonjol */
        background: rgba(255,255,255,0.9) !important; /* Background lebih solid putih */
        padding-left: 3.5rem; /* Padding samping lebih lega */
        padding-right: 3.5rem; /* Padding samping lebih lega */
        border: none !important;
    }

    /* Sidebar styling (diselaraskan agar lebih bersih dan terang) */
    .st-emotion-cache-10pw50 ul { /* Target navigasi sidebar */
        background-color: rgba(255,255,255,0.95) !important; /* Lebih terang dan solid */
        border-radius: 10px; /* Opsional: sedikit border-radius */
    }
    .st-emotion-cache-10pw50 ul li a { /* Link sidebar */
        color: #333 !important; /* Warna teks gelap untuk link sidebar */
    }
    .st-emotion-cache-10pw50 ul li a:hover {
        background-color: #e0e7ff !important; /* Efek hover */
        color: #333 !important;
    }
    .st-emotion-cache-16txtl3 { /* Header/judul sidebar */
        color: #6c63ff !important; /* Tetap warna ungu seperti sebelumnya */
    }

    /* Warna teks dan header */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #4A4A4A !important; /* Warna judul lebih gelap untuk kontras */
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    /* Styling khusus untuk st.title */
    .stMarkdown h1:first-child {
        color: #6c63ff !important; /* Warna ungu untuk judul utama */
        font-size: 2.8em !important; /* Ukuran font judul lebih besar */
        text-align: center; /* Pusatkan judul */
        margin-bottom: 0.5em;
    }
    /* Styling khusus untuk st.subheader atau headline baru */
    .stMarkdown h2:first-of-type {
        color: #555 !important;
        font-size: 1.6em !important;
        text-align: center; /* Pusatkan tagline */
        margin-bottom: 1.5em;
        font-weight: 500;
    }
    .stMarkdown { /* Warna teks biasa */
        color: #333333 !important;
        line-height: 1.6; /* Jarak baris lebih nyaman dibaca */
    }

    /* Styling tombol (biru solid yang konsisten) */
    .stButton > button {
        background-color: #1877f2 !important; /* Biru solid */
        color: #ffffff !important; /* Teks putih */
        border: none !important;
        border-radius: 8px !important;
        padding: 0.8em 2.5em !important; /* Padding tombol lebih besar */
        font-size: 1.2em !important; /* Ukuran font tombol lebih besar */
        font-weight: 600 !important; /* Font tombol lebih tebal */
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.35) !important; /* Shadow lebih dalam */
        transition: 0.2s !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background-color: #1256b4 !important; /* Biru lebih gelap saat hover */
        color: #ffffff !important;
        box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.5) !important; /* Shadow lebih dalam saat hover */
    }

    /* Kotak Info/Warning/Success */
    .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
        background: linear-gradient(90deg, #e0e7ff 0%, #f8fafc 100%) !important; /* Gradient ringan untuk alert */
        color: #333 !important; /* Teks gelap */
        border: 1px solid #c0d9ff !important; /* Border ringan */
    }
    </style>
''', unsafe_allow_html=True)

# --- Konten Halaman Home (Diperbarui) ---
st.title("CV-Based Job Recommendation System")  # Main page title
st.subheader("Find Your Dream Career Faster.")  # Customized tagline

st.write(
    """
    This revolutionary system is designed to simplify your career journey.
    We thoroughly analyze your CV to match you with the most relevant job positions
    that fit your skills and experience.
    """
)

# --- Ilustrasi Besar ---
# Pastikan Anda memiliki gambar ini di folder 'images/' Anda
# Contoh: images/ai_job_search.png atau images/career_path.png
# Ganti URL/path gambar ini dengan ilustrasi Anda sendiri
st.image("https://img.freepik.com/premium-vector/3d-resume-concept-cv-curriculum-vitae-headhunting-recruting-rating-employees-worker-icon-website-cartoon-isometric-vector-illustration-isolated-blue-background_1002658-1592.jpg") # Menggunakan lebar kolom penuh

st.markdown("---")

st.header("Bagaimana Sistem Ini Bekerja?") # Judul bagian cara kerja
st.markdown("""
1.  **Upload Your CV:** Simply upload your ATS-friendly CV in PDF or DOCX format.
2.  **Automatic Extraction:** The system will automatically extract key details such as your name, email, education, experience, and **skills**.
3.  **Smart Recommendations:** Based on the detected skills, we will recommend a list of jobs that best match you, complete with similarity scores.
4.  **Interactive Visualization:** See how your skills connect to job requirements through intuitive *graph* visualizations.
""")

st.markdown("---")

# --- Tombol Ajakan Bertindak (Call to Action) ---
# Tombol ini akan membuat tombol dan mengarahkan ke halaman aplikasi utama
# if st.button("Mulai Temukan Pekerjaan Impian Anda!", use_container_width=True): # Teks tombol
#     # Dalam aplikasi Streamlit multi-halaman, navigasi biasanya dilakukan dengan mengklik tautan di sidebar.
#     # Namun, untuk tombol eksplisit, Anda bisa menggunakan instruksi ini.
st.markdown("[Click here to enter the main application!](/CV_Recommendation)", unsafe_allow_html=True) 

st.info("Or, you can simply click the 'CV Recommendation' link in the left sidebar.")  # Info message