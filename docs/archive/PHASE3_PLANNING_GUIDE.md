# Phase 3 Planning Guide: React Frontend Development

**Document Version**: 1.0
**Created**: 2025-11-03
**Status**: Ready for Phase 3 Implementation

---

## Executive Summary

The Factory Agent codebase is **production-ready for frontend development**. Phase 1 (Backend API) and Phase 2 (Azure Blob Storage) are complete with:

- ✅ Fully functional FastAPI backend with all required endpoints
- ✅ Comprehensive test coverage (79+ tests)
- ✅ Dual storage mode (local JSON + Azure Blob Storage)
- ✅ Security hardening (CORS, rate limiting, input validation)
- ✅ Proper async/await patterns throughout
- ✅ Clean API documentation (auto-generated Swagger UI at /docs)

The backend is now **waiting for the React frontend** to complete the full system.

---

## 1. Current Backend Capabilities (Ready to Use)

### All Available API Endpoints

#### Metrics Endpoints (GET)
```
GET /api/metrics/oee
  Required: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
  Optional: machine=<name>
  Response: {oee, availability, performance, quality, produced_units, defective_units}

GET /api/metrics/scrap
  Required: start_date, end_date
  Optional: machine
  Response: {total_scrap, scrap_rate, by_machine}

GET /api/metrics/quality
  Required: start_date, end_date
  Optional: severity (Low|Medium|High), machine
  Response: {total_issues, by_severity, issues: []}

GET /api/metrics/downtime
  Required: start_date, end_date
  Optional: machine
  Response: {total_downtime, by_reason, major_events: []}
```

#### Data Management Endpoints
```
POST /api/setup
  Optional: {days: 30}
  Response: {message, days, start_date, end_date, machines}
  Rate limit: 5/minute

GET /api/stats
  Response: {exists, start_date, end_date, total_days, total_machines, total_records}

GET /api/machines
  Response: [{id, name, type, ideal_cycle_time}, ...]

GET /api/date-range
  Response: {start_date, end_date, total_days}
```

#### Chat Endpoint (POST)
```
POST /api/chat
  Request: {message: string, history: [{role, content}, ...]}
  Response: {response: string, history: [{role, content}, ...]}
  Rate limit: 10/minute
  Features:
  - Tool calling with 4 analysis functions
  - Conversation history management
  - Input validation
```

#### System Endpoints
```
GET /health
  Response: {status: "healthy"}

GET /docs
  Response: Interactive Swagger UI with all endpoints
```

---

## 2. Backend Running Instructions

### Quick Start (Local Development)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment (MUST do this first)
cp ../.env.example ../.env
# Edit .env with your Azure OpenAI credentials

# 3. Start backend server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Using Docker

```bash
# From project root
docker-compose up --build

# This starts:
# - Backend: http://localhost:8000
# - Frontend will be on port 3000 (when ready)
```

### Generating Test Data

```bash
# Using API
curl -X POST http://localhost:8000/api/setup

# Or using curl with days parameter
curl -X POST http://localhost:8000/api/setup -H "Content-Type: application/json" -d '{"days": 60}'
```

---

## 3. React Frontend Setup (Phase 3 Work)

### Project Structure to Create

```
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── OEEGauge.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── DowntimeTable.tsx
│   │   │   ├── QualityTable.tsx
│   │   │   └── MachineFilter.tsx
│   │   ├── console/
│   │   │   ├── ChatConsole.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageItem.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── DashboardPanel.tsx
│   │   └── ConsolePanel.tsx
│   ├── services/
│   │   └── api.ts              # Axios HTTP client
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces
│   ├── App.tsx                 # Main app with split-pane layout
│   ├── App.css                 # Global styles
│   └── main.tsx                # Entry point
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .eslintrc.json
└── Dockerfile
```

### Step 1: Initialize React Project (PR11 Work)

```bash
# Create React + Vite project
npm create vite@latest factory-agent-frontend -- --template react-ts

# Navigate to project
cd factory-agent-frontend

# Install dependencies
npm install

# Install additional libraries
npm install @mui/material @emotion/react @emotion/styled
npm install recharts
npm install axios
npm install @azure/msal-react @azure/msal-browser  # For future auth
npm install typescript --save-dev

# Create .env for development
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.development
```

