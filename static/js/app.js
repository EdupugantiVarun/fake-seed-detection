const input = document.getElementById("seed_image");
const preview = document.getElementById("preview");
const wrap = document.getElementById("previewWrap");
const form = document.getElementById("uploadForm");

if (input) {
  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    preview.src = url;
    preview.classList.remove("hidden");
    wrap.classList.add("hidden");
  });
}
if (form) {
  form.addEventListener("submit", () => {
    const button = form.querySelector("button");
    button.textContent = "⏳ Analyzing...";
    button.disabled = true;
  });
}
