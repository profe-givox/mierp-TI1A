document.addEventListener('DOMContentLoaded', function () {
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const codigoField = document.getElementById('codigo');
    const nombreField = document.getElementById('nombre');
    const deleteButton = document.querySelector('.btn-submit'); // Botón de eliminación

    let productoId = null; // Variable para almacenar el ID del producto

    searchButton.addEventListener('click', function () {
        const searchQuery = searchInput.value.trim();
        
        if (searchQuery) {
            fetch(`/inventory/buscar_producto/?search=${searchQuery}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);  // Muestra una alerta si el producto no se encuentra
                        codigoField.value = '';  // Limpia los campos
                        nombreField.value = '';
                        productoId = null;
                    } else {
                        // Llenar los campos con los datos del producto encontrado
                        codigoField.value = data.producto.codigo_producto;
                        nombreField.value = data.producto.nombre_producto;
                        productoId = data.producto.id; // Almacena el ID del producto para usarlo al eliminar
                    }
                })
                .catch(error => {
                    console.error('Error al realizar la búsqueda:', error);
                    alert('Error al realizar la búsqueda');
                });
        } else {
            alert('Por favor, ingresa un código o nombre para buscar.');
        }
    });

    deleteButton.addEventListener('click', function (event) {
        event.preventDefault();

        // Confirmación de eliminación
        if (productoId) {
            const confirmacion = confirm(`¿Estás seguro de que deseas eliminar el producto con código ${codigoField.value}?`);
            if (confirmacion) {
                fetch(`/inventory/api/productos/${productoId}/eliminar/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        alert(data.mensaje); // Mensaje de éxito
                        // Limpia los campos después de eliminar
                        codigoField.value = '';
                        nombreField.value = '';
                        searchInput.value = '';
                        productoId = null; // Reinicia el ID del producto
                    }
                })
                .catch(error => {
                    console.error('Error al eliminar el producto:', error);
                    alert('Error al eliminar el producto');
                });
            }
        } else {
            alert('No se ha seleccionado un producto para eliminar.');
        }
    });
});
