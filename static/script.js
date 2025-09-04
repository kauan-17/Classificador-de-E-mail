const form = document.getElementById("email-form");
const emailTextarea = document.getElementById("email-text");
const emailFile = document.getElementById("email-file");
const resultsDiv = document.getElementById("results");
const loader = document.getElementById("loader");
const submitButton = form.querySelector("button[type='submit']");

// Novos campos
const emailSender = document.getElementById("email-sender");
const emailSubject = document.getElementById("email-subject");

// Histórico
const historyDiv = document.getElementById("history");
const historyList = document.getElementById("history-list");

// Função para mostrar toast
function showToast(message, type = "info", duration = 4000) {
  // Cria container se não existir
  let toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.classList.add("toast", type);
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

// Loader
function toggleLoader(show) {
  loader.style.display = show ? "block" : "none";
  submitButton.disabled = show;
}

// Resultados
function updateResults(data, emailContent) {
  document.getElementById("category-result").textContent =
    data.category || "Indefinido";
  document.getElementById("response-result").textContent =
    data.response || "Sem resposta gerada.";
  resultsDiv.style.display = "block";

  // Adiciona no histórico
  addToHistory({
    sender: emailSender.value || "Desconhecido",
    subject: emailSubject.value || "Sem assunto",
    content: emailContent,
    category: data.category,
    response: data.response,
  });
}

// Adiciona item no histórico
function addToHistory(entry) {
  const li = document.createElement("li");
  li.innerHTML = `
    <strong>De:</strong> ${entry.sender} <br>
    <strong>Assunto:</strong> ${entry.subject} <br>
    <strong>Categoria:</strong> ${entry.category} <br>
    <strong>Resposta:</strong> ${entry.response} <br>
    <strong>Trecho do conteúdo:</strong> ${entry.content.substring(0, 100)}...
    <hr>
  `;
  historyList.prepend(li);
  historyDiv.style.display = "block";
}

// Pega conteúdo do email
function getEmailContent() {
  return new Promise((resolve, reject) => {
    if (emailTextarea.value.trim() !== "") {
      resolve(emailTextarea.value);
    } else if (emailFile.files.length > 0) {
      const file = emailFile.files[0];
      const reader = new FileReader();
      reader.onload = (event) => resolve(event.target.result);
      reader.onerror = () => reject("Erro ao ler o arquivo.");
      reader.readAsText(file);
    } else {
      reject(
        "Por favor, insira o texto do e-mail ou faça upload de um arquivo."
      );
    }
  });
}

// Envio do formulário
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultsDiv.style.display = "none";
  toggleLoader(true);

  try {
    const emailContent = await getEmailContent();

    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email_content: emailContent,
        sender: emailSender.value,
        subject: emailSubject.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || response.statusText);
    }

    const data = await response.json();
    updateResults(data, emailContent);
    showToast("E-mail processado com sucesso!", "success");
  } catch (error) {
    resultsDiv.style.display = "none";
    showToast(
      "Erro ao processar o e-mail. Verifique se o backend está rodando.",
      "error"
    );
    console.error(error);
  } finally {
    toggleLoader(false);
  }
});

// Botão de limpar
document.getElementById("clear-btn").addEventListener("click", () => {
  resultsDiv.style.display = "none";
  emailTextarea.value = "";
  emailFile.value = "";
  emailSender.value = "";
  emailSubject.value = "";
});

// Atualiza nome do arquivo e mostra toast
emailFile.addEventListener("change", () => {
  if (emailFile.files.length > 0) {
    showToast(`Arquivo selecionado: ${emailFile.files[0].name}`, "info");
  }
});
// -------------------------