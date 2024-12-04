$(document).ready(function () {
    let productosCargados = []; // Almacenar todos los productos obtenidos al inicio
    let pedidosCargados = {};  // Almacenar el total de pedidos por producto_id

    

    // Función para cargar todos los productos al inicio
    function cargarProductosIniciales() {
        $.ajax({
            url: '/pos/api_productos/',
            type: 'GET',
            success: function (response) {
                productosCargados = response.productos; // Almacenar los productos obtenidos
                cargarPedidosEnTabla(); // Cargar la tabla con los datos de pedidos
            },
            error: function (error) {
                console.error('Error al cargar los productos:', error);
            }
        });
    }

    // Función para cargar los pedidos desde el backend
    function cargarPedidosEnTabla() {
        $.ajax({
            url: '/inventory/obtener_pedidos/', // Endpoint para obtener datos de pedidos
            type: 'GET',
            success: function (response) {
                pedidosCargados = response.pedidos; // Almacenar los totales de pedidos
                actualizarTabla(productosCargados); // Renderizar todos los productos en la tabla
            },
            error: function (error) {
                console.error('Error al cargar los pedidos:', error);
            }
        });
    }

    // Función para actualizar la tabla con los productos filtrados
    function actualizarTabla(productos) {
        let productosHtml = '';

        if (productos.length > 0) {
            productos.forEach(producto => {
                const enPedido = pedidosCargados[producto.id] || 0; // Suma total de pedidos por producto_id
                let btnClass = 'btn-success';
                let btnText = 'Hacer Pedido';

                if (enPedido > 0) {
                    btnClass = 'btn-warning'; // Naranja si está en pedido
                    btnText = 'Pedido en Espera';
                } else if (producto.stock < 10) {
                    btnClass = 'btn-danger'; // Rojo si el stock es bajo
                }

                productosHtml += `
                    <tr>
                        <td>${producto.id}</td>
                        <td>${producto.nombre}</td>
                        <td>${producto.descripcion}</td>
                        <td>$${producto.precio_unitario}</td>
                        <td>${producto.stock}</td>
                        <td>${enPedido}</td>
                        <td>${producto.descuento}%</td>
                        <td>Sucursal ${producto.sucursal_id}</td>
                        <td>
                            <button class="btn ${btnClass} hacer-pedido" 
                                    data-id="${producto.id}" 
                                    data-nombre="${producto.nombre}">
                                ${btnText}
                            </button>
                        </td>
                    </tr>`;
            });
        } else {
            productosHtml = `
                <tr>
                    <td colspan="9" style="text-align: center;">No hay productos disponibles</td>
                </tr>`;
        }

        $('#productos-list').html(productosHtml); // Insertar los productos en la tabla
    }

    // Función para filtrar los productos según búsqueda y filtros
    function filtrarProductos() {
        const filtroTexto = $('#search-input').val().toLowerCase().trim(); // Texto de búsqueda
        const stockFiltro = $('#stock-filter').val(); // Filtro de stock seleccionado

        // Filtrar los productos por texto y stock
        const productosFiltrados = productosCargados.filter(producto => {
            const cumpleBusqueda = producto.nombre.toLowerCase().includes(filtroTexto) || 
                                   producto.id.toString().includes(filtroTexto);

            let cumpleStock = true;
            if (stockFiltro === 'faltantes') {
                cumpleStock = producto.stock < 10;
            } else if (stockFiltro === 'suficientes') {
                cumpleStock = producto.stock >= 10;
            }

            return cumpleBusqueda && cumpleStock;
        });

        actualizarTabla(productosFiltrados); // Actualizar la tabla con los productos filtrados
    }

    // Llamar a la función para cargar productos al inicio
    cargarProductosIniciales();

    // Evento para búsqueda al hacer clic en "Buscar"
    $('#search-button').click(function (e) {
        e.preventDefault(); // Evitar que se recargue la página
        filtrarProductos();
    });

    // Evento para filtrar por stock al cambiar el select
    $('#stock-filter').change(function () {
        filtrarProductos();
    });

    // Evento para resetear búsqueda y filtro
    $('#reset-button').click(function (e) {
        e.preventDefault(); // Evitar que se recargue la página
        $('#search-input').val(''); // Limpiar el campo de búsqueda
        $('#stock-filter').val('todos'); // Resetear el filtro al valor predeterminado
        actualizarTabla(productosCargados); // Mostrar todos los productos
    });

    // Abrir el modal al hacer clic en "Hacer Pedido"
    $(document).on('click', '.hacer-pedido', function () {
        const productoId = $(this).data('id');
        const productoNombre = $(this).data('nombre');

        $('#productoSeleccionado').val(productoNombre); // Mostrar el nombre del producto en el modal
        $('#productoSeleccionado').data('id', productoId); // Guardar el ID del producto en el input
        $('#pedidoModal').modal('show'); // Mostrar el modal
    });

    // Enviar el formulario del pedido
    $('#pedidoForm').submit(function (e) {
        e.preventDefault(); // Evitar recargar la página
        const productoId = $('#productoSeleccionado').data('id'); // ID del producto
        const cantidad = parseInt($('#cantidadPedido').val()); // Cantidad del pedido

        if (!productoId || cantidad <= 0) {
            alert('Por favor, ingresa una cantidad válida.');
            return;
        }

        $.ajax({
            url: '/inventory/agregar_pedido/',
            type: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': getCSRFToken() }, // Obtener CSRF si aplica
            data: JSON.stringify({
                producto_id: productoId,
                cantidad: cantidad,
            }),
            success: function (response) {
                alert(response.mensaje);
                $('#pedidoModal').modal('hide');

                // Actualizar "en_pedido" después de crear el pedido
                cargarPedidosEnTabla(); // Actualizar los totales de pedidos
            },
            error: function (xhr, status, error) {
                console.error('Error al agregar el pedido:', {
                    status: status,
                    error: error,
                    response: xhr.responseText,
                });
                alert(`Ocurrió un error: ${xhr.responseText}`);
            }
        });
    });

    // Obtener CSRF token
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        const csrftokenCookie = cookies.find(row => row.trim().startsWith('csrftoken='));
        
        // Verifica si existe la cookie y si tiene un valor
        if (csrftokenCookie) {
            return csrftokenCookie.split('=')[1];  // Retorna el valor de la cookie
        } else {
            console.error('CSRF token no encontrado');
            return '';  // Retorna una cadena vacía si no se encuentra la cookie
        }
    }
});
