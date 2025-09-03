const form = document.getElementById('email-form');
        const emailTextarea = document.getElementById('email-text');
        const emailFile = document.getElementById('email-file');
        const fileLabel = document.getElementById('file-label');
        const resultsDiv = document.getElementById('results');
        const loader = document.getElementById('loader');
        const originalFileLabel = fileLabel.textContent;

        emailFile.addEventListener('change', () => {
            if (emailFile.files.length > 0) {
                fileLabel.textContent = `Arquivo anexado: ${emailFile.files[0].name}`;
            } else {
                fileLabel.textContent = originalFileLabel;
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            resultsDiv.style.display = 'none';
            loader.style.display = 'block';

            let emailContent = '';
            
            if (emailTextarea.value.trim() !== '') {
                emailContent = emailTextarea.value;
                processEmail(emailContent);
            } else if (emailFile.files.length > 0) {
                const file = emailFile.files[0];
                const reader = new FileReader();

                reader.onload = async (event) => {
                    emailContent = event.target.result;
                    processEmail(emailContent);
                };

                reader.onerror = () => {
                    alert('Erro ao ler o arquivo.');
                    loader.style.display = 'none';
                };

                reader.readAsText(file);
            } else {
                loader.style.display = 'none';
                alert('Por favor, insira o texto do e-mail ou faça upload de um arquivo.');
            }
        });

        async function processEmail(content) {
            try {
                // A URL agora é relativa, pois o backend e o frontend estarão no mesmo servidor.
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email_content: content })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    alert(`Erro ao conectar com o servidor: ${errorData.error || response.statusText}. Verifique se o backend está rodando.`);
                    return;
                }

                const data = await response.json();
                
                document.getElementById('category-result').textContent = data.category;
                document.getElementById('response-result').textContent = data.response;
                
                loader.style.display = 'none';
                resultsDiv.style.display = 'block';
            } catch (error) {
                loader.style.display = 'none';
                resultsDiv.style.display = 'none';
                alert('Erro ao conectar com o servidor. Verifique se o backend está rodando.');
                console.error('Error:', error);
            }
        }