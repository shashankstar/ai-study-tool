import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)

# --- 2. Security & API Key Management ---
# It looks for GEMINI_API_KEY in your Streamlit Cloud Settings / Secrets first.
api_key = st.secrets.get("GEMINI_API_KEY")

# Sidebar backup: if the secret isn't set, allow manual entry.
with st.sidebar:
    st.title("🔐 Configuration")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.caption("Get a key at [aistudio.google.com](https://aistudio.google.com/)")
    else:
        st.success("API Key loaded from Secrets ✅")
    
    st.divider()
    st.info("Upload a PDF or Image to generate study materials.")

# Stop the app if no API key is available
if not api_key:
    st.warning("Please provide an API Key to continue.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. File Upload Logic ---
st.title("📚 AI Educator: PDF & Image to Study Material")

uploaded_file = st.file_uploader("Upload a Textbook PDF or a Page Photo", type=['pdf', 'jpg', 'png', 'jpeg'])

if uploaded_file:
    with st.spinner("Processing your content..."):
        # Handle PDF Text Extraction
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            input_data = [f"Source Material:\n\n{text_content}"]
            st.success("PDF text successfully extracted!")
        
        # Handle Image (Vision)
        else:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", width=400)
            input_data = ["Analyze this educational material and use it for the following tasks:", img]
            st.success("Image uploaded and analyzed!")

    # --- 4. Generation Controls ---
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Generate Lecture Plan"):
            with st.spinner("Creating plan..."):
                prompt = "Create a detailed 5-day lecture plan based on this content. Include objectives and daily activities."
                response = model.generate_content([prompt, *input_data])
                st.markdown("### 📅 Lecture Plan")
                st.write(response.text)

    with col2:
        if st.button("📝 Create Mock Test"):
            with st.spinner("Writing questions..."):
                prompt = "Generate a 10-question mock test (MCQs and Short Answers) based on this material. Include an Answer Key at the end."
                response = model.generate_content([prompt, *input_data])
                st.markdown("### 📝 Mock Test")
                st.write(response.text)

    with col3:
        if st.button("📓 Extract Study Notes"):
            with st.spinner("Summarizing..."):
                prompt = "Create high-quality study notes from this content. Use bullet points and bold key concepts."
                response = model.generate_content([prompt, *input_data])
                st.markdown("### 📓 Study Notes")
                st.write(response.text)
else:
    st.info("Waiting for a file upload...")

# --- 5. Footer ---
st.divider()
st.caption("Built with Streamlit & Gemini 1.5 Flash")
