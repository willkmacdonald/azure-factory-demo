# Next Session Context

**Date**: 2025-11-29
**Task**: Complete Tailwind CSS Migration (Phase 6)
**Start With**: PR32 - ChatPage Migration

---

## What Happened This Session

1. **PR30 COMPLETE** - DashboardPage migrated to Tailwind CSS
   - Commit: `9d73bb8`
   - All MUI components replaced with Tailwind + Lucide icons
   - Custom Recharts tooltip for dark mode
   - Framer Motion animations added

2. **PR31 COMPLETE** - MachinesPage + AlertsPage migrated to Tailwind CSS
   - Commit: `9b85f61`
   - Custom progress bars replacing MUI LinearProgress
   - Custom table with pagination controls
   - Native select dropdown styling

---

## Current UI State

**Already Tailwind** (working):
- `frontend/src/components/layout/MainLayout.tsx` ✅
- `frontend/src/components/auth/AuthButton.tsx` ✅
- `frontend/src/pages/DashboardPage.tsx` ✅ (PR30)
- `frontend/src/pages/MachinesPage.tsx` ✅ (PR31)
- `frontend/src/pages/AlertsPage.tsx` ✅ (PR31)

**Still MUI** (need to convert):
- `frontend/src/pages/ChatPage.tsx` ← **START HERE (PR32)**
- `frontend/src/pages/TraceabilityPage.tsx` (PR33)
- `frontend/src/components/MemoryPanel.tsx` (PR34)
- `frontend/src/components/MemoryBadge.tsx` (PR34)
- `frontend/src/components/ApiHealthCheck.tsx` (PR35)

---

## How to Start

```bash
# Terminal 1 - Backend
cd backend
PYTHONPATH=/Users/willmacdonald/Documents/Code/azure/factory-agent venv/bin/uvicorn src.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Then open http://localhost:5174

---

## PR32: Chat Page Migration

**File**: `frontend/src/pages/ChatPage.tsx` (462 lines)

**Tasks**:
1. Replace MUI imports with Lucide icons (Send, Trash2, Bot, User, etc.)
2. Convert Container/Box/Paper to div with Tailwind
3. Convert message bubbles (user vs AI styling)
4. Convert TextField to styled input with send button
5. Convert tool call status indicators
6. Convert IconButton to motion.button
7. Convert CircularProgress to Loader2 spinner
8. Style markdown rendering for dark theme
9. Test responsive + dark mode

**Key Patterns**:
```tsx
// User message bubble
<div className="bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2 ml-auto max-w-[80%]">

// AI message bubble
<div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%]">

// Tool status indicator
<div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-1.5 text-sm">

// Chat input
<input className="flex-1 px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500" />
```

**Icon mapping for ChatPage**:
- `Send` → `Send`
- `Delete` → `Trash2`
- `Person` → `User`
- `SmartToy` → `Bot`
- `Psychology` → `Brain`
- `Summarize` → `FileText`
- `Close` → `X`

---

## Design System Quick Reference

```tsx
// Card
<div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">

// Primary Button
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
>

// Alert (info)
<div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3">
  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />
  <p className="text-blue-800 dark:text-blue-200">...</p>
</div>

// Loading
<Loader2 className="w-8 h-8 text-blue-600 animate-spin" />

// Page container
<div className="p-8">
  <div className="max-w-7xl mx-auto">
```

---

## Remaining PRs After PR32

- **PR33**: TraceabilityPage (1044 lines - largest, most complex)
- **PR34**: MemoryPanel + MemoryBadge
- **PR35**: ApiHealthCheck + remove MUI dependencies

---

## Full Plan Location

See `implementation-plan.md` → "Phase 6: Tailwind CSS Migration" section for:
- Complete PR breakdown (PR30-PR35)
- Full icon mapping table
- Component patterns
- Testing checklist
- Success criteria

---

Delete this file when Phase 6 is complete.
