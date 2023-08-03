from math import sqrt

import openmc
import numpy as np

from .material import fuel_mat, cladding_mat, water_mat, fuel_with_Gd_mat, absorber_mat
from .params import GeometryParams

p = GeometryParams()

# Surfaces
fuel_surf = openmc.ZCylinder(r=p.tvel_fuel_radius)
cladding_surf = openmc.ZCylinder(r=p.tvel_global_radius)
water_surf = openmc.hexagonal_prism(edge_length=p.tvel_step / sqrt(3), orientation='y', boundary_type='transmission')

tube_inner_surf = openmc.ZCylinder(r=p.tube_inner_radius)
tube_outer_surf = openmc.ZCylinder(r=p.tube_outer_radius)

abs_rod_inner_surf = openmc.ZCylinder(r=p.absorber_rod_inner_radius)
abs_rod_outer_surf = openmc.ZCylinder(r=p.absorber_rod_outer_radius)

top_surf = openmc.ZPlane(z0=p.tvel_heigh / 2)
bottom_surf = openmc.ZPlane(z0=-p.tvel_heigh / 2)

TVS_hex_lat_surf = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                          )

hex_lat_surf_1 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(0, p.TVS_edge_length * sqrt(3)))
hex_lat_surf_4 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(0, -p.TVS_edge_length * sqrt(3)))
hex_lat_surf_2 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(p.TVS_edge_length * 1.5, p.TVS_edge_length * sqrt(3) / 2))
hex_lat_surf_3 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(p.TVS_edge_length * 1.5, -p.TVS_edge_length * sqrt(3) / 2))
hex_lat_surf_5 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(-p.TVS_edge_length * 1.5, -p.TVS_edge_length * sqrt(3) / 2))
hex_lat_surf_6 = openmc.hexagonal_prism(edge_length=p.TVS_edge_length, orientation=p.orientation,
                                        origin=(-p.TVS_edge_length * 1.5, p.TVS_edge_length * sqrt(3) / 2))

hex_lat_surf = TVS_hex_lat_surf | hex_lat_surf_1 | hex_lat_surf_2 | hex_lat_surf_3 | hex_lat_surf_4 | hex_lat_surf_5 | hex_lat_surf_6

box = openmc.ZCylinder(r=40, boundary_type='reflective')
box_region = -box & -top_surf & +bottom_surf
# hex_lat_surf.boundary_type = 'reflective'

top_surf.boundary_type = 'vacuum'
bottom_surf.boundary_type = 'vacuum'

# Geometry

# 1 TVS container
TVS_container_cell = openmc.Cell(fill=water_mat, region=TVS_hex_lat_surf & -top_surf & +bottom_surf)
TVS_container_universe = openmc.Universe(cells=[TVS_container_cell])

# 7 TVS container
container_cell = openmc.Cell(fill=water_mat, region=box_region)
container_universe = openmc.Universe(cells=[container_cell])

# 1.1 tvel in water
fuel_cell = openmc.Cell(fill=fuel_mat, region=-fuel_surf & +bottom_surf & -top_surf)
cladding_cell = openmc.Cell(fill=cladding_mat, region=+fuel_surf & -cladding_surf & +bottom_surf & -top_surf)
water_cell = openmc.Cell(fill=water_mat, region=+cladding_surf & water_surf & +bottom_surf & -top_surf)

tvel_universe = openmc.Universe(cells=[fuel_cell, cladding_cell, water_cell])

# 1.2 tveg in water
fuel_with_Gd_cell = openmc.Cell(fill=fuel_with_Gd_mat, region=-fuel_surf & +bottom_surf & -top_surf)
cladding_with_Gd_cell = openmc.Cell(fill=cladding_mat, region=+fuel_surf & -cladding_surf & +bottom_surf & -top_surf)
water_with_Gd_cell = openmc.Cell(fill=water_mat, region=+cladding_surf & water_surf & +bottom_surf & -top_surf)

