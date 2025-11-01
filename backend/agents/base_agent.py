# backend/agents/base_agent.py

from typing import List, Any
from backend.util.config import load_config

from langchain_groq.chat_models import ChatGroq
from langchain_core.tools import BaseTool
from langchain.agents import create_agent


class BaseAgent:
    """
    A generic base agent class that uses ChatGroq with native tool calling support.
    """

    def __init__(
        self,
        tools: List[BaseTool],
        model_name: str = "openai/gpt-oss-120b",
        temperature: float = 0.0,
        verbose: bool = False,
        **llm_kwargs: Any,
    ):
        # Load API key from config
        cfg = load_config()
        api_key = cfg.get("GROK_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required in config but not present")

        # Instantiate ChatGroq model with tool binding
        self.llm = ChatGroq(
            model=model_name, temperature=temperature, api_key=api_key, **llm_kwargs
        )

        self.tools = tools
        self.verbose = verbose

        # Bind tools to the LLM - this enables native tool calling
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Create agent using LangGraph's prebuilt react agent
        self.agent_executor = create_agent(model=self.llm, tools=self.tools)

    def run(self, user_input: str) -> Any:
        """
        Execute the agent with a single user prompt.
        """
        try:
            # Invoke the agent with the user input
            result = self.agent_executor.invoke({"messages": [("user", user_input)]})

            # Extract the final response from messages
            if self.verbose:
                print(f"Full result: {result}")

            # Get the last message content
            final_message = result["messages"][-1]
            return final_message.content
        except Exception as exc:
            raise RuntimeError(f"Agent execution failed: {exc}") from exc


# example usage

# tool_list: List[BaseTool] = [echo_tool, calculate]
# agent = BaseAgent(tools=tool_list, verbose=True)
# print("Agent ready! Try asking math questions like:")
# print("  - 'What is 15 * 7?'")
# print("  - 'Calculate (100 - 25) * 2'")
# print("  - 'What's 2 to the power of 8?'")
# print()
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ("quit", "exit"):
#         print("Bye!")
#         break
#     output = agent.run(user_input)
#     print("Agent:", output)
#     print()