### Step 2: API Client Service (shared across components)

Create `src/services/api.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  history: ChatMessage[];
}

export const apiService = {
  // Health
  checkHealth: () => apiClient.get('/health'),

  // Data management
  generateData: (days?: number) => 
    apiClient.post('/api/setup', { days: days || 30 }),
  getStats: () => apiClient.get('/api/stats'),
  getMachines: () => apiClient.get('/api/machines'),
  getDateRange: () => apiClient.get('/api/date-range'),

  // Metrics
  getOEE: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get('/api/metrics/oee', {
      params: { start_date: startDate, end_date: endDate, machine },
    }),
  getScrap: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get('/api/metrics/scrap', {
      params: { start_date: startDate, end_date: endDate, machine },
    }),
  getQuality: (startDate: string, endDate: string, severity?: string, machine?: string) =>
    apiClient.get('/api/metrics/quality', {
      params: { start_date: startDate, end_date: endDate, severity, machine },
    }),
  getDowntime: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get('/api/metrics/downtime', {
      params: { start_date: startDate, end_date: endDate, machine },
    }),

  // Chat
  chat: (request: ChatRequest) => 
    apiClient.post<ChatResponse>('/api/chat', request),
};

export default apiService;
```

### Step 3: Type Definitions

Create `src/types/index.ts`:

```typescript
export interface Machine {
  id: number;
  name: string;
  type: string;
  ideal_cycle_time: number;
}

export interface OEEMetrics {
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  produced_units: number;
  defective_units: number;
}

export interface ScrapMetrics {
  total_scrap: number;
  scrap_rate: number;
  by_machine: Record<string, number>;
}

export interface QualityIssue {
  date: string;
  machine: string;
  defect_type: string;
  quantity: number;
  severity: 'Low' | 'Medium' | 'High';
  description: string;
}

export interface QualityIssues {
  total_issues: number;
  by_severity: Record<string, number>;
  issues: QualityIssue[];
}

export interface DowntimeEvent {
  date: string;
  machine: string;
  reason: string;
  duration_hours: number;
  severity: 'Critical' | 'Major' | 'Minor';
}

export interface DowntimeAnalysis {
  total_downtime: number;
  by_reason: Record<string, number>;
  major_events: DowntimeEvent[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface DateRange {
  start_date: string;
  end_date: string;
  total_days: number;
}
```

---

## 4. Component Design Patterns

### Dashboard Components

#### OEEGauge.tsx Pattern
```typescript
import { useState, useEffect } from 'react';
import apiService from '../services/api';
import { OEEMetrics } from '../types';

interface OEEGaugeProps {
  startDate: string;
  endDate: string;
  machine?: string;
}

export const OEEGauge: React.FC<OEEGaugeProps> = ({ startDate, endDate, machine }) => {
  const [oee, setOee] = useState<OEEMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOEE = async () => {
      try {
        setLoading(true);
        const response = await apiService.getOEE(startDate, endDate, machine);
        setOee(response.data);
      } catch (err) {
        setError(`Failed to load OEE data: ${err}`);
      } finally {
        setLoading(false);
      }
    };

    fetchOEE();
  }, [startDate, endDate, machine]);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!oee) return <Alert severity="info">No data available</Alert>;

  return (
    <Box>
      <Typography>OEE: {(oee.oee * 100).toFixed(1)}%</Typography>
      {/* Gauge component rendering */}
    </Box>
  );
};
```

### Chat Console Pattern
```typescript
import { useState } from 'react';
import apiService, { ChatMessage } from '../services/api';

export const ChatConsole: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      setLoading(true);
      const response = await apiService.chat({
        message: input,
        history: messages,
      });
      setMessages(response.data.history);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <MessageList messages={messages} />
      <ChatInput 
        value={input}
        onChange={setInput}
        onSend={handleSendMessage}
        disabled={loading}
      />
    </Box>
  );
};
```

---

## 5. Layout Design: Split-Pane Dashboard

