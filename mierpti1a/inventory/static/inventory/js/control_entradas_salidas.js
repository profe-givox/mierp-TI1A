$(document).ready(function () {
    let movimientosCargados = [];
    let productos = {};

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


   
    


    // Sanitizar texto para prevenir XSS
    function escapeHTML(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // Cargar productos
    function cargarProductos() {
        return $.ajax({
            url: '/pos/api_productos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() },
            success: function (response) {
                productos = response.productos.reduce((map, producto) => {
                    map[producto.id] = escapeHTML(producto.nombre);
                    return map;
                }, {});
            },
            error: function (error) {
                console.error('Error al cargar los productos:', error);
                showToast('Error al cargar los productos.', 'error');
            }
        });
    }

    // Cargar movimientos
    function cargarMovimientos(filtro = '', tipoFiltro = 'todo') {
        $.ajax({
            url: '/inventory/obtener_movimientos/',
            type: 'GET',
            headers: { 'Authorization': 'Bearer ' + getAuthToken() },
            success: function (response) {
                movimientosCargados = response.movimientos.map(mov => ({
                    ...mov,
                    producto_nombre: productos[mov.producto_id] || `Producto ${mov.producto_id}`
                }));

                let movimientosFiltrados = movimientosCargados;

                if (filtro) {
                    movimientosFiltrados = movimientosFiltrados.filter(mov =>
                        mov.producto_nombre.toLowerCase().includes(filtro.toLowerCase()) ||
                        new Date(mov.fecha).toLocaleString().includes(filtro)
                    );
                }

                if (tipoFiltro !== 'todo') {
                    movimientosFiltrados = movimientosFiltrados.filter(mov =>
                        mov.tipo.trim().toLowerCase() === tipoFiltro.trim().toLowerCase()
                    );
                }

                const movimientosHtml = movimientosFiltrados.map(mov => `
                    <tr data-id="${escapeHTML(mov.id)}" class="ver-detalles">
                        <td>${escapeHTML(mov.id)}</td>
                        <td>${escapeHTML(mov.producto_nombre)}</td>
                        <td>${escapeHTML(mov.tipo.charAt(0).toUpperCase() + mov.tipo.slice(1))}</td>
                        <td>${escapeHTML(mov.cantidad)}</td>
                        <td>${escapeHTML(new Date(mov.fecha).toLocaleString())}</td>
                        <td>${escapeHTML(mov.sucursal_id)}</td>
                    </tr>
                `).join('');

                $('#movimientos-list').html(movimientosHtml);
            },
            error: function (error) {
                console.error('Error al cargar los movimientos:', error);
                showToast('Error al cargar los movimientos.', 'error');
            }
        });
    }

    // Mostrar alertas/toasts
    function showToast(message, type = 'success') {
        const toastClass = {
            success: 'alert-success',
            error: 'alert-danger',
            warning: 'alert-warning'
        }[type] || 'alert-primary';

        const toastHtml = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        $('#toast-container').append(toastHtml);
        const toast = $('#toast-container .toast').last();
        toast.toast({ delay: 3000 });
        toast.toast('show');

        setTimeout(() => {
            toast.remove();
        }, 3500);
    }

    // Inicializar productos y movimientos
    cargarProductos().then(() => {
        cargarMovimientos();
    });

    // Buscar y filtrar movimientos
    $('#search-form').submit(function (e) {
        e.preventDefault();
        const filtro = $('#search-input').val();
        const tipoFiltro = $('#tipo-filtro').val();
        cargarMovimientos(filtro, tipoFiltro);
    });

    // Actualizar tabla al cambiar el select de filtro
    $('#tipo-filtro').change(function () {
        const filtro = $('#search-input').val();
        const tipoFiltro = $(this).val();
        cargarMovimientos(filtro, tipoFiltro); // Recargar movimientos con los nuevos filtros
    });

    

    // Resetear filtros
    $('#reset-button').click(function () {
        $('#search-input').val('');
        $('#tipo-filtro').val('todo');
        cargarMovimientos();
    });

    // Mostrar detalles
    $(document).on('click', '.ver-detalles', function () {
        const id = $(this).data('id');
        const movimiento = movimientosCargados.find(mov => mov.id === id);

        if (movimiento) {
            $('#detalle-producto').text(movimiento.producto_nombre);
            $('#detalle-tipo').text(movimiento.tipo.charAt(0).toUpperCase() + movimiento.tipo.slice(1));
            $('#detalle-cantidad').text(movimiento.cantidad);
            $('#detalle-fecha').text(new Date(movimiento.fecha).toLocaleString());
            $('#detalle-sucursal').text(movimiento.sucursal_id);
            $('#detallesMovimientoModal').modal('show');
        } else {
            showToast('Movimiento no encontrado.', 'warning');
        }
    });
});
