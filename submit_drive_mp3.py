import os
import sys

import subprocess

from common import (
    S3_BUCKET,
    start_transcription_job,
    upload_audio_to_s3,
    save_job,
)


def download_from_drive(file_id, output_filename):
    if os.path.exists(output_filename):
        print(f"File {output_filename} already exists. Skipping download.")
        return

    url = f"https://drive.google.com/uc?id={file_id}"
    subprocess.run(["wget", "-O", output_filename, url], check=True)


def main(file_id, youtube_id):
    local_audio_path = f"{youtube_id}.mp3"
    download_from_drive(file_id, local_audio_path)

    s3_uri = upload_audio_to_s3(local_audio_path, S3_BUCKET)

    job_name = f"podcast-{youtube_id}"
    output_bucket_name = S3_BUCKET

    print(f"Starting transcription job for audio file: {local_audio_path}...")
    start_transcription_job(job_name, s3_uri, output_bucket_name)

    save_job(
        youtube_id=youtube_id,
        job_name=job_name,
        s3_uri=s3_uri,
        output_bucket_name=output_bucket_name,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python submit_drive_mp3.py <file_id> <youtube_id>")
        sys.exit(1)

    file_id = sys.argv[1]
    youtube_id = sys.argv[2]
    main(file_id, youtube_id)
