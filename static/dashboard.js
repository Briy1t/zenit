// Aumentar resolución interna del canvas (más nítido, NO más grande)
Chart.defaults.devicePixelRatio = 2;

document.addEventListener("DOMContentLoaded", () => {

    /* -------------------------
       PLUGIN TEXTO EN EL CENTRO
    ------------------------- */
    const centerTextPlugin = {
        id: "centerText",
        afterDraw(chart) {
            const { ctx, chartArea: { width, height } } = chart;
            const valor = chart.config.data.datasets[0].data[0];
            ctx.save();
            ctx.font = "bold 24px 'Segoe UI'";
            ctx.fillStyle = "#000";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(valor + "%", width / 2, height / 2);
            ctx.restore();
        }
    };

    /* -------------------------
       GAUGE DEL DÍA
    ------------------------- */
    const gauge = document.getElementById("gaugeDia");
    if (gauge) {
        const porcentaje = parseFloat(gauge.dataset.zenit);

        new Chart(gauge, {
            type: "doughnut",
            data: {
                datasets: [{
                    data: [porcentaje, 100 - porcentaje],
                    backgroundColor: ["#00d4ff", "rgba(255,255,255,0.15)"],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: "70%",
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            },
            plugins: [centerTextPlugin]
        });
    }

    /* -------------------------
       GRÁFICO SEMANAL 
    ------------------------- */

    const semana = document.getElementById("graficoSemana");
    if (semana) {

        const valores = JSON.parse(semana.dataset.valores.replace(/'/g, '"'));
        const dias = JSON.parse(semana.dataset.dias.replace(/'/g, '"'));

        const ctx = semana.getContext("2d");

        // Degradado suave
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, "rgba(0, 212, 255, 0.25)");
        gradient.addColorStop(1, "rgba(0, 212, 255, 0)");

        new Chart(semana, {
            type: "line",
            data: {
                labels: dias,
                datasets: [{
                    label: "Energía (%)",
                    data: valores,
                    borderColor: "#00a0c8",
                    backgroundColor: gradient,
                    borderWidth: 3,
                    tension: 0.45,
                    pointRadius: 5,
                    pointBackgroundColor: "#00a0c8",
                    pointBorderColor: "#ffffff",
                    pointBorderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: false,     
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 20,
                        bottom: 10
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "rgba(0,0,0,0.8)",
                        titleColor: "#fff",
                        bodyColor: "#fff",
                        padding: 10,
                        displayColors: false,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: {
                            color: "rgba(0,0,0,0.1)"
                        },
                        ticks: {
                            color: "#000000",
                            font: { size: 13 }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: "#000000",
                            font: { size: 13 }
                        }
                    }
                }
            }
        });
    }

});
