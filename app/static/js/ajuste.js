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

  const colorEje = (ctx) => (ctx.tick.value === 0 ? "#94a3b8" : "#e2e8f0");
  const grosorEje = (ctx) => (ctx.tick.value === 0 ? 1.5 : 1);

  const etiquetasPuntos = {
    id: "etiquetasPuntos",
    afterDatasetsDraw(chart) {
      const indice = chart.data.datasets.findIndex((dataset) => dataset.label === "Puntos");
      if (indice < 0) {
        return;
      }
      const meta = chart.getDatasetMeta(indice);
      const ctx = chart.ctx;
      ctx.save();
      ctx.fillStyle = "#334155";
      ctx.font = "12px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      meta.data.forEach((punto, i) => {
        ctx.fillText(`P${i + 1}`, punto.x, punto.y - 8);
      });
      ctx.restore();
    },
  };

  const destruir = () => {
    if (chart) {
      chart.destroy();
      chart = undefined;
    }
  };

  const renderAjuste = (root) => {
    const canvas = root.querySelector("canvas");
    if (!canvas || typeof Chart === "undefined") {
      return;
    }

    const puntosX = JSON.parse(root.dataset.puntosX || "[]");
    const puntosY = JSON.parse(root.dataset.puntosY || "[]");
    const xs = JSON.parse(root.dataset.xs || "[]");
    const ys = JSON.parse(root.dataset.ys || "[]");
    const puntos = puntosX.map((x, i) => ({ x, y: puntosY[i] }));
    const recta = xs.map((x, i) => ({ x, y: ys[i] }));

    destruir();

    chart = new Chart(canvas, {
      type: "scatter",
      data: {
        datasets: [
          {
            type: "line",
            label: "Curva de ajuste",
            data: recta,
            borderColor: "#2563eb",
            backgroundColor: "transparent",
            pointRadius: 0,
            borderWidth: 2,
            tension: 0,
            order: 2,
          },
          {
            type: "scatter",
            label: "Puntos",
            data: puntos,
            backgroundColor: "#0f172a",
            pointRadius: 5,
            order: 1,
          },
        ],
      },
      plugins: [etiquetasPuntos],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, labels: { color: "#334155" } },
          tooltip: {
            callbacks: {
              label(ctx) {
                const { x, y } = ctx.parsed;
                if (ctx.dataset.label === "Puntos") {
                  return `P${ctx.dataIndex + 1} (${formatDecimal(x)}, ${formatDecimal(y)})`;
                }
                return `y = ${formatDecimal(y)}`;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            title: { display: true, text: "X", color: "#64748b" },
            ticks: { color: "#64748b" },
            grid: { color: colorEje, lineWidth: grosorEje },
            border: { display: false },
          },
          y: {
            type: "linear",
            title: { display: true, text: "Y", color: "#64748b" },
            ticks: { color: "#64748b" },
            grid: { color: colorEje, lineWidth: grosorEje },
            border: { display: false },
          },
        },
      },
    });
  };

  const buscarYRenderizar = () => {
    const root = document.querySelector("[data-ajuste]");
    if (!root) {
      destruir();
      return;
    }
    requestAnimationFrame(() => {
      renderAjuste(root);
      requestAnimationFrame(() => chart?.resize());
    });
  };

  document.addEventListener("htmx:oobAfterSwap", buscarYRenderizar);
  document.addEventListener("DOMContentLoaded", buscarYRenderizar);
})();
