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

    start: str = Field(..., description="Start timestamp in MM:SS format")
    end: str = Field(..., description="End timestamp in MM:SS format")
    description: str = Field(..., description="Description of the scene")
    reason: Optional[str] = Field(None, description="Why this scene was selected")

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS format."""
        if not re.match(r'^\d{1,2}:\d{2}$', v):
            raise ValueError(f"Timestamp must be in MM:SS format, got: {v}")
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

    @field_validator('start', 'end')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate MM:SS format."""
        if not re.match(r'^\d{1,2}:\d{2}$', v):
            raise ValueError(f"Timestamp must be in MM:SS format, got: {v}")
        return v


class ClipsMetadataOutput(BaseModel):
    """Metadata output for cut clips."""

    source_video: str
    clips: List[ClipMetadata]
