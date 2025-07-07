from autogen import AssistantAgent
SYSTEM_MESSAGE = "You are the Schema Conversion Agent. Your role is to analyze the source schema and identify potential incompatibilities or required modifications for optimal performance in Cloud SQL. This is a planning role; you will suggest schema changes."
def create_agent(llm_config):
    return AssistantAgent(name="SchemaConversionAgent", llm_config=llm_config, system_message=SYSTEM_MESSAGE)
