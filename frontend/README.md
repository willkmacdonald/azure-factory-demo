# Factory Agent Frontend

React + TypeScript frontend for the Factory Agent application.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Authentication**: @azure/msal-react (Phase 5)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.development

# Edit .env.development if needed (default is localhost:8000)
```

### Development

```bash
# Start development server
npm run dev

# Access at http://localhost:5173
```

### Building for Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Development Status - PR11 Complete ✅

### PR11: Frontend Setup (COMPLETE)
- ✅ Vite + React + TypeScript project initialized
- ✅ Dependencies installed (MUI, Recharts, Axios, MSAL)
- ✅ Project structure created
- ✅ API client service implemented
- ✅ Type definitions created
- ✅ Environment configuration set up
- ✅ Basic App component with layout placeholders
- ✅ Build successfully compiles

### Next: PR12 - Dashboard Layout
- Split-pane layout implementation
- Machine filter component
- Date range selector
- Tab navigation

## Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
