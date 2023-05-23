import time
import os
import json
from langchain.utilities import BashProcess
from langchain import Wikipedia
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.llms import LlamaCpp
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, ConversationTokenBufferMemory, ConversationSummaryBufferMemory

# Load environment variables
MODEL_PATH = os.getenv("LLAMACPP_MODEL", "models/default/model.bin")
TEMP = float(os.getenv("TEMP", 1.0))
NCTX = int(os.getenv("N_CTX", 1024))
AI_GOAL = os.getenv("AI_GOAL", "default_goal")

# Initialize LlamaCpp model
llm = LlamaCpp(model_path=MODEL_PATH, temperature=TEMP, n_ctx=NCTX)

# Initialize memory
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=4098)  # Summary and Token Limit Memory

# Load tools
tools = load_tools(["google-search", "requests_all", "wikipedia", "human"], llm=llm)

print("Initializing agent...")
react = initialize_agent(tools, llm, memory=memory, n_batch=8, agent="zero-shot-react-description", verbose=True, return_intermediate_steps=True)

print("Goal: "+AI_GOAL)

# Main execution
try:
    startTime = time.time()
    response = react({"input": AI_GOAL})
    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
except Exception as e:
    response = str(e)
    if response.startswith("Could not parse LLM output: `"):
        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        print("Corrected: "+response)
