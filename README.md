# Podcast Transcriber

## Overview

The Podcast Transcriber project is designed to automate the process of transcribing podcast episodes and managing those transcripts. It allows users to submit transcription jobs, check their statuses, and handle the resulting transcripts. This tool is particularly useful for podcast creators who need to efficiently manage transcripts, synchronize them with audio, or edit content.

## How to Use

### Programmatic Approach

1. **Submit a Transcription Job**: Use the `submit_transcribe_job.py` script to submit a new transcription job. This script downloads an audio file from YouTube using the provided YouTube video ID, uploads it to an S3 bucket, and starts a transcription job.
   
```bash
python submit_transcribe_job.py <youtube_video_id>
```

2. **Check Transcription Job Status**: Use the `check_transcribe_jobs.py` script to check the status of ongoing transcription jobs. This helps you monitor whether your submitted jobs are complete and ready for processing.
    
```bash
python check_transcribe_jobs.py
```

3. **Process Transcripts**: Once transcripts are ready, they are stored in the `transcripts/raw` directory. These files are plain text with time-coded entries to synchronize with the podcast audio.

### Post-Processing the Transcripts

After transcription jobs are completed, the resulting transcripts are saved in the `transcripts/raw` directory. These files include timecodes that allow for easy navigation and editing. To refine and finalize these transcripts, use ChatGPT as follows:

1. **Editing with ChatGPT**:

Open each transcript file and use ChatGPT to refine and edit the text. Follow the "Prompt for Correcting" in the `prompt.md` file to:

- Remove unnecessary filler words.
- Correct grammatical errors and improve sentence clarity.
- Use specific names for the host and guest.
- Keep the structure with timestamps for synchronization.
    
Refer to the **Prompt for Correcting** section in the `prompt.md` file for detailed instructions on how to use this prompt.

2. **Creating Titles and Sections**:

- Use ChatGPT to generate a structured outline with titles for key topics discussed in the podcast. Follow the "Prompt for Titles" in the `prompt.md` file to create topic titles and provide timestamps.

Refer to the **Prompt for Titles** section in the `prompt.md` file for detailed instructions on how to use this prompt.

### Using GitHub Actions

This project supports automation through GitHub Actions, allowing users to submit transcription jobs and check job statuses directly from the GitHub interface.

1. **Submit a Transcription Job via GitHub Actions**:

- Navigate to the "Actions" tab in your GitHub repository.
- Select the "Submit Transcribe Job" workflow from the list of available workflows.
- Click on the "Run workflow" button.
- Provide the required `YouTube ID` for the audio file you wish to transcribe and start the workflow.

The workflow is defined in `.github/workflows/submit_transcribe_job.yml` and will automatically handle the submission of a new transcription job using the provided YouTube ID.

2. **Check Transcription Job Status via GitHub Actions**:

- Navigate to the "Actions" tab in your GitHub repository.
- Select the "Check Transcribe Jobs" workflow.
- Click on the "Run workflow" button to manually trigger a check on the transcription job statuses.

The workflow is defined in `.github/workflows/check_transcribe_jobs.yml` and will run the `check_transcribe_jobs.py` script to update the status of ongoing jobs.

### Environment Variables

For both programmatic and GitHub Actions usage, ensure that the following environment variables are set (typically in the GitHub Secrets for GitHub Actions):

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `AWS_REGION`
- `S3_BUCKET` (default: `podcast-audio-storage`)

These are used to authenticate and interact with the cloud services handling the transcription jobs.

## File Descriptions

- `.envrc_template`: Template for environment variables. It should be copied to `.envrc` and filled with necessary configuration details like API keys.
- `.github/`: Contains GitHub workflows for automating tasks such as testing and deployment.
- `Pipfile` & `Pipfile.lock`: Define the Python environment and dependencies needed to run the project.
- `check_transcribe_jobs.py`: Script to check the status of transcription jobs submitted to the external service.
- `jobs/`: Directory to store job-related metadata and temporary files.
- `prompt.md`: Contains the prompt or instructions for the transcription process, including sections for correcting transcripts and generating titles.
- `submit_transcribe_job.py`: Script to submit new transcription jobs.
- `transcripts/raw/`: Directory for storing raw text transcripts with timecodes.

## Getting Started

1. Clone the repository:
   
```bash
git clone <repository_url>
cd podcast-transcriber-main
```

2. Install dependencies using Pipenv:
    
```bash
pipenv install
```

3. Set up environment variables by copying `.envrc_template` to `.envrc` and filling in the required API keys and settings.

4. Run transcription jobs and manage transcripts as outlined in the usage section.

## Contributing

Contributions are welcome! Please create a new branch for each feature or bug fix, and submit a pull request for review.

