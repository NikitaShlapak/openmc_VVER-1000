from math import sqrt

import openmc
import numpy as np

from .material import fuel_mat, cladding_mat, water_mat
from .params import GeometryParams
p = GeometryParams()

# Surfaces
fuel_surf = openmc.ZCylinder(r=p.tvel_fuel_radius)
cladding_surf = openmc.ZCylinder(r=p.tvel_global_radius)
water_surf = openmc.hexagonal_prism(edge_length=p.tvel_step, orientation=p.orientation, boundary_type='periodic')

top_surf = openmc.ZPlane(z0=p.tvel_heigh / 2)
bottom_surf = openmc.ZPlane(z0=-p.tvel_heigh / 2)

hex_lat_surf = openmc.hexagonal_prism(edge_length=p.TVS_edge_lenght,orientation=p.orientation, boundary_type='vacuum')

top_surf.boundary_type = 'vacuum'
bottom_surf.boundary_type = 'vacuum'

# Geometry
container_cell = openmc.Cell(fill=water_mat, region=hex_lat_surf & -top_surf & +bottom_surf)
container_universe = openmc.Universe(cells=[container_cell])

# 1. tvel in water
fuel_cell = openmc.Cell(fill=fuel_mat, region=-fuel_surf & +bottom_surf & -top_surf)
cladding_cell = openmc.Cell(fill=cladding_mat, region=+fuel_surf & -cladding_surf & +bottom_surf & -top_surf)
water_cell = openmc.Cell(fill=water_mat, region=+cladding_surf & water_surf & +bottom_surf & -top_surf)

sub_universe = openmc.Universe(cells=[fuel_cell, cladding_cell, water_cell])

# 2. lattice


hex_lat = openmc.HexLattice()
hex_lat.orientation=p.orientation
hex_lat.center = (0,0)
hex_lat.pitch = [p.tvel_step]

lat_center = [sub_universe]
lat_rings = []
for i in range(1, p.n_tvel_rows):
    lat_rings.append([sub_universe]*6*i)
lat_rings.reverse()
hex_lat.universes = [*lat_rings, lat_center]
hex_lat.outer = container_universe

lat_cell = openmc.Cell(region=hex_lat_surf, fill=hex_lat)

universe = openmc.Universe(cells=[lat_cell])
