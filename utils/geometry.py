from math import sqrt

import openmc
import numpy as np

from .material import fuel_mat, cladding_mat, water_mat

# Surfaces
fuel_surf = openmc.ZCylinder(r=9)
cladding_surf = openmc.ZCylinder(r=10)
water_surf = openmc.hexagonal_prism(edge_length=15, orientation='x', boundary_type='vacuum')

top_surf = openmc.ZPlane(z0=3500 / 2)
bottom_surf = openmc.ZPlane(z0=-3500 / 2)

lat_surf = openmc.rectangular_prism(width=75, height=75, boundary_type='vacuum')
hex_lat_surf = openmc.hexagonal_prism(edge_length=15*sqrt(3)*5/2+2.5, boundary_type='transmission')

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

lat = openmc.RectLattice()
lat.lower_left = (-25 * 3 / 2, -25 * 3 / 2)
lat.pitch = (25, 25)
lat.universes = np.tile(sub_universe, (3, 3))

lat.outer = container_universe

hex_lat = openmc.HexLattice()
hex_lat.center = (0,0)
hex_lat.pitch = [15*sqrt(3)]

lat_center = [sub_universe]
lat_ring_1 = [sub_universe]*6
lat_ring_2 = [sub_universe]*12

hex_lat.universes = [lat_ring_2, lat_ring_1, lat_center]
hex_lat.outer = container_universe

lat_cell = openmc.Cell(region=hex_lat_surf, fill=hex_lat)

universe = openmc.Universe(cells=[lat_cell])

#full_lat_cell = openmc.Cell()
# for i in range(6):
#  print(f"i = {i} - {universe.find((i*3,0,0))}\n\n")