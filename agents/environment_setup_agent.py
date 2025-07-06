from autogen import AssistantAgent
SYSTEM_MESSAGE = "You are the Environment Setup Agent. Your sole responsibility is to provision the cloud infrastructure. You MUST use the `run_terraform_apply` tool. After the tool runs successfully, the infrastructure details will be captured automatically. Report your success and await further instructions."
def create_agent(llm_config):
    return AssistantAgent(name="EnvironmentSetupAgent", llm_config=llm_config, system_message=SYSTEM_MESSAGE)
