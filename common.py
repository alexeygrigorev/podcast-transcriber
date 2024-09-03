import os
import sys
import json

import boto3

S3_BUCKET = os.getenv("S3_BUCKET", "podcast-audio-storage")


def start_transcription_job(
    job_name, s3_uri, output_bucket_name, language_code="en-US"
):
    print(f"Starting transcription job {job_name} for {s3_uri}...")

    transcribe = boto3.client("transcribe")

    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": s3_uri},
        MediaFormat="mp3",
        LanguageCode=language_code,
        OutputBucketName=output_bucket_name,
        Settings={
            "ShowSpeakerLabels": True,
            "MaxSpeakerLabels": 2,
        },
    )

    return response


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

    uri = f"s3://{s3_bucket}/{s3_object_name}"

    if check_file_exists_in_s3(s3_bucket, s3_object_name):
        print(
            f"File {uri} already exists in S3. Skipping upload."
        )
        return uri

    success = upload_to_s3(s3_bucket, output_audio_path, s3_object_name)
    if not success:
        print("Failed to upload audio.")
        sys.exit(1)

    print(f"Audio uploaded successfully to {uri}")
    return uri
        



def save_job(youtube_id, job_name, s3_uri, output_bucket_name):
    job_data = {
        "job_name": job_name,
        "s3_uri": s3_uri,
        "output_bucket_name": output_bucket_name,
        "youtube_id": youtube_id,
    }

    job_dir = "jobs"
    os.makedirs(job_dir, exist_ok=True)

    job_file = f"{job_dir}/{job_name}.json"

    with open(job_file, "w") as f_out:
        json.dump(job_data, f_out, indent=2)

    print(f"Job submitted and details saved to {job_file}")

    return job_file
