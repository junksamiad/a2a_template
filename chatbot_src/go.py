#!/usr/bin/env python
import os
# import re # No longer needed for query_classification_list
import asyncio
from dotenv import load_dotenv
# from pydantic import BaseModel, Field # Keep BaseModel if needed elsewhere, remove if not. Field likely not needed.
# from typing import Literal, Optional # Keep these if needed elsewhere

# --- Agent SDK Imports ---
from agents import Agent, Runner # Removed InputGuardrail, GuardrailFunctionOutput, RunContextWrapper, function_tool unless a tool is directly defined here.
                                # function_tool will be needed if we define tools in this file, but validate_registration_code is imported.

# --- Import Standardized Prompt Prefix ---
# from .prompt_prefix import format_prompt_with_prefix # Assuming this is not used by the new single agent's direct instructions. Can be re-added if needed.

# --- Import Registration Components (Updated) ---
# from .registration import registration_agent, RegistrationSummary, renew_registration_agent, new_registration_agent, code_verification_agent # Removed all these

# --- Import Tools ---
from .tools import validate_registration_code # Keep this for the new agent
from agents import function_tool # Import for the new internal tool

# --- Load Environment Variables ---
load_dotenv()

# OpenAI Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: FATAL: OPENAI_API_KEY not found.")
    exit(1)
else:
    print("OpenAI API Key loaded successfully.")

# Airtable Keys (Added checks for clarity) - Keep these if tools.py needs them
airtable_api_key = os.getenv("AIRTABLE_API_KEY")
airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
if not airtable_api_key:
    print("Warning: AIRTABLE_API_KEY not found in .env. Code verification tool will fail.") # This warning comes from tools.py now
if not airtable_base_id:
    print("Warning: AIRTABLE_BASE_ID not found in .env. Code verification tool will fail.") # This warning comes from tools.py now

# --- Fake DB for Team Availability (Placeholder) ---
_FAKE_TEAM_DB = {
    "U8 Lions": {"capacity": 12, "registered": 12, "gender": "Mixed", "age_group": "U8"},
    "U10 Tigers": {"capacity": 14, "registered": 12, "gender": "Mixed", "age_group": "U10"},
    "U12 Eagles": {"capacity": 16, "registered": 16, "gender": "Boys", "age_group": "U12"},
    "U14 Phoenix": {"capacity": 18, "registered": 15, "gender": "Girls", "age_group": "U14"}
}

# --- Internal SDK Tool for Team Availability ---
@function_tool
async def sdk_get_team_availability(team_name: str) -> dict:
    """Checks if a specific football team has player vacancies.

    Args:
        team_name: The full name of the team to check (e.g., 'U10 Tigers').

    Returns:
        A dictionary containing team availability details or an error if not found.
    """
    team_info = _FAKE_TEAM_DB.get(team_name)
    if team_info:
        spaces_left = team_info["capacity"] - team_info["registered"]
        return {
            "team_found": True,
            "team_name": team_name,
            "age_group": team_info["age_group"],
            "gender": team_info["gender"],
            "capacity": team_info["capacity"],
            "registered": team_info["registered"],
            "spaces_available": spaces_left > 0,
            "spaces_left": spaces_left
        }
    else:
        return {
            "team_found": False,
            "team_name": team_name,
            "message": f"Team '{team_name}' not found in our records."
        }

# --- Define the Orchestrator Agent ---
orchestrator_agent = Agent( # RENAMED
    name="Urmston Town Orchestrator Agent", # RENAMED
    instructions=(
        "You are the orchestrator agent for Urmston Town Juniors Football Club, "
        "a local grassroots football club based in Manchester, England.\n\n"
        "Your primary role is to understand user queries and use your available tools to answer them accurately. "
        "When asked to check team availability, use the 'sdk_get_team_availability' tool. "
        "Provide the full details from the tool back to the user in a clear, friendly way.\n\n"
        "For any other queries for the moment, please reply with the message: "
        "'I AM URMSTON TOWN\'S CHATBOT AND I HAVE RECEIVED YOUR MESSAGE AND AM READY TO SERVE'."
    ),
    tools=[validate_registration_code, sdk_get_team_availability] # ADDED sdk_get_team_availability
)

print("Urmston Town Orchestrator Agent defined.") # UPDATED print message


# --- Main Execution Logic (Simplified for Single Agent) ---
async def main():
    print("\\nPlease enter your query:")
    
    conversation_history = []

    while True:
        user_message_content = input("You: ")
        if user_message_content.lower() in ["quit", "exit"]:
            print("Ending conversation.")
            break

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message_content})
        
        agent_to_run = orchestrator_agent # Always use the single agent (RENAMED)
        agent_input = conversation_history
        
        print(f"Agent ({agent_to_run.name}) thinking...")
        try:
            current_run_result = await Runner.run(agent_to_run, agent_input)

            # Display the agent's response 
            print("\\n--- Agent Response ---")
            agent_emoji = "⚽" # Simplified emoji
            
            responding_agent_name = agent_to_run.name # Always the same agent
            
            if current_run_result.final_output:
                # Check if the output is our structured summary (RegistrationSummary is removed, so this check might need to change if new structured outputs are used)
                # For now, just print the string output
                print(f"{agent_emoji} {responding_agent_name}: {current_run_result.final_output}")
                # Add assistant's response to history
                conversation_history.append({"role": "assistant", "content": str(current_run_result.final_output)})
            else:
                print(f"{agent_emoji} {responding_agent_name}: (No response generated for this turn)")
                # Potentially add a placeholder to history or handle differently
                conversation_history.append({"role": "assistant", "content": "[No explicit response generated]"})


            # Prune history if it gets too long (optional)
            # MAX_HISTORY_LENGTH = 10 
            # if len(conversation_history) > MAX_HISTORY_LENGTH:
            #     conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

        except Exception as e:
            error_message = str(e)
            # Simplified error handling for now
            print(f"\\nAn error occurred during execution: {e}")
            # conversation_history.append({"role": "assistant", "content": f"[Error: {e}]"}) # Optionally log error to history
            # Potentially reset or truncate history on error
            # conversation_history = [] 


# --- Boilerplate ---
if __name__ == "__main__":
    asyncio.run(main()) 