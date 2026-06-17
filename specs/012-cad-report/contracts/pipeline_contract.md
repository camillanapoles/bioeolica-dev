# Contract: CAD+REPORT Pipeline Interface

## CLI Interface

```
usage: python -m src.cadreport.pipeline [-h] --params PARAMS --output-dir DIR

Generate complete engineering package: STEP + report + metadata.

options:
  -h, --help            show help
  --params PARAMS       Path to parameters JSON
  --output-dir DIR      Output directory for package
  --no-mesh             Skip Gmsh meshing
  --format {markdown,html,pdf}  Report format (default: markdown)
```

## Output Structure

```
{output-dir}/
├── model.step         # CAD geometry
├── model.msh          # GMSH mesh (optional)
├── report.md          # CRSLR engineering report
├── metadata.json      # Package metadata
└── checksums.sha256   # SHA-256 of all files
```

## Metadata JSON Schema

```json
{
  "package_id": "uuid",
  "model_id": "string",
  "generated_at": "ISO 8601",
  "step_checksum": "sha256",
  "mesh_checksum": "sha256 | null",
  "report_path": "string",
  "parameters": { "width": 100, "height": 50, "depth": 20, "material": "steel" },
  "dependencies": ["crslr", "cad"]
}
```
