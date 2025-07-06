from autogen import AssistantAgent
SYSTEM_MESSAGE = "You are the Data Validation Agent. After a migration is complete, your job is to ensure data integrity. Formulate a high-level plan to validate the data, such as performing row counts on critical tables. You do not need to execute the plan, just provide it."
def create_agent(llm_config):
    return AssistantAgent(name="DataValidationAgent", llm_config=llm_config, system_message=SYSTEM_MESSAGE)
