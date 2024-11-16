// Función que maneja el envío del formulario sin recargar la página
function handleLogin(event) {
    event.preventDefault();  // Evitar el envío tradicional del formulario

    // Obtener los valores de los campos del formulario
    const folio = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Mostrar mensaje de carga o deshabilitar el botón
    const button = document.getElementById('btnAceptar');
    button.textContent = 'Iniciando sesión...';
    button.disabled = true;

    // Realizar la solicitud POST a la API usando fetch
    fetch('http://localhost:8000/RRHH/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // CSRF Token para la seguridad
        },
        body: JSON.stringify({
            folio: folio,  // Usamos el valor del campo de usuario
            password: password  // Usamos el valor del campo de contraseña
        })
    })
    .then(response => response.json())  // Procesar la respuesta JSON
    .then(data => {
        if (data.status === 'success') {
            // Si la respuesta es exitosa, redirigir al usuario
            window.location.href = '/catalogo/'; 
        } else {
            // Mostrar error si el login falla
            alert('Error en el login: ' + data.message);
            button.textContent = 'Iniciar sesión';
            button.disabled = false;
        }
    })
    .catch(error => {
        // Manejo de errores en caso de que falle la solicitud
        console.error('Error:', error);
        alert('Ocurrió un error al intentar iniciar sesión');
        button.textContent = 'Iniciar sesión';
        button.disabled = false;
    });
}

// Función para obtener el CSRF token desde las cookies
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