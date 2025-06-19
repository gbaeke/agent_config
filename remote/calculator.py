from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, function_tool, Runner
from typing import Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(title="OpenAI Agent API", description="FastAPI with OpenAI Agent SDK and square root calculator")

class QueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    result: str

# Create the square root calculator tool using the OpenAI Agent SDK
@function_tool
def calculate_square_root(number: float) -> str:
    """Calculate the square root of a positive number.
    
    Args:
        number: The number to calculate the square root of (must be non-negative)
        
    Returns:
        str: The result of the square root calculation
    """
    if number < 0:
        return f"Error: Cannot calculate square root of negative number {number}"
    
    try:
        result = math.sqrt(number)
        return f"The square root of {number} is {result}"
    except Exception as e:
        return f"Error calculating square root: {str(e)}"

# Create the agent with the square root calculator tool
agent = Agent(
    name="Square Root Calculator Agent",
    instructions="""You are a helpful assistant that specializes in calculating square roots. 
    You have access to a calculate_square_root tool that can compute the square root of any non-negative number.
    When a user asks for a square root calculation, use the tool to provide the answer.
    If they ask about something else, politely explain that you specialize in square root calculations.""",
    model="gpt-4o-mini",
    tools=[calculate_square_root]
)

@app.get("/")
async def root():
    """Root endpoint with basic information about the agent."""
    return {
        "message": "OpenAI Agent API with Square Root Calculator",
        "agent_name": agent.name,
        "model": agent.model,
        "tools": ["calculate_square_root"],
        "usage": "Send a POST request to /run with a query about square roots"
    }

@app.post("/run", response_model=AgentResponse)
async def run_agent(request: QueryRequest):
    """
    Run the OpenAI agent with a given query.
    
    The agent specializes in calculating square roots using the OpenAI Agent SDK.
    Example queries:
    - "What is the square root of 25?"
    - "Calculate sqrt of 16"
    - "Find the square root of 2.5"
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if OpenAI API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY is not set in environment variables"
            )
        
        # Create the conversation with the user's query
        messages = [{"content": request.query, "role": "user"}]
        
        # Run the agent
        result = await Runner.run(agent, messages)
        
        return AgentResponse(result=result.final_output)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "agent": agent.name,
        "openai_api_key_set": bool(os.environ.get("OPENAI_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 