// Función para obtener el CSRF token desde las cookies
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

// Función para guardar el empleado en las cookies
function setEmpleadoCookie(empleado) {
    const empleadoJSON = JSON.stringify(empleado);
    document.cookie = `empleado=${encodeURIComponent(empleadoJSON)}; path=/; max-age=3600`; // Expira en 1 hora
}

// Función para guardar el empleado en almacenamiento local y de sesión
function saveEmpleadoInStorages(empleado) {
    const empleadoJSON = JSON.stringify(empleado);
    // Guardar en almacenamiento local
    localStorage.setItem('empleado', empleadoJSON);
    // Guardar en almacenamiento de sesión
    sessionStorage.setItem('empleado', empleadoJSON);

    console.log("Debug: Empleado guardado en localStorage y sessionStorage.");
}

document.getElementById("formLogin").addEventListener("submit", function(event) { 
    event.preventDefault();  // Evitar el envío tradicional del formulario

    // Obtener los valores de los campos del formulario
    const folio = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Mostrar mensaje de carga o deshabilitar el botón
    const button = document.getElementById('btnAceptar');

    // Realizar la solicitud POST a la API usando fetch
    fetch('http://127.0.0.1:8000/RRHH/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // CSRF Token para la seguridad
        },
        body: JSON.stringify({
            folio: folio,  // Usamos el valor del campo de usuario
            password: password  // Usamos el valor del campo de contraseña
        })
    })
    .then(response => response.json())  // Procesar la respuesta JSON
    .then(data => {
        if (data.success) {
            // Si la respuesta es exitosa, guardar en localStorage, sessionStorage y cookies
            console.log(data.empleado.nombre);

            // Guardar en localStorage y sessionStorage
            saveEmpleadoInStorages(data.empleado);

            // Guardar en cookies
            setEmpleadoCookie(data.empleado);

            // Verificar el rol del empleado y redirigir según corresponda
            const puesto = data.empleado.puesto.split(' ')[0];
            if (puesto === "Administrador") {
                console.log("Debug: Redirigiendo al CRUD de productos para administrador.");
                window.location.href = 'http://127.0.0.1:8000/pos/productos/';
            } else {
                // Redirigir al usuario normal a la vista de ventas
                window.location.href = 'venta/';
            }
        } else {
            // Mostrar error si el login falla
            alert(data.error);
            console.log(data.empleado);
        }
    })
    .catch(error => {
        // Manejo de errores en caso de que falle la solicitud
        console.error('Error:', error);
        alert('Ocurrió un error al intentar iniciar sesión');
        button.textContent = 'Iniciar sesión';
        button.disabled = false;
    });
});
