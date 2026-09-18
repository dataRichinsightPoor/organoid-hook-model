import numpy as np
from organoid_hook.equilibrium import ternary_equilibrium,peak_primary_nm

def test_equilibrium_zero_controls():
    assert ternary_equilibrium(0,1,1)==0
    assert ternary_equilibrium(1,0,1)==0
    assert ternary_equilibrium(1,1,0)==0

def test_analytic_peak_matches_dense_grid():
    for s in (.1,3,100):
        peak=peak_primary_nm(s)
        x=np.geomspace(peak/10,peak*10,10001)
        y=ternary_equilibrium(x,s,.001)
        assert np.isclose(x[np.argmax(y)],peak,rtol=1e-4)

def test_high_primary_asymptote():
    a=1e7;s=3;r=.01
    assert np.isclose(ternary_equilibrium(a,s,r),r*s/a,rtol=1e-5)

def test_more_secondary_moves_equilibrium_peak():
    assert peak_primary_nm(100)>peak_primary_nm(3)>peak_primary_nm(.1)
