# Contract: CRSLR Input JSON Schema

```json
{
  "analysis_id": "uuid",
  "title": "string",
  "date": "ISO 8601",
  "domain": "string",
  "sections": {
    "context": { "content": "markdown", "priority": 1 },
    "results": { "content": "markdown", "priority": 2, "metrics": {} },
    "synthesis": { "content": "markdown", "priority": 3 },
    "limitations": { "content": "markdown", "priority": 4 },
    "recommendations": { "content": "markdown", "priority": 5 }
  },
  "vvv_status": "PASS|FAIL|PENDING",
  "uncertainty_interval": "95%",
  "references": ["string"]
}
```

## Output

- Markdown report (always)
- PDF (optional, via WeasyPrint)
