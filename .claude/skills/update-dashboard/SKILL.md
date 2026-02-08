# Update Dashboard Skill

Updates the Dashboard.md file with current vault status and recent activity.

## Trigger
- Run manually: `claude /update-dashboard`
- Called automatically after process-inbox completes
- Can be scheduled independently

## Workflow

### Step 1: Count Items in Each Folder
1. Count files in `/AI_Employee_Vault/Inbox/` (excluding hidden files)
2. Count `.md` files in `/AI_Employee_Vault/Needs_Action/`
3. Count items in `/AI_Employee_Vault/Done/` completed today

### Step 2: Read Recent Activity from Logs
1. Open today's log file: `/AI_Employee_Vault/Logs/{YYYY-MM-DD}.json`
2. Parse the last 10 log entries
3. Format as table rows with Time, Action, Item, Status

### Step 3: Check for Active Plans
1. Scan `/AI_Employee_Vault/Plans/` for incomplete plans
2. Look for plans with unchecked items `- [ ]`
3. List each active plan with its status

### Step 4: Generate Alerts
Check for conditions requiring attention:
- High priority items pending > 1 hour
- Items that have failed processing (3+ retries)
- Large files awaiting review
- Unknown file types requiring guidance

### Step 5: Update Dashboard.md
Replace the content of `/AI_Employee_Vault/Dashboard.md` with:

```markdown
# AI Employee Dashboard

## Status
- **Last Updated**: {current ISO timestamp}
- **Inbox Items**: {inbox_count}
- **Pending Actions**: {needs_action_count}
- **Completed Today**: {done_today_count}

## Recent Activity
| Time | Action | Item | Status |
|------|--------|------|--------|
| {time} | {action} | {item} | {status} |
...

## Active Plans
- [ ] {plan_name} - {status}
...

## Alerts
- {alert_message}
...

---
*Dashboard auto-updated by AI Employee at {timestamp}*
```

## Dashboard Schema

### Status Section
| Field | Description |
|-------|-------------|
| Last Updated | ISO 8601 timestamp of last update |
| Inbox Items | Count of files in /Inbox |
| Pending Actions | Count of action files in /Needs_Action |
| Completed Today | Items moved to /Done today |

### Recent Activity Table
| Column | Description |
|--------|-------------|
| Time | HH:MM format |
| Action | Type of action (file_drop, processed, error) |
| Item | Filename or description |
| Status | Success, Error, Pending |

### Active Plans
Bullet list of plans from /Plans that have incomplete checkboxes.

### Alerts
Bullet list of items requiring human attention:
- High priority items waiting
- Processing errors
- Items needing human guidance

## Error Handling

### Missing Log File
If today's log doesn't exist:
- Display "No activity logged today" in Recent Activity
- Continue with other sections

### Corrupted Log Entry
If a log entry can't be parsed:
- Skip that entry
- Log warning but don't fail

### Permission Error
If Dashboard.md can't be written:
- Log error
- Attempt to create backup in /Logs

## Example Output

```markdown
# AI Employee Dashboard

## Status
- **Last Updated**: 2026-02-08T15:30:00Z
- **Inbox Items**: 2
- **Pending Actions**: 3
- **Completed Today**: 5

## Recent Activity
| Time | Action | Item | Status |
|------|--------|------|--------|
| 15:28 | Processed | report.pdf | Success |
| 15:25 | File drop | invoice_urgent.pdf | Pending |
| 15:20 | Processed | notes.txt | Success |

## Active Plans
- [ ] PLAN_quarterly_report_2026-02-08 - In Progress (2/5 steps complete)

## Alerts
- HIGH PRIORITY: invoice_urgent.pdf awaiting processing
- REVIEW NEEDED: large_file.zip (25MB) requires human review

---
*Dashboard auto-updated by AI Employee at 2026-02-08T15:30:00Z*
```

## Usage

```bash
# Update dashboard with current status
claude /update-dashboard

# Force refresh even if recently updated
claude /update-dashboard --force
```
