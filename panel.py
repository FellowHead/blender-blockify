import bpy


class BlockifyPanel(bpy.types.Panel):
    bl_idname = "TEST_PT_Panel"
    bl_label = "Blockify Panel"
    bl_category = "Blockify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        mytool = scene.blockify

        layout.prop(mytool, "block_size", text="Block size")
        layout.prop(mytool, "divide_by_vector", text="Invert block size")

        layout.prop(mytool, "precision", text="Precision")

        layout.prop(mytool, "overwrite_destination_mesh",
                    text="Overwrite mesh")
        row = layout.row()
        row.enabled = mytool.overwrite_destination_mesh
        row.prop(mytool, "destination_mesh", text="Destination mesh")
        layout.prop(mytool, "frame_start", text="Start frame")
        layout.prop(mytool, "frame_end", text="End frame")

        layout.prop(mytool, "cache_path")

        layout.operator("object.blockify",
                        text="Blockify selected object")
