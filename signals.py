from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tally
from .utils import ensure_session_for_date


@receiver(post_save, sender=Tally)
def auto_generate_session(sender, instance, **kwargs):
    if instance.date:
        ensure_session_for_date(instance.date)
