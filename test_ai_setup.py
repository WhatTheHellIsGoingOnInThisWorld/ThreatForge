#!/usr/bin/env python3
"""
Test script to verify ThreatForge AI orchestration layer setup
"""

def test_ai_imports():
    """Test if all AI-related modules can be imported"""
    try:
        print("🔍 Testing AI module imports...")
        
        # Test AI service
        from app.ai_service import AIOrchestrator, AIAnalysisResult, VulnerabilityAnalysis, MitigationRecommendation
        print("✅ AI service modules imported successfully")
        
        # Test enhanced report generator
        from app.enhanced_report_generator import EnhancedPDFReportGenerator
        print("✅ Enhanced report generator imported successfully")
        
        # Test AI router
        from app.routers.ai import router as ai_router
        print("✅ AI router imported successfully")
        
        # Test LangChain and Groq (optional)
        try:
            from langchain_groq import ChatGroq
            print("✅ LangChain Groq imported successfully")
        except ImportError:
            print("⚠️  LangChain Groq not available (install with: pip install langchain-groq)")
        
        try:
            import groq
            print("✅ Groq client imported successfully")
        except ImportError:
            print("⚠️  Groq client not available (install with: pip install groq)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all AI dependencies:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ai_configuration():
    """Test AI configuration settings"""
    try:
        print("\n🔍 Testing AI configuration...")
        
        from app.config import settings
        
        print(f"✅ AI Model Provider: {settings.ai_model_provider}")
        print(f"✅ AI Fallback Enabled: {settings.ai_fallback_enabled}")
        print(f"✅ AI Cost Limit: ${settings.ai_cost_limit_per_job}")
        print(f"✅ AI Model Name: {settings.ai_model_name}")
        print(f"✅ AI Max Tokens: {settings.ai_max_tokens}")
        print(f"✅ AI Temperature: {settings.ai_temperature}")
        
        # Check API keys
        if settings.groq_api_key:
            print(f"✅ Groq API Key: {'Set' if settings.groq_api_key != 'your-groq-api-key-here' else 'Default (configure in .env)'}")
        else:
            print("⚠️  Groq API Key: Not configured")
        
        if settings.openai_api_key:
            print(f"✅ OpenAI API Key: {'Set' if settings.openai_api_key != 'your-openai-api-key-here' else 'Default (configure in .env)'}")
        else:
            print("⚠️  OpenAI API Key: Not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_ai_orchestrator():
    """Test AI orchestrator functionality"""
    try:
        print("\n🔍 Testing AI orchestrator...")
        
        from app.ai_service import AIOrchestrator
        
        # Create orchestrator instance
        orchestrator = AIOrchestrator()
        print("✅ AI orchestrator created successfully")
        
        # Test fallback rules loading
        fallback_rules = orchestrator.fallback_rules
        if fallback_rules and "vulnerability_patterns" in fallback_rules:
            print(f"✅ Fallback rules loaded: {len(fallback_rules['vulnerability_patterns'])} patterns")
        else:
            print("❌ Fallback rules not loaded properly")
            return False
        
        # Test available models
        models = orchestrator.get_available_models()
        if models:
            print(f"✅ Available models: {len(models)}")
            for model in models:
                print(f"   - {model['provider']}: {model['name']} ({model['status']})")
        else:
            print("❌ No models available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI orchestrator error: {e}")
        return False

def test_enhanced_report_generator():
    """Test enhanced PDF report generator"""
    try:
        print("\n🔍 Testing enhanced report generator...")
        
        from app.enhanced_report_generator import EnhancedPDFReportGenerator
        from app.ai_service import AIAnalysisResult, VulnerabilityAnalysis, MitigationRecommendation
        
        # Create report generator
        generator = EnhancedPDFReportGenerator()
        print("✅ Enhanced report generator created successfully")
        
        # Create mock AI analysis result
        mock_vulnerabilities = [
            VulnerabilityAnalysis(
                vulnerability_type="sql_injection",
                description="SQL injection vulnerability detected",
                severity="high",
                cvss_score=8.5,
                affected_components=["login_form", "search_function"],
                attack_vector="network",
                impact="Data compromise",
                likelihood="medium"
            )
        ]
        
        mock_mitigations = [
            MitigationRecommendation(
                priority="high",
                action="Implement parameterized queries",
                description="Use prepared statements to prevent SQL injection",
                implementation_steps=["Review code", "Replace queries", "Test thoroughly"],
                estimated_cost="Low",
                time_to_implement="2-3 days",
                effectiveness="High"
            )
        ]
        
        mock_ai_result = AIAnalysisResult(
            vulnerabilities=mock_vulnerabilities,
            mitigations=mock_mitigations,
            risk_score=75,
            executive_summary="Critical SQL injection vulnerability requires immediate attention",
            technical_details="SQL injection found in login form allowing unauthorized access",
            cost_estimate=0.002,
            model_used="groq_llama3",
            confidence_score=0.85
        )
        
        print("✅ Mock AI analysis result created successfully")
        
        # Test report generation (without actual job object)
        print("✅ Enhanced report generator test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced report generator error: {e}")
        return False

def test_ai_router():
    """Test AI router endpoints"""
    try:
        print("\n🔍 Testing AI router...")
        
        from app.routers.ai import router as ai_router
        
        # Check router configuration
        if ai_router.prefix == "/ai":
            print("✅ AI router prefix configured correctly")
        else:
            print("❌ AI router prefix incorrect")
            return False
        
        # Check available endpoints
        routes = [route.path for route in ai_router.routes]
        expected_routes = [
            "/ai/models",
            "/ai/analyze/{job_id}",
            "/ai/status/{job_id}",
            "/ai/costs",
            "/ai/batch-analyze",
            "/ai/health"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} available")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        print("✅ All AI router endpoints available")
        return True
        
    except Exception as e:
        print(f"❌ AI router error: {e}")
        return False

def test_cost_optimization():
    """Test AI cost optimization features"""
    try:
        print("\n🔍 Testing AI cost optimization...")
        
        from app.ai_service import AIOrchestrator
        
        orchestrator = AIOrchestrator()
        
        # Test cost calculation
        mock_usage = type('MockUsage', (), {
            'prompt_tokens': 1000,
            'completion_tokens': 500
        })()
        
        cost = orchestrator._calculate_cost(mock_usage)
        print(f"✅ Cost calculation: ${cost:.4f} for 1000 input + 500 output tokens")
        
        # Test cost limits
        if cost <= 0.01:
            print("✅ Cost within per-job limit ($0.01)")
        else:
            print("❌ Cost exceeds per-job limit")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cost optimization error: {e}")
        return False

def main():
    """Run all AI tests"""
    print("🚀 ThreatForge AI Orchestration Layer Test")
    print("=" * 50)
    
    tests = [
        test_ai_imports,
        test_ai_configuration,
        test_ai_orchestrator,
        test_enhanced_report_generator,
        test_ai_router,
        test_cost_optimization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 AI Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI tests passed! Your AI orchestration layer is ready.")
        print("\n🚀 AI Features Available:")
        print("   • AI-powered vulnerability analysis")
        print("   • Intelligent risk scoring")
        print("   • Automated mitigation recommendations")
        print("   • Cost-optimized processing")
        print("   • Fallback rule-based analysis")
        print("   • Enhanced PDF reporting")
        print("\n📚 AI API Endpoints:")
        print("   • GET /api/v1/ai/models - Available AI models")
        print("   • POST /api/v1/ai/analyze/{job_id} - Request AI analysis")
        print("   • GET /api/v1/ai/status/{job_id} - Analysis status")
        print("   • GET /api/v1/ai/costs - Cost summary")
        print("   • POST /api/v1/ai/batch-analyze - Batch processing")
        print("   • GET /api/v1/ai/health - AI service health")
    else:
        print("❌ Some AI tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 