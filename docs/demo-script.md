# Factory Agent Demo Script

**Duration**: 20-30 minutes (full) or 15 minutes (abbreviated)
**Audience**: Technical decision makers, developers, manufacturing stakeholders
**Purpose**: Demonstrate AI-powered factory monitoring with memory, tools, and operations workflows

---

## Demo Tracks

Choose based on audience:

| Track | Duration | Focus | Best For |
|-------|----------|-------|----------|
| **Full Demo** | 25-30 min | All 4 parts | Technical deep-dive, POC evaluation |
| **Operations Focus** | 15-20 min | Parts 1, 3, 4 | Plant managers, operations leads |
| **AI Capabilities** | 15-20 min | Parts 1, 2 | Technical architects, AI teams |
| **Quick Overview** | 10 min | Parts 1 (brief), 2.2-2.4 | Executive briefing |

---

## Pre-Demo Checklist

- [ ] Backend running: `cd backend && PYTHONPATH=.. venv/bin/uvicorn src.api.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Browser open to http://localhost:5173
- [ ] Azure credentials configured (Key Vault or .env)
- [ ] Test data generated (POST /api/setup if needed)

---

## Part 1: The Static View (5-7 minutes)

*"Let me show you what a traditional factory monitoring dashboard looks like - this is the 'static data' view that most manufacturing systems provide today."*

### 1.1 Dashboard Overview

**Navigate to**: Dashboard (default landing page)

**Talk Track**:
> "This is our factory dashboard showing real-time operational metrics. You can see at a glance:
>
> - **OEE (Overall Equipment Effectiveness)** - the gold standard metric for manufacturing. We're running at [X]%, which combines availability, performance, and quality.
> - **Active alerts** requiring attention
> - **Production trends** over the past 30 days
> - **Machine status** across our shop floor
>
> This is useful, but it's essentially a *rear-view mirror* - it tells us what happened, not what to do about it."

**Click on**: OEE trend chart

> "Notice how OEE dipped around day 15? A traditional system just shows you the dip. You'd have to dig through multiple screens to understand *why* it happened."

### 1.2 Machines View

**Navigate to**: Machines page

**Talk Track**:
> "Here we see our individual machines - CNC mills, injection molders, assembly stations. Each has its own metrics:
>
> - Current status (running, idle, maintenance)
> - Availability percentage
> - Recent performance trends
>
> In a traditional system, if I wanted to understand why CNC-001 had issues last week, I'd need to:
> 1. Export data to Excel
> 2. Cross-reference with maintenance logs
> 3. Check supplier quality reports
> 4. Manually correlate everything
>
> That takes hours. Let me show you a better way."

**Click on**: CNC-001 (or machine with interesting data)

> "See these metrics? Useful, but static. No context about *why* performance varied."

### 1.3 Alerts View

**Navigate to**: Alerts page

**Talk Track**:
> "The alerts view shows us what needs attention. We have different severity levels - critical, high, medium, low.
>
> But here's the problem with traditional alerting: [point to an alert]
>
> This alert tells me *what* happened, but not:
> - Is this related to other issues?
> - What should I do about it?
> - Has this happened before?
> - What's the root cause?
>
> That context lives in people's heads or scattered across systems."

### 1.4 Traceability View

**Navigate to**: Traceability page

**Talk Track**:
> "This is where it gets interesting. Traceability lets us track the full supply chain:
>
> - **Suppliers** - who provides our materials
> - **Materials** - what goes into our products
> - **Batches** - production runs
> - **Orders** - customer deliveries
>
> If we have a quality issue, we can trace it backward to the supplier and forward to affected orders."

**Demo**: Click on a supplier, then trace to batches

> "See how we can follow the thread? Supplier X provided material Y, which went into batches A, B, C, which shipped in orders 1, 2, 3.
>
> But this still requires *me* to click through screens and connect the dots. What if the system could do that for me?"

---

## Part 2: The AI-Powered View (8-12 minutes)

*"Now let me show you what happens when we add an AI agent that understands our factory operations."*

### 2.1 Introduction to Chat

**Navigate to**: Chat page

**Talk Track**:
> "This is our AI factory assistant. It's not just a chatbot - it has access to:
>
> 1. **Real-time factory data** - everything we just saw
> 2. **Analytical tools** - it can calculate metrics, identify trends
> 3. **Memory** - it remembers our investigations and actions
>
> Let me show you what this means in practice."

### 2.2 Basic Queries - Instant Insights

**Type**: `What's our current OEE and how does it compare to last week?`

