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

# --- Define Club Policy Placeholder --- (No longer needed with the new simple instructions)
# club_policy_placeholder = '''
# [
#   {
#     "query_type": "Player Registration",
#     "keywords": ["register", "sign up", "join", "membership"],
#     "resolution_steps": "Ask for registration code. Use 'validate_registration_code' tool. If valid, guide through steps XYZ. If invalid, inform user.",
#     "required_tools": ["validate_registration_code"]
#   },
#   {
#     "query_type": "Training Information",
#     "keywords": ["training", "practice", "schedule"],
#     "resolution_steps": "Provide current training schedule based on age group (tool to be defined: 'get_training_schedule').",
#     "required_tools": ["get_training_schedule"]
#   },
#   {
#     "query_type": "Payment Queries",
#     "keywords": ["payment", "fee", "subs"],
#     "resolution_steps": "Explain payment process and direct to club treasurer for setup/issues (tool to be defined: 'get_treasurer_contact').",
#     "required_tools": ["get_treasurer_contact"]
#   },
#   {
#     "query_type": "General Inquiry",
#     "keywords": [], 
#     "resolution_steps": "Provide a polite general response and offer to find more specific help if needed.",
#     "required_tools": []
#   }
# ]
# '''

# --- Define the Single Triage Agent ---
urmston_town_triage_agent = Agent(
    name="Urmston Town Triage Agent",
    instructions=(
        "You are the front-door triage agent for Urmston Town Juniors Football Club, "
        "a local grassroots football club based in Manchester, England.\n\n"
        "For the moment, please reply to all queries with the message "
        "'I AM URMSTON TOWN\'S CHATBOT AND I HAVE RECEIVED YOUR MESSAGE AND AM READY TO SERVE'."
    ),
    tools=[validate_registration_code] # Tool will not be used with current instructions, but kept for future use
)

print("Urmston Town Triage Agent defined.")


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
        
        agent_to_run = urmston_town_triage_agent # Always use the single agent
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