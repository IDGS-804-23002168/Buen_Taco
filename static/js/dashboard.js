// Módulo 3 - Dashboard
document.addEventListener('DOMContentLoaded', function () {

    // Datos inyectados desde el template
    const labels = window.dashData.diasLabels;
    const data   = window.dashData.ventasDiarias;

    const ctx = document.getElementById('graficaVentas');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas ($)',
                data: data,
                backgroundColor: 'rgba(139, 58, 14, 0.75)',
                borderColor:     '#8B3A0E',
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => '$' + ctx.parsed.y.toFixed(2)
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: v => '$' + v
                    },
                    grid: { color: '#f3f4f6' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
});