import os
import re
import json
import boto3
from botocore.exceptions import ClientError
from prefect import task
from typing import Optional
from sst.contracts.interfaces import AlbumMetadata

def sanitize_filename(name: str) -> str:
    """Removes invalid filesystem characters and trims whitespace."""
    s = re.sub(r'[<>:"/\\\\|?*]', '_', name)
    return s.strip()

@task(retries=3, retry_delay_seconds=60)
def store_results_task(audio_file_path: str, metadata: Optional[AlbumMetadata], track_index: int, app_id: int, job_id: str, is_success: bool) -> str:
    """
    Uploads audio and JSON metadata to SeaweedFS deterministically.
    Path format: /{status_dir}/{app_id}/{normalized_album}/{disc_number}-{track_number}-{normalized_title}.{ext}
    where status_dir is 'archive' or 'review'.
    """
    ext = os.path.splitext(audio_file_path)[1].lower()
    if not ext:
        ext = ".mp3" # default fallback
        
    s3_endpoint = os.getenv("SEAWEEDFS_S3_ENDPOINT_URL", "http://localhost:8333")
    access_key = os.getenv("SEAWEEDFS_ACCESS_KEY", "admin")
    secret_key = os.getenv("SEAWEEDFS_SECRET_KEY", "admin")
    bucket = os.getenv("SEAWEEDFS_BUCKET", "sst-sounds")
    
    alb_title = sanitize_filename(metadata.title) if metadata else "Unknown Album"
    track_meta = metadata.tracks[track_index] if (metadata and metadata.tracks and track_index < len(metadata.tracks)) else None
    
    t_num = str(track_meta.track_number).zfill(2) if track_meta else "01"
    disc_num = "1" # Hardcoded disc 1 if multi-disc isn't strictly tracked yet
    t_title = sanitize_filename(track_meta.title) if track_meta else "Unknown Track"
    
    status_dir = "archive" if is_success else "review"
    s3_key_audio = f"{status_dir}/{app_id}/{alb_title}/{disc_num}-{t_num}-{t_title}{ext}"
    s3_key_json = s3_key_audio + ".json"
    
    json_data = {
        "app_id": app_id,
        "game_title": alb_title,
        "source": "worker",
        "processing_timestamp": "now",
        "job_id": job_id,
        "album_metadata": metadata.model_dump() if metadata else None
    }
    
    try:
        s3 = boto3.client('s3', 
            endpoint_url=s3_endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Atomically upload Audio first, then JSON
        s3.upload_file(audio_file_path, bucket, s3_key_audio)
        s3.put_object(Bucket=bucket, Key=s3_key_json, Body=json.dumps(json_data, indent=2).encode('utf-8'))
        
        return f"s3://{bucket}/{s3_key_audio}"
    except ClientError as e:
        # ClientError usually falls under RETRYABLE
        raise ValueError(f"RETRYABLE: Failed to upload to SeaweedFS S3: {e}")
    except Exception as e:
        raise ValueError(f"NON_RETRYABLE: Unexpected Storage Upload Error: {e}")
