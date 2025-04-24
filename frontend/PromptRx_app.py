import streamlit as st
import requests
from PyPDF2 import PdfReader
import pandas as pd

API_URL = "http://127.0.0.1:5000/full-summary-pdf"

# --- File Parsers ---
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def extract_text_from_csv(file):
    df = pd.read_csv(file)
    if "instruction" not in df.columns:
        raise ValueError("CSV must contain a column named 'instruction'")
    return "\n".join(df["instruction"].dropna().astype(str).tolist())

# --- Page Setup ---
st.set_page_config(page_title="PromptRx", layout="centered")
st.markdown("## 🏥 PromptRx")
st.markdown("Upload your discharge instructions in **PDF, TXT, or CSV** format. We will simplify and categorize the instructions for you. You can review the output before downloading the PDF.")

# --- Initialize session state ---
if "simplified_items" not in st.session_state:
    st.session_state.simplified_items = None
    st.session_state.grouped_summary = ""
    st.session_state.raw_text = ""

uploaded_file = st.file_uploader("📤 Upload File (PDF, TXT, or CSV)", type=["pdf", "txt", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            raw_text = extract_text_from_txt(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            raw_text = extract_text_from_csv(uploaded_file)
        else:
            st.error("❌ Unsupported file type.")
            raw_text = ""

        if raw_text:
            st.markdown("### 📄 Extracted Instructions")
            st.text_area("Text Preview", raw_text, height=300)

            if st.button("🔁 Simplify and Categorize"):
                with st.spinner("🧠 Processing..."):
                    response = requests.post(
                        API_URL,
                        headers={"Content-Type": "application/json"},
                        json={"text": raw_text, "preview_only": True}
                    )

                if response.status_code == 200:
                    output = response.json()
                    st.session_state.simplified_items = output["simplified_items"]
                    st.session_state.grouped_summary = output["grouped_summary"]
                    st.session_state.raw_text = raw_text
                    st.success("✅ Simplification Complete!")

            # Display results if they exist
            if st.session_state.simplified_items:
                st.markdown("### 🧩 Simplified & Categorized Instructions")
                for item in st.session_state.simplified_items:
                    st.markdown(f"- **{item['category']}**: {item['simplified_text']}")

                st.markdown("### 📦 Grouped Summary")
                st.text_area("Grouped Instructions", st.session_state.grouped_summary, height=300)

                if st.button("⬇️ Download as PDF"):
                    with st.spinner("📄 Generating PDF..."):
                        download_response = requests.post(
                            API_URL,
                            headers={"Content-Type": "application/json"},
                            json={"text": st.session_state.raw_text}
                        )
                    if download_response.status_code == 200:
                        st.download_button(
                            label="📥 Click here to download your PDF",
                            data=download_response.content,
                            file_name="Simplified_Discharge_Instructions.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("❌ PDF generation failed.")

    except Exception as e:
        st.error(f"⚠️ Error processing file: {str(e)}")

else:
    st.info("Please upload a file to begin.")
