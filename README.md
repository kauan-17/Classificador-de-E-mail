Classificador de E-mail com IA
Visão Geral
Este projeto é um classificador de e-mail que utiliza a API do Gemini para categorizar e-mails como "Produtivo" ou "Improdutivo" e, em seguida, gerar uma resposta automática. O backend é construído com Flask em Python e o frontend com HTML, CSS e JavaScript.

Estrutura do Projeto
A estrutura de pastas do projeto segue as convenções recomendadas para aplicações Flask, garantindo uma implantação e manutenção mais fáceis.

/nome-do-seu-projeto
├── app.py                      # Backend da aplicação em Flask
├── requirements.txt            # Dependências Python
├── Procfile                    # Comando de inicialização para o Render
├── static/                     # Arquivos estáticos (CSS, JS)
│   ├── style.css
│   └── script.js
└── templates/                  # Arquivos de template (HTML)
    └── index.html

Requisitos
Para executar este projeto localmente, você precisa ter o Python 3.10 ou superior instalado. Além disso, é necessário ter uma chave de API para o Google Gemini.

Instalação e Execução
Siga os passos abaixo para configurar e executar a aplicação em seu ambiente local.

Clone o Repositório:

git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio

Crie e Ative um Ambiente Virtual (Recomendado):

python -m venv venv
source venv/bin/activate   # No Linux/macOS
# ou
venv\Scripts\activate      # No Windows

Instale as Dependências:

pip install -r requirements.txt

Configure a Chave de API:

Crie um arquivo .env na raiz do projeto e adicione sua chave de API.

GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"

Execute a Aplicação:

python app.py

A aplicação estará disponível em http://127.0.0.1:5000.

Implantação (Deploy)
Para implantar no Render, você precisará configurar as variáveis de ambiente e o comando de inicialização.

Variáveis de Ambiente:

Adicione a sua chave de API nas variáveis de ambiente do Render, usando o nome GOOGLE_API_KEY.

Comando de Inicialização (Procfile):

Certifique-se de que o seu Procfile contenha o seguinte comando, que é essencial para o Render iniciar a aplicação.

web: gunicorn app:app
