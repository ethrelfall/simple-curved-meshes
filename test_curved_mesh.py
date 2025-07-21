from firedrake import *

mesh = Mesh("test_circle.msh")
V = FunctionSpace(mesh, "CG", 2)
f = Function(V)
File("test_curved_mesh.pvd").write(f)
