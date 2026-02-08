# Digital FTE - Personal AI Employee

## Overview

This project implements a **Bronze Tier Personal AI Employee** - a local-first, autonomous assistant that monitors file drops and processes tasks using Claude Code as the reasoning engine and an Obsidian-compatible vault as the knowledge base.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BRONZE TIER ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      FILE DROP (User)                        │
│           Drop files into /Vault/Inbox folder                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              File System Watcher (Python)              │  │
│  │   - Uses watchdog library                              │  │
│  │   - Monitors /Inbox for new files                      │  │
│  │   - Creates .md action files in /Needs_Action          │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Local)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /Inbox/          - Drop zone for incoming files       │  │
│  │  /Needs_Action/   - Items requiring processing         │  │
│  │  /Done/           - Completed tasks                    │  │
│  │  /Plans/          - Claude's generated plans           │  │
│  │  /Logs/           - Audit trail                        │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  Dashboard.md     - Real-time status overview          │  │
│  │  Company_Handbook.md - Rules and preferences           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    CLAUDE CODE                         │  │
│  │   - Reads /Needs_Action for pending items              │  │
│  │   - Processes based on Company_Handbook.md rules       │  │
│  │   - Creates Plans in /Plans                            │  │
│  │   - Updates Dashboard.md                               │  │
│  │   - Moves completed items to /Done                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Agent Skills:                                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │ process-inbox   │ │ update-dashboard│ │ create-plan   │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Vault Structure

```
AI_Employee_Vault/
├── Inbox/                    # Drop zone for incoming files
├── Needs_Action/             # Items requiring Claude's attention
├── Done/                     # Completed/archived items
├── Plans/                    # Claude's generated action plans
├── Logs/                     # JSON audit logs
├── Dashboard.md              # Status overview
└── Company_Handbook.md       # Rules and preferences
```

### 2. File System Watcher

**Location**: `watchers/filesystem_watcher.py`

**Purpose**: Monitors the `/Inbox` folder and creates action files when new items are detected.

**Behavior**:
- Watches for file creation events in `/Inbox`
- Creates a corresponding `.md` file in `/Needs_Action` with metadata
- Copies the original file to `/Needs_Action` for processing
- Logs all events to `/Logs`

**Dependencies**:
- `watchdog` - File system monitoring
- `pathlib` - Path handling

### 3. Agent Skills

All AI functionality is implemented as Claude Code Agent Skills in `.claude/skills/`.

#### Skill: `process-inbox`

**Trigger**: Run manually or via orchestrator when items exist in `/Needs_Action`

**Behavior**:
1. Scan `/Needs_Action` for unprocessed items
2. Read `Company_Handbook.md` for processing rules
3. Analyze each item and determine required actions
4. Create a plan in `/Plans` if multi-step action needed
5. Execute simple actions directly
6. Update `Dashboard.md` with status
7. Move completed items to `/Done`

#### Skill: `update-dashboard`

**Trigger**: After any processing action

**Behavior**:
1. Count items in each folder
2. Read recent activity from `/Logs`
3. Update `Dashboard.md` with current status

#### Skill: `create-plan`

**Trigger**: When an item requires multi-step processing

**Behavior**:
1. Analyze the item and required actions
2. Create a structured plan with checkboxes
3. Save to `/Plans` with timestamp

### 4. Dashboard.md Schema

```markdown
# AI Employee Dashboard

## Status
- **Last Updated**: [timestamp]
- **Inbox Items**: [count]
- **Pending Actions**: [count]
- **Completed Today**: [count]

## Recent Activity
| Time | Action | Item | Status |
|------|--------|------|--------|
| ... | ... | ... | ... |

## Active Plans
- [ ] [Plan name] - [status]

## Alerts
- [Any items requiring attention]
```

### 5. Company_Handbook.md Schema

```markdown
# Company Handbook

## Identity
- **Name**: [Your AI Employee's name]
- **Role**: Personal Assistant

## Processing Rules

### File Types
| Extension | Action |
|-----------|--------|
| .pdf | Summarize content, extract key info |
| .txt | Read and categorize |
| .csv | Analyze data, create summary |
| .jpg/.png | Describe image content |

### Priority Rules
- Files with "urgent" in name: High priority
- Files with "invoice" in name: Flag for review
- Default: Normal priority

### Response Style
- Be concise and action-oriented
- Always update Dashboard after processing
- Log all actions to /Logs

## Boundaries
- Never delete original files without approval
- Flag financial items for human review
- Ask for clarification if instructions unclear
```

## Data Flow

```
1. USER drops file → /Inbox/document.pdf

2. WATCHER detects → creates /Needs_Action/FILE_document.pdf.md
   ---
   type: file_drop
   original_name: document.pdf
   size: 12345
   detected: 2026-02-08T10:00:00Z
   status: pending
   ---
   New file dropped for processing.

3. CLAUDE reads /Needs_Action, processes item
   - Reads Company_Handbook.md for rules
   - Analyzes document.pdf
   - Creates summary/actions

4. CLAUDE updates Dashboard.md
   - Increments completed count
   - Adds to recent activity

5. CLAUDE moves to /Done
   - /Done/FILE_document.pdf.md (with results)
   - /Done/document.pdf (original)

6. WATCHER logs event → /Logs/2026-02-08.json
```

## Orchestration

For Bronze tier, orchestration is manual or via simple cron:

### Manual Mode
```bash
# Process all pending items
claude --skill process-inbox

# Update dashboard only
claude --skill update-dashboard
```

### Scheduled Mode (cron)
```bash
# Check for new items every 5 minutes
*/5 * * * * cd /path/to/vault && claude --skill process-inbox
```

## Future Tiers

### Silver Tier Additions
- Gmail Watcher
- WhatsApp Watcher
- MCP servers for external actions
- Human-in-the-loop approval workflow
- Automated scheduling

### Gold Tier Additions
- Ralph Wiggum persistence loop
- Multiple MCP servers
- CEO Briefing generation
- Error recovery
- Comprehensive audit logging

## Security Considerations

- Vault is local-only (no cloud sync for Bronze)
- No credentials stored in vault
- All actions logged for audit
- No auto-delete without approval
