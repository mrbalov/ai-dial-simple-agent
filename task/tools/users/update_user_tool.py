from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):
    """Tool for updating existing users in the user service."""

    @property
    def name(self) -> str:
        """Returns the name of the tool."""
        return "update_user"

    @property
    def description(self) -> str:
        """Returns a description of what this tool does."""
        return "Updates an existing user's information by their ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Returns the JSON schema for the tool's input parameters."""
        # Get the schema for UserUpdate model
        user_update_schema = UserUpdate.model_json_schema()
        
        # Create the complete schema with both id and new_info
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID that should be updated"
                },
                "new_info": {
                    "type": "object",
                    "description": "New information to update for the user",
                    "properties": user_update_schema["properties"],
                    # UserUpdate has all optional fields, so no required fields
                    "required": user_update_schema.get("required", [])
                }
            },
            "required": ["id", "new_info"]  # Both id and new_info are required
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Executes the tool with the given arguments.
        
        Args:
            arguments: Dictionary containing user ID and new information
            
        Returns:
            Success message or error description
        """
        try:
            # Step 1: Get the user ID from arguments
            user_id = arguments.get("id")
            if user_id is None:
                return "Error: User ID is required"
            
            # Convert to int if needed
            user_id = int(user_id)
            
            # Step 2: Get new_info and create UserUpdate model
            new_info = arguments.get("new_info", {})
            user_update_model = UserUpdate.model_validate(new_info)
            
            # Step 3: Call the user client to update the user
            result = self._user_client.update_user(user_id, user_update_model)
            
            # Return the result
            return result
            
        except Exception as e:
            # If any error occurs (validation or API call), return a friendly error message
            return f"Error while updating user: {str(e)}"