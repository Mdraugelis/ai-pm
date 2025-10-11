# AI Atlas - Backend API

**Navigate AI initiatives with intelligent assistance**

FastAPI backend for Geisinger's conversational AI Product Manager with SSE streaming support for thinking indicators.

## Features

✅ **Conversational Agent API** - Set mode and send messages
✅ **SSE Streaming** - Real-time thinking indicators (expandable reasoning)
✅ **Document Upload** - ServiceNow tickets, vendor docs, research papers
✅ **CORS Enabled** - Ready for React frontend
✅ **Error Handling** - Comprehensive exception handling
✅ **Health Checks** - Monitoring endpoint

## Architecture

```
UI (React) → FastAPI Backend → ConversationalAgent → Orchestrator (Agent Loop)
                ↓ SSE Stream
            Thinking Indicators
            (gather, plan, execute, verify)
```

## Directory Structure

```
backend/
├── __init__.py
├── config.py                    # Backend configuration
├── main.py                      # FastAPI app
├── api/
│   ├── models.py                # Pydantic request/response models
│   ├── routes/
│   │   ├── agent.py             # Agent endpoints (with SSE)
│   │   ├── documents.py         # Document upload
│   │   └── health.py            # Health check
│   └── services/
│       └── agent_service.py     # ConversationalAgent wrapper
└── middleware/
    └── error_handlers.py        # Exception handlers
```

## API Endpoints

### Health

- **GET** `/api/health` - Health check

### Agent

- **POST** `/api/agent/mode` - Set agent mode
  ```json
  {"mode": "ai_discovery"}
  ```

- **POST** `/api/agent/message/stream` - Send message with SSE streaming
  ```json
  {"message": "Generate Discovery Form for Epic Inbox AI"}
  ```
  **Returns:** SSE stream with thinking indicators

- **GET** `/api/agent/status` - Get agent status

- **GET** `/api/agent/conversation` - Get conversation history

- **DELETE** `/api/agent/conversation` - Clear conversation

### Documents

- **POST** `/api/documents/upload` - Upload document
  ```json
  {
    "content": "...",
    "doc_type": "vendor_doc",
    "metadata": {}
  }
  ```

- **GET** `/api/documents` - List documents

- **DELETE** `/api/documents/{doc_id}` - Delete document

- **DELETE** `/api/documents` - Clear all documents

## SSE Stream Format

The `/api/agent/message/stream` endpoint returns Server-Sent Events:

### Event Types

1. **thinking** - Agent reasoning step (expandable!)
   ```json
   {
     "step": "gather"|"plan"|"execute"|"verify",
     "iteration": 0,
     "confidence": 0.85,
     "reasoning": "Planning approach...",
     "details": {...}  // Full trace for expansion
   }
   ```

2. **iteration** - Iteration progress
   ```json
   {
     "iteration": 0,
     "total_iterations": 10,
     "status": "complete"
   }
   ```

3. **response** - Final agent response
   ```json
   {
     "content": "I've analyzed your request..."
   }
   ```

4. **complete** - Task completion
   ```json
   {
     "status": "SUCCESS",
     "requires_approval": false,
     "confidence": 0.85
   }
   ```

5. **error** - Error occurred
   ```json
   {
     "error": "AgentExecutionError",
     "message": "..."
   }
   ```

## Running the Server

### Development

```bash
# Start server with auto-reload
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Or use the main script
python -m backend.main
```

### Production

```bash
# Start with multiple workers
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the API

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/health

# Set mode
curl -X POST http://localhost:8000/api/agent/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "ai_discovery"}'

# Send message with SSE streaming
curl -N http://localhost:8000/api/agent/message/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate Discovery Form"}'

# Upload document
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Epic Inbox AI is a clinical decision support tool...",
    "doc_type": "vendor_doc",
    "metadata": {"vendor": "Epic"}
  }'

# Get conversation history
curl http://localhost:8000/api/agent/conversation

# Clear conversation
curl -X DELETE http://localhost:8000/api/agent/conversation
```

### Python Example

```python
import httpx

# Set mode
response = httpx.post(
    "http://localhost:8000/api/agent/mode",
    json={"mode": "ai_discovery"}
)
print(response.json())

# Stream message response
with httpx.stream(
    "POST",
    "http://localhost:8000/api/agent/message/stream",
    json={"message": "Generate Discovery Form"},
    timeout=60.0
) as response:
    for line in response.iter_lines():
        if line.startswith("data:"):
            data = line[5:].strip()
            print(data)
```

### JavaScript Example (React)

```javascript
// Using EventSource for SSE
const sendMessage = async (message) => {
  // Set message
  await fetch('http://localhost:8000/api/agent/message/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });

  // Listen to SSE stream
  const eventSource = new EventSource(
    'http://localhost:8000/api/agent/message/stream'
  );

  eventSource.addEventListener('thinking', (e) => {
    const data = JSON.parse(e.data);
    console.log('Thinking:', data.step, data.reasoning);
    // Show thinking indicator in UI
  });

  eventSource.addEventListener('response', (e) => {
    const data = JSON.parse(e.data);
    console.log('Response:', data.content);
    // Show final response
  });

  eventSource.addEventListener('complete', (e) => {
    const data = JSON.parse(e.data);
    console.log('Complete:', data.status);
    eventSource.close();
  });
};
```

## Configuration

Edit `backend/config.py` to configure:

- Server host and port
- CORS origins
- Agent configuration path
- Upload limits
- Session timeout
- SSE settings

## Error Handling

The backend includes custom exception handlers:

- **ValidationError** (400) - Invalid request data
- **ModeNotSetError** (400) - Mode not set before messaging
- **AgentExecutionError** (500) - Agent execution failed
- **Generic Exception** (500) - Unexpected error

All errors return JSON:
```json
{
  "error": "ErrorType",
  "message": "Error description",
  "detail": {...}
}
```

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Next Steps

1. **Start the backend**: `uvicorn backend.main:app --reload`
2. **Test endpoints**: Use cURL or Swagger UI
3. **Build React frontend**: Connect to SSE streaming endpoints
4. **Implement thinking indicators**: Use `thinking` events to show agent reasoning

## Notes

- The backend requires `ANTHROPIC_API_KEY` in `.env` to function
- Agent service is currently a singleton (single global instance)
- In production, implement per-session/per-user agent instances
- SSE streaming provides real-time thinking indicators for UI

## Troubleshooting

### Port already in use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### ANTHROPIC_API_KEY not set

Make sure `.env` contains:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Import errors

Make sure you're using the virtual environment:
```bash
source venv/bin/activate  # or ./venv/bin/python
```

---

**Version**: 1.0.0
**Last Updated**: October 2025
