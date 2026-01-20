import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:
    """
    Client for interacting with the DIAL API.
    This class handles communication with the AI model and manages tool execution.
    """

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        """
        Initialize the DIAL client.
        
        Args:
            endpoint: Base URL for the DIAL API
            deployment_name: Name of the model deployment to use
            api_key: API key for authentication
            tools: List of tools the AI can use
        """
        # 1. Check if API key is provided, raise error if not
        if not api_key:
            raise ValueError("API key is required for DIAL client")
        
        # 2. Format the complete endpoint URL with the model deployment name
        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        
        # 3. Store the API key for authentication
        self.__api_key = api_key
        
        # 4. Create a dictionary for quick tool lookup by name
        # This allows us to easily find and execute tools when the AI requests them
        self.__tools_dict = {}
        if tools:
            for tool in tools:
                self.__tools_dict[tool.name] = tool
        
        # 5. Prepare the list of tool schemas that will be sent to the AI
        # The AI needs these schemas to know what tools are available
        self.__tools = []
        if tools:
            for tool in tools:
                self.__tools.append(tool.schema)
        
        # 6. Optional: Print configuration info for debugging
        print(f"🚀 DIAL Client initialized")
        print(f"📍 Endpoint: {self.__endpoint}")
        print(f"🔧 Available tools: {list(self.__tools_dict.keys()) if self.__tools_dict else 'None'}")
        if self.__tools:
            print(f"📋 Tool schemas loaded: {len(self.__tools)} tools")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        """
        Get a completion from the AI model.
        
        Args:
            messages: Conversation history
            print_request: Whether to print debug information
            
        Returns:
            The AI's response message
        """
        # 1. Create headers for the API request
        headers = {
            "api-key": self.__api_key,  # Authentication
            "Content-Type": "application/json"  # We're sending JSON data
        }
        
        # 2. Prepare the request data with message history and available tools
        request_data = {
            "messages": [msg.to_dict() for msg in messages],  # Convert Message objects to dictionaries
            "tools": self.__tools  # Include available tools so AI knows what it can use
        }
        
        # 3. Optional: Print the message history for debugging
        if print_request:
            print("\n📤 Sending request with messages:")
            for msg in messages[-3:]:  # Show last 3 messages for brevity
                role = msg.role.value
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                print(f"  [{role}]: {content}")
        
        # 4. Make the POST request to the DIAL API
        response = requests.post(
            url=self.__endpoint,
            headers=headers,
            json=request_data
        )
        
        # 5. Process the response if successful
        if response.status_code == 200:
            # Parse the JSON response
            response_json = response.json()
            
            # Get the choices array from response
            choices = response_json.get("choices", [])
            
            # Get the first choice (there's usually only one)
            choice = choices[0] if choices else {}
            
            # Optional: Print choice for debugging
            if print_request:
                print(f"📥 Received response with finish_reason: {choice.get('finish_reason')}")
            
            # Extract message data from the choice
            message_data = choice.get("message", {})
            
            # Get the content (what the AI said)
            content = message_data.get("content", "")
            
            # Get any tool calls (functions the AI wants to execute)
            tool_calls = message_data.get("tool_calls", None)
            
            # Create a Message object with the AI's response
            ai_response = Message(
                role=Role.AI,
                content=content,
                tool_calls=tool_calls
            )
            
            # Check if the AI wants to use tools
            if choice.get("finish_reason") == "tool_calls":
                # Yes, the AI wants to use tools
                print("\n🔧 AI requested tool execution")
                
                # Add the AI's message (with tool requests) to history
                messages.append(ai_response)
                
                # Execute the requested tools and get results
                tool_messages = self._process_tool_calls(tool_calls)
                
                # Add tool results to the conversation history
                messages.extend(tool_messages)
                
                # Recursively call to get the final response after tool execution
                # The AI will now see the tool results and provide a final answer
                return self.get_completion(messages, print_request)
            else:
                # No tools needed, return the final response
                return ai_response
        else:
            # Handle API errors
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """
        Process tool calls requested by the AI and return results as messages.
        
        Args:
            tool_calls: List of tool call requests from the AI
            
        Returns:
            List of messages containing tool execution results
        """
        tool_messages = []
        
        for tool_call in tool_calls:
            # 1. Extract the unique ID for this tool call
            # This ID links the request to its response
            tool_call_id = tool_call.get("id")
            
            # 2. Get the function details
            function = tool_call.get("function", {})
            
            # 3. Get the function name to identify which tool to use
            function_name = function.get("name")
            
            # 4. Parse the arguments from JSON string to dictionary
            arguments_str = function.get("arguments", "{}")
            arguments = json.loads(arguments_str)
            
            # 5. Execute the tool with the provided arguments
            tool_execution_result = self._call_tool(function_name, arguments)
            
            # 6. Create a message with the tool execution result
            # The tool_call_id is crucial - it tells the AI which request this result belongs to
            tool_message = Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,
                content=tool_execution_result
            )
            tool_messages.append(tool_message)
            
            # 7. Print execution details for debugging
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")
        
        # 8. Return all tool result messages
        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        """
        Execute a specific tool with given arguments.
        
        Args:
            function_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            String result from tool execution
        """
        # Check if the requested tool exists in our tools dictionary
        if function_name in self.__tools_dict:
            # Execute the tool and return its result
            tool = self.__tools_dict[function_name]
            return tool.execute(arguments)
        else:
            # Return error message if tool doesn't exist
            return f"Unknown function: {function_name}"