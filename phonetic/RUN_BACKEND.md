# Running the Backend Server

The backend runs a **FastAPI** application that exposes both a standard REST API and a Model Context Protocol (MCP) server.

## 1. Start the Server
Run the following command from the root of your project:

```bash
uv run uvicorn app.main:app --reload
```
*The `--reload` flag automatically restarts the server if you make changes to the code.*

## 2. Test the REST API
Once the server is running (usually at `http://127.0.0.1:8000`), you can test the pronunciation endpoint.

Open a new terminal and run:
```bash
curl http://127.0.0.1:8000/pronounce/beautiful
```

**Expected JSON Response:**
```json
{
  "word": "beautiful",
  "ipa": "ˈbjuːtɪfəl",
  "gujarati": "બ્યૂટિફઅલ"
}
```

## 3. View API Documentation
You can view the auto-generated Swagger documentation by opening your browser and navigating to:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
