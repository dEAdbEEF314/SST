import pytest
from prefect.testing.utilities import prefect_test_harness
from sst.worker.tasks.scoring_engine import score_candidates_task, ScoringTarget
from sst.contracts.interfaces import Candidate, AlbumMetadata, Track

@pytest.fixture(autouse=True)
def prefect_test_fixture():
    with prefect_test_harness():
        yield

def test_score_candidates_success():
    target = ScoringTarget(album_title="Super Soundtrack", track_count=10, artist="Nobuo", release_date="2020-01-01")
    
    metadata = AlbumMetadata(
        title="Super Soundtrack",
        artists=["Nobuo"],
        tracks=[Track(track_number=i, title=f"T{i}", duration=100) for i in range(1, 11)],
        release_date="2020-05-05", # matches year
        quality_score=0.0
    )
    
    c1 = Candidate(source="musicbrainz", score=0.5, metadata=metadata, raw_data={"formats": ["Digital Media"]})
    c2 = Candidate(source="vgmdb", score=0.5, metadata=metadata, raw_data={})
    
    # Intentionally ruin c2's title to give c1 a large margin
    c2.metadata.title = "Completely Unrelated"
    
    result = score_candidates_task([c1, c2], target)
    
    # c1 should have: 50 (title) + 40 (track) + 20 (date) + 50 (artist) + 30 (digital media) = 190. (190/190 = 1.0)
    # c2 will have huge penalty.
    assert result.success is True
    assert result.best_candidate.source == "musicbrainz"
    assert result.best_candidate.score == 1.0
    assert result.reason == "SUCCESS"

def test_score_candidates_ambiguous_review():
    target = ScoringTarget(album_title="Super Soundtrack", track_count=10, artist="Nobuo", release_date="2020-01-01")
    
    metadata = AlbumMetadata(
        title="Super Soundtrack",
        artists=["Nobuo"],
        tracks=[Track(track_number=i, title=f"T{i}", duration=100) for i in range(1, 11)],
        release_date="2020-05-05",
        quality_score=0.0
    )
    
    # Create two identical strong candidates (margin is 0)
    c1 = Candidate(source="vgmdb", score=0.5, metadata=metadata)
    c2 = Candidate(source="musicbrainz", score=0.5, metadata=metadata, raw_data={"formats": []})
    
    result = score_candidates_task([c1, c2], target)
    
    assert result.success is False
    assert "REVIEW" in result.reason
    assert "margin < 0.05" in result.reason

def test_score_candidates_fail_low_score():
    target = ScoringTarget(album_title="Super Soundtrack", track_count=10, artist="Nobuo", release_date="2020-01-01")
    
    metadata = AlbumMetadata(
        title="Bad Title",
        artists=["Someone Else"],
        tracks=[Track(track_number=1, title="T1", duration=100)], # track count mismatch
        release_date="1999-05-05",
        quality_score=0.0
    )
    
    c1 = Candidate(source="vgmdb", score=0.5, metadata=metadata)
    
    result = score_candidates_task([c1], target)
    
    assert result.success is False
    assert "REVIEW" in result.reason
    assert result.best_candidate.score < 0.55
