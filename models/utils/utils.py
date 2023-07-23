import neutronics_material_maker as nmm


def profile_material(material_name="Uranium Oxide", n_profs=10):
    material_profiled = {"name": material_name}
    for i in range(n_profs):
        props = {"name": material_name}
        mat = nmm.Material.from_library(**props)
        prof_name = f"{material_name} r{i + 1}"
        mat.name = prof_name
        material_profiled[prof_name] = mat.openmc_material
    return material_profiled


def search_in_library(material: str):
    mats = list(nmm.material_dict.keys())
    for mat in mats:
        if material.lower() in mat.lower():
            print(mat)
