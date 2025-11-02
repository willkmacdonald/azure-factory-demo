# Development Workflow

This document describes the optimized development workflow for the Factory Agent project, designed to maximize efficiency while managing context usage in Claude Code.

---

## Overview

The workflow is organized into distinct phases with context clearing between phases to optimize token usage. Each phase has specific tools and agents to accomplish its goals efficiently.

---

## Phase 1: Planning

**Goal**: Create or update `implementation-plan.md` with PR-sized work chunks

### Tools & Agents
- Built-in **Plan** agent (for new features requiring exploration)
- **plan-manager** agent (for updating plan with review findings)
- Manual planning (for straightforward features)

### Process
1. **For new features**:
   ```
   Use Plan agent to explore codebase and create implementation strategy
   ```
   - Agent will use Explore, Grep, Read to understand existing code
   - Will break down feature into PR-sized chunks
   - Will write initial plan to `implementation-plan.md`

2. **For updates based on reviews**:
   ```
   Use plan-manager agent to update implementation-plan.md with [pr-reviewer/security-scanner] findings
   ```
   - Agent will read current plan structure
   - Will convert review findings into actionable tasks
   - Will organize by priority and assign to appropriate PRs
   - Will maintain clean plan structure

3. **For simple changes**:
   - Manually edit `implementation-plan.md`
   - Follow the PR structure template (see plan-manager agent for format)

### Output
- Updated `implementation-plan.md` with:
  - Current status summary
  - Active PR (in progress)
  - Planned PRs (prioritized)
  - Backlog (lower priority)
  - Completed PRs (archive)

---

## Phase 2: Context Clear

**Goal**: Save tokens before implementation

### Process
```
/clear
```

This resets the conversation context while preserving:
- All file changes made in Phase 1
- CLAUDE.md settings
- Agent configurations

**Why**: Starting implementation with fresh context ensures maximum available tokens for code reading, tool usage, and implementation.

---

## Phase 3: Implementation

**Goal**: Implement the current PR from `implementation-plan.md`

### Tools & Agents
- Built-in **Explore** agent (to familiarize with codebase)
- **deepcontext** MCP server (for semantic code search)
- **context7** MCP server (for library documentation - ALWAYS use)
- **azure-mcp** MCP server (for Azure-specific help)

### Process

#### Step 1: Familiarize with Codebase
```
Use Explore agent to understand [relevant part of codebase for this PR]
```

Or use deepcontext directly:
```
Search codebase for [relevant functionality] using deepcontext
```

**Explore agent benefits**:
- Fast, focused exploration
- Can specify thoroughness level: "quick", "medium", or "very thorough"
- Better than manual Grep/Glob for open-ended exploration

**deepcontext benefits**:
- Semantic search (understands meaning, not just keywords)
- Finds relevant code across multiple files
- Returns code chunks with context (imports, exports, symbols)

#### Step 2: Get Library Documentation
**ALWAYS use context7 for library documentation**:
```
Get latest documentation for [library] using context7
```

Examples:
- "Get FastAPI async route documentation from context7"
- "Get Pydantic validation documentation from context7"
- "Get React hooks documentation from context7"

#### Step 3: Get Azure-Specific Help
For Azure services, use azure-mcp:
```
Use azure-mcp to [Azure-specific task]
```

Examples:
- "Get Azure OpenAI best practices from azure-mcp"
- "Check Azure Container Apps deployment options"
- "Get Azure Blob Storage documentation"

#### Step 4: Implement Tasks
- Work through tasks in the current PR (from `implementation-plan.md`)
- Follow CLAUDE.md standards:
  - Type hints on all functions
  - Async/await for FastAPI routes
  - Synchronous I/O for CLI commands
  - Comprehensive error handling with logging
  - Pydantic models for validation
- Mark tasks as completed in your local tracking (not in implementation-plan.md yet)

#### Step 5: Commit Changes
When PR implementation is complete:
```
Create a git commit with the changes for PR[X]
```

Claude Code will:
- Run `git status` and `git diff` to see changes
- Draft appropriate commit message
- Create commit with co-authored-by tag

**Note**: Do NOT push to remote unless explicitly requested.

### Common Commands During Implementation
```bash
# Test changes
pytest
pytest tests/test_specific.py

# Format code
black src/ tests/

# Run the application
python -m src.main chat           # CLI mode
python run_dashboard.py           # Dashboard
uvicorn src.api:app --reload      # API (future)

# Check types (if using mypy)
mypy src/
```

---

## Phase 4: Context Clear

**Goal**: Save tokens before code review

### Process
```
/clear
```

**Why**: Code review agents need to read multiple files and provide detailed analysis. Starting with fresh context ensures enough tokens for comprehensive review.

---

## Phase 5: Code Review

**Goal**: Review implemented code for quality, compliance, and security

### Tools & Agents

#### Primary Review: pr-reviewer
```
Use pr-reviewer agent to review [files/feature] from PR[X]
```

