document.addEventListener('DOMContentLoaded', function() {

    document.getElementById('btnVolver').addEventListener('click', function(event) {
        event.preventDefault(); // Prevenir comportamiento predeterminado
        window.location.href = '/ecar/carrito'; // Redirigir a la página deseada
    });
    
    // Agregar un evento al campo de selección de tipo de pago para que llame a la función al cambiar
    document.getElementById('paymentType').addEventListener('change', showFields);
  
       // debugger
        document.getElementById('paymentForm').addEventListener('submit', function (event) {
            event.preventDefault(); // Prevenir el envío predeterminado del formulario
            //debugger
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
            fetch('/payments/api_pagos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Token CSRF
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData) // Convertir los datos a JSON
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json(); // Parsear la respuesta JSON
            })
            .then(data => {
                if (data.status === "success") {
                    //alert(`Pago realizado con éxito. ID del pago: ${data.payment_id}`);
                    console.log(data);
            
                    // Datos para generar el pedido
                    const formDataPedido = {
                        pago_id: data.payment_id // Usar el ID del pago recibido
                    };
                    debugger
                    // Enviar la solicitud para generar el pedido
                    return fetch('/payments/generarPedido/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Token CSRF
                             'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify(formDataPedido) // Convertir los datos del pedido a JSON
                    });
                } else {
                    alert(`Error al realizar el pago: ${data.error}`);
                    throw new Error(data.error);
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error en la solicitud de pedido: ${response.statusText}`);
                }
                
                return response.json(); // Parsear la respuesta JSON del pedido
            })
            .then(data => {
                if (data.status === "success") {
                    
                    window.location.href = '/payments/succesful/';
                    //alert(`Pedido generado con éxito. Orden #${data.orden_id}`);
                    console.log(data);
                } else {
                    alert(`Error al generar el pedido: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error durante el proceso:', error);
                alert('Ocurrió un error durante el proceso.');
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
