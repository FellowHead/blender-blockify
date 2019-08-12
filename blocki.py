import bpy
import bmesh
import os

from threading import Thread
from mathutils import Vector


class BlockGrid:
    def __init__(self, data, block_size, bounds_min):
        self.data = data
        self.block_size = block_size
        self.bounds_min = bounds_min


class BlockifIO:
    @staticmethod
    def vector_write(v):
        return f"{v.x},{v.y},{v.z}"

    @staticmethod
    def vector_read(s):
        return Vector([float(i) for i in s.split(',')])


class Blockify:
    COLLECTION_NAME = "Blockified"

    @staticmethod
    def write_grid_file(path, grid):
        print("saving...")
        with open(path, "w+") as file:
            file.write(BlockifIO.vector_write(grid.block_size) + "\n")
            file.write(BlockifIO.vector_write(grid.bounds_min) + "\n")
            file.write(f"{len(grid.data)},")
            file.write(f"{len(grid.data[0])},")
            file.write(f"{len(grid.data[0][0])}\n")
            for x in grid.data:
                for y in x:
                    for z in y:
                        file.write(str(z) + ",")
            file.write("420")
            print("saved to " + os.path.realpath(file.name))

    @staticmethod
    def read_grid_file(path):
        with open(path, "r") as file:
            block_size = BlockifIO.vector_read(file.readline().rstrip())
            bounds_min = BlockifIO.vector_read(file.readline().rstrip())
            size = [int(i) for i in file.readline().rstrip().split(',')]
            grid = []

            readData = [int(i) for i in file.readline().rstrip().split(',')]

            x = 0
            while x < size[0]:
                y = 0
                grid.append([])
                while y < size[1]:
                    z = 0
                    grid[x].append([])
                    while z < size[2]:
                        # print(str(3 + x * sizeZ * sizeY + y * sizeZ + z))
                        # print(x,y,z)
                        grid[x][y].append(
                            readData[x * size[1] * size[2] + y * size[2] + z]
                        )
                        z = z + 1
                    y = y + 1
                x = x + 1

            return BlockGrid(grid, block_size, bounds_min)

    @staticmethod
    def valid_objects(scene):
        valid = []
        for obj in scene.objects:
            blk_obj = obj.blockify
            if ((blk_obj.enabled and obj.visible_get() and
                 (Blockify.COLLECTION_NAME not in bpy.data.collections or
                  bpy.data.collections[Blockify.COLLECTION_NAME]
                  not in obj.users_collection))):
                valid.append(obj)
        return valid

    @staticmethod
    def compute_grid(deps_obj, block_size=Vector((1, 1, 1)), precision=0):
        C = bpy.context
        D = bpy.data

        deps = C.evaluated_depsgraph_get()

        bs = block_size / 2
        bounds_min = Vector(deps_obj.bound_box[0]) + bs
        bounds_max = Vector(deps_obj.bound_box[6]) - bs
        bounds = (bounds_max - bounds_min)
        bounds = Vector((
            bounds.x / block_size.x,
            bounds.y / block_size.y,
            bounds.z / block_size.z
        ))

        # create voxel grid

        print("Creating voxel grid...")

        grid = []

        x = 0
        while x <= bounds.x:
            grid.append([])
            y = 0
            while y <= bounds.y:
                grid[x].append([])
                z = 0
                while z <= bounds.z:
                    grid[x][y].append(0)
                    # print("added " + str(x) + "," + str(y) + "," + str(z))
                    z = z + 1
                y = y + 1
            x = x + 1

        # subdivide mesh

        srcObj = deps_obj.original
        bm = bmesh.new()
        bm.from_object(srcObj, deps)

        if precision > 0:
            print("Subdiving source mesh...")
            bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=precision,
                                      use_grid_fill=True)

        # calculate affected blocks

        print("Calculating affected blocks...")

        def fint(value, b):
            return int(min(bounds[b], round(value)))

        max = 0

        for v in bm.verts:
            g = v.co - bounds_min
            g = Vector((
                g.x / block_size.x,
                g.y / block_size.y,
                g.z / block_size.z
            ))
            gv = grid[fint(g.x, 0)][fint(g.y, 1)][fint(g.z, 2)] + 1
            grid[fint(g.x, 0)][fint(g.y, 1)][fint(g.z, 2)] = gv
            if gv > max:
                max = gv

        bm.free()
        return BlockGrid(grid, block_size, bounds_min)

    @staticmethod
    def create_mesh(grid, mesh, uv_option=False,
                    mat_top=0, mat_bottom=0,
                    mat_x_p=0, mat_x_n=0,
                    mat_y_p=0, mat_y_n=0):
        bm = bmesh.new()

        bounds = Vector((
            len(grid.data),
            len(grid.data[0]),
            len(grid.data[0][0])
        ))

        def add(off, v1, v2):
            return bm.faces.new([
                bm.verts.new(off - v1 - v2),
                bm.verts.new(off + v1 - v2),
                bm.verts.new(off + v1 + v2),
                bm.verts.new(off - v1 + v2),
            ])

        def u1(face, i1, i2, b1, b2):
            if not uv_option:
                face.loops[0][uv].uv = Vector((1, 0))
                face.loops[1][uv].uv = Vector((1, 1))
                face.loops[2][uv].uv = Vector((0, 1))
                face.loops[3][uv].uv = Vector((0, 0))
            else:
                off = Vector((i1 * b1 % 1.0, i2 * b2 % 1.0))
                face.loops[0][uv].uv = off + Vector((b1, 0))
                face.loops[1][uv].uv = off + Vector((b1, b2))
                face.loops[2][uv].uv = off + Vector((0, b2))
                face.loops[3][uv].uv = off + Vector((0, 0))

        def u2(face, i1, i2, b1, b2):
            if not uv_option:
                face.loops[0][uv].uv = Vector((0, 0))
                face.loops[1][uv].uv = Vector((1, 0))
                face.loops[2][uv].uv = Vector((1, 1))
                face.loops[3][uv].uv = Vector((0, 1))
            else:
                off = Vector((i1 * b1 % 1.0, i2 * b2 % 1.0))
                face.loops[0][uv].uv = off + Vector((0, 0))
                face.loops[1][uv].uv = off + Vector((b1, 0))
                face.loops[2][uv].uv = off + Vector((b1, b2))
                face.loops[3][uv].uv = off + Vector((0, b2))

        def m(face, mi):
            face.material_index = mi
            return face

        # create blockified mesh

        print("Creating blockified mesh...")

        def e(dx, dy, dz):  # e ~ "empty?"
            # check if in bounds
            if (
                dx < 0 or dy < 0 or dz < 0 or
                dx >= bounds.x or dy >= bounds.y or dz >= bounds.z
            ):
                return True
            return grid.data[dx][dy][dz] <= threshold

        bs = grid.block_size / 2
        # helpers
        vx = Vector((bs.x, 0, 0))
        vy = Vector((0, bs.y, 0))
        vz = Vector((0, 0, bs.z))

        uv = bm.loops.layers.uv.verify()

        threshold = 0

        bs = grid.block_size

        x = 0
        while x < bounds.x:
            y = 0
            while y < bounds.y:
                z = 0
                while z < bounds.z:
                    if grid.data[x][y][z] > threshold:
                        v = Vector((
                            x * bs.x,
                            y * bs.y,
                            z * bs.z
                        )) + grid.bounds_min

                        if e(x + 1, y, z):
                            u2(m(add(v + vx, vy, vz), mat_x_p),
                                y, z, bs.y, bs.z)
                        if e(x - 1, y, z):
                            u1(m(add(v - vx, vz, vy), mat_x_n),
                                y, z, bs.y, bs.z)

                        if e(x, y + 1, z):
                            u1(m(add(v + vy, vz, vx), mat_y_p),
                                x, z, bs.x, bs.z)
                        if e(x, y - 1, z):
                            u2(m(add(v - vy, vx, vz), mat_y_n),
                                x, z, bs.x, bs.z)

                        if e(x, y, z + 1):
                            u2(m(add(v + vz, vx, vy), mat_top),
                                x, y, bs.x, bs.y)
                        if e(x, y, z - 1):
                            u1(m(add(v - vz, vy, vx), mat_bottom),
                                x, y, bs.x, bs.y)
                    z = z + 1
                y = y + 1
            x = x + 1
            # print("Progress: " + str(x / bounds.x))

        print("Removing doubles...")

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=(min(bs) / 2))

        bm.to_mesh(mesh)
        print("converted to mesh " + str(mesh))
        bm.free()
        print("so guys, we did it")
