(() => {
  const syncCamposIterativos = () => {
    const form = document.querySelector("#formulario");
    const metodo = form?.querySelector('[name="metodo"]');
    if (!form || !metodo) {
      return;
    }
    const requiere = metodo.value !== "gauss_jordan";
    form.querySelectorAll('[data-campo-iterativo] input').forEach((campo) => {
      campo.required = requiere;
    });
  };

  document.addEventListener("change", (event) => {
    if (event.target?.name === "metodo") {
      syncCamposIterativos();
    }
  });
  document.addEventListener("DOMContentLoaded", syncCamposIterativos);
  document.addEventListener("htmx:oobAfterSwap", syncCamposIterativos);

  let enviandoCalculo = false;

  const generar = (form) => {
    const boton = form.querySelector("[data-accion-generar]");
    const url = boton?.getAttribute("hx-post");
    if (!url || typeof htmx?.ajax !== "function") {
      return Promise.resolve();
    }
    return htmx.ajax("POST", url, {
      source: boton,
      include: "#formulario",
      swap: "none",
    });
  };

  document.addEventListener(
    "submit",
    (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement) || form.id !== "formulario") {
        return;
      }
      if (enviandoCalculo) {
        return;
      }

      event.preventDefault();
      event.stopImmediatePropagation();

      generar(form).finally(() => {
        const actual = document.querySelector("#formulario");
        if (!actual || typeof htmx?.trigger !== "function") {
          return;
        }
        enviandoCalculo = true;
        htmx.trigger(actual, "submit");
        enviandoCalculo = false;
      });
    },
    true,
  );
})();
