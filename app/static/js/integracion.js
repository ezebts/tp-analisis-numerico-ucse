(() => {
  const syncSubintervalos = () => {
    const form = document.querySelector("#formulario");
    const metodo = form?.querySelector('[name="metodo"]');
    const campo = form?.querySelector("[data-campo-n]");
    const input = form?.querySelector('[name="n"]');
    if (!form || !metodo || !campo || !input) {
      return;
    }
    const conN = new Set((form.dataset.metodosConN || "").split(",").filter(Boolean));
    const visible = conN.has(metodo.value);
    campo.hidden = !visible;
    input.required = visible;
  };

  document.addEventListener("change", (event) => {
    if (event.target?.name === "metodo") {
      syncSubintervalos();
    }
  });
  document.addEventListener("htmx:oobAfterSwap", syncSubintervalos);
  document.addEventListener("DOMContentLoaded", syncSubintervalos);
})();
