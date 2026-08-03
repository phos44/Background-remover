const dropZone = document.querySelector("#dropZone");
const fileInput = document.querySelector("#fileInput");
const pickFile = document.querySelector("#pickFile");
const sourcePreview = document.querySelector("#sourcePreview");
const resultPreview = document.querySelector("#resultPreview");
const processButton = document.querySelector("#processButton");
const downloadButton = document.querySelector("#downloadButton");
const statusText = document.querySelector("#status");
const fileMeta = document.querySelector("#fileMeta");
const resultMeta = document.querySelector("#resultMeta");
const loader = document.querySelector("#loader");

let selectedFile = null;
let resultUrl = null;

const setStatus = (message, isError = false) => {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
};

const revokeResult = () => {
  if (resultUrl) {
    URL.revokeObjectURL(resultUrl);
    resultUrl = null;
  }
};

const formatSize = (bytes) => {
  const mb = bytes / 1024 / 1024;
  return `${mb.toFixed(mb >= 10 ? 0 : 1)} МБ`;
};

const selectFile = (file) => {
  if (!file) return;

  selectedFile = file;
  revokeResult();

  sourcePreview.src = URL.createObjectURL(file);
  sourcePreview.hidden = false;
  resultPreview.hidden = true;
  downloadButton.classList.add("disabled");
  downloadButton.removeAttribute("href");
  processButton.disabled = false;
  fileMeta.textContent = `${file.name} · ${formatSize(file.size)}`;
  resultMeta.textContent = "Готов к обработке";
  setStatus("Файл выбран. Можно запускать обработку.");
};

const processImage = async () => {
  if (!selectedFile) return;

  const body = new FormData();
  body.append("image", selectedFile);

  processButton.disabled = true;
  loader.hidden = false;
  resultPreview.hidden = true;
  resultMeta.textContent = "Обработка";
  setStatus("Удаляю фон...");

  try {
    const response = await fetch("/api/remove-background", {
      method: "POST",
      body,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || "Не удалось обработать изображение");
    }

    const blob = await response.blob();
    revokeResult();
    resultUrl = URL.createObjectURL(blob);
    resultPreview.src = resultUrl;
    resultPreview.hidden = false;
    downloadButton.href = resultUrl;
    downloadButton.classList.remove("disabled");
    resultMeta.textContent = "PNG с прозрачностью";
    setStatus("Готово. Результат можно скачать.");
  } catch (error) {
    resultMeta.textContent = "Ошибка";
    setStatus(error.message, true);
  } finally {
    loader.hidden = true;
    processButton.disabled = false;
  }
};

pickFile.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (event) => selectFile(event.target.files[0]));
processButton.addEventListener("click", processImage);

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("active");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("active");
  });
});

dropZone.addEventListener("drop", (event) => {
  selectFile(event.dataTransfer.files[0]);
});

