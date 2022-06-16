# OBJ-Voxel-Visualizer

# ==================================================
# Parameters
# ==================================================

OBJ_Output_Filename = 'voxel-mesh-visual.obj' # Default Filename of OBJ output

Surface_View = True # Toggles the default state of surface view mode

# NOTE: it is recommended to leave Surface_View set to TRUE to reduce the number of mesh bodies created.

# ==================================================
# Import Packages
# ==================================================

import sys
import math
import argparse
import numpy as np
from numpy.lib import stride_tricks

# ==================================================
# OBJ Voxel Visualizer Functions
# ==================================================

def get_shape_and_strides( voxel_array ):
	""" Calculate the shape of a stride region and stride step distance
		to move a 3x3 or 3x3x3 kernel window over every internal value.
	Parameters
	----------
		voxel_array : array
			3D array of values that define a volume of voxels.
	Returns
	-------
		( shape, strides ) : 1xN int array, 1xN int array 
			The shape of the stride region to the provided NumPy array.
			Strides define the stepover that indexes over every cell in
			the inner array, ignores 1 value border. Kernel window size
			is 3x3 for 2D array, 3x3x3 for 3D array.
	Examples
    --------
		Calculate shape and strides of an array with:
			shape = ( 102, 59, 44 )
			dtype = int8
		>>> get_shape_and_strides( voxel_array )
		>>> (array([100,   57,   42,    3,    3,    3]),
 			 array([  1,  102, 6018,    1,  102, 6018]))
		Calculate shape and strides of an array with:
			shape = ( 7, 7 )
			dtype = int64
		>>> get_shape_and_strides( example_array2D )
		>>> (array([ 5,  5,  3,  3]), 
			 array([56,  8, 56,  8]))
	"""
	kernel_size = np.ones(voxel_array.ndim, dtype='int8') * 3
	kernel_strides = np.tile( voxel_array.strides, 2 )
	stride_region = np.asarray(voxel_array.shape) - 2
	neighborhood_shape = np.concatenate(( stride_region, kernel_size ))
	
	return neighborhood_shape, kernel_strides


def get_surface_voxels( voxel_array ):
	""" Remove all values that contain non-zero neighbors in every direction.
		Returns an array of identical size with values that define the surface
		of the voxel volume.
	Parameters
	----------
		voxel_array : array
			3D array of values that define a volume of voxels.
	Returns
	-------
		surface_voxel_array : array
			An array the same size as the one provided with all internal values
			removed, leaving values that define boundary with zero-value regions.
	"""
	shape, strides = get_shape_and_strides( voxel_array.astype(bool) )
	batched_neighborhoods = stride_tricks.as_strided( voxel_array, shape, strides )
	
	neighborhood_spacing, neighborhood_size = np.split(shape, 2)
	neighborhood_rows = batched_neighborhoods.reshape( np.prod(neighborhood_spacing), np.prod(neighborhood_size) )
	neighborhood_max = np.prod(neighborhood_size)
	neighbor_count = np.add.reduce(neighborhood_rows, -1)
	
	internal_voxel_mask = np.where( neighbor_count < neighborhood_max, True, False )
	internal_voxels = np.pad(internal_voxel_mask.reshape(neighborhood_spacing), pad_width=1, constant_values=True)
	
	return np.where( internal_voxels, voxel_array.astype(bool), False )


