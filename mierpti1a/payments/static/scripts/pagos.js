
document.addEventListener('DOMContentLoaded', function() {
    
    // Agregar un evento al campo de selección de tipo de pago para que llame a la función al cambiar
    document.getElementById('paymentType').addEventListener('change', showFields);
  
        debugger
        document.getElementById('paymentForm').addEventListener('submit', function (event) {
            event.preventDefault(); // Prevenir el envío predeterminado del formulario
            debugger
            // Obtener valores del formulario
            const clientId = document.getElementById('clientId').value;
            const amount = document.getElementById('amount').value;
            const paymentType = document.getElementById('paymentType').value;
            const cardHolder = document.getElementById('cardHolder').value;
            const cardNumber = document.getElementById('cardNumber').value;
            const expiryDate = document.getElementById('expiryDate').value;
            const cvv = document.getElementById('cvv').value;
            const paypalHolder = document.getElementById('paypalHolder').value;
            const paypalEmail = document.getElementById('paypalEmail').value;
            const voucherNumber = document.getElementById('voucherNumber').value;
    
            // Crear un objeto de datos
            let formData = {
                clientId: clientId,
                amount: amount,
                paymentType: paymentType
            };
    
            // Agregar campos específicos según el tipo de pago
            if (paymentType === 'Tarjeta') {
                formData.cardHolder = cardHolder;
                formData.cardNumber = cardNumber;
                formData.expiryDate = expiryDate;
                formData.cvv = cvv;
            } else if (paymentType === 'Paypal') {
                formData.paypalHolder = paypalHolder;
                formData.paypalEmail = paypalEmail;
            } else if (paymentType === 'Vale') {
                formData.voucherNumber = voucherNumber;
            }
    
            // Enviar la solicitud POST al servidor
            fetch('/api_pagos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Obtener el token CSRF del formulario
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.text(); // Cambiar a text si la respuesta es un mensaje de éxito simple
            })
            .then(data => {
                alert('Pago creado exitosamente');
                console.log(data);
            })
            .catch(error => {
                console.error('Error al realizar la solicitud:', error);
                alert('Ocurrió un error al procesar el pago.');
            });
        });
    });
    
    


function showFields() {
    // Ocultar todos los campos específicos
    document.getElementById('cardFields').classList.add('hidden');
    document.getElementById('paypalFields').classList.add('hidden');
    document.getElementById('voucherFields').classList.add('hidden');

    // Obtener el tipo de pago seleccionado
    const paymentType = document.getElementById('paymentType').value;

    // Mostrar los campos según el tipo de pago
    if (paymentType === 'Tarjeta') {
        document.getElementById('cardFields').classList.remove('hidden');
    } else if (paymentType === 'Paypal') {
        document.getElementById('paypalFields').classList.remove('hidden');
    } else if (paymentType === 'Vale') {
        document.getElementById('voucherFields').classList.remove('hidden');
    }
}
