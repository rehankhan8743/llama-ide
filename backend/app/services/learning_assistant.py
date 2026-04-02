from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import random


class LearningProgress(BaseModel):
    concept: str
    mastery_level: int  # 0-100
    last_practiced: str
    practice_count: int


class Tutorial(BaseModel):
    id: str
    title: str
    topic: str
    skill_level: str  # "beginner", "intermediate", "advanced"
    content: str
    code_examples: List[str]
    exercises: List[str]
    estimated_minutes: int
    steps: List[Dict[str, str]] = []  # step_number: explanation
    prerequisites: List[str] = []


class ConceptExplanation(BaseModel):
    concept: str
    explanation: str
    examples: List[str]
    related_concepts: List[str]
    difficulty: str


class LearningPath(BaseModel):
    path_name: str
    topics: List[str]
    estimated_duration: str
    skill_level: str


class ProgressTracking(BaseModel):
    user_id: str
    completed_topics: List[str]
    current_topic: str
    progress_percentage: float
    streak_days: int
    last_activity: str


class LearningAssistantService:
    def __init__(self):
        self.concept_database = self._load_concepts()
        self.user_progress: Dict[str, List[LearningProgress]] = {}
        self.tutorials = self._load_tutorials()
        self.learning_paths = self._load_learning_paths()

    def _load_concepts(self) -> Dict[str, Dict[str, Any]]:
        """Load programming concepts database"""
        return {
            "variables": {
                "name": "Variables",
                "category": "Fundamentals",
                "explanation": "Variables are containers for storing data values. In Python, you don't need to declare a variable type.",
                "examples": [
                    "x = 5  # Integer variable",
                    "name = 'Alice'  # String variable",
                    "is_active = True  # Boolean variable"
                ],
                "related_concepts": ["data_types", "assignment", "scope"],
                "difficulty": "beginner"
            },
            "functions": {
                "name": "Functions",
                "category": "Fundamentals",
                "explanation": "Functions are blocks of code designed to perform a particular task. They are executed when called.",
                "examples": [
                    "def greet(name):\n    return f'Hello, {name}!'",
                    "def calculate_area(length, width):\n    return length * width"
                ],
                "related_concepts": ["parameters", "return_values", "scope"],
                "difficulty": "beginner"
            },
            "classes": {
                "name": "Classes",
                "category": "Object-Oriented Programming",
                "explanation": "Classes are blueprints for creating objects. They define properties and methods that the objects created from the class can have.",
                "examples": [
                    "class Dog:\n    def __init__(self, name):\n        self.name = name\n\n    def bark(self):\n        return 'Woof!'"
                ],
                "related_concepts": ["objects", "inheritance", "encapsulation"],
                "difficulty": "intermediate"
            },
            "recursion": {
                "name": "Recursion",
                "category": "Fundamentals",
                "explanation": "Recursion is a programming technique where a function calls itself to solve a problem by breaking it into smaller sub-problems.",
                "examples": [
                    "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
                    "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
                ],
                "related_concepts": ["dynamic programming", "iteration", "call stack"],
                "difficulty": "intermediate"
            },
            "oop": {
                "name": "Object-Oriented Programming",
                "category": "Programming Paradigms",
                "explanation": "OOP is a programming paradigm based on the concept of 'objects' which contain data and code. Key principles include encapsulation, inheritance, and polymorphism.",
                "examples": [
                    "class Dog: def __init__(self, name): self.name = name",
                    "class Cat(Animal): # inheritance",
                    "def speak(self): pass  # polymorphism"
                ],
                "related_concepts": ["classes", "inheritance", "polymorphism", "encapsulation"],
                "difficulty": "beginner"
            },
            "algorithms": {
                "name": "Algorithms",
                "category": "Computer Science",
                "explanation": "An algorithm is a step-by-step procedure for solving a problem or accomplishing a task.",
                "examples": [
                    "Sorting: bubble sort, merge sort, quicksort",
                    "Searching: binary search, linear search",
                    "Graph: BFS, DFS, Dijkstra's algorithm"
                ],
                "related_concepts": ["data structures", "complexity analysis", "big O notation"],
                "difficulty": "intermediate"
            },
            "async": {
                "name": "Asynchronous Programming",
                "category": "Advanced Topics",
                "explanation": "Async programming allows tasks to run concurrently without blocking the main thread. Essential for I/O-bound operations and web development.",
                "examples": [
                    "async def fetch_data(): await requests.get(url)",
                    "asyncio.gather(*tasks)  # concurrent execution",
                    "await asyncio.sleep(1)  # non-blocking pause"
                ],
                "related_concepts": ["promises", "callbacks", "event loop", "concurrency"],
                "difficulty": "advanced"
            },
            "design_patterns": {
                "name": "Design Patterns",
                "category": "Software Engineering",
                "explanation": "Design patterns are reusable solutions to common problems in software design. They provide templates for solving issues in a consistent way.",
                "examples": [
                    "Singleton: one instance only",
                    "Factory: creates objects without specifying exact class",
                    "Observer: notify dependents of state changes"
                ],
                "related_concepts": ["SOLID principles", "clean code", "refactoring"],
                "difficulty": "advanced"
            }
        }

    def _load_tutorials(self) -> Dict[str, Tutorial]:
        """Load built-in tutorials"""
        return {
            "python_basics": Tutorial(
                id="python_basics",
                title="Python Basics",
                topic="python",
                skill_level="beginner",
                content="Learn the fundamentals of Python programming including variables, data types, control flow, and functions.",
                code_examples=[
                    "# Variables and Data Types\nname = 'Alice'\nage = 30\nis_active = True",
                    "# Control Flow\nif age > 18:\n    print('Adult')\nelse:\n    print('Minor')",
                    "# Functions\ndef greet(name):\n    return f'Hello, {name}!'"
                ],
                exercises=[
                    "Create a function that calculates the area of a rectangle",
                    "Write a program that checks if a number is prime",
                    "Implement a simple calculator using functions"
                ],
                estimated_minutes=60,
                steps=[
                    {"step": "1", "description": "Understanding variables and data types"},
                    {"step": "2", "description": "Working with strings and numbers"},
                    {"step": "3", "description": "Control flow with if/else statements"},
                    {"step": "4", "description": "Loops: for and while"},
                    {"step": "5", "description": "Functions and modules"}
                ],
                prerequisites=[]
            ),
            "oop_concepts": Tutorial(
                id="oop_concepts",
                title="Object-Oriented Programming",
                topic="python",
                skill_level="intermediate",
                content="Master OOP principles in Python",
                code_examples=[
                    "class Animal:\n    def __init__(self, name):\n        self.name = name",
                    "class Dog(Animal):\n    def speak(self):\n        return f'{self.name} says Woof!'"
                ],
                exercises=[
                    "Create a BankAccount class with deposit and withdraw methods",
                    "Implement inheritance with Animal -> Dog, Cat",
                    "Use polymorphism to make different animals speak differently"
                ],
                estimated_minutes=120,
                steps=[
                    {"step": "1", "description": "Introduction to classes and objects"},
                    {"step": "2", "description": "Understanding encapsulation"},
                    {"step": "3", "description": "Inheritance and polymorphism"},
                    {"step": "4", "description": "Class methods and static methods"},
                    {"step": "5", "description": "Design patterns overview"}
                ],
                prerequisites=["python_basics"]
            ),
            "javascript_async": Tutorial(
                id="javascript_async",
                title="JavaScript Async Programming",
                topic="javascript",
                skill_level="intermediate",
                content="Master asynchronous JavaScript including callbacks, promises, and async/await.",
                code_examples=[
                    "// Promise example\nconst fetchData = () => new Promise((resolve, reject) => {\n  setTimeout(() => resolve('data'), 1000);\n});",
                    "// Async/await\nasync function getData() {\n  const result = await fetchData();\n  console.log(result);\n}",
                    "// Error handling\ntry {\n  const data = await riskyOperation();\n} catch (error) {\n  console.error(error);\n}"
                ],
                exercises=[
                    "Convert callback-based code to use Promises",
                    "Implement a function that runs multiple promises concurrently",
                    "Create an async retry mechanism with exponential backoff"
                ],
                estimated_minutes=45,
                steps=[
                    {"step": "1", "description": "Understanding callbacks"},
                    {"step": "2", "description": "Working with Promises"},
                    {"step": "3", "description": "Async/await syntax"},
                    {"step": "4", "description": "Error handling in async code"},
                    {"step": "5", "description": "Concurrent execution with Promise.all"}
                ],
                prerequisites=["javascript_basics"]
            ),
            "git_fundamentals": Tutorial(
                id="git_fundamentals",
                title="Git Version Control",
                topic="git",
                skill_level="beginner",
                content="Learn essential Git commands for version control and collaboration.",
                code_examples=[
                    "# Basic commands\ngit init\ngit add .\ngit commit -m 'Initial commit'",
                    "# Branching\ngit branch feature\ngit checkout feature\ngit merge main",
                    "# Collaboration\ngit pull origin main\ngit push origin feature"
                ],
                exercises=[
                    "Initialize a repo and make your first commit",
                    "Create and merge a feature branch",
                    "Resolve a merge conflict"
                ],
                estimated_minutes=40,
                steps=[
                    {"step": "1", "description": "Initializing a Git repository"},
                    {"step": "2", "description": "Staging and committing changes"},
                    {"step": "3", "description": "Branching and merging"},
                    {"step": "4", "description": "Working with remotes"},
                    {"step": "5", "description": "Resolving conflicts"}
                ],
                prerequisites=[]
            )
        }

    def _load_learning_paths(self) -> List[LearningPath]:
        """Load predefined learning paths"""
        return [
            LearningPath(
                path_name="Web Development with Python",
                topics=["python_basics", "flask", "html_css", "databases", "deployment"],
                estimated_duration="8 weeks",
                skill_level="beginner"
            ),
            LearningPath(
                path_name="Data Science Fundamentals",
                topics=["python_basics", "numpy", "pandas", "matplotlib", "machine_learning"],
                estimated_duration="12 weeks",
                skill_level="intermediate"
            ),
            LearningPath(
                path_name="Full Stack JavaScript",
                topics=["javascript_basics", "nodejs", "react", "databases", "deployment"],
                estimated_duration="10 weeks",
                skill_level="beginner"
            )
        ]

    def explain_concept(self, concept: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Explain a programming concept with optional context"""
        concept_lower = concept.lower()

        # Search in database
        for key, data in self.concept_database.items():
            if key in concept_lower or concept_lower in key:
                result = {
                    "found": True,
                    "concept": data["name"],
                    "category": data["category"],
                    "explanation": data["explanation"],
                    "examples": data["examples"],
                    "related_concepts": data["related_concepts"],
                    "difficulty": data["difficulty"]
                }
                # Customize based on context if provided
                if context:
                    result["explanation"] += f"\n\nIn the context of your code: {context}"
                return result

        # Generate contextual explanation if not found
        if context:
            return {
                "found": False,
                "concept": concept,
                "explanation": f"{concept} is a concept in {context} programming. Based on the context, it appears to relate to...",
                "examples": [],
                "related_concepts": [],
                "difficulty": "unknown"
            }

        return {
            "found": False,
            "concept": concept,
            "explanation": f"I don't have detailed information about '{concept}' yet, but I can help you learn about it!",
            "examples": [f"Example for {concept} would go here..."],
            "related_concepts": [],
            "difficulty": "unknown"
        }

    def generate_tutorial(self, topic: str, skill_level: str = "beginner") -> Dict[str, Any]:
        """Generate or find a tutorial for a topic"""
        topic_lower = topic.lower()

        # Search for matching tutorial
        for tutorial_id, tutorial in self.tutorials.items():
            if topic_lower in tutorial.topic.lower() or topic_lower in tutorial.title.lower():
                return tutorial.model_dump()

        # Generate a basic tutorial structure if not found
        return {
            "id": str(uuid.uuid4()),
            "title": f"Learning {topic.title()}",
            "topic": topic,
            "skill_level": skill_level,
            "content": f"A comprehensive guide to {topic}",
            "code_examples": [
                f"# Example 1: Getting started with {topic}",
                f"# Example 2: {topic} basics"
            ],
            "exercises": [
                f"Create a simple {topic} program",
                f"Practice {topic} fundamentals"
            ],
            "estimated_minutes": 30,
            "steps": [
                {"step": "1", "description": f"Introduction to {topic}"},
                {"step": "2", "description": f"Basic concepts of {topic}"},
                {"step": "3", "description": f"Advanced features of {topic}"},
                {"step": "4", "description": f"Best practices for {topic}"},
                {"step": "5", "description": f"Real-world applications of {topic}"}
            ],
            "prerequisites": []
        }

    def get_concept_related(self, concept: str) -> List[str]:
        """Get related concepts"""
        concept_lower = concept.lower()
        for key, data in self.concept_database.items():
            if key in concept_lower or concept_lower in key:
                return data.get("related_concepts", [])
        return []

    def track_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get learning progress for a user"""
        return self.user_progress.get(user_id, [])

    def get_detailed_progress(self, user_id: str) -> ProgressTracking:
        """Get detailed progress tracking for a user"""
        progress_list = self.user_progress.get(user_id, [])
        completed = [p.concept for p in progress_list if p.mastery_level >= 80]

        # Calculate progress percentage
        total_concepts = len(self.concept_database)
        progress_pct = (len(completed) / total_concepts * 100) if total_concepts > 0 else 0

        # Find current topic (most recently practiced)
        current_topic = "Getting Started"
        if progress_list:
            sorted_progress = sorted(progress_list, key=lambda x: x.last_practiced, reverse=True)
            current_topic = sorted_progress[0].concept

        return ProgressTracking(
            user_id=user_id,
            completed_topics=completed,
            current_topic=current_topic,
            progress_percentage=round(progress_pct, 2),
            streak_days=random.randint(1, 30),  # Simulated for demo
            last_activity=datetime.now().isoformat() if progress_list else None
        )

    def update_progress(self, user_id: str, concept: str, mastery_level: int) -> Dict[str, Any]:
        """Update user's learning progress for a concept"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = []

        progress = LearningProgress(
            concept=concept,
            mastery_level=mastery_level,
            last_practiced=datetime.now().isoformat(),
            practice_count=1
        )

        # Update existing or add new
        for p in self.user_progress[user_id]:
            if p.concept == concept:
                p.mastery_level = mastery_level
                p.last_practiced = progress.last_practiced
                p.practice_count += 1
                return p.model_dump()

        self.user_progress[user_id].append(progress)
        return progress.model_dump()

    def get_recommended_concepts(self, user_id: str) -> List[str]:
        """Recommend concepts based on user's learning path"""
        if user_id not in self.user_progress:
            return list(self.concept_database.keys())[:3]

        learned = {p.concept for p in self.user_progress[user_id]}
        recommended = []

        for concept, data in self.concept_database.items():
            if concept not in learned:
                # Prioritize concepts related to what user already knows
                for learned_concept in learned:
                    if learned_concept in data.get("related_concepts", []):
                        recommended.append(concept)
                        break

        return recommended[:5]

    def recommend_next_topic(self, user_id: str) -> str:
        """Recommend the next topic based on progress"""
        progress = self.get_detailed_progress(user_id)
        current = progress.current_topic

        # Map current topics to next topics
        learning_flow = {
            "variables": "functions",
            "functions": "classes",
            "classes": "inheritance",
            "inheritance": "polymorphism",
            "polymorphism": "recursion",
            "recursion": "algorithms",
            "algorithms": "design_patterns"
        }

        return learning_flow.get(current, "variables")

    def get_learning_paths(self, skill_level: str = "all") -> List[LearningPath]:
        """Get available learning paths"""
        if skill_level == "all":
            return self.learning_paths
        return [path for path in self.learning_paths if path.skill_level == skill_level]

    def suggest_exercise(self, topic: str) -> str:
        """Suggest a coding exercise for a topic"""
        exercises = {
            "variables": "Create a program that calculates the area of different shapes using variables",
            "functions": "Write a function that takes a list of numbers and returns only the even numbers",
            "classes": "Create a BankAccount class with deposit and withdraw methods",
            "loops": "Write a program that generates the Fibonacci sequence up to n terms",
            "recursion": "Implement a recursive function to calculate factorial",
            "algorithms": "Implement binary search on a sorted array",
            "oop": "Design a class hierarchy for a library management system"
        }
        return exercises.get(topic.lower(), f"Practice {topic} by creating your own examples")

    def get_tutorial_by_id(self, tutorial_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tutorial by ID"""
        tutorial = self.tutorials.get(tutorial_id)
        return tutorial.model_dump() if tutorial else None

    def get_all_tutorials(self) -> List[Dict[str, Any]]:
        """Get all available tutorials"""
        return [t.model_dump() for t in self.tutorials.values()]


# Global learning assistant instance
learning_assistant = LearningAssistantService()
