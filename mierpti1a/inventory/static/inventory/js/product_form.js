document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('product-form');
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');

    // Verificar que el token CSRF exista antes de usarlo
    if (!csrfTokenElement) {
        console.error("Error: No se encontró el token CSRF.");
        alert("Error: No se encontró el token CSRF. Por favor, recargue la página.");
        return;  // Salir si no se encuentra el token CSRF
    }

    const csrfToken = csrfTokenElement.value;

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Evitar el envío del formulario tradicional

        const formData = {
            codigo_producto: document.getElementById('codigo_producto').value,
            nombre: document.getElementById('nombre_producto').value,
            proveedor: document.getElementById('proveedor').value,
            categoria: document.getElementById('categoria').value,
            cantidad_por_unidad: document.getElementById('cantidad_por_unidad').value,
            precio_unitario: document.getElementById('precio_unitario').value,
            unidades_en_existencia: document.getElementById('unidades_en_existencia').value,
            unidades_en_pedido: document.getElementById('unidades_en_pedido').value,
            nivel_reorden: document.getElementById('nivel_reorden').value,
            almacen: document.getElementById('almacen').value,
            estante: document.getElementById('estante').value,
            lugar: document.getElementById('lugar').value
        };

        fetch('/inventory/api/productos/nuevo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);  // Mostrar mensaje de error en una alerta
            } else {
                alert('Producto creado exitosamente');
                form.reset();  // Limpiar el formulario después de agregar
            }
        })
        .catch(error => {
            console.error('Error al crear el producto:', error);
            alert('Error al crear el producto');
        });
    });
});
