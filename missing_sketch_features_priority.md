# Missing Sketch Features - Priority Implementation Order

## 🔥 **Priority 1: Essential Geometry (Immediate Need)**

### **Ellipses**
- `fusion.create_ellipse` - Center, major/minor axes, rotation
- Critical for mechanical design (bolt patterns, oval holes)

### **Slots** 
- `fusion.create_slot` - Start/end points with width
- Essential for mechanical fasteners and adjustment features

### **Construction Lines**
- `fusion.create_construction_line` - Infinite reference lines
- `fusion.create_construction_circle` - Reference circles
- Foundation for parametric design

### **3-Point Arcs**
- `fusion.create_arc_by_three_points` - More intuitive than center+angle
- Common workflow for tangent curves

## 🚀 **Priority 2: Advanced Constraints (High Impact)**

### **Tangent Constraints**
- `fusion.add_tangent_constraint` - Between curves and lines
- Critical for smooth transitions

### **Concentric Constraints**
- `fusion.add_concentric_constraint` - Align circle centers
- Essential for holes and bearing features

### **Horizontal/Vertical Constraints**
- `fusion.add_horizontal_constraint` - Lock to horizontal
- `fusion.add_vertical_constraint` - Lock to vertical
- Fundamental for precise alignment

### **Equal Constraints**
- `fusion.add_equal_constraint` - Make dimensions equal
- Key for symmetric designs

## 🎨 **Priority 3: Modification Operations (Workflow Enhancement)**

### **Trim/Extend**
- `fusion.trim_entities` - Cut lines at intersections
- `fusion.extend_entities` - Extend to boundaries
- Essential for cleanup operations

### **Fillet/Chamfer**
- `fusion.add_fillet` - Round corners with radius
- `fusion.add_chamfer` - Cut corners at angle
- Critical for manufacturing-ready designs

### **Offset**
- `fusion.offset_entities` - Create parallel curves
- Important for wall thickness, clearances

## 🔄 **Priority 4: Pattern Operations (Productivity)**

### **Rectangular Patterns**
- `fusion.create_rectangular_pattern` - Row/column arrays
- High productivity for repetitive features

### **Circular Patterns**
- `fusion.create_circular_pattern` - Radial arrays
- Essential for bolt circles, gear teeth

### **Mirror Operations**
- `fusion.mirror_entities` - Reflect across lines
- Critical for symmetric designs

## 📐 **Priority 5: Advanced Features (Professional)**

### **Sketch Text**
- `fusion.create_text` - Add text annotations
- Important for part marking, labels

### **Project Geometry**
- `fusion.project_geometry` - Project 3D edges to sketch
- Key for complex assemblies

### **Sketch Blocks**
- `fusion.create_block` - Reusable geometry groups
- Advanced productivity feature

## 📁 **Priority 6: Import/Export (Integration)**

### **DXF Import**
- `fusion.import_dxf` - Import CAD files
- Critical for legacy data integration

### **Image Import** 
- `fusion.import_sketch_image` - Reference images
- Useful for tracing existing designs

---

## 🎯 **Recommended Implementation Order:**

1. **Week 1**: Ellipses, Slots, Construction geometry
2. **Week 2**: Tangent, Concentric, Horizontal/Vertical constraints  
3. **Week 3**: Trim/Extend, Fillet/Chamfer, Offset
4. **Week 4**: Rectangular/Circular patterns, Mirror
5. **Week 5**: Text, Project geometry, advanced constraints
6. **Week 6**: Import/Export capabilities

This order prioritizes the most commonly used features that provide immediate value for real-world CAD workflows.