def voxel_array2mesh( voxel_array, surface_view = True ):
	""" Covert an array of voxels into vertices and faces that create a mesh volume.
		Includes option to disable surface view which will generate vertices and
		faces for all voxels found in the provided array.
	Parameters
	----------
		voxel_array : ndarray
			3D array of values that define a volume of voxels.
		surface_view : boolean 
			Toggle if output contains only surface voxels.
	Returns
	-------
		vertices : Nx3 float64 array
			Valid vertex coordinates that are used to define the voxel cube faces.
		faces : Nx3 int64 array
			Coordinate index positions that correspond to the index of points 
			listed in the vertices array. Each set of index positions defines
			the corners of a triangular face found in the exported mesh.
	"""
	scale = 0.01
	cube_dist_scale = 1.1
	cube_verts = np.array(
		[[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], 
		 [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]) # 8 points
	cube_faces = np.array(
		[[1, 2, 3], [2, 4, 3], [3, 4, 7], [4, 8, 7],
		 [1, 3, 7], [1, 7, 5], [1, 6, 2], [1, 5, 6], 
		 [7, 8, 6], [7, 6, 5], [2, 8, 4], [2, 6, 8]]) # 12 faces
	
	# Check Surface View State
	if surface_view:
		surfvoxel_array = get_surface_voxels(voxel_array)
		positions = np.stack(np.where(surfvoxel_array > 0), axis=-1)
	else:
		positions = np.stack(np.where(voxel_array > 0), axis=-1)
	
	voxel_count = positions.shape[0]
	# Calculate Vertices of Voxel Mesh
	scaled_positions = (cube_dist_scale * positions).reshape(voxel_count,1,3)
	assigned_vertices = (scaled_positions + cube_verts).reshape( (voxel_count * 8), 3 )
	vertices = assigned_vertices * scale
	
	# Calculate Faces of Voxel Mesh
	vertex_order = np.arange( 0, (voxel_count * 8), 8 )
	vert_offsets = vertex_order[:, np.newaxis, np.newaxis]
	faces = (cube_faces + vert_offsets).reshape( (voxel_count * 12), 3 )
	
	return vertices, faces


def write_obj(filename, vertices, faces):
	""" Write vertices and faces to an Wavefront OBJ file.
	Parameters
	----------
		filename : string ("*.obj")
			Name of the OBJ file to be created in local directory. Requires
			the filename to end in ".obj" for a valid file.
		vertices : Nx3 float64 ndarray
			Valid vertex coordinates that are used to define the voxel cube faces.
		faces : Nx3 int64 ndarray
			Index groups that define triangular faces using the corresponding 
			points found in the vertices argument.
	"""
	with open(filename, 'w') as f:
		f.write('g\n# %d vertex\n' % len(vertices))
		for vert in vertices: # Write Vertices
			f.write('v %f %f %f\n' % tuple(vert))
		
		f.write('# %d faces\n' % len(faces))
		for face in faces: # Write Faces
			f.write('f %d %d %d\n' % tuple(face))


def voxel_array2voxel_mesh_obj(filename, voxel_array, surface_view = True):
	""" Convert voxels in a NumPy array into mesh vertices and faces
		then save the mesh data to a Wavefront OBJ file.   
	Parameters
	----------
		filename : string ("*.obj")
			Name of the OBJ file to be created in local directory. Requires
			the filename to end in ".obj" for a valid file.
		voxel_array : ndarray
			3D array of values that define a volume of voxels.
		surface_view : boolean 
			Toggle if output contains only surface voxels.
	"""
	verts, faces = voxel_array2mesh( voxel_array, surface_view )
	write_obj( filename, verts, faces )


# ==================================================
# Main Script
# ==================================================

def obj_voxel_visualizer( 
		npy_input_filename, 
		obj_output_filename=OBJ_Output_Filename , 
		surface_view=Surface_View):

	voxel_array = np.load( npy_input_filename )
	if surface_view: voxel_array = get_surface_voxels( voxel_array )

	if voxel_limit_check( voxel_array ):
		print( "Total Number of Voxels:", np.count_nonzero( voxel_array ) )
		print( "Surface_View:", surface_view )
		print( "Output Filename:", obj_output_filename )


# ==================================================
# Input Argument Parsing
# ==================================================

def query_yes_no( question, default="yes" ):
	valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
	if default is None:
		prompt = ( question + " [y/n] " )
	elif default == "yes":
		prompt = ( question + " [Y/n] " )
	elif default == "no":
		prompt = ( question + " [y/N] " )
	else:
		raise ValueError("invalid default answer: '%s'" % default)
	
	while True:
		sys.stdout.write( prompt )
		choice = input().lower()
		if default is not None and choice == "":
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def voxel_limit_check( voxel_array, limit=1000000 ):
	if np.count_nonzero(voxel_array) > limit:
		print("Total number of voxels is over 1,000,000. Creating a mesh with this many faces can cause performance issues when opened.")
		return query_yes_no("Do you want to continue?", default="no")
	else:
		return True

if __name__ == '__main__':

	def parse_arguments():
		parser = argparse.ArgumentParser()
		parser.add_argument("npy_input_filename", type=str)
		parser.add_argument("--output", "-o", type=str, default=OBJ_Output_Filename)
		parser.add_argument("--surface-view", default=Surface_View, action=argparse.BooleanOptionalAction)

		args = parser.parse_args()
		assert args.npy_input_filename.endswith(".npy"), "Input must be a numpy array (.npy)"

		if args.output:
			if args.output.endswith(".obj"):
				obj_output_filename = args.output
			else:
				obj_output_filename = (args.output + ".obj")
		
		return args.npy_input_filename, obj_output_filename, args.surface_view
	
	# Main Script Call
	args = parse_arguments()
	obj_voxel_visualizer(*args)


# ==================================================
# Functions for Jupyter Notebook (Optional)
# ==================================================

if __name__ != '__main__':
	def old_voxel_array2mesh( voxels, surface_view ):
		cube_verts = np.array(
			[[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], 
			[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]) # 8 points
		cube_faces = np.array(
			[[1, 2, 3], [2, 4, 3], [3, 4, 7], [4, 8, 7],
			[1, 3, 7], [1, 7, 5], [1, 6, 2], [1, 5, 6], 
			[7, 8, 6], [7, 6, 5], [2, 8, 4], [2, 6, 8]]) # 12 faces
		
		scale = 0.01
		cube_dist_scale = 1.1
		verts = []
		faces = []
		current_vert = 0

		positions = np.where(voxels > 0)
		voxels[positions] = 1

		for i, j, k in zip(*positions):
			if not surface_view or np.sum(voxels[i-1:i+2, j-1:j+2, k-1:k+2]) < 27:
				verts.extend(scale * (cube_verts + cube_dist_scale * np.array([[i, j, k]])))
				faces.extend(cube_faces + current_vert)
				current_vert += len(cube_verts)

		return np.array(verts), np.array(faces)

	def convert_size(size_bytes):
		if size_bytes == 0:
			return "0B"
		
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
		i = int(math.floor(math.log(size_bytes, 1024)))
		p = math.pow(1024, i)
		s = round(size_bytes / p, 2)

		return "%s %s" % (s, size_name[i])

