from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate, Address, CreditCard


class CreateUserTool(BaseUserServiceTool):
    """
    Tool for creating new users in the user service.
    
    This tool allows the AI agent to create new user accounts in the system
    with all the necessary information like name, email, and other details.
    """

    @property
    def name(self) -> str:
        """
        Returns the name of the tool.
        
        This is the identifier that the AI model will use to call this tool.
        """
        return "add_user"

    @property
    def description(self) -> str:
        """
        Returns a description of what this tool does.
        
        This helps the AI model understand when to use this tool for creating users.
        """
        return "Creates a new user in the system with the provided information"

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        Returns the JSON schema for the tool's input parameters.
        
        This schema is automatically generated from the Pydantic UserCreate model,
        which ensures type safety and validation of all user fields.
        
        Required fields: name, surname, email, about_me
        Optional fields: phone, date_of_birth, address, gender, company, salary, credit_card
        """
        # Pydantic models can generate JSON schemas automatically!
        # This is super helpful as it keeps our schema in sync with the model
        schema = UserCreate.model_json_schema()
        
        # Wrap the Pydantic schema in the format expected by the tool interface
        return {
            "type": "object",
            "properties": schema["properties"],
            "required": schema.get("required", [])
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Executes the tool with the given arguments.
        
        This method creates a new user in the system with the provided information.
        It validates all input data before sending it to the user service.
        
        Args:
            arguments: Dictionary containing user information
                      Example:
                      {
                          "name": "John",
                          "surname": "Doe",
                          "email": "john.doe@example.com",
                          "about_me": "Software developer with 5 years experience",
                          "phone": "+1234567890",  # optional
                          "gender": "male",  # optional
                          "company": "Tech Corp",  # optional
                          "salary": 75000.0,  # optional
                          "date_of_birth": "1990-01-15",  # optional
                          "address": {  # optional nested object
                              "country": "USA",
                              "city": "New York",
                              "street": "123 Main St",
                              "flat_house": "Apt 4B"
                          },
                          "credit_card": {  # optional nested object
                              "num": "1234-5678-9012-3456",
                              "cvv": "123",
                              "exp_date": "12/25"
                          }
                      }
            
        Returns:
            Success message with user ID if created successfully,
            or an error message if validation fails or service is unavailable
        """
        try:
            # Step 1: Validate the input data using Pydantic
            # Pydantic will:
            # - Check that all required fields are present
            # - Validate data types (e.g., email format, numeric values)
            # - Handle nested objects (Address, CreditCard)
            # - Apply any custom validators defined in the model
            user_create_model = UserCreate.model_validate(arguments)
            
            # Step 2: Send the validated data to the user service
            # The user_client handles the HTTP POST request
            # model_dump() converts the Pydantic model back to a dictionary
            result = self._user_client.add_user(user_create_model)
            
            # Step 3: Return the success message
            # Typically includes the new user's ID for reference
            return result
            
        except ValueError as e:
            # Handle Pydantic validation errors
            # These occur when required fields are missing or data types are wrong
            return f"Error: Invalid user data - {str(e)}"
        except Exception as e:
            # Handle any other errors (network issues, service down, etc.)
            return f"Error while creating a new user: {str(e)}"