# Factory Agent Memory System - Demo Guide

**Duration**: 10-15 minutes
**Focus**: Agent memory capabilities for manufacturing context persistence
**Last Updated**: 2025-11-26

---

## Overview

The Factory Agent memory system enables persistent context across conversations, allowing the AI to:
- Track ongoing investigations into factory issues
- Log actions/changes with baseline metrics for impact measurement
- Generate shift handoff summaries
- Proactively remind about pending follow-ups

This guide demonstrates these capabilities with step-by-step scenarios.

---

## Prerequisites

- Backend running: `cd backend && PYTHONPATH=.. venv/bin/uvicorn src.api.main:app --reload --port 8000`
- Frontend running: `cd frontend && npm run dev`
- Browser open to http://localhost:5173/chat
- Azure Blob Storage configured (memory persists to `memory.json` blob)

---

## Demo Scenario 1: Creating an Investigation

**Context**: You notice the CNC-001 machine has elevated scrap rates and want to track the investigation.

### Step 1: Report the Issue

**Type in chat**:
```
I'm seeing elevated scrap rates on CNC-001 today - about 8% vs our normal 3%.
Can you create an investigation to track this issue?
```

**Expected AI Response**:
- AI acknowledges the issue
- Creates investigation using `save_investigation` tool
- Returns investigation ID (e.g., `INV-20251126-143022`)
- Confirms the investigation is open

**Talking Points**:
> "The AI has created a formal investigation record. This persists in Azure Blob Storage -
> it will remember this even if we close the browser or come back tomorrow."

### Step 2: Verify in Memory Panel

**Click the brain icon** (Psychology icon) in the chat header to open the Memory Panel.

**What you'll see**:
- **Investigations tab**: Shows the new investigation with "Open" status
- **Investigation details**: Title, initial observation, machine ID
- **Timestamp**: When it was created

**Talking Points**:
> "The Memory Panel gives operators visibility into what the AI is tracking.
> Anyone on the team can see open investigations - this is institutional memory."

---

## Demo Scenario 2: Logging an Action with Impact Tracking

**Context**: You've decided to adjust machine parameters and want to track whether it helps.

### Step 1: Log the Action

**Type in chat**:
```
I'm going to reduce the spindle speed on CNC-001 from 2000 to 1800 RPM to see if it
improves quality. The current OEE is 72% and scrap rate is 8%. Log this action so we
can measure the impact later.
```

**Expected AI Response**:
- AI acknowledges the change
- Calls `log_action` tool with:
  - Description of the change
  - Action type: `parameter_change`
  - Baseline metrics: `{"oee": 0.72, "scrap_rate": 0.08}`
  - Expected impact
- Returns action ID (e.g., `ACT-20251126-143522`)
- Optionally asks about follow-up date

**Talking Points**:
> "Notice the AI captured baseline metrics automatically. When we come back in a few days,
> it can tell us: 'Your spindle speed change improved scrap rate from 8% to 4%' - or warn
> us if things got worse."

### Step 2: Set a Follow-up Date

**Type in chat**:
```
Set a follow-up for this action in 3 days so we can check the results.
```

**Talking Points**:
> "The AI will remind us to check the impact. Nothing falls through the cracks."

---

## Demo Scenario 3: Shift Handoff Summary

**Context**: Day shift is ending and night shift needs a briefing.

### Step 1: Request Shift Summary

**Type in chat**:
```
Generate a shift summary for the incoming night shift.
```

**Expected AI Response**:
- Calls `generate_shift_summary` internally
- Returns a structured summary including:
  - **Active Investigations**: What issues are being tracked
  - **Today's Actions**: What changes were made
  - **Pending Follow-ups**: What needs attention
  - **Key Metrics**: Summary of today's performance

### Step 2: View in Memory Panel

**Click the brain icon** and navigate to the **Summary tab**.

**What you'll see**:
- Summary date
- Counts: Active investigations, today's actions, pending follow-ups
- Detailed lists for each category

**Talking Points**:
> "This used to be a 30-minute verbal briefing where half the details got lost.
> Now it's instant, documented, and consistent every shift change."

---

## Demo Scenario 4: Investigation Continuity

**Context**: It's the next day. Let's see if the AI remembers our investigation.

### Step 1: Ask About Open Issues

**Type in chat**:
```
What investigations do we have open? Any updates on the CNC-001 quality issue?
```

**Expected AI Response**:
- AI recalls the investigation from memory
- Shows investigation status, initial observation, any findings
- May proactively mention if follow-ups are due

**Talking Points**:
> "The AI remembered our investigation from yesterday - and will remember it next week too.
> This is institutional knowledge that doesn't walk out the door when people change shifts."

### Step 2: Update the Investigation

**Type in chat**:
```
We found the root cause - the tooling was worn and causing vibration.
Update the CNC-001 investigation with this finding and change status to 'resolved'.
```

**Expected AI Response**:
- Calls `update_investigation` with:
  - New finding appended
  - Status changed to "resolved"
- Confirms the update

**Talking Points**:
> "Now we have a complete audit trail - when we discovered the issue, what we tried,
> what the root cause was. This knowledge compounds over time."

---

## Demo Scenario 5: Follow-up Reminders

**Context**: Checking what needs attention today.

### Step 1: Check Pending Follow-ups

**Type in chat**:
```
Are there any actions due for follow-up today?
```

