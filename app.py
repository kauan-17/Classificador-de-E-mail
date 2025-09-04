from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import os
import re
import json
from datetime import datetime

# -------------------------
# Configuração do Flask
# -------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/predict": {"origins": "*"}})

# -------------------------
# Configuração do Banco (SQLite)
# -------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emails.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------------
# Modelo de Tabela
# -------------------------
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    data_processamento = db.Column(db.DateTime, default=datetime.utcnow)

# Criar as tabelas no banco
with app.app_context():
    db.create_all()

# -------------------------
# Configuração da API Gemini
# -------------------------
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# -------------------------
# Função de pré-processamento
# -------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# -------------------------
# Rotas
# -------------------------
@app.route("/")
def serve_index():
    return render_template("index.html")  

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True) or {}
        email_content = data.get("email_content", "").strip()

        if not email_content:
            return jsonify({"error": "Nenhum conteúdo de e-mail fornecido"}), 400

        processed_content = preprocess_text(email_content)

        # Prompt para AI
        prompt = f"""
        Você é um assistente de IA especializado em classificar e-mails de clientes.
        Classifique o seguinte e-mail como "Produtivo" ou "Improdutivo" e gere uma resposta automática adequada.

        E-mail:
        "{processed_content}"

        Siga este formato JSON para a sua resposta:
        {{
          "category": "Produtivo" ou "Improdutivo",
          "response": "Resposta automática sugerida"
        }}
        """

        # Chamada ao modelo
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-05-20",
            system_instruction="Sua resposta deve ser um objeto JSON válido, sem nenhum texto extra antes ou depois do JSON."
        )

        response = model.generate_content(
            contents=[{"parts": [{"text": prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )

        response_json_text = response.text.replace("```json", "").replace("```", "")

        try:
            response_object = json.loads(response_json_text)
        except json.JSONDecodeError:
            response_object = {
                "category": "Indefinido",
                "response": "Não foi possível classificar o e-mail."
            }

        # -------------------------
        # Salvar no banco
        # -------------------------
        novo_email = Email(
            conteudo=email_content,
            categoria=response_object["category"],
            resposta=response_object["response"]
        )
        db.session.add(novo_email)
        db.session.commit()

        return jsonify(response_object), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    emails = Email.query.order_by(Email.data_processamento.desc()).limit(10).all()
    result = [
        {
            "id": e.id,
            "conteudo": e.conteudo,
            "categoria": e.categoria,
            "resposta": e.resposta,
            "data_processamento": e.data_processamento.strftime("%Y-%m-%d %H:%M:%S")
        }
        for e in emails
    ]
    return jsonify(result), 200

# -------------------------
# Executa servidor
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
