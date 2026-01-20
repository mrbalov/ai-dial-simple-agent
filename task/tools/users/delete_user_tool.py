from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):
    """Tool for deleting users from the user service."""

    @property
    def name(self) -> str:
        """Returns the name of the tool."""
        return "delete_users"

    @property
    def description(self) -> str:
        """Returns a description of what this tool does."""
        return "Deletes a user from the system by their ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Returns the JSON schema for the tool's input parameters."""
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The ID of the user to delete"
                }
            },
            "required": ["id"]  # id is required for deletion
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Executes the tool with the given arguments.
        
        Args:
            arguments: Dictionary containing the user ID to delete
            
        Returns:
            Success message or error description
        """
        try:
            # Step 1: Get the user ID from arguments
            user_id = arguments.get("id")
            if user_id is None:
                return "Error: User ID is required for deletion"
            
            # Convert to int (in case it comes as string or float)
            user_id = int(user_id)
            
            # Step 2: Call the user client to delete the user
            result = self._user_client.delete_user(user_id)
            
            # Return the result
            return result
            
        except Exception as e:
            # If any error occurs (validation or API call), return a friendly error message
            return f"Error while deleting user by id: {str(e)}"