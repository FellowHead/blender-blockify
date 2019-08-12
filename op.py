import bpy
import bmesh

from mathutils import Vector

from . blocki import Blockify


class BlockifyOperator(bpy.types.Operator):
    bl_idname = "scene.run_blockify"
    bl_label = "Run object blockifier"
    bl_description = "Turn 'em into bloccs"

    _timer = None
    grid = None
    valid_objects = None
    obj = 0
    frame = 0
    dg = None
    coll = None

    def execute(self, context):
        self.grid = None

        if Blockify.COLLECTION_NAME not in bpy.data.collections:
            self.coll = bpy.data.collections.new(Blockify.COLLECTION_NAME)
            context.scene.collection.children.link(self.coll)
        else:
            self.coll = bpy.data.collections[Blockify.COLLECTION_NAME]

        self.valid_objects = []

        for obj in context.scene.objects:
            blk_obj = obj.blockify
            if blk_obj.enabled and self.coll not in obj.users_collection:
                self.valid_objects.append(obj)

        self.frame = context.scene.blockify.frame_start - 1
        self.obj = len(self.valid_objects)

        if self.obj == 0:
            print("No objects to blockify")
            return {'FINISHED'}

        # clear old meshes

        rm = []
        for mesh in bpy.data.meshes:
            if mesh.users == 0 and mesh.name.startswith("zzz_"):
                rm.append(mesh)
        for mesh in rm:
            bpy.data.meshes.remove(mesh)

        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.5, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            blk_glo = context.scene.blockify

            if self.obj >= len(self.valid_objects):
                self.obj = 0
                self.frame = self.frame + 1
                if self.frame > blk_glo.frame_end:
                    print("DONE ALL FRAMES")
                    self.cancel(context)
                    return {'FINISHED'}
                context.scene.frame_set(self.frame)
                self.dg = context.evaluated_depsgraph_get()

            obj = self.valid_objects[self.obj]
            blk_obj = obj.blockify
            if self.grid is None:
                blk = blk_obj if blk_obj.override_block_size else blk_glo
                block_size = Vector(blk.block_size)
                div = blk.divide_by_vector
                precision = blk_obj.precision

                if div:
                    block_size = Vector((
                        1 / block_size.x,
                        1 / block_size.y,
                        1 / block_size.z
                    ))

                self.grid = Blockify.compute_grid(
                    self.dg.objects[obj.name])
            else:
                name = "zzz_" + obj.name + "_" + str(self.frame)
                if name in bpy.data.meshes:
                    mesh = bpy.data.meshes[name]
                    mesh.materials.clear()
                else:
                    mesh = bpy.data.meshes.new(name)
                mesh.materials.append(blk_obj.material)
                Blockify.create_mesh(self.grid, mesh)

                name = "zzz_" + obj.name
                if name not in self.coll.objects:
                    self.coll.objects.link(bpy.data.objects.new(name, mesh))
                self.grid = None
                self.obj = self.obj + 1

        return {'PASS_THROUGH'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
