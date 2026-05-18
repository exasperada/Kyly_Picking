const Dashboard = {
    init() {
        if (!document.querySelector("[data-dashboard]")) {
            return;
        }
        this.renderCharts();
        this.startRefresh();
    },

    renderCharts() {
        this.renderBarChart();
        this.renderPieChart();
    },

    renderBarChart() {
        const canvas = document.getElementById("chart-erros-tipo");
        if (!canvas) {
            return;
        }

        const labels = [];
        const values = [];
        document.querySelectorAll("[data-erro-tipo]").forEach((node) => {
            labels.push(node.dataset.erroTipo);
            values.push(Number(node.dataset.erroCount));
        });

        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (!values.length) {
            return;
        }

        const max = Math.max(...values, 1);
        const baseY = canvas.height - 35;
        const width = canvas.width / values.length;

        values.forEach((value, index) => {
            const barHeight = (value / max) * 180;
            const x = index * width + 26;
            const y = baseY - barHeight;

            ctx.fillStyle = "#4db6ff";
            ctx.fillRect(x, y, width - 34, barHeight);
            ctx.fillStyle = "#e5edf5";
            ctx.font = "12px sans-serif";
            ctx.fillText(String(value), x, y - 8);
            ctx.fillStyle = "#8ea5bb";
            ctx.fillText(labels[index].slice(0, 12), x, baseY + 18);
        });
    },

    renderPieChart() {
        const canvas = document.getElementById("chart-pedidos-status");
        if (!canvas) {
            return;
        }

        const values = [
            Number(document.querySelector('[data-stat="pedidos-concluidos"]')?.textContent || 0),
            Number(document.querySelector('[data-stat="pedidos-pendentes"]')?.textContent || 0),
            Number(document.querySelector('[data-stat="pedidos-em-picking"]')?.textContent || 0),
        ];
        const colors = ["#30c36b", "#f4b63d", "#4db6ff"];
        const total = values.reduce((sum, current) => sum + current, 0);
        if (!total) {
            return;
        }

        const ctx = canvas.getContext("2d");
        const radius = 100;
        let startAngle = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        values.forEach((value, index) => {
            const angle = (value / total) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(170, 150);
            ctx.arc(170, 150, radius, startAngle, startAngle + angle);
            ctx.closePath();
            ctx.fillStyle = colors[index];
            ctx.fill();
            startAngle += angle;
        });

        [["Concluido", colors[0]], ["Pendente", colors[1]], ["Em picking", colors[2]]].forEach((item, index) => {
            ctx.fillStyle = item[1];
            ctx.fillRect(340, 90 + index * 34, 18, 18);
            ctx.fillStyle = "#e5edf5";
            ctx.font = "13px sans-serif";
            ctx.fillText(item[0], 366, 104 + index * 34);
        });
    },

    startRefresh() {
        setInterval(async () => {
            try {
                const response = await fetch("/api/dashboard/");
                if (!response.ok) {
                    return;
                }
                const data = await response.json();
                document.querySelector('[data-stat="total-pedidos"]').textContent = data.stats.total_pedidos;
                document.querySelector('[data-stat="pedidos-concluidos"]').textContent = data.stats.pedidos_concluidos;
                document.querySelector('[data-stat="pedidos-pendentes"]').textContent = data.stats.pedidos_pendentes;
                document.querySelector('[data-stat="pedidos-em-picking"]').textContent = data.stats.pedidos_em_picking;
                document.querySelector('[data-stat="total-erros"]').textContent = data.stats.total_erros;
                document.querySelector('[data-stat="total-operadores"]').textContent = data.stats.total_operadores;
                this.renderPieChart();
            } catch (error) {
                console.error(error);
            }
        }, 30000);
    },
};

document.addEventListener("DOMContentLoaded", () => Dashboard.init());
