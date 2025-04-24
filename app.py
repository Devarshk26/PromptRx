from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.formatter import format_prompt
import requests
from fpdf import FPDF
import uuid
from textwrap import wrap
import re
import io

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

CATEGORY_EMOJIS = {
    "medication": "[MEDICATION]",
    "follow_up": "[FOLLOW-UP]",
    "warning": "[WARNING]",
    "general_info": "[INFO]",
    "emergency_room": "[EMERGENCY]"
}

def sanitize_text(text):
    text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return text.encode('latin-1', 'replace').decode('latin-1')

def call_llm(prompt, model="openai/gpt-4o-mini"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    try:
        data = response.json()
        if response.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {data.get('error', {}).get('message', 'Unknown API error')}"
    except Exception as e:
        return f"Error: Failed to parse LLM response - {str(e)}"

@app.route("/full-summary-pdf", methods=["POST"])
def full_summary_pdf():
    data = request.json
    full_text = data.get("text")
    model = data.get("model", "openai/gpt-4o-mini")

    if not full_text:
        return jsonify({"error": "No input text provided"}), 400

    instructions = [line.strip() for line in full_text.replace(". ", ".\n").split("\n") if line.strip()]
    simplified_items = []

    for instruction in instructions:
        simplified = call_llm(format_prompt(instruction), model)
        cat_prompt = (
            "You are a strict classifier for Emergency Room Discharge Instructions.\n"
            "Your task is to assign the instruction below to exactly one of the following categories:\n"
            "- medication\n"
            "- follow_up\n"
            "- warning\n"
            "- general_info\n"
            "- emergency_room\n\n"
            "IMPORTANT RULES:\n"
            "- Only reply with category from the list.\n"
            "- Do not explain.\n"
            "- Do not repeat the instruction.\n"
            "- Do NOT add, guess, or explain anything beyond the original content.\n"
            "- Do not say anything else.\n\n"
            f"Instruction:\n{simplified}"
        )
        category = call_llm(cat_prompt, model).lower().strip().replace(" ", "_")
        simplified_items.append({
            "category": CATEGORY_EMOJIS.get(category, "[UNCATEGORIZED]"),
            "simplified_text": simplified
        })

    group_prompt = f"""
        You are a medical assistant simplifying Emergency room discharge instructions.

        Your task:
        - Rewrite the instructions below using plain, simplified language.
        - Organize the content into categories.
        - Use bullet points.
        - **IMPORTANT** - Do NOT add, guess, or explain anything beyond the original content.
        - Keep each item short and focused.

        Categories:
        1) Emergency signs when to go to the ER\n
        2) Medicines and pain relief what to take, when, how\n
        3) Things the patient should avoid actions, foods, etc.\n
        4) Things the patient should do recovery actions\n
        5) Follow-up and next steps appointments or further care\n
        6) Other important details anything else provided\n

Instructions to rewrite:
\"\"\"{full_text.strip()}\"\"\"
"""
    grouped_summary = call_llm(group_prompt, model)

    if data.get("preview_only", False):
        return jsonify({
            "simplified_items": simplified_items,
            "grouped_summary": grouped_summary
        })

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Discharge Instruction Summary", ln=True)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "\nSimplified & Categorized Instructions:", ln=True)
        pdf.set_font("Arial", size=11)

        for item in simplified_items:
            cleaned = sanitize_text(item['simplified_text'].replace("\n", " ").strip())
            cleaned = re.sub(r'(\S{50,})', lambda m: ' '.join(wrap(m.group(1), 50)), cleaned)
            line = f"- {item['category']} {cleaned}"
            for wline in wrap(line, width=100):
                pdf.cell(0, 8, wline, ln=True)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "\nGrouped Summary:", ln=True)
        pdf.set_font("Arial", size=11)
        for wline in wrap(sanitize_text(grouped_summary.strip()), width=100):
            pdf.cell(0, 8, wline, ln=True)

        pdf_buffer = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        pdf_buffer.write(pdf_bytes)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="Simplified_Discharge_Instructions.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("🚨 PDF generation error:", str(e))
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
