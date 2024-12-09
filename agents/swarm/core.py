# Standard library imports
import copy
import json
from datetime import datetime, timezone
from collections import defaultdict
from typing import List

# Package/library imports
from openai import OpenAI
import asyncio

# Local imports
from .util import function_to_json, debug_print, merge_chunk
from models.session_context import SessionContext
from .types import (
    Agent,
    AgentFunction,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
    Function,
    Response,
    Result,
)

__SESSION_CONTEXT_NAME__ = "session_context"

class Swarm:
    def __init__(self, client=None):
        if not client:
            client = OpenAI()
        self.client = client

    def get_chat_completion(
        self,
        agent: Agent,
        history: List,
        session_context: SessionContext,
        model_override: str,
        stream: bool,
        debug: bool,
    ) -> ChatCompletionMessage:
        instructions = (
            agent.instructions(session_context.variables)
            if callable(agent.instructions)
            else agent.instructions
        )
        messages = [{"role": "system", "content": instructions}] + history
        debug_print(debug, "Getting chat completion for...:", messages)

        tools = [function_to_json(f) for f in agent.functions]
        # Simplify - only need to handle session_context
        for tool in tools:
            params = tool["function"]["parameters"]
            params["properties"].pop(__SESSION_CONTEXT_NAME__, None)
            if __SESSION_CONTEXT_NAME__ in params["required"]:
                params["required"].remove(__SESSION_CONTEXT_NAME__)

        create_params = {
            "model": model_override or agent.model,
            "messages": messages,
            "tools": tools or None,
            "tool_choice": agent.tool_choice,
            "stream": stream,
        }

        if tools:
            create_params["parallel_tool_calls"] = agent.parallel_tool_calls

        return self.client.chat.completions.create(**create_params)

    def handle_function_result(self, result, debug) -> Result:
        match result:
            case Result() as result:
                return result

            case Agent() as agent:
                return Result(
                    value=json.dumps({"assistant": agent.name}),
                    agent=agent,
                )
            case dict() | list():
                return Result(value=result)
            case _:
                try:
                    return Result(value=str(result))
                except Exception as e:
                    error_message = f"Failed to cast response to string: {result}. Make sure agent functions return a string or Result object. Error: {str(e)}"
                    debug_print(debug, error_message)
                    raise TypeError(error_message)
                
    def summarize_tool_output(self, full_output):
        """
        Summarizes tool output for the agent's next step.
        Handles structured data (dict, list) and strings appropriately.
        """
        if isinstance(full_output, (dict, list)):
            summary = {
                "summary": "Processed structured tool output",
                "type": type(full_output).__name__,
                "preview": str(full_output)[:100],  # Include a preview of the data
            }
        elif isinstance(full_output, str):
            try:
                # Attempt to parse if it's a JSON-encoded string
                output_data = json.loads(full_output)
                summary = {
                    "summary": "Processed JSON string",
                    "type": "json",
                    "preview": str(output_data)[:100],
                }
            except json.JSONDecodeError:
                # Handle plain strings
                summary = {
                    "summary": "Processed plain string",
                    "type": "string",
                    "preview": full_output[:100],
                }
        else:
            raise TypeError(f"Unsupported type for tool output: {type(full_output)}")

        # Ensure the output is JSON-serializable for messages
        return json.dumps(summary)
    
    async def handle_tool_calls(
        self,
        tool_calls: List[ChatCompletionMessageToolCall],
        functions: List[AgentFunction],
        session_context: SessionContext,
        debug: bool,
    ) -> Response:
        function_map = {f.__name__: f for f in functions}
        partial_response = Response(messages=[], agent=None)

        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Handle missing tool case
            if name not in function_map:
                print(debug, f"Tool {name} not found in function map.")
                partial_response.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "tool_name": name,
                        "content": f"Error: Tool {name} not found.",
                    }
                )
                continue
            
            print(debug, f"Processing tool call: {name} with arguments {args}")

            func = function_map[name]
            # Simplify - only inject session_context
            if __SESSION_CONTEXT_NAME__ in func.__code__.co_varnames:
                args[__SESSION_CONTEXT_NAME__] = session_context

            if asyncio.iscoroutinefunction(func):
                raw_result = await func(**args)
            else:
                raw_result = func(**args)

            result = self.handle_function_result(raw_result, debug)
            
            # Clean up - only need to handle session_context
            if __SESSION_CONTEXT_NAME__ in args:
                del args[__SESSION_CONTEXT_NAME__]

            session_context.add_step({
              "step_id": tool_call.id,
              "tool": name,
              "input": args,
              "output": result,
              "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            
            
            summary = self.summarize_tool_output(result.value)
            
            partial_response.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "tool_name": name,
                    "content": summary,
                }
            )
            
            if result.agent:
                partial_response.agent = result.agent

        return partial_response
            
    async def run_and_stream(
        self,
        agent: Agent,
        messages: List,
        session_context: SessionContext,
        model_override: str = None,
        debug: bool = False,
        max_turns: int = float("inf"),
        execute_tools: bool = True,
    ):
        active_agent = agent
        history = copy.deepcopy(messages)
        init_len = len(messages)

        while len(history) - init_len < max_turns:

            message = {
                "content": "",
                "sender": agent.name,
                "role": "assistant",
                "function_call": None,
                "tool_calls": defaultdict(
                    lambda: {
                        "function": {"arguments": "", "name": ""},
                        "id": "",
                        "type": "",
                    }
                ),
            }
            # get completion with current history, agent
            completion = self.get_chat_completion(
                agent=active_agent,
                history=history,
                session_context=session_context,
                model_override=model_override,
                stream=True,
                debug=debug,
            )

            yield {"delim": "start"}
            for chunk in completion:
                delta = json.loads(chunk.choices[0].delta.json())
                if delta["role"] == "assistant":
                    delta["sender"] = active_agent.name
                yield delta
                delta.pop("role", None)
                delta.pop("sender", None)
                merge_chunk(message, delta)
            yield {"delim": "end"}

            message["tool_calls"] = list(
                message.get("tool_calls", {}).values())
            if not message["tool_calls"]:
                message["tool_calls"] = None
            print(debug, "Received completion:", message)
            history.append(message)

            if not message["tool_calls"] or not execute_tools:
                print(debug, "Ending turn.")
                break

            tool_calls = []
            for tool_call in message["tool_calls"]:
                function = Function(
                    arguments=tool_call["function"]["arguments"],
                    name=tool_call["function"]["name"],
                )
                tool_call_object = ChatCompletionMessageToolCall(
                    id=tool_call["id"], function=function, type=tool_call["type"]
                )
                tool_calls.append(tool_call_object)

            partial_response = await self.handle_tool_calls(
                tool_calls, active_agent.functions, session_context, debug
            )
            history.extend(partial_response.messages)
            if partial_response.agent:
                active_agent = partial_response.agent

        yield {
            "response": Response(
                messages=history[init_len:],
                agent=active_agent,
            )
        }
    
    async def run(
        self,
        agent: Agent,
        messages: List,
        session_context: SessionContext,
        model_override: str = None,
        stream: bool = False,
        debug: bool = False,
        max_turns: int = float("inf"),
        execute_tools: bool = True,
    ) -> Response:      
        if stream:
            return self.run_and_stream(
                agent=agent,
                messages=messages,
                session_context=session_context,
                model_override=model_override,
                debug=debug,
                max_turns=max_turns,
                execute_tools=execute_tools,
            )
        active_agent = agent
        history = copy.deepcopy(messages)
        init_len = len(messages)

        while len(history) - init_len < max_turns and active_agent:

            # get completion with current history, agent
            completion = self.get_chat_completion(
                agent=active_agent,
                history=history,
                session_context=session_context,
                model_override=model_override,
                stream=stream,
                debug=debug,
            )
            message = completion.choices[0].message
            print(debug, "Received completion:", message)
            message.sender = active_agent.name
            history.append(
                json.loads(message.model_dump_json())
            )  # to avoid OpenAI types (?)

            if not message.tool_calls or not execute_tools:
                print(debug, "Ending turn.")
                break

            # handle function calls, updating context_variables, and switching agents
            partial_response = await self.handle_tool_calls(
                message.tool_calls, active_agent.functions, session_context, debug
            )
            history.extend(partial_response.messages)
            if partial_response.agent:
                active_agent = partial_response.agent

        return Response(
            messages=history[init_len:],
            agent=active_agent
        )
