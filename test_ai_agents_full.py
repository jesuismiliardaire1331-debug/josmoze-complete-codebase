#!/usr/bin/env python3
"""
Complete AI Agents System Testing for Josmose.com
Tests all AI agents endpoints with Schopenhauer strategies
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://josmoze-crm.preview.emergentagent.com/api"

class AIAgentsFullTester:
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
                        # Check for expected agent names with emojis
                        expected_names = ["Socrate 🧠", "Aristote 📞", "Cicéron 💬", "Démosthène 🛒", "Platon 📊"]
                        actual_names = [agents_status[key]["name"] for key in expected_agents if key in agents_status]
                        
                        if all(name in actual_names for name in expected_names):
                            self.log_test("AI Agents Dashboard", True, 
                                        f"Dashboard loaded with all 5 agents: {', '.join(found_agents)}")
                            return True
                        else:
                            self.log_test("AI Agents Dashboard", False, f"Missing expected agent names. Found: {actual_names}")
                            return False
                    else:
                        self.log_test("AI Agents Dashboard", False, f"Expected 5 agents, found {len(found_agents)}: {found_agents}")
                        return False
                else:
                    self.log_test("AI Agents Dashboard", False, f"Invalid response structure")
                    return False
            else:
                self.log_test("AI Agents Dashboard", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Agents Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_agent_status_control(self):
        """Test PUT /api/crm/ai-agents/{agent_name}/status - Toggle agents ON/OFF"""
        try:
            if not self.authenticate_manager():
                self.log_test("Agent Status Control", False, "Authentication failed")
                return False
            
            # Test toggling Socrate agent status
            agent_name = "socrate"
            
            # First, try to activate the agent
            status_data = {"status": "active"}
            
            response = self.session.put(
                f"{BACKEND_URL}/crm/ai-agents/{agent_name}/status",
                json=status_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "status_change" in data:
                    status_change = data["status_change"]
                    
                    if status_change.get("status") == "success":
                        agent_name_display = status_change.get("agent", "")
                        new_status = status_change.get("new_status", "")
                        
                        self.log_test("Agent Status Control", True, 
                                    f"Successfully controlled {agent_name_display} -> {new_status}")
                        return True
                    else:
                        self.log_test("Agent Status Control", False, f"Status change failed: {status_change}")
                        return False
                else:
                    self.log_test("Agent Status Control", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Agent Status Control", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agent Status Control", False, f"Exception: {str(e)}")
            return False

    def test_client_profiling_system(self):
        """Test GET /api/crm/ai-agents/client-profiles - Client personality analysis"""
        try:
            if not self.authenticate_manager():
                self.log_test("Client Profiling System", False, "Authentication failed")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/crm/ai-agents/client-profiles?limit=20")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "profiles" in data and "statistics" in data:
                    profiles = data["profiles"]
                    statistics = data["statistics"]
                    
                    # Check statistics structure
                    required_stats = ["total_profiles", "personality_distribution", "high_conversion", "cart_abandoned"]
                    if all(stat in statistics for stat in required_stats):
                        total_profiles = statistics["total_profiles"]
                        high_conversion = statistics["high_conversion"]
                        cart_abandoned = statistics["cart_abandoned"]
                        
                        self.log_test("Client Profiling System", True, 
                                    f"Profiles loaded: {total_profiles} total, {high_conversion} high conversion, {cart_abandoned} abandoned carts")
                        return True
                    else:
                        missing_stats = [stat for stat in required_stats if stat not in statistics]
                        self.log_test("Client Profiling System", False, f"Missing statistics: {missing_stats}")
                        return False
                else:
                    self.log_test("Client Profiling System", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Client Profiling System", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Client Profiling System", False, f"Exception: {str(e)}")
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
                    actively_used = reference.get("actively_used", 0)
                    strategies = reference.get("strategies", [])
                    
                    if total_stratagems == 38:
                        self.log_test("Schopenhauer Strategies", True, 
                                    f"All 38 stratagems available, {actively_used} actively used, {len(strategies)} with usage stats")
                        return True
                    else:
                        self.log_test("Schopenhauer Strategies", False, f"Expected 38 stratagems, got {total_stratagems}")
                        return False
                else:
                    self.log_test("Schopenhauer Strategies", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Schopenhauer Strategies", False, f"Status: {response.status_code}")
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
                    required_kpis = ["total_interactions", "average_response_time_seconds", "satisfaction_score", "target_satisfaction"]
                    
                    if all(kpi in global_kpis for kpi in required_kpis):
                        total_interactions = global_kpis["total_interactions"]
                        avg_response_time = global_kpis["average_response_time_seconds"]
                        satisfaction_score = global_kpis["satisfaction_score"]
                        target_satisfaction = global_kpis["target_satisfaction"]
                        
                        # Check if satisfaction meets target (95%+)
                        meets_target = satisfaction_score >= target_satisfaction
                        
                        self.log_test("Performance Analytics", True, 
                                    f"KPIs: {total_interactions} interactions, {avg_response_time}s response, {satisfaction_score}% satisfaction (target: {target_satisfaction}%)")
                        
                        if meets_target and satisfaction_score >= 95.0:
                            self.log_test("Satisfaction Target", True, 
                                        f"Satisfaction {satisfaction_score}% exceeds 95% target")
                        
                        if avg_response_time < 300:  # Less than 5 minutes
                            self.log_test("Response Time Target", True, 
                                        f"Response time {avg_response_time}s meets <5min target")
                        
                        return True
                    else:
                        missing_kpis = [kpi for kpi in required_kpis if kpi not in global_kpis]
                        self.log_test("Performance Analytics", False, f"Missing KPIs: {missing_kpis}")
                        return False
                else:
                    self.log_test("Performance Analytics", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Performance Analytics", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Performance Analytics", False, f"Exception: {str(e)}")
            return False

    def test_agent_interaction(self):
        """Test POST /api/crm/ai-agents/{agent_name}/interact - Agent interaction"""
        try:
            if not self.authenticate_manager():
                self.log_test("Agent Interaction", False, "Authentication failed")
                return False
            
            # Test interaction with Socrate agent
            interaction_data = {
                "client_data": {
                    "name": "Marie Dubois",
                    "email": "marie.dubois@example.fr",
                    "phone": "+33123456789"
                },
                "message_type": "sms"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/crm/ai-agents/socrate/interact",
                json=interaction_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "interaction_result" in data:
                    interaction_result = data["interaction_result"]
                    
                    # Check interaction result structure
                    if interaction_result.get("status") == "success":
                        agent_name = interaction_result.get("agent", "")
                        message = interaction_result.get("message", "")
                        
                        if "Socrate" in agent_name and len(message) > 0:
                            self.log_test("Agent Interaction", True, 
                                        f"Successful interaction with {agent_name}, message length: {len(message)} chars")
                            return True
                        else:
                            self.log_test("Agent Interaction", False, f"Invalid agent response: {agent_name}")
                            return False
                    elif interaction_result.get("status") == "agent_inactive":
                        self.log_test("Agent Interaction", True, 
                                    f"Agent correctly reported as inactive: {interaction_result.get('message', '')}")
                        return True
                    else:
                        self.log_test("Agent Interaction", False, f"Interaction failed: {interaction_result}")
                        return False
                else:
                    self.log_test("Agent Interaction", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Agent Interaction", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agent Interaction", False, f"Exception: {str(e)}")
            return False

    def test_working_hours_configuration(self):
        """Test agent working hours configuration (9h-18h vs 24/7)"""
        try:
            if not self.authenticate_manager():
                self.log_test("Working Hours Configuration", False, "Authentication failed")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/crm/ai-agents/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "dashboard" in data:
                    dashboard = data["dashboard"]
                    agents_status = dashboard.get("agents_status", {})
                    
                    # Check working hours for each agent
                    working_hours_correct = True
                    agent_schedules = []
                    
                    for agent_key, agent_info in agents_status.items():
                        working_hours = agent_info.get("working_hours", {})
                        agent_name = agent_info.get("name", agent_key)
                        
                        if agent_key in ["socrate", "platon"]:
                            # Should be 24/7
                            if working_hours.get("always_active"):
                                agent_schedules.append(f"{agent_name}: 24/7 ✓")
                            else:
                                agent_schedules.append(f"{agent_name}: NOT 24/7 ✗")
                                working_hours_correct = False
                        else:
                            # Should have specific hours (9h-18h)
                            if "start_time" in working_hours and "end_time" in working_hours:
                                start_time = working_hours.get("start_time", "")
                                end_time = working_hours.get("end_time", "")
                                agent_schedules.append(f"{agent_name}: {start_time}-{end_time} ✓")
                            else:
                                agent_schedules.append(f"{agent_name}: No schedule ✗")
                                working_hours_correct = False
                    
                    if working_hours_correct:
                        self.log_test("Working Hours Configuration", True, 
                                    f"All agents have correct schedules: {'; '.join(agent_schedules)}")
                        return True
                    else:
                        self.log_test("Working Hours Configuration", False, 
                                    f"Schedule issues: {'; '.join(agent_schedules)}")
                        return False
                else:
                    self.log_test("Working Hours Configuration", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Working Hours Configuration", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Working Hours Configuration", False, f"Exception: {str(e)}")
            return False

    def run_tests(self):
        """Run all AI agents tests"""
        print("🤖 COMPLETE AI AGENTS SYSTEM TESTING")
        print("="*60)
        
        tests_passed = 0
        total_tests = 7
        
        if self.test_ai_agents_dashboard():
            tests_passed += 1
        if self.test_agent_status_control():
            tests_passed += 1
        if self.test_client_profiling_system():
            tests_passed += 1
        if self.test_schopenhauer_strategies():
            tests_passed += 1
        if self.test_performance_analytics():
            tests_passed += 1
        if self.test_agent_interaction():
            tests_passed += 1
        if self.test_working_hours_configuration():
            tests_passed += 1
        
        print("="*60)
        print(f"📊 RESULTS: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.1f}%)")
        print("="*60)

if __name__ == "__main__":
    tester = AIAgentsFullTester()
    tester.run_tests()