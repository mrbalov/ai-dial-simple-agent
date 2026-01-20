from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):
    """
    Tool for searching users based on various criteria.
    
    This tool allows the AI agent to search for users in the system
    using different filters like name, surname, email, or gender.
    All search parameters are optional, allowing flexible searches.
    """

    @property
    def name(self) -> str:
        """
        Returns the name of the tool.
        
        This is the identifier that the AI model will use to call this tool.
        """
        return "search_users"

    @property
    def description(self) -> str:
        """
        Returns a description of what this tool does.
        
        This helps the AI model understand when to use this tool for searching users.
        """
        return "Searches for users based on optional criteria like name, surname, email, or gender"

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        Returns the JSON schema for the tool's input parameters.
        
        All parameters are optional, allowing for flexible search queries:
        - No parameters: returns all users
        - One parameter: filters by that field
        - Multiple parameters: filters by all provided fields (AND operation)
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Filter users by first name (optional)"
                },
                "surname": {
                    "type": "string",
                    "description": "Filter users by last name (optional)"
                },
                "email": {
                    "type": "string",
                    "description": "Filter users by email address (optional)"
                },
                "gender": {
                    "type": "string",
                    "description": "Filter users by gender (optional)"
                }
            },
            # Empty required array means all parameters are optional
            # This allows searching with any combination of filters
            "required": []
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Executes the tool with the given arguments.
        
        This method performs the user search based on the provided criteria.
        If no criteria are provided, it returns all users.
        
        Args:
            arguments: Dictionary containing optional search criteria
                      Examples:
                      - {} (empty dict returns all users)
                      - {"name": "John"} (search by name only)
                      - {"name": "John", "surname": "Doe"} (search by multiple fields)
            
        Returns:
            List of matching users as a formatted string if successful,
            or an error message if something goes wrong
        """
        try:
            # The beauty of Python's **kwargs!
            # **arguments unpacks the dictionary as keyword arguments
            # This means {"name": "John", "email": "john@example.com"}
            # becomes search_users(name="John", email="john@example.com")
            
            # The user_client.search_users method is designed to handle:
            # - None values (ignored in the search)
            # - Empty dictionary (returns all users)
            # - Any combination of the supported parameters
            result = self._user_client.search_users(**arguments)
            
            # Return the formatted result
            # The user_client formats multiple users nicely for display
            return result
            
        except TypeError as e:
            # Handle cases where invalid parameters are provided
            return f"Error: Invalid search parameters - {str(e)}"
        except Exception as e:
            # Handle any other errors (network issues, service down, etc.)
            return f"Error while searching users: {str(e)}"