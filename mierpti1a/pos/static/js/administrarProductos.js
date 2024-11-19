document.addEventListener("DOMContentLoaded", ()=>{
    // Validaciones
    document.getElementById("mdlAgregar").addEventListener('shown.bs.modal', (e) => {
        let operacion=e.relatedTarget.innerText;
        e.target.querySelector(".modal-title").innerText=operacion;
    });

    document.getElementById("modalNombre").onkeyup = e =>{
        let txtNombre = document.getElementById("modalNombre");
        if (txtNombre.value.trim().length < 5 || txtNombre.value.trim().length > 50 ) {
            txtNombre.setCustomValidity("El nombre es obligatorio y debe tener entre 5 y 50 caracteres.");
        }
        if ( /[\'"]/.test(txtNombre.value)) {
            txtNombre.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }
        else{
            txtNombre.setCustomValidity("");
        }
    };
    
    document.getElementById("modalPrecio").onkeyup = e =>{
        let txtPrecio = document.getElementById("modalPrecio");
        if (isNaN(txtPrecio.value) || txtPrecio.value <= 0) {
            txtPrecio.setCustomValidity("El precio es obligatorio y debe ser un número mayor o igual a uno.");
        }
        if ( /[\'"]/.test(txtPrecio.value)) {
            txtPrecio.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }
        else{
            txtPrecio.setCustomValidity("");
        }
    };
    
    document.getElementById("modalStock").onkeyup = e =>{
        let txtStock = document.getElementById("modalStock");
        if (!/^\d+$/.test(txtStock.value)) {
            txtStock.setCustomValidity("El stock es obligatorio y debe contener solo números.");
        }
        if ( /[\'"]/.test(txtStock.value)) {
            txtStock.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }
        else{
            txtStock.setCustomValidity("");
        }
    };
    
    document.getElementById("productoForm").addEventListener("submit", function(e) {
        e.preventDefault(); // Evita el envío predeterminado del formulario
        //console.log("pruebaaa")
        let form = e.target;
        let txtNombre = document.getElementById("modalNombre");
        let txtPrecio = document.getElementById("modalPrecio");
        let txtStock = document.getElementById("modalStock");
    
        // Reset custom validity
        txtNombre.setCustomValidity("");
        txtPrecio.setCustomValidity("");
        txtStock.setCustomValidity("");
    
        // Validación personalizada
        if (txtNombre.value.trim().length < 5 || txtNombre.value.trim().length > 50) {
            txtNombre.setCustomValidity("El nombre es obligatorio y debe tener entre 5 y 50 caracteres.");
        }
        if ( /[\'"]/.test(txtNombre.value)) {
            txtNombre.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }
        if (isNaN(txtPrecio.value) || txtPrecio.value <= 0) {
            txtPrecio.setCustomValidity("El precio es obligatorio y debe ser un número mayor o igual a uno.");
        }
        if ( /[\'"]/.test(txtPrecio.value)) {
            txtPrecio.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }
        if (!/^\d+$/.test(txtStock.value)) {
            txtStock.setCustomValidity("El stock es obligatorio y debe contener solo números.");
        }
        if ( /[\'"]/.test(txtStock.value)) {
            txtStock.setCustomValidity("Estas intentando agregar un caracter que no esta permitido");
        }

        console.log(e);

        // Si el formulario es válido, envíalo
        /*if (form.checkValidity()) {
            form.submit();
        }
        else{
            e.preventDefault();
        }*/
    });

    // Cargar datos desde los views de django
    cargarProductos();
    
    
});

async function cargarProductos()
{
    const tbody = document.getElementById("productos-tbody");
    
    try {
        const response = await fetch('get_productos');
        const productos = await response.json();

        console.log("Cola");
        console.log(productos);
        console.log(Array.isArray(productos));

        //Limpiar datos
        tbody.innerHTML = "";

        if (productos.message == "Success") {
            productos.productos.forEach(producto => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${producto.id}</td>
                    <td>${producto.nombre}</td>
                    <td>${producto.precio_unitario}</td>
                    <td>${producto.descuento}</td>
                    <td></td>
                    <td>${producto.stock}</td>
                    <td>${producto.descripcion}</td>
                    <td>${producto.sucursal_id}</td>
                    <td>
                        <div>
                            <button type="button" class="btn btn-primary btn-editar" data-id="${producto.id}" data-bs-toggle="modal" data-bs-target="#mdlAgregar">Editar</button>
                            <button type="button" class="btn btn-danger btn-borrar" data-id="${producto.id}" data-bs-toggle="modal" data-bs-target="#mdlBorrar">Borrar</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
            document.querySelectorAll(".btn-editar").forEach(button => {
                button.addEventListener("click", function() {
                    console.log(button.dataset.id);
                    cargarDatosProducto(button.dataset.id);
                });
            });
            document.querySelectorAll(".btn-borrar").forEach(button => {
                button.addEventListener("click", function() {
                    borrarProducto(button.dataset.id);
                });
            });
        } else {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="8">No hay productos disponibles.</td>`;
            tbody.appendChild(row);
        }
    } catch (error) {
        console.error('Error al cargar los datos:', error);
    }
}

async function cargarDatosProducto(id) {
    try {
        document.getElementById("modalImagen").value = "";
        const response = await fetch(`get_productos/${id}/`);  // URL para obtener los datos del producto específico
        const producto = await response.json();
        document.getElementById("modalImagen").required = false;

        producto.productos.forEach(producto => {
            document.getElementById("modalId").value = producto.id;
            document.getElementById("modalNombre").value = producto.nombre;
            document.getElementById("modalPrecio").value = producto.precio_unitario;
            document.getElementById("modalDescuento").value = producto.descuento;
            document.getElementById("modalStock").value = producto.stock;
            document.getElementById("modalDescripcion").value = producto.descripcion;
            const imgPreview = document.getElementById("imagenPreview");
            const partesRuta = producto.imagen.split('/');
            const nombreArchivo = partesRuta[partesRuta.length - 1];
            if (imgPreview) {
                imgPreview.src = `${staticBaseUrl}img/${nombreArchivo}`;  // Combina la URL base con la ruta de la imagen
            }
            //document.getElementById("modalSucursal").value = producto.productos.sucursal;
            // Voy a mover esto hasta que se arregle los views, para poder ver como cargarlo

            document.getElementById("btnGuardarCambios").onclick = () => editarProducto(id);
        });
    } catch (error) {
        console.error("Error al cargar los datos del producto:", error);
    }
}

async function editarProducto(id) {
    const formData = new FormData();
    
    formData.append('nombre', document.getElementById("modalNombre").value);
    formData.append('precio_unitario', document.getElementById("modalPrecio").value);
    formData.append('descuento', document.getElementById("modalDescuento").value);
    formData.append('stock', document.getElementById("modalStock").value);
    formData.append('descripcion', document.getElementById("modalDescripcion").value);
    formData.append('sucursal', 1); // Cambia esto según sea necesario
    formData.append('imagen', document.getElementById("modalImagen").files[0]); // Cambia aquí para obtener el archivo

    try {
        // Cambiar a la url que se usara en el views de django (De preferencia recibir el id)
        const response = await fetch(`editar_producto/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken  // Agrega el token CSRF aquí
            },
            body: formData,
        });

        if (response.ok) {
            //alert("Producto editado con éxito");

            $('#mdlAgregar').modal('hide');

           cargarProductos();
        } else {
            console.error("Error al editar el producto");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

async function borrarProducto(id) {
    // Mostrar el modal de confirmación y agregar el mensaje personalizado
    const modal = new bootstrap.Modal(document.getElementById("mdlBorrar"));
    const modalMessage = document.getElementById("contenido-borrar");
    
    // Agrega el mensaje de confirmación al modal
    modalMessage.textContent = `¿Estás seguro de que deseas eliminar el producto con ID ${id}? Esta acción no se puede deshacer.`;

    // Al hacer clic en el botón de confirmación del modal, proceder con la eliminación
    document.getElementById("btnBorrar").onclick = async () => {
        try {
            // Realizar la solicitud DELETE al servidor para eliminar el producto
            const response = await fetch(`borrar_producto/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken  // Incluye el token CSRF si es necesario
                }
            });

            if (response.ok) {
                alert("Producto borrado con éxito");

                cargarProductos();

                // Cierra el modal después de borrar el producto
                $('#mdlBorrar').modal('hide');
            } else {
                console.error("Error al borrar el producto");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };
}


async function agregarProducto() {
    const formData = new FormData();
    
    formData.append('nombre', document.getElementById("modalNombre").value);
    formData.append('precio_unitario', document.getElementById("modalPrecio").value);
    formData.append('descuento', document.getElementById("modalDescuento").value);
    formData.append('stock', document.getElementById("modalStock").value);
    formData.append('descripcion', document.getElementById("modalDescripcion").value);
    formData.append('sucursal', document.getElementById("modalSelect").value); // Cambia esto según sea necesario
    formData.append('imagen', document.getElementById("modalImagen").files[0]); // Cambia aquí para obtener el archivo

    try {
        const response = await fetch('agregar_producto/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken  // Agrega el token CSRF aquí
            },
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            //alert("Producto agregado con éxito");

            $('#mdlAgregar').modal('hide');

            cargarProductos();

        } else {
            console.error("Error al agregar el producto");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

async function limpiarDatos() {
    document.getElementById("modalId").value = "";
    document.getElementById("modalNombre").value = "";
    document.getElementById("modalPrecio").value = "";
    document.getElementById("modalDescuento").value = "";
    document.getElementById("modalStock").value = "";
    document.getElementById("modalDescripcion").value = "";
    document.getElementById("imagenPreview").src = "";
    document.getElementById("btnGuardarCambios").onclick = () => agregarProducto();
    document.getElementById("modalImagen").required = true;
    document.getElementById("modalImagen").value = "";
    try {
        const response = await fetch(`http://localhost:8000/RRHH/get_sucursales/`);
        
        // Verifica si la respuesta es válida
        if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.statusText}`);
        }

        const sucursales = await response.json();

        // Selecciona el elemento <select> del DOM
        const modalSelect = document.getElementById('modalSelect');
        
        if (!modalSelect) {
            console.error("No se encontró el elemento select con ID 'modalSelect'");
            return;
        }

        // Limpia las opciones actuales del <select>
        modalSelect.innerHTML = '<option value="" disabled selected>Seleccione una sucursal</option>';

        // Recorre las sucursales y agrégalas como opciones al <select>
        sucursales.sucursales.forEach(sucursal => {
            const option = document.createElement('option');
            option.value = sucursal.id; // Usar el ID de la sucursal como valor
            option.textContent = sucursal.nombre; // Mostrar el nombre de la sucursal
            modalSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error al cargar las sucursales:", error);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');