from autogen import AssistantAgent
SYSTEM_MESSAGE = "You are the Performance Optimization Agent. After migration, analyze the new Cloud SQL environment based on the information provided. Provide high-level recommendations on instance sizing, read replicas, and query optimizations."
def create_agent(llm_config):
    return AssistantAgent(name="PerformanceOptimizationAgent", llm_config=llm_config, system_message=SYSTEM_MESSAGE)
