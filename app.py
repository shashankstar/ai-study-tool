import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# Page Setup
st.set_page_config(page_title="AI Study Tool", layout="wide")
st.title("📚 AI Educator: PDF & Image to Study Material")

# Sidebar for API Key & Instructions
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("[Get a free API Key here](https://aistudio.google.com/)")
    st.divider()
    st.info("Upload a textbook PDF or a photo of a page to generate materials.")

if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# File Uploader
uploaded_file = st.file_uploader("Upload Study Material (PDF or Image)", type=['pdf', 'jpg', 'png', 'jpeg'])

if uploaded_file:
    with st.spinner("Reading your file..."):
        # Scenario A: User uploads a PDF
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            input_data = [f"System: Treat the following text as the source material for all tasks.\n\n{text_content}"]
            st.success("PDF loaded successfully!")

        # Scenario B: User uploads an Image
        else:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Page", width=400)
            input_data = ["System: Analyze this image and use its content for the following tasks.", img]
            st.success("Image loaded successfully!")

    # Action Buttons
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Generate Lecture Plan"):
            with st.spinner("Creating plan..."):
                prompt = "Create a 5-day structured lecture plan based on this content. Include learning objectives and a daily breakdown."
                response = model.generate_content([prompt, *input_data])
                st.subheader("Lecture Plan")
                st.write(response.text)

    with col2:
        if st.button("📝 Create Mock Test"):
            with st.spinner("Writing questions..."):
                prompt = "Generate a 10-question mock test (multiple choice and short answer) based on this material. Include an answer key at the bottom."
                response = model.generate_content([prompt, *input_data])
                st.subheader("Mock Test")
                st.write(response.text)

    with col3:
        if st.button("📓 Summarize Notes"):
            with st.spinner("Summarizing..."):
                prompt = "Summarize this content into high-quality study notes. Use bullet points, bold key terms, and highlight core concepts."
                response = model.generate_content([prompt, *input_data])
                st.subheader("Study Notes")
                st.write(response.text)
