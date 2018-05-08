from django.db import models

from expert_user.models import ExUser


class Category(models.Model):
    category_name = models.CharField(max_length=100)


class Skill(models.Model):
    skill_name = models.CharField(max_length=100, unique=True)
    skill_description = models.TextField(null=True)
    skill_price = models.FloatField(default=0.0)
    need_top = models.BooleanField(default=False)
    is_system = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='skill', on_delete=models.CASCADE)
    user = models.ManyToManyField(ExUser, related_name='skill')

    class Meta:
        ordering = ['need_top', 'is_system', 'id']
