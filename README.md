# Digital FTE - Personal AI Employee

A local-first, autonomous AI assistant powered by Claude Code and Obsidian.

**Tier**: Bronze (Foundation)

## What This Does

Drop files into an inbox folder, and your AI Employee will:
- Detect new files automatically
- Analyze and categorize them
- Create action plans when needed
- Update a dashboard with status
- Move completed items to archive

## Prerequisites

| Component | Requirement | Installation |
|-----------|-------------|--------------|
| Claude Code | Active subscription | `npm install -g @anthropic/claude-code` |
| Python | 3.13+ | [python.org](https://python.org) |
| UV | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Obsidian | v1.10.6+ (optional) | [obsidian.md](https://obsidian.md) |

Verify installations:
```bash
claude --version
python3 --version
uv --version
```

## Quick Start

### 1. Clone and Setup

```bash
cd /Volumes/Macintosh\ HD/DigitalFTE

# Install dependencies with UV
uv sync

# Or install manually
uv add watchdog
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings (optional for Bronze tier)
nano .env
```

### 3. Verify Vault Structure

The vault is pre-created with all necessary folders:

```bash
ls AI_Employee_Vault/
# Inbox/  Needs_Action/  Done/  Plans/  Logs/  Dashboard.md  Company_Handbook.md
```

### 4. Start the File Watcher

```bash
# Run the file system watcher
uv run python watchers/filesystem_watcher.py

# Or in dry-run mode (no changes)
DRY_RUN=true uv run python watchers/filesystem_watcher.py
```

### 5. Process Items with Claude

```bash
# Process all pending items
claude --skill process-inbox

# Or run Claude in the vault directory
cd AI_Employee_Vault && claude
```

## Project Structure

```
DigitalFTE/
├── AI_Employee_Vault/        # Obsidian-compatible vault
│   ├── Inbox/                # Drop files here
│   ├── Needs_Action/         # Pending items
│   ├── Done/                 # Completed items
│   ├── Plans/                # Generated plans
│   ├── Logs/                 # Audit logs
│   ├── Dashboard.md          # Status overview
│   └── Company_Handbook.md   # Rules and preferences
├── watchers/                 # Python watcher scripts
│   └── filesystem_watcher.py
├── .claude/
│   └── skills/               # Agent skills
│       ├── process-inbox/
│       ├── update-dashboard/
│       └── create-plan/
├── AGENTS.md                 # Architecture documentation
├── README.md                 # This file
└── pyproject.toml            # Python dependencies
```

## Usage

### Dropping Files

Simply copy or move files into `AI_Employee_Vault/Inbox/`:

```bash
# Example: Drop a document
cp ~/Downloads/invoice.pdf AI_Employee_Vault/Inbox/

# The watcher will detect it and create an action file
```

### Processing Items

Run Claude to process pending items:

```bash
# From project root
claude "Process all items in AI_Employee_Vault/Needs_Action"

# Or use the skill directly
claude --skill process-inbox
```

### Checking Status

Open `AI_Employee_Vault/Dashboard.md` in Obsidian or any text editor to see:
- Current inbox count
- Pending actions
- Recent activity
- Active plans

### Viewing Logs

Audit logs are stored as JSON in `AI_Employee_Vault/Logs/`:

```bash
# View today's log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq
```

## Configuration

### Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to customize:

- **Processing rules**: How to handle different file types
- **Priority rules**: What triggers high/low priority
- **Response style**: How the AI should communicate
- **Boundaries**: What actions require approval

### Watcher Settings

Environment variables for `filesystem_watcher.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VAULT_PATH` | `./AI_Employee_Vault` | Path to vault |
| `CHECK_INTERVAL` | `5` | Seconds between checks |
| `DRY_RUN` | `false` | Log without acting |

## Development

### Running in Dev Mode

```bash
# Set dry run mode
export DRY_RUN=true

# Run watcher (logs but doesn't create files)
uv run python watchers/filesystem_watcher.py
```

### Testing

```bash
# Create a test file
echo "Test document" > AI_Employee_Vault/Inbox/test.txt

# Check if action file was created
ls AI_Employee_Vault/Needs_Action/
```

## Automation (Optional)

### Using cron (macOS/Linux)

```bash
# Edit crontab
crontab -e

# Add: Process inbox every 5 minutes
*/5 * * * * cd /Volumes/Macintosh\ HD/DigitalFTE && claude --skill process-inbox >> /tmp/ai-employee.log 2>&1
```

### Using PM2 (Keep Watcher Running)

```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start watchers/filesystem_watcher.py --interpreter python3

# Save for restart on reboot
pm2 save
pm2 startup
```

## Troubleshooting

### Watcher not detecting files

1. Check the watcher is running: `ps aux | grep filesystem_watcher`
2. Verify vault path is correct
3. Check file permissions on Inbox folder

### Claude not processing items

1. Ensure Claude Code is authenticated: `claude --version`
2. Check for items in `/Needs_Action`: `ls AI_Employee_Vault/Needs_Action/`
3. Review Company_Handbook.md for conflicting rules

### Missing logs

1. Check `/Logs` folder exists
2. Verify write permissions
3. Check watcher error output

## Edge Cases Handled

The filesystem watcher handles these edge cases:

| Edge Case | Solution |
|-----------|----------|
| Multiple files at once | Batch processing with queue |
| Large files being copied | Wait for file stability |
| Naming conflicts | Timestamp + counter suffix |
| Duplicate files | SHA-256 hash detection |
| Special characters | Filename sanitization |
| Watcher restarts | Scan existing files on startup |
| Partial writes | Size stability check |
| Hidden files (.DS_Store) | Automatic filtering |
| Empty files | Flagged for review |
| Permission errors | Graceful error logging |

## Roadmap

- [x] Bronze Tier: Foundation (current)
  - [x] Vault structure
  - [x] Documentation
  - [x] File System Watcher (with edge case handling)
  - [x] Agent Skills (process-inbox, update-dashboard, create-plan)
  - [x] Dashboard template
  - [x] Company Handbook template
  - [x] pyproject.toml for UV
  - [x] .env.example for configuration
  - [x] .gitignore for security
- [ ] Silver Tier: Functional Assistant
  - [ ] Gmail Watcher
  - [ ] MCP server integration
  - [ ] Human-in-the-loop approval
- [ ] Gold Tier: Autonomous Employee
  - [ ] Ralph Wiggum persistence loop
  - [ ] CEO Briefing generation
  - [ ] Multi-domain integration

## Resources

- [Claude Code Documentation](https://claude.com/product/claude-code)
- [Agent Skills Guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Obsidian Help](https://help.obsidian.md)

## License

MIT
