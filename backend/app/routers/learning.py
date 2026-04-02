from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.learning_assistant import (
    learning_assistant,
    LearningPath,
    ProgressTracking
)

router = APIRouter(prefix="/learning")


class ExplainConceptRequest(BaseModel):
    concept: str
    context: str = ""


class GenerateTutorialRequest(BaseModel):
    topic: str
    skill_level: str = "beginner"


class TrackProgressRequest(BaseModel):
    user_id: str


class UpdateProgressRequest(BaseModel):
    user_id: str
    concept: str
    mastery_level: int  # 0-100


class RecommendTopicRequest(BaseModel):
    user_id: str


class ConceptExplanationResponse(BaseModel):
    found: bool
    concept: str
    category: Optional[str] = None
    explanation: str
    examples: List[str]
    related_concepts: List[str]
    difficulty: str


class TutorialResponse(BaseModel):
    id: str
    title: str
    topic: str
    skill_level: str
    content: str
    code_examples: List[str]
    exercises: List[str]
    estimated_minutes: int
    steps: List[Dict[str, str]] = []
    prerequisites: List[str] = []


class ProgressTrackingResponse(BaseModel):
    user_id: str
    completed_topics: List[str]
    current_topic: str
    progress_percentage: float
    streak_days: int
    last_activity: Optional[str] = None


class LearningProgressItem(BaseModel):
    concept: str
    mastery_level: int
    last_practiced: str
    practice_count: int


class ExerciseResponse(BaseModel):
    exercise: str


class RecommendationResponse(BaseModel):
    next_topic: str
    recommended_concepts: List[str]


@router.post("/explain", response_model=ConceptExplanationResponse)
async def explain_concept(request: ExplainConceptRequest):
    """Explain a programming concept with optional context"""
    try:
        explanation = learning_assistant.explain_concept(
            request.concept,
            request.context
        )
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tutorial", response_model=TutorialResponse)
async def generate_tutorial(request: GenerateTutorialRequest):
    """Generate or retrieve a tutorial for a topic"""
    try:
        tutorial = learning_assistant.generate_tutorial(
            request.topic,
            request.skill_level
        )
        return tutorial
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tutorials")
async def get_all_tutorials():
    """Get all available tutorials"""
    try:
        tutorials = learning_assistant.get_all_tutorials()
        return {"tutorials": tutorials}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tutorials/{tutorial_id}")
async def get_tutorial_by_id(tutorial_id: str):
    """Get a specific tutorial by ID"""
    try:
        tutorial = learning_assistant.get_tutorial_by_id(tutorial_id)
        if tutorial:
            return tutorial
        raise HTTPException(status_code=404, detail="Tutorial not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/progress", response_model=List[LearningProgressItem])
async def track_progress(request: TrackProgressRequest):
    """Track user learning progress"""
    try:
        progress = learning_assistant.track_progress(request.user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/progress/detailed", response_model=ProgressTrackingResponse)
async def get_detailed_progress(request: TrackProgressRequest):
    """Get detailed progress tracking for a user"""
    try:
        progress = learning_assistant.get_detailed_progress(request.user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/progress/update")
async def update_progress(request: UpdateProgressRequest):
    """Update user's learning progress for a concept"""
    try:
        result = learning_assistant.update_progress(
            request.user_id,
            request.concept,
            request.mastery_level
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_next_topic(request: RecommendTopicRequest):
    """Recommend the next topic and concepts to learn"""
    try:
        next_topic = learning_assistant.recommend_next_topic(request.user_id)
        recommended_concepts = learning_assistant.get_recommended_concepts(request.user_id)
        return {
            "next_topic": next_topic,
            "recommended_concepts": recommended_concepts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/paths", response_model=List[LearningPath])
async def get_learning_paths(skill_level: str = "all"):
    """Get available learning paths"""
    try:
        paths = learning_assistant.get_learning_paths(skill_level)
        return paths
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/concepts/{concept}/related")
async def get_related_concepts(concept: str):
    """Get concepts related to a given concept"""
    try:
        related = learning_assistant.get_concept_related(concept)
        return {"concept": concept, "related_concepts": related}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/exercise", response_model=ExerciseResponse)
async def suggest_exercise(topic: str):
    """Suggest a coding exercise for a topic"""
    try:
        exercise = learning_assistant.suggest_exercise(topic)
        return {"exercise": exercise}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/concepts")
async def get_all_concepts():
    """Get all available programming concepts"""
    try:
        concepts = list(learning_assistant.concept_database.keys())
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
