# LangGraph Agent with Chainlit

This allows you to use a simple agent created with LangGraph as a web application using Chainlit.

Detailed explanations are provided in the following articles:

- Article on the initial implementation
  - https://zenn.dev/0msys/articles/9873e25a610c5e
- Article on multimodal support
  - https://zenn.dev/0msys/articles/3d38729aa7f75b
- Article on library updates
  - https://zenn.dev/0msys/articles/49ebb76cea1af6
- Article on TTS using VOICEVOX
  - https://zenn.dev/0msys/articles/ac55214d8d95cd

## How to Use

### How to Start

Clone the repository.

Create graph_agent.env and write the following content:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

Execute the following command:

```
docker compose up -d
```

Access http://localhost:8000.

### How to Stop

Execute the following command:

```
docker compose down
```

### How to Develop

Add the following to graph_agent.env:

```
VOICEVOX_API_DOMAIN=http://voicevox_engine-dev:50021/
```

If you want to develop, such as adding custom Tools, please open this directory as a devcontainer.

Once the devcontainer is open, execute the following command:

```
chainlit run -w src/main.py
```

You can develop while checking the screen by accessing http://localhost:8000.

#### Confirming Agent Operation Only

Since both Chainlit and LangGraph are frequently updated, we have prepared a method to start only the Agent to make it easier to identify which is causing issues if it doesn't work.

Execute the following command on the development container:

```
python src/test_agent.py
```

This will start only the Agent, allowing you to confirm its operation.
You can pass either "stream" or "invoke" as an argument to check each operation.

```
python src/test_agent.py invoke
```
(If nothing is passed, "stream" will be executed by default.)

#### Confirming VOICEVOX Operation Only

To confirm only the operation of VOICEVOX, execute the following command:

```
python src/services/voicevox.py
```

If there are no issues, output.wav will be generated.
