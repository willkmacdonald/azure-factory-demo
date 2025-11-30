# Next Session Context

**Date**: 2025-11-29
**Task**: Complete Tailwind CSS Migration (Phase 6)
**Start With**: PR30 - Dashboard Page Migration

---

## What Happened This Session

1. **Dashboard was broken** - showing only header, no content
2. **Root cause**: Dashboard was rewritten to Tailwind CSS in commit `8a4c3de` but Tailwind wasn't fully working
3. **Quick fix applied**: Restored Dashboard to MUI (now working)
4. **Decision made**: Complete the Tailwind migration (Option A) rather than revert to pure MUI

---

## Current UI State

**Already Tailwind** (working):
- `frontend/src/components/layout/MainLayout.tsx`
- `frontend/src/components/auth/AuthButton.tsx`

**Still MUI** (need to convert):
- `frontend/src/pages/DashboardPage.tsx` ← **START HERE**
- `frontend/src/pages/MachinesPage.tsx`
- `frontend/src/pages/AlertsPage.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/TraceabilityPage.tsx`
- `frontend/src/components/MemoryPanel.tsx`
- `frontend/src/components/MemoryBadge.tsx`
- `frontend/src/components/ApiHealthCheck.tsx`

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

## PR30: Dashboard Page Migration

**File**: `frontend/src/pages/DashboardPage.tsx` (466 lines)

**Tasks**:
1. Replace MUI imports with Lucide icons
2. Convert Container/Box/Paper to div with Tailwind
3. Convert Grid to CSS Grid (`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6`)
4. Convert Card/CardContent to Tailwind card pattern
5. Convert Typography to semantic HTML with Tailwind
6. Convert Alert to Tailwind alert pattern
7. Convert Button to motion.button
8. Convert CircularProgress to Loader2 spinner
9. Style Recharts tooltips for dark theme
10. Test responsive + dark mode

**Reference file for patterns**: `MainLayout.tsx` - shows the Tailwind + Framer Motion style

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
<div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 text-blue-800 dark:text-blue-200">

// Loading
<Loader2 className="w-8 h-8 text-blue-600 animate-spin" />

// Page container
<div className="p-8">
  <div className="max-w-7xl mx-auto">
```

**Icon mapping**: `Add`→`Plus`, `Login`→`LogIn`, `Warning`→`AlertTriangle`, `CheckCircle`→`CheckCircle`

---

## Full Plan Location

See `implementation-plan.md` → "Phase 6: Tailwind CSS Migration" section for:
- Complete PR breakdown (PR30-PR35)
- Full icon mapping table
- Component patterns
- Testing checklist
- Success criteria

---

## After PR30

Continue with:
- PR31: MachinesPage + AlertsPage
- PR32: ChatPage
- PR33: TraceabilityPage
- PR34: MemoryPanel + MemoryBadge
- PR35: ApiHealthCheck + remove MUI dependencies

Delete this file when Phase 6 is complete.