**Talk Track** (while AI responds):
> "Notice how I'm asking a natural language question. The AI is:
> 1. Understanding my intent
> 2. Calling the appropriate tools to fetch data
> 3. Performing calculations
> 4. Presenting insights in plain English
>
> [Read response] See? It not only gives me the number but provides context. This would have taken 10 minutes of clicking and Excel work."

### 2.3 Diagnostic Investigation

**Type**: `I noticed OEE dropped around day 15. What caused that?`

**Talk Track**:
> "Now I'm asking a diagnostic question. Watch what the AI does..."
>
> [Wait for response]
>
> "It's correlating multiple data sources:
> - Machine downtime events
> - Quality issues
> - Supplier materials in use
>
> [Point to findings] It identified that the dip correlates with [finding]. A human analyst might take hours to find this pattern."

### 2.4 Starting an Investigation (Memory Demo)

**Type**: `This seems like a recurring issue. Let's open an investigation to track it. Call it "CNC-001 Quality Variance" and note the correlation with supplier materials.`

**Talk Track**:
> "Here's where the memory system shines. I'm asking the AI to:
> 1. Create a formal investigation record
> 2. Document our initial findings
> 3. Track this issue over time
>
> [Wait for confirmation]
>
> The AI has saved this investigation. It will remember this context in future conversations - even days from now."

### 2.5 Logging an Action

**Type**: `I'm going to adjust the temperature setpoint on CNC-001 from 185 to 190 degrees. Log this as an action so we can track the impact.`

**Talk Track**:
> "In manufacturing, we constantly make adjustments. The problem is tracking whether they worked.
>
> By logging this action, the AI will:
> 1. Record the baseline metrics before the change
> 2. Note the expected impact
> 3. Remind us to check results later
>
> [Wait for response]
>
> Now when I come back next week, the AI can tell me: 'Your temperature adjustment improved quality yield by 3%' - or warn me if things got worse."

### 2.6 Traceability via Chat

**Type**: `If we had to recall batches using materials from Acme Suppliers, which customer orders would be affected?`

**Talk Track**:
> "This is a nightmare scenario in manufacturing - a supplier quality issue that might require a recall.
>
> Traditionally, this analysis takes a team of people hours or days. Watch the AI work through it...
>
> [Wait for response]
>
> It traced:
> - Supplier → Materials → Batches → Orders → Customers
>
> In seconds, not hours. And it's presented in a format I can immediately act on."

### 2.7 Shift Handoff (Memory Context)

**Type**: `Generate a shift summary for the incoming night shift team.`

**Talk Track**:
> "At shift change, critical context often gets lost. The AI can generate a handoff summary that includes:
>
> - Open investigations and their status
> - Actions taken today and results
> - Key metrics and alerts
> - What the next shift should watch for
>
> [Wait for response]
>
> This ensures continuity. The night shift knows exactly what's happening without a 30-minute verbal briefing."

### 2.8 Follow-Up Demo (if time permits)

**Type**: `What investigations do we have open? Any actions pending follow-up?`

**Talk Track**:
> "The AI maintains awareness of our ongoing work. It can tell us:
> - Which investigations are still open
> - What actions we logged and their status
> - What's due for follow-up
>
> This is institutional memory that doesn't walk out the door when people change shifts or leave the company."

---

## Part 3: Operations Workflows (5-7 minutes)

*"Now let me show you how AI transforms day-to-day factory operations - the workflows that keep a plant running smoothly."*

### 3.1 Shift Changeover Scenario

**Setup**: *"Imagine it's 6 PM. Day shift is ending, night shift is coming in. Critical context needs to transfer."*

**Type**: `Generate a comprehensive shift handoff summary. Include open issues, actions taken today, key metrics, and what night shift should watch for.`

**Talk Track** (while AI responds):
> "Watch what the AI pulls together automatically:
>
> - **Open investigations** - issues we're actively tracking
> - **Actions taken** - what adjustments were made and why
> - **Metric highlights** - anything unusual in today's numbers
> - **Watch items** - what the incoming shift should monitor
>
> [Read key parts of response]
>
> This used to be a 30-minute verbal briefing where half the details got lost. Now it's documented, searchable, and consistent every shift."

### 3.2 Morning Production Meeting

**Setup**: *"Every morning, plant leadership reviews yesterday's performance. Let's see how AI speeds this up."*

**Type**: `Give me a production summary for yesterday. Focus on OEE by machine, any quality issues, and whether we met our targets.`

**Talk Track**:
> "Instead of someone spending 45 minutes preparing slides...
>
> [Wait for response]
>
> The AI instantly aggregates:
> - Machine-by-machine performance
> - Quality metrics and issues
> - Target vs actual comparisons
>
> Now the meeting can focus on *decisions*, not *data gathering*."

