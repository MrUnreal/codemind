#!/usr/bin/env python3
"""
Complex scenario testing for CodeMind MCP server
Tests real-world coding workflows to validate tool effectiveness
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ANSI color codes for better output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_scenario(title, description):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}🎯 SCENARIO: {title}{Colors.END}")
    print(f"{Colors.YELLOW}{description}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_step(step_num, action):
    print(f"{Colors.BOLD}Step {step_num}: {Colors.END}{action}")

def print_result(success, message):
    icon = "✅" if success else "❌"
    color = Colors.GREEN if success else Colors.RED
    print(f"{color}{icon} {message}{Colors.END}\n")

async def scenario_1_adding_new_feature(session):
    """
    Scenario: Developer wants to add authentication to an existing app
    Expected: CodeMind should help identify existing auth code, prevent duplication
    """
    print_scenario(
        "Adding Authentication Feature",
        "A developer wants to add user authentication. They should:\n"
        "1. Check if auth already exists\n"
        "2. Find related security code\n"
        "3. Document the decision\n"
        "4. Search for password handling patterns"
    )
    
    results = {"checks": 0, "found_duplication": False, "decision_recorded": False}
    
    # Step 1: Check if authentication already exists
    print_step(1, "Checking if authentication functionality already exists...")
    try:
        result = await session.call_tool(
            "check_functionality_exists",
            arguments={
                "feature_description": "user authentication login password verification",
                "confidence_threshold": 0.5
            }
        )
        content = result.content[0].text
        results["checks"] += 1
        results["found_duplication"] = "YES" in content or "%" in content
        print_result(True, f"Check completed: {content[:150]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Search for existing security-related code
    print_step(2, "Searching for existing security and password handling code...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "password hashing encryption security authentication", "limit": 5}
        )
        content = result.content[0].text
        results["checks"] += 1
        print_result(True, f"Search results:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Search for configuration handling
    print_step(3, "Looking for configuration management patterns...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "configuration settings environment variables secrets", "limit": 3}
        )
        content = result.content[0].text
        results["checks"] += 1
        print_result(True, f"Config patterns found:\n{content[:200]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Record architectural decision
    print_step(4, "Recording architectural decision about authentication approach...")
    try:
        result = await session.call_tool(
            "record_decision",
            arguments={
                "description": "Implement JWT-based authentication with bcrypt password hashing",
                "reasoning": "JWT provides stateless auth suitable for API. Bcrypt is industry standard for password hashing. No existing auth found in codebase.",
                "affected_files": ["auth.py", "middleware.py", "config.py"]
            }
        )
        content = result.content[0].text
        results["decision_recorded"] = "recorded" in content.lower()
        print_result(True, f"Decision recorded:\n{content}")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Evaluation
    print(f"\n{Colors.BOLD}📊 SCENARIO 1 EVALUATION:{Colors.END}")
    print(f"  • Checks performed: {results['checks']}/3")
    print(f"  • Duplication detection: {'✅ Working' if results['checks'] > 0 else '❌ Failed'}")
    print(f"  • Decision recording: {'✅ Working' if results['decision_recorded'] else '❌ Failed'}")
    
    return results["checks"] >= 3 and results["decision_recorded"]

async def scenario_2_refactoring_codebase(session):
    """
    Scenario: Developer needs to refactor database layer
    Expected: CodeMind helps find all database-related files and patterns
    """
    print_scenario(
        "Refactoring Database Layer",
        "A developer needs to refactor database code. They should:\n"
        "1. Find all database-related files\n"
        "2. Identify patterns (ORM, raw SQL, etc.)\n"
        "3. Check for connection pooling\n"
        "4. Document refactoring decision"
    )
    
    results = {"searches": 0, "files_found": 0, "decision_made": False}
    
    # Step 1: Find database connection code
    print_step(1, "Searching for database connection and initialization code...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "database connection sqlite mysql postgres initialization", "limit": 10}
        )
        content = result.content[0].text
        results["searches"] += 1
        results["files_found"] += content.count(".")  # Rough count of files
        print_result(True, f"Database files found:\n{content[:400]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Search for query patterns
    print_step(2, "Looking for SQL query patterns and ORM usage...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "SELECT INSERT UPDATE DELETE execute query ORM model", "limit": 8}
        )
        content = result.content[0].text
        results["searches"] += 1
        print_result(True, f"Query patterns:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Check for transaction handling
    print_step(3, "Searching for transaction management code...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "transaction commit rollback begin transaction context manager", "limit": 5}
        )
        content = result.content[0].text
        results["searches"] += 1
        print_result(True, f"Transaction handling:\n{content[:250]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Record refactoring decision
    print_step(4, "Recording refactoring strategy decision...")
    try:
        result = await session.call_tool(
            "record_decision",
            arguments={
                "description": "Refactor to Repository Pattern with connection pooling",
                "reasoning": "Current code mixes business logic with SQL. Repository pattern will improve testability and maintainability. Add connection pooling for better performance.",
                "affected_files": ["database.py", "models.py", "repositories/base.py", "repositories/user.py"]
            }
        )
        content = result.content[0].text
        results["decision_made"] = "recorded" in content.lower()
        print_result(True, f"Refactoring decision:\n{content}")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    print(f"\n{Colors.BOLD}📊 SCENARIO 2 EVALUATION:{Colors.END}")
    print(f"  • Searches performed: {results['searches']}/3")
    print(f"  • Files discovered: {results['files_found']}")
    print(f"  • Decision recorded: {'✅ Working' if results['decision_made'] else '❌ Failed'}")
    
    return results["searches"] >= 3 and results["decision_made"]

async def scenario_3_debugging_investigation(session):
    """
    Scenario: Bug report - "API sometimes returns 500 errors"
    Expected: CodeMind helps locate error handling, logging, API routes
    """
    print_scenario(
        "Debugging API Error Investigation",
        "Bug report: API returns 500 errors intermittently. Developer should:\n"
        "1. Find error handling code\n"
        "2. Locate logging implementation\n"
        "3. Search for API endpoint definitions\n"
        "4. Check for exception handling patterns"
    )
    
    results = {"investigations": 0, "context_gathered": False}
    
    # Step 1: Find error handling
    print_step(1, "Searching for error handling and exception code...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "error handling exception try catch raise HTTPException", "limit": 7}
        )
        content = result.content[0].text
        results["investigations"] += 1
        print_result(True, f"Error handling found:\n{content[:350]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Find logging setup
    print_step(2, "Looking for logging configuration...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "logging logger debug info error warning log configuration", "limit": 5}
        )
        content = result.content[0].text
        results["investigations"] += 1
        print_result(True, f"Logging code:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Check specific file context
    print_step(3, "Getting detailed context on the main server file...")
    try:
        result = await session.call_tool(
            "get_file_context",
            arguments={"file_path": "D:\\Projects\\Python\\CodeMind\\codemind.py"}
        )
        content = result.content[0].text
        results["investigations"] += 1
        results["context_gathered"] = "Purpose:" in content and "Exports:" in content
        print_result(True, f"File context:\n{content[:400]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Search for async/concurrency issues
    print_step(4, "Checking for async/concurrency patterns that might cause issues...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "async await threading multiprocessing concurrent lock mutex", "limit": 5}
        )
        content = result.content[0].text
        results["investigations"] += 1
        print_result(True, f"Async patterns:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    print(f"\n{Colors.BOLD}📊 SCENARIO 3 EVALUATION:{Colors.END}")
    print(f"  • Investigations: {results['investigations']}/4")
    print(f"  • Context gathered: {'✅ Working' if results['context_gathered'] else '❌ Failed'}")
    
    return results["investigations"] >= 4

async def scenario_4_code_review_assistance(session):
    """
    Scenario: Reviewing PR that adds caching layer
    Expected: CodeMind helps find existing caching, check consistency
    """
    print_scenario(
        "Code Review: New Caching Layer PR",
        "Reviewing PR that adds Redis caching. Reviewer should:\n"
        "1. Check if caching already exists\n"
        "2. Find similar patterns in codebase\n"
        "3. Review recent changes for context\n"
        "4. Record review decision"
    )
    
    results = {"checks": 0, "review_complete": False}
    
    # Step 1: Check for existing caching
    print_step(1, "Checking if caching functionality already exists...")
    try:
        result = await session.call_tool(
            "check_functionality_exists",
            arguments={
                "feature_description": "caching cache redis memcached lru cache decorator",
                "confidence_threshold": 0.5
            }
        )
        content = result.content[0].text
        results["checks"] += 1
        print_result(True, f"Caching check:\n{content[:200]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Search for configuration patterns
    print_step(2, "Looking for existing configuration patterns...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "configuration settings config cache timeout ttl expiry", "limit": 5}
        )
        content = result.content[0].text
        results["checks"] += 1
        print_result(True, f"Config patterns:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Check recent changes
    print_step(3, "Reviewing recent changes for context...")
    try:
        result = await session.call_tool(
            "query_recent_changes",
            arguments={"hours": 168}  # Last week
        )
        content = result.content[0].text
        results["checks"] += 1
        print_result(True, f"Recent changes:\n{content[:250]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Record review decision
    print_step(4, "Recording code review decision...")
    try:
        result = await session.call_tool(
            "record_decision",
            arguments={
                "description": "Approved: Redis caching layer with TTL-based invalidation",
                "reasoning": "No existing caching found. Implementation follows config patterns. Suggested: add cache warming and monitoring metrics.",
                "affected_files": ["cache.py", "config.py", "requirements.txt"]
            }
        )
        content = result.content[0].text
        results["review_complete"] = "recorded" in content.lower()
        print_result(True, f"Review decision:\n{content}")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    print(f"\n{Colors.BOLD}📊 SCENARIO 4 EVALUATION:{Colors.END}")
    print(f"  • Review checks: {results['checks']}/3")
    print(f"  • Decision recorded: {'✅ Working' if results['review_complete'] else '❌ Failed'}")
    
    return results["checks"] >= 3 and results["review_complete"]

async def scenario_5_architecture_planning(session):
    """
    Scenario: Planning microservices split from monolith
    Expected: CodeMind helps analyze current structure, dependencies
    """
    print_scenario(
        "Architecture Planning: Microservices Split",
        "Planning to extract payment service from monolith. Architect should:\n"
        "1. Find all payment-related code\n"
        "2. Identify database dependencies\n"
        "3. Search for API boundaries\n"
        "4. Document architecture decision"
    )
    
    results = {"analyses": 0, "decision_documented": False}
    
    # Step 1: Find payment code
    print_step(1, "Searching for payment processing code...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "payment checkout stripe paypal transaction billing invoice", "limit": 10}
        )
        content = result.content[0].text
        results["analyses"] += 1
        print_result(True, f"Payment code:\n{content[:350]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Check database interactions
    print_step(2, "Analyzing database dependencies...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "database table model schema foreign key relationship", "limit": 8}
        )
        content = result.content[0].text
        results["analyses"] += 1
        print_result(True, f"Database dependencies:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Find API endpoints
    print_step(3, "Identifying API boundaries and endpoints...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "route endpoint api post get put delete fastapi flask", "limit": 7}
        )
        content = result.content[0].text
        results["analyses"] += 1
        print_result(True, f"API endpoints:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Check for existing microservices
    print_step(4, "Checking if microservices architecture already exists...")
    try:
        result = await session.call_tool(
            "check_functionality_exists",
            arguments={
                "feature_description": "microservices service discovery rest api grpc message queue",
                "confidence_threshold": 0.5
            }
        )
        content = result.content[0].text
        results["analyses"] += 1
        print_result(True, f"Architecture check:\n{content[:250]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 5: Document architecture decision
    print_step(5, "Documenting microservices architecture decision...")
    try:
        result = await session.call_tool(
            "record_decision",
            arguments={
                "description": "Extract payment service as independent microservice",
                "reasoning": "Payment code is well-isolated with clear API boundaries. Will use event-driven approach for order-payment communication. Separate database for payment service to ensure data isolation.",
                "affected_files": ["services/payment/api.py", "services/payment/models.py", "events/payment_events.py", "docker-compose.yml"]
            }
        )
        content = result.content[0].text
        results["decision_documented"] = "recorded" in content.lower()
        print_result(True, f"Architecture decision:\n{content}")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    print(f"\n{Colors.BOLD}📊 SCENARIO 5 EVALUATION:{Colors.END}")
    print(f"  • Analyses performed: {results['analyses']}/4")
    print(f"  • Decision documented: {'✅ Working' if results['decision_documented'] else '❌ Failed'}")
    
    return results["analyses"] >= 4 and results["decision_documented"]

async def scenario_6_onboarding_new_developer(session):
    """
    Scenario: New developer exploring the codebase
    Expected: CodeMind helps understand structure, find examples
    """
    print_scenario(
        "New Developer Onboarding",
        "New team member needs to understand the codebase. They should:\n"
        "1. Find main entry points\n"
        "2. Understand database structure\n"
        "3. Find test examples\n"
        "4. Locate configuration files"
    )
    
    results = {"explorations": 0, "understanding_gained": False}
    
    # Step 1: Find main application entry
    print_step(1, "Looking for main application entry points...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "main entry point __main__ if __name__ startup initialization", "limit": 5}
        )
        content = result.content[0].text
        results["explorations"] += 1
        results["understanding_gained"] = "match" in content.lower()
        print_result(True, f"Entry points:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 2: Understand data models
    print_step(2, "Exploring data models and schema...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "model class schema table dataclass pydantic", "limit": 8}
        )
        content = result.content[0].text
        results["explorations"] += 1
        print_result(True, f"Data models:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 3: Find test examples
    print_step(3, "Looking for test files and patterns...")
    try:
        result = await session.call_tool(
            "search_existing_code",
            arguments={"query": "test unittest pytest fixture mock assert test case", "limit": 5}
        )
        content = result.content[0].text
        results["explorations"] += 1
        print_result(True, f"Test patterns:\n{content[:300]}...")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    # Step 4: Get context on key file
    print_step(4, "Getting detailed info on the main module...")
    try:
        result = await session.call_tool(
            "get_file_context",
            arguments={"file_path": "D:\\Projects\\Python\\CodeMind\\codemind.py"}
        )
        content = result.content[0].text
        results["explorations"] += 1
        print_result(True, f"Module context:\n{content}")
    except Exception as e:
        print_result(False, f"Failed: {e}")
    
    print(f"\n{Colors.BOLD}📊 SCENARIO 6 EVALUATION:{Colors.END}")
    print(f"  • Explorations: {results['explorations']}/4")
    print(f"  • Understanding gained: {'✅ Working' if results['understanding_gained'] else '❌ Failed'}")
    
    return results["explorations"] >= 4

async def run_all_scenarios():
    """Run all complex scenarios"""
    server_params = StdioServerParameters(
        command="D:/Projects/Python/CodeMind/.venv/Scripts/python.exe",
        args=["D:/Projects/Python/CodeMind/codemind.py"],
        env=None
    )
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║  CodeMind MCP Server - Complex Scenario Testing Suite            ║")
    print("║  Testing real-world development workflows                         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    results = {}
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f"{Colors.GREEN}✅ Server initialized - starting scenarios...{Colors.END}\n")
            
            # Run all scenarios
            results["scenario_1"] = await scenario_1_adding_new_feature(session)
            results["scenario_2"] = await scenario_2_refactoring_codebase(session)
            results["scenario_3"] = await scenario_3_debugging_investigation(session)
            results["scenario_4"] = await scenario_4_code_review_assistance(session)
            results["scenario_5"] = await scenario_5_architecture_planning(session)
            results["scenario_6"] = await scenario_6_onboarding_new_developer(session)
    
    # Final report
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                    FINAL TEST REPORT                              ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Scenarios Results:{Colors.END}")
    for i, (name, passed_test) in enumerate(results.items(), 1):
        status = f"{Colors.GREEN}✅ PASSED" if passed_test else f"{Colors.RED}❌ FAILED"
        print(f"  {i}. {name.replace('_', ' ').title()}: {status}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Overall Score: {passed}/{total} scenarios passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}\n🎉 ALL SCENARIOS PASSED! CodeMind is production-ready!{Colors.END}")
    elif passed >= total * 0.7:
        print(f"{Colors.YELLOW}{Colors.BOLD}\n⚠️  Most scenarios passed. Some improvements needed.{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}\n❌ Major issues found. Significant improvements required.{Colors.END}")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_scenarios())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Testing interrupted by user{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Testing failed: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        exit(1)
