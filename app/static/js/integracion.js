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

  const pasoCuadricula = (span, marcas = 8) => {
    const crudo = Math.abs(span) / marcas || 1;
    const mag = 10 ** Math.floor(Math.log10(crudo));
    const resto = crudo / mag;
    const nice = resto >= 5 ? 5 : resto >= 2 ? 2 : 1;
    return nice * mag;
  };

  const etiquetaArea = {
    id: "etiquetaArea",
    afterDatasetsDraw(chart) {
      const texto = chart.canvas.parentElement?.dataset.area;
      if (!texto) {
        return;
      }
      const { ctx, chartArea } = chart;
      ctx.save();
      ctx.fillStyle = "#1e293b";
      ctx.font = "600 14px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(
        texto,
        (chartArea.left + chartArea.right) / 2,
        (chartArea.top + chartArea.bottom) / 2,
      );
      ctx.restore();
    },
  };

  const renderGrafico = (root) => {
    const canvas = root.querySelector("canvas");
    if (!canvas || typeof Chart === "undefined") {
      return;
    }

    const xs = JSON.parse(root.dataset.xs || "[]");
    const ys = JSON.parse(root.dataset.ys || "[]");
    const areaXs = JSON.parse(root.dataset.areaXs || "[]");
    const areaYs = JSON.parse(root.dataset.areaYs || "[]");
    const placesRaw = Number(root.dataset.places);
    const places = Number.isInteger(placesRaw) && placesRaw >= 0 ? placesRaw : 4;

    const curva = xs
      .map((x, i) => ({ x, y: ys[i] }))
      .filter((punto) => punto.y !== null);
    const area = areaXs.map((x, i) => ({ x, y: areaYs[i] }));
    const ordenadas = [...curva, ...area].map((punto) => punto.y);
    const xMin = xs.length ? xs[0] : 0;
    const xMax = xs.length ? xs[xs.length - 1] : 1;
    let yMin = ordenadas.length ? Math.min(0, ...ordenadas) : -1;
    let yMax = ordenadas.length ? Math.max(0, ...ordenadas) : 1;
    const margen = (yMax - yMin) * 0.08 || 1;
    yMin -= margen;
    yMax += margen;

    if (chart) {
      chart.destroy();
    }

    chart = new Chart(canvas, {
      type: "line",
      data: {
        datasets: [
          {
            label: "Área aproximada",
            data: area,
            borderColor: "rgba(37, 99, 235, 0.45)",
            backgroundColor: "rgba(37, 99, 235, 0.18)",
            pointRadius: 0,
            borderWidth: 1,
            fill: "origin",
            tension: 0,
          },
          {
            label: "f(x)",
            data: curva,
            borderColor: "#2563eb",
            backgroundColor: "transparent",
            pointRadius: 0,
            borderWidth: 2,
            tension: 0.15,
          },
        ],
      },
      plugins: [etiquetaArea],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, labels: { color: "#334155" } },
          tooltip: {
            callbacks: {
              label(ctx) {
                const { x, y } = ctx.parsed;
                return `f(${formatDecimal(x, places)}) = ${formatDecimal(y, places)}`;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            min: xMin,
            max: xMax,
            title: { display: true, text: "x" },
            ticks: { stepSize: pasoCuadricula(xMax - xMin), color: "#64748b" },
            grid: { color: colorEje, lineWidth: grosorEje },
            border: { display: false },
          },
          y: {
            type: "linear",
            min: yMin,
            max: yMax,
            title: { display: true, text: "y" },
            ticks: { stepSize: pasoCuadricula(yMax - yMin), color: "#64748b" },
            grid: { color: colorEje, lineWidth: grosorEje },
            border: { display: false },
          },
        },
      },
    });
  };

  const buscarYRenderizar = () => {
    const root = document.querySelector("[data-grafico]");
    if (!root) {
      if (chart) {
        chart.destroy();
        chart = undefined;
      }
      return;
    }
    requestAnimationFrame(() => {
      renderGrafico(root);
      requestAnimationFrame(() => chart?.resize());
    });
  };

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
  document.addEventListener("htmx:oobAfterSwap", () => {
    syncSubintervalos();
    buscarYRenderizar();
  });
  document.addEventListener("DOMContentLoaded", () => {
    syncSubintervalos();
    buscarYRenderizar();
  });
})();
