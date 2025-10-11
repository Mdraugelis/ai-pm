# AI Atlas Frontend - AI Product Manager Agent Chat Interface

A modern React + TypeScript + Vite application providing a chat interface for the AI Product Manager Agent. Built with Mantine UI for professional, responsive components.

## Features

### Core Functionality
- **Multi-Mode Agent Support**: Switch between different agent modes for specialized assistance
  - AI Discovery Form Generation
  - Risk Assessment Analysis
  - POC Planning
  - General AI Product Management

- **Real-Time Streaming**: Server-sent events (SSE) for live agent responses
- **Transparent Reasoning**: Visual thinking indicators showing agent's decision process
- **Document Context**: Upload and manage documents to provide context for the agent
- **Professional UI**: Clean, responsive design using Mantine components

### Key Components

#### Chat Interface
- Message history with user/assistant distinction
- Real-time thinking indicators during processing
- Auto-scroll to latest messages
- Clear conversation functionality

#### Thinking Indicators
- Step-by-step visualization (Gather → Plan → Execute → Verify)
- Iteration tracking
- Confidence scores
- Expandable details for each reasoning step

#### Document Management
- File upload support (TXT, JSON, YAML, Markdown, PDF)
- Paste text from clipboard
- View uploaded documents
- Delete documents

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast builds and HMR
- **Mantine UI** for component library
- **TanStack Query** for data fetching
- **Tabler Icons** for iconography
- **Axios** for API communication

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:8000

## Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API service layer
│   │   └── agent.ts      # Agent API functions
│   ├── components/       # React components
│   │   ├── ChatInterface.tsx       # Main chat UI
│   │   ├── ModeSelector.tsx        # Agent mode selector
│   │   ├── ThinkingIndicator.tsx   # Reasoning visualization
│   │   ├── MessageList.tsx         # Message history display
│   │   ├── MessageInput.tsx        # Message input control
│   │   └── DocumentUpload.tsx      # Document management
│   ├── hooks/            # Custom React hooks
│   │   ├── useAgentStream.ts      # SSE streaming hook
│   │   └── useAgent.ts            # Agent state management
│   ├── types/            # TypeScript definitions
│   │   └── agent.ts              # Agent-related types
│   ├── styles/           # Global styles
│   │   └── global.css           # Global CSS
│   ├── App.tsx          # Main app component
│   └── main.tsx         # App entry point
├── package.json
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── index.html           # HTML template
```

## Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. Key endpoints:

- `POST /api/agent/mode` - Set agent mode
- `GET /api/agent/message/stream` - SSE stream for messages
- `GET /api/agent/conversation` - Get conversation history
- `POST /api/agent/conversation/clear` - Clear conversation
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Vite Configuration

The Vite config is set to:
- Run on port 5173
- Enable host access for network testing
- Configure React plugin for JSX

### Mantine Theme

The app uses Mantine's default blue theme with:
- Primary color: blue
- Default radius: md
- System font stack

## Development

### Adding New Components

1. Create component in `src/components/`
2. Import Mantine components as needed
3. Use TypeScript for type safety
4. Follow existing patterns for consistency

### Working with SSE

The `useAgentStream` hook handles SSE connections:
- Automatic reconnection on errors
- Event parsing for different message types
- Cleanup on component unmount

### State Management

- Local state with React hooks
- Server state with TanStack Query
- Agent state with custom `useAgent` hook

## Production Build

```bash
# Build the application
npm run build

# The build output will be in the 'dist' directory
# Serve with any static file server

# Preview the build locally
npm run preview
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### SSE Connection Issues
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify network connectivity

### UI Not Updating
- Check React DevTools for state changes
- Verify SSE events are being received
- Look for console errors

### Document Upload Failures
- Check file size limits
- Verify supported file types
- Ensure backend endpoint is accessible

## Contributing

1. Follow existing code patterns
2. Use TypeScript for all new code
3. Test components thoroughly
4. Update documentation as needed

## License

Proprietary - Geisinger Health System

## Support

For issues or questions, contact the AI Architecture Team.
