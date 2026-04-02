from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..services.security_manager import (
    security_manager,
    SecurityReport,
    Vulnerability,
    PolicyViolation,
    AccessLog,
    SecurityPolicy
)

router = APIRouter(prefix="/security")

class ScanRequest(BaseModel):
    code: str
    file_path: str

class PolicyEnforcementRequest(BaseModel):
    code: str
    file_path: str
    policies: Optional[List[str]] = None

class AuditAccessRequest(BaseModel):
    user_id: str
    resource: str
    action: str
    ip_address: str
    success: bool
    details: Optional[str] = None

class SecurityReportRequest(BaseModel):
    code_files: Dict[str, str]  # file_path: content

class UpdatePolicyRequest(BaseModel):
    policy: SecurityPolicy

class ComplianceRequest(BaseModel):
    requirements: List[str]
    code_files: Dict[str, str]

@router.post("/scan", response_model=List[Vulnerability])
async def scan_for_vulnerabilities(request: ScanRequest):
    """Scan code for security vulnerabilities"""
    try:
        vulnerabilities = security_manager.scan_for_vulnerabilities(
            request.code,
            request.file_path
        )
        return vulnerabilities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enforce", response_model=List[PolicyViolation])
async def enforce_policies(request: PolicyEnforcementRequest):
    """Ensure code complies with organizational policies"""
    try:
        violations = security_manager.enforce_policies(
            request.code,
            request.file_path,
            request.policies
        )
        return violations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit")
async def audit_access(request: AuditAccessRequest):
    """Audit access to sensitive resources"""
    try:
        log = security_manager.audit_access(
            request.user_id,
            request.resource,
            request.action,
            request.ip_address,
            request.success,
            request.details
        )
        return {"message": "Access audited successfully", "log_id": log.timestamp.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report", response_model=SecurityReport)
async def generate_security_report(request: SecurityReportRequest):
    """Generate comprehensive security report"""
    try:
        report = security_manager.generate_security_report(request.code_files)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/policies")
async def list_policies():
    """List all security policies"""
    try:
        policies = [policy.dict() for policy in security_manager.policies.values()]
        return {"policies": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/policies/{policy_name}")
async def get_policy(policy_name: str):
    """Get a specific security policy"""
    try:
        policy = security_manager.get_policy(policy_name)
        if policy:
            return policy
        else:
            raise HTTPException(status_code=404, detail="Policy not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/policies/{policy_name}")
async def update_policy(policy_name: str, request: UpdatePolicyRequest):
    """Update a security policy"""
    try:
        success = security_manager.update_policy(policy_name, request.policy)
        if success:
            return {"message": "Policy updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update policy")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_access_logs(limit: int = 100):
    """Get recent access logs"""
    try:
        logs = security_manager.get_recent_access_logs(limit)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_code_security(code_files: Dict[str, str]):
    """Validate code security and provide recommendations"""
    try:
        # Scan for vulnerabilities
        all_vulnerabilities = []
        all_policy_violations = []

        for file_path, code in code_files.items():
            vulnerabilities = security_manager.scan_for_vulnerabilities(code, file_path)
            policy_violations = security_manager.enforce_policies(code, file_path)

            all_vulnerabilities.extend(vulnerabilities)
            all_policy_violations.extend(policy_violations)

        # Generate recommendations
        recommendations = []
        critical_issues = [v for v in all_vulnerabilities if v.severity == "critical"]
        high_issues = [v for v in all_vulnerabilities if v.severity == "high"]

        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical security issues immediately")
        if high_issues:
            recommendations.append(f"Prioritize {len(high_issues)} high-severity issues")
        if all_policy_violations:
            recommendations.append(f"Fix {len(all_policy_violations)} policy violations")

        # Security score calculation (simplified)
        total_issues = len(all_vulnerabilities) + len(all_policy_violations)
        security_score = max(0, 100 - (total_issues * 5))  # 5 points deducted per issue

        return {
            "security_score": security_score,
            "vulnerabilities_found": len(all_vulnerabilities),
            "policy_violations": len(all_policy_violations),
            "critical_issues": len(critical_issues),
            "recommendations": recommendations,
            "details": {
                "vulnerabilities": [v.dict() for v in all_vulnerabilities],
                "policy_violations": [v.dict() for v in all_policy_violations]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threats")
async def get_threat_intelligence():
    """Get threat intelligence and security advisories"""
    try:
        # In a real implementation, this would connect to threat intelligence feeds
        # For now, return sample data
        return {
            "current_threats": [
                {
                    "id": "THREAT-001",
                    "title": "Log4Shell Vulnerability",
                    "description": "Critical RCE vulnerability in Log4j",
                    "severity": "critical",
                    "affected_versions": ["log4j 2.0-beta9 through 2.14.1"],
                    "recommendation": "Upgrade to Log4j 2.15.0 or later"
                },
                {
                    "id": "THREAT-002",
                    "title": "Dependency Confusion Attacks",
                    "description": "Attackers publishing malicious packages with similar names",
                    "severity": "high",
                    "recommendation": "Use private package registries and lock file verification"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance")
async def check_compliance(request: ComplianceRequest):
    """Check compliance with security standards"""
    try:
        compliance_results = {}

        for requirement in request.requirements:
            if requirement == "owasp_top_10":
                # Check for OWASP Top 10 compliance
                owasp_violations = []
                for file_path, code in request.code_files.items():
                    # Simplified OWASP checks
                    if "eval(" in code:
                        owasp_violations.append(f"{file_path}: Potential Injection vulnerability")
                    if "document.cookie" in code and "=" in code:
                        owasp_violations.append(f"{file_path}: Potential XSS vulnerability")

                compliance_results[requirement] = {
                    "compliant": len(owasp_violations) == 0,
                    "violations": owasp_violations
                }
            elif requirement == "gdpr":
                # Check for GDPR compliance
                gdpr_violations = []
                for file_path, code in request.code_files.items():
                    if "personal_data" in code.lower() or "user_data" in code.lower():
                        if "encrypt" not in code.lower() and "hash" not in code.lower():
                            gdpr_violations.append(f"{file_path}: Personal data handling without encryption")

                compliance_results[requirement] = {
                    "compliant": len(gdpr_violations) == 0,
                    "violations": gdpr_violations
                }

        return {
            "compliance_status": compliance_results,
            "overall_compliant": all(result["compliant"] for result in compliance_results.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
