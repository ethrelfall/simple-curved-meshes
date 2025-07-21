from firedrake import *

mesh = Mesh("test_circle.msh")
V = FunctionSpace(mesh, "CG", 1)
f = Function(V)
File("test_curved_mesh.pvd").write(f)
