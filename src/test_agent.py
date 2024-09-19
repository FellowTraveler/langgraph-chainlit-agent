import sys
import asyncio

from langchain_core.messages import HumanMessage, AIMessage

from services.agent import SingleAgent


async def main(mode: str):
    """
    Function to verify the operation of the Agent.
    Enter 'exit' to terminate.

    Args:
        mode (str): Agent operation mode
            - stream: Mode where output is displayed as a stream
            - invoke: Mode where output is displayed all at once

    Returns:
        None
    """
    if mode is None:
        mode = "stream"
    print(f"mode: {mode}")
    inputs = []
    agent = SingleAgent(
        system_prompt="You are the best assistant chatbot.",
    )

    while True:
        print("Input to the chatbot:")
        query = input()
        if query == "exit":
            break

        inputs.append(HumanMessage(content=query))

        output_text = ""
        if mode == "stream":
            async for output in agent.astream_events(inputs):
                if output["kind"] == "on_chat_model_stream":
                    output_text += output["content"]
                    print(output["content"], end="", flush=True)
                elif output["kind"] == "on_tool_start":
                    print("--------------------")
                    print(f"Tool {output['tool_name']} started\n")
                    print(f"Input: {output["tool_input"]}\n")
                    print("--------------------\n")
                elif output["kind"] == "on_tool_end":
                    print("--------------------")
                    print(f"Tool {output['tool_name']} finished\n")
                    print(f"Input: {output["tool_input"]}\n")
                    print(f"Output:\n{output["tool_output"]}\n")
                    print("--------------------\n")
        elif mode == "invoke":
            output = await agent.ainvoke(inputs)
            output_text = output["content"]
            print(output_text)
            if output["tool_outputs"] != []:
                print("\nTool outputs:")
                for tool_output in output["tool_outputs"]:
                    print(f"Tool {tool_output['name']} output:")
                    print(tool_output["output"])
                    print("\n")

        print("\n\n")
        inputs.append(AIMessage(content=output_text))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode not in ["stream", "invoke"] and mode is not None:
        print("Invalid mode. Use 'stream' or 'invoke'.")
        # End the process
        sys.exit(1)
    asyncio.run(main(mode))