**Expected AI Response**:
- Checks pending follow-ups using `get_pending_followups` tool
- Lists any actions where:
  - Follow-up date has passed
  - Actual impact hasn't been recorded yet
- Suggests checking the results

### Step 2: Record the Impact

**Type in chat**:
```
The spindle speed adjustment worked - scrap rate is now down to 3.5% from 8%.
Record this as the actual impact for that action.
```

**Talking Points**:
> "We now have empirical evidence that this change works for our factory.
> Over time, this builds a knowledge base of proven improvements."

---

## Memory UI Components

### MemoryBadge (Chat Header)

Location: Next to the chat input clear button

**Features**:
- Shows count of open investigations + pending follow-ups
- **Color coding**:
  - Red badge: Pending follow-ups need attention
  - Orange badge: Open investigations exist
  - No badge: No active items
- **Pulsing animation**: When items need attention
- **Tooltip**: Hover to see breakdown

### MemoryPanel (Drawer)

Click the MemoryBadge to open.

**Three Tabs**:

1. **Investigations Tab**
   - List of all investigations
   - Status badges (Open, In Progress, Resolved, Closed)
   - Machine/Supplier ID chips
   - Findings preview

2. **Actions Tab**
   - List of all logged actions
   - Action type (parameter_change, maintenance, process_change)
   - Expected vs actual impact
   - Follow-up date warnings

3. **Summary Tab**
   - Today's date
   - Count cards (Active, Actions, Follow-ups)
   - Active investigations list
   - Pending follow-ups list (highlighted in red)
   - Today's actions list

---

## API Endpoints

For developers who want to integrate with the memory system:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/memory/summary` | GET | Overall memory statistics |
| `/api/memory/investigations` | GET | List investigations (filters: machine_id, supplier_id, status) |
| `/api/memory/actions` | GET | List actions (filter: machine_id) |
| `/api/memory/shift-summary` | GET | Generate shift handoff summary |

### Example API Calls

```bash
# Get memory summary
curl http://localhost:8000/api/memory/summary

# Get open investigations
curl "http://localhost:8000/api/memory/investigations?status=open"

# Get actions for a specific machine
curl "http://localhost:8000/api/memory/actions?machine_id=CNC-001"

# Get shift summary
curl http://localhost:8000/api/memory/shift-summary
```

---

## Memory Tools (Chat System)

The AI agent has access to these memory tools:

| Tool | Purpose |
|------|---------|
| `save_investigation` | Create new investigation record |
| `log_action` | Record user action with baseline metrics |
| `get_pending_followups` | Check for actions needing follow-up |
| `get_memory_context` | Retrieve relevant memory for machine/supplier |

These tools are automatically called based on conversation context.

---

## Data Model

### Investigation

```json
{
  "id": "INV-20251126-112117",
  "title": "CNC-001 Quality Investigation",
  "machine_id": "CNC-001",
  "supplier_id": null,
  "status": "open",  // open, in_progress, resolved, closed
  "initial_observation": "Increased scrap rate on CNC-001",
  "findings": ["Tooling wear detected", "Vibration above threshold"],
  "hypotheses": ["Coolant flow insufficient"],
  "created_at": "2025-11-26T11:21:17.076685",
  "updated_at": "2025-11-26T14:35:22.123456"
}
```

### Action

```json
{
  "id": "ACT-20251126-112117",
  "description": "Adjusted spindle speed from 2000 to 1800 RPM",
  "action_type": "parameter_change",  // parameter_change, maintenance, process_change
  "machine_id": "CNC-001",
  "baseline_metrics": {
    "oee": 0.72,
    "scrap_rate": 0.08
  },
  "expected_impact": "5% reduction in scrap rate",
  "actual_impact": "Scrap rate reduced to 3.5%",
  "follow_up_date": "2025-11-29",
  "created_at": "2025-11-26T11:21:17.387617"
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Memory not persisting | Verify `STORAGE_MODE="azure"` in `.env` |
| Investigation not showing | Check Azure Blob Storage connection |
| Memory Panel empty | Run a chat query that creates memory first |
| Follow-ups not detected | Ensure follow_up_date is set and has passed |
| "Memory service requires azure" warning | Set `STORAGE_MODE="azure"` (not "local") |

---

## Key Value Propositions

1. **Institutional Memory**: Context persists across sessions, users, and time
2. **Impact Tracking**: Measure whether changes actually worked
3. **Shift Continuity**: Seamless handoffs with comprehensive summaries
4. **Proactive Reminders**: Nothing falls through the cracks
5. **Audit Trail**: Full history of investigations and actions

---

## Quick Demo Script (5 minutes)

For a fast memory demo:

1. **Create Investigation** (1 min)
   ```
   CNC-001 has high scrap rates. Create an investigation to track this.
   ```

2. **Log Action** (1 min)
   ```
   I adjusted the spindle speed from 2000 to 1800 RPM. Current OEE is 72%. Log this action.
   ```

3. **Show Memory Panel** (1 min)
   - Click brain icon
   - Show Investigation tab
   - Show Actions tab

4. **Shift Summary** (1 min)
   ```
   Generate a shift summary for night shift.
   ```

5. **Check Follow-ups** (1 min)
   ```
   What investigations are open? Any pending follow-ups?
   ```

---

*For the full demo including dashboards and traceability, see [demo-script.md](demo-script.md)*
