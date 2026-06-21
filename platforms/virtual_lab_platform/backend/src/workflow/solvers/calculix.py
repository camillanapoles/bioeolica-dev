"""CalculiX input file preparation."""
import os

def prepare_calculix_case(params: dict, workdir: str) -> None:
    """
    Prepare CalculiX input file (.inp) in the given workdir.
    Expected params:
        - length, width, height: dimensions (mm)
        - youngs_modulus: Young's modulus (MPa)
        - poisson_ratio: Poisson's ratio
        - density: density (g/mm^3) maybe
        - force: applied force (N) on a face
        - fixed_face: which face is fixed (e.g., 'xmin')
    For simplicity, we create a single hexahedral element block.
    """
    # Create the .inp file
    inp_path = os.path.join(workdir, "model.inp")
    with open(inp_path, "w") as f:
        f.write("*HEADING\n")
        f.write("** Simple block for virtual lab\n")
        f.write("*NODE, SET=Nall\n")
        f.write("1, 0, 0, 0\n")
        f.write("2, {length}, 0, 0\n".format(length=params.get('length', 10)))
        f.write("3, {length}, {width}, 0\n".format(length=params.get('length', 10), width=params.get('width', 10)))
        f.write("4, 0, {width}, 0\n".format(width=params.get('width', 10)))
        f.write("5, 0, 0, {height}\n".format(height=params.get('height', 10)))
        f.write("6, {length}, 0, {height}\n".format(length=params.get('length', 10), height=params.get('height', 10)))
        f.write("7, {length}, {width}, {height}\n".format(length=params.get('length', 10), width=params.get('width', 10), height=params.get('height', 10)))
        f.write("8, 0, {width}, {height}\n".format(width=params.get('width', 10), height=params.get('height', 10)))
        f.write("\n*ELEMENT, TYPE=C3D8, ELSET=Eall\n")
        f.write("1, 1, 2, 3, 4, 5, 6, 7, 8\n")
        f.write("\n*MATERIAL, NAME=MAT1\n")
        f.write("*ELASTIC\n")
        f.write("{youngs_modulus}, {poisson_ratio}\n".format(
            youngs_modulus=params.get('youngs_modulus', 210000),
            poisson_ratio=params.get('poisson_ratio', 0.3)))
        f.write("*DENSITY\n")
        f.write("{density}\n".format(density=params.get('density', 7.85e-3)))
        f.write("\n*BOUNDARY\n")
        # Fix face x=0 (nodes 1,4,5,8) in all directions
        f.write("1,1,1,0\n")
        f.write("4,1,1,0\n")
        f.write("5,1,1,0\n")
        f.write("8,1,1,0\n")
        f.write("\n*CLOAD\n")
        # Apply force on face x=length (nodes 2,3,6,7) in x-direction
        force_per_node = params.get('force', 1000) / 4.0
        f.write("2,1,{force_per_node}\n".format(force_per_node=force_per_node))
        f.write("3,1,{force_per_node}\n".format(force_per_node=force_per_node))
        f.write("6,1,{force_per_node}\n".format(force_per_node=force_per_node))
        f.write("7,1,{force_per_node}\n".format(force_per_node=force_per_node))
        f.write("\n*STEP\n*STATIC\n")
        f.write("1.0, 1.0, 1e-6, 1.0\n")
        f.write("*NODE FILE\nU\n")
        f.write("*EL FILE\nS, E\n")
        f.write("*END STEP\n")
        f.write("** End of input\n")
