document.addEventListener("submit", (event) => {
  const button = event.target.querySelector("button[type='submit']");
  if (!button) return;
  button.dataset.originalText = button.textContent;
  button.textContent = "Working…";
  button.disabled = true;
});
