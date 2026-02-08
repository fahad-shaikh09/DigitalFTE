# Process Inbox Skill

Process all pending action files in the /Needs_Action folder according to Company Handbook rules.

## Trigger
- Run manually: `claude /process-inbox`
- Run via orchestrator when items exist in /Needs_Action
- Can be scheduled via cron

## Workflow

### Step 1: Scan for Pending Items
1. Read all `.md` files in `/AI_Employee_Vault/Needs_Action/`
2. Parse YAML frontmatter to extract metadata
3. Sort by priority (high > medium > normal) then by detection time

### Step 2: Load Processing Rules
1. Read `/AI_Employee_Vault/Company_Handbook.md`
2. Extract file type processing rules
3. Extract priority rules and boundaries

### Step 3: Process Each Item
For each action file:

1. **Validate the action file**
   - Check frontmatter is valid
   - Verify original file still exists in /Inbox
   - Check if already processed (status field)

2. **Determine action based on file type**
   Use the extension from frontmatter to lookup action in Company Handbook:
   - `.pdf`: Summarize content, extract key info
   - `.txt`: Read and categorize
   - `.csv`: Analyze data, create summary
   - `.jpg/.png`: Describe image if possible
   - `.docx/.xlsx`: Extract and summarize
   - `.md/.json`: Parse and summarize
   - Other: Log and flag for human review

3. **Execute processing**
   - Read the original file from /Inbox
   - Perform the appropriate analysis
   - Add processing notes to the action file

4. **Handle high priority items**
   - If priority is "high", add to Dashboard alerts
   - Consider creating a Plan if multi-step action needed

5. **Complete the item**
   - Update action file status to "completed"
   - Add completion timestamp
   - Move action file to /Done
   - Move original file to /Done
   - Update Dashboard.md with activity

### Step 4: Update Dashboard
After processing all items, run the update-dashboard skill.

## Error Handling

### File Not Found
If original file is missing:
1. Update action file with ERROR status
2. Add note explaining the issue
3. Move to /Done with ERROR_ prefix
4. Log error

### Processing Error
If analysis fails:
1. Keep file in /Needs_Action
2. Add error details to action file
3. Increment retry counter (max 3)
4. Flag for human review if max retries exceeded

### Unknown File Type
1. Log the file type
2. Create a plan requesting human guidance
3. Keep in /Needs_Action until resolved

## Output

After running, this skill will:
1. Process all valid items in /Needs_Action
2. Move completed items to /Done
3. Update Dashboard.md with activity
4. Log all actions to /Logs/{date}.json

## Example Usage

```bash
# Process all pending items
claude /process-inbox

# With verbose output
claude /process-inbox --verbose
```

## Vault Structure Reference

```
AI_Employee_Vault/
├── Inbox/              # Original dropped files
├── Needs_Action/       # Action files to process
│   └── ACTION_*.md     # Created by watcher
├── Done/               # Completed items
│   ├── ACTION_*.md     # Processed action files
│   └── [original files]
├── Plans/              # Multi-step plans
├── Logs/               # JSON audit logs
├── Dashboard.md        # Status overview
└── Company_Handbook.md # Processing rules
```
