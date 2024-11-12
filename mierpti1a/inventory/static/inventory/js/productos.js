$(document).ready(function() {
    // Función para cargar productos mediante AJAX
    function cargarProductos(filtro = '') {
        $.ajax({
            url: '/inventory/api/productos/',
            type: 'GET',
            data: { search: filtro },
            success: function(response) {
                const productos = response.productos;
                let productosHtml = '';

                if (productos.length > 0) {
                    productos.forEach(producto => {
                        productosHtml += `
                            <tr>
                                <td>${producto.codigo_producto || 'SIN_CODIGO'}</td>
                                <td>${producto.nombre_producto}</td>
                                <td>${producto.proveedor}</td>
                                <td>${producto.categoria}</td>
                                <td>${producto.cantidad_por_unidad}</td>
                                <td>$${producto.precio_unitario}</td>
                                <td>${producto.unidades_en_existencia}</td>
                                <td>${producto.unidades_en_pedido}</td>
                                <td>${producto.nivel_reorden}</td>
                                <td>${producto.almacen}</td>
                                <td>${producto.ubicacion_almacen}</td>
                                <td>${producto.estante}</td>
                                <td>${producto.lugar}</td>
                            </tr>`;
                    });
                } else {
                    productosHtml = `
                        <tr>
                            <td colspan="13" style="text-align: center;">No hay productos disponibles</td>
                        </tr>`;
                }
                $('#productos-list').html(productosHtml);
            },
            error: function(error) {
                console.error('Error al cargar productos:', error);
            }
        });
    }

    // Llamar a la función para cargar productos cuando la página esté lista
    cargarProductos();

    // Función de búsqueda al hacer clic en el botón de búsqueda
    $('#search-button').click(function() {
        const filtro = $('#search-input').val();
        cargarProductos(filtro);
    });

    // Función de búsqueda al presionar "Enter" en el campo de entrada
    $('#search-input').keypress(function(e) {
        if (e.which === 13) {  // Código de la tecla Enter
            const filtro = $(this).val();
            cargarProductos(filtro);
        }
    });
});