### Main App Layout
```typescript
// App.tsx
import { useState } from 'react';
import { Box, Container, Paper } from '@mui/material';
import DashboardPanel from './components/DashboardPanel';
import ConsolePanel from './components/ConsolePanel';

export default function App() {
  const [selectedMachine, setSelectedMachine] = useState<string | undefined>();
  const [dateRange, setDateRange] = useState({
    startDate: '2024-10-01',
    endDate: '2024-10-31',
  });

  return (
    <Container maxWidth="xl" sx={{ height: '100vh', py: 2 }}>
      <Box sx={{ display: 'flex', gap: 2, height: '100%' }}>
        {/* Dashboard Panel (left) */}
        <Paper sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <DashboardPanel
            selectedMachine={selectedMachine}
            dateRange={dateRange}
            onMachineChange={setSelectedMachine}
            onDateRangeChange={setDateRange}
          />
        </Paper>

        {/* Console Panel (right) */}
        <Paper sx={{ flex: 1, overflow: 'auto', p: 2, display: 'flex', flexDirection: 'column' }}>
          <ConsolePanel />
        </Paper>
      </Box>
    </Container>
  );
}
```

---

## 6. Testing Strategy for Frontend

### Unit Tests (for PR13+)
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { OEEGauge } from './OEEGauge';

test('OEEGauge loads and displays OEE percentage', async () => {
  render(<OEEGauge startDate="2024-10-01" endDate="2024-10-31" />);
  
  await waitFor(() => {
    expect(screen.getByText(/OEE:/)).toBeInTheDocument();
  });
});
```

### Integration Tests (for PR14+)
```typescript
// Test full chat flow
test('Chat console sends message and receives response', async () => {
  render(<ChatConsole />);
  
  // Type message
  userEvent.type(screen.getByPlaceholderText(/message/i), 'What was OEE?');
  
  // Send
  userEvent.click(screen.getByRole('button', { name: /send/i }));
  
  // Wait for response
  await waitFor(() => {
    expect(screen.getByText(/response/i)).toBeInTheDocument();
  });
});
```

---

## 7. Material-UI Configuration

### Theme Setup (optional but recommended)
```typescript
// src/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// In App.tsx
import { ThemeProvider } from '@mui/material/styles';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      {/* App content */}
    </ThemeProvider>
  );
}
```

---

## 8. Environment Configuration

### .env.development
```
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG=true
```

### .env.production
```
VITE_API_BASE_URL=https://api.factory-agent.com
VITE_DEBUG=false
```

### Using in Components
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const debugMode = import.meta.env.VITE_DEBUG === 'true';
```

---

## 9. Development Workflow

### Running Frontend + Backend Locally

**Terminal 1: Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 3: Tests (optional)**
```bash
cd frontend
npm run test
```

**Access in Browser**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 10. Key Implementation Notes

### Why These Technology Choices?

1. **Vite** instead of Create React App
   - Faster build times
   - Better development experience
   - Smaller bundle size

2. **Material-UI (MUI)**
   - Comprehensive component library
   - Professional appearance
   - Good TypeScript support
   - Beginner-friendly

3. **Recharts** for charts
   - Simpler API than Plotly for React
   - Small bundle size
   - Good React integration

4. **Axios** for HTTP
   - Simple API
   - Request/response interceptors
   - Better error handling than fetch

### Error Handling Best Practices

```typescript
const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 429) {
      return 'Too many requests. Please wait a moment.';
    }
    return error.response?.data?.detail || 'API error';
  }
  return 'Unknown error';
};
```

### Loading States

```typescript
// Always use three states: loading, error, success
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<Data | null>(null);

if (loading) return <CircularProgress />;
if (error) return <Alert severity="error">{error}</Alert>;
if (!data) return <Alert severity="info">No data</Alert>;
```

---

## 11. PR Plan for Phase 3

### PR11: React Frontend Setup & Infrastructure
- Initialize Vite + React + TypeScript project
- Install all dependencies
- Create project structure and directories
- Set up environment variable handling
- Create API client service (api.ts)
- Create type definitions (types/index.ts)
- Add .env.example for frontend
- Basic App component with layout structure
- **Deliverable**: Empty frontend that can compile and connect to backend

### PR12: Dashboard Layout & Filters
- Create DashboardPanel component
- Create ConsolePanel component
- Implement split-pane layout
- Add MachineFilter component with machine selection
- Add DateRangeSelector component
- Add tabs for OEE, Availability, Quality
- Wire up date/machine filtering
- **Deliverable**: Layout with functional filters (data not yet displayed)

