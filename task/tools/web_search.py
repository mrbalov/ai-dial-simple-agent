from typing import Any

import requests

from task.tools.base import BaseTool


class WebSearchTool(BaseTool):
    """
    A tool that allows the AI to search the web for information.
    Uses another AI model with Google search capabilities to find information.
    """

    def __init__(self, api_key: str, endpoint: str):
        """
        Initialize the web search tool.
        
        Args:
            api_key: API key for authentication
            endpoint: Base endpoint for the DIAL API
        """
        self.__api_key = api_key
        # We'll use a specific model that has web search capabilities
        self.__endpoint = f"{endpoint}/openai/deployments/gemini-2.5-pro/chat/completions"

    @property
    def name(self) -> str:
        """
        The unique name identifier for this tool.
        This is what the AI will use to call this tool.
        """
        return "web_search_tool"

    @property
    def description(self) -> str:
        """
        Description that helps the AI understand when to use this tool.
        """
        return "Tool for searching the web to find current information, facts, or details about people, events, or topics"

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema that defines what parameters this tool accepts.
        This tells the AI what information it needs to provide when calling this tool.
        """
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web"
                }
            },
            "required": ["request"]  # The 'request' parameter is mandatory
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Execute the web search with the provided query.
        
        Args:
            arguments: Dictionary containing the 'request' key with search query
            
        Returns:
            Search results as a string
        """
        try:
            # 1. Create headers for API authentication
            headers = {
                "api-key": self.__api_key,
                "Content-Type": "application/json"
            }
            
            # 2. Prepare the request data
            # We're asking another AI model to search the web for us
            request_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": str(arguments["request"])  # The search query
                    }
                ],
                "tools": [
                    {
                        "type": "static_function",
                        "static_function": {
                            "name": "google_search",
                            "description": "Grounding with Google Search",
                            "configuration": {}
                        }
                    }
                ]
            }
            
            # 3. Make the POST request to the API
            response = requests.post(
                url=self.__endpoint,
                headers=headers,
                json=request_data
            )
            
            # 4. Check if the request was successful and return results
            if response.status_code == 200:
                # Parse the response and extract the message content
                response_json = response.json()
                choices = response_json.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    content = message.get("content", "No results found")
                    return content
                return "No search results found"
            else:
                # Return error message if request failed
                return f"Error: {response.status_code} {response.text}"
                
        except Exception as e:
            # Handle any unexpected errors
            return f"Error during web search: {str(e)}"