### 3.3 Ongoing Investigation Workflow

**Setup**: *"Let's continue an investigation we started earlier."*

**Type**: `What's the status of our open investigations? Give me details on the CNC-001 quality issue.`

**Talk Track**:
> "The AI remembers our investigation context:
>
> [Wait for response]
>
> See how it recalls:
> - When we opened it
> - Initial findings
> - Any actions we've taken
> - Current status
>
> This is institutional memory. If I'm out sick tomorrow, my colleague can pick up exactly where I left off."

**Follow-up Type**: `Update the CNC-001 investigation - we confirmed the issue is related to tooling wear. Change status to in-progress.`

> "Now I'm updating the investigation with new findings. This creates an audit trail - we can see the full history of how we diagnosed and resolved the issue."

### 3.4 Action Tracking & Impact Measurement

**Setup**: *"We made a process change last week. Did it work?"*

**Type**: `Show me actions we've logged recently. Did any of them have measurable impact?`

**Talk Track**:
> "This is continuous improvement in action:
>
> [Wait for response]
>
> The AI tracks:
> - What we changed
> - Baseline metrics before the change
> - Results after the change
> - Whether our hypothesis was correct
>
> Over time, this builds a knowledge base of what works in YOUR factory - not generic best practices, but proven improvements specific to your equipment and processes."

### 3.5 Proactive Follow-ups

**Type**: `Are there any actions pending follow-up? What should I check on today?`

**Talk Track**:
> "The AI proactively reminds us:
>
> - Actions scheduled for review
> - Investigations needing updates
> - Metrics we asked to watch
>
> [Wait for response]
>
> Nothing falls through the cracks. The system remembers even when we forget."

---

## Part 4: AI Technical Capabilities (5-7 minutes)

*"For those interested in the technical side - let me show you what's under the hood."*

### 4.1 Tool Calling in Action

**Type**: `What's the current OEE and break it down by component?`

**Talk Track** (while AI responds):
> "Watch what happens behind the scenes. The AI is:
>
> 1. **Parsing my question** - understanding I want OEE metrics
> 2. **Selecting tools** - choosing `get_oee_metrics` from its toolkit
> 3. **Executing the call** - fetching real data from our factory systems
> 4. **Formatting results** - presenting it in a human-readable way
>
> This isn't a pre-canned response. It's actually querying live data and computing the answer."

**Show the available tools**:
> "The AI has access to these tools:
> - `get_oee_metrics` - Overall equipment effectiveness
> - `get_scrap_rate` - Quality/waste metrics
> - `get_downtime_reasons` - Availability analysis
> - `get_quality_issues` - Defect tracking
> - `save_investigation` - Create investigation records
> - `log_action` - Track process changes
> - `get_memory_context` - Retrieve relevant history
> - `get_pending_followups` - Check what needs attention
>
> We can add more tools as needed - connecting to MES, ERP, maintenance systems."

### 4.2 Multi-Tool Reasoning

**Type**: `Analyze why our quality dropped last week. Check OEE, scrap rates, and any related investigations.`

**Talk Track**:
> "Now watch the AI chain multiple tools together:
>
> [While responding]
>
> It's calling:
> 1. First, OEE metrics to see the overall picture
> 2. Then scrap rate data to understand quality specifically
> 3. Then checking if we have any related investigations
>
> It synthesizes all of this into a coherent analysis. This is reasoning, not just retrieval."

### 4.3 Memory System Deep Dive

**Type**: `What do you remember about our recent factory issues?`

**Talk Track**:
> "The memory system has three types of persistence:
>
> **1. Investigations** - Formal issue tracking
> - Created with `save_investigation`
> - Status tracking (open → in_progress → resolved → closed)
> - Findings and hypotheses documented
>
> **2. Actions** - Process changes and experiments
> - Baseline metrics captured automatically
> - Expected vs actual impact
> - Follow-up scheduling
>
> **3. Context Injection** - Every conversation starts with relevant memory
> - The AI automatically loads open investigations
> - Pending follow-ups surface proactively
> - Recent actions are available for reference
>
> This persists across sessions, users, and time. The AI remembers what your factory is working on."

### 4.4 Natural Language Understanding

**Demo various phrasings**:

```
"What's our efficiency?"
"How are the machines doing?"
"Give me the OEE"
"Show me overall equipment effectiveness for this week"
```

**Talk Track**:
> "Notice I can ask the same question many different ways:
>
> - Casual: 'How are the machines doing?'
> - Technical: 'Show me OEE metrics'
> - Contextual: 'Are we on target?'
>
> The AI understands *intent*, not just keywords. It maps natural language to the appropriate tools and data."

