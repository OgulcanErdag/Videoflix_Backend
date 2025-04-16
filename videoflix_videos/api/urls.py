from django.urls import path
from .views import UploadVideoView, VideoListView, SingleVideoView, VideoProgressView

urlpatterns = [
    path('videos/upload/', UploadVideoView.as_view(), name='upload_video'),
    path('videos/', VideoListView.as_view(), name='video_list'),
    path('videos/<int:video_id>/', SingleVideoView.as_view(), name='single_video'),
    path('video/<int:video_id>/progress/', VideoProgressView.as_view(), name='video-progress'),
]