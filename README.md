# Protein Artist
![1IGT](/img/1IGT_style1.png)

This is a repo for simplely fetching and rendering protein 3D structure using [Blender](https://www.blender.org/) Python module bpy.

## Table of Contents
- [Dependencies](#dependencies)
- [Usages](#usages)
- [Examples](#examples)

## Dependencies
### Dependencies ###
* [python](https://www.python.org/) (version 3.10)
* [pymol](https://pymol.org/2/)
* [bpy](https://docs.blender.org/api/current/info_quickstart.html)

1. Install dependencies by conda:   
```
conda env create -f env.yml
```   
2. Activate conda environment:   
```
source activate blender
```

## Usages
### First, set the file access permissions by running ###
```
chmod +x render_PDB.py
```
### Then, refer the following usages to run the scripts ###
```
usage: ./render_PDB.py [-h] [--id ID] [--camera_lens CAMERA_LENS]
                     [--camera_pos CAMERA_POS] [--core_style CORE_STYLE]
                     [--shell_style SHELL_STYLE]
                     [--temporary_path TEMPORARY_PATH]
                     [--output_path OUTPUT_PATH]
                     [--output_quality OUTPUT_QUALITY]

options:
  -h, --help            show this help message and exit
  --id ID, -i ID        PDB ID or PDB_chain (default: 1IGT)
  --camera_lens CAMERA_LENS, -lens CAMERA_LENS
                        Camera lens. Default 22. (default: 18)
  --camera_pos CAMERA_POS, -pos CAMERA_POS
                        Camera position. Default 140. (default: 40)
  --core_style CORE_STYLE, -cs CORE_STYLE
                        Core structure style. (default: cartoon)
  --shell_style SHELL_STYLE, -ss SHELL_STYLE
                        Shell structure style. (default: surface)
  --temporary_path TEMPORARY_PATH, -tmp TEMPORARY_PATH
                        output file folder name (default: data)
  --output_path OUTPUT_PATH, -o OUTPUT_PATH
                        output file folder name (default: ../img)
  --output_quality OUTPUT_QUALITY, -q OUTPUT_QUALITY
                        output image quality (default: low)
```   

## Examples

### Render an antibody using default setting
```
renderPDB -i 1IGT
```

![1IGT](/img/1IGT_style1_1.png)

### Render an antibody with different modes
```
renderPDB -i 1IGT -cs ribbon
```
![1IGT](/img/1IGT_style3.png)
### Render an antibody with different modes and different views
```
renderPDB -i 1IGT -pos 40
```
![1IGT](/img/1IGT_style4_1.png)
### Render 2019-nCoV RBD/ACE2-B0AT1 complex
```
./renderPDB -i 6M17
```
![6M17](/img/6M17.png)
