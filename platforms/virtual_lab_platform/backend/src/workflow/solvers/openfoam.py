"""OpenFOAM case preparation."""
import os

def prepare_openfoam_case(params: dict, workdir: str) -> None:
    """
    Prepare OpenFOAM case files in the given workdir.
    params may contain:
        - velocity: inflow velocity (m/s)
        - viscosity: kinematic viscosity (m2/s)
        - length, width, height: dimensions of the block (m)
    """
    # Create necessary directories
    os.makedirs(os.path.join(workdir, "system"), exist_ok=True)
    os.makedirs(os.path.join(workdir, "constant"), exist_ok=True)
    os.makedirs(os.path.join(workdir, "constant", "polymesh"), exist_ok=True)

    # Write controlDict
    control_dict_template = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
| \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
*-----------------------------------------------------------------*/ 
application     simpleFoam;

startFrom       latestTime;

startTime       0;
stopAt          endTime;

endTime         1000;          // number of time steps
deltaT          1;
writeControl    timeStep;
writeInterval   100;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression  off;
timeFormat      general;
timePrecision   6;
graphFormat     raw;
runTimeModifiable  true;

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * // */

velocities    ({VELOCITY} 0 0);
"""
    control_dict = control_dict_template.replace("{VELOCITY}", str(params.get('velocity', 0)))
    with open(os.path.join(workdir, "system", "controlDict"), "w") as f:
        f.write(control_dict)

    # Write fvSchemes (simple)
    fv_schemes = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
| \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
*-----------------------------------------------------------------*/ 
ddtScheme           Euler;
gradSchemes         { default GaussLinear; }
divSchemes          { default GaussLinear; laplacianSchemes { default GaussLinear corrected; }
interpolationSchemes { default linear; }
snGradSchemes       { default corrected; }
fluxRequired        { default no;       p; }
*/
"""
    with open(os.path.join(workdir, "system", "fvSchemes"), "w") as f:
        f.write(fv_schemes)

    # Write fvSolution
    fv_solution = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
| \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
*-----------------------------------------------------------------*/ 
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    "(U|k|epsilon|omega|nu|mut)"
    {
        solver          smoothSolver;
        smoother        symmetricGaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
}
PIMPLE
{
    momentumPredictor yes;
    nCorrectors       1;
    nOuterCorrectors  1;
    nNonOrthogonalCorrectors 0;
}
"""
    with open(os.path.join(workdir, "system", "fvSolution"), "w") as f:
        f.write(fv_solution)

    # Write transportProperties
    transport_template = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
| \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
*-----------------------------------------------------------------*/ 
transportModel  Newtonian;

nu              {NU};
"""
    transport = transport_template.replace("{NU}", str(params.get('viscosity', 1.5e-5)))
    with open(os.path.join(workdir, "constant", "transportProperties"), "w") as f:
        f.write(transport)

    # Write blockMeshDict
    length = params.get('length', 1.0)
    width = params.get('width', 1.0)
    height = params.get('height', 1.0)
    nx = int(length * 20)
    ny = int(width * 20)
    nz = int(height * 20)
    block_mesh_template = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
| \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
*-----------------------------------------------------------------*/ 
convertToMeters 1;

vertices
(
    (0 0 0)
    ({LENGTH} 0 0)
    ({LENGTH} {WIDTH} 0)
    (0 {WIDTH} 0)
    (0 0 {HEIGHT})
    ({LENGTH} 0 {HEIGHT})
    ({LENGTH} {WIDTH} {HEIGHT})
    (0 {WIDTH} {HEIGHT})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({NX} {NY} {NZ} simpleGrading (1 1 1))
);

edges
(
);

boundary
(
    inlet
    {
        type            patch;
        faces
        (
            (0 4 7 3)
        );
    }
    outlet
    {
        type            patch;
        faces
        (
            (1 5 6 2)
        );
    }
    walls
    {
        type            wall;
        faces
        (
            (0 1 5 4)
            (1 2 6 5)
            (2 3 7 6)
            (3 0 4 7)
            (4 5 6 7)
        );
    }
    frontAndBack
    {
        type            empty;
        faces
        (
            (0 3 2 1)
            (4 7 6 5)
        );
    }
);

mergePatchPairs
(
);
"""
    block_mesh = block_mesh_template.replace("{LENGTH}", str(length)).replace("{WIDTH}", str(width)).replace("{HEIGHT}", str(height)).replace("{NX}", str(nx)).replace("{NY}", str(ny)).replace("{NZ}", str(nz))
    with open(os.path.join(workdir, "system", "blockMeshDict"), "w") as f:
        f.write(block_mesh)