tvel_with_Gd_universe = openmc.Universe(cells=[fuel_with_Gd_cell, cladding_with_Gd_cell, water_with_Gd_cell])

# 1.3 tube in water
tube_cladding_cell = openmc.Cell(fill=cladding_mat,
                                 region=+tube_inner_surf & -tube_outer_surf & +bottom_surf & -top_surf)
tube_water_region = -tube_inner_surf | +tube_outer_surf & water_surf
tube_water_cell = openmc.Cell(fill=water_mat, region=tube_water_region & +bottom_surf & -top_surf)

empty_tube_universe = openmc.Universe(cells=[tube_water_cell, tube_cladding_cell])

# 1.4 absorber in tube
absorber_cell = openmc.Cell(fill=absorber_mat, region=-abs_rod_inner_surf & +bottom_surf & -top_surf)
absorber_cladding_cell = openmc.Cell(fill=cladding_mat,
                                     region=-abs_rod_outer_surf & +abs_rod_inner_surf & +bottom_surf & -top_surf)

abs_tube_water_inner_cell= openmc.Cell(fill=water_mat, region=+abs_rod_outer_surf & -tube_inner_surf & +bottom_surf & -top_surf)

abs_tube_cladding_cell = openmc.Cell(fill=cladding_mat,
                                     region=+tube_inner_surf & -tube_outer_surf & +bottom_surf & -top_surf)

abs_tube_water_outer_cell = openmc.Cell(fill=water_mat, region=+tube_outer_surf & water_surf & +bottom_surf & -top_surf)

absorber_tube_universe = openmc.Universe(
    cells=[absorber_cell, absorber_cladding_cell, abs_tube_water_inner_cell, abs_tube_cladding_cell,abs_tube_water_outer_cell])
#1.4.2 tube choosing

if p.rod_inserted:
    tube_universe = absorber_tube_universe
else:
    tube_universe = empty_tube_universe

# 2. 1 TVS lattice
TVS_hex_lat = openmc.HexLattice()
TVS_hex_lat.orientation = p.orientation
TVS_hex_lat.center = (0, 0)
TVS_hex_lat.pitch = [p.tvel_step]

TVS_lat_center = [empty_tube_universe]
TVS_lat_rings = []
for i in range(1, p.n_tvel_rows):
    TVS_lat_rings.append([tvel_universe] * 6 * i)
TVS_lat_rings[2] = [tvel_universe, tvel_universe, tube_universe] * 6
TVS_lat_rings[3] = [tvel_universe, tvel_universe, tvel_universe, tvel_with_Gd_universe] * 6
TVS_lat_rings[4] = [tube_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe] * 6
TVS_lat_rings[5] = [tvel_universe, tvel_universe, tvel_universe, tube_universe, tvel_universe,
                    tvel_universe] * 6
TVS_lat_rings[7] = [tvel_with_Gd_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe, tvel_universe,
                    tvel_universe, tvel_universe] * 6
TVS_lat_rings.reverse()
TVS_hex_lat.universes = [*TVS_lat_rings, TVS_lat_center]
TVS_hex_lat.outer = TVS_container_universe

TVS_lat_cell = openmc.Cell(region=TVS_hex_lat_surf, fill=TVS_hex_lat)

TVS_universe = openmc.Universe(cells=[TVS_lat_cell])
# universe = openmc.Universe(cells=[container_cell])

# 7 TVS lattice

hex_lat = openmc.HexLattice(lattice_id=228)
hex_lat.orientation = 'y'
hex_lat.center = (0, 0)
hex_lat.pitch = [p.TVS_edge_length * sqrt(3)]

lat_center = [TVS_universe]
lat_ring = [TVS_universe] * 6
hex_lat.universes = [lat_ring, lat_center]
hex_lat.outer = container_universe

lat_cell = openmc.Cell(region=box_region, fill=hex_lat)

universe = openmc.Universe(cells=[lat_cell])
