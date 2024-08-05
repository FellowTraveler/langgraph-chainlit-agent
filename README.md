# LangGraph Agent with Chainlit

This project allows you to use a simple agent created with LangGraph as a web application using Chainlit.

For more details, please refer to the following articles:

- Article on the initial implementation
  - https://zenn.dev/0msys/articles/9873e25a610c5e
- Article on multimodal support
  - https://zenn.dev/0msys/articles/3d38729aa7f75b

## How to Use

### Starting the Application

Clone the repository.

Create a file named graph_agent.env and add the following content:
```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

Run the following command:
```
docker compose up -d
```

Access http://localhost:8000.

### Shutting Down

Run the following command:
```
docker compose down
```

### Development

If you want to develop, such as adding custom Tools, open this directory as a devcontainer.

Once the devcontainer is open, run the following command:

```
chainlit run -w main.py
```

You can then access http://localhost:8000 to view the interface while developing.
