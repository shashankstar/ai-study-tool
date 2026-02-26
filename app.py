import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. Page Setup ---
st.set_page_config(page_title="AI Study Assistant", page_icon="🎓", layout="wide")

# --- 2. Security & API Key ---
# Priority: 1. Streamlit Cloud Secrets, 2. Sidebar Input
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.title("🔐 Settings")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    else:
        st.success("API Key Active ✅")
    st.info("Get a key: [aistudio.google.com](https://aistudio.google.com/)")

if not api_key:
    st.warning("Please provide an API Key to start.")
    st.stop()

# --- 3. Initialize Model with Safety Settings ---
genai.configure(api_key=api_key)

# Relaxed safety settings prevent common "false positive" blocks for educational content
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

# --- 4. Main App UI ---
st.title("📚 AI Educator Tool")
uploaded_file = st.file_uploader("Upload PDF or Image", type=['pdf', 'jpg', 'png', 'jpeg'])

if uploaded_file:
    with st.spinner("Reading file..."):
        if uploaded_file.type == "application/pdf":
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = "".join([page.get_text() for page in doc])
                input_data = [f"Text content: {text}"]
                st.success("PDF Text Extracted!")
            except Exception as e:
                st.error(f"Could not read PDF: {e}")
                st.stop()
        else:
            img = Image.open(uploaded_file)
            st.image(img, width=300)
            input_data = ["Analyze this educational image:", img]
            st.success("Image Loaded!")

    st.divider()
    
    # Helper function to prevent the "Retry Unary" crash
    def safe_generate(prompt_text, data):
        try:
            response = model.generate_content([prompt_text, *data])
            # Check if the AI actually returned a result or was blocked
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            else:
                return "⚠️ The AI blocked this response due to safety filters. Try a different page."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Lecture Plan"):
            with st.spinner("Working..."):
                result = safe_generate("Create a 5-day lecture plan for this content.", input_data)
                st.markdown(result)

    with col2:
        if st.button("📝 Mock Test"):
            with st.spinner("Working..."):
                result = safe_generate("Create a 10-question mock test with an answer key based on this.", input_data)
                st.markdown(result)

    with col3:
        if st.button("📓 Study Notes"):
            with st.spinner("Working..."):
                result = safe_generate("Summarize this into clear, bulleted study notes.", input_data)
                st.markdown(result)
