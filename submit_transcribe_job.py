import os
import sys

from yt_dlp import YoutubeDL

from common import (
    S3_BUCKET,
    start_transcription_job,
    upload_audio_to_s3,
    save_job,
)


def download_audio_from_youtube_main(youtube_id):
    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
    output_audio_path_template = f"{youtube_id}.%(ext)s"

    actual_filename = []

    def my_hook(d):
        if d["status"] == "finished":
            actual_filename.append(d["filename"])

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_audio_path_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [my_hook],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    if actual_filename:
        filename = actual_filename[0]
        if filename.endswith(".webm"):
            filename = filename.replace(".webm", ".mp3")
        return filename

    return output_audio_path_template % "mp3"


def download_audio_from_youtube(youtube_id):
    expected_output_audio_path = f"{youtube_id}.mp3"

    if not os.path.exists(expected_output_audio_path):
        actual_filename = download_audio_from_youtube_main(youtube_id)
        if not actual_filename:
            print("Failed to download audio.")
            sys.exit(1)
    else:
        print(
            f"File {expected_output_audio_path} already exists locally. Skipping download."
        )
        actual_filename = expected_output_audio_path

    return actual_filename


def main(youtube_id):
    filename = download_audio_from_youtube(youtube_id)

    upload_audio_to_s3(filename, S3_BUCKET)

    job_name = f"podcast-{youtube_id}"
    s3_uri = f"s3://{S3_BUCKET}/dtc/{youtube_id}.mp3"
    output_bucket_name = S3_BUCKET

    print(f"Starting transcription job for YouTube ID: {youtube_id}...")
    start_transcription_job(job_name, s3_uri, output_bucket_name)

    save_job(
        youtube_id=youtube_id,
        job_name=job_name,
        s3_uri=s3_uri,
        output_bucket_name=output_bucket_name,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python submit_transcribe_job.py <youtube_id>")
        sys.exit(1)

    youtube_id = sys.argv[1]
    main(youtube_id)
