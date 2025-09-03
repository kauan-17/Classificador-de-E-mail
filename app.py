from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
import re
import json

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/predict": {"origins": "*"}})

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        email_content = data.get('email_content', '')

        if not email_content:
            return jsonify({'error': 'Nenhum conteúdo de e-mail fornecido'}), 400

        processed_content = preprocess_text(email_content)
        
        prompt = f"""
        Você é um assistente de IA especializado em classificar e-mails de clientes.
        Classifique o seguinte e-mail como "Produtivo" ou "Improdutivo" e gere uma resposta automática adequada.
        - "Produtivo" significa que o e-mail requer uma ação ou atenção direta (ex: pedido de ajuda, reclamação, solicitação de informação, etc.).
        - "Improdutivo" significa que o e-mail não requer uma ação direta, sendo apenas uma mensagem de cortesia ou spam.
        
        E-mail:
        "{processed_content}"

        Siga este formato JSON para a sua resposta:
        {{
          "category": "Produtivo" ou "Improdutivo",
          "response": "Resposta automática sugerida"
        }}
        """

        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-preview-05-20',
            system_instruction="Sua resposta deve ser um objeto JSON válido, sem nenhum texto extra antes ou depois do JSON."
        )

        response = model.generate_content(
            contents=[{'parts': [{'text': prompt}]}],
            generation_config={'response_mime_type': 'application/json'}
        )
        
        response_json_text = response.text.replace('```json', '').replace('```', '')
        response_object = json.loads(response_json_text)
        
        return jsonify(response_object), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
