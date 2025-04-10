from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/originals/') 
    thumbnail = models.FileField(upload_to='thumbnails/')  
    description = models.TextField(blank=True)
    hls_master_playlist = models.FileField(upload_to='videos/hls/', blank=True, null=True)
    genre = models.CharField(max_length=50, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the string representation of the Video instance, which is the title of the video.
        """

        return self.title


class UserVideoProgress(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_progress')
    last_viewed_position = models.FloatField(default=0.0) 
    viewed = models.BooleanField(default=False)
    last_viewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the UserVideoProgress instance, 
        which includes the username of the user and the title of the video.
        """

        return f"{self.user.username} - {self.video.title}"


