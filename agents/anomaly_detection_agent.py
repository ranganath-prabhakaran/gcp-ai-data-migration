from autogen import AssistantAgent
SYSTEM_MESSAGE = "You are the Anomaly Detection Agent. You monitor the migration process for unusual patterns, such as significant performance issues or error spikes in logs. You report any anomalies to the group. Your role is observational."
def create_agent(llm_config):
    return AssistantAgent(name="AnomalyDetectionAgent", llm_config=llm_config, system_message=SYSTEM_MESSAGE)
