from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os, re, json
import pdfplumber
import google.generativeai as genai

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))
CORS(app, resources={r"/predict": {"origins": "*"}})

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def serve_index():
    return render_template("index.html")

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def read_file(file):
    if file.filename.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    return ""

def call_ai(processed_content):
    prompt = f"""
    Classifique o seguinte e-mail como 'Produtivo' ou 'Improdutivo' e gere uma resposta:

    "{processed_content}"

    Formato JSON:
    {{
        "category": "Produtivo" ou "Improdutivo",
        "response": "Resposta automática"
    }}
    """
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-05-20",
        system_instruction="Resposta deve ser JSON válido, sem texto extra."
    )
    response = model.generate_content(
        contents=[{"parts":[{"text": prompt}]}],
        generation_config={"response_mime_type": "application/json"}
    )
    try:
        text = response.text.replace("```json","").replace("```","")
        return json.loads(text)
    except:
        return {"category":"Indefinido","response":"Não foi possível classificar o e-mail."}

@app.route("/predict", methods=["POST"])
def predict():
    try:
        email_text = request.form.get("email_text", "").strip()
        email_file = request.files.get("email_file")
        if email_file and not email_text:
            email_text = read_file(email_file)
        if not email_text:
            return jsonify({"error":"Nenhum conteúdo fornecido"}), 400
        processed_content = preprocess_text(email_text)
        response_object = call_ai(processed_content)
        return jsonify(response_object)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__=="__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
