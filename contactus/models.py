from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValidationError('Name is required')
        
        # Validate subject is not empty
        if not self.subject or not self.subject.strip():
            raise ValidationError('Subject is required')
        
        # Validate message is not empty
        if not self.message or not self.message.strip():
            raise ValidationError('Message is required')

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
