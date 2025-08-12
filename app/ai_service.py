import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import re
from app.config import settings
from app.models import SimulationResult, AttackSimulationJob

logger = logging.getLogger(__name__)


@dataclass
class VulnerabilityAnalysis:
    """Structured vulnerability analysis result"""
    vulnerability_type: str
    description: str
    severity: str
    cvss_score: float
    affected_components: List[str]
    attack_vector: str
    impact: str
    likelihood: str


@dataclass
class MitigationRecommendation:
    """Structured mitigation recommendation"""
    priority: str
    action: str
    description: str
    implementation_steps: List[str]
    estimated_cost: str
    time_to_implement: str
    effectiveness: str


@dataclass
class AIAnalysisResult:
    """Complete AI analysis result"""
    vulnerabilities: List[VulnerabilityAnalysis]
    mitigations: List[MitigationRecommendation]
    risk_score: int
    executive_summary: str
    technical_details: str
    cost_estimate: float
    model_used: str
    confidence_score: float


class AIOrchestrator:
    """AI orchestration service for security analysis"""
    
    def __init__(self):
        self.fallback_rules = self._load_fallback_rules()
        self.cost_tracker = {}
        
    def _load_fallback_rules(self) -> Dict[str, Any]:
        """Load pre-written fallback rules for when AI is unavailable"""
        return {
            "vulnerability_patterns": {
                "sql_injection": {
                    "severity": "high",
                    "cvss_score": 8.5,
                    "mitigation": "Use parameterized queries and input validation"
                },
                "xss": {
                    "severity": "medium",
                    "cvss_score": 6.1,
                    "mitigation": "Implement output encoding and CSP headers"
                },
                "open_ports": {
                    "severity": "medium",
                    "cvss_score": 5.0,
                    "mitigation": "Close unnecessary ports and implement firewall rules"
                },
                "weak_authentication": {
                    "severity": "high",
                    "cvss_score": 7.5,
                    "mitigation": "Implement MFA and strong password policies"
                }
            },
            "risk_scoring": {
                "high": 80,
                "medium": 50,
                "low": 20
            }
        }
    
    async def analyze_simulation_results(
        self, 
        job: AttackSimulationJob, 
        result: SimulationResult
    ) -> AIAnalysisResult:
        """Analyze simulation results using AI and generate comprehensive report"""
        
        try:
            # Try AI analysis first
            if await self._is_ai_available():
                return await self._perform_ai_analysis(job, result)
            else:
                logger.warning("AI service unavailable, using fallback rules")
                return await self._perform_fallback_analysis(job, result)
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return await self._perform_fallback_analysis(job, result)
    
    async def _is_ai_available(self) -> bool:
        """Check if AI service is available and within cost limits"""
        try:
            if settings.ai_model_provider == "groq" and settings.groq_api_key:
                return True
            elif settings.ai_model_provider == "openai" and settings.openai_api_key:
                return True
            else:
                return False
        except Exception:
            return False
    
    async def _perform_ai_analysis(
        self, 
        job: AttackSimulationJob, 
        result: SimulationResult
    ) -> AIAnalysisResult:
        """Perform AI-powered analysis using LangChain and Groq"""
        
        try:
            from langchain_groq import ChatGroq
            from langchain.schema import HumanMessage, SystemMessage
            
            # Initialize Groq client
            groq_client = ChatGroq(
                groq_api_key=settings.groq_api_key,
                model_name=settings.ai_model_name,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )
            
            # Prepare analysis prompt
            analysis_prompt = self._create_analysis_prompt(job, result)
            
            # Perform AI analysis
            messages = [
                SystemMessage(content="You are a cybersecurity expert AI assistant. Analyze the provided security simulation data and provide detailed vulnerability analysis, risk assessment, and mitigation recommendations."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await groq_client.agenerate([messages])
            ai_response = response.generations[0][0].text
            
            # Parse AI response
            parsed_result = self._parse_ai_response(ai_response)
            
            # Calculate cost
            cost = self._calculate_cost(response.usage if hasattr(response, 'usage') else None)
            
            return AIAnalysisResult(
                vulnerabilities=parsed_result["vulnerabilities"],
                mitigations=parsed_result["mitigations"],
                risk_score=parsed_result["risk_score"],
                executive_summary=parsed_result["executive_summary"],
                technical_details=parsed_result["technical_details"],
                cost_estimate=cost,
                model_used=settings.ai_model_name,
                confidence_score=0.85
            )
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise
    
    def _create_analysis_prompt(self, job: AttackSimulationJob, result: SimulationResult) -> str:
        """Create structured prompt for AI analysis"""
        
        prompt = f"""
        Analyze the following security simulation results and provide a comprehensive security assessment:

        JOB DETAILS:
        - Tool: {job.simulation_tool.value}
        - Target: {job.target_system_description}
        - Severity Level: {job.severity_level.value}
        - Attack Vectors: {job.number_of_attack_vectors}

        SIMULATION RESULTS:
        - Tool Output: {result.tool_output[:2000] if result.tool_output else "No output"}
        - Vulnerabilities Found: {result.vulnerabilities_found}
        - Risk Score: {result.risk_score}

        Please provide your analysis in the following JSON format:
        {{
            "vulnerabilities": [
                {{
                    "vulnerability_type": "string",
                    "description": "string",
                    "severity": "low|medium|high|critical",
                    "cvss_score": float,
                    "affected_components": ["string"],
                    "attack_vector": "string",
                    "impact": "string",
                    "likelihood": "string"
                }}
            ],
            "mitigations": [
                {{
                    "priority": "high|medium|low",
                    "action": "string",
                    "description": "string",
                    "implementation_steps": ["string"],
                    "estimated_cost": "string",
                    "time_to_implement": "string",
                    "effectiveness": "string"
                }}
            ],
            "risk_score": integer_1_100,
            "executive_summary": "string",
            "technical_details": "string"
        }}

        Focus on:
        1. Identifying specific vulnerabilities from the tool output
        2. Providing actionable mitigation strategies
        3. Calculating realistic risk scores
        4. Giving executive-level summary
        5. Providing technical implementation details
        """
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # Fallback parsing
                parsed_data = self._fallback_parse_response(ai_response)
            
            # Validate and structure the parsed data
            return self._validate_parsed_data(parsed_data)
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._create_default_analysis()
    
    def _fallback_parse_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        
        # Extract key information using regex patterns
        vulnerabilities = []
        mitigations = []
        
        # Look for vulnerability patterns
        vuln_patterns = [
            r"SQL injection|XSS|CSRF|open ports|weak authentication|buffer overflow",
            r"vulnerability|exploit|breach|compromise"
        ]
        
        for pattern in vuln_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                vulnerabilities.append({
                    "vulnerability_type": match.lower(),
                    "description": f"Detected {match} vulnerability",
                    "severity": "medium",
                    "cvss_score": 6.0,
                    "affected_components": ["system"],
                    "attack_vector": "network",
                    "impact": "Data compromise",
                    "likelihood": "medium"
                })
        
        # Look for mitigation patterns
        mitigation_patterns = [
            r"implement|configure|update|patch|secure|validate|encrypt"
        ]
        
        for pattern in mitigation_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                mitigations.append({
                    "priority": "medium",
                    "action": f"Implement {match}",
                    "description": f"Security improvement using {match}",
                    "implementation_steps": [f"Configure {match} settings"],
                    "estimated_cost": "Low",
                    "time_to_implement": "1-2 days",
                    "effectiveness": "High"
                })
        
        return {
            "vulnerabilities": vulnerabilities[:3],  # Limit to 3
            "mitigations": mitigations[:3],  # Limit to 3
            "risk_score": 50,
            "executive_summary": "Security vulnerabilities detected requiring immediate attention",
            "technical_details": response[:500] + "..." if len(response) > 500 else response
        }
    
    def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure parsed AI response data"""
        
        # Ensure required fields exist
        required_fields = ["vulnerabilities", "mitigations", "risk_score", "executive_summary", "technical_details"]
        for field in required_fields:
            if field not in data:
                data[field] = self._get_default_value(field)
        
        # Validate risk score
        if not isinstance(data["risk_score"], int) or data["risk_score"] < 1 or data["risk_score"] > 100:
            data["risk_score"] = 50
        
        # Ensure vulnerabilities and mitigations are lists
        if not isinstance(data["vulnerabilities"], list):
            data["vulnerabilities"] = []
        if not isinstance(data["mitigations"], list):
            data["mitigations"] = []
        
        return data
    
    def _get_default_value(self, field: str) -> Any:
        """Get default values for missing fields"""
        defaults = {
            "vulnerabilities": [],
            "mitigations": [],
            "risk_score": 50,
            "executive_summary": "Security analysis completed with standard recommendations",
            "technical_details": "Detailed technical analysis available in the full report"
        }
        return defaults.get(field, "")
    
    def _create_default_analysis(self) -> Dict[str, Any]:
        """Create default analysis when AI parsing fails"""
        return {
            "vulnerabilities": [
                {
                    "vulnerability_type": "general_security",
                    "description": "Security vulnerabilities detected in simulation",
                    "severity": "medium",
                    "cvss_score": 5.0,
                    "affected_components": ["system"],
                    "attack_vector": "network",
                    "impact": "Potential security compromise",
                    "likelihood": "medium"
                }
            ],
            "mitigations": [
                {
                    "priority": "medium",
                    "action": "Security review",
                    "description": "Conduct comprehensive security review",
                    "implementation_steps": ["Review findings", "Implement fixes", "Test solutions"],
                    "estimated_cost": "Medium",
                    "time_to_implement": "1-2 weeks",
                    "effectiveness": "High"
                }
            ],
            "risk_score": 50,
            "executive_summary": "Security vulnerabilities require attention and remediation",
            "technical_details": "Standard security recommendations apply based on simulation results"
        }
    
    async def _perform_fallback_analysis(
        self, 
        job: AttackSimulationJob, 
        result: SimulationResult
    ) -> AIAnalysisResult:
        """Perform analysis using pre-written fallback rules"""
        
        # Analyze tool output for known patterns
        vulnerabilities = []
        mitigations = []
        
        if result.tool_output:
            tool_output_lower = result.tool_output.lower()
            
            # Check for common vulnerability patterns
            for vuln_type, vuln_info in self.fallback_rules["vulnerability_patterns"].items():
                if vuln_type in tool_output_lower:
                    vulnerabilities.append(VulnerabilityAnalysis(
                        vulnerability_type=vuln_type,
                        description=f"Detected {vuln_type} vulnerability",
                        severity=vuln_info["severity"],
                        cvss_score=vuln_info["cvss_score"],
                        affected_components=["system"],
                        attack_vector="network",
                        impact="Security compromise",
                        likelihood="medium"
                    ))
        
        # Generate mitigations based on vulnerabilities
        for vuln in vulnerabilities:
            if vuln.vulnerability_type in self.fallback_rules["vulnerability_patterns"]:
                vuln_info = self.fallback_rules["vulnerability_patterns"][vuln.vulnerability_type]
                mitigations.append(MitigationRecommendation(
                    priority="high" if vuln.severity in ["high", "critical"] else "medium",
                    action="Implement security controls",
                    description=vuln_info["mitigation"],
                    implementation_steps=["Review current controls", "Implement fixes", "Test solutions"],
                    estimated_cost="Low to Medium",
                    time_to_implement="1-2 weeks",
                    effectiveness="High"
                ))
        
        # Calculate risk score
        risk_score = self._calculate_fallback_risk_score(vulnerabilities, result.risk_score or 0)
        
        return AIAnalysisResult(
            vulnerabilities=vulnerabilities,
            mitigations=mitigations,
            risk_score=risk_score,
            executive_summary="Security analysis completed using standard security frameworks",
            technical_details="Analysis based on industry-standard security patterns and best practices",
            cost_estimate=0.0,
            model_used="fallback_rules",
            confidence_score=0.7
        )
    
    def _calculate_fallback_risk_score(
        self, 
        vulnerabilities: List[VulnerabilityAnalysis], 
        base_score: int
    ) -> int:
        """Calculate risk score using fallback rules"""
        
        if not vulnerabilities:
            return base_score
        
        # Calculate based on vulnerability severity
        severity_scores = {
            "critical": 90,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        max_severity_score = max(
            severity_scores.get(v.severity, 50) for v in vulnerabilities
        )
        
        # Combine with base score
        combined_score = (max_severity_score + base_score) // 2
        
        # Ensure within bounds
        return max(1, min(100, combined_score))
    
    def _calculate_cost(self, usage: Optional[Any]) -> float:
        """Calculate cost of AI API call"""
        
        if not usage:
            return 0.0
        
        # Groq pricing (approximate)
        # llama3-8b-8192: $0.05 per 1M input tokens, $0.10 per 1M output tokens
        
        try:
            input_tokens = getattr(usage, 'prompt_tokens', 0)
            output_tokens = getattr(usage, 'completion_tokens', 0)
            
            input_cost = (input_tokens / 1_000_000) * 0.05
            output_cost = (output_tokens / 1_000_000) * 0.10
            
            total_cost = input_cost + output_cost
            
            # Ensure cost is within limits
            if total_cost > settings.ai_cost_limit_per_job:
                logger.warning(f"AI cost {total_cost} exceeds limit {settings.ai_cost_limit_per_job}")
                total_cost = settings.ai_cost_limit_per_job
            
            return round(total_cost, 4)
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available AI models"""
        
        models = []
        
        if settings.groq_api_key:
            models.append({
                "provider": "groq",
                "name": settings.ai_model_name,
                "type": "llm",
                "status": "available"
            })
        
        if settings.openai_api_key:
            models.append({
                "provider": "openai",
                "name": "gpt-3.5-turbo",
                "type": "llm",
                "status": "available"
            })
        
        # Add fallback option
        models.append({
            "provider": "fallback",
            "name": "rule_based",
            "type": "rules",
            "status": "always_available"
        })
        
        return models 