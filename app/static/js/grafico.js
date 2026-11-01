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

  const leerLista = (texto) => JSON.parse(texto || "[]");

  const leerNumero = (texto) => {
    if (texto === undefined || texto === "") {
      return null;
    }
    const numero = Number(texto);
    return Number.isFinite(numero) ? numero : null;
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

  const cortarSaltos = (puntos) => {
    const magnitudes = puntos
      .filter((punto) => punto.y !== null)
      .map((punto) => Math.abs(punto.y))
      .sort((a, b) => a - b);
    const mediana = magnitudes.length ? magnitudes[Math.floor(magnitudes.length / 2)] : 0;
    const umbral = Math.max(mediana * 8, 1);
    const cortada = [];
    for (const punto of puntos) {
      const anterior = cortada.at(-1);
      const salto =
        anterior &&
        anterior.y !== null &&
        punto.y !== null &&
        anterior.y * punto.y < 0 &&
        Math.abs(anterior.y) > umbral &&
        Math.abs(punto.y) > umbral;
      if (salto) {
        cortada.push({ x: (anterior.x + punto.x) / 2, y: null });
      }
      cortada.push(punto);
    }
    return cortada;
  };

  const destruir = () => {
    if (chart) {
      chart.destroy();
      chart = undefined;
    }
  };

  const renderGrafico = (root) => {
    const canvas = root.querySelector("canvas");
    if (!canvas || typeof Chart === "undefined") {
      return;
    }

    const placesRaw = Number(root.dataset.places);
    const places = Number.isInteger(placesRaw) && placesRaw >= 0 ? placesRaw : 4;
    const unoAUno = root.dataset.escala === "uno-a-uno";
    const mismaEscala = root.dataset.escala === "igual";
    const incluyeCero = root.hasAttribute("data-incluye-cero");
    const etiquetaCurva = root.dataset.curva || "f(x)";

    const xs = leerLista(root.dataset.xs);
    const ys = leerLista(root.dataset.ys);
    const curva = cortarSaltos(xs.map((x, i) => ({ x, y: ys[i] })));
    const hayCurva = curva.some((punto) => punto.y !== null);
    const puntosX = leerLista(root.dataset.puntosX);
    const puntosY = leerLista(root.dataset.puntosY);
    const puntos = puntosX.map((x, i) => ({ x, y: puntosY[i] }));
    const areaXs = leerLista(root.dataset.areaXs);
    const areaYs = leerLista(root.dataset.areaYs);
    const area = areaXs.map((x, i) => ({ x, y: areaYs[i] }));
    const raiz = leerNumero(root.dataset.raiz);

    const xMin = leerNumero(root.dataset.xmin) ?? (xs.length ? xs[0] : -1);
    const xMax = leerNumero(root.dataset.xmax) ?? (xs.length ? xs[xs.length - 1] : 1);
    const xSpan = xMax - xMin || 2;

    const datasets = [];
    if (area.length) {
      datasets.push({
        label: "Área aproximada",
        data: area,
        borderColor: "rgba(37, 99, 235, 0.45)",
        backgroundColor: "rgba(37, 99, 235, 0.18)",
        pointRadius: 0,
        borderWidth: 1,
        fill: "origin",
        tension: 0,
        order: 3,
      });
    }
    if (hayCurva) {
      datasets.push({
        label: etiquetaCurva,
        data: curva,
        borderColor: "#2563eb",
        backgroundColor: "transparent",
        pointRadius: 0,
        borderWidth: 2,
        tension: 0.15,
        spanGaps: false,
        order: 2,
      });
    }
    if (puntos.length) {
      datasets.push({
        type: "scatter",
        label: "Puntos",
        data: puntos,
        backgroundColor: "#0f172a",
        pointRadius: 5,
        order: 1,
      });
    }
    if (raiz !== null) {
      datasets.push({
        label: "Raíz",
        data: [{ x: raiz, y: 0 }],
        showLine: false,
        pointRadius: 6,
        pointBackgroundColor: "#0f172a",
        pointBorderColor: "#0f172a",
        order: 0,
      });
    }

    const escalas = {
      x: {
        type: "linear",
        min: xMin,
        max: xMax,
        title: { display: true, text: root.dataset.tituloX || "x", color: "#64748b" },
        ticks: { color: "#64748b" },
        grid: { color: colorEje, lineWidth: grosorEje },
        border: { display: false },
      },
      y: {
        type: "linear",
        title: { display: true, text: root.dataset.tituloY || "y", color: "#64748b" },
        ticks: { color: "#64748b" },
        grid: { color: colorEje, lineWidth: grosorEje },
        border: { display: false },
      },
    };

    if (unoAUno) {
      const paso = pasoCuadricula(xSpan);
      escalas.x.ticks.stepSize = paso;
      escalas.y.min = -xSpan / 2;
      escalas.y.max = xSpan / 2;
      escalas.y.ticks.stepSize = paso;
    } else if (incluyeCero) {
      const ordenadas = [...curva, ...area]
        .filter((punto) => punto.y !== null && punto.x >= xMin && punto.x <= xMax)
        .map((punto) => punto.y);
      let yMin = ordenadas.length ? Math.min(0, ...ordenadas) : -1;
      let yMax = ordenadas.length ? Math.max(0, ...ordenadas) : 1;
      const margen = (yMax - yMin) * 0.08 || 1;
      yMin -= margen;
      yMax += margen;
      escalas.x.ticks.stepSize = pasoCuadricula(xSpan);
      escalas.y.min = yMin;
      escalas.y.max = yMax;
      escalas.y.ticks.stepSize = pasoCuadricula(yMax - yMin);
    } else if (mismaEscala) {
      const paso = pasoCuadricula(xSpan);
      escalas.x.ticks.stepSize = paso;
      escalas.y.min = xMin;
      escalas.y.max = xMax;
      escalas.y.ticks.stepSize = paso;
    }

    destruir();

    const plugins = [etiquetasPuntos, etiquetaArea];
    if (unoAUno) {
      plugins.push(escalaUnoAUno);
    }

    chart = new Chart(canvas, {
      type: "line",
      data: { datasets },
      plugins,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        resizeDelay: 0,
        layout: { padding: 0 },
        plugins: {
          legend: { display: true, labels: { color: "#334155" } },
          tooltip: {
            callbacks: {
              label(ctx) {
                const { x, y } = ctx.parsed;
                const nombre = ctx.dataset.label;
                if (nombre === "Raíz") {
                  return `Raíz: f(${formatDecimal(x, places)}) = ${formatDecimal(y, places)}`;
                }
                if (nombre === "Puntos") {
                  return `P${ctx.dataIndex + 1} (${formatDecimal(x)}, ${formatDecimal(y)})`;
                }
                if (nombre === "Curva de ajuste") {
                  return `y = ${formatDecimal(y)}`;
                }
                return `f(${formatDecimal(x, places)}) = ${formatDecimal(y, places)}`;
              },
            },
          },
        },
        scales: escalas,
      },
    });
  };

  const buscarYRenderizar = () => {
    const root = document.querySelector("[data-grafico]");
    if (!root) {
      destruir();
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
