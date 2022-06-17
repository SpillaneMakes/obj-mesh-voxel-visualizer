![OBJ Mesh Voxel Visualizer Banner](images/OBJ-Mesh-Voxel-Visualizer-Nittany-Lion-Shrine-Banner.png)

*A utility to convert voxel data stored in a 3D NumPy array into a collection of OBJ mesh cubes for visualizing, sharing, and rendering.*


## Overview
- Generates mesh vertices and faces corresponding to each point in a NumPy array. 
- The script is a utility to share voxel models with peers who can access a basic mesh modeling program that can open Wavefront OBJ files. 
- A helpful tool for generating voxel mesh models for images and renders. 
- The mesh OBJ files are relatively large due to the number of generated vertices and faces. 
- By default, the script filters out all internal voxels creating a surface view shell made only of voxels that border empty voxel regions.


## Usage
**Dependencies**
- NumPy is the only package dependency for the main python script.
- Additional dependencies listed in `requirements.txt` support the analysis done in the jupyter notebook.

**Example Script Commands**

*Convert Numpy Voxel Data into OBJ Mesh*
```Bash
python obj-voxel-visualizer.py input-numpy-file.npy
```

*Specify Filename of OBJ Output*
```Bash
python obj-voxel-visualizer.py input-numpy-file.npy --output voxel-mesh-visual.obj
```

*Toggle Surface View Off*
```Bash
python obj-voxel-visualizer.py input-numpy-file.npy --no-surface-view
```

**Jupyter Notebook**
- Interactive examples
	- Converting NPY files using the command line function
	- Using internal functions to export loaded NPY data
	- Inline mesh viewer using Trimesh
- Measured runtime improvements over the original iteration of the function.
- Voxel data metrics evaluating voxel count and file size.
- Data plots illustrating the relationship between voxel count and the resulting OBJ file size when in surface view mode.


## Examples

<p style="text-align:center;">Surface View ON vs Surface View Off</p>

![Surface View Enabled vs Disabled](images/SurfView_vs_NoSurfView.JPG)

<p style="text-align:center;">Different Resolution Voxel Mesh Models</p>

<p align="center">
  <img style="width: 45%; min-width: 300px;" src="images/voxel-scale-comparison/1.voxel-lion-0.25-4x3.png"></img>
  <img style="width: 45%; min-width: 300px;" src="images/voxel-scale-comparison/2.voxel-lion-0.50-4x3.png"></img>
  <img style="width: 45%; min-width: 300px;" src="images/voxel-scale-comparison/3.voxel-lion-0.75-4x3.png"></img>
  <img style="width: 45%; min-width: 300px;" src="images/voxel-scale-comparison/4.voxel-lion-1.0-4x3.png"></img>
</p>

|     | Voxel Array Bounding Dimensions | Surface Voxel Count | Voxel % of Bounding Unit Magnitude |
|:---:| -------------------------------:| -------------------:|:----------------------------------:|
|  1  |                 (408, 236, 176) |             340,106 |              0.1988%               |
|  2  |                  (204, 118, 88) |              83,142 |              0.3975%               |
|  3  |                   (136, 79, 59) |              36,269 |              0.5953%               |
|  4  |                   (102, 59, 44) |              19,786 |              0.7950%               |


$$
\left(\ x\, \ y\, \ z \ \right) = \text{voxelˍarray.shape}
$$

$$
\text{Voxel ％ of Bounding Magnitude} = \left( \frac{1}{ \sqrt{x^2+y^2+z^2} } \right) * 100
$$