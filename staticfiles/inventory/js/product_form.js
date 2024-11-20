document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('product-form');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const messageContainer = document.getElementById('message-container');

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Evitar el envío del formulario tradicional
        messageContainer.innerHTML = '';  // Limpiar mensajes previos

        const formData = {
            codigo_producto: document.getElementById('codigo_producto').value,
            nombre: document.getElementById('nombre_producto').value,
            descripcion: document.getElementById('descripcion').value,
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
                showMessage(data.error, 'error');
            } else {
                showMessage('Producto creado exitosamente', 'success');
                form.reset();  // Limpiar el formulario después de agregar
            }
        })
        .catch(error => {
            console.error('Error al crear el producto:', error);
            showMessage('Error al crear el producto', 'error');
        });
    });

    function showMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(type === 'error' ? 'error-message' : 'success-message');
        messageElement.textContent = message;
        messageContainer.appendChild(messageElement);
    }
});
