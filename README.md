
# 🏥 PromptRx – Discharge Instruction Simplifier

PromptRx is an AI-powered tool to simplify hospital discharge instructions into clear, categorized, and patient-friendly summaries, with an option to download the results as a PDF.

---

## 🌟 Features

- 📤 Upload discharge notes in **PDF, TXT, or CSV**
- 🧠 Uses OpenRouter + GPT to simplify and categorize
- 📋 Organized into 6 useful patient-focused categories
- 📄 Download everything as a clean PDF summary

---

## 🛠 Project Structure

```
PromptRx/
│
├── backend/
│   ├── app.py                 # Flask backend server
│   ├── utils/
│   │   └── formatter.py       # Prompt formatting utilities
│   ├── requirements.txt
│
├── frontend/
│   └── PromptRx_app.py                 # Streamlit frontend interface
│
├── README.md
```

---

## 🚀 How to Run This Project Locally

### 🔧 1. Clone the Repository



### 📦 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### ⚙️ 3. Set Up Environment

Make sure you have your [OpenRouter API key](https://openrouter.ai) and update it inside `backend/app.py`:
```python
OPENROUTER_API_KEY = "your_api_key"
```

---

### ▶️ 4. Run the Backend (Flask API)
```bash
cd backend
python app.py
```

This starts the backend at:
📍 `http://127.0.0.1:5000`

---

### 💻 5. Run the Frontend (Streamlit UI)
Open another terminal and run:

```bash
cd frontend
streamlit run PromptRx_app.py
```

This launches the app at:
🌐 `http://localhost:8501`

---

## 📂 Sample File Formats Supported

- PDF (text-based only)
- TXT
- CSV (must contain a column named `instruction`)

---

## 📦 Python Dependencies

- Flask
- Streamlit
- Requests
- FPDF
- Pandas
- PyPDF2

All are listed in `requirements.txt`.

---

## 💡 Troubleshooting

- Make sure Flask and Streamlit are not blocked by firewall
- Ensure Python version is 3.8 or higher
- If PDF download fails, check API key usage or console logs for detailed error

---

