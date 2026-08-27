# Running the Gemini AI Agent

This script runs an interactive terminal session where Gemini acts as an intelligent assistant. It understands your natural language questions and automatically calls your Python phonetics engine as a "tool" to get the exact Gujarati pronunciation.

## 1. Prerequisite: Add your API Key
Before running the agent, you must provide a valid Gemini API key.

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Open the `.env` file in the root of this project.
3. Replace the placeholder with your actual key:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key...
   ```

## 2. Start the Agent
Run the agent script directly as a Python module:

```bash
uv run python -m app.services.ai_agent
```

## 3. Interact with the Agent
Once the agent starts, you will see a terminal prompt. You can ask it natural language questions:

```text
You ▸ How do you say 'kitchen' in Gujarati phonetic text?

Gemini ▸ The English word "kitchen" is pronounced as કિટ્શઅન (IPA: ˈkɪt͡ʃən) in Gujarati phonetic script.
```

*Note: You do not need to run the backend server (`uvicorn`) to use this agent script. The script imports and runs your Python logic directly.*