### PR13: Dashboard Visualizations
- OEEGauge component (circular gauge chart)
- TrendChart component (line chart showing OEE over time)
- DowntimeTable component (sortable table)
- QualityTable component (severity-colored table)
- Wire up API calls to display metrics
- Add error handling and loading states
- **Deliverable**: Fully functional dashboard displaying data from backend

### PR14: Chat Console
- ChatConsole component (main container)
- MessageList component (displays messages)
- MessageItem component (individual messages with styling)
- ChatInput component (text input + send button)
- Wire up /api/chat endpoint
- Implement conversation history management
- Add loading indicators while waiting for response
- **Deliverable**: Fully functional chat interface with backend AI

### PR15: Deployment & Polish
- Create Docker configuration for frontend
- Update docker-compose.yml for both services
- Create GitHub Actions CI/CD workflow
- Add ESLint configuration
- Add basic unit tests for key components
- Documentation updates
- **Deliverable**: Deployed to Azure Container Apps

---

## 12. Testing Checklist for Phase 3

### Before Each PR (Dev Testing)
- [ ] Frontend compiles without errors
- [ ] Browser console shows no errors
- [ ] API calls work correctly (check Network tab)
- [ ] Rate limiting works (verify 429 after 10+ requests)
- [ ] Error messages display properly
- [ ] Loading states work (add artificial delays to test)
- [ ] Responsive design works on mobile

### Before Final Merge
- [ ] All tests pass: `npm run test`
- [ ] ESLint passes: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors: `npm run type-check` (if available)
- [ ] API documentation matches implementation

---

## 13. Current Backend Readiness Checklist

- [x] All endpoints implemented
- [x] All tests passing (79+ tests)
- [x] Rate limiting working
- [x] CORS configured
- [x] Input validation implemented
- [x] Error handling comprehensive
- [x] Async/await patterns correct
- [x] Documentation auto-generated
- [x] Docker containerization ready
- [x] Environment variables configurable
- [x] Azure Blob Storage support implemented
- [x] Conversation history validation implemented

**Status**: ✅ READY FOR FRONTEND DEVELOPMENT

---

## 14. Quick Reference: Backend Requirements

```yaml
Backend Running:
  - Command: uvicorn src.api.main:app --reload
  - Port: 8000
  - URL: http://localhost:8000

Environment Variables (Required):
  - AZURE_ENDPOINT: Your Azure OpenAI endpoint
  - AZURE_API_KEY: Your API key
  - AZURE_DEPLOYMENT_NAME: Your model deployment

Optional Environment Variables:
  - STORAGE_MODE: local (default) or azure
  - DEBUG: false (default) or true
  - ALLOWED_ORIGINS: http://localhost:3000,http://localhost:5173

Available at:
  - API: http://localhost:8000
  - Swagger Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/health

Data Management:
  - Generate test data: POST /api/setup
  - Check status: GET /api/stats
  - List machines: GET /api/machines
```

---

## 15. Success Criteria for Phase 3

### By End of PR11: Frontend Infrastructure
- React project initializes and builds
- Environment variables properly configured
- API client can make requests to backend
- TypeScript compilation clean

### By End of PR12: Layout Complete
- Split-pane layout renders correctly
- Filters accept user input
- Layout responsive on different screen sizes

### By End of PR13: Dashboard Functional
- All 4 metric charts render data
- Filtering by machine works
- Date range selection works
- Error states handled gracefully

### By End of PR14: Chat Functional
- Chat messages send and receive
- Conversation history maintained
- Tool calling works (AI uses analysis functions)
- Loading states display correctly

### By End of PR15: Deployment Ready
- Docker image builds successfully
- GitHub Actions workflow executes
- Azure Container Apps deployment works
- Frontend + backend communicate in production

---

## Summary

The Factory Agent backend is **production-ready and waiting for the React frontend**. All necessary APIs are implemented, tested, and documented. The frontend development can proceed immediately with the guidance provided in this document.

**Current Status**: 🟢 Ready for Phase 3 Implementation
**Estimated Effort**: 2-3 weeks for 5 PRs at current pace
**Next Action**: Initialize React project (PR11)

