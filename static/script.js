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

  addToHistory({
    sender: emailSender.value || "Desconhecido",
    subject: emailSubject.value || "Sem assunto",
    content: emailContent,
    category: data.category,
    response: data.response,
  });
}

// Histórico
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

// Envio do formulário
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultsDiv.style.display = "none";
  toggleLoader(true);

  try {
    const formData = new FormData();
    if (emailTextarea.value.trim() !== "") {
      formData.append("email_content", emailTextarea.value.trim());
    }
    if (emailFile.files.length > 0) {
      formData.append("email_file", emailFile.files[0]);
    }
    formData.append("sender", emailSender.value.trim());
    formData.append("subject", emailSubject.value.trim());

    const response = await fetch("/predict", {
      method: "POST",
      body: formData, // enviando multipart/form-data
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || response.statusText);
    }

    const data = await response.json();
    const emailContent = emailTextarea.value || (emailFile.files[0]?.name || "");
    updateResults(data, emailContent);
    showToast("E-mail processado com sucesso!", "success");

    // Limpar campos após envio
    emailTextarea.value = "";
    emailFile.value = "";
    emailSender.value = "";
    emailSubject.value = "";
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

// Mostra toast com nome do arquivo
emailFile.addEventListener("change", () => {
  if (emailFile.files.length > 0) {
    showToast(`Arquivo selecionado: ${emailFile.files[0].name}`, "info");
  }
});
