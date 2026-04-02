from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from ..services.code_review import code_review_service

router = APIRouter(prefix="/code-review")


class CodeReviewRequest(BaseModel):
    code: str
    language: str
    filepath: Optional[str] = None


class CodeReviewDiffRequest(BaseModel):
    old_code: str
    new_code: str
    language: str
    filepath: Optional[str] = None


class CodeReviewResponse(BaseModel):
    issues: List[Dict[str, Any]]
    complexity_score: float
    security_violations: List[Dict[str, Any]]
    best_practices: List[str]
    overall_rating: int


@router.post("/analyze", response_model=CodeReviewResponse)
async def analyze_code(request: CodeReviewRequest):
    """Analyze code for issues, security violations, and best practices"""
    try:
        report = code_review_service.review_code(request.code, request.language)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze-with-ai", response_model=CodeReviewResponse)
async def analyze_code_with_ai(request: CodeReviewRequest):
    """Analyze code with AI-enhanced review"""
    try:
        report = await code_review_service.review_code_with_ai(
            request.code,
            request.language,
            request.filepath
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/diff")
async def review_diff(request: CodeReviewDiffRequest):
    """Review code changes between two versions"""
    try:
        result = code_review_service.review_diff(
            request.old_code,
            request.new_code,
            request.language
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/compare")
async def compare_implementations(code_samples: Dict[str, Dict[str, str]]):
    """Compare multiple code implementations"""
    try:
        reports = {}
        for name, code_info in code_samples.items():
            code = code_info.get('code', '')
            language = code_info.get('language', 'python')
            reports[name] = code_review_service.review_code(code, language)

        # Compare reports
        comparison = {
            "implementations": reports,
            "comparison": {}
        }

        # Find best implementation based on ratings
        best_impl = max(reports.items(), key=lambda x: x[1].get('overall_rating', 0))
        comparison["comparison"]["recommended"] = best_impl[0]
        comparison["comparison"]["reasoning"] = f"Highest rating ({best_impl[1].get('overall_rating', 0)}/10)"

        return comparison
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/summary")
async def get_code_summary(request: CodeReviewRequest):
    """Get a human-readable summary of the code review"""
    try:
        summary = code_review_service.get_summary(request.code, request.language)
        return {"summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    languages = list(code_review_service.language_patterns.keys())
    return {
        "languages": languages,
        "total_supported": len(languages)
    }
