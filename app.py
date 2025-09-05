from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import os
import re
import json
from datetime import datetime
import pdfplumber  # Para extrair texto de PDFs

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
    subcategoria = db.Column(db.String(50), nullable=True)
    resposta = db.Column(db.Text, nullable=False)
    data_processamento = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# -------------------------
# Configuração da API Gemini
# -------------------------
genai.configure(api_key=os.environ.get("API_KEY"))

# -------------------------
# Função de pré-processamento
# -------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
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
        # Recebe conteúdo do arquivo ou texto
        email_content = ""
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
        ALLOWED_EXTENSIONS = {".txt", ".pdf"}

        if 'email_file' in request.files and request.files['email_file'].filename != "":
            file = request.files['email_file']
            filename = file.filename.lower()
            ext = os.path.splitext(filename)[1]

            # Verifica extensão
            if ext not in ALLOWED_EXTENSIONS:
                return jsonify({"error": "Arquivo inválido! Apenas .txt ou .pdf são permitidos."}), 400

            # Verifica tamanho
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > MAX_FILE_SIZE:
                return jsonify({"error": "Arquivo muito grande! O limite é 2 MB."}), 400

            # Processa arquivo
            if filename.endswith(".pdf"):
                with pdfplumber.open(file) as pdf:
                    pages = [page.extract_text() for page in pdf.pages]
                    email_content = "\n".join([p for p in pages if p])
            else:  # .txt
                email_content = file.read().decode("utf-8")

        else:
            data = request.form or request.get_json(silent=True) or {}
            email_content = data.get("email_content", "").strip()

        # Se conteúdo estiver vazio
        if not email_content:
            email_content = "(Conteúdo vazio)"

        processed_content = preprocess_text(email_content)

        # Prompt atualizado com subcategorias
        prompt = f"""
        Você é um assistente de IA que classifica e-mails de clientes.
        Classifique o e-mail em Categoria Principal (Produtivo ou Improdutivo)
        e Subcategoria (Solicitação de Status, Reclamação, Agradecimento, Spam)
        e gere uma resposta automática adequada.

        E-mail:
        "{processed_content}"

        Responda apenas com JSON no formato:
        {{
          "category": "Produtivo ou Improdutivo",
          "subcategory": "Subcategoria apropriada",
          "response": "Resposta automática sugerida"
        }}
        """

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-05-20",
            system_instruction="Retorne apenas um objeto JSON válido, sem texto extra."
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
                "subcategory": "Indefinida",
                "response": "Não foi possível classificar o e-mail."
            }

        # Salvar no banco
        novo_email = Email(
            conteudo=email_content,
            categoria=response_object.get("category", "Indefinido"),
            subcategoria=response_object.get("subcategory", "Indefinida"),
            resposta=response_object.get("response", "")
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
            "subcategory": e.subcategoria,
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
#    app.run(debug=True)    
