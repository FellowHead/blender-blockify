import bpy
import bmesh

from threading import Thread
from mathutils import Vector

def blockify(blockSize = Vector((1,1,1)), precision=0):
	C = bpy.context
	D = bpy.data

	deps = C.evaluated_depsgraph_get()

	obj = deps.objects["Src"] # HARDCODED

	bs = blockSize / 2
	boundsMin = Vector(obj.bound_box[0]) + bs
	boundsMax = Vector(obj.bound_box[6]) - bs
	#print(boundsMin)
	#print(boundsMax)
	bounds = (boundsMax - boundsMin)
	bounds = Vector((bounds.x / blockSize.x, bounds.y / blockSize.y, bounds.z / blockSize.z))

	#print("grid size: " + str(bounds))

	### create voxel grid

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
				#print("added " + str(x) + "," + str(y) + "," + str(z))
				z = z+1
			y = y+1
		x = x+1

	### subdivide mesh

	srcObj = D.objects["Src"] # HARDCODED!!!
	bm = bmesh.new()
	bm.from_object(srcObj, deps)
	print("Subdiving source mesh...")
	bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=precision, use_grid_fill=True)

	### calculate affected blocks

	print("Calculating affected blocks...")

	def fint(value, b):
		return int(min(bounds[b], round(value)))
	
	def add(bm, off, v1, v2):
		return bm.faces.new([
			bm.verts.new(off-v1-v2),
			bm.verts.new(off+v1-v2),
			bm.verts.new(off+v1+v2),
			bm.verts.new(off-v1+v2),
		])
	def u1(uv, face, i1, i2, b1, b2):
		off = Vector((i1 * b1 % 1.0, i2 * b2 % 1.0))
		face.loops[0][uv].uv = off+Vector((b1,0))
		face.loops[1][uv].uv = off+Vector((b1,b2))
		face.loops[2][uv].uv = off+Vector((0,b2))
		face.loops[3][uv].uv = off+Vector((0,0))
	def u2(uv, face, i1, i2, b1, b2):
		off = Vector((i1 * b1 % 1.0, i2 * b2 % 1.0))
		face.loops[0][uv].uv = off+Vector((0,0))
		face.loops[1][uv].uv = off+Vector((b1,0))
		face.loops[2][uv].uv = off+Vector((b1,b2))
		face.loops[3][uv].uv = off+Vector((0,b2))

	max = 0

	for v in bm.verts:
		g = v.co - boundsMin
		g = Vector((g.x / blockSize.x, g.y / blockSize.y, g.z / blockSize.z))
		#print(str(g.y))
		#print(fint(g.y, 0))
		gv = grid[fint(g.x, 0)][fint(g.y, 1)][fint(g.z, 2)] + 1
		grid[fint(g.x, 0)][fint(g.y, 1)][fint(g.z, 2)] = gv
		if gv > max:
			max = gv

	#print("max: " + str(max))
	threshold = 0

	### create blockified mesh

	print("Creating blockified mesh...")

	bm.clear()

	def e(dx,dy,dz): # e ~ "empty?"
		# check if in bounds
		if dx < 0 or dy < 0 or dz < 0 or dx > bounds.x or dy > bounds.y or dz > bounds.z:
			return True
		return grid[dx][dy][dz] <= threshold

	# bs = blockSize / 2
	# helper
	vx = Vector((bs.x, 0, 0))
	vy = Vector((0, bs.y, 0))
	vz = Vector((0, 0, bs.z))

	uv = bm.loops.layers.uv.verify()
	u = blockSize # uv size


	x = 0
	while x <= bounds.x:
		y = 0
		while y <= bounds.y:
			z = 0
			while z <= bounds.z:
				if grid[x][y][z] > threshold:
					bs = blockSize
					v = Vector((x * bs.x, y * bs.y, z * bs.z)) + boundsMin
					bs = blockSize
					if e(x+1,y,z):
						#u2(add(v+vx, vy, vz))
						u2(uv, add(bm, v+vx, vy, vz), y, z, bs.y, bs.z)
					if e(x-1,y,z):
						u1(uv, add(bm, v-vx, vz, vy), y, z, bs.y, bs.z)
					
					if e(x,y+1,z):
						u1(uv, add(bm, v+vy, vz, vx), x, z, bs.x, bs.z)
					if e(x,y-1,z):
						u2(uv, add(bm, v-vy, vx, vz), x, z, bs.x, bs.z)
					
					if e(x,y,z+1):
						u2(uv, add(bm, v+vz, vx, vy), x, y, bs.x, bs.y)
					if e(x,y,z-1):
						u1(uv, add(bm, v-vz, vy, vx), x, y, bs.x, bs.y)
				z = z+1
			y = y+1
		x = x+1
		#print("Progress: " + str(x / bounds.x))

	print("Removing doubles...")

	bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = min(blockSize) / 2)

	#TODO: create new mesh
	#D.meshes.new
	bm.to_mesh(D.meshes["kapow"])
	bm.free()

	obj.original.data = D.meshes["kapow"]

	print("so guys, we did it")