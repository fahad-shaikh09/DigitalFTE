# Plans

> [!info] Multi-Step Action Plans
> Complex tasks are broken down into trackable plans.

---

## Active Plans

```dataview
TABLE WITHOUT ID
  file.link as "Plan",
  status as "Status",
  steps_completed + "/" + steps_total as "Progress",
  priority as "Priority",
  created as "Created"
FROM "Plans"
WHERE status != "completed" AND file.name != "Plans"
SORT priority DESC, created DESC
```

---

## Completed Plans

```dataview
TABLE WITHOUT ID
  file.link as "Plan",
  steps_total as "Steps",
  created as "Created"
FROM "Plans"
WHERE status = "completed"
SORT created DESC
LIMIT 10
```

---

## Create New Plan

Use the template: [[Templates/Plan|📋 Plan Template]]

Or via Claude:
```bash
claude /create-plan "Your task description"
```

---

## Plan Status Legend

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `in_progress` | Currently working |
| `blocked` | Waiting for approval |
| `completed` | All steps done |

---

[[Home|← Back to Home]] | [[Dashboard|📊 Dashboard]]
