# test_netgen_sphere.py
# make / load an order-2 geometry sphere
# Thanks to Umberto Zerbinati for help - see
# https://github.com/firedrakeproject/firedrake/discussions/4455

from firedrake import *
from netgen.occ import *

# make sphere using occ

sphere = Sphere((0,0,0),1.4)
geo = OCCGeometry(sphere, dim=3)
ngmesh3d = geo.GenerateMesh(maxh=0.5)
ngmesh3d.Save("sphere_mesh.vol")
msh3d = Mesh(Mesh(ngmesh3d,comm=COMM_WORLD).curve_field(2))  # convert to Firedrake mesh
VTKFile("sphere_mesh.pvd").write(msh3d)

# load saved sphere (works with all the make sphere stuff commented out)

#try:
#    import netgen
#except ImportError:
#    import sys
#    warning("Unable to import NetGen.")
#    sys.exit(0)

#ngmesh3d = netgen.meshing.Mesh()
#ngmesh3d.Load("sphere_mesh.vol")
#mesh3d = Mesh(Mesh(ngmesh3d,comm=COMM_WORLD).curve_field(2))  # convert to Firedrake mesh
#VTKFile("sphere_mesh.pvd").write(mesh3d)

