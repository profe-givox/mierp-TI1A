document.addEventListener('DOMContentLoaded', async function () {
    const staticBaseUrl = "{% static '' %}"; // Base URL para cargar imágenes
    const sucursalSelect = document.getElementById('sucursalSelect');
    const productosContainer = document.getElementById('productosContainer');

    // Función para cargar las sucursales desde la API
    async function cargarSucursales() {
        try {
            const response = await fetch('http://localhost:8000/RRHH/get_sucursales/'); // Cambia a la URL correcta en tu proyecto
            const data = await response.json();

            if (data.success) {
                // Rellenar el select con las sucursales
                data.sucursales.forEach(sucursal => {
                    const option = document.createElement('option');
                    option.value = sucursal.id; // Usar el ID de la sucursal
                    option.textContent = sucursal.nombre; // Nombre de la sucursal
                    sucursalSelect.appendChild(option);
                });
            } else {
                console.error("Error al cargar sucursales:", data.error);
            }
        } catch (error) {
            console.error("Error al cargar sucursales:", error);
        }
    }

    // Función para cargar productos desde la API
    async function cargarProductos() {
        try {
            const response = await fetch('get_catalogo/'); // Cambia a la URL correcta en tu proyecto
            const data = await response.json();

            if (data.success) {
                mostrarProductos(data.catalogo);
            } else {
                console.error("Error al cargar productos:", data.error);
            }
        } catch (error) {
            console.error("Error al cargar productos:", error);
        }
    }

    // Función para mostrar productos en el contenedor
    function mostrarProductos(productos) {
        productosContainer.innerHTML = ''; // Limpiar contenedor
        productos.forEach(producto => {
            const div = document.createElement('div');
            div.className = 'producto';
            div.dataset.sucursal = producto.sucursal; // Asociar sucursal al producto
            const partesRuta = producto.imagen.split('/');
            const nombreArchivo = partesRuta[partesRuta.length - 1];
            const urlImagen = `${staticBaseUrl}img/${nombreArchivo}`;

            div.innerHTML = `
                <img src="${urlImagen}" alt="${producto.nombre}">
                <div>
                    <h3>${producto.nombre}</h3>
                    <label>ID: ${producto.id}</label>
                    <label>${producto.descripcion}</label>
                    <label>Stock: ${producto.stock}</label>
                </div>
                <div>
                    <input type="button" value="Ver" data-bs-toggle="modal" data-bs-target="#modal-detalles" 
                        onclick="cargarDatosModal('${producto.nombre}', ${producto.id}, ${producto.stock}, '${producto.descripcion}', '${urlImagen}')">
                </div>
            `;
            productosContainer.appendChild(div);
        });
    }

    // Función para cargar datos en el modal
    function cargarDatosModal(Nombre, ID, Stock, Descripcion, Imagen) {
        const nombreModal = document.getElementById("nombreModal");
        const idModal = document.getElementById("idModal");
        const stockModal = document.getElementById("stockModal");
        const descripcionModal = document.getElementById("descripcionModal");
        const imgModal = document.getElementById("imgModal");

        nombreModal.textContent = Nombre;
        idModal.textContent = "ID: " + ID;
        stockModal.textContent = "Stock: " + Stock;
        descripcionModal.textContent = Descripcion;
        imgModal.src = Imagen;
    }

    // Función para filtrar productos por sucursal seleccionada
    function filtrarProductosPorSucursal() {
        const idSucursal = sucursalSelect.value;
        const productos = document.querySelectorAll('.producto');

        productos.forEach(producto => {
            if (idSucursal === 'all' || producto.dataset.sucursal === idSucursal) {
                producto.style.display = 'flex';
            } else {
                producto.style.display = 'none';
            }
        });
    }

    // Función para buscar productos por nombre
    function filtrarProductos() {
        const input = document.getElementById('buscar');
        const filter = input.value.toLowerCase();
        const productos = document.querySelectorAll('.producto');

        productos.forEach(producto => {
            const nombre = producto.querySelector('h3').textContent.toLowerCase();
            if (nombre.includes(filter)) {
                producto.style.display = 'flex';
            } else {
                producto.style.display = 'none';
            }
        });
    }

    // Asignar eventos a los elementos
    sucursalSelect.addEventListener('change', filtrarProductosPorSucursal);

    // Cargar sucursales y productos al cargar la página
    await cargarSucursales();
    await cargarProductos();
});
