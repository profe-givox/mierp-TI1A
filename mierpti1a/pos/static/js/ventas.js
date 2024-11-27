document.addEventListener("DOMContentLoaded", () => {
    let tablaVacia = true;
    let totalSubtotal = 0;

    const empleado = JSON.parse(localStorage.getItem('empleado'));
    document.getElementById("Empleado").innerText= "Empleado: "+empleado.nombre;
    document.getElementById("establecimiento").innerText = "Sucursal: "+empleado.nombre_sucursal;


     function getCSRFToken() {
        let cookieValue = null;
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = decodeURIComponent(cookie.substring("csrftoken=".length));
                break;
            }
        }
        return cookieValue;
    }
    
    setTimeout(function() {
        var alertElements = document.querySelectorAll('.alert-dismissible');
        alertElements.forEach(function(alertElement) {
            var bootstrapAlert = new bootstrap.Alert(alertElement);
            bootstrapAlert.close();
        });
    }, 3000); // 5000 milisegundos = 5 segundos



    document.getElementById("txtEfectivo").onkeyup = e => {
        let total = parseFloat(document.getElementById("totalGeneral").textContent);
        let efectivo = parseFloat(document.getElementById("txtEfectivo").value);
        let txtEfectivo = document.getElementById("txtEfectivo");

        txtEfectivo.setCustomValidity("");
        console.log(txtEfectivo.value);
        console.log(total);
        if (total > efectivo) {
            txtEfectivo.setCustomValidity("El efectivo debe ser mayor al total.");
        } else if (efectivo <= 0) {
            txtEfectivo.setCustomValidity("El efectivo debe ser mayor a 0");
        }
        if (isNaN(txtEfectivo.value) || txtEfectivo.value.trim() === "") {
            txtEfectivo.setCustomValidity("Ingresa una cantidad válida.");
        }
    };

    document.getElementById("idProducto").onkeyup = e => {
        let txtProducto = document.getElementById("idProducto");
        txtProducto.setCustomValidity("");

        if (isNaN(txtProducto.value) || txtProducto.value.trim() === "") {
            txtProducto.setCustomValidity("Ingresa un ID de producto válido");
        }
    };

    document.getElementById("formTotal").addEventListener("submit", function(e) {
        e.preventDefault();
        let form = e.target;
        let total = parseFloat(document.getElementById("totalGeneral").textContent);
        let efectivo = parseFloat(document.getElementById("txtEfectivo").value);
        let txtEfectivo = document.getElementById("txtEfectivo");

        txtEfectivo.setCustomValidity("");

        if (total > efectivo) {
            txtEfectivo.setCustomValidity("El efectivo debe ser mayor al total.");
        }

        if (isNaN(txtEfectivo.value) || txtEfectivo.value.trim() === "") {
            txtEfectivo.setCustomValidity("Ingresa una cantidad válida.");
        }

        if (total == 0) {
            txtEfectivo.setCustomValidity("Ingrese productos para efectuar la venta.");
        }

        if (form.checkValidity()) {
            let modal = new bootstrap.Modal(document.getElementById('modalConfirmacionVenta'));
            modal.show();
            document.getElementById("txtTotal").value = total;
            document.getElementById("txtEfectivoFinal").value = efectivo;
            document.getElementById("txtCambio").value = efectivo - total;
            document.getElementById("txtTotal").disabled = true;
            document.getElementById("txtEfectivoFinal").disabled = true;
            document.getElementById("txtCambio").disabled = true;
        } else {
            form.reportValidity();
        }
    });


    document.getElementById("formVentas").addEventListener("submit", async function(e) {
        e.preventDefault();

        let productoId = document.getElementById("idProducto").value;
        let cantidad = parseInt(document.getElementById("cantidad").value);
        let idProducto = parseInt(productoId);

        document.getElementById("idProducto").setCustomValidity("");

        if (isNaN(idProducto) || productoId.trim() === "") {
            document.getElementById("idProducto").setCustomValidity("Ingresa un ID de producto válido");
        } else {
            try {
                const response = await fetchProducto(idProducto);
                if (response && response.productos && response.productos.length > 0) {
                    const producto = response.productos[0];
                    producto.cantidad = cantidad
                    actualizarTablaConProducto(producto);
                } else {
                    alert("Producto no encontrado");
                }
            } catch (error) {
                console.error("Error al buscar el producto:", error);
            }
        }
    });

    async function fetchProducto(idProducto) {
        try {
            const response = await fetch(`get_productos/${idProducto}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken(),  // Incluye el token CSRF
                    'Content-Type': 'application/json',
                }
            });
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                console.error("Error al obtener el producto:", response.status);
                return null;
            }
        } catch (error) {
            console.error("Error en la solicitud:", error);
            return null;
        }
    }

    function actualizarTablaConProducto(producto) {
        const tbody = document.querySelector("#tblVentas tbody");

        if (tablaVacia) {
            tbody.innerHTML = "";
            tablaVacia = false;
        }

        const precioUnitario = parseFloat(producto.precio_unitario);
        const cantidad = producto.cantidad;
        const subtotalProducto = precioUnitario * cantidad;
        totalSubtotal += subtotalProducto;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${producto.id || "N/A"}</td>
            <td>${producto.nombre || "N/A"}</td>
            <td>${precioUnitario.toFixed(2)}</td>
            <td>${cantidad}</td>
            <td>${subtotalProducto.toFixed(2)}</td>
        `;
        tbody.appendChild(row);

        actualizarTotales();
    }

    function actualizarTotales() {
        const iva = totalSubtotal * 0.16;
        const totalGeneral = totalSubtotal + iva;

        document.getElementById("subtotal").textContent = Math.ceil(totalSubtotal).toFixed(2);
        document.getElementById("iva").textContent = Math.ceil(iva).toFixed(2);
        document.getElementById("totalGeneral").textContent = Math.ceil(totalGeneral).toFixed(2);
    }


    // Mostrar modal al hacer clic en "Cobrar"
    document.getElementById("btnCobrar").addEventListener("click", function() {
        const total = parseFloat(document.getElementById("totalGeneral").textContent);
        const efectivo = parseFloat(document.getElementById("txtEfectivo").value);

        if (isNaN(efectivo) || efectivo < total) {
            alert("La cantidad de efectivo es insuficiente para realizar la venta.");
        } else {
            const modalElement = document.getElementById('modalConfirmacionVenta');
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    });

    document.getElementById("confirmarVentaBtn").addEventListener("click", async function() {
        const productosVendidos = obtenerProductosDeTabla();
    
        if (productosVendidos.length === 0) {
            alert("No hay productos para cobrar");
            return;
        }
    
        const descripcion = productosVendidos.map(producto => producto.nombre).join(", ");
        const totalVenta = parseFloat(document.getElementById("totalGeneral").textContent);
    
        // Recuperar el empleado desde localStorage
        const empleado = JSON.parse(localStorage.getItem('empleado'));
        if (!empleado) {
            alert("No se encontró información del empleado. Por favor, inicia sesión nuevamente.");
            return;
        }
    
        // Construir los datos de la venta
        const ventaData = {
            descripcion: descripcion,
            total: totalVenta,
            empleado_id: empleado.id,   // ID del empleado
            sucursal_id: empleado.sucursal, // ID de la sucursal asignada al empleado
            fecha: new Date().toISOString()
        };
    
        console.log("Datos de venta a enviar:", ventaData);
    
        try {
            const response = await fetch("../venta/realizar_venta/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(ventaData),
                credentials: 'same-origin',
            });
    
            if (response.ok) {
                alert("Venta registrada exitosamente");
                limpiarTabla();
                totalSubtotal = 0;
                actualizarTotales();
    
                // Ocultar el modal antes de recargar
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmacionVenta'));
                modal.hide();
                window.location.reload();
                
            } else {
                alert("Error al registrar la venta");
            }
        } catch (error) {
            console.error("Error al realizar la venta:", error);
        }
    });
    

    function limpiarTabla() {
        const tbody = document.querySelector("#tblVentas tbody");
        tbody.innerHTML = `<tr><td colspan="6">No hay ventas registradas.</td></tr>`;
        tablaVacia = true;
    }

    // Función para obtener productos desde la tabla
    function obtenerProductosDeTabla() {
        const productos = [];
        const rows = document.querySelectorAll("#tblVentas tbody tr");

        rows.forEach(row => {
            const columns = row.querySelectorAll("td");
            if (columns.length === 5) {
                const producto = {
                    id: parseInt(columns[0].textContent.trim()),
                    nombre: columns[1].textContent.trim(),
                    precio_unitario: parseFloat(columns[2].textContent.trim()),
                    cantidad: parseInt(columns[3].textContent.trim()),
                    subtotal: parseFloat(columns[4].textContent.trim())
                };
                productos.push(producto);
            }
        });

        return productos;
    }
});