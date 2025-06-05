# yourapp/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save 
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail

# Welcome email on account creation
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to BuyIt'
        message = f"Welcome {instance.username}, thank you for joining BuyIt!"
        recipient_list = [instance.email]
        send_mail(subject, message, 'noreply@buyit.com', recipient_list)

# Login notification email
@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    subject = 'Login Notification'
    message = f"Hello {user.username}, you just logged into your BuyIt account."
    send_mail(subject, message, 'noreply@buyit.com', [user.email])
