document.getElementById("search-button").addEventListener("click", function () {
    const searchQuery = document.getElementById("search-input").value.trim();
    if (searchQuery) {
        fetch(`/inventory/buscar_producto/?search=${searchQuery}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Producto no encontrado");
                } else {
                    document.getElementById("codigo_producto").value = data.producto.codigo_producto;
                    document.getElementById("nombre_producto").value = data.producto.nombre_producto;
                    document.getElementById("proveedor").value = data.producto.proveedor;
                    document.getElementById("categoria").value = data.producto.categoria;
                    document.getElementById("cantidad_por_unidad").value = data.producto.cantidad_por_unidad;
                    document.getElementById("precio_unitario").value = data.producto.precio_unitario;
                    document.getElementById("unidades_en_existencia").value = data.producto.unidades_en_existencia;
                    document.getElementById("unidades_en_pedido").value = data.producto.unidades_en_pedido;
                    document.getElementById("nivel_reorden").value = data.producto.nivel_reorden;

                    const almacenSelect = document.getElementById("almacen");
                    for (let option of almacenSelect.options) {
                        if (option.text === data.producto.almacen) {
                            option.selected = true;
                            break;
                        }
                    }

                    document.getElementById("estante").value = data.producto.estante;
                    document.getElementById("lugar").value = data.producto.lugar;

                    // Guardar el ID del producto en una variable global
                    window.productoId = data.producto.id;
                }
            })
            .catch(error => {
                console.error("Error al realizar la búsqueda:", error);
                alert("Error al realizar la búsqueda");
            });
    } else {
        alert("Por favor, ingresa un código o nombre para buscar.");
    }
});

document.getElementById("edit-product-form").addEventListener("submit", function (event) {
    event.preventDefault();
    if (window.productoId) {
        const updatedData = {
            codigo_producto: document.getElementById("codigo_producto").value,
            nombre: document.getElementById("nombre_producto").value,
            proveedor: document.getElementById("proveedor").value,
            categoria: document.getElementById("categoria").value,
            cantidad_por_unidad: document.getElementById("cantidad_por_unidad").value,
            precio_unitario: document.getElementById("precio_unitario").value,
            unidades_en_existencia: document.getElementById("unidades_en_existencia").value,
            unidades_en_pedido: document.getElementById("unidades_en_pedido").value,
            nivel_reorden: document.getElementById("nivel_reorden").value,
            almacen: document.getElementById("almacen").value,
            estante: document.getElementById("estante").value,
            lugar: document.getElementById("lugar").value
        };

        fetch(`/inventory/api/productos/${window.productoId}/actualizar/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(updatedData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error al actualizar el producto: " + data.error);
            } else {
                alert("Producto actualizado exitosamente");
            }
        })
        .catch(error => {
            console.error("Error al actualizar el producto:", error);
            alert("Error al actualizar el producto");
        });
    } else {
        alert("No se ha seleccionado un producto para actualizar.");
    }
});
