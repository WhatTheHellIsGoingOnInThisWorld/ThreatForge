from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import AttackSimulationJob, SimulationTool, SeverityLevel
from app.ai_service import AIAnalysisResult
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF reports for security simulation results with AI integration"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            spaceAfter=6,
            fontName='Courier'
        )
    
    def generate_report(
        self, 
        job: AttackSimulationJob, 
        tool_output: str,
        vulnerabilities: List[Dict[str, Any]], 
        risk_score: int,
        ai_result: Optional[AIAnalysisResult] = None
    ) -> bytes:
        """Generate a PDF report from simulation results with optional AI analysis"""
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Build the story (content)
        story = []
        
        # Title
        title_text = "AI-Enhanced Security Simulation Report" if ai_result else "Security Simulation Report"
        story.append(Paragraph(title_text, self.title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.extend(self._create_metadata_section(job, ai_result))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        if ai_result:
            story.extend(self._create_ai_executive_summary(job, ai_result))
        else:
            story.extend(self._create_executive_summary(job, risk_score, vulnerabilities))
        story.append(Spacer(1, 20))
        
        # Simulation Details
        story.extend(self._create_simulation_details(job))
        story.append(Spacer(1, 20))
        
        # AI Analysis Results (if available)
        if ai_result:
            story.extend(self._create_ai_analysis_section(ai_result))
            story.append(Spacer(1, 20))
        
        # Vulnerabilities Found
        if vulnerabilities:
            story.extend(self._create_vulnerabilities_section(vulnerabilities))
            story.append(Spacer(1, 20))
        
        # Tool Output
        if tool_output:
            story.extend(self._create_tool_output_section(tool_output))
            story.append(Spacer(1, 20))
        
        # Recommendations
        if ai_result:
            story.extend(self._create_ai_recommendations_section(ai_result))
        else:
            story.extend(self._create_recommendations_section(risk_score, vulnerabilities))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _create_metadata_section(self, job: AttackSimulationJob, ai_result: Optional[AIAnalysisResult] = None) -> List:
        """Create the metadata section of the report"""
        elements = []
        
        elements.append(Paragraph("Report Information", self.heading_style))
        
        # Create metadata table
        data = [
            ["Report ID", f"JOB-{job.id:06d}"],
            ["Generated Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Job Created", job.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Simulation Tool", job.simulation_tool.value.title()],
            ["Severity Level", job.severity_level.value.title()],
            ["Attack Vectors", str(job.number_of_attack_vectors)]
        ]
        
        if ai_result:
            data.extend([
                ["AI Model Used", ai_result.model_used],
                ["AI Confidence", f"{ai_result.confidence_score:.1%}"],
                ["Analysis Cost", f"${ai_result.cost_estimate:.4f}"]
            ])
        
        if job.completed_at:
            data.append(["Completed", job.completed_at.strftime("%Y-%m-%d %H:%M:%S UTC")])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_ai_executive_summary(self, job: AttackSimulationJob, ai_result: AIAnalysisResult) -> List:
        """Create the executive summary section with AI analysis"""
        elements = []
        
        elements.append(Paragraph("AI-Enhanced Executive Summary", self.heading_style))
        
        # AI-generated summary
        elements.append(Paragraph(
            f"<b>AI Analysis Summary:</b><br/><br/>{ai_result.executive_summary}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 15))
        
        # Key metrics
        elements.append(Paragraph("Key Findings:", self.normal_style))
        elements.append(Paragraph(
            f"• <b>Vulnerabilities Detected:</b> {len(ai_result.vulnerabilities)}<br/>"
            f"• <b>High/Critical Issues:</b> {len([v for v in ai_result.vulnerabilities if v.severity in ['high', 'critical']])}<br/>"
            f"• <b>Mitigation Actions:</b> {len(ai_result.mitigations)}<br/>"
            f"• <b>AI Confidence:</b> {ai_result.confidence_score:.1%}<br/>"
            f"• <b>Analysis Cost:</b> ${ai_result.cost_estimate:.4f}",
            self.normal_style
        ))
        
        return elements
    
    def _create_executive_summary(self, job: AttackSimulationJob, risk_score: int,
                                vulnerabilities: List[Dict[str, Any]]) -> List:
        """Create the executive summary section (legacy method)"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.heading_style))
        
        # Risk assessment
        risk_level = self._get_risk_level(risk_score)
        risk_color = self._get_risk_color(risk_score)
        
        summary_text = f"""
        This security simulation was conducted using {job.simulation_tool.value.title()} 
        against the target system: <b>{job.target_system_description}</b>.
        
        The simulation identified <b>{len(vulnerabilities)} vulnerability(ies)</b> with an 
        overall risk score of <b>{risk_score}/100</b>, which is classified as 
        <b style="color: {risk_color}">{risk_level}</b>.
        """
        
        elements.append(Paragraph(summary_text, self.normal_style))
        
        # Key findings
        if vulnerabilities:
            elements.append(Paragraph("Key Findings:", self.normal_style))
            for vuln in vulnerabilities[:3]:  # Show top 3
                elements.append(Paragraph(
                    f"• {vuln.get('description', 'Vulnerability detected')} "
                    f"({vuln.get('severity', 'unknown')} severity)",
                    self.normal_style
                ))
        
        return elements
    
    def _create_ai_analysis_section(self, ai_result: AIAnalysisResult) -> List:
        """Create the AI analysis results section"""
        elements = []
        
        elements.append(Paragraph("AI-Powered Security Analysis", self.heading_style))
        
        elements.append(Paragraph(
            f"<b>Analysis Model:</b> {ai_result.model_used}<br/>"
            f"<b>Confidence Score:</b> {ai_result.confidence_score:.1%}<br/>"
            f"<b>Analysis Cost:</b> ${ai_result.cost_estimate:.4f}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 15))
        
        # Technical details from AI
        if ai_result.technical_details:
            elements.append(Paragraph(
                f"<b>Technical Analysis:</b><br/><br/>{ai_result.technical_details}",
                self.normal_style
            ))
        
        return elements
    
    def _create_simulation_details(self, job: AttackSimulationJob) -> List:
        """Create the simulation details section"""
        elements = []
        
        elements.append(Paragraph("Simulation Details", self.heading_style))
        
        details_text = f"""
        <b>Target System:</b> {job.target_system_description}
        
        <b>Simulation Parameters:</b>
        • Tool: {job.simulation_tool.value.title()}
        • Severity Level: {job.severity_level.value.title()}
        • Number of Attack Vectors: {job.number_of_attack_vectors}
        • Job Status: {job.status.value.title()}
        """
        
        elements.append(Paragraph(details_text, self.normal_style))
        
        return elements
    
    def _create_vulnerabilities_section(self, vulnerabilities: List[Dict[str, Any]]) -> List:
        """Create the vulnerabilities section"""
        elements = []
        
        elements.append(Paragraph("Vulnerabilities Identified", self.heading_style))
        
        if not vulnerabilities:
            elements.append(Paragraph("No vulnerabilities were identified during this simulation.", self.normal_style))
            return elements
        
        # Create vulnerabilities table
        data = [["Type", "Description", "Severity"]]
        
        for vuln in vulnerabilities:
            data.append([
                vuln.get('type', 'Unknown'),
                vuln.get('description', 'No description'),
                vuln.get('severity', 'Unknown').title()
            ])
        
        table = Table(data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_tool_output_section(self, tool_output: str) -> List:
        """Create the tool output section"""
        elements = []
        
        elements.append(Paragraph("Tool Output", self.heading_style))
        
        # Truncate output if too long
        if len(tool_output) > 2000:
            truncated_output = tool_output[:2000] + "\n\n... [Output truncated for readability]"
        else:
            truncated_output = tool_output
        
        elements.append(Paragraph(
            f"<b>Raw Tool Output:</b><br/><br/>"
            f"<code>{truncated_output}</code>",
            self.normal_style
        ))
        
        return elements
    
    def _create_ai_recommendations_section(self, ai_result: AIAnalysisResult) -> List:
        """Create the recommendations section with AI-generated mitigations"""
        elements = []
        
        elements.append(Paragraph("AI-Generated Mitigation Recommendations", self.heading_style))
        
        if not ai_result.mitigations:
            elements.append(Paragraph("No specific mitigation actions are required based on the AI analysis.", self.normal_style))
            return elements
        
        # Create mitigation table
        data = [["Priority", "Action", "Description", "Cost", "Time", "Effectiveness"]]
        
        for mitigation in ai_result.mitigations:
            data.append([
                mitigation.priority.title(),
                mitigation.action,
                mitigation.description,
                mitigation.estimated_cost,
                mitigation.time_to_implement,
                mitigation.effectiveness
            ])
        
        table = Table(data, colWidths=[1*inch, 1.5*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Add detailed implementation steps
        for i, mitigation in enumerate(ai_result.mitigations, 1):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(
                f"<b>{i}. {mitigation.action}</b>",
                self.normal_style
            ))
            
            elements.append(Paragraph(
                f"<b>Description:</b> {mitigation.description}<br/>"
                f"<b>Priority:</b> {mitigation.priority.title()}<br/>"
                f"<b>Estimated Cost:</b> {mitigation.estimated_cost}<br/>"
                f"<b>Time to Implement:</b> {mitigation.time_to_implement}<br/>"
                f"<b>Effectiveness:</b> {mitigation.effectiveness}",
                self.normal_style
            ))
            
            if mitigation.implementation_steps:
                elements.append(Paragraph("<b>Implementation Steps:</b>", self.normal_style))
                for step in mitigation.implementation_steps:
                    elements.append(Paragraph(f"• {step}", self.normal_style))
        
        return elements
    
    def _create_recommendations_section(self, risk_score: int,
                                      vulnerabilities: List[Dict[str, Any]]) -> List:
        """Create the recommendations section (legacy method)"""
        elements = []
        
        elements.append(Paragraph("Recommendations", self.heading_style))
        
        if risk_score >= 80:
            recommendations = [
                "Immediate action required - Critical vulnerabilities detected",
                "Conduct comprehensive security audit",
                "Implement security patches and updates",
                "Review and update security policies",
                "Consider engaging external security consultants"
            ]
        elif risk_score >= 60:
            recommendations = [
                "High priority action required",
                "Address identified vulnerabilities promptly",
                "Review security configurations",
                "Update security monitoring tools",
                "Conduct security awareness training"
            ]
        elif risk_score >= 40:
            recommendations = [
                "Medium priority action recommended",
                "Address vulnerabilities within reasonable timeframe",
                "Review security practices",
                "Consider security improvements",
                "Monitor for new vulnerabilities"
            ]
        else:
            recommendations = [
                "Low risk level - maintain current security posture",
                "Continue regular security monitoring",
                "Keep systems updated",
                "Review security policies annually",
                "Consider proactive security measures"
            ]
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.normal_style))
        
        return elements
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level description based on score"""
        if risk_score >= 80:
            return "Critical"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        elif risk_score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _get_risk_color(self, risk_score: int) -> str:
        """Get color for risk level"""
        if risk_score >= 80:
            return "red"
        elif risk_score >= 60:
            return "orange"
        elif risk_score >= 40:
            return "yellow"
        else:
            return "green" 