**What pr-reviewer checks**:
- ✅ Type hints completeness
- ✅ Async/sync pattern correctness (FastAPI=async, CLI=sync)
- ✅ CLAUDE.md compliance (tech stack, frameworks, conventions)
- ✅ Code quality (error handling, logging, documentation)
- ✅ Simplicity assessment (appropriate for demo/prototype)
- ✅ Framework conventions (FastAPI, Typer, React)

**Output format**:
- Executive Summary
- Critical Issues (must fix)
- Important Improvements (should fix)
- Enhancement Opportunities (nice to have)
- Positive Highlights (what was done well)
- Quick Wins (top 3 changes for maximum impact)

#### Security Review: security-scanner (when needed)
```
Use security-scanner agent to scan [files/feature] for security vulnerabilities
```

**When to use**:
- After implementing authentication/authorization
- After adding new API endpoints
- After implementing database queries
- After adding file operations or user input handling
- Before deploying to production
- Periodically as part of security hygiene

**What security-scanner checks**:
- ❌ SQL injection, NoSQL injection, command injection
- ❌ XSS vulnerabilities
- ❌ Hardcoded secrets (API keys, passwords, tokens)
- ❌ Missing authentication/authorization
- ❌ Missing rate limiting
- ❌ Insecure password handling
- ❌ Path traversal vulnerabilities
- ❌ Sensitive data exposure in logs/responses
- ❌ Prompt injection (for LLM apps)
- ❌ Known dependency vulnerabilities

**Output format**:
- Security Assessment Summary (risk level)
- Critical Vulnerabilities (immediate fix)
- High Severity Issues (fix before production)
- Medium Severity Issues (address soon)
- Low Severity Issues (best practices)
- Positive Security Practices
- Quick Wins (top 3 security improvements)

### Review Strategy

**For all PRs**:
1. Run **pr-reviewer** (always)
2. Review findings and decide what to fix now vs later

**For security-sensitive PRs** (auth, API endpoints, DB queries):
1. Run **pr-reviewer** (code quality + compliance)
2. Run **security-scanner** (dedicated security analysis)
3. Address all Critical and High security findings before merge

**For demo/prototype work**:
- Fix all Critical issues (broken functionality, major violations)
- Fix Important/High issues when feasible
- Document Medium/Low issues if skipping (acceptable for demos)

**For production-bound work**:
- Fix ALL Critical and Important/High issues
- Address Medium issues before deployment
- Plan to address Low issues in future sprints

---

## Phase 6: Update Plan

**Goal**: Incorporate review findings into `implementation-plan.md`

### Tools & Agents
- **plan-manager** agent

### Process

#### For review findings that need immediate fixes:
```
Use plan-manager agent to update implementation-plan.md with pr-reviewer findings as a new high-priority PR
```

The agent will:
- Read current plan structure
- Parse review findings by severity
- Create new PR section for fixes (or add to existing PR if related)
- Organize tasks by priority
- Provide effort estimates

#### For findings that can be deferred:
```
Use plan-manager agent to add pr-reviewer enhancement suggestions to backlog
```

#### For completed work:
```
Use plan-manager agent to mark PR[X] as completed
```

The agent will:
- Mark all tasks as [x] completed
- Move PR to "Completed PRs" archive with date
- Update "Current Status" summary

### Output
- Updated `implementation-plan.md` with:
  - New PR(s) for critical/important fixes
  - Backlog items for enhancements
  - Completed PR moved to archive

---

## Phase 7: Context Clear

**Goal**: Save tokens before next PR implementation

### Process
```
/clear
```

**Why**: Starting next PR with fresh context optimizes token usage for the next implementation cycle.

---

## Phase 8: Next PR

**Goal**: Begin next PR from `implementation-plan.md`

### Process
Return to **Phase 3: Implementation** with the next PR.

---

## Workflow Summary (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Planning                                           │
│ • Use Plan agent / plan-manager / manual editing           │
│ • Create/update implementation-plan.md                      │
│ • Output: Organized plan with PR-sized chunks              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Context Clear                                      │
│ • Run: /clear                                               │
│ • Save tokens for implementation phase                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Implementation                                     │
│ • Use Explore agent + deepcontext to familiarize           │
│ • Use context7 for library docs (ALWAYS)                   │
│ • Use azure-mcp for Azure help                             │
│ • Implement current PR tasks                                │
│ • Create git commit                                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Context Clear                                      │
│ • Run: /clear                                               │
│ • Save tokens for review phase                              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Code Review                                        │
│ • Use pr-reviewer (always)                                  │
│ • Use security-scanner (for security-sensitive code)       │
│ • Review findings, decide what to fix                       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Update Plan                                        │
│ • Use plan-manager to add findings to plan                 │
│ • Create new PRs for critical/important fixes              │
│ • Mark current PR as completed                              │
│ • Add enhancements to backlog                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: Context Clear                                      │
│ • Run: /clear                                               │
│ • Save tokens for next PR                                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 8: Next PR                                            │
│ • Return to Phase 3 with next PR from plan                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Agent Usage

| Agent | When to Use | Primary Purpose |
|-------|-------------|-----------------|
| **Plan** | Phase 1 | Explore codebase and create implementation strategy for new features |
| **Explore** | Phase 3 | Quick codebase familiarization before implementation |
| **pr-reviewer** | Phase 5 | Comprehensive code review (quality + compliance + simplicity) |
| **security-scanner** | Phase 5 | Dedicated security vulnerability scanning |
| **plan-manager** | Phase 1, 6 | Create/update implementation-plan.md with tasks and findings |

