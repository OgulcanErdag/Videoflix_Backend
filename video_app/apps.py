from django.apps import AppConfig


class VideoflixVideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_app'

    def ready(self):
        """
        This method is called when the Django application is ready.

        It imports the signals module from the video_app package. This is
        typically done to ensure that signal handlers are connected when the app
        is initialized.
        """

        import video_app.signals