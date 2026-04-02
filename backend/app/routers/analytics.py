from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.analytics import (
    analytics_dashboard,
    AnalyticsProfile,
    ProductivityMetric,
    Insight
)

router = APIRouter(prefix="/analytics")

class TrackCodingRequest(BaseModel):
    user_id: str
    code_snippet: str
    language: str

class TrackProductivityRequest(BaseModel):
    user_id: str
    lines_of_code: int
    functions_written: int = 0
    bugs_fixed: int = 0
    code_reviews: int = 0
    time_spent_coding: int  # minutes

class UpdateSkillRequest(BaseModel):
    user_id: str
    skill: str
    level: int  # 1-10

class PredictProductivityRequest(BaseModel):
    user_id: str
    days_ahead: int = 7

class LeaderboardRequest(BaseModel):
    metric: str = "lines_of_code"
    limit: int = 10

@router.post("/patterns")
async def track_coding_patterns(request: TrackCodingRequest):
    """Analyze coding habits and patterns"""
    try:
        patterns = analytics_dashboard.track_coding_patterns(
            request.user_id,
            request.code_snippet,
            request.language
        )
        return {"patterns": patterns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/productivity")
async def track_productivity(request: TrackProductivityRequest):
    """Track user productivity metrics"""
    try:
        metric = ProductivityMetric(
            date=datetime.now(),
            lines_of_code=request.lines_of_code,
            functions_written=request.functions_written,
            bugs_fixed=request.bugs_fixed,
            code_reviews=request.code_reviews,
            time_spent_coding=request.time_spent_coding
        )

        analytics_dashboard.track_productivity(request.user_id, metric)
        return {"message": "Productivity tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user analytics profile"""
    try:
        profile = analytics_dashboard.get_profile(user_id)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights")
async def generate_insights(user_id: str):
    """Generate actionable insights from coding data"""
    try:
        insights = analytics_dashboard.generate_insights(user_id)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict_productivity(request: PredictProductivityRequest):
    """Predict future productivity trends"""
    try:
        prediction = analytics_dashboard.predict_productivity(
            request.user_id,
            request.days_ahead
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skills")
async def update_skill_progress(request: UpdateSkillRequest):
    """Update user skill progress"""
    try:
        analytics_dashboard.update_skill_progress(
            request.user_id,
            request.skill,
            request.level
        )
        return {"message": "Skill progress updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leaderboard")
async def get_leaderboard(request: LeaderboardRequest):
    """Get leaderboard based on specified metric"""
    try:
        leaderboard = analytics_dashboard.get_leaderboard(
            request.metric,
            request.limit
        )
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{user_id}")
async def get_analytics_summary(user_id: str):
    """Get comprehensive analytics summary for user"""
    try:
        profile = analytics_dashboard.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Calculate summary statistics
        total_lines = sum(m.lines_of_code for m in profile.productivity_history)
        total_time = sum(m.time_spent_coding for m in profile.productivity_history)
        avg_lines_per_session = total_lines / len(profile.productivity_history) if profile.productivity_history else 0
        favorite_language = max(set(profile.favorite_languages), key=profile.favorite_languages.count) if profile.favorite_languages else "None"

        summary = {
            "user_id": user_id,
            "total_lines_of_code": total_lines,
            "total_hours_coded": profile.total_hours_coded,
            "streak_days": profile.streak_days,
            "favorite_language": favorite_language,
            "average_lines_per_session": round(avg_lines_per_session, 2),
            "skills": profile.skill_progress,
            "recent_patterns": [p.pattern_type for p in profile.coding_patterns[-5:] if profile.coding_patterns]
        }

        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/profile/{user_id}")
async def reset_profile(user_id: str):
    """Reset user analytics profile"""
    try:
        # Delete profile file
        import os
        profile_file = f"./analytics/{user_id}_profile.json"
        if os.path.exists(profile_file):
            os.remove(profile_file)

        # Remove from memory
        if user_id in analytics_dashboard.profiles:
            del analytics_dashboard.profiles[user_id]

        return {"message": "Profile reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
