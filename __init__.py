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
from . panel import BlockifyPanel

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


class MySettings(PropertyGroup):
    block_size = FloatVectorProperty(
        name="Block size",
        description="Configure the block size",
        default=Vector((1, 1, 1))
    )

    precision = IntProperty(
        name="Precision",
        description="Amount of pre-subdivisions",
        default=0,
        min=0,
        max=10
    )

    divide_by_vector = BoolProperty(
        name="Divide by vector",
        description="Use (1.0 / [block size]) as actual size",
        default=False
    )

    frame_start = IntProperty(
        name="Start frame",
        description="The frame to start the bake from",
        default=0
    )

    frame_end = IntProperty(
        name="End frame",
        description="The frame to end the bake at",
        default=250
    )

frame = 0


def register():
    print("register")
    frame = 0
    bpy.utils.register_class(BlockifyOperator)
    bpy.utils.register_class(BlockifyPanel)
    bpy.utils.register_class(MySettings)
    bpy.types.Scene.blockify = PointerProperty(type=MySettings)


def unregister():
    bpy.utils.unregister_class(BlockifyOperator)
    bpy.utils.unregister_class(BlockifyPanel)
    bpy.utils.unregister_class(MySettings)
    del bpy.types.Scene.blockify


def my_handler(scene):
    global frame
    if frame != scene.frame_current:
        frame = scene.frame_current
        print("Frame Change", scene.frame_current)

if len(bpy.app.handlers.frame_change_pre) > 0:
    bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(my_handler)

if __name__ == "__main__":
    register()
    frame = -1
