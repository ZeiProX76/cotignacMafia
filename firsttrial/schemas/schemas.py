"""Pydantic models for validating pipeline data structures."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re


class Sentence(BaseModel):
    """Single sentence with timestamps from audio transcription."""

    start: str = Field(..., description="Start timestamp in MM:SS format")
    end: str = Field(..., description="End timestamp in MM:SS format")
    text: str = Field(..., description="Transcribed sentence text")

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS format."""
        if not re.match(r'^\d{1,2}:\d{2}$', v):
            raise ValueError(f"Timestamp must be in MM:SS format, got: {v}")
        return v


class TranscriptionOutput(BaseModel):
    """Output schema for step 1: Audio transcription."""

    sentences: List[Sentence] = Field(..., description="List of transcribed sentences with timestamps")


class ScreenActivity(BaseModel):
    """Screen activity detected in video (no visible humans)."""

    start: str = Field(..., description="Start timestamp in MM:SS format")
    end: str = Field(..., description="End timestamp in MM:SS format")
    description: str = Field(..., description="Description of what's happening on screen")
    activity_type: Optional[str] = Field(None, description="Type of activity (e.g., 'UI interaction', 'code typing', 'animation')")

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS format."""
        if not re.match(r'^\d{1,2}:\d{2}$', v):
            raise ValueError(f"Timestamp must be in MM:SS format, got: {v}")
        return v


class ScreenAnalysisOutput(BaseModel):
    """Output schema for step 2: Screen activity analysis."""

    activities: List[ScreenActivity] = Field(..., description="List of detected screen activities")


class SceneSelection(BaseModel):
    """Selected scene for final video clips."""

    start: str = Field(..., description="Start timestamp in MM:SS or MM:SS.mmm format")
    end: str = Field(..., description="End timestamp in MM:SS or MM:SS.mmm format")
    description: str = Field(..., description="Description of the scene")
    reason: Optional[str] = Field(None, description="Why this scene was selected")

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS or MM:SS.mmm format (accepts milliseconds)."""
        if not re.match(r'^\d{1,2}:\d{2}(\.\d{1,3})?$', v):
            raise ValueError(f"Timestamp must be in MM:SS or MM:SS.mmm format, got: {v}")
        return v


class TargetedAnalysisOutput(BaseModel):
    """Output schema for step 4: Targeted scene selection."""

    scenes: List[SceneSelection] = Field(..., description="List of selected scenes for clipping")


class SegmentAnalysis(BaseModel):
    """Analysis of a single video segment for human detection."""

    segment: int = Field(..., description="Segment number (1-10)")
    start_seconds: float = Field(..., description="Segment start time in seconds")
    end_seconds: float = Field(..., description="Segment end time in seconds")
    description: str = Field(..., description="Detailed description of what's happening in this segment")
    isHuman: bool = Field(..., description="Whether a real human person with full face is visible in this segment")


class HumanDetection(BaseModel):
    """Human presence detection result for a clip after iterative removal."""

    source_filename: str = Field(..., description="Original clip filename")
    output_filename: str = Field(..., description="Output filename for clean clip")
    status: Literal["clean", "unsaveable", "failed"] = Field(..., description="Final status after attempts")
    clean_start: Optional[str] = Field(None, description="Safe start timestamp (MM:SS.S)")
    clean_end: Optional[str] = Field(None, description="Safe end timestamp (MM:SS.S)")
    attempts: int = Field(..., description="Number of attempts made")
    final_result: Literal["none", "start", "end", "all"] = Field(..., description="Final detection result")
    video_id: Optional[str] = Field(None, description="Source video identifier (e.g., 'video_001')")
    original_context: Optional[dict] = Field(None, description="Original scene context from step 4")
    segment_analyses: Optional[List[SegmentAnalysis]] = Field(None, description="VLM analysis results for each 10% segment")
    gpt5_reasoning: Optional[str] = Field(None, description="GPT-5 reasoning for timestamp decision")


class OptimizationOutput(BaseModel):
    """Output schema for step 6: Clip optimization."""

    clips: List[HumanDetection] = Field(..., description="List of clips with human detection results")


