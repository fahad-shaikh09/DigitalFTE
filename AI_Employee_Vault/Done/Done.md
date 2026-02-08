# Done

> [!success] Completed Items
> Successfully processed files are archived here.

---

## Recently Completed

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  original_name as "Original File",
  processed as "Completed",
  priority as "Priority"
FROM "Done"
WHERE status = "completed" AND file.name != "Done"
SORT processed DESC
LIMIT 20
```

---

## Statistics

| Metric | Count |
|--------|-------|
| Total Completed | `$= dv.pages('"Done"').where(p => p.status === 'completed').length` |
| Completed Today | `$= dv.pages('"Done"').where(p => p.file.cday.equals(dv.date('today'))).length` |
| This Week | `$= dv.pages('"Done"').where(p => p.file.cday >= dv.date('today').minus({days: 7})).length` |

---

## Completed by Priority

```dataview
TABLE WITHOUT ID
  priority as "Priority",
  length(rows) as "Count"
FROM "Done"
WHERE status = "completed"
GROUP BY priority
```

---

[[Home|← Back to Home]] | [[Dashboard|📊 Dashboard]] | [[Needs_Action|⚡ Pending]]
