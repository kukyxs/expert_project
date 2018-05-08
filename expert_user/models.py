from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

GENDER_CHOICES = ((0, u'Male'), (1, u'Female'), (2, u'Secret'))


class ExUser(models.Model):
    user = models.OneToOneField(User, related_name='ex', on_delete=models.CASCADE, null=True)
    phone_num = models.CharField(max_length=20, null=True, unique=True)
    qq = models.CharField(max_length=20, null=True, unique=True)
    we_chat = models.CharField(max_length=30, null=True, unique=True)
    sex = models.IntegerField(choices=GENDER_CHOICES, default=2)
    age = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(blank=True, upload_to="/avatar/")
    avg_grade = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_ex(sender, instance, created, **kwargs):
    if created:
        ExUser.objects.get_or_create(user=instance)
