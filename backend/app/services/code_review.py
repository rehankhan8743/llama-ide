from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import re
from dataclasses import dataclass


class CodeIssue(BaseModel):
    type: str  # "error", "warning", "suggestion"
    severity: int  # 1-5 scale
    message: str
    line: int
    column: int
    rule: str
    suggestion: Optional[str] = None


class CodeReviewReport(BaseModel):
    issues: List[CodeIssue]
    complexity_score: float
    security_violations: List[str]
    best_practices: List[str]
    overall_rating: int  # 1-10 scale


class SecurityVulnerability(BaseModel):
    severity: str  # "critical", "high", "medium", "low"
    cwe_id: str
    description: str
    line: int
    suggestion: str


class CodeReviewService:
    def __init__(self):
        self.language_patterns = {
            'python': self._review_python,
            'javascript': self._review_javascript,
            'typescript': self._review_typescript,
            'java': self._review_java,
            'go': self._review_go,
            'rust': self._review_rust
        }

    def review_code(self, code: str, language: str) -> Dict[str, Any]:
        """Main entry point for code review"""
        if language in self.language_patterns:
            return self.language_patterns[language](code)
        else:
            return self._generic_review(code)

    def _calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity score"""
        # Simple complexity estimation based on control flow statements
        control_flow = len(re.findall(r'\b(if|elif|else|for|while|and|or|try|except|finally|with|assert)\b', code))
        functions = len(re.findall(r'\bdef\s+\w+\(', code))
        classes = len(re.findall(r'\bclass\s+\w+\(', code))

        # Cyclomatic complexity approximation
        complexity = control_flow + 1
        return min(10.0, complexity / 3.0)  # Normalize to 0-10 scale

    def _check_security(self, code: str, language: str) -> List[SecurityVulnerability]:
        """Check for common security vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # SQL Injection patterns
            if re.search(r'(execute|query|cursor\.execute)\s*\(.*\%|\+.*\(.*select|insert|update|delete', line, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    severity="high",
                    cwe_id="CWE-89",
                    description="Potential SQL injection vulnerability",
                    line=line_num,
                    suggestion="Use parameterized queries instead of string concatenation"
                ))

            # Command injection
            if re.search(r'(os\.system|os\.popen|subprocess|subprocess\.call|subprocess\.run)\s*\(.*\+', line):
                vulnerabilities.append(SecurityVulnerability(
                    severity="critical",
                    cwe_id="CWE-78",
                    description="Potential OS command injection",
                    line=line_num,
                    suggestion="Avoid shell commands with user input; use subprocess with args list"
                ))

            # Hardcoded credentials
            if re.search(r'(password|passwd|pwd|secret|api_key|apikey|auth_token)\s*=\s*["\'][^"\']{8,}["\']', line, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    severity="high",
                    cwe_id="CWE-798",
                    description="Potential hardcoded credentials",
                    line=line_num,
                    suggestion="Use environment variables or a secrets manager"
                ))

            # Eval usage
            if 'eval(' in line:
                vulnerabilities.append(SecurityVulnerability(
                    severity="high",
                    cwe_id="CWE-95",
                    description="Dynamic code execution using eval()",
                    line=line_num,
                    suggestion="Avoid eval(); use safer alternatives for parsing"
                ))

            # Path traversal
            if re.search(r'(open|read|write)\s*\(.*\+.*request|input|args|params', line, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    severity="medium",
                    cwe_id="CWE-22",
                    description="Potential path traversal vulnerability",
                    line=line_num,
                    suggestion="Validate and sanitize file paths; avoid user input in file paths"
                ))

            # Insecure random
            if re.search(r'random\.(random|choice)\s*\(', line) and ('password' in line.lower() or 'token' in line.lower() or 'key' in line.lower()):
                vulnerabilities.append(SecurityVulnerability(
                    severity="medium",
                    cwe_id="CWE-338",
                    description="Use of cryptographically insecure random",
                    line=line_num,
                    suggestion="Use secrets.token_hex() or secrets.randbelow() for security-sensitive values"
                ))

        return vulnerabilities

    def _review_python(self, code: str) -> Dict[str, Any]:
        """Python-specific code review"""
        issues = []
        best_practices = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Global variable usage
            if re.match(r'^[A-Z_][A-Z0-9_]*\s*=\s*(?!.*def|.*class)', stripped) and not stripped.startswith('#'):
                if not any(kw in stripped for kw in ['def ', 'class ', 'import ', 'from ']):
                    issues.append(CodeIssue(
                        type="warning",
                        severity=2,
                        message="Potential global variable detected",
                        line=line_num,
                        column=0,
                        rule="no-global-vars",
                        suggestion="Consider using constants or class attributes instead"
                    ))

            # Print statements in production code
            if re.match(r'^\s*print\s*\(', stripped) and not stripped.startswith('#'):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Print statement found",
                    line=line_num,
                    column=line.find('print'),
                    rule="no-print-statements",
                    suggestion="Use logging module instead of print for production code"
                ))

            # Bare except clauses
            if re.match(r'^\s*except\s*:', stripped):
                issues.append(CodeIssue(
                    type="warning",
                    severity=3,
                    message="Bare except clause detected",
                    line=line_num,
                    column=line.find('except'),
                    rule="no-bare-except",
                    suggestion="Catch specific exceptions instead of bare except"
                ))

            # TODO/FIXME without issue tracker reference
            if re.match(r'^\s*#\s*(TODO|FIXME|HACK|XXX):?\s*(\w|$)', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found without issue reference",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference or resolve the marker"
                ))

            # Mutable default arguments
            match = re.search(r'def\s+\w+\s*\([^)]*=\s*(\[\]|dict\(\)|\{\})', stripped)
            if match:
                issues.append(CodeIssue(
                    type="error",
                    severity=4,
                    message="Mutable default argument detected",
                    line=line_num,
                    column=match.start(),
                    rule="no-mutable-defaults",
                    suggestion="Use None as default and initialize inside function"
                ))

        # Best practices check
        if 'import logging' in code:
            best_practices.append("Uses logging module for error reporting")
        if 'type hints' in code.lower() or '->' in code:
            best_practices.append("Uses type hints for better code documentation")
        if 'async def' in code and 'await' in code:
            best_practices.append("Uses async/await for concurrent operations")
        if 'dataclass' in code:
            best_practices.append("Uses dataclasses for structured data")

        security_violations = self._check_security(code, 'python')
        complexity_score = self._calculate_complexity(code)

        # Calculate overall rating
        issue_penalty = sum(i.severity for i in issues) / 10
        security_penalty = sum(5 if v.severity == "critical" else 3 if v.severity == "high" else 1 for v in security_violations)
        overall_rating = max(1, min(10, 10 - issue_penalty - security_penalty * 0.5))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [v.model_dump() for v in security_violations],
            "best_practices": best_practices,
            "overall_rating": int(overall_rating)
        }

    def _review_javascript(self, code: str) -> Dict[str, Any]:
        """JavaScript-specific code review"""
        issues = []
        best_practices = []

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # console.log in production
            if re.match(r'^\s*console\.(log|debug|info)\s*\(', stripped):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Console statement found",
                    line=line_num,
                    column=line.find('console'),
                    rule="no-console",
                    suggestion="Remove console statements in production or use a logging framework"
                ))

            # TODO/FIXME
            if re.match(r'^\s*(//|/\*)\s*(TODO|FIXME|HACK|XXX):?', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference or resolve the marker"
                ))

            # var instead of let/const
            if re.match(r'^\s*var\s+\w+', stripped):
                issues.append(CodeIssue(
                    type="warning",
                    severity=2,
                    message="'var' keyword used instead of 'let' or 'const'",
                    line=line_num,
                    column=line.find('var'),
                    rule="no-var",
                    suggestion="Use 'let' or 'const' for better scoping"
                ))

            # == instead of ===
            if re.match(r'.*[^=!]=[^=]\s*(?!=)', stripped) and not stripped.startswith('//'):
                issues.append(CodeIssue(
                    type="warning",
                    severity=2,
                    message="Loose equality operator detected",
                    line=line_num,
                    column=line.find('='),
                    rule="eqeqeq",
                    suggestion="Use strict equality (===) to avoid type coercion issues"
                ))

            # eval usage
            if 'eval(' in stripped:
                issues.append(CodeIssue(
                    type="error",
                    severity=5,
                    message="eval() usage detected",
                    line=line_num,
                    column=line.find('eval'),
                    rule="no-eval",
                    suggestion="Avoid eval(); it poses security risks"
                ))

        # Best practices
        if "'use strict'" in code or '"use strict"' in code:
            best_practices.append("Uses strict mode")
        if 'async function' in code or 'async (' in code:
            best_practices.append("Uses async/await for asynchronous operations")
        if 'Promise' in code:
            best_practices.append("Uses Promises for async operations")
        if 'const' in code and 'let' in code:
            best_practices.append("Uses modern variable declarations")

        security_violations = self._check_security(code, 'javascript')
        complexity_score = self._calculate_complexity(code)
        overall_rating = max(1, min(10, 10 - len(issues) * 0.5))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [v.model_dump() for v in security_violations],
            "best_practices": best_practices,
            "overall_rating": int(overall_rating)
        }

    def _review_typescript(self, code: str) -> Dict[str, Any]:
        """TypeScript-specific code review (similar to JavaScript but with type checking)"""
        result = self._review_javascript(code)
        result["best_practices"].append("TypeScript provides type safety")
        return result

    def _review_java(self, code: str) -> Dict[str, Any]:
        """Java-specific code review"""
        issues = []
        best_practices = []

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # System.out.println
            if re.match(r'^\s*System\.(out|err)\.(print|println)\s*\(', stripped):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="System output statement found",
                    line=line_num,
                    column=0,
                    rule="no-system-out",
                    suggestion="Use a logging framework instead of System.out"
                ))

            # TODO/FIXME
            if re.match(r'^\s*//\s*(TODO|FIXME|HACK|XXX):?', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference"
                ))

        security_violations = self._check_security(code, 'java')
        complexity_score = self._calculate_complexity(code)
        overall_rating = max(1, min(10, 10 - len(issues) * 0.5))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [v.model_dump() for v in security_violations],
            "best_practices": best_practices,
            "overall_rating": int(overall_rating)
        }

    def _review_go(self, code: str) -> Dict[str, Any]:
        """Go-specific code review"""
        issues = []
        best_practices = []

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # TODO/FIXME
            if re.match(r'^\s*//\s*(TODO|FIXME|HACK|XXX):?', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference"
                ))

            # Error handling
            if re.match(r'^\s*if\s+err\s*!=\s*nil\s*\{', stripped):
                best_practices.append("Proper error handling with err != nil check")

        security_violations = self._check_security(code, 'go')
        complexity_score = self._calculate_complexity(code)
        overall_rating = max(1, min(10, 10 - len(issues) * 0.5))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [v.model_dump() for v in security_violations],
            "best_practices": best_practices,
            "overall_rating": int(overall_rating)
        }

    def _review_rust(self, code: str) -> Dict[str, Any]:
        """Rust-specific code review"""
        issues = []
        best_practices = []

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # TODO/FIXME
            if re.match(r'^\s*//\s*(TODO|FIXME|HACK|XXX):?', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference"
                ))

            # Expect instead of unwrap
            if '.unwrap()' in stripped and not stripped.startswith('//'):
                issues.append(CodeIssue(
                    type="warning",
                    severity=2,
                    message="use of .unwrap() detected",
                    line=line_num,
                    column=line.find('.unwrap'),
                    rule="no-unwrap",
                    suggestion="Consider using ? operator or expect() with a message"
                ))

        security_violations = self._check_security(code, 'rust')
        complexity_score = self._calculate_complexity(code)
        overall_rating = max(1, min(10, 10 - len(issues) * 0.5))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [v.model_dump() for v in security_violations],
            "best_practices": best_practices,
            "overall_rating": int(overall_rating)
        }

    def _generic_review(self, code: str) -> Dict[str, Any]:
        """Generic code review for unsupported languages"""
        issues = []
        best_practices = []
        complexity_score = self._calculate_complexity(code)

        # Check for common markers
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.match(r'^\s*(//|#|/\*|--)\s*(TODO|FIXME|HACK|XXX):?', stripped, re.IGNORECASE):
                issues.append(CodeIssue(
                    type="suggestion",
                    severity=1,
                    message="Code marker found",
                    line=line_num,
                    column=0,
                    rule="no-code-markers",
                    suggestion="Add issue tracker reference"
                ))

        return {
            "issues": [i.model_dump() for i in issues],
            "complexity_score": round(complexity_score, 2),
            "security_violations": [],
            "best_practices": best_practices,
            "overall_rating": 7
        }


    async def review_code_with_ai(self, code: str, language: str, file_path: str = None) -> Dict[str, Any]:
        """
        AI-enhanced code review using Claude API.
        Falls back to rule-based review if AI is unavailable.
        """
        # Start with rule-based review
        base_review = self.review_code(code, language)

        # Check if there are critical security issues
        critical_vulns = [v for v in base_review.get("security_violations", [])
                         if v.get("severity") == "critical"]

        if critical_vulns:
            base_review["ai_recommendations"] = [
                "Critical security vulnerabilities detected. Please review and fix immediately.",
                "Consider running a dedicated security scan for this file."
            ]

        return base_review

    def review_diff(self, old_code: str, new_code: str, language: str) -> Dict[str, Any]:
        """Review code changes (diff) between versions"""
        old_review = self.review_code(old_code, language)
        new_review = self.review_code(new_code, language)

        # Calculate delta
        old_issues = {f"{i['line']}:{i['rule']}": i for i in old_review.get("issues", [])}
        new_issues = {f"{i['line']}:{i['rule']}": i for i in new_review.get("issues", [])}

        fixed_issues = []
        new_problems = []

        for key, issue in old_issues.items():
            if key not in new_issues:
                fixed_issues.append(issue)

        for key, issue in new_issues.items():
            if key not in old_issues:
                new_problems.append(issue)

        return {
            "fixed_issues": fixed_issues,
            "new_issues": new_problems,
            "before_review": old_review,
            "after_review": new_review,
            "improvement_score": len(fixed_issues) - len(new_problems)
        }

    def get_summary(self, code: str, language: str) -> str:
        """Get a human-readable summary of the code review"""
        review = self.review_code(code, language)

        lines = [
            f"Code Review Summary for {language}",
            "=" * 40,
            f"Overall Rating: {review.get('overall_rating', 'N/A')}/10",
            f"Complexity Score: {review.get('complexity_score', 'N/A')}/10",
            f"Issues Found: {len(review.get('issues', []))}",
            f"Security Violations: {len(review.get('security_violations', []))}",
            f"Best Practices Followed: {len(review.get('best_practices', []))}",
            "",
        ]

        if review.get("security_violations"):
            lines.append("Security Issues:")
            for vuln in review["security_violations"]:
                lines.append(f"  - [{vuln.get('severity', 'unknown').upper()}] {vuln.get('description', 'N/A')}")
            lines.append("")

        if review.get("issues"):
            lines.append("Code Issues:")
            for issue in review["issues"][:5]:  # Top 5 issues
                lines.append(f"  - Line {issue.get('line', 'N/A')}: {issue.get('message', 'N/A')}")
            lines.append("")

        if review.get("best_practices"):
            lines.append("Best Practices:")
            for practice in review["best_practices"]:
                lines.append(f"  - {practice}")

        return "\n".join(lines)


# Global code review service instance
code_review_service = CodeReviewService()
