# Fusion 360 MCP Specification (High-Level)

## Purpose

Expose Fusion 360's API capabilities (Design, CAM, Mesh, Sheet Metal) as structured MCP tools so agents can:

- Open / modify designs
- Automate parameter sweeps
- Generate CAM setups + toolpaths + G-code
- Export meshes (STL/OBJ) for additive workflows
- Create + unfold sheet metal parts (DXF for fabrication)

Fusion stays the execution engine (must be open, add-in loaded). MCP is the controller.

## System Architecture

### Fusion Add-in (Python)

- Runs inside Fusion 360
- Uses `adsk.core`, `adsk.fusion`, `adsk.cam`, `adsk.mesh`, `adsk.sheetmetal`
- Implements command handlers, exposes JSON RPC (local socket / pipe)

### MCP Server (Python or Node)

- Defines tool schemas and validates inputs
- Talks to Fusion add-in via RPC
- Returns structured results + downloadable artifacts (STL, DXF, NC, PNG)

## Core Tool Categories

### 1. Document & Parameters

- `fusion.open_document(path)`
- `fusion.list_parameters(doc_id)`
- `fusion.set_parameters(doc_id, updates[])`

**Documentation:**
- Scripts & Add-ins overview

### 2. Mesh / Export

- `fusion.export_mesh(doc_id, ref, format)` (STL, OBJ, 3MF)
- `fusion.snapshot_view(doc_id, view, w, h)` → PNG for human approval

**Documentation:**
- Fusion API Overview – Design & Mesh

### 3. CAM (Manufacture)

- `fusion.generate_cam_setup(doc_id, setup_type, stock, origin)`
- `fusion.create_operation(setup_id, operation, tool, geometry, passes, feeds)`
- `fusion.generate_toolpaths(scope)`
- `fusion.post_process(setup_id, ops[], post, program_name, output_dir)`

**Documentation:**
- Manufacture API overview
- Generate toolpaths sample
- Post processing reference

### 4. Sheet Metal

- `fusion.create_sheet_metal_rule(material, thickness, bend_radius, k_factor, relief_type)`
- `fusion.list_sheet_metal_rules()`
- `fusion.convert_body_to_sheet_metal(doc_id, body_id, rule_id)`
- `fusion.create_flange(face_id, length, angle)`
- `fusion.create_flat_pattern(component_id)` → DXF/STEP

**Documentation:**
- Fusion API Overview – Sheet Metal Manager & Rules
- Fusion Help – Sheet Metal workflows

## Rules & Constraints

### Mesh

- **Supported formats:** STL, OBJ, 3MF export
- **Resolution:** Can be controlled (low/med/high/custom)
- **Scope:** Only exports bodies/components (not entire assemblies in one go)

### CAM

- **Operations:** Supports 2D & 3D operations (pocket, contour, adaptive, drill, turning ops)
- **Setup requirement:** Requires a setup (milling/turning)
- **Tool libraries:** Tool assignment from local/cloud libraries
- **Toolpath regeneration:** Can regenerate toolpaths (`generateToolpath` or `generateAll`)
- **Post-processing:** Requires valid `.cps` post processor
- **Limitations:** No API for arbitrary custom toolpath point-by-point programming (must use Fusion ops/templates)

### Sheet Metal

- **Conversion requirement:** Must apply a `SheetMetalRule` to convert solids
- **Rule parameters:**
  - Thickness
  - Bend radius
  - K-factor / bend allowance
  - Relief types (rectangular, round, tear)
- **Flat patterns:** Can be generated & exported (typically DXF for fabrication)
- **API limitations:** Some advanced features (lofted flanges, specific corner reliefs) aren't exposed in API
- **Export support:** Flat pattern export is supported via `ExportManager`

## Safety & Guardrails

- **Communication:** Local-only communication (pipe/socket)
- **Testing:** Dry-run flags for posting/exports
- **Confirmation:** Confirmation required for G-code posting
- **Units:** Unit normalization (always echo back mm/inch)
- **Throttling:** Operation limits (max ops per request)

## Known Limitations

- **Runtime requirement:** Fusion must be running (no headless mode)
- **Documentation gaps:** CAM API is powerful but unevenly documented
- **API maturity:** Sheet metal API has fewer high-level helpers than solids or CAM
- **User intervention:** Some workflows require user intervention (e.g., complex constraints, advanced CAM ops)

## Example MCP Call Flow

```python
# Open document and set parameters
fusion.open_document("part.f3d")
fusion.set_parameters([{"name": "Thickness", "value": 3, "unit": "mm"}])

# Sheet metal workflow
fusion.convert_body_to_sheet_metal(body_id, rule_id)
fusion.create_flat_pattern(component_id)  # → DXF

# CAM workflow
fusion.generate_cam_setup("milling", stock="+2mm", origin="model_center")
fusion.create_operation("2d_pocket", tool="6mm_flat", feeds="...", passes="...")
fusion.generate_toolpaths()
fusion.post_process("grbl.cps", program_name="PART_001")  # → NC file

# Export for 3D printing
fusion.export_mesh(format="stl")  # → STL for 3DP
```

## Next Steps

The next step could be to expand this into a proper schema library: every tool with JSON `input_schema` and `output_schema`, plus references to the exact Fusion API classes (`adsk.fusion.SheetMetalRule`, `adsk.cam.Operation`, etc.).

Would you like me to take this spec and draft a JSON schema library (per MCP tool) so it's copy-paste usable inside an MCP server?