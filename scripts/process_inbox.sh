#!/bin/bash
# Digital FTE - Auto Process Inbox Script
# Called by cron to process pending items

# Configuration
VAULT_PATH="/Volumes/Macintosh HD/DigitalFTE/AI_Employee_Vault"
LOG_FILE="/tmp/digital-fte-cron.log"
LOCK_FILE="/tmp/digital-fte-process.lock"

# Prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
    echo "$(date -Iseconds) - Process already running, skipping" >> "$LOG_FILE"
    exit 0
fi

# Create lock file
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Check if there are pending items
PENDING_COUNT=$(ls -1 "$VAULT_PATH/Needs_Action"/*.md 2>/dev/null | grep -v "Needs_Action.md" | wc -l | tr -d ' ')

if [ "$PENDING_COUNT" -eq 0 ]; then
    echo "$(date -Iseconds) - No pending items" >> "$LOG_FILE"
    exit 0
fi

echo "$(date -Iseconds) - Processing $PENDING_COUNT pending item(s)" >> "$LOG_FILE"

# Run Claude to process items
cd "/Volumes/Macintosh HD/DigitalFTE"
claude --print "Process all items in AI_Employee_Vault/Needs_Action following Company_Handbook.md rules. Update Dashboard when done." >> "$LOG_FILE" 2>&1

echo "$(date -Iseconds) - Processing complete" >> "$LOG_FILE"
