# *📧 Classificador de E-mail com IA*
## *💡 Visão Geral*
Este projeto é um classificador de e-mail que utiliza a API do Gemini para categorizar e-mails como "Produtivo" ou "Improdutivo" e, em seguida, gerar uma resposta automática. O backend é construído com Flask em Python e o frontend com HTML, CSS e JavaScript, proporcionando uma interface simples e funcional.

## *📂 Estrutura do Projeto*
A estrutura de pastas segue as convenções recomendadas do Flask, garantindo uma implantação e manutenção mais fáceis.

#### /Classificador de E mail
├── app.py                     
├── requirements.txt          
├── Procfile                   
├── static/                    
│   ├── style.css
│   └── script.js
└──  templates/                 
    └── index.html

#### *⚙️ Requisitos*
Para executar este projeto localmente, você precisa ter o Python 3.10 ou superior instalado. Além disso, é necessário ter uma chave de API para o Google Gemini.

## *🚀 Instalação e Execução*
Siga os passos abaixo para configurar e executar a aplicação em seu ambiente local.

### Clone o Repositório:

git clone [https://github.com/kauan-17/Classificador-de-E-mail.git](https://github.com/kauan-17o/Classificador-de-E-mail.git)
cd seu-repositorio

### *Crie e Ative um Ambiente Virtual (Recomendado):*

### *No Windows*
python -m venv venv

venv\Scripts\activate

Instale as Dependências:

py -m pip install -r requirements.txt

### *Configure a Chave de API:*

Crie um arquivo .env na raiz do projeto e adicione sua chave de API.

GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"

### *Execute a Aplicação:*

py app.py

A aplicação estará disponível em http://127.0.0.1:5000.

## *☁️ Implantação (Deploy) com Render*
Para hospedar a aplicação online, você pode usar a plataforma Render.

Crie uma Conta no Render: Se ainda não tiver, crie uma conta em https://render.com/.

Crie um Novo Web Service: No seu painel do Render, clique em "New" e selecione "Web Service".

Conecte o Repositório: Conecte sua conta do GitHub e selecione o repositório Classificador-de-E-mail.

### Configure as Variáveis de Ambiente:

Vá para a seção "Environment" ou "Environment Variables" do seu serviço no Render.

Adicione uma nova variável com a chave GOOGLE_API_KEY e o valor da sua chave de API.

### Verifique o Comando de Inicialização:

Certifique-se de que o Render esteja usando o comando correto para iniciar a aplicação, que deve estar no seu arquivo Procfile:

web: gunicorn app:app
### Observação sobre a Hospedagem Gratuita: 
A versão gratuita do Render tem algumas limitações. Uma delas é o suporte a arquivos grandes, que pode causar falhas na implantação. A URL da aplicação implantada será algo como: https://classificador-de-e-mail.onrender.com/.