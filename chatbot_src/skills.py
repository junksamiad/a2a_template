from a2a import agent
from agents import Runner # Import the SDK Runner
from .go import orchestrator_agent # Import the agent instance from go.py
import asyncio

@agent("check_team_spaces")
async def check_team_spaces(team_name: str) -> dict:
    """Check if a team has player vacancies using the orchestrator agent.

    Args:
        team_name: The name of the team to check.

    Returns:
        A dictionary with team availability information or an error message.
    """
    # Construct the input for the orchestrator_agent
    # For this specific skill, the orchestrator_agent will get the direct query
    # as if the user asked it about team availability.
    agent_input = f"Do you have spaces on the {team_name} team?"

    try:
        # Run the orchestrator_agent
        # Note: The orchestrator_agent itself manages conversation history if run repeatedly in its own loop.
        # For a single A2A skill invocation that maps to a single query/response from the orchestrator,
        # we pass the direct input. If the A2A skill needed to manage a longer conversation with the
        # orchestrator_agent, this part would be more complex.
        result = await Runner.run(orchestrator_agent, agent_input)
        
        final_output = result.final_output
        
        # The orchestrator_agent's sdk_get_team_availability tool returns a dict.
        # If the agent successfully uses the tool and its instruction is to provide full details,
        # the final_output might already be structured or be a string representation of that dict.
        # For A2A, we want to return a structured JSON response (dict).

        if isinstance(final_output, dict):
            return final_output
        elif isinstance(final_output, str):
            # Attempt to see if the string is the direct output of our tool (which is a dict)
            # This is a bit of a heuristic; ideally the agent is instructed to output JSON for this skill.
            # For now, we assume if the orchestrator used the tool, its natural language response
            # might contain the core info we want to pass back structured.
            # Let's assume for this step, the orchestrator_agent's direct string output based on the tool is sufficient for the A2A response.
            # A more robust solution would have the orchestrator_agent itself return a specific Pydantic model.
            
            # We expect the orchestrator agent to have used the tool, and its output will be based on the tool's dict.
            # The tool now returns a dict directly. If the agent uses the tool, its output might be stringified.
            # We'll try to see if the string describes the dict. For now, we'll just return it as a string in a dict.
            # This part needs refinement based on actual agent output. 
            # The ideal scenario: orchestrator_agent is instructed to return JSON for this type of query.
            return {"response_text": final_output} # Placeholder - ideally, this skill ensures structured output
        else:
            return {"error": "Unexpected response type from orchestrator agent", "details": str(final_output)}

    except Exception as e:
        print(f"Error running orchestrator_agent from A2A skill: {e}")
        return {"error": "Failed to process request via orchestrator agent", "details": str(e)} 