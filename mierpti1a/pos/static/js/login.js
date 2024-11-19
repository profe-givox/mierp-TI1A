
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

document.getElementById("formLogin").addEventListener("submit", function(event) { 
    event.preventDefault();  // Evitar el envío tradicional del formulario

    // Obtener los valores de los campos del formulario
    const folio = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Mostrar mensaje de carga o deshabilitar el botón
    const button = document.getElementById('btnAceptar');

    // Realizar la solicitud POST a la API usando fetch
    fetch('http://localhost:8000/RRHH/login/', {
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
            // Si la respuesta es exitosa, redirigir al usuario
            console.log(data.empleado.nombre);
            localStorage.setItem('empleado', JSON.stringify(data.empleado));
            window.location.href = 'venta/'; 
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