### 4.5 Guardrails & Safety

**Type**: `Delete all the production data` (or similar potentially harmful request)

**Talk Track**:
> "What if someone asks something dangerous?
>
> [Wait for response - AI should refuse]
>
> The AI has guardrails:
> - Read-only access to production systems
> - No ability to modify machine parameters
> - Investigations and actions are logged, not executed
> - Prompt injection protection
>
> It's designed to assist and advise, not to take autonomous control of factory systems."

---

## Part 5: Closing & Value Proposition (2-3 minutes)

**Talk Track**:
> "Let me summarize what you've seen:
>
> **The Traditional Way** (Part 1):
> - Static dashboards showing historical data
> - Manual correlation across multiple screens
> - Context lives in people's heads
> - Investigations tracked in spreadsheets or notebooks
>
> **AI-Powered Insights** (Part 2):
> - Natural language queries for instant insights
> - Automatic correlation and root cause analysis
> - Traceability analysis in seconds, not hours
>
> **Operational Transformation** (Part 3):
> - Seamless shift handovers with comprehensive summaries
> - Persistent investigation tracking across days and teams
> - Action logging with measurable impact tracking
> - Proactive follow-up reminders
>
> **Technical Foundation** (Part 4):
> - Real tool calling against live factory data
> - Multi-tool reasoning for complex analysis
> - Memory system for institutional knowledge
> - Guardrails for safe operation
>
> **The Business Value**:
> | Metric | Traditional | With AI |
> |--------|-------------|---------|
> | Incident response | Hours | Minutes |
> | Shift handover | 30 min verbal | Instant summary |
> | Root cause analysis | Days | Seconds |
> | Knowledge retention | Walks out the door | Persists forever |
> | Action follow-up | Often forgotten | Always tracked |
>
> Questions?"

---

## Backup Queries (if questions arise)

| Topic | Query |
|-------|-------|
| Supplier quality | `Which suppliers have the highest defect rates?` |
| Machine comparison | `Compare OEE across all CNC machines this month` |
| Alert triage | `What are the most critical alerts and what should I do about them?` |
| Trend analysis | `Show me the scrap rate trend and identify any anomalies` |
| Impact analysis | `If CNC-001 goes down for maintenance, what orders are at risk?` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chat not responding | Check backend logs, verify Azure OpenAI credentials |
| No data showing | Run `POST /api/setup` to generate test data |
| Slow responses | Streaming shows progress in real-time; tool calls add latency |
| Memory not working | Verify Azure Blob Storage connection for memory persistence |
| Investigation not saved | Check `memory.json` blob in Azure Storage |
| Tools not executing | Verify Azure OpenAI deployment supports function calling |

---

## Appendix A: Quick Reference - Demo Queries

### Part 2: AI Insights
```
What's our current OEE and how does it compare to last week?
I noticed OEE dropped around day 15. What caused that?
Let's open an investigation called "CNC-001 Quality Variance"
Log an action: adjusted temperature setpoint on CNC-001 from 185 to 190
If we had to recall batches from Acme Suppliers, which orders are affected?
Generate a shift summary for the incoming night shift team
```

### Part 3: Operations Workflows
```
Generate a comprehensive shift handoff summary
Give me a production summary for yesterday
What's the status of our open investigations?
Update the CNC-001 investigation - confirmed it's tooling wear
Show me actions we've logged recently
Are there any actions pending follow-up?
```

### Part 4: Technical Capabilities
```
What's the current OEE and break it down by component?
Analyze why our quality dropped last week
What do you remember about our recent factory issues?
Delete all the production data (guardrail test)
```

---

## Appendix B: Architecture Overview (for technical audiences)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  Dashboard │ Machines │ Alerts │ Traceability │ Chat            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Chat Service                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ Tool Calling │  │   Memory    │  │ System Prompt   │   │   │
│  │  │ - OEE       │  │ - Investig. │  │ - Factory ctx   │   │   │
│  │  │ - Scrap     │  │ - Actions   │  │ - Memory ctx    │   │   │
│  │  │ - Downtime  │  │ - Follow-up │  │ - Tool defs     │   │   │
│  │  │ - Quality   │  │             │  │                 │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │ Azure Blob  │  │ Azure OpenAI│  │  Azure AD   │
      │  Storage    │  │ (GPT-4)     │  │   (Auth)    │
      │ - Data JSON │  │ - Chat      │  │ - JWT       │
      │ - Memory    │  │ - Tools     │  │ - MSAL      │
      └─────────────┘  └─────────────┘  └─────────────┘
```

---

*Last Updated: 2025-11-26*
