from configs.agents import *
from swarm.repl import run_demo_loop

context_variables = {
    "user_context": """Here is what you know about the user:
""",
    "notebook_context": """""",
}
if __name__ == "__main__":
    run_demo_loop(general_agent, context_variables=context_variables, debug=True)