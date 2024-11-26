document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('fetchPagosBtn').addEventListener('click', function () {
        const clienteId = document.getElementById('clienteIdInput').value;
        if (clienteId) {
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || document.getElementById('csrfToken')?.value;
            debugger
            fetch('/payments/api/pagos-por-cliente/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ cliente_id: clienteId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const pagos = JSON.parse(data.pagos); // Parseamos el JSON recibido
                    const pagosBody = document.getElementById('pagosBody');

                    pagosBody.innerHTML = ''; // Limpiar contenido existente

                    pagos.forEach(pago => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${pago.fields.tipo === 'tarjeta' && pago.fields.detalle_tarjeta ? pago.fields.detalle_tarjeta.nombre_titular : (pago.fields.tipo === 'paypal' && pago.fields.detalle_paypal ? pago.fields.detalle_paypal.nombre_titular : (pago.fields.tipo === 'vale' && pago.fields.detalle_vale ? 'No aplica' : 'No disponible'))}</td>
                            <td>$${pago.fields.monto}</td>
                            <td>${pago.fields.tipo}</td>
                            <td>${new Date(pago.fields.fecha_pago).toLocaleString()}</td>
                        `;
                        pagosBody.appendChild(row);
                    });

                    // Inicializar DataTable
                    $('#pagosTable').DataTable();
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error al realizar la solicitud:', error);
                alert('Ocurrió un error al obtener los pagos.');
            });
        } else {
            alert('Por favor ingrese un ID de cliente.');
        }
    });
});
