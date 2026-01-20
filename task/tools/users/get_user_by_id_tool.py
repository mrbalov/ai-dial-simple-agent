from typing import Any

from task.tools.users.base import BaseUserServiceTool


class GetUserByIdTool(BaseUserServiceTool):
    """
    Tool for retrieving user information by their ID.
    
    This tool allows the AI agent to fetch detailed information about a specific user
    when given their unique identifier (ID).
    """

    @property
    def name(self) -> str:
        """
        Returns the name of the tool.
        
        This name is what the AI model will use to call this tool.
        It should be descriptive and match what's expected in the API.
        """
        return "get_user_by_id"

    @property
    def description(self) -> str:
        """
        Returns a description of what this tool does.
        
        This description helps the AI model understand when to use this tool.
        It should be clear and concise about the tool's purpose.
        """
        return "Retrieves detailed information about a user by their ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        Returns the JSON schema for the tool's input parameters.
        
        This schema tells the AI model what parameters this tool expects.
        In this case, we only need the user's ID.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The unique identifier (ID) of the user to retrieve"
                }
            },
            "required": ["id"]  # The ID is mandatory - we can't get a user without it
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Executes the tool with the given arguments.
        
        This is the main method that performs the actual work of the tool.
        It takes the arguments provided by the AI model and uses them to
        fetch user information from the user service.
        
        Args:
            arguments: Dictionary containing the user ID to retrieve
                      Example: {"id": 123}
            
        Returns:
            User information as a formatted string if successful,
            or an error message if something goes wrong
        """
        try:
            # Step 1: Extract the user ID from the arguments
            # The AI model passes arguments as a dictionary
            user_id = arguments.get("id")
            
            # Step 2: Validate that we received an ID
            if user_id is None:
                return "Error: User ID is required but was not provided"
            
            # Step 3: Convert the ID to an integer
            # The ID might come as a string or float from the AI model,
            # but our API expects an integer
            user_id = int(user_id)
            
            # Step 4: Use the user client to fetch the user from the service
            # The user_client handles the actual HTTP request to the user service
            result = self._user_client.get_user(user_id)
            
            # Step 5: Return the result
            # The user_client already formats the response nicely for us
            return result
            
        except ValueError as e:
            # Handle cases where the ID can't be converted to an integer
            return f"Error: Invalid user ID format - {str(e)}"
        except Exception as e:
            # Handle any other errors (network issues, service down, etc.)
            return f"Error while retrieving user by ID: {str(e)}"