const form = document.getElementById("email-form");
const emailTextarea = document.getElementById("email-text");
const emailFile = document.getElementById("email-file");
const fileLabel = document.getElementById("file-label");
const loader = document.getElementById("loader");
const resultsDiv = document.getElementById("results");
const originalFileLabel = fileLabel.textContent;

emailFile.addEventListener("change", () => {
    if (emailFile.files.length > 0) {
        fileLabel.textContent = `Arquivo anexado: ${emailFile.files[0].name}`;
    } else {
        fileLabel.textContent = originalFileLabel;
    }
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultsDiv.style.display = "none";
    loader.style.display = "block";

    const formData = new FormData();
    if (emailTextarea.value.trim() !== "") {
        formData.append("email_text", emailTextarea.value);
    } else if (emailFile.files.length > 0) {
        formData.append("email_file", emailFile.files[0]);
    } else {
        loader.style.display = "none";
        alert("Por favor, insira texto ou faça upload de um arquivo.");
        return;
    }

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("category-result").textContent = data.category;
            document.getElementById("response-result").textContent = data.response;
            resultsDiv.style.display = "block";
        }

    } catch (err) {
        alert("Erro ao conectar com o servidor.");
        console.error(err);
    } finally {
        loader.style.display = "none";
    }
});
