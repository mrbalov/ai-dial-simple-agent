import os

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    """
    Main function that runs the AI agent with user management capabilities.
    
    This function:
    1. Initializes all necessary clients and tools
    2. Creates a conversation with a system prompt
    3. Runs an interactive loop where users can chat with the AI agent
    """
    
    # 1. Create UserClient
    # This client handles all communication with the user service
    user_client = UserClient()
    print("✅ UserClient initialized")
    
    # 2. Create DialClient with all tools
    # First, initialize all the tools that the AI agent can use
    
    # Web search tool for finding information online
    web_search_tool = WebSearchTool(
        api_key=API_KEY,
        endpoint=DIAL_ENDPOINT
    )
    
    # User management tools - each tool needs the user_client to work
    get_user_tool = GetUserByIdTool(user_client)
    search_users_tool = SearchUsersTool(user_client)
    create_user_tool = CreateUserTool(user_client)
    update_user_tool = UpdateUserTool(user_client)
    delete_user_tool = DeleteUserTool(user_client)
    
    # Create the DIAL client with all available tools
    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4o",  # Using GPT-4o model
        api_key=API_KEY,
        tools=[
            web_search_tool,
            get_user_tool,
            search_users_tool,
            create_user_tool,
            update_user_tool,
            delete_user_tool
        ]
    )
    print("✅ DialClient initialized with all tools")
    
    # 3. Create Conversation and add the system message
    # The conversation keeps track of all messages between the user and AI
    conversation = Conversation()
    
    # Add the system prompt as the first message
    # This tells the AI what role it should play
    system_message = Message(
        role=Role.SYSTEM,
        content=SYSTEM_PROMPT
    )
    conversation.add_message(system_message)
    print("✅ Conversation initialized with system prompt")
    
    # Print welcome message
    print("\n" + "="*60)
    print("🤖 AI User Management Assistant Ready!")
    print("="*60)
    print("Type your message and press Enter. Type 'exit' or 'quit' to stop.")
    print("Example: 'Add Andrej Karpathy as a new user'")
    print("="*60 + "\n")
    
    # 4. Run infinite loop for user interaction
    while True:
        try:
            # Get user input from terminal
            user_input = input("> ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'stop']:
                print("\n👋 Goodbye! Thank you for using the AI User Management Assistant.")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Add User message to Conversation
            user_message = Message(
                role=Role.USER,
                content=user_input
            )
            conversation.add_message(user_message)
            
            # Call DialClient with conversation history
            # The client will handle tool calls if needed and return the final response
            print("\n🤔 Thinking...")
            ai_response = dial_client.get_completion(
                messages=conversation.get_messages(),
                print_request=False  # Set to True for debugging
            )
            
            # Add Assistant message to Conversation
            conversation.add_message(ai_response)
            
            # Print the AI's response
            print("\n🤖 Assistant:")
            print(ai_response.content)
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            # Handle any errors that occur
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    # Check if API key is set
    if not API_KEY:
        print("❌ Error: DIAL_API_KEY environment variable is not set!")
        print("Please set your API key using:")
        print("  export DIAL_API_KEY='your-api-key-here'")
        exit(1)
    
    # Run the main function
    main()

#TODO:
# Request sample:
# Add Andrej Karpathy as a new user