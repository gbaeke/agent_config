from dotenv import load_dotenv
import os
import asyncio
from agents import Agent, RunContextWrapper, Runner, TResponseInputItem, trace, RunHooks
from agent_factory import create_agent_from_config

# loads the .env file (if you have a global environment variable, you can skip this)
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")


# create run hooks class
class MyRunHooks(RunHooks):
    def on_tool_start(self, context, agent, tool):
        print(f"\033[92mTool {tool.name} called from {agent.name}\033[0m")
        return super().on_tool_start(context, agent, tool)


# Create agents from configuration
weather_agent = create_agent_from_config("weather")
news_agent = create_agent_from_config("news")


# We want to use the weather agent as a tool in the conversation agent
# This requires the reference to the agent to be passed in as a tool
agent_array = {
    "weather": {
        "agent": weather_agent,
        "name": "weather",
        "description": "Get weather information based on the user's full question"
    },
    "news": {
        "agent": news_agent,
        "name": "news",
        "description": "Get news information based on the user's full question"
    }
}



# Create conversation agent that uses the weather agent as a tool
# The second argument will add the agents as tools on top of the tools of the 
# onversation agent itself
conversation_agent = create_agent_from_config("conversation", agent_array)


async def chat():
    with trace("conversation"):
        convo: list[TResponseInputItem] = []
        print("You are now chatting with the conversation agent. Type 'exit' to end the conversation.")
        
        while True:
            user_input = input("You: ")

            if user_input == "exit":
                print("Goodbye!")
                break

            convo.append({"content": user_input, "role": "user"})
            result = await Runner.run(conversation_agent, convo)

            # Extract and display all responses in order
            print("Agent: ", result.final_output)

            convo = result.to_input_list()


# Run the chat interface
asyncio.run(chat())


