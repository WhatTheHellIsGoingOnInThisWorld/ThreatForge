from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
from app.models import AttackSimulationJob, SimulationTool, SeverityLevel
from app.ai_service import AIAnalysisResult, VulnerabilityAnalysis, MitigationRecommendation
import logging

logger = logging.getLogger(__name__)


class EnhancedPDFReportGenerator:
    """Enhanced PDF report generator with AI analysis integration"""
    
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
        
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.darkred
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            spaceAfter=6,
            fontName='Courier'
        )
        
        self.highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.darkred,
            alignment=TA_JUSTIFY
        )
    
    def generate_enhanced_report(
        self, 
        job: AttackSimulationJob, 
        ai_result: AIAnalysisResult,
        tool_output: str = ""
    ) -> bytes:
        """Generate enhanced PDF report with AI analysis"""
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Build the story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page(job, ai_result))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(job, ai_result))
        story.append(PageBreak())
        
        # AI Analysis Results
        story.extend(self._create_ai_analysis_section(ai_result))
        story.append(PageBreak())
        
        # Vulnerability Details
        story.extend(self._create_vulnerabilities_section(ai_result.vulnerabilities))
        story.append(PageBreak())
        
        # Mitigation Recommendations
        story.extend(self._create_mitigations_section(ai_result.mitigations))
        story.append(PageBreak())
        
        # Risk Assessment
        story.extend(self._create_risk_assessment_section(ai_result))
        story.append(PageBreak())
        
        # Technical Details
        story.extend(self._create_technical_details_section(job, ai_result, tool_output))
        story.append(PageBreak())
        
        # Appendices
        story.extend(self._create_appendices_section(job, ai_result))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _create_title_page(self, job: AttackSimulationJob, ai_result: AIAnalysisResult) -> List:
        """Create the title page of the report"""
        elements = []
        
        # Main title
        elements.append(Paragraph("AI-Enhanced Security Analysis Report", self.title_style))
        elements.append(Spacer(1, 40))
        
        # Report metadata
        elements.append(Paragraph("Report Information", self.heading_style))
        
        data = [
            ["Report ID", f"JOB-{job.id:06d}"],
            ["Generated Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Job Created", job.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Simulation Tool", job.simulation_tool.value.title()],
            ["Severity Level", job.severity_level.value.title()],
            ["Attack Vectors", str(job.number_of_attack_vectors)],
            ["AI Model Used", ai_result.model_used],
            ["AI Confidence", f"{ai_result.confidence_score:.1%}"],
            ["Analysis Cost", f"${ai_result.cost_estimate:.4f}"]
        ]
        
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
        elements.append(Spacer(1, 30))
        
        # Risk score indicator
        risk_color = self._get_risk_color(ai_result.risk_score)
        risk_level = self._get_risk_level(ai_result.risk_score)
        
        elements.append(Paragraph(
            f"<b>Overall Risk Score: <span style='color: {risk_color}'>{ai_result.risk_score}/100</span> ({risk_level})</b>",
            self.heading_style
        ))
        
        return elements
    
    def _create_executive_summary(self, job: AttackSimulationJob, ai_result: AIAnalysisResult) -> List:
        """Create the executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.heading_style))
        elements.append(Spacer(1, 20))
        
        # AI-generated executive summary
        elements.append(Paragraph(
            f"<b>AI Analysis Summary:</b><br/><br/>{ai_result.executive_summary}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 20))
        
        # Key metrics
        elements.append(Paragraph("Key Findings:", self.subheading_style))
        
        # Create metrics table
        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Vulnerabilities Detected", str(len(ai_result.vulnerabilities)), 
             "⚠️" if ai_result.vulnerabilities else "✅"],
            ["High/Critical Issues", str(len([v for v in ai_result.vulnerabilities if v.severity in ["high", "critical"]])), 
             "🔴" if any(v.severity in ["high", "critical"] for v in ai_result.vulnerabilities) else "🟢"],
            ["Mitigation Actions", str(len(ai_result.mitigations)), "📋"],
            ["AI Confidence", f"{ai_result.confidence_score:.1%}", "🤖"],
            ["Analysis Cost", f"${ai_result.cost_estimate:.4f}", "💰"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    def _create_ai_analysis_section(self, ai_result: AIAnalysisResult) -> List:
        """Create the AI analysis results section"""
        elements = []
        
        elements.append(Paragraph("AI-Powered Security Analysis", self.heading_style))
        elements.append(Spacer(1, 20))
        
        # AI model information
        elements.append(Paragraph(
            f"<b>Analysis Model:</b> {ai_result.model_used}<br/>"
            f"<b>Confidence Score:</b> {ai_result.confidence_score:.1%}<br/>"
            f"<b>Analysis Cost:</b> ${ai_result.cost_estimate:.4f}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 20))
        
        # Create vulnerability severity chart
        if ai_result.vulnerabilities:
            elements.append(Paragraph("Vulnerability Distribution by Severity", self.subheading_style))
            
            # Count vulnerabilities by severity
            severity_counts = {}
            for vuln in ai_result.vulnerabilities:
                severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
            
            # Create pie chart
            chart_data = [severity_counts.get(sev, 0) for sev in ["critical", "high", "medium", "low"]]
            chart_labels = ["Critical", "High", "Medium", "Low"]
            
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 150
            pie.height = 150
            pie.data = chart_data
            pie.labels = chart_labels
            pie.slices.strokeWidth = 0.5
            
            # Color the slices
            colors_list = [colors.red, colors.orange, colors.yellow, colors.green]
            for i, color in enumerate(colors_list):
                if i < len(pie.slices):
                    pie.slices[i].fillColor = color
            
            drawing.add(pie)
            elements.append(drawing)
        
        return elements
    
    def _create_vulnerabilities_section(self, vulnerabilities: List[VulnerabilityAnalysis]) -> List:
        """Create the detailed vulnerabilities section"""
        elements = []
        
        elements.append(Paragraph("Detailed Vulnerability Analysis", self.heading_style))
        elements.append(Spacer(1, 20))
        
        if not vulnerabilities:
            elements.append(Paragraph(
                "No specific vulnerabilities were identified during this analysis. "
                "This may indicate a secure system or limited scope of testing.",
                self.normal_style
            ))
            return elements
        
        # Create detailed vulnerability table
        vuln_data = [["Type", "Description", "Severity", "CVSS", "Impact", "Likelihood"]]
        
        for vuln in vulnerabilities:
            vuln_data.append([
                vuln.vulnerability_type.title(),
                vuln.description,
                vuln.severity.title(),
                str(vuln.cvss_score),
                vuln.impact,
                vuln.likelihood
            ])
        
        vuln_table = Table(vuln_data, colWidths=[1.2*inch, 2.5*inch, 0.8*inch, 0.5*inch, 1.5*inch, 1*inch])
        vuln_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(vuln_table)
        
        # Add detailed descriptions for each vulnerability
        for i, vuln in enumerate(vulnerabilities, 1):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(
                f"<b>{i}. {vuln.vulnerability_type.title()} Vulnerability</b>",
                self.subheading_style
            ))
            
            elements.append(Paragraph(
                f"<b>Description:</b> {vuln.description}<br/>"
                f"<b>Severity:</b> {vuln.severity.title()}<br/>"
                f"<b>CVSS Score:</b> {vuln.cvss_score}<br/>"
                f"<b>Affected Components:</b> {', '.join(vuln.affected_components)}<br/>"
                f"<b>Attack Vector:</b> {vuln.attack_vector}<br/>"
                f"<b>Impact:</b> {vuln.impact}<br/>"
                f"<b>Likelihood:</b> {vuln.likelihood}",
                self.normal_style
            ))
        
        return elements
    
    def _create_mitigations_section(self, mitigations: List[MitigationRecommendation]) -> List:
        """Create the mitigation recommendations section"""
        elements = []
        
        elements.append(Paragraph("Mitigation Recommendations", self.heading_style))
        elements.append(Spacer(1, 20))
        
        if not mitigations:
            elements.append(Paragraph(
                "No specific mitigation actions are required based on the current analysis.",
                self.normal_style
            ))
            return elements
        
        # Create mitigation priority table
        priority_data = [["Priority", "Action", "Description", "Cost", "Time", "Effectiveness"]]
        
        for mitigation in mitigations:
            priority_data.append([
                mitigation.priority.title(),
                mitigation.action,
                mitigation.description,
                mitigation.estimated_cost,
                mitigation.time_to_implement,
                mitigation.effectiveness
            ])
        
        priority_table = Table(priority_data, colWidths=[0.8*inch, 1.5*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch])
        priority_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(priority_table)
        
        # Add detailed implementation steps for each mitigation
        for i, mitigation in enumerate(mitigations, 1):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(
                f"<b>{i}. {mitigation.action}</b>",
                self.subheading_style
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
    
    def _create_risk_assessment_section(self, ai_result: AIAnalysisResult) -> List:
        """Create the risk assessment section"""
        elements = []
        
        elements.append(Paragraph("Risk Assessment & Scoring", self.heading_style))
        elements.append(Spacer(1, 20))
        
        # Risk score visualization
        risk_color = self._get_risk_color(ai_result.risk_score)
        risk_level = self._get_risk_level(ai_result.risk_score)
        
        elements.append(Paragraph(
            f"<b>Overall Risk Score: <span style='color: {risk_color}'>{ai_result.risk_score}/100</span></b>",
            self.heading_style
        ))
        
        elements.append(Paragraph(
            f"<b>Risk Level:</b> {risk_level}<br/>"
            f"<b>AI Confidence:</b> {ai_result.confidence_score:.1%}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 20))
        
        # Risk breakdown
        elements.append(Paragraph("Risk Breakdown by Component", self.subheading_style))
        
        if ai_result.vulnerabilities:
            risk_breakdown_data = [["Component", "Risk Level", "Score"]]
            
            for vuln in ai_result.vulnerabilities:
                vuln_risk_score = self._calculate_vulnerability_risk_score(vuln)
                risk_breakdown_data.append([
                    vuln.vulnerability_type.title(),
                    vuln.severity.title(),
                    str(vuln_risk_score)
                ])
            
            risk_table = Table(risk_breakdown_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(risk_table)
        
        return elements
    
    def _create_technical_details_section(
        self, 
        job: AttackSimulationJob, 
        ai_result: AIAnalysisResult, 
        tool_output: str
    ) -> List:
        """Create the technical details section"""
        elements = []
        
        elements.append(Paragraph("Technical Analysis Details", self.heading_style))
        elements.append(Spacer(1, 20))
        
        # AI technical analysis
        elements.append(Paragraph(
            f"<b>AI-Generated Technical Analysis:</b><br/><br/>{ai_result.technical_details}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 20))
        
        # Tool output (truncated if too long)
        if tool_output:
            elements.append(Paragraph("Raw Tool Output", self.subheading_style))
            
            if len(tool_output) > 3000:
                truncated_output = tool_output[:3000] + "\n\n... [Output truncated for readability]"
            else:
                truncated_output = tool_output
            
            elements.append(Paragraph(
                f"<code>{truncated_output}</code>",
                self.code_style
            ))
        
        return elements
    
    def _create_appendices_section(self, job: AttackSimulationJob, ai_result: AIAnalysisResult) -> List:
        """Create the appendices section"""
        elements = []
        
        elements.append(Paragraph("Appendices", self.heading_style))
        elements.append(Spacer(1, 20))
        
        # Methodology
        elements.append(Paragraph("Analysis Methodology", self.subheading_style))
        elements.append(Paragraph(
            "This report was generated using an AI-powered security analysis system that combines:"
            "<br/>• Automated vulnerability detection from security tools"
            "<br/>• AI-powered risk assessment and scoring"
            "<br/>• Intelligent mitigation recommendation generation"
            "<br/>• Industry-standard security frameworks and best practices",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 15))
        
        # AI model information
        elements.append(Paragraph("AI Model Information", self.subheading_style))
        elements.append(Paragraph(
            f"<b>Model Used:</b> {ai_result.model_used}<br/>"
            f"<b>Confidence Score:</b> {ai_result.confidence_score:.1%}<br/>"
            f"<b>Analysis Cost:</b> ${ai_result.cost_estimate:.4f}<br/>"
            f"<b>Analysis Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            self.normal_style
        ))
        
        elements.append(Spacer(1, 15))
        
        # Disclaimer
        elements.append(Paragraph("Disclaimer", self.subheading_style))
        elements.append(Paragraph(
            "This report is generated using AI-powered analysis tools and should be reviewed by qualified "
            "security professionals. The recommendations provided are based on automated analysis and "
            "industry best practices, but may require customization for specific environments.",
            self.highlight_style
        ))
        
        return elements
    
    def _calculate_vulnerability_risk_score(self, vuln: VulnerabilityAnalysis) -> int:
        """Calculate individual vulnerability risk score"""
        base_scores = {
            "critical": 90,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        base_score = base_scores.get(vuln.severity.lower(), 50)
        
        # Adjust based on CVSS score
        cvss_adjustment = (vuln.cvss_score - 5.0) * 2  # Scale CVSS to 0-100
        
        final_score = base_score + cvss_adjustment
        
        return max(1, min(100, int(final_score)))
    
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