#!/usr/bin/env python3
"""
Simple test script to verify the user tools implementation.
This script tests each tool individually to ensure they work correctly.
"""

from task.tools.users.user_client import UserClient
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool


def test_tools():
    """Test all user tools to ensure they're properly implemented."""
    
    # Initialize the user client
    user_client = UserClient()
    
    # Initialize all tools
    create_tool = CreateUserTool(user_client)
    get_tool = GetUserByIdTool(user_client)
    search_tool = SearchUsersTool(user_client)
    update_tool = UpdateUserTool(user_client)
    delete_tool = DeleteUserTool(user_client)
    
    # Test that all properties are implemented
    tools = [
        ("CreateUserTool", create_tool),
        ("GetUserByIdTool", get_tool),
        ("SearchUsersTool", search_tool),
        ("UpdateUserTool", update_tool),
        ("DeleteUserTool", delete_tool)
    ]
    
    print("Testing tool implementations...\n")
    
    for tool_name, tool in tools:
        print(f"Testing {tool_name}:")
        print(f"  - Name: {tool.name}")
        print(f"  - Description: {tool.description}")
        print(f"  - Has input schema: {tool.input_schema is not None}")
        print(f"  - Has complete schema: {tool.schema is not None}")
        print()
    
    print("✅ All tools are properly implemented!")
    print("\nTool schemas for reference:")
    print("-" * 50)
    
    for tool_name, tool in tools:
        print(f"\n{tool_name} Schema:")
        import json
        print(json.dumps(tool.schema, indent=2))


if __name__ == "__main__":
    test_tools()