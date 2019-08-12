# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
import mathutils

from mathutils import Vector

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import (
    Panel,
    Operator,
    AddonPreferences,
    PropertyGroup,
)

from . op import BlockifyOperator
from . panel import ObjectBlockifyPanel, GlobalBlockifyPanel
from . blocki import Blockify

bl_info = {
    "name": "blockify",
    "author": "FellowHead",
    "description": "Blockify any object",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}


class ObjectSettings(PropertyGroup):
    enabled: BoolProperty(
        name="Enable/Disable",
        description="Toggle wether to use Blockify on this object",
        default=False
    )

    block_size: FloatVectorProperty(
        name="Block size",
        description="Configure the block size",
        default=Vector((1, 1, 1))
    )

    divide_by_vector: BoolProperty(
        name="Divide by vector",
        description="Use (1.0 / [block size]) as actual size",
        default=False
    )

    override_block_size: BoolProperty(
        name="Override block size",
        description="duh",
        default=True
    )

    precision: IntProperty(
        name="Precision",
        description="""Amount of pre-subdivisions.
Increase this value if you happen to find holes in the blockified mesh""",
        default=0,
        min=0,
        max=10
    )

    mat_main: PointerProperty(
        name="Material",
        description="",
        type=bpy.types.Material
    )

    mat_top: PointerProperty(
        name="Material",
        description="",
        type=bpy.types.Material
    )

    mat_side: PointerProperty(
        name="Material",
        description="",
        type=bpy.types.Material
    )

    mat_bottom: PointerProperty(
        name="Material",
        description="",
        type=bpy.types.Material
    )


class GlobalSettings(PropertyGroup):
    block_size: FloatVectorProperty(
        name="Block size",
        description="Configure the block size",
        default=Vector((1, 1, 1))
    )

    divide_by_vector: BoolProperty(
        name="Divide by vector",
        description="Use (1.0 / [block size]) as actual size",
        default=False
    )

    cache_path: StringProperty(
        name="Cache path",
        description="",
        default="/cache",
        subtype='DIR_PATH'
    )

    frame_start: IntProperty(
        name="Start frame",
        description="The frame to start the bake from",
        default=0
    )

    frame_end: IntProperty(
        name="End frame",
        description="The frame to end the bake at",
        default=250
    )

frame = 0


def my_handler(scene):
    global frame
    if frame != scene.frame_current:
        frame = scene.frame_current
        print("Frame Change", scene.frame_current)
        if Blockify.COLLECTION_NAME in bpy.data.collections:
            for obj in bpy.data.collections[Blockify.COLLECTION_NAME].objects:
                if obj.visible_get():
                    mesh_name = obj.name + "_" + str(frame)
                    if mesh_name in bpy.data.meshes:
                        obj.data = bpy.data.meshes[mesh_name]


def register():
    print("register")
    frame = 0
    bpy.utils.register_class(BlockifyOperator)
    bpy.utils.register_class(ObjectBlockifyPanel)
    bpy.utils.register_class(GlobalBlockifyPanel)
    bpy.utils.register_class(ObjectSettings)
    bpy.utils.register_class(GlobalSettings)
    bpy.types.Object.blockify = PointerProperty(type=ObjectSettings)
    bpy.types.Scene.blockify = PointerProperty(type=GlobalSettings)


def unregister():
    bpy.utils.unregister_class(BlockifyOperator)
    bpy.utils.unregister_class(ObjectBlockifyPanel)
    bpy.utils.unregister_class(GlobalBlockifyPanel)
    bpy.utils.unregister_class(ObjectSettings)
    bpy.utils.unregister_class(GlobalSettings)
    del bpy.types.Object.blockify
    del bpy.types.Scene.blockify

if len(bpy.app.handlers.frame_change_pre) > 0:
    bpy.app.handlers.frame_change_pre.clear()

bpy.app.handlers.frame_change_pre.append(my_handler)

if __name__ == "__main__":
    register()
    frame = -1
