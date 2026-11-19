/* Dashboard charts (Chart.js). */

(function () {
  "use strict";

  const node = document.getElementById("chart-data");
  if (!node || typeof Chart === "undefined") return;

  const data = JSON.parse(node.textContent);

  Chart.defaults.font.family =
    "'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif";
  Chart.defaults.color = "#55665e";

  const trend = document.getElementById("trendChart");
  if (trend) {
    const ctx = trend.getContext("2d");
    const fill = ctx.createLinearGradient(0, 0, 0, 230);
    fill.addColorStop(0, "rgba(26, 122, 80, .26)");
    fill.addColorStop(1, "rgba(26, 122, 80, 0)");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.trend.labels,
        datasets: [
          {
            data: data.trend.values,
            borderColor: "#1a7a50",
            backgroundColor: fill,
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "#1a7a50",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0f3d2e",
            padding: 10,
            displayColors: false,
            callbacks: {
              label: (item) => `${item.parsed.y} booking${item.parsed.y === 1 ? "" : "s"}`,
            },
          },
        },
        scales: {
          x: { grid: { display: false }, border: { display: false } },
          y: {
            beginAtZero: true,
            ticks: { precision: 0, maxTicksLimit: 5 },
            grid: { color: "#e6ece8" },
            border: { display: false },
          },
        },
      },
    });
  }

  const status = document.getElementById("statusChart");
  if (status) {
    const colours = {
      new: "#b8860b",
      contacted: "#1b54b8",
      scheduled: "#35636f",
      completed: "#1a7a50",
      cancelled: "#a3372a",
    };

    const labels = Object.keys(data.breakdown);
    if (!labels.length) return;

    new Chart(status, {
      type: "doughnut",
      data: {
        labels: labels.map((l) => l.charAt(0).toUpperCase() + l.slice(1)),
        datasets: [
          {
            data: labels.map((l) => data.breakdown[l]),
            backgroundColor: labels.map((l) => colours[l] || "#86968e"),
            borderWidth: 2,
            borderColor: "#fff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "62%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true, padding: 14 },
          },
          tooltip: { backgroundColor: "#0f3d2e", padding: 10 },
        },
      },
    });
  }
})();
