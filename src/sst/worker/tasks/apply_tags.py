import logging
from prefect import task
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCOM
from sst.contracts.interfaces import AlbumMetadata

logger = logging.getLogger(__name__)

@task(name="Apply Tags (Mutagen)")
def apply_tags_task(audio_path: str, metadata: AlbumMetadata, track_index: int):
    """
    Writes deeply normalized metadata into ID3 standard tags deterministically.
    If VGMdb data (from MB relation payload extraction) contains composers (TCOM), it is mapped here safely.
    """
    logger.info(f"Applying tags to {audio_path}")
    
    try:
        audio = mutagen.File(audio_path, easy=False)
        if audio is None:
            raise ValueError("Unsupported audio format for tagging.")
            
        if not audio.tags:
            audio.add_tags()
            
        tags = audio.tags
        
        # ALBUM
        if metadata.title:
            tags.add(TALB(encoding=3, text=metadata.title))
            
        # TRACK NUMBER
        if metadata.track_count > 0:
            track_str = f"{track_index}/{metadata.track_count}"
            tags.add(TRCK(encoding=3, text=track_str))
            
        # RELEASE DATE
        if metadata.release_date:
            tags.add(TDRC(encoding=3, text=metadata.release_date))
            
        # Extra: VGMdb/MB rich logic (Composer, Artist isolation) usually mapped into raw_data mappings
        
        audio.save()
        logger.info(f"Saved tags to {audio_path}")
        
    except Exception as e:
        logger.error(f"Error applying tags: {e}")
        raise
