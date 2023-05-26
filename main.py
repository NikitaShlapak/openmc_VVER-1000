import openmc
openmc.config['cross_sections'] = '/home/main/cross_section_libs/jeff32/jeff-3.3-hdf5/cross_sections.xml'

from utils.utils import profile_material

print(profile_material(material_name='Water, Liquid'))