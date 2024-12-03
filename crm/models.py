from django.db import models

# ------------------------------------------------------------------------------------
# MODELOS RELACIONADOS CON EL MÓDULO DE PREGUNTAS FRECUENTES, ARTÍCULOS Y GUÍAS 
# ------------------------------------------------------------------------------------

# Categoría de las preguntas
class SupportCategory(models.Model):
    name = models.CharField(max_length=255) # Nombre de l acategoría
    description = models.TextField() # Descripción de la categoría

    def __str__(self):
        return self.name

# El modelo de FACArticle es muy reutilizable, puede usarse para preguntas frecuentes, noticias, artículos y guías
# Hay un nuevo de ForeignKey. Dejo la documentación: https://docs.djangoproject.com/en/5.1/ref/models/fields/
# Documentación DateField: https://docs.djangoproject.com/en/5.1/ref/models/fields/#django.db.models.DateField.auto_now
class FAQArticle(models.Model):
    title = models.CharField(max_length=255) # Título del articulo, pregunta, guía, etc.
    content = models.TextField() # Contenido
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE, related_name='articles') # Categoría a la que pertenece
    created_at = models.DateTimeField(auto_now_add=True) # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True) # Fecha de edición

    def __str__(self):
        return self.title


# ------------------------------------------------------------------------------------
# SISTEMA DE TICKETS PARA EL SEGUIMIENTO DE LOS CASOS DE LOS USUARIOS 
# ------------------------------------------------------------------------------------

# Modelo de usuario para tener su información básica
class User(models.Model):
    name = models.CharField(max_length=60)
    lastName = models.CharField(max_length=60)
    email = models.EmailField()
    phone = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=60)

    def __str__(self):
        return self.name
    
# Modelo del agente de soporte, es practicamente lo mismo que es cliente 
# pero por ahora estará separado y seguramente se quedará así
class SupportAgent(models.Model):
    name = models.CharField(max_length=60)
    firstName = models.CharField(max_length=60)
    email = models.EmailField()
    phone = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

# El modelo de tickets para el seguimiento de las incidencias de los usuarios
class Ticket(models.Model):
    # opciones por defecto del estado del tiecket
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('in_progress', 'En progreso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ]

    title = models.CharField(max_length=255) # Título del ticket
    description = models.TextField() # Descripción o contenido
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open') # Estado del ticket
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario que abrió el ticket
    assigned_to = models.ForeignKey(SupportAgent, on_delete=models.SET_NULL, null=True, blank=True) # Agente asignado, puede ser nulo

    def __str__(self):
        return f"{self.title} ({self.status})"

# Modelo de comentarios para tickets, puede haber varios comentarios en un solo ticket
class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments') # Ticket al que pertenece el comentario
    comment = models.TextField() # Contenido del comentario
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario en {self.ticket.title}"


# ------------------------------------------------------------------------------------
# MODELO RELACIONADO CON EL MÓDULO DE COMUNIDAD 
# ------------------------------------------------------------------------------------

# Modelo de post, es la entidad donde los usuarios publican sus incidencias o problemas 
# para obtener solución de otros usuarios o del equipo de soporte inclusive
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  # Usuario que crea el post
    title = models.CharField(max_length=255)  # Título del problema
    description = models.TextField()  # Descripción del problema o incidencia
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización

    def __str__(self):
        return self.title
    
# Modelo de respuesta, es la entidad en donde otros usuarios responden a la incidencia de un usuario
class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')  # Post al que responde
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')  # Usuario que responde
    content = models.TextField()  # Contenido de la respuesta
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    is_useful = models.BooleanField(default=False)  # Marca si la respuesta fue útil o no

    def __str__(self):
        return f'Respuesta de {self.user.emal} al post {self.post.title}'


class ResponseVote(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='votes')  # Respuesta votada
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='response_votes')  # Usuario que vota
    vote_type = models.BooleanField()  # True si el voto es útil, False si no es útil

    # La siguiente es de Django, es una clase que permite establecer reglas en los datos
    # Documentación: https://docs.djangoproject.com/en/5.1/ref/models/options/
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['response', 'user'], name='unique_user_vote_per_response')
        ]  # Un usuario solo puede votar una vez en cada respuesta

    def __str__(self):
        return f'Voto de {self.user.email} en {self.response.id}'


# ------------------------------------------------------------------------------------
# MODELOS RELACIONADOS CON EL CHAT EN VIVO
# ------------------------------------------------------------------------------------

# Modelo que representa la sesión activa entre un usuario y un agente de soporte
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # El usuario que abrio el chat
    agent = models.ForeignKey(SupportAgent, on_delete=models.SET_NULL, null=True, blank=True) # El agente que atiende
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Chateando con {self.agent.emal}"

# Modelo para guardar los mensajes del chat
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages') # la sesión a la que pertenecen los mensajes
    sender = models.ForeignKey(User, on_delete=models.CASCADE) # El que envía los mensajes
    sender_type = models.CharField(max_length=10, choices=[('agent', 'Agente'), ('user', 'Usuario')]) # El tipo de entidad que envía un mensaje
    message = models.TextField() # Contenido del mensaje
    timestamp = models.DateTimeField(auto_now_add=True) # fecha y hora de envío

    def __str__(self):
        return f"Mensaje de {self.sender.email} en sesión {self.session.id}"


# ------------------------------------------------------------------------------------
# MODELOS RELACIONADOS CON EL MÓDULO DE SOPORTE MULTICANAL
# ------------------------------------------------------------------------------------

class SupportChannel(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------------------
# MODELOS RELACIONADOS CON EL MÓDULO DE AUTOMATIZACIÓN Y CHATBOT
# ------------------------------------------------------------------------------------

# Modelo del chatbot
class BotResponse(models.Model):
    trigger = models.CharField(max_length=255) # Palabra clave o frase que activa la respuesta del bot.
    response = models.TextField() # La respuesta generada por el bot
    
    def __str__(self):
        return self.trigger


# ------------------------------------------------------------------------------------
# MODELOS RELACIONADOS CON EL MÓDULO DE REPORTES
# ------------------------------------------------------------------------------------

# El modelo de reportes no esta tan claro por ahora
class Report(models.Model):
    title = models.CharField(max_length=255)  # Título del reporte
    data = models.JSONField()  # Todavía no esta establecido como guardar los datos, JSON es una opción
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos para el periodo de dodnde pertenecen los datos
    start_date = models.DateTimeField()  # Fecha de inicio
    end_date = models.DateTimeField()  # Fecha de finalización
