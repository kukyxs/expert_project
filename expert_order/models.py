from django.db import models

from expert_user.models import ExUser

ORDER_STATE = ((0, 'Publish'), (1, 'Picked'), (2, 'Finished'), (3, 'Evaluated'))


class Order(models.Model):
    order_name = models.CharField(max_length=100)
    order_state = models.IntegerField(choices=ORDER_STATE, default=0)
    order_sum = models.FloatField(default=0.0, null=False)
    order_location = models.CharField(max_length=255)
    publish_time = models.DateTimeField(auto_now_add=True)
    picked_time = models.DateTimeField(null=True)
    finished_time = models.DateTimeField(null=True)
    evaluate_time = models.DateTimeField(null=True)
    owner = models.ForeignKey(ExUser, on_delete=models.CASCADE, related_name='publish_order', null=True)
    picker = models.ForeignKey(ExUser, on_delete=models.CASCADE, related_name='picked_order', null=True)
    evaluation = models.TextField(null=True)
    grade = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ['-publish_time', 'id']

    def __str__(self):
        return self.order_name
