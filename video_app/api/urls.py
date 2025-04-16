from django.urls import path
from .views import AdminVideoUploadView, UserVideoListView, UserVideoDetailView, UserVideoProgressUpdateView

urlpatterns = [
    path('videos/upload/', AdminVideoUploadView.as_view(), name='upload_video'),
    path('videos/', UserVideoListView.as_view(), name='video_list'),
    path('videos/<int:video_id>/', UserVideoDetailView.as_view(), name='single_video'),
    path('video/<int:video_id>/progress/', UserVideoProgressUpdateView.as_view(), name='video-progress'),
]