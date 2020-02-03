#%% Import Dependencies
from IPython.display import display
from pyvlm import LatticeResult, LatticeOptimum
from pyvlm.tools import bell_lift_distribution, elliptical_lift_distribution
from pyvlm import latticesystem_from_json

#%% Inputs
L = 64.498 # N
rho = 1.206 # kg/m**3
V = 12.9173511047957 # m/s

#%% Low AR Wing
jsonfilepath1 = r'..\files\Test_rhofw_elliptical.json'
lsys1 = latticesystem_from_json(jsonfilepath1)
display(lsys1)

#%% High AR Wing
jsonfilepath2 = r'..\files\Test_rhofw_bell.json'
lsys2 = latticesystem_from_json(jsonfilepath2)
display(lsys2)

#%% Low AR Wing Optimum
lres1 = LatticeResult('Low AR Wing Elliptical', lsys1)
lres1.set_state(speed=V)
lres1.set_density(rho=rho)

l1 = elliptical_lift_distribution(lsys1.srfcs[0].strpy, lsys1.bref, L)
lres1.set_lift_distribution(l1, rho=rho, speed=V)
display(lres1)

lopt1 = LatticeOptimum('Low AR Wing Elliptical', lsys1)
lopt1.set_lift_distribution(l1, rho=rho, speed=V)
lopt1.add_record('l', strplst='Mirrored')
display(lopt1)

#%% High AR Wing Constrained Optimum
lres2 = LatticeResult('High AR Wing Bell', lsys2)
lres2.set_state(speed=V)
lres2.set_density(rho=rho)

l2 = bell_lift_distribution(lsys2.srfcs[0].strpy, lsys2.bref, L)
lres2.set_lift_distribution(l2, rho=rho, speed=V)
display(lres2)

lopt2 = LatticeOptimum('High AR Wing Bell', lsys2)
lopt2.set_lift_distribution(l2, rho=rho, speed=V)
lopt2.add_record('l', strplst='Mirrored')
display(lopt2)

#%% Print Drag Ratio
Di1 = lopt1.return_induced_drag()
Di2 = lopt2.return_induced_drag()

print(f'\nDrag Ratio = {Di2/Di1*100:.2f}%')

bm1 = lopt1.record[0].evaluate(lopt1.pmat)
bm2 = lopt2.record[0].evaluate(lopt2.pmat)

print(f'Elliptical Root Bending Moment = {bm1:.2f} N.m')
print(f'Bell Root Bending Moment = {bm2:.2f} N.m')

print(f'Elliptical Centre of Lift = {bm1/(L/2):.3f} m')
print(f'Bell Centre of Lift = {bm2/(L/2):.3f} m')

#%% Plots
from matplotlib.pyplot import subplots

fig, (axl, axd, axw) = subplots(nrows=3, figsize=(12, 8))

axl.grid(True)
axl = lres1.plot_trefftz_lift_distribution(ax=axl)
axl = lres2.plot_trefftz_lift_distribution(ax=axl)
axl.set_ylabel('Lift Distribution [N/m]')

axd.grid(True)
axd = lres1.plot_trefftz_drag_distribution(ax=axd)
axd = lres2.plot_trefftz_drag_distribution(ax=axd)
axd.set_ylabel('Drag Distribution [N/m]')

axw.grid(True)
axw = lres1.plot_trefftz_wash_distribution(ax=axw)
axw = lres2.plot_trefftz_wash_distribution(ax=axw)
axw.set_ylabel('Wash Distribution [m/s]')

_ = axw.set_xlabel('Span Coordinate - y [m]')
