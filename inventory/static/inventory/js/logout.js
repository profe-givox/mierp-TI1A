document.addEventListener('DOMContentLoaded', () => {
    const cerrarSesionBtn = document.getElementById('confirmar-cierre-sesion');
    if (cerrarSesionBtn) {
        cerrarSesionBtn.addEventListener('click', () => {
            // Cerrar sesión enviando solicitud al servidor
            fetch('/accounts/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.cookie
                        .split('; ')
                        .find(row => row.startsWith('csrftoken='))
                        ?.split('=')[1],
                    'Content-Type': 'application/json',
                },
            })
                .then(response => {
                    if (response.ok) {
                        console.log('Sesión cerrada correctamente.');
                        // Redirigir al usuario a la página de inicio de sesión
                        window.location.href = '/accounts/login/';
                    } else {
                        console.error('Error al cerrar sesión:', response.statusText);
                        alert('Ocurrió un error al cerrar sesión. Intenta de nuevo.');
                    }
                })
                .catch(error => {
                    console.error('Error en la solicitud de cierre de sesión:', error);
                    alert('Ocurrió un error al cerrar sesión. Intenta de nuevo.');
                });
        });
    } else {
        console.error('El botón confirmar-cierre-sesion no existe en el DOM.');
    }
});