class ClipMetadata(BaseModel):
    """Metadata for a single cut clip."""

    clip_number: int
    filename: str
    start: str
    end: str
    description: str
    reason: Optional[str] = None
    video_id: Optional[str] = Field(None, description="Source video identifier (e.g., 'video_001')")

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS or MM:SS.mmm format (accepts milliseconds)."""
        if not re.match(r'^\d{1,2}:\d{2}(\.\d{1,3})?$', v):
            raise ValueError(f"Timestamp must be in MM:SS or MM:SS.mmm format, got: {v}")
        return v


class ClipsMetadataOutput(BaseModel):
    """Metadata output for cut clips."""

    source_video: str
    clips: List[ClipMetadata]


# ==============================================================================
# MULTI-VIDEO PIPELINE SCHEMAS (Steps 2-8 with multiple videos)
# ==============================================================================


class VideoConfig(BaseModel):
    """Configuration for a single video source."""

    id: str = Field(..., description="Unique video identifier (e.g., 'video_001')")
    name: str = Field(..., description="Human-readable video name")
    url: str = Field(..., description="Video URL (for VLM API calls)")
    local_path: str = Field(..., description="Local video file path (for FFmpeg)")
    priority: int = Field(1, description="Video priority (higher = more important)")


class VideosConfig(BaseModel):
    """Configuration for multiple video sources."""

    videos: List[VideoConfig] = Field(..., description="List of video configurations")


class ClipRankingCriteria(BaseModel):
    """Ranking criteria scores for a single clip (0-100 each)."""

    human_visibility_score: int = Field(..., ge=0, le=100, description="100 = zero humans visible, 0 = humans throughout")
    animation_completeness_score: int = Field(..., ge=0, le=100, description="100 = animation fully complete, 0 = severely truncated")
    reason_match_score: int = Field(..., ge=0, le=100, description="100 = perfectly matches selection reason, 0 = doesn't match")
    broll_quality_score: int = Field(..., ge=0, le=100, description="100 = perfect for overlay, 0 = poor for overlay")

    human_reasoning: str = Field(..., description="Explanation for human visibility score")
    animation_reasoning: str = Field(..., description="Explanation for animation completeness score")
    reason_reasoning: str = Field(..., description="Explanation for reason match score")
    broll_reasoning: str = Field(..., description="Explanation for B-roll quality score")


class ClipRanking(BaseModel):
    """Complete ranking for a single clip."""

    video_id: str = Field(..., description="Source video identifier")
    clip_filename: str = Field(..., description="Clip filename")
    clip_path: str = Field(..., description="Full path to clip file")

    criteria: ClipRankingCriteria = Field(..., description="Detailed ranking criteria and scores")
    total_score: int = Field(..., ge=0, le=400, description="Sum of all 4 criteria scores (0-400)")
    normalized_score: float = Field(..., ge=0, le=100, description="Normalized score (0-100)")
    rank: int = Field(..., ge=1, description="Rank among all clips (1 = best)")

    # Context from previous steps
    original_context: Optional[dict] = Field(None, description="Original context from step 5 (ClipMetadata)")
    optimization_result: Optional[dict] = Field(None, description="Optimization result from step 6 (HumanDetection)")


class RankingsOutput(BaseModel):
    """Output schema for step 6.5: All clip rankings."""

    total_clips: int = Field(..., description="Total number of clips ranked")
    rankings: List[ClipRanking] = Field(..., description="List of all clips ranked (sorted by total_score descending)")


class Top15Clip(BaseModel):
    """A clip selected for the top 15 final set."""

    rank: int = Field(..., ge=1, le=15, description="Rank in top 15 (1 = best)")
    video_id: str = Field(..., description="Source video identifier")

    # File paths
    original_filename: str = Field(..., description="Original clip filename from clips_final/")
    top15_filename: str = Field(..., description="New filename in top15/ directory")
    final_path: str = Field(..., description="Full path in top15/ directory")

    # Ranking info
    total_score: int = Field(..., description="Total ranking score from step 6.5")
    normalized_score: float = Field(..., description="Normalized score (0-100)")
    ranking_details: ClipRankingCriteria = Field(..., description="Detailed ranking criteria")

    # Timeline metadata
    duration_seconds: float = Field(..., description="Clip duration in seconds")
    clean_start: Optional[str] = Field(None, description="Clean start timestamp (MM:SS.S) from step 6")
    clean_end: Optional[str] = Field(None, description="Clean end timestamp (MM:SS.S) from step 6")
    description: str = Field(..., description="Clip description from original selection")
    reason: Optional[str] = Field(None, description="Reason for original selection")


class Top15Selection(BaseModel):
    """Output schema for step 7: Top 15 clips selection."""

    selection_timestamp: str = Field(..., description="When the selection was made (ISO format)")
    total_candidates: int = Field(..., description="Total number of clips that were candidates")
    selected_clips: List[Top15Clip] = Field(..., description="The 15 selected clips in ranked order")
    selection_criteria: str = Field(..., description="GPT-5 Mini's reasoning for selection")
