# test_netgen.py
# testing Firedrake Netgen integration stuff at 
# https://www.firedrakeproject.org/demos/netgen_mesh.py.html
# working toward curved meshes in Firedrake
# ultimate aim is to do MAST-U divertor with curved tiles in FEM

# what can this script do:
# 1. Create a very simple mesh of a square domain containing a circle using NetGen integration.
# 2. Save that mesh in Netgen .vol format.
# 3. Load that mesh in Netgen .vol format.
# 4. Perform a very simple electrostatics calculation on the mesh (Polarized dielectric in uniform field).

from firedrake import *

try:
    import netgen
except ImportError:
    import sys
    warning("Unable to import NetGen.")
    sys.exit(0)

from netgen.geom2d import SplineGeometry
geo = SplineGeometry()

geo = SplineGeometry()
geo.AddRectangle(p1=(-1, -1),
                 p2=(1, 1),
                 bc="rectangle",
                 leftdomain=1,
                 rightdomain=0)
geo.AddCircle(c=(0, 0),
              r=0.5,
              bc="circle",
              leftdomain=2,
              rightdomain=1)

# Flagging for the inside of the disk with a different material IDs
geo.SetMaterial(1, "outer")
geo.SetMaterial(2, "inner")
geo.SetDomainMaxH(2, 1.0)

ngmsh = geo.GenerateMesh(maxh=1.0)
# Generating a Firedrake mesh from the NetGen mesh
msh = Mesh(Mesh(ngmsh,comm=COMM_WORLD).curve_field(2))  # convert to Firedrake mesh
VTKFile("test_netgen_msh.pvd").write(msh)

# now try output a netgen mesh
# formats: see
# https://forum.freecad.org/viewtopic.php?t=26655
# was eventually guided by this to use the .vol version, .msh didn't work (loaded mesh was empty)
# https://forum.ngsolve.org/t/error-when-re-loading-mesh-from-file/2008

ngmsh.Save("test_netgen_ngmsh.vol")
# here are some other formats (at least some do not re-load correctly):
#ngmsh.Export("test_netgen_ngmsh.msh", "Gmsh Format")
#ngmsh.Export("test_netgen_ngmsh.msh", "Gmsh2 Format")
#ngmsh.Export("test_netgen_ngmsh.msh", "Neutral Format")

# now try re-loading the mesh from file:
ngmsh2 = netgen.meshing.Mesh()
ngmsh2.Load("test_netgen_ngmsh.vol")
ngmsh2.Save("test_netgen_ngmsh2.vol")  # save again to check by inspection
msh2 = Mesh(Mesh(ngmsh2,comm=COMM_WORLD).curve_field(2))  # convert to Firedrake mesh
VTKFile("test_netgen_msh2.pvd").write(msh2)


# now try to solve a test problem on either the original or the re-loaded mesh
# maybe later on try out some FEEC spaces - vector solves ..

V = FunctionSpace(msh, "CG", 2)
VD = FunctionSpace(msh, "DG", 0)  # this is DG because dielectric constant is a discontinuous function
x, y = SpatialCoordinate(msh)
a = 0.50  # dielectric disc radius, must be consistent with r=0.5 in mesh
eps_in = 10.0  # dielectric const of disc (unit outside)
eps = Function(VD) # this is dielectric constant
eps.interpolate(conditional(le(x**2+y**2, 0.25), eps_in, 1.0))
phi_out = Function(V)
phi_out.interpolate(x+a*a*((1-eps_in)/(1+eps_in))*x/(x**2+y**2))  # this is the analytic "outside" potential solution
u = TrialFunction(V)
v = TestFunction(V)

a = inner(eps*grad(u), grad(v))*dx
f = Function(V)  # dummy as RHS is zero
f.interpolate(0.0*x)
L = inner(f,v)*dx

phi = Function(V)

bc = DirichletBC(V, phi_out, "on_boundary")

solve( a==L, phi, bcs=bc)

phi.rename("potential")
eps.rename("dielectric_const")
VTKFile("test_netgen_field.pvd").write(phi, eps)

quit()

# here is experiment loading a converted mesh e.g. from meshio
# I made a curved Gmsh mesh test_circle.msh and converted to .vol using meshio
# i.e. meshio convert test_circle.msh test_circle.vol
# for meshio info see
# https://pypi.org/project/meshio/

ngmsh3 = netgen.meshing.Mesh()
ngmsh3.Load("test_circle.vol")  # doesn't work
#ngmsh3.Load("test_circle_straight.vol")  # OK (stuff without curved edges seems to work OK)
msh3 = Mesh(Mesh(ngmsh3,comm=COMM_WORLD).curve_field(2))
VTKFile("output/MeshExample3.pvd").write(msh3)

print("Finished.")

quit()

