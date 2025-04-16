from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Video
import os
import shutil
from django.conf import settings
from .tasks import convert_to_hls
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Video)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[Signal] Triggering HLS conversion for video id: {instance.id}")
        convert_to_hls.delay(instance.id)

@receiver(post_delete, sender=Video)       
def auto_delete_files_on_video_delete(sender, instance, **kwargs):
   
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

    hls_dir = os.path.join(instance.file.storage.location, 'videos', 'hls', str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)