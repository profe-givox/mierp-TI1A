
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

document.querySelector('.btn-container').addEventListener('click', (event) => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const action = event.target.value === 'Entrada' ? 'E' : 'S';

    if (!username || !password) {
        alert('Por favor, completa todos los campos.');
        return;
    }

    fetch('/RRHH/registro/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            folio: username,
            action: action,
            password: password
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.error || 'Error en la respuesta del servidor');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const empleado = data.empleado;
            const action = data.action;
            console.log("URL de la imagen:", `${empleado.foto}`);
            // Acción de entrada: crea un nuevo slot para el empleado
            if (action === 'E') {
                // Crear un nuevo slot
                const newSlot = document.createElement('div');
                newSlot.classList.add('slot', 'occupied');
                newSlot.innerHTML = `<img src="${empleado.foto}" alt="${empleado.nombre}" class="slot-image" />`;
                
                // Agregar el nuevo slot al contenedor
                document.getElementById('slots-container').appendChild(newSlot);
            }
            // Acción de salida: busca el slot y lo limpia
            else if (action === 'S') {
                const slots = document.querySelectorAll('.slot');
                slots.forEach(slot => {
                    if (slot.innerHTML.includes(empleado.nombre)) {
                        slot.remove();         
                    }
                });
            }

            alert('Registro exitoso');
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un problema al procesar la solicitud: ' + error.message);
    });
});
