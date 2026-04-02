import re
import ast
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import hashlib
import json
import os

class Vulnerability(BaseModel):
    id: str
    type: str  # sql_injection, xss, command_injection, etc.
    severity: str  # low, medium, high, critical
    file_path: str
    line_number: int
    description: str
    remediation: str
    code_snippet: str

class PolicyViolation(BaseModel):
    id: str
    policy_name: str
    file_path: str
    line_number: int
    description: str
    severity: str

class SecurityReport(BaseModel):
    scan_id: str
    timestamp: datetime
    vulnerabilities: List[Vulnerability]
    policy_violations: List[PolicyViolation]
    summary: Dict[str, int]  # severity: count
    recommendations: List[str]

class AccessLog(BaseModel):
    user_id: str
    resource: str
    action: str  # read, write, execute, delete
    timestamp: datetime
    ip_address: str
    success: bool
    details: Optional[str] = None

class SecurityPolicy(BaseModel):
    name: str
    description: str
    rules: List[Dict[str, Any]]  # Rule definitions
    enabled: bool = True
    created_at: datetime
    updated_at: datetime

class SecurityManager:
    def __init__(self, security_dir: str = "./security"):
        self.security_dir = security_dir
        os.makedirs(security_dir, exist_ok=True)
        self.policies = self._load_policies()
        self.access_logs: List[AccessLog] = []

    def _load_policies(self) -> Dict[str, SecurityPolicy]:
        """Load security policies from storage"""
        policies = {}
        policies_file = os.path.join(self.security_dir, "policies.json")

        if os.path.exists(policies_file):
            try:
                with open(policies_file, 'r') as f:
                    data = json.load(f)
                    for policy_data in data:
                        policy_data["created_at"] = datetime.fromisoformat(policy_data["created_at"])
                        policy_data["updated_at"] = datetime.fromisoformat(policy_data["updated_at"])
                        policy = SecurityPolicy(**policy_data)
                        policies[policy.name] = policy
            except Exception as e:
                print(f"Error loading policies: {e}")

        # Create default policies if none exist
        if not policies:
            default_policies = self._create_default_policies()
            policies.update(default_policies)
            self._save_policies(policies)

        return policies

    def _create_default_policies(self) -> Dict[str, SecurityPolicy]:
        """Create default security policies"""
        now = datetime.now()
        return {
            "no_hardcoded_secrets": SecurityPolicy(
                name="no_hardcoded_secrets",
                description="Prevent hardcoded secrets in code",
                rules=[{"pattern": r'(password|secret|key|token)\s*=\s*["\'][^"\']{5,}["\']', "type": "regex"}],
                enabled=True,
                created_at=now,
                updated_at=now
            ),
            "secure_file_permissions": SecurityPolicy(
                name="secure_file_permissions",
                description="Ensure secure file permissions",
                rules=[{"extension": ".env", "permissions": "600"}, {"extension": ".key", "permissions": "600"}],
                enabled=True,
                created_at=now,
                updated_at=now
            ),
            "no_eval_usage": SecurityPolicy(
                name="no_eval_usage",
                description="Prevent unsafe eval() usage",
                rules=[{"pattern": r"\beval\s*\(", "type": "regex"}],
                enabled=True,
                created_at=now,
                updated_at=now
            )
        }

    def _save_policies(self, policies: Dict[str, SecurityPolicy]):
        """Save policies to file"""
        try:
            policies_file = os.path.join(self.security_dir, "policies.json")
            policies_data = []
            for policy in policies.values():
                policy_dict = policy.dict()
                policy_dict["created_at"] = policy_dict["created_at"].isoformat()
                policy_dict["updated_at"] = policy_dict["updated_at"].isoformat()
                policies_data.append(policy_dict)

            with open(policies_file, 'w') as f:
                json.dump(policies_data, f, indent=2)
        except Exception as e:
            print(f"Error saving policies: {e}")

    def scan_for_vulnerabilities(self, code: str, file_path: str) -> List[Vulnerability]:
        """Scan code for security vulnerabilities"""
        vulnerabilities = []

        try:
            # Parse code to AST for deeper analysis
            tree = ast.parse(code)

            # Check for SQL injection vulnerabilities
            vulnerabilities.extend(self._check_sql_injection(tree, code, file_path))

            # Check for XSS vulnerabilities
            vulnerabilities.extend(self._check_xss_vulnerabilities(code, file_path))

            # Check for command injection
            vulnerabilities.extend(self._check_command_injection(code, file_path))

            # Check for hardcoded secrets
            vulnerabilities.extend(self._check_hardcoded_secrets(code, file_path))

            # Check for insecure deserialization
            vulnerabilities.extend(self._check_insecure_deserialization(code, file_path))

        except SyntaxError as e:
            vulnerabilities.append(Vulnerability(
                id=hashlib.md5(f"syntax_error_{file_path}".encode()).hexdigest()[:8],
                type="syntax_error",
                severity="low",
                file_path=file_path,
                line_number=0,
                description=f"Syntax error in code: {str(e)}",
                remediation="Fix syntax errors in the code",
                code_snippet=str(e)
            ))
        except Exception as e:
            print(f"Error scanning for vulnerabilities: {e}")

        return vulnerabilities

    def _check_sql_injection(self, tree: ast.AST, code: str, file_path: str) -> List[Vulnerability]:
        """Check for SQL injection vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                # Check for direct string concatenation in SQL queries
                if node.func.attr in ['execute', 'executemany'] and len(node.args) > 0:
                    # Check if first argument is a string with concatenation
                    if isinstance(node.args[0], ast.BinOp) and isinstance(node.args[0].op, ast.Add):
                        line_no = node.lineno
                        vulnerabilities.append(Vulnerability(
                            id=hashlib.md5(f"sql_injection_{file_path}_{line_no}".encode()).hexdigest()[:8],
                            type="sql_injection",
                            severity="high",
                            file_path=file_path,
                            line_number=line_no,
                            description="Potential SQL injection through string concatenation",
                            remediation="Use parameterized queries or ORM methods instead",
                            code_snippet=lines[line_no - 1] if line_no <= len(lines) else ""
                        ))

        return vulnerabilities

    def _check_xss_vulnerabilities(self, code: str, file_path: str) -> List[Vulnerability]:
        """Check for XSS vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')

        # Patterns that might indicate XSS
        xss_patterns = [
            r'render_template\s*\(',  # Flask templates
            r'response\.write\s*\(',   # Direct response writing
            r'document\.write\s*\(',   # Client-side JS
            r'innerHTML\s*=',
            r'outerHTML\s*='
        ]

        for line_no, line in enumerate(lines, 1):
            for pattern in xss_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append(Vulnerability(
                        id=hashlib.md5(f"xss_{file_path}_{line_no}".encode()).hexdigest()[:8],
                        type="xss",
                        severity="medium",
                        file_path=file_path,
                        line_number=line_no,
                        description="Potential XSS vulnerability detected",
                        remediation="Sanitize user input and use secure templating",
                        code_snippet=line
                    ))

        return vulnerabilities

    def _check_command_injection(self, code: str, file_path: str) -> List[Vulnerability]:
        """Check for command injection vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')

        # Dangerous functions that can lead to command injection
        dangerous_functions = [
            r'\bos\.system\s*\(',
            r'\bsubprocess\.call\s*\(',
            r'\bsubprocess\.run\s*\(',
            r'\bsubprocess\.Popen\s*\(',
            r'\bos\.popen\s*\('
        ]

        for line_no, line in enumerate(lines, 1):
            for pattern in dangerous_functions:
                if re.search(pattern, line):
                    vulnerabilities.append(Vulnerability(
                        id=hashlib.md5(f"cmd_injection_{file_path}_{line_no}".encode()).hexdigest()[:8],
                        type="command_injection",
                        severity="high",
                        file_path=file_path,
                        line_number=line_no,
                        description="Potential command injection vulnerability",
                        remediation="Validate and sanitize all inputs before executing commands",
                        code_snippet=line
                    ))

        return vulnerabilities

    def _check_hardcoded_secrets(self, code: str, file_path: str) -> List[Vulnerability]:
        """Check for hardcoded secrets"""
        vulnerabilities = []
        lines = code.split('\n')

        # Patterns for hardcoded secrets
        secret_patterns = [
            r'(password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{4,}',
            r'(secret|token|key)\s*[:=]\s*[\'"][^\'"]{8,}',
            r'AWS_SECRET_ACCESS_KEY\s*[:=]\s*[\'"][^\'"]{8,}',
            r'PRIVATE_KEY\s*[:=]\s*[\'"][^\'"]{8,}'
        ]

        for line_no, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(Vulnerability(
                        id=hashlib.md5(f"hardcoded_secret_{file_path}_{line_no}".encode()).hexdigest()[:8],
                        type="hardcoded_secret",
                        severity="critical",
                        file_path=file_path,
                        line_number=line_no,
                        description="Hardcoded secret detected",
                        remediation="Move secrets to environment variables or secure vault",
                        code_snippet=line
                    ))

        return vulnerabilities

    def _check_insecure_deserialization(self, code: str, file_path: str) -> List[Vulnerability]:
        """Check for insecure deserialization"""
        vulnerabilities = []
        lines = code.split('\n')

        # Dangerous deserialization functions
        dangerous_patterns = [
            r'pickle\.loads?\s*\(',
            r'yaml\.load\s*\(',
            r'json\.loads?\s*\([^,]*,\s*cls\s*=',
            r'eval\s*\('
        ]

        for line_no, line in enumerate(lines, 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append(Vulnerability(
                        id=hashlib.md5(f"insecure_deserialize_{file_path}_{line_no}".encode()).hexdigest()[:8],
                        type="insecure_deserialization",
                        severity="high",
                        file_path=file_path,
                        line_number=line_no,
                        description="Potentially insecure deserialization detected",
                        remediation="Use safe deserialization methods and validate input",
                        code_snippet=line
                    ))

        return vulnerabilities

    def enforce_policies(self, code: str, file_path: str, policies: List[str] = None) -> List[PolicyViolation]:
        """Ensure code complies with organizational policies"""
        violations = []

        if policies is None:
            policies = list(self.policies.keys())

        lines = code.split('\n')

        for policy_name in policies:
            if policy_name in self.policies:
                policy = self.policies[policy_name]
                if not policy.enabled:
                    continue

                for rule in policy.rules:
                    if rule.get("type") == "regex":
                        pattern = rule.get("pattern", "")
                        for line_no, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                violations.append(PolicyViolation(
                                    id=hashlib.md5(f"policy_{policy_name}_{file_path}_{line_no}".encode()).hexdigest()[:8],
                                    policy_name=policy_name,
                                    file_path=file_path,
                                    line_number=line_no,
                                    description=f"Policy violation: {policy.description}",
                                    severity="medium"
                                ))
                    elif "extension" in rule:
                        if file_path.endswith(rule["extension"]):
                            # Check file permissions (simplified)
                            pass  # In real implementation, check actual file permissions

        return violations

    def audit_access(self, user_id: str, resource: str, action: str,
                    ip_address: str, success: bool, details: str = None) -> AccessLog:
        """Audit access to sensitive resources"""
        log = AccessLog(
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.now(),
            ip_address=ip_address,
            success=success,
            details=details
        )

        self.access_logs.append(log)

        # Save to file for persistence
        try:
            log_file = os.path.join(self.security_dir, "access_logs.json")
            logs_data = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs_data = json.load(f)

            logs_data.append({
                "user_id": log.user_id,
                "resource": log.resource,
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "success": log.success,
                "details": log.details
            })

            with open(log_file, 'w') as f:
                json.dump(logs_data, f, indent=2)
        except Exception as e:
            print(f"Error saving access log: {e}")

        return log

    def generate_security_report(self, code_files: Dict[str, str]) -> SecurityReport:
        """Generate comprehensive security report"""
        import uuid

        all_vulnerabilities = []
        all_policy_violations = []

        for file_path, code in code_files.items():
            vulnerabilities = self.scan_for_vulnerabilities(code, file_path)
            policy_violations = self.enforce_policies(code, file_path)

            all_vulnerabilities.extend(vulnerabilities)
            all_policy_violations.extend(policy_violations)

        # Generate summary
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for vuln in all_vulnerabilities:
            severity_counts[vuln.severity] += 1
        for violation in all_policy_violations:
            severity_counts[violation.severity] += 1

        # Generate recommendations
        recommendations = []
        if severity_counts["critical"] > 0:
            recommendations.append("Address critical vulnerabilities immediately")
        if severity_counts["high"] > 0:
            recommendations.append("Prioritize high-severity issues")
        if len(all_policy_violations) > 0:
            recommendations.append("Review and update security policies")

        report = SecurityReport(
            scan_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            vulnerabilities=all_vulnerabilities,
            policy_violations=all_policy_violations,
            summary=severity_counts,
            recommendations=recommendations
        )

        # Save report
        try:
            report_file = os.path.join(self.security_dir, f"report_{report.scan_id}.json")
            report_dict = report.dict()
            report_dict["timestamp"] = report_dict["timestamp"].isoformat()
            with open(report_file, 'w') as f:
                json.dump(report_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving security report: {e}")

        return report

    def get_policy(self, policy_name: str) -> Optional[SecurityPolicy]:
        """Get a specific security policy"""
        return self.policies.get(policy_name)

    def update_policy(self, policy_name: str, policy: SecurityPolicy) -> bool:
        """Update a security policy"""
        self.policies[policy_name] = policy
        policy.updated_at = datetime.now()
        self._save_policies(self.policies)
        return True

    def get_recent_access_logs(self, limit: int = 100) -> List[AccessLog]:
        """Get recent access logs"""
        # In a real implementation, this would query a database
        # For now, return recent logs from memory
        return self.access_logs[-limit:] if self.access_logs else []

# Initialize security manager
security_manager = SecurityManager()
