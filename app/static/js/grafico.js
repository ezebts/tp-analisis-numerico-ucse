(() => {
  let chart;

  const pasoCuadricula = (span, marcas = 8) => {
    const crudo = Math.abs(span) / marcas || 1;
    const mag = 10 ** Math.floor(Math.log10(crudo));
    const resto = crudo / mag;
    const nice = resto >= 5 ? 5 : resto >= 2 ? 2 : 1;
    return nice * mag;
  };

  const colorEje = (ctx) => (ctx.tick.value === 0 ? "#94a3b8" : "#e2e8f0");
  const grosorEje = (ctx) => (ctx.tick.value === 0 ? 1.5 : 1);

  const escalaUnoAUno = {
    id: "escalaUnoAUno",
    afterLayout(chart) {
      if (chart.$ajustandoEscala) {
        return;
      }
      const x = chart.scales.x;
      const y = chart.scales.y;
      if (!x?.width || !y?.height) {
        return;
      }
      const xSpan = x.max - x.min;
      if (!(xSpan > 0)) {
        return;
      }
      const unidad = xSpan / x.width;
      const ySpan = unidad * y.height;
      const yMin = -ySpan / 2;
      const yMax = ySpan / 2;
      if (
        Math.abs((y.options.min ?? y.min) - yMin) < unidad * 0.01 &&
        Math.abs((y.options.max ?? y.max) - yMax) < unidad * 0.01
      ) {
        return;
      }
      y.options.min = yMin;
      y.options.max = yMax;
      chart.$ajustandoEscala = true;
      chart.update("none");
      chart.$ajustandoEscala = false;
    },
  };

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
    const xMin = xs.length ? xs[0] : -1;
    const xMax = xs.length ? xs[xs.length - 1] : 1;
    const xSpan = xMax - xMin || 2;
    const paso = pasoCuadricula(xSpan);

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
      plugins: [escalaUnoAUno],
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
            min: xMin,
            max: xMax,
            title: { display: true, text: "x" },
            ticks: { stepSize: paso, color: "#64748b" },
            grid: { color: colorEje, lineWidth: grosorEje },
            border: { display: false },
          },
          y: {
            type: "linear",
            min: -xSpan / 2,
            max: xSpan / 2,
            title: { display: true, text: "f(x)" },
            ticks: { stepSize: paso, color: "#64748b" },
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
