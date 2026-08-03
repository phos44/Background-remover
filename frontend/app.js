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
const modelSelect = document.querySelector("#modelSelect");
const alphaMatting = document.querySelector("#alphaMatting");
const postProcessMask = document.querySelector("#postProcessMask");

let selectedFile = null;
let resultUrl = null;
let defaultModel = "bria-rmbg";

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

const loadModels = async () => {
  try {
    const response = await fetch("/api/models");
    if (!response.ok) {
      throw new Error("Не удалось загрузить список моделей");
    }

    const payload = await response.json();
    defaultModel = payload.default_model;
    modelSelect.innerHTML = "";

    payload.models.forEach((model) => {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.title;
      option.title = model.description;
      modelSelect.appendChild(option);
    });

    modelSelect.value = defaultModel;
    modelSelect.disabled = false;
  } catch (error) {
    modelSelect.innerHTML = '<option value="bria-rmbg">Универсальный (рекомендуется)</option>';
    modelSelect.disabled = false;
    setStatus(error.message, true);
  }
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

const buildRequestUrl = () => {
  const params = new URLSearchParams();
  params.set("model", modelSelect.value || defaultModel);
  params.set("alpha_matting", String(alphaMatting.checked));
  params.set("post_process_mask", String(postProcessMask.checked));
  return `/api/remove-background?${params.toString()}`;
};

const processImage = async () => {
  if (!selectedFile) return;

  const body = new FormData();
  body.append("image", selectedFile);

  processButton.disabled = true;
  loader.hidden = false;
  resultPreview.hidden = true;
  resultMeta.textContent = "Обработка";
  setStatus("Удаляю фон... Первый запуск модели может занять до минуты.");

  try {
    const response = await fetch(buildRequestUrl(), {
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
loadModels();

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
