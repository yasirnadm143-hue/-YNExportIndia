from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order
from .mlm import distribute_commission


@receiver(post_save, sender=Order)
def order_delivered_signal(
    sender,
    instance,
    created,
    **kwargs
):
    """
    Order DELIVERED होने पर commission distribute करेगा.
    """

    if instance.status != "DELIVERED":
        return

    distribute_commission(
        instance
    )
