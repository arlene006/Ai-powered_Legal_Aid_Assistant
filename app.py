from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

LEGAL_PROMPT = """
You are an AI legal assistant for people in India.
When the user describes their problem:
1. Identify the legal category.
2. Name the relevant Indian law(s) and section(s).
3. Explain their rights simply.
4. Suggest next steps.
Format:
Category: ...
Relevant Law: ...
Rights: ...
Next Steps: ...
"""

def call_llm(user_message):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(LEGAL_PROMPT + "\nUser: " + user_message)
        print("✅ Gemini Response:", response.text)  # 👈 This line shows Gemini's output in terminal
        return response.text
    except Exception as e:
        print("❌ Gemini Error:", e)
        return f"⚠️ Error contacting AI: {e}"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    if not user_msg.strip():
        return jsonify({"reply": "Please enter a message."})
    ai_reply = call_llm(user_msg)
    return jsonify({"reply": ai_reply})

@app.route("/generate_notice", methods=["POST"])
def generate_notice():
    data = request.json
    name = data.get("name", "Your Name")
    address = data.get("address", "Your Address")
    issue = data.get("issue", "Your Issue Description")
    advice = data.get("advice", "")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Legal Notice / Complaint Letter", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, f"From:\n{name}\n{address}\n\nTo:\nConcerned Authority\n\nSubject: Legal Notice Regarding: {issue}\n\n{advice}\n\nKindly take necessary action at the earliest.\n\nSincerely,\n{name}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return send_file(temp_file.name, as_attachment=True, download_name="legal_notice.pdf")

if __name__ == "__main__":
    app.run(debug=True)
