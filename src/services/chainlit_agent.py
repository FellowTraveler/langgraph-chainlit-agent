import chainlit as cl
import pytz

from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from chainlit.input_widget import Select, Switch

from services.agent import SingleAgent
from services.voicevox import Voicevox
from services.voicevox import SpeakerData


class ChainlitAgent(SingleAgent):

    def __init__(
        self,
        system_prompt: str,
        speak: bool = False,
        speaker_name: str = "Shikoku Metan",
        style_name: str = "Normal",
        file_path: str = "./",
    ):
        super().__init__(system_prompt=system_prompt)
        self.speak = speak
        self.file_path = file_path
        if speak:
            self.voicevox_service = Voicevox(
                speaker_name=speaker_name, style_name=style_name, file_path=file_path
            )

    async def on_chat_start(self):
        """
        Function called when the chat starts
        """
        # Set initial values for Settings
        settings = await cl.ChatSettings(
            [
                Switch(
                    id="Speak",
                    label="Text-to-Speech",
                    initial=False,
                    description="Please select whether to use text-to-speech.",
                ),
                Select(
                    id="Speaker_ID",
                    label="VOICEVOX - Speaker Name and Style",
                    items=SpeakerData().get_all_speaker_and_style_dict(),
                    initial_value="2",
                    description="Please select the character and style to use for text-to-speech.",
                ),
            ]
        ).send()
        # Update settings based on initial values
        await self.on_settings_update(settings)

    async def on_settings_update(self, settings: dict):
        """
        Function called when Settings are updated
        """
        # Get Settings values and update VOICEVOX settings
        self.speak = settings["Speak"]
        self.voicevox_service = Voicevox(
            speaker_id=settings["Speaker_ID"], file_path=self.file_path
        )

    async def on_message(self, msg: cl.Message, inputs: list):
        """
        Function called when a message is sent
        """

        content = msg.content

        # Get information about attached files
        attachment_file_text = ""

        for element in msg.elements:
            attachment_file_text += f'- {element.name} (path: {element.path.replace("/workspace", ".")})\n'  # Adjust to match ./files/***/***.png format when the agent refers to it

        if attachment_file_text:
            content += f"\n\nAttached files\n{attachment_file_text}"

        # Get current date and time (JST)
        now = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S %Z")

        content += f"\n\n(Input time: {now})"

        # Add user's message to history
        inputs.append(HumanMessage(content=content))

        res = cl.Message(content="")
        steps = {}
        async for output in self.astream_events(inputs):
            if output["kind"] == "on_chat_model_stream":
                await res.stream_token(output["content"])
            elif output["kind"] == "on_tool_start":
                async with cl.Step(name=output["tool_name"], type="tool") as step:
                    step.input = output["tool_input"]
                    steps[output["run_id"]] = step
            elif output["kind"] == "on_tool_end":
                step = steps[output["run_id"]]
                step.output = output["tool_output"]
                await step.update()

        await res.send()

        # If text-to-speech is enabled, generate the speech file and add it to the message
        if self.speak:
            file_path = self.voicevox_service.post_synthesis_returned_in_file(
                text=res.content, use_manuscript=True, file_name="Text-to-Speech"
            )
            elements = [
                cl.Audio(
                    name="Text-to-Speech", path=file_path, display="inline", auto_play=True
                ),
            ]
            res.elements = elements
            await res.update()

        return AIMessage(content=res.content)
