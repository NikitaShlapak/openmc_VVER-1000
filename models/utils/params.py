from math import sqrt
class GeometryParams:
    tvel_fuel_radius = 0.72
    tvel_global_radius = 0.91
    tvel_heigh = 350.0

    orientation = 'x'

    n_tvel_rows = 11
    tvel_step = 1.275*sqrt(3)

    def __init__(self):
        self.TVS_edge_lenght =self.tvel_step*(self.n_tvel_rows)
        # print(self.TVS_edge_lenght)

class MaterialParams:
    U235_enrichment_high = 3.6
    U235_enrichment_medium = 2.4
    U235_enrichment_low = 1.6