---

## Quick Reference: MCP Servers

| MCP Server | When to Use | Primary Purpose |
|------------|-------------|-----------------|
| **context7** | Phase 3 (ALWAYS) | Get up-to-date library documentation and code examples |
| **deepcontext** | Phase 3 | Semantic code search to understand existing implementation |
| **azure-mcp** | Phase 3 | Azure-specific documentation, best practices, and help |

---

## Tips for Efficient Workflow

### Context Management
- **Clear aggressively**: Don't hesitate to clear context between phases
- **Front-load exploration**: Use Explore agent early to understand code before implementing
- **Batch related work**: Group related tasks in same PR to minimize context switches

### Code Review Strategy
- **Always run pr-reviewer**: Catches quality, compliance, and simplicity issues in one pass
- **Run security-scanner for sensitive code**: Auth, API endpoints, DB queries, file operations
- **Fix Critical issues immediately**: Don't accumulate critical debt
- **Defer enhancements strategically**: Add to backlog, address in future PRs

### Planning Strategy
- **Keep PRs small**: 2-8 related tasks per PR (easier to review, faster to complete)
- **Prioritize ruthlessly**: Critical → High → Medium → Low
- **Group logically**: Related tasks together (e.g., all auth fixes in one PR)
- **Update plan frequently**: After every review, update plan with findings

### Using Agents Effectively
- **Be specific with agent requests**: "Review async chat endpoint in main.py:145-200" vs "Review main.py"
- **Provide context to agents**: "This is a demo project, prioritize simplicity over robustness"
- **Read agent output carefully**: Agents provide file:line references - use them for quick fixes
- **Trust agent findings**: Agents are calibrated to CLAUDE.md standards

### Git Workflow
- **Commit after each PR**: One commit per PR keeps history clean
- **Don't push unless asked**: Local commits are fine, push only when ready
- **Use descriptive commit messages**: Claude Code will generate good ones from git diff
- **Create PR when ready**: Use `gh pr create` for pull requests when work is ready for review

---

## Common Scenarios

### Scenario 1: Starting New Feature
```
Phase 1: Use Plan agent to explore codebase and create implementation plan
Phase 2: /clear
Phase 3: Use Explore + context7 + azure-mcp to implement
Phase 4: /clear
Phase 5: Use pr-reviewer to review
Phase 6: Use plan-manager to mark PR complete and add any follow-ups
Phase 7: /clear
Phase 8: Next PR or new feature
```

### Scenario 2: Implementing Security Fixes
```
Phase 1: Use plan-manager to create security PR from security-scanner findings
Phase 2: /clear
Phase 3: Implement security fixes
Phase 4: /clear
Phase 5: Use pr-reviewer AND security-scanner to verify fixes
Phase 6: Use plan-manager to mark PR complete
Phase 7: /clear
Phase 8: Next PR
```

### Scenario 3: Quick Bug Fix
```
Phase 1: Manually add task to implementation-plan.md (no agent needed)
Phase 2: /clear
Phase 3: Fix bug (may skip Explore if familiar with code)
Phase 4: /clear
Phase 5: Use pr-reviewer to verify fix didn't introduce issues
Phase 6: Use plan-manager to mark task complete
Phase 7: /clear
Phase 8: Next PR
```

---

## Anti-Patterns to Avoid

❌ **Don't skip context clearing**: Leads to token exhaustion mid-task
❌ **Don't skip code review**: Catches issues early, cheaper to fix now than later
❌ **Don't batch too many PRs**: Review findings accumulate, plan gets stale
❌ **Don't skip security review for auth/API code**: Security issues expensive to fix in production
❌ **Don't ignore Critical findings**: Technical debt compounds quickly
❌ **Don't update plan manually after reviews**: Use plan-manager to maintain consistency
❌ **Don't explore without agent help**: Manual exploration wastes tokens, agents are optimized

---

## Adapting the Workflow

### For Production Projects
- Run security-scanner on EVERY PR
- Fix ALL Critical and High findings before merge
- Add comprehensive tests
- Add monitoring/logging
- Document security decisions

### For Quick Prototypes
- Can skip Phase 1 planning (manual task list)
- Can combine Phases 3-5 (implement + review without clearing)
- Can defer Medium/Low findings to backlog
- Focus on Critical issues only

### For Large Features
- Break into multiple related PRs
- Use Plan agent extensively in Phase 1
- Consider creating feature branch for multiple PRs
- Review incrementally (each PR) rather than at end

---

## Questions?

For questions about:
- **Agent usage**: Check agent description in `.claude/agents/[agent-name].md`
- **CLAUDE.md standards**: Review `.claude/CLAUDE.md` for project-specific rules
- **Git workflow**: See AGENTS.md for commit and PR guidelines
- **Testing**: See AGENTS.md for testing guidelines

For feedback on this workflow, create an issue at: https://github.com/anthropics/claude-code/issues
