# Needs Action

> [!pending] Pending Items
> These items are awaiting processing by Claude.

---

## Pending Items

```dataview
TABLE WITHOUT ID
  file.link as "Action File",
  original_name as "Original File",
  priority as "Priority",
  detected as "Detected"
FROM "Needs_Action"
WHERE status = "pending" AND file.name != "Needs_Action"
SORT priority DESC, detected ASC
```

---

## How to Process

### Manual Processing
```bash
claude "Process all items in AI_Employee_Vault/Needs_Action"
```

### Using Skills
```bash
claude /process-inbox
```

---

## Priority Legend

| Priority | Meaning |
|----------|---------|
| **HIGH** | Urgent, invoice, payment, contract keywords |
| **MEDIUM** | Large files (>10MB) |
| **NORMAL** | Standard processing |

---

[[Home|← Back to Home]] | [[Dashboard|📊 Dashboard]] | [[Done|✅ Completed]]
