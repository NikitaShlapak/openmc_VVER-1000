import openmc
import neutronics_material_maker as nmm

from models.utils.params import MaterialParams

# Materials
fuel_mat = openmc.Material(name='Uranium Oxide')
fuel_mat.add_element('U',1, enrichment=MaterialParams.U235_enrichment_high)
fuel_mat.add_element('O', 2)
fuel_mat.set_density('g/cm3', 10.5)

water_mat = nmm.Material.from_library(name='Water, Liquid').openmc_material
cladding_mat = nmm.Material.from_library(name='Zircaloy-2').openmc_material
