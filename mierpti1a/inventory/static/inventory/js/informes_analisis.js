$(document).ready(function () {
    const ctx1 = document.getElementById('grafico-principal').getContext('2d');
    const ctx2 = document.getElementById('grafico-secundario').getContext('2d');
    let chart1, chart2;

    // Variable para almacenar el mapeo de ID a nombre de producto
    let idToName = {};

    // Obtener el token JWT
    function getAuthToken() {
        return localStorage.getItem('auth_token');
    }

    // Obtener CSRF token
    function getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : null;
    }

    // Configurar CSRF para AJAX
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            const csrftoken = getCSRFToken();
            if (csrftoken) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    

    // Función para cargar los productos desde el POS (solo al inicio)
    function cargarProductos() {
        $.ajax({
            url: '/pos/api_productos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() },
            success: function(response) {
                response.productos.forEach(item => {
                    idToName[item.id] = item.nombre;  // Guardar nombre del producto por ID
                });
            },
            error: function(error) {
                console.error('Error al cargar los productos:', error);
            }
        });
    }

    // Función para cargar movimientos filtrados por fechas
    function cargarMovimientos(tipo) {
        let url = '/inventory/obtener_movimientos/';  // Endpoint para movimientos
        const fechaInicio = $('#fecha-inicio').val();
        const fechaFin = $('#fecha-fin').val();

        // Crear objeto de parámetros con el rango de fechas
        const params = {
            tipo: tipo,
            fecha_inicio: fechaInicio || null,  // Si no hay fecha, se envía null
            fecha_fin: fechaFin || null
        };

        $.ajax({
            url: url,
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() },
            data: params,  // Enviar parámetros de fecha al backend
            success: function(response) {
                const movimientos = response.movimientos;
                const movimientosFiltrados = filtrarPorFechas(movimientos, fechaInicio, fechaFin);
                const movimientosAgrupados = agruparMovimientos(movimientosFiltrados);
                generarGraficos(movimientosAgrupados, tipo);
                generarTabla(movimientosFiltrados, tipo);
            },
            error: function(error) {
                console.error('Error al cargar los movimientos:', error);
            }
        });
    }

    // Función para filtrar movimientos por rango de fechas
    function filtrarPorFechas(movimientos, fechaInicio, fechaFin) {
        if (!fechaInicio && !fechaFin) return movimientos;  // Si no hay fechas, no se filtra

        // Convertir fechas de inicio y fin a objetos Date
        if (fechaInicio) {
            const [year, month, day] = fechaInicio.split('-');
            fechaInicio = new Date(year, month - 1, day, 0, 0, 0);  // Fecha de inicio a las 00:00:00
        }
        
        if (fechaFin) {
            const [year, month, day] = fechaFin.split('-');
            fechaFin = new Date(year, month - 1, day, 23, 59, 59);  // Fecha de fin a las 23:59:59
        }

        return movimientos.filter(item => {
            const fechaMovimiento = new Date(item.fecha);  // Fecha del movimiento
            return (!fechaInicio || fechaMovimiento >= fechaInicio) && 
                (!fechaFin || fechaMovimiento <= fechaFin);
        });
    }


    // Función para agrupar movimientos por producto y sumar cantidades
    function agruparMovimientos(movimientos) {
        const movimientosAgrupados = {};

        movimientos.forEach(item => {
            if (!movimientosAgrupados[item.producto_id]) {
                movimientosAgrupados[item.producto_id] = 0;
            }
            movimientosAgrupados[item.producto_id] += item.cantidad;
        });

        return Object.keys(movimientosAgrupados).map(id => ({
            id: id,
            nombre: idToName[id],
            cantidad: movimientosAgrupados[id]
        }));
    }

    // Función para obtener el inventario actual (sin filtro de fecha)
    function cargarInventario() {
        $.ajax({
            url: '/pos/api_productos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() },
            success: function(response) {
                const inventario = response.productos.map(item => ({
                    id: item.id,
                    nombre: item.nombre,
                    stock: item.stock
                }));
                generarGraficos(inventario, 'inventario');
                generarTabla(inventario, 'inventario');
            },
            error: function(error) {
                console.error('Error al cargar el inventario:', error);
            }
        });
    }

    // Función para generar los gráficos
function generarGraficos(datos, tipo) {
    const labels = datos.map(item => item.nombre || idToName[item.producto_id]);
    const cantidades = datos.map(item => item.cantidad || item.stock);

    // Definir los colores que se pueden usar para el gráfico de tipo pie
    const colores = [
        'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(99, 255, 132, 0.2)', 'rgba(54, 235, 255, 0.2)',
        'rgba(255, 99, 64, 0.2)', 'rgba(132, 99, 255, 0.2)', 'rgba(255, 159, 132, 0.2)'
    ];

    // Destruir gráficos anteriores
    if (chart1) chart1.destroy();
    if (chart2) chart2.destroy();

    // Gráfico principal (Barra)
    chart1 = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Cantidad por Producto (${tipo})`,
                data: cantidades,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',  // Color de fondo para las barras
                borderColor: 'rgba(75, 192, 192, 1)',      // Color de borde para las barras
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' }
            }
        }
    });

    // Gráfico secundario (Pie)
    chart2 = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: `Proporción por Producto (${tipo})`,
                data: cantidades,
                // Usar los colores definidos en la lista
                backgroundColor: colores.slice(0, datos.length),  // Asignar colores según la cantidad de datos
                borderColor: colores.slice(0, datos.length).map(color => color.replace('0.2', '1')),  // Colores de borde
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' }
            }
        }
    });
}


    // Función para generar la tabla de resumen
    function generarTabla(datos, tipo) {
        const rows = datos.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.nombre || idToName[item.producto_id]}</td>
                <td>${item.cantidad || item.stock}</td>
                <td>${tipo === 'inventario' ? 'Stock' : (item.tipo || 'N/A')}</td>
                <td>${item.fecha || 'N/A'}</td>
            </tr>
        `).join('');
        $('#reporte-tabla').html(rows);
    }

    // Cargar productos al inicio para el mapeo
    cargarProductos();

    // Generar informe inicial con el inventario
    cargarInventario();  // Mostrar inventario actual al cargar la página

    // Manejar cambio de tipo de reporte
    $('#tipo-reporte').change(function () {
        const tipo = $(this).val();
        if (tipo === 'inventario') {
            cargarInventario();  // Si es Inventario Actual, mostrar inventario
        } else if (tipo === 'entradas') {
            cargarMovimientos('entrada');  // Si es Entradas, cargar entradas
        } else if (tipo === 'salidas') {
            cargarMovimientos('salida');  // Si es Salidas, cargar salidas
        }
    });

    // Generar reporte al hacer click en el botón
    $('#generar-reporte').click(function (e) {
        e.preventDefault();
        const tipo = $('#tipo-reporte').val();
        if (tipo === 'inventario') {
            cargarInventario();
        } else if (tipo === 'entradas') {
            cargarMovimientos('entrada');
        } else if (tipo === 'salidas') {
            cargarMovimientos('salida');
        }
    });
});
