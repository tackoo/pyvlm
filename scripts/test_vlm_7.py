#%% Load Dependencies
from pyvlm import LatticeResult, LatticeOptimum
from pyvlm import latticesystem_from_json
from pyvlm.tools import elliptical_lift_distribution

#%% Create Lattice System
jsonfilepath = r'..\files\Straight_Wing_Cosine_b100_c1.json'
lsys = latticesystem_from_json(jsonfilepath)
print(lsys)

#%% Create Elliptical Distribution
lell = elliptical_lift_distribution(lsys.srfcs[0].strpy, lsys.bref, 10000.0)

#%% Create Elliptical Optimum
lopt_ell = LatticeOptimum('Equivalent Elliptical', lsys)
lopt_ell.set_lift_distribution(lell, rho=1.0, speed=100.0)
print(lopt_ell)

#%% Determine Optimal Twist
al_ell = lopt_ell.optimum_strip_twist(crit=1e-1)

#%% Print Result
print(lopt_ell.res)

#%% Plot Optimal Wash
axw = None
axw = lopt_ell.res.plot_trefftz_wash_distribution(ax=axw)
axw = lopt_ell.res.plot_panel_near_field_velocities(ax=axw, component='z')

#%% Print Near Field Results
print(lopt_ell.res.panel_near_field_results)
