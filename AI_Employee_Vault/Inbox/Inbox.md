# Inbox

> [!tip] Drop Zone
> Place files here for processing. The watcher will automatically detect them.

---

## How to Use

1. **Drag & drop** files into this folder
2. **Copy/paste** files from Finder
3. **Save directly** from applications

The file watcher monitors this folder and creates action items in [[Needs_Action]] automatically.

---

## Current Files

```dataview
TABLE WITHOUT ID
  file.link as "File",
  file.size as "Size",
  file.ctime as "Added"
FROM "Inbox"
WHERE file.name != "Inbox"
SORT file.ctime DESC
```

---

## Supported File Types

| Type | Extension | Processing |
|------|-----------|------------|
| Documents | .pdf, .docx, .txt | Summarize & categorize |
| Data | .csv, .xlsx, .json | Analyze structure |
| Images | .jpg, .png, .gif | Describe content |
| Markdown | .md | Extract action items |

---

[[Home|← Back to Home]] | [[Dashboard|📊 Dashboard]]
