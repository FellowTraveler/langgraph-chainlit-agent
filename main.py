import chainlit as cl

from langchain_core.messages import HumanMessage, AIMessage

from graph_agent import create_agent


@cl.on_chat_start
async def on_chat_start():
    # When a session starts, create an agent and save it to the session
    app = create_agent()
    cl.user_session.set("app", app)

    # Save a list in the session to store the message history
    cl.user_session.set("inputs", {"messages": []})


@cl.on_message
async def on_message(msg: cl.Message):
    # When a message is received, retrieve the agent and message history from the session
    app = cl.user_session.get("app")
    inputs = cl.user_session.get("inputs")

    attachment_file_text = ""

    for element in msg.elements:
        attachment_file_text += f'- {element.name} (path: {element.path.replace("/workspace", ".")})\n' # Adjust the path so that when the agent references it, it becomes ./files/***/***.png
    
    content = msg.content
    
    if attachment_file_text:
        content += f"\n\nAttachment\n{attachment_file_text}"

    # Add the user's message to the history
    inputs["messages"].append(HumanMessage(content=content))

    # Send an empty message to prepare a place for streaming
    agent_message = cl.Message(content="")
    await agent_message.send()
    
    chunks = []

    # Execute the agent
    async for output in app.astream_log(inputs, include_types=["llm"]):
        for op in output.ops:
            if op["path"] == "/streamed_output/-":
                # Display the progress in steps
                edge_name = list(op["value"].keys())[0]
                message = op["value"][edge_name]["messages"][-1]
                
                # For action nodes, display the message content (the return value of the Tool is displayed)
                if edge_name == "action":
                    step_name = message.name
                    step_output = "```\n" + message.content + "\n```"

                # For agent nodes, in case of a function call, display the function name and arguments
                elif hasattr(message, "additional_kwargs") and message.additional_kwargs:
                    step_name = edge_name
                    step_output = f'function call: {message.additional_kwargs["function_call"]["name"]}\n\n```\n{message.additional_kwargs["function_call"]["arguments"]}\n```'
                
                # For other patterns, don't display anything for now
                else:
                    continue

                # Send the step
                async with cl.Step(name=step_name) as step:
                    step.output = step_output
                    await step.update()

            elif op["path"].startswith("/logs/") and op["path"].endswith(
                "/streamed_output_str/-"
            ):
                # Stream the final response to the message prepared in advance
                chunks.append(op["value"])
                await agent_message.stream_token(op["value"])

        # Combine the streamed responses to create the final response
        res = "".join(chunks)

    # Add the final response to the history and save it to the session
    inputs["messages"].append(AIMessage(content=res))
    cl.user_session.set("inputs", inputs)

    await agent_message.update()
