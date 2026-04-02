from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from ..services.code_generation import (
    code_generation_assistant,
    ProjectStructure,
    GeneratedCode,
    RefactorRequest
)

router = APIRouter(prefix="/generation")

class GenerateBoilerplateRequest(BaseModel):
    framework: str
    requirements: List[str]
    project_name: str = "my_project"

class ScaffoldProjectRequest(BaseModel):
    project_type: str
    features: List[str]

class RefactorCodeRequest(BaseModel):
    code: str
    target_style: str
    options: Dict[str, Any] = {}

class GenerateFunctionRequest(BaseModel):
    purpose: str
    parameters: List[str]
    return_type: str

class GenerateClassRequest(BaseModel):
    class_name: str
    methods: List[str]
    attributes: List[str]

@router.post("/boilerplate", response_model=ProjectStructure)
async def generate_boilerplate(request: GenerateBoilerplateRequest):
    """Generate complete boilerplate code"""
    try:
        project = code_generation_assistant.generate_boilerplate(
            request.framework,
            request.requirements,
            request.project_name
        )
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scaffold", response_model=ProjectStructure)
async def scaffold_project(request: ScaffoldProjectRequest):
    """Create entire project structure"""
    try:
        project = code_generation_assistant.scaffold_project(
            request.project_type,
            request.features
        )
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refactor", response_model=GeneratedCode)
async def refactor_code(request: RefactorCodeRequest):
    """Automatically refactor code to different styles"""
    try:
        refactored = code_generation_assistant.refactor_code(
            request.code,
            request.target_style,
            request.options
        )
        return refactored
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/function", response_model=GeneratedCode)
async def generate_function(request: GenerateFunctionRequest):
    """Generate a function based on description"""
    try:
        function = code_generation_assistant.generate_function(
            request.purpose,
            request.parameters,
            request.return_type
        )
        return function
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/class", response_model=GeneratedCode)
async def generate_class(request: GenerateClassRequest):
    """Generate a class with specified methods and attributes"""
    try:
        klass = code_generation_assistant.generate_class(
            request.class_name,
            request.methods,
            request.attributes
        )
        return klass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_templates():
    """List available boilerplate templates"""
    try:
        templates = list(code_generation_assistant.templates.keys())
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customize")
async def customize_template(template_name: str, customizations: Dict[str, Any]):
    """Customize a template with specific requirements"""
    try:
        if template_name not in code_generation_assistant.templates:
            raise HTTPException(status_code=404, detail="Template not found")

        template = code_generation_assistant.templates[template_name]
        customized_files = {}

        for filename, content in template.template_files.items():
            # Apply customizations
            customized_content = content
            for key, value in customizations.items():
                customized_content = customized_content.replace(f"{{{key}}}", str(value))
            customized_files[filename] = customized_content

        return {
            "template": template_name,
            "files": customized_files,
            "dependencies": template.dependencies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
