from math import pi

import openmc
import neutronics_material_maker as nmm

from models.utils.params import MaterialParams, GeometryParams

# Materials
fuel_mat = openmc.Material(name='Uranium Oxide')
fuel_mat.add_element('U',1, enrichment=MaterialParams.U235_enrichment_high)
fuel_mat.add_element('O', 2)
fuel_mat.set_density('g/cm3', 10.5)
fuel_mat.volume = GeometryParams().tvel_fuel_radius**2*pi*GeometryParams().tvel_heigh*(312-18)*7

Gd2o3_mat = openmc.Material(name='Gadolinium Oxide')
Gd2o3_mat.add_element('Gd',2)
Gd2o3_mat.add_element('O', 3)
Gd2o3_mat.set_density('g/cm3', 7.41)

fuel_with_Gd_mat = openmc.Material.mix_materials(materials=(fuel_mat,Gd2o3_mat),fracs=(0.95,0.05),percent_type='wo',name='U+Gg Oxide')
fuel_with_Gd_mat.volume = GeometryParams().tvel_fuel_radius**2*pi*GeometryParams().tvel_heigh*18*7

water_mat = nmm.Material.from_library(name='Water, Liquid').openmc_material
cladding_mat = nmm.Material.from_library(name='Zircaloy-2').openmc_material
absorber_mat = nmm.Material.from_library(name='Boron Carbide (B4C)').openmc_material
