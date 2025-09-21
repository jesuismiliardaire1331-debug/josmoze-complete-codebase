#!/usr/bin/env python3
"""
AI Agents System Testing for Josmose.com
Tests the complete AI agents system with Schopenhauer strategies
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://chatbot-debug-2.preview.emergentagent.com/api"

class AIAgentsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def authenticate_manager(self):
        """Authenticate as manager for AI agents tests"""
        try:
            login_data = {
                "username": "naima@josmose.com",
                "password": "Naima@2024!Commerce"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    return True
            return False
        except:
            return False

    def test_ai_agents_dashboard(self):
        """Test GET /api/crm/ai-agents/dashboard - Main AI agents dashboard with 5 agents"""
        try:
            if not self.authenticate_manager():
                self.log_test("AI Agents Dashboard", False, "Authentication failed")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/crm/ai-agents/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "dashboard" in data:
                    dashboard = data["dashboard"]
                    
                    # Check for 5 agents
                    agents_status = dashboard.get("agents_status", {})
                    expected_agents = ["socrate", "aristote", "ciceron", "demosthene", "platon"]
                    
                    found_agents = []
                    for agent_key in expected_agents:
                        if agent_key in agents_status:
                            agent_info = agents_status[agent_key]
                            agent_name = agent_info.get("name", "")
                            status = agent_info.get("status", "")
                            
                            found_agents.append(f"{agent_name} ({status})")
                    
                    if len(found_agents) == 5:
                        self.log_test("AI Agents Dashboard", True, 
                                    f"Dashboard loaded with all 5 agents: {', '.join(found_agents)}")
                        return True
                    else:
                        self.log_test("AI Agents Dashboard", False, f"Expected 5 agents, found {len(found_agents)}: {found_agents}")
                        return False
                else:
                    self.log_test("AI Agents Dashboard", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("AI Agents Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI Agents Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_schopenhauer_strategies(self):
        """Test GET /api/crm/ai-agents/schopenhauer-strategies - 38 dialectical strategies"""
        try:
            if not self.authenticate_manager():
                self.log_test("Schopenhauer Strategies", False, "Authentication failed")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/crm/ai-agents/schopenhauer-strategies")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "schopenhauer_reference" in data:
                    reference = data["schopenhauer_reference"]
                    
                    # Check for 38 strategies
                    total_stratagems = reference.get("total_stratagems", 0)
                    
                    if total_stratagems == 38:
                        self.log_test("Schopenhauer Strategies", True, 
                                    f"All 38 stratagems available")
                        return True
                    else:
                        self.log_test("Schopenhauer Strategies", False, f"Expected 38 stratagems, got {total_stratagems}")
                        return False
                else:
                    self.log_test("Schopenhauer Strategies", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Schopenhauer Strategies", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Schopenhauer Strategies", False, f"Exception: {str(e)}")
            return False

    def test_performance_analytics(self):
        """Test GET /api/crm/ai-agents/performance-analytics - Advanced analytics dashboard"""
        try:
            if not self.authenticate_manager():
                self.log_test("Performance Analytics", False, "Authentication failed")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/crm/ai-agents/performance-analytics?time_range=7days")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "analytics" in data:
                    analytics = data["analytics"]
                    
                    # Check global KPIs
                    global_kpis = analytics.get("global_kpis", {})
                    satisfaction_score = global_kpis.get("satisfaction_score", 0)
                    avg_response_time = global_kpis.get("average_response_time_seconds", 0)
                    
                    self.log_test("Performance Analytics", True, 
                                f"Analytics loaded: {satisfaction_score}% satisfaction, {avg_response_time}s response time")
                    return True
                else:
                    self.log_test("Performance Analytics", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Performance Analytics", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance Analytics", False, f"Exception: {str(e)}")
            return False

    def run_tests(self):
        """Run all AI agents tests"""
        print("🤖 AI AGENTS SYSTEM TESTING")
        print("="*50)
        
        self.test_ai_agents_dashboard()
        self.test_schopenhauer_strategies()
        self.test_performance_analytics()
        
        print("="*50)

if __name__ == "__main__":
    tester = AIAgentsTester()
    tester.run_tests()