(() => {
  let chart;

  const formatDecimal = (value, places = 4) => {
    if (value == null || Number.isNaN(value)) {
      return "—";
    }
    let texto = Number(value).toFixed(places);
    if (texto.includes(".")) {
      texto = texto.replace(/0+$/, "").replace(/\.$/, "");
    }
    return texto;
  };

  const renderGrafico = (root) => {
    const canvas = root.querySelector("canvas");
    if (!canvas || typeof Chart === "undefined") {
      return;
    }

    const xs = JSON.parse(root.dataset.xs || "[]");
    const ys = JSON.parse(root.dataset.ys || "[]");
    const raizRaw = root.dataset.raiz;
    const raiz = raizRaw === "" ? null : Number(raizRaw);
    const placesRaw = Number(root.dataset.places);
    const places = Number.isInteger(placesRaw) && placesRaw >= 0 ? placesRaw : 4;

    const puntos = xs.map((x, i) => ({ x, y: ys[i] })).filter((punto) => punto.y !== null);

    if (chart) {
      chart.destroy();
    }

    const datasets = [
      {
        label: "f(x)",
        data: puntos,
        borderColor: "#2563eb",
        backgroundColor: "transparent",
        pointRadius: 0,
        borderWidth: 2,
        tension: 0.15,
      },
    ];

    if (raiz !== null && !Number.isNaN(raiz)) {
      datasets.push({
        label: "Raíz",
        data: [{ x: raiz, y: 0 }],
        showLine: false,
        pointRadius: 6,
        pointBackgroundColor: "#0f172a",
        pointBorderColor: "#0f172a",
      });
    }

    chart = new Chart(canvas, {
      type: "line",
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        resizeDelay: 0,
        layout: {
          padding: 0,
        },
        plugins: {
          legend: { display: true, labels: { color: "#334155" } },
          tooltip: {
            callbacks: {
              label(ctx) {
                const { x, y } = ctx.parsed;
                const label = `f(${formatDecimal(x, places)}) = ${formatDecimal(y, places)}`;
                if (ctx.dataset.label === "Raíz") {
                  return `Raíz: ${label}`;
                }
                return label;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            min: xs.length ? xs[0] : undefined,
            max: xs.length ? xs[xs.length - 1] : undefined,
            title: { display: true, text: "x" },
            grid: { color: "#e2e8f0" },
          },
          y: {
            type: "linear",
            title: { display: true, text: "f(x)" },
            grid: { color: "#e2e8f0" },
          },
        },
      },
    });
  };

  const buscarYRenderizar = () => {
    const root = document.querySelector("[data-grafico]");
    if (!root) {
      return;
    }
    requestAnimationFrame(() => {
      renderGrafico(root);
      requestAnimationFrame(() => chart?.resize());
    });
  };

  document.addEventListener("htmx:oobAfterSwap", buscarYRenderizar);
  document.addEventListener("DOMContentLoaded", buscarYRenderizar);
})();
