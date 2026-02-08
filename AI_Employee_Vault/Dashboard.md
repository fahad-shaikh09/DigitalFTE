# AI Employee Dashboard

> [!tip] Quick Actions
> - [[Inbox|📥 Drop Files Here]] | [[Needs_Action|⚡ Pending Items]] | [[Done|✅ Completed]] | [[Plans|📋 Plans]]

---

## Status Overview

| Metric | Count |
|--------|-------|
| 📥 Inbox Items | `$= dv.pages('"Inbox"').where(p => !p.file.name.startsWith('.')).length` |
| ⚡ Pending Actions | `$= dv.pages('"Needs_Action"').where(p => p.status === 'pending').length` |
| ✅ Completed Today | `$= dv.pages('"Done"').where(p => p.file.cday.equals(dv.date('today'))).length` |
| 📋 Active Plans | `$= dv.pages('"Plans"').where(p => p.status !== 'completed').length` |

---

## Pending Items

> [!pending] Items Awaiting Processing

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  priority as "Priority",
  detected as "Detected",
  status as "Status"
FROM "Needs_Action"
WHERE status = "pending"
SORT priority DESC, detected ASC
```

---

## High Priority Alerts

> [!alert] Requires Immediate Attention

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  original_name as "File",
  detected as "Detected"
FROM "Needs_Action"
WHERE priority = "high" AND status = "pending"
SORT detected ASC
```

---

## Active Plans

```dataview
TABLE WITHOUT ID
  file.link as "Plan",
  status as "Status",
  steps_completed + "/" + steps_total as "Progress",
  created as "Created"
FROM "Plans"
WHERE status != "completed"
SORT created DESC
```

---

## Recently Completed

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  original_name as "File",
  processed as "Completed"
FROM "Done"
WHERE status = "completed"
SORT processed DESC
LIMIT 10
```

---

## Recent Activity Log

| Time | Action | Item | Status |
|------|--------|------|--------|
| 12:15 | Processed | FastAPI_A_Visual_Guide.pdf | Completed |
| 12:10 | File drop | FastAPI_A_Visual_Guide.pdf | Detected |
| 11:45 | Processed | test_task.txt | Completed |
| 11:32 | File drop | test_task.txt | Detected |
| 11:24 | System initialized | Dashboard.md | Ready |

---

> [!success] System Status
> **AI Employee**: Online
> **Last Updated**: 2026-02-08T12:15:00Z
> **Version**: Bronze Tier v1.0

---
*Dashboard powered by Digital FTE + Dataview*
