document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('myChart');
    var labels = JSON.parse(document.getElementById('labels').textContent);
    var values = JSON.parse(document.getElementById('values').textContent);

    // Calcular el total de casos
    var totalCasos = values.reduce((total, valor) => total + valor, 0);
    document.getElementById('totalCasos').textContent = totalCasos;

    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Grupo de Riesgo',
                data: values,
                backgroundColor: [
                    'rgba(0, 255, 0, 0.7)', // Verde para el Caso A
                    'rgba(255, 255, 0, 0.7)', // Amarillo para el Caso B
                    'rgba(255, 0, 0, 0.7)', // Rojo para el Caso C
                ],
                borderColor: [
                    'rgba(0, 255, 0, 0.7)', // Verde para el Caso A
                    'rgba(255, 255, 0, 0.7)', // Amarillo para el Caso B
                    'rgba(255, 0, 0, 0.7)', // Rojo para el Caso C
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
