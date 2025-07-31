# test_netgen_reduced.py
# testing Firedrake Netgen integration stuff at 
# https://www.firedrakeproject.org/demos/netgen_mesh.py.html
# working toward curved meshes in Firedrake
# ultimate aim is to do MAST-U divertor with curved tiles in FEM

# what can this script do:
# it shows that loading a mesh from file does not work unless geo.GenerateMesh is called - !!

from firedrake import *

try:
    import netgen
except ImportError:
    import sys
    warning("Unable to import NetGen.")
    sys.exit(0)

from netgen.geom2d import SplineGeometry
geo = SplineGeometry()

geo.AddCircle(c=(0, 0),
              r=0.5,
              bc="circle",
              leftdomain=1,
              rightdomain=0)

geo.SetDomainMaxH(1, 1.0)

ngmsh = geo.GenerateMesh(maxh=1.0)  # if comment this out it breaks!  WHY??

#ngmsh.Save("test_netgen_reduced.vol")

# now try re-loading the mesh from file:
ngmsh2 = netgen.meshing.Mesh()
ngmsh2.Load("test_netgen_reduced.vol")
msh2 = Mesh(Mesh(ngmsh2,comm=COMM_WORLD).curve_field(2))  # convert to Firedrake mesh
VTKFile("test_netgen_reduced.pvd").write(msh2)

