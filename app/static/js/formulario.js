(() => {
  const syncXd = () => {
    const form = document.querySelector("#formulario");
    const metodo = form?.querySelector('[name="metodo"]');
    const xd = form?.querySelector('[name="xd"]');
    if (!metodo || !xd) {
      return;
    }
    xd.required = metodo.value !== "tangente";
  };

  document.addEventListener("change", (event) => {
    if (event.target?.name === "metodo") {
      syncXd();
    }
  });
  document.addEventListener("DOMContentLoaded", syncXd);
  document.addEventListener("htmx:oobAfterSwap", syncXd);
})();
