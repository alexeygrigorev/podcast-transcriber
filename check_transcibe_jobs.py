import os

import json
from urllib.parse import urlparse

import boto3


S3_BUCKET = os.getenv("S3_BUCKET", "podcast-audio-storage")


def convert_https_to_s3(http_url):
    parsed_url = urlparse(http_url)

    split = parsed_url.path.split('/')
    bucket_name = split[1]
    s3_key = '/'.join(split[2:])

    return bucket_name, s3_key


def check_transcription_job(job_name):
    transcribe = boto3.client("transcribe")

    response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = response["TranscriptionJob"]["TranscriptionJobStatus"]

    if status in ["COMPLETED", "FAILED"]:
        https_url = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        return {"status": status, "https_url": https_url}

    return {"status": status}


def download_transcript_file(http_url, local_file_path):
    s3 = boto3.client("s3")
    bucket_name, s3_key = convert_https_to_s3(http_url)
    print(f"Downloading transcript file from s3://{bucket_name}/{s3_key} to {local_file_path}")
    s3.download_file(bucket_name, s3_key, local_file_path)


def format_timestamp(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"


def parse_transcript(results):
    transcript_text = ""
    current_speaker = None
    timestamp = "0:00"

    names = {"spk_0": "Host", "spk_1": "Guest"}

    for item in results["items"]:
        if "speaker_label" in item:
            speaker = item["speaker_label"]

        if "start_time" in item:
            start_time = float(item["start_time"])
            timestamp = format_timestamp(start_time)

        if speaker != current_speaker:
            current_speaker = speaker
            speaker_name = names.get(speaker, speaker)
            transcript_text += f"\n\n{timestamp}\n{speaker_name}\n"

        if item["type"] == "pronunciation":
            word = item["alternatives"][0]["content"]
            transcript_text += word + " "
        elif item["type"] == "punctuation":
            punctuation = item["alternatives"][0]["content"]
            transcript_text = transcript_text.rstrip() + punctuation + " "

    return transcript_text.strip()


def process_job(job_file):
    with open(job_file, "r") as f:
        job_data = json.load(f)

    job_name = job_data["job_name"]
    youtube_id = job_data["youtube_id"]
    local_file_path = f"podcast-{youtube_id}.json"
    output_transcript_path = f"transcripts/raw/{youtube_id}.txt"

    print(f"Checking status of job {job_name}...")
    result = check_transcription_job(job_name)

    if result["status"] == "COMPLETED":
        transcript_uri = result["https_url"]
        print(f"Transcription completed. Transcript available at: {transcript_uri}")

        download_transcript_file(transcript_uri, local_file_path)

        with open(local_file_path, "rt") as f_in:
            transcript_job = json.load(f_in)

        results = transcript_job["results"]
        transcript_text = parse_transcript(results)

        os.makedirs(os.path.dirname(output_transcript_path), exist_ok=True)
        with open(output_transcript_path, "w") as f_out:
            f_out.write(transcript_text)

        print(f"Transcript saved to {output_transcript_path}")
        os.remove(job_file)

    elif result["status"] == "FAILED":
        print(f"Transcription job {job_name} failed.")
        failed_dir = "failed_jobs"
        os.makedirs(failed_dir, exist_ok=True)
        os.rename(job_file, f"{failed_dir}/{os.path.basename(job_file)}")

    else:
        print(f"Transcription job {job_name} is still in progress...")


def main():
    job_dir = "jobs"
    for job_file in os.listdir(job_dir):
        if not job_file.endswith(".json"):
            print(f"Skipping non-JSON file: {job_file}")
            continue

        job_file_path = os.path.join(job_dir, job_file)
        if os.path.isfile(job_file_path):
            process_job(job_file_path)


if __name__ == "__main__":
    main()
