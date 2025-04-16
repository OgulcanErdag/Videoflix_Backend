from celery import shared_task
import subprocess
from video_app.models import Video
import os
import time
import logging
logger = logging.getLogger(__name__)
import shutil
from django.conf import settings

@shared_task
def convert_to_hls(video_id):
    logger.info(f"Starting HLS conversion for video ID: {video_id}")

    try:
        video = Video.objects.get(id=video_id)
        input_file = video.file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(video.id))
        os.makedirs(output_dir, exist_ok=True)

        variants = [
            {'scale': '426x240', 'bitrate': '500k', 'variant': '0'},
            {'scale': '640x360', 'bitrate': '1000k', 'variant': '1'},
            {'scale': '1280x720', 'bitrate': '2500k', 'variant': '2'},
            {'scale': '1920x1080', 'bitrate': '5000k', 'variant': '3'}
        ]

        ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"

        for v in variants:
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-vf', f'scale={v["scale"]}',
                '-b:v', v['bitrate'], '-c:v', 'h264', '-preset', 'fast',
                '-c:a', 'aac', '-b:a', '128k',
                '-f', 'hls',
                '-hls_time', '5',
                '-hls_list_size', '0',
                '-hls_segment_filename', os.path.join(output_dir, f'segment_{v["variant"]}_%03d.ts'),
                os.path.join(output_dir, f'variant_{v["variant"]}.m3u8')
            ]
            logger.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

        master_playlist = os.path.join(output_dir, 'master.m3u8')
        master_content = """
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
            variant_0.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
            variant_1.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
            variant_2.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
            variant_3.m3u8
        """
        with open(master_playlist, 'w') as f:
            f.write(master_content.strip())
        video.hls_master_playlist = f"videos/hls/{video.id}/master.m3u8"

        thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_path = os.path.join(thumbnail_dir, f"{video.id}_thumb.jpg")

        thumb_cmd = [
            ffmpeg_path,
            '-ss', '00:00:05',
            '-i', input_file,
            '-vframes', '1',
            '-q:v', '2',
            thumbnail_path
        ]
        subprocess.run(thumb_cmd, check=True)

        video.thumbnail = f'thumbnails/{video.id}_thumb.jpg'

        video.save()
        logger.info(f"Successfully completed HLS conversion for video ID: {video_id}")

    except Exception as e:
        logger.error(f"Error in HLS conversion task: {e}")


@shared_task(queue='default')
def test_celery_task():
    print("Task started!")
    time.sleep(1)
    print("Task completed!")
    return "Task completed"
