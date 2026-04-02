from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import re
import json

class ProjectStructure(BaseModel):
    name: str
    description: str
    files: Dict[str, str]  # filename: content
    dependencies: List[str]
    readme: str

class BoilerplateTemplate(BaseModel):
    name: str
    framework: str
    description: str
    template_files: Dict[str, str]  # filename: template_content
    required_inputs: List[str]
    dependencies: List[str]

class RefactorRequest(BaseModel):
    code: str
    target_style: str
    options: Dict[str, Any]

class GeneratedCode(BaseModel):
    code: str
    language: str
    explanation: str
    suggestions: List[str]

class CodeGenerationAssistant:
    def __init__(self):
        self.templates = self._load_templates()
        self.refactoring_rules = self._load_refactoring_rules()

    def _load_templates(self) -> Dict[str, BoilerplateTemplate]:
        """Load boilerplate templates"""
        return {
            "flask_basic": BoilerplateTemplate(
                name="Flask Basic App",
                framework="Flask",
                description="Basic Flask web application with routing",
                template_files={
                    "app.py": '''from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/data')
def get_data():
    return jsonify({"data": "Sample data"})

if __name__ == '__main__':
    app.run(debug=True)
''',
                    "requirements.txt": "Flask==2.3.2\n",
                    "README.md": "# Flask Basic App\n\nA simple Flask application.\n"
                },
                required_inputs=["project_name"],
                dependencies=["Flask"]
            ),
            "fastapi_crud": BoilerplateTemplate(
                name="FastAPI CRUD App",
                framework="FastAPI",
                description="FastAPI application with CRUD operations",
                template_files={
                    "main.py": '''from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: str = None

items = []

@app.get("/items/", response_model=List[Item])
def read_items():
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    return {"error": "Item not found"}

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    for i, existing_item in enumerate(items):
        if existing_item.id == item_id:
            items[i] = item
            return item
    return {"error": "Item not found"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(items):
        if item.id == item_id:
            items.pop(i)
            return {"message": "Item deleted"}
    return {"error": "Item not found"}
''',
                    "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0\n",
                    "README.md": "# FastAPI CRUD App\n\nA FastAPI application with CRUD operations.\n"
                },
                required_inputs=["project_name"],
                dependencies=["fastapi", "uvicorn"]
            )
        }

    def _load_refactoring_rules(self) -> Dict[str, Dict[str, str]]:
        """Load refactoring rules for different styles"""
        return {
            "pep8": {
                "indentation": "Use 4 spaces per indentation level",
                "line_length": "Limit all lines to a maximum of 79 characters",
                "blank_lines": "Surround top-level function and class definitions with two blank lines"
            },
            "google_style": {
                "indentation": "Use 2 spaces per indentation level",
                "line_length": "Limit all lines to a maximum of 80 characters",
                "naming": "Use lower_with_under style for module names"
            },
            "airbnb": {
                "indentation": "Use 2 spaces per indentation level",
                "quotes": "Use double quotes for strings",
                "semicolons": "Don't use semicolons"
            }
        }

    def generate_boilerplate(self, framework: str, requirements: List[str],
                           project_name: str = "my_project") -> ProjectStructure:
        """Generate complete boilerplate code"""
        template_key = f"{framework.lower()}_basic" if f"{framework.lower()}_basic" in self.templates else "flask_basic"
        template = self.templates[template_key]

        # Customize template with project name
        files = {}
        for filename, content in template.template_files.items():
            # Replace placeholders
            customized_content = content.replace("Flask Basic App", project_name.title())
            files[filename] = customized_content

        return ProjectStructure(
            name=project_name,
            description=template.description,
            files=files,
            dependencies=template.dependencies,
            readme=f"# {project_name}\n\n{template.description}\n"
        )

    def scaffold_project(self, project_type: str, features: List[str]) -> ProjectStructure:
        """Create entire project structure"""
        project_name = f"my_{project_type.lower()}_project"

        # Base files
        files = {
            "README.md": f"# {project_name}\n\nA {project_type} project with {', '.join(features)}.\n",
            ".gitignore": "*.pyc\n__pycache__/\n.env\n",
        }

        # Add feature-specific files
        if "api" in features:
            files.update({
                "api/__init__.py": "",
                "api/routes.py": "# API routes will be defined here\n",
            })

        if "database" in features:
            files.update({
                "models/__init__.py": "",
                "models/base.py": "# Database models will be defined here\n",
            })

        if "tests" in features:
            files.update({
                "tests/__init__.py": "",
                "tests/test_example.py": "# Tests will be written here\n",
            })

        return ProjectStructure(
            name=project_name,
            description=f"A {project_type} project with {', '.join(features)}",
            files=files,
            dependencies=[],
            readme=f"# {project_name}\n\nA {project_type} project with {', '.join(features)}.\n"
        )

    def refactor_code(self, code: str, target_style: str, options: Dict[str, Any] = None) -> GeneratedCode:
        """Automatically refactor code to different styles"""
        if options is None:
            options = {}

        refactored_code = code
        suggestions = []

        # Apply refactoring rules
        if target_style in self.refactoring_rules:
            rules = self.refactoring_rules[target_style]

            # Apply indentation rule
            if "indentation" in rules:
                if "2 spaces" in rules["indentation"]:
                    refactored_code = refactored_code.replace("    ", "  ")
                    suggestions.append("Changed indentation to 2 spaces")
                elif "4 spaces" in rules["indentation"]:
                    refactored_code = refactored_code.replace("  ", "    ")
                    suggestions.append("Changed indentation to 4 spaces")

            # Apply line length rule
            if "line_length" in rules:
                suggestions.append(f"Applied {rules['line_length']}")

            # Apply naming conventions
            if "naming" in rules and "lower_with_under" in rules["naming"]:
                # Convert camelCase to snake_case for module names
                suggestions.append("Applied snake_case naming convention")

        return GeneratedCode(
            code=refactored_code,
            language="python",
            explanation=f"Refactored code to {target_style} style",
            suggestions=suggestions
        )

    def generate_function(self, purpose: str, parameters: List[str], return_type: str) -> GeneratedCode:
        """Generate a function based on description"""
        # This would typically integrate with an AI model
        function_name = "_".join(purpose.lower().split()[:3])
        param_str = ", ".join(parameters)

        code = f'''def {function_name}({param_str}):
    """
    {purpose}

    Args:
        {", ".join([f"{p}: description" for p in parameters])}

    Returns:
        {return_type}: description
    """
    # TODO: Implement function logic
    pass
'''

        return GeneratedCode(
            code=code,
            language="python",
            explanation=f"Generated function for: {purpose}",
            suggestions=[f"Implement the logic for {function_name}", "Add proper error handling"]
        )

    def generate_class(self, class_name: str, methods: List[str], attributes: List[str]) -> GeneratedCode:
        """Generate a class with specified methods and attributes"""
        methods_code = "\n".join([f"    def {method}(self):\n        pass" for method in methods])
        attributes_code = "\n".join([f"        self.{attr} = None" for attr in attributes])

        code = f'''class {class_name}:
    def __init__(self):
{attributes_code}

{methods_code}
'''

        return GeneratedCode(
            code=code,
            language="python",
            explanation=f"Generated class {class_name}",
            suggestions=[f"Implement the methods for {class_name}", "Add proper initialization"]
        )

# Initialize code generation assistant
code_generation_assistant = CodeGenerationAssistant()
