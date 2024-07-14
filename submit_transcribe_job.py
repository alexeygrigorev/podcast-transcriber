import os
import sys
import json

from urllib.parse import urlparse

import boto3
from yt_dlp import YoutubeDL


S3_BUCKET = os.getenv("S3_BUCKET", "podcast-audio-storage")


def start_transcription_job(
    job_name, s3_uri, output_bucket_name, language_code="en-US"
):
    transcribe = boto3.client("transcribe")
    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": s3_uri},
        MediaFormat="mp3",
        LanguageCode=language_code,
        OutputBucketName=output_bucket_name,
        Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
    )
    return response


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
        return actual_filename[0]
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


def check_file_exists_in_s3(bucket, object_name):
    s3_client = boto3.client("s3")
    try:
        s3_client.head_object(Bucket=bucket, Key=object_name)
        return True
    except:
        return False


def upload_to_s3(bucket, file_name, object_name=None):
    s3_client = boto3.client("s3")
    try:
        object_name = object_name or file_name
        s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False
    return True


def upload_audio_to_s3(output_audio_path, s3_bucket):
    s3_object_name = f"dtc/{output_audio_path}"

    if check_file_exists_in_s3(s3_bucket, s3_object_name):
        print(
            f"File s3://{s3_bucket}/{s3_object_name} already exists in S3. Skipping upload."
        )
        return

    success = upload_to_s3(s3_bucket, output_audio_path, s3_object_name)
    if success:
        print(f"Audio uploaded successfully to s3://{s3_bucket}/{s3_object_name}")
    else:
        print("Failed to upload audio.")
        sys.exit(1)


def main(youtube_id):
    filename = download_audio_from_youtube(youtube_id)

    upload_audio_to_s3(filename, S3_BUCKET)

    job_name = f"podcast-{youtube_id}"
    s3_uri = f"s3://{S3_BUCKET}/dtc/{youtube_id}.mp3"
    output_bucket_name = S3_BUCKET

    print(f"Starting transcription job for YouTube ID: {youtube_id}...")
    start_transcription_job(job_name, s3_uri, output_bucket_name)

    job_data = {
        "job_name": job_name,
        "s3_uri": s3_uri,
        "output_bucket_name": output_bucket_name,
        "youtube_id": youtube_id,
    }

    job_dir = "jobs"
    os.makedirs(job_dir, exist_ok=True)
    with open(f"{job_dir}/{job_name}.json", "w") as f_out:
        json.dump(job_data, f_out)

    print(f"Job submitted and details saved to {job_dir}/{job_name}.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python submit_transcribe_job.py <youtube_id>")
        sys.exit(1)

    youtube_id = sys.argv[1]
    main(youtube_id)
