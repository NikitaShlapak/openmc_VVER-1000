from math import sqrt

import numpy as np
import openmc
from openmc import deplete
from openmc import stats

from models.utils.params import GeometryParams, SourceParams

openmc.config['cross_sections'] = '/media/main/data/neutron_libs/jeff-3.3-hdf5/cross_sections.xml'
openmc.config['chain_file'] = '/media/main/data/neutron_libs/chains/chain_endfb71_pwr.xml'

from models.utils.geometry import universe
from models.utils.material import water_mat, cladding_mat, fuel_mat, fuel_with_Gd_mat, absorber_mat

import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Materials
    print(fuel_with_Gd_mat.nuclides)
    materials = openmc.Materials([fuel_mat, water_mat, cladding_mat, fuel_with_Gd_mat, absorber_mat])

    # Geometry
    geometry = openmc.Geometry(universe)
    params = GeometryParams()

    # Plotting by universe...
    colors = {water_mat: (120, 120, 255), cladding_mat: 'black', fuel_mat: (0, 200, 0), fuel_with_Gd_mat: (0, 100, 0),
              absorber_mat: (250, 125, 125)}
    color_data = dict(color_by='material', colors=colors)
    width = np.array([params.TVS_edge_length * 6, params.TVS_edge_length * 6, ])
    scale = 5.1 / 2
    fig, ax = plt.subplots(2, 2)

    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data,
                  origin=(0, 0, GeometryParams.tvel_heigh / 2 - 1), axes=ax[0][0])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data, origin=(0, 0, 0), axes=ax[1][1])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xz', **color_data,
                  origin=(0, 0, -GeometryParams.tvel_heigh / 2 + 1),
                  axes=ax[0][1])
    universe.plot(width=width / scale, pixels=(250, 250), basis='xy', **color_data, origin=(0, 0, 0), axes=ax[1][0])
    plt.savefig('data/plots/geometry.jpg')

    # ...and by openmc.Plots
    plots = [openmc.Plot(), openmc.Plot(), openmc.Plot(), openmc.Plot(), ]
    for i in range(4):
        plots[i].width = width
        plots[i].pixels = (500, 500)
        plots[i].basis = 'xz'
        plots[i].color_by = 'material'
        plots[i].colors = colors
    plots[0].origin = (0, 0, GeometryParams.tvel_heigh / 2 - 1)
    plots[2].origin = (0, 0, -GeometryParams.tvel_heigh / 2 - 1)
    plots[-1].basis = 'xy'
    plots[-1].pixels = (3200, 3200)

    plots = openmc.Plots(plots)

    # Settings
    setting = openmc.Settings()
    setting.batches = 70
    setting.inactive = 20
    setting.particles = 1000
    # setting.run_mode = 'fixed source'

    source = openmc.Source()
    source.space = stats.Box([-100, -100, -350 / 2], [100, 100, 350 / 2], only_fissionable=True)
    # n = SourceParams.neutrons_per_second
    # source.time = stats.Uniform(n, 1)
    setting.source = source

    # Tallies
    flux_tally = openmc.Tally(name='flux')
    flux_tally.scores = ['flux']

    U_tally = openmc.Tally(name='fuel')
    U_tally.scores = ['fission', 'total', 'absorption', 'elastic', 'scatter', 'decay-rate']
    U_tally.nuclides = ['U235', 'U238', 'Gd152', 'O16', 'H1']

    heat_tally = openmc.Tally(name='heating')
    heat_tally.scores = ['heating']
    heat_tally.nuclides = ['U235', 'U238', 'Gd152', 'O16', 'H1','Zr90']

    tallies = openmc.Tallies([U_tally, flux_tally, heat_tally])

    # XML export
    materials.export_to_xml('data/xmls/materials.xml')
    geometry.export_to_xml('data/xmls/geometry.xml')
    setting.export_to_xml('data/xmls/settings.xml')
    tallies.export_to_xml('data/xmls/tallies.xml')
    plots.export_to_xml('data/xmls/plots.xml')

    # RUN
    # model = openmc.Model(geometry=geometry, materials=materials, tallies=tallies, plots=plots, settings=setting)
    if params.rod_inserted:
        rods_cwd = 'rods_in'
    else:
        rods_cwd = 'rods_out'
    openmc.plot_geometry(path_input='data/xmls/', output=False, )
    openmc.run(output=True, path_input='data/xmls/')

    # Deplition
    # operator = deplete.CoupledOperator(model=model)
    # power = 1000e6/163*7
    # time_steps = [1]
    # integrator = deplete.PredictorIntegrator(operator, time_steps, power, timestep_units='s')
    # integrator.integrate()

    # with openmc.StatePoint('statepoint.100.h5') as sp:
    #     print(sp.keff)
    #     output_tally = sp.get_tally(name='fuel')
    #     df = output_tally.get_pandas_dataframe()
    #     # df.to_csv('out_fuel_3.6.csv')
    #     output_tally = sp.get_tally(name='flux')
    #     flux = output_tally.get_pandas_dataframe()
    #     # flux.to_csv('out_flux_3.6.csv')
    #     output_tally = sp.get_tally(name='heating')
    #     heat = output_tally.get_pandas_dataframe()
    #     # flux.to_csv('out_flux_3.6.csv')
    #     print(df, flux,heat, sep='\n\n')
