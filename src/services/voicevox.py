import requests
import base64
import json
import re
import os

from openai import OpenAI


class SpeakerData:
    """
    SpeakerData class
    Class for retrieving speaker information from VOICEVOX
    """

    def __init__(self, domain: str = None):
        self.domain = domain or os.getenv(
            "VOICEVOX_API_DOMAIN", "http://voicevox_engine:50021/"
        )
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Retrieve the list of speakers from the API and return in dictionary format"""
        speakers_json = requests.get(url=f"{self.domain}speakers").json()
        return {
            item["name"]: {style["name"]: style["id"] for style in item["styles"]}
            for item in speakers_json
        }

    def get_all_speaker_and_style_list(self) -> list:
        """Get a list of speaker_ids for combinations of speakers and styles"""
        return [
            {
                f"{speaker}-{style}": self.data[speaker][style]
                for style in self.data[speaker]
            }
            for speaker in self.data
        ]

    def get_all_speaker_and_style_dict(self) -> dict:
        """Get a dictionary of speaker_ids for combinations of speakers and styles"""
        return {
            f"{speaker} - {style}": str(self.data[speaker][style])
            for speaker in self.data
            for style in self.data[speaker]
        }


class Voicevox:
    """
    Voicevox class
    Class for using the VOICEVOX API
    """

    def __init__(
        self,
        speaker_name: str = None,
        style_name: str = None,
        speaker_id: str = None,
        file_path: str = "./",
    ):
        self.domain = os.getenv("VOICEVOX_API_DOMAIN", "http://voicevox_engine:50021/")
        self.speaker_id = self._get_speaker_id(speaker_name, style_name, speaker_id)
        self.file_path = file_path

    def _get_speaker_id(
        self, speaker_name: str, style_name: str, speaker_id: str
    ) -> str:
        """Helper method to get speaker_id"""
        if speaker_id:
            return speaker_id
        elif speaker_name and style_name:
            speakers = SpeakerData().data
            return speakers[speaker_name][style_name]
        else:
            raise ValueError(
                "speaker_id or speaker_name and style_name must be provided"
            )

    def _post_audio_query(self, text: str) -> json:
        """POST audio query and return the result"""
        response = requests.post(
            url=f"{self.domain}audio_query",
            params={"text": text, "speaker": self.speaker_id},
        )
        return response.json()

    def _post_synthesis(self, text: str) -> bytes:
        """Perform voice synthesis and return the binary data result"""
        query = self._post_audio_query(text)
        response = requests.post(
            url=f"{self.domain}synthesis",
            params={"speaker": self.speaker_id},
            json=query,
        )
        return response.content

    def post_synthesis_returned_in_base64(
        self, text: str, use_manuscript: bool = False
    ) -> str:
        """Input text, generate audio file, and return in base64 format"""
        if use_manuscript:
            text = self._create_manuscript(text)
        audio_data = self._post_synthesis(text)
        return base64.b64encode(audio_data).decode()

    def post_synthesis_returned_in_file(
        self, text: str, use_manuscript: bool = False, file_name: str = "output"
    ) -> str:
        """Input text, generate audio file, and return the file path"""
        if use_manuscript:
            text = self._create_manuscript(text)
        audio_data = self._post_synthesis(text)
        file_path = os.path.join(self.file_path, f"{file_name}.wav")
        with open(file_path, "wb") as file:
            file.write(audio_data)
        return file_path

    def _create_manuscript(self, text: str) -> str:
        """Input text and generate a script for reading aloud"""
        client = OpenAI()
        system_prompt = re.sub(
            r"\n\s*",
            "\n",
            """You are a text-to-speech generator. Please respond with a script to read aloud the text provided by the user. Follow these rules:
                    - Convert alphabetic proper nouns to katakana and kanji to hiragana to avoid mispronunciation
                    - For URLs and code blocks, instead of reading them as-is, rephrase to prompt the viewer to check the screen
                    Input text:""",
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{text}\n\nScript for reading aloud:"},
            ],
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    voicevox = Voicevox(speaker_name="Zundamon", style_name="Normal")
    text = "Hello"
    audio_file = voicevox.post_synthesis_returned_in_file(text, use_manuscript=True)
    print(audio_file)
