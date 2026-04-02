from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

class CodingPattern(BaseModel):
    pattern_type: str
    frequency: int
    last_used: datetime
    efficiency_score: float  # 0-1 scale

class ProductivityMetric(BaseModel):
    date: datetime
    lines_of_code: int
    functions_written: int
    bugs_fixed: int
    code_reviews: int
    time_spent_coding: int  # minutes

class Insight(BaseModel):
    title: str
    description: str
    severity: str  # low, medium, high, positive
    recommendation: str
    related_metrics: List[str]

class AnalyticsProfile(BaseModel):
    user_id: str
    coding_patterns: List[CodingPattern]
    productivity_history: List[ProductivityMetric]
    insights: List[Insight]
    streak_days: int
    total_hours_coded: int
    favorite_languages: List[str]
    skill_progress: Dict[str, int]  # skill: level (1-10)

class AnalyticsDashboard:
    def __init__(self, analytics_dir: str = "./analytics"):
        self.analytics_dir = analytics_dir
        os.makedirs(analytics_dir, exist_ok=True)
        self.profiles: Dict[str, AnalyticsProfile] = self._load_profiles()

    def _load_profiles(self) -> Dict[str, AnalyticsProfile]:
        """Load user profiles from storage"""
        profiles = {}
        for filename in os.listdir(self.analytics_dir):
            if filename.endswith("_profile.json"):
                try:
                    with open(os.path.join(self.analytics_dir, filename), 'r') as f:
                        data = json.load(f)
                        # Convert datetime strings back to datetime objects
                        for metric in data.get("productivity_history", []):
                            metric["date"] = datetime.fromisoformat(metric["date"])
                        for pattern in data.get("coding_patterns", []):
                            pattern["last_used"] = datetime.fromisoformat(pattern["last_used"])
                        profile = AnalyticsProfile(**data)
                        profiles[profile.user_id] = profile
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
        return profiles

    def track_coding_patterns(self, user_id: str, code_snippet: str, language: str) -> List[CodingPattern]:
        """Analyze coding habits and patterns"""
        if user_id not in self.profiles:
            self.profiles[user_id] = AnalyticsProfile(
                user_id=user_id,
                coding_patterns=[],
                productivity_history=[],
                insights=[],
                streak_days=0,
                total_hours_coded=0,
                favorite_languages=[],
                skill_progress={}
            )

        patterns = []
        profile = self.profiles[user_id]

        # Analyze code snippet for patterns
        lines = code_snippet.split('\n')

        # Pattern: Use of list comprehensions
        if any('[' in line and 'for' in line and 'in' in line for line in lines):
            patterns.append(CodingPattern(
                pattern_type="list_comprehension",
                frequency=1,
                last_used=datetime.now(),
                efficiency_score=0.8
            ))

        # Pattern: Use of lambda functions
        if any('lambda' in line for line in lines):
            patterns.append(CodingPattern(
                pattern_type="lambda_function",
                frequency=1,
                last_used=datetime.now(),
                efficiency_score=0.6
            ))

        # Pattern: Error handling
        if any('try:' in line or 'except' in line for line in lines):
            patterns.append(CodingPattern(
                pattern_type="error_handling",
                frequency=1,
                last_used=datetime.now(),
                efficiency_score=0.9
            ))

        # Update profile with new patterns
        for pattern in patterns:
            existing_pattern = next((p for p in profile.coding_patterns if p.pattern_type == pattern.pattern_type), None)
            if existing_pattern:
                existing_pattern.frequency += pattern.frequency
                existing_pattern.last_used = pattern.last_used
            else:
                profile.coding_patterns.append(pattern)

        # Update favorite languages
        if language not in profile.favorite_languages:
            profile.favorite_languages.append(language)

        self._save_profile(profile)
        return patterns

    def track_productivity(self, user_id: str, metric: ProductivityMetric):
        """Track productivity metrics"""
        if user_id not in self.profiles:
            self.profiles[user_id] = AnalyticsProfile(
                user_id=user_id,
                coding_patterns=[],
                productivity_history=[],
                insights=[],
                streak_days=0,
                total_hours_coded=0,
                favorite_languages=[],
                skill_progress={}
            )

        profile = self.profiles[user_id]
        profile.productivity_history.append(metric)

        # Update total hours coded
        profile.total_hours_coded += metric.time_spent_coding // 60

        # Update streak days (simplified)
        if not profile.productivity_history or \
           (datetime.now().date() - profile.productivity_history[-1].date.date()).days <= 1:
            profile.streak_days += 1
        else:
            profile.streak_days = 1

        self._save_profile(profile)

    def generate_insights(self, user_id: str) -> List[Insight]:
        """Generate actionable insights from coding data"""
        if user_id not in self.profiles:
            return []

        profile = self.profiles[user_id]
        insights = []

        # Insight: High usage of certain patterns
        for pattern in profile.coding_patterns:
            if pattern.frequency > 10:
                insights.append(Insight(
                    title=f"Frequent use of {pattern.pattern_type}",
                    description=f"You use {pattern.pattern_type} {pattern.frequency} times",
                    severity="medium",
                    recommendation=f"Consider if {pattern.pattern_type} is always the best approach",
                    related_metrics=["coding_patterns"]
                ))

        # Insight: Productivity trends
        if len(profile.productivity_history) > 7:
            recent_avg = sum(m.lines_of_code for m in profile.productivity_history[-7:]) / 7
            overall_avg = sum(m.lines_of_code for m in profile.productivity_history) / len(profile.productivity_history)
            if recent_avg > overall_avg * 1.2:
                insights.append(Insight(
                    title="Increased productivity",
                    description="Your recent coding output is 20% higher than average",
                    severity="positive",
                    recommendation="Keep up the good work!",
                    related_metrics=["productivity_history"]
                ))

        # Insight: Skill progression
        for skill, level in profile.skill_progress.items():
            if level < 5:
                insights.append(Insight(
                    title=f"Skill development opportunity: {skill}",
                    description=f"Your {skill} skill is at level {level}/10",
                    severity="medium",
                    recommendation=f"Focus on improving your {skill} skills through practice",
                    related_metrics=["skill_progress"]
                ))

        profile.insights = insights
        self._save_profile(profile)
        return insights

    def predict_productivity(self, user_id: str, days_ahead: int = 7) -> Dict[str, Any]:
        """Predict future productivity trends"""
        if user_id not in self.profiles:
            return {"prediction": "No data available"}

        profile = self.profiles[user_id]

        # Simple prediction based on recent trends
        if len(profile.productivity_history) >= 7:
            recent_metrics = profile.productivity_history[-7:]
            avg_lines_per_day = sum(m.lines_of_code for m in recent_metrics) / 7
            avg_time_per_day = sum(m.time_spent_coding for m in recent_metrics) / 7

            predicted_lines = avg_lines_per_day * days_ahead
            predicted_time = avg_time_per_day * days_ahead

            trend = "increasing" if avg_lines_per_day > 100 else "stable" if avg_lines_per_day > 50 else "decreasing"

            return {
                "predicted_lines_of_code": int(predicted_lines),
                "predicted_coding_time_minutes": int(predicted_time),
                "trend": trend,
                "confidence": "medium"
            }
        else:
            return {
                "prediction": "Insufficient data for prediction",
                "confidence": "low"
            }

    def get_productivity_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get productivity summary for a time period"""
        if user_id not in self.profiles:
            return {}

        profile = self.profiles[user_id]
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = [m for m in profile.productivity_history if m.date > cutoff_date]

        if not recent_metrics:
            return {"message": "No data for the specified period"}

        return {
            "total_lines": sum(m.lines_of_code for m in recent_metrics),
            "total_functions": sum(m.functions_written for m in recent_metrics),
            "total_bugs_fixed": sum(m.bugs_fixed for m in recent_metrics),
            "total_hours": sum(m.time_spent_coding for m in recent_metrics) // 60,
            "average_lines_per_day": sum(m.lines_of_code for m in recent_metrics) / days,
            "current_streak": profile.streak_days
        }

    def get_profile(self, user_id: str) -> Optional[AnalyticsProfile]:
        """Get user analytics profile"""
        return self.profiles.get(user_id)

    def update_skill_progress(self, user_id: str, skill: str, level: int):
        """Update user skill progress"""
        if user_id not in self.profiles:
            self.profiles[user_id] = AnalyticsProfile(
                user_id=user_id,
                coding_patterns=[],
                productivity_history=[],
                insights=[],
                streak_days=0,
                total_hours_coded=0,
                favorite_languages=[],
                skill_progress={}
            )

        profile = self.profiles[user_id]
        profile.skill_progress[skill] = level
        self._save_profile(profile)

    def get_leaderboard(self, metric: str = "lines_of_code", limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard based on specified metric"""
        user_metrics = []

        for user_id, profile in self.profiles.items():
            if profile.productivity_history:
                if metric == "lines_of_code":
                    total = sum(m.lines_of_code for m in profile.productivity_history)
                elif metric == "hours_coded":
                    total = profile.total_hours_coded
                elif metric == "streak_days":
                    total = profile.streak_days
                else:
                    total = 0

                user_metrics.append({
                    "user_id": user_id,
                    "value": total,
                    "profile": profile
                })

        # Sort by value descending
        user_metrics.sort(key=lambda x: x["value"], reverse=True)
        return user_metrics[:limit]

    def _save_profile(self, profile: AnalyticsProfile):
        """Save profile to file"""
        try:
            profile_file = os.path.join(self.analytics_dir, f"{profile.user_id}_profile.json")
            # Convert datetime objects to strings for JSON serialization
            profile_dict = profile.dict()
            for metric in profile_dict.get("productivity_history", []):
                metric["date"] = metric["date"].isoformat()
            for pattern in profile_dict.get("coding_patterns", []):
                pattern["last_used"] = pattern["last_used"].isoformat()

            with open(profile_file, 'w') as f:
                json.dump(profile_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving profile for {profile.user_id}: {e}")

# Initialize analytics dashboard
analytics_dashboard = AnalyticsDashboard()
