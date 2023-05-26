import openmc
import neutronics_material_maker as nmm

# Materials
fuel_mat = nmm.Material.from_library(name='Uranium Oxide').openmc_material
water_mat = nmm.Material.from_library(name='Water, Liquid').openmc_material
cladding_mat = nmm.Material.from_library(name='Zircaloy-2').openmc_material
