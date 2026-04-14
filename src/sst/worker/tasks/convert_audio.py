import os
import subprocess
import json
from prefect import task

LOSSLESS_EXTS = {".flac", ".wav", ".alac", ".ape", ".m4a"}

def get_audio_info(file_path: str):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "audio":
            sample_rate = int(stream.get("sample_rate", "44100"))
            bits = int(stream.get("bits_per_raw_sample", stream.get("bits_per_sample", "16")))
            codec = stream.get("codec_name", "")
            # Validate m4a if it's lossless (alac) vs lossy (aac)
            if file_path.endswith(".m4a") and codec != "alac":
                return None  # It's lossy m4a
            return {"sample_rate": sample_rate, "bits": bits}
    return None

@task(retries=1, retry_delay_seconds=10)
def convert_lossless_to_aiff_task(audio_file_path: str) -> str:
    """
    Converts lossless files to AIFF.
    Upper bounds: 24-bit / 48kHz.
    Returns the path to the newly generated AIFF file.
    Deletes the original file upon successful conversion.
    """
    if not os.path.exists(audio_file_path):
        raise ValueError(f"File not found: {audio_file_path}")
        
    ext = os.path.splitext(audio_file_path)[1].lower()
    
    if ext not in LOSSLESS_EXTS:
        return audio_file_path  # Nothing to do for lossy files (.mp3, etc.)

    info = get_audio_info(audio_file_path)
    if not info:
        return audio_file_path # Could not parse or lossy internal
        
    out_path = os.path.splitext(audio_file_path)[0] + ".aiff"
    
    cmd = ["ffmpeg", "-y", "-i", audio_file_path]
    
    # Calculate target parameters bounded by 24bit / 48kHz
    target_sample_rate = min(info["sample_rate"], 48000)
    target_bits = min(info["bits"], 24)
    
    # AIFF standard pcm format map based on bits
    pcm_format = "pcm_s16be" # baseline
    if target_bits > 16:
        pcm_format = "pcm_s24be"
        
    cmd.extend(["-c:a", pcm_format])
    
    if target_sample_rate != info["sample_rate"]:
        # Only resample if we are actually downsampling
        cmd.extend(["-ar", str(target_sample_rate)])
        
    cmd.append(out_path)
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        # Verify it was successfully written
        if os.path.exists(out_path):
            os.remove(audio_file_path)
            return out_path
        else:
            raise ValueError(f"ffmpeg completed but {out_path} not found.")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"NON_RETRYABLE: ffmpeg conversion failed on {audio_file_path}: {e.stderr.decode('utf-8', 'ignore')}")
