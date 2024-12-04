$(document).ready(function () {
    let pedidosCargados = []; // Almacenar todos los pedidos obtenidos al inicio
    let productos = {}; // Mapa de productos por ID
    let movimientosCargados = []; // Almacenar todos los movimientos de inventario
    let pedidoIdSeleccionado = null; // Para almacenar el pedido seleccionado en el modal

    // Función para obtener el token JWT desde el localStorage
    function getAuthToken() {
        return localStorage.getItem('auth_token'); // Suponiendo que el token se guarda en localStorage
    }


    // Función para obtener el token CSRF desde las cookies
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return null;
    }

    // Configurar todas las solicitudes AJAX para incluir el CSRF token
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            const csrftoken = getCSRFToken();
            if (csrftoken) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Verificar si el usuario es administrador
    $.ajax({
        url: '/inventory/usuario_actual/', // Endpoint para verificar el usuario actual
        type: 'GET',
        headers: { 'Authorization': 'Bearer ' + getAuthToken() }, // Token JWT
        success: function (response) {
            if (!response.is_administrador) {
                alert('No tienes permiso para acceder a esta página.');
                window.location.href = '/ecar/catalogo/';
            }
        },
        error: function (xhr, status, error) {
            console.error('Error al verificar permisos:', xhr.responseText);
            alert('Ocurrió un error. Redirigiendo a la página de inicio de sesión.');
            window.location.href = '/ecar/login/';
        }
    });


    

    // Función para cargar los productos desde la API y mapearlos por ID
    function cargarProductos() {
        return $.ajax({
            url: '/pos/api_productos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() }, // Incluir el token JWT en los encabezados
            success: function (response) {
                productos = response.productos.reduce((map, producto) => {
                    map[producto.id] = escapeHTML(producto.nombre); // Sanitizar el nombre del producto
                    return map;
                }, {});
            },
            error: function (error) {
                console.error('Error al cargar los productos:', error);
            }
        });
    }

    // Función para cargar los pedidos desde el servidor
    function cargarPedidos() {
        return $.ajax({
            url: '/inventory/obtener_pedidos_completo/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() }, // Incluir el token JWT en los encabezados
            success: function (response) {
                pedidosCargados = response.pedidos.map(pedido => ({
                    ...pedido,
                    nombre_producto: productos[pedido.producto_id] || `Producto ${pedido.producto_id}`
                }));
            },
            error: function (error) {
                console.error('Error al cargar los pedidos:', error);
            }
        });
    }

    // Función para cargar los movimientos desde el servidor
    function cargarMovimientos() {
        return $.ajax({
            url: '/inventory/obtener_movimientos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() }, // Incluir el token JWT en los encabezados
            success: function (response) {
                movimientosCargados = response.movimientos;
            },
            error: function (error) {
                console.error('Error al cargar los movimientos:', error);
            }
        });
    }

    // Función para actualizar la tabla con los pedidos cargados
    function actualizarTabla(pedidos) {
        let pedidosHtml = '';

        if (pedidos.length > 0) {
            pedidos.forEach(pedido => {
                const estado = pedido.estado.charAt(0).toUpperCase() + pedido.estado.slice(1); // Capitalizar estado
                const fechaPedido = pedido.fecha_pedido || 'N/A'; // Fecha de pedido
                const movimientoSalida = movimientosCargados.find(
                    mov => mov.pedido_id === pedido.id && mov.tipo === 'salida'
                );
                const btnEntregado = pedido.estado === 'pendiente' ?
                    `<button class="btn btn-success marcar-entregado" data-id="${pedido.id}" data-producto="${pedido.nombre_producto}">Marcar como Entregado</button>` :
                    `<button class="btn btn-secondary" disabled>Entregado</button>`;
                const btnSucursal = pedido.estado === 'entregado' && !movimientoSalida ?
                    `<button class="btn btn-primary abrir-modal-sucursal" data-id="${pedido.id}" data-producto="${pedido.nombre_producto}">Mandar a Sucursal</button>` :
                    `<button class="btn btn-secondary mandar-sucursal" disabled>${movimientoSalida ? 'Enviado' : 'Mandar a Sucursal'}</button>`;

                pedidosHtml += `
                    <tr>
                        <td>${pedido.id}</td>
                        <td>${escapeHTML(pedido.nombre_producto)}</td>
                        <td>${pedido.cantidad}</td>
                        <td>${fechaPedido}</td>
                        <td>${estado}</td>
                        <td>${btnEntregado}</td>
                        <td>${btnSucursal}</td>
                    </tr>`;
                
            });
        } else {
            pedidosHtml = `
                <tr>
                    <td colspan="7" style="text-align: center;">No hay pedidos disponibles</td>
                </tr>`;
        }

        $('#pedidos-list').html(pedidosHtml); // Insertar pedidos en la tabla
    }

    // Función para sanitizar texto y prevenir XSS
    function escapeHTML(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // Función para filtrar los pedidos según búsqueda y filtros
    function filtrarPedidos() {
        const filtroTexto = $('#search-input').val().toLowerCase().trim();
        const estadoFiltro = $('#estado-filter').val();

        const pedidosFiltrados = pedidosCargados.filter(pedido => {
            const cumpleBusqueda = (pedido.nombre_producto && pedido.nombre_producto.toLowerCase().includes(filtroTexto)) ||
                pedido.producto_id.toString().includes(filtroTexto);

            let cumpleEstado = true;
            if (estadoFiltro === 'pendiente') {
                cumpleEstado = pedido.estado === 'pendiente';
            } else if (estadoFiltro === 'entregado') {
                cumpleEstado = pedido.estado === 'entregado';
            } else if (estadoFiltro === 'falta-enviar') {
                cumpleEstado = pedido.estado === 'entregado' &&
                    !movimientosCargados.find(mov => mov.pedido_id === pedido.id && mov.tipo === 'salida');
            } else if (estadoFiltro === 'enviados') {
                cumpleEstado = movimientosCargados.find(mov => mov.pedido_id === pedido.id && mov.tipo === 'salida');
            }

            return cumpleBusqueda && cumpleEstado;
        });

        actualizarTabla(pedidosFiltrados);
    }

    // Cargar productos, pedidos y movimientos
    cargarProductos().then(() => {
        Promise.all([cargarPedidos(), cargarMovimientos()]).then(() => {
            actualizarTabla(pedidosCargados);
        });
    });

    // Evento para filtrar por estado al cambiar el select
    $('#estado-filter').change(function () {
        filtrarPedidos();
    });

    // Evento para resetear búsqueda y filtro
    $('#reset-button').click(function (e) {
        e.preventDefault();
        $('#search-input').val('');
        $('#estado-filter').val('todos');
        actualizarTabla(pedidosCargados);
    });

    // Evento para búsqueda al hacer clic en "Buscar"
    $('#search-button').click(function (e) {
        const searchInput = document.getElementById('search-input');
        if (!searchInput.checkValidity()) {
            searchInput.reportValidity();
            e.preventDefault();
            return;
        }

        e.preventDefault();
        filtrarPedidos();
    });

    // Abrir el modal de confirmación para marcar como entregado
    $(document).on('click', '.marcar-entregado', function () {
        pedidoIdSeleccionado = $(this).data('id');
        const producto = $(this).data('producto');
        $('#confirmacionTexto').text(`¿Estás seguro de que el pedido de "${producto}" ya ha sido entregado?`);
        $('#confirmacionModal').modal('show');
    });

    // Confirmar la entrega del pedido y registrar la entrada
    $('.confirmar-entregado').click(function () {
        if (pedidoIdSeleccionado !== null) {
            $.ajax({
                url: `/inventory/marcar_entregado/${pedidoIdSeleccionado}/`,
                type: 'POST',
                headers: { 
                    'Authorization': 'Bearer ' + getAuthToken() // Incluir el token JWT en los encabezados
                },
                success: function (response) {
                    alert(response.mensaje);
                    $('#confirmacionModal').modal('hide');

                    // Registrar la entrada en inventario
                    $.ajax({
                        url: `/inventory/registrar_entrada/${pedidoIdSeleccionado}/`,
                        type: 'POST',
                        headers: { 
                            'Authorization': 'Bearer ' + getAuthToken() // Incluir el token JWT en los encabezados
                        },
                        success: function (entradaResponse) {
                            alert(`Entrada registrada: ${entradaResponse.mensaje}`);
                            console.log('Entrada registrada:', entradaResponse);
                        },
                        error: function (error) {
                            console.error('Error al registrar entrada:', error);
                            alert('Error al registrar la entrada en el inventario.');
                        }
                    });

                    Promise.all([cargarPedidos(), cargarMovimientos()]).then(() => {
                        actualizarTabla(pedidosCargados);
                    });
                },
                error: function (xhr, status, error) {
                    console.error('Error al marcar como entregado:', error);
                    alert(`Ocurrió un error: ${xhr.responseText}`);
                }
            });
        }
    });

    // Abrir modal para mandar a sucursal
    $(document).on('click', '.abrir-modal-sucursal', function () {
        pedidoIdSeleccionado = $(this).data('id');
        const producto = $(this).data('producto');
        $('#sucursalTexto').text(`¿Estás seguro de que deseas mandar el producto "${producto}" a la sucursal?`);
        $('#mandarSucursalModal').modal('show');
    });

    // Confirmar mandar a sucursal
    $('.confirmar-mandar').click(function () {
        if (pedidoIdSeleccionado !== null) {
            // Registrar salida en inventario
            $.ajax({
                url: `/inventory/registrar_salida/${pedidoIdSeleccionado}/`,
                type: 'POST',
                headers: { 
                    'Authorization': 'Bearer ' + getAuthToken() // Incluir el token JWT en los encabezados
                },
                success: function (response) {
                    const productoId = response.producto_id;
                    const cantidadEnviar = response.cantidad;

                    if (!productoId || cantidadEnviar === undefined) {
                        alert('Error al registrar la salida: Datos incompletos devueltos por el servidor.');
                        console.error('Datos incompletos recibidos:', response);
                        return;
                    }

                    console.log('Producto ID recibido:', productoId, 'Cantidad a enviar:', cantidadEnviar);

                    // Obtener datos actuales del producto desde la API
                    $.ajax({
                        url: '/pos/api_productos/',
                        type: 'GET',
                        headers: { 
                            'Authorization': 'Bearer ' + getAuthToken() // Incluir el token JWT en los encabezados
                        },
                        success: function (productosResponse) {
                            const producto = productosResponse.productos.find(p => p.id === productoId);

                            if (producto) {
                                // Crear FormData y actualizar solo el stock
                                const formData = new FormData();
                                formData.append('nombre', producto.nombre);
                                formData.append('precio_unitario', producto.precio_unitario);
                                formData.append('descuento', producto.descuento);
                                formData.append('stock', producto.stock + cantidadEnviar); // Actualizar stock
                                formData.append('descripcion', producto.descripcion);
                                formData.append('sucursal', producto.sucursal_id);

                                // Enviar los datos actualizados a POS
                                fetch(`/pos/productos/editar_producto/${productoId}/`, {
                                    method: 'POST',
                                    headers: {
                                        'Authorization': 'Bearer ' + getAuthToken(), // Incluir el token JWT en los encabezados
                                    },
                                    body: formData,
                                })
                                    .then(editResponse => {
                                        if (editResponse.ok) {
                                            alert(`Producto enviado a sucursal y stock actualizado correctamente.`);
                                            $('#mandarSucursalModal').modal('hide');

                                            // Actualizar tablas
                                            Promise.all([cargarPedidos(), cargarMovimientos()]).then(() => {
                                                actualizarTabla(pedidosCargados);
                                            });
                                        } else {
                                            alert('Error al actualizar el stock en POS.');
                                            console.error('Error al editar el producto:', editResponse.statusText);
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error al enviar la solicitud de edición:', error);
                                        alert('Ocurrió un error al editar el producto.');
                                    });
                            } else {
                                alert('No se encontró el producto en la API de POS.');
                            }
                        },
                        error: function (error) {
                            console.error('Error al obtener datos del producto desde la API:', error);
                            alert('Error al obtener los datos del producto desde la API.');
                        },
                    });
                },
                error: function (xhr, status, error) {
                    console.error('Error al enviar a sucursal:', error);
                    alert(`Ocurrió un error: ${xhr.responseText}`);
                },
            });
        }
    });
});
