# Create Plan Skill

Creates structured multi-step action plans when items require complex processing.

## Trigger
- Run manually: `claude /create-plan "task description"`
- Called by process-inbox when multi-step processing is needed
- Called when human guidance is requested

## When to Create a Plan

A plan should be created when:
1. Task requires more than 3 distinct steps
2. Task spans multiple files or systems
3. Task requires human approval at intermediate steps
4. Task has dependencies between steps
5. Task is complex enough to benefit from checkboxes

## Workflow

### Step 1: Analyze the Task
1. Read the action file or task description
2. Identify all required steps
3. Determine dependencies between steps
4. Identify steps requiring human approval

### Step 2: Structure the Plan
1. Create a logical sequence of steps
2. Group related steps together
3. Mark approval gates clearly
4. Estimate complexity of each step

### Step 3: Generate Plan File
Create a new file in `/AI_Employee_Vault/Plans/` with format:
`PLAN_{task_name}_{YYYY-MM-DD_HH-MM-SS}.md`

### Step 4: Link to Source
If plan was created from an action file:
1. Update the action file with plan reference
2. Keep action file in /Needs_Action until plan completes

### Step 5: Update Dashboard
Add the new plan to the Active Plans section.

## Plan Template

```markdown
---
created: {ISO timestamp}
source: {action file path or "manual"}
status: pending
priority: {high|medium|normal}
steps_total: {count}
steps_completed: 0
---

# Plan: {Descriptive Title}

## Objective
{Clear description of what this plan accomplishes}

## Context
- **Source**: {Original file or request}
- **Priority**: {Priority level with reason}
- **Created**: {Timestamp}

## Steps

### Phase 1: {Phase Name}
- [ ] Step 1.1: {Description}
- [ ] Step 1.2: {Description}

### Phase 2: {Phase Name}
- [ ] Step 2.1: {Description}
- [ ] **[APPROVAL REQUIRED]** Step 2.2: {Description requiring human approval}

### Phase 3: Completion
- [ ] Update Dashboard
- [ ] Move files to /Done
- [ ] Log completion

## Approval Gates
List any steps that require human approval before proceeding.

| Step | Reason | Status |
|------|--------|--------|
| 2.2 | {reason} | Pending |

## Notes
{Additional context, constraints, or considerations}

## Progress Log
| Time | Step | Status | Notes |
|------|------|--------|-------|
| {timestamp} | Created | Plan initialized | |

---
*Plan created by AI Employee*
```

## Plan States

| Status | Description |
|--------|-------------|
| pending | Plan created, not yet started |
| in_progress | At least one step completed |
| blocked | Waiting for human approval |
| completed | All steps done |
| cancelled | Plan abandoned |

## Example: Invoice Processing Plan

```markdown
---
created: 2026-02-08T10:30:00Z
source: /Needs_Action/ACTION_invoice_client_a.md
status: pending
priority: high
steps_total: 6
steps_completed: 0
---

# Plan: Process and Send Invoice to Client A

## Objective
Generate January invoice for Client A and send via email.

## Context
- **Source**: WhatsApp request from Client A
- **Priority**: High (invoice keyword detected)
- **Created**: 2026-02-08T10:30:00Z

## Steps

### Phase 1: Preparation
- [ ] Verify client details in contacts
- [ ] Calculate invoice amount from rates

### Phase 2: Generation
- [ ] Generate invoice PDF
- [ ] **[APPROVAL REQUIRED]** Review invoice before sending

### Phase 3: Delivery
- [ ] Send invoice via email
- [ ] Log transaction

### Phase 4: Completion
- [ ] Update Dashboard
- [ ] Move to /Done

## Approval Gates
| Step | Reason | Status |
|------|--------|--------|
| Review invoice | Financial document | Pending |

## Notes
- Client A rates: $150/hour
- January hours: 10 hours
- Total: $1,500

## Progress Log
| Time | Step | Status | Notes |
|------|------|--------|-------|
| 10:30 | Created | Plan initialized | From WhatsApp request |

---
*Plan created by AI Employee*
```

## Usage

```bash
# Create a plan from description
claude /create-plan "Prepare quarterly tax documents"

# Create a plan from an action file
claude /create-plan --from /Needs_Action/ACTION_complex_task.md

# Create a plan with specific priority
claude /create-plan "Urgent client request" --priority high
```

## Error Handling

### Invalid Task Description
If task is too vague:
- Create a clarification plan
- First step: "Gather more information about requirements"

### Plan Already Exists
If similar plan exists:
- Link to existing plan
- Ask if should create new or update existing

### Write Error
If plan file can't be created:
- Log error to /Logs
- Keep task in /Needs_Action
- Add alert to Dashboard
