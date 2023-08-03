import openmc
from openmc import deplete

from models.utils.material import fuel_mat

results = openmc.deplete.Results("./depletion_results.h5")
time, k = results.get_keff()
time /= (24 * 60 * 60)

print(time,k, sep='\n\n\n')

time, output_tally = results.get_reaction_rate(mat=fuel_mat,nuc='U238',rx='fission')
# df = output_tally.get_pandas_dataframe()
print(output_tally)