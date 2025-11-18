"""Pydantic schemas for pipeline data validation."""

from .schemas import (
    Sentence,
    TranscriptionOutput,
    ScreenActivity,
    ScreenAnalysisOutput,
    SceneSelection,
    TargetedAnalysisOutput,
    SegmentAnalysis,
    HumanDetection,
    OptimizationOutput,
    ClipMetadata,
    ClipsMetadataOutput,
    # Multi-video schemas
    VideoConfig,
    VideosConfig,
    ClipRankingCriteria,
    ClipRanking,
    RankingsOutput,
    Top15Clip,
    Top15Selection,
)

__all__ = [
    'Sentence',
    'TranscriptionOutput',
    'ScreenActivity',
    'ScreenAnalysisOutput',
    'SceneSelection',
    'TargetedAnalysisOutput',
    'SegmentAnalysis',
    'HumanDetection',
    'OptimizationOutput',
    'ClipMetadata',
    'ClipsMetadataOutput',
    # Multi-video schemas
    'VideoConfig',
    'VideosConfig',
    'ClipRankingCriteria',
    'ClipRanking',
    'RankingsOutput',
    'Top15Clip',
    'Top15Selection',
]
