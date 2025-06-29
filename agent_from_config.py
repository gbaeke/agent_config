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
simulator_agent = create_agent_from_config("simulator")

# We want to use the weather agent as a tool in the conversation agent
# This requires the reference to the agent to be passed in as a tool
agent_as_tools = {
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

agent_handoffs = [
    simulator_agent
]




# Create conversation agent that uses the weather agent as a tool
# The second argument will add the agents as tools on top of the tools of the 
# onversation agent itself
conversation_agent = create_agent_from_config("conversation", agent_as_tools, agent_handoffs)


async def chat():
    with trace("conversation"):
        current_agent = conversation_agent
        convo: list[TResponseInputItem] = []
        print(f"You are now chatting with the {current_agent.name}. Type 'exit' to end the conversation.")
        
        while True:
            user_input = input("You: ")

            if user_input == "exit":
                if current_agent != conversation_agent:
                    print(f"Going from {current_agent.name} to {conversation_agent.name}")
                    current_agent = conversation_agent
                else:
                    print("Goodbye!")
                    break

            # allow reset which clears the convo
            if user_input == "reset":
                convo = []
                print("\033[91mConversation reset\033[0m")
                current_agent = conversation_agent
                continue

            convo.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, convo)

            # Extract and display all responses in order
            print("Agent: ", result.final_output)

            convo = result.to_input_list()
            current_agent = result.last_agent


# Run the chat interface
asyncio.run(chat())


