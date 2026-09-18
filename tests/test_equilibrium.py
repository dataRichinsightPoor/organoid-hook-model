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

def test_article_tenfold_primary_with_secondary_excess():
    # Receptor-dilute analytical example, not a dynamic organoid simulation.
    a=np.array([1.,10.])
    fraction=ternary_equilibrium(a,1000.,.001)/.001
    assert np.allclose(fraction,[.500,.909],atol=.0002,rtol=0)
    assert np.isclose(fraction[1]/fraction[0],1.82,atol=.003)
    assert np.allclose(fraction,a/(1+a),rtol=.0004)
    grid=np.geomspace(1.,10.,101)
    assert np.all(np.diff(ternary_equilibrium(grid,1000.,.001))>0)
    assert peak_primary_nm(1000.)>10.

def test_finite_secondary_excess_is_not_a_universal_monotonicity_rule():
    # Test the exact finite-S criterion, not an extreme-affinity tiny decline.
    ka=1e-3
    ks=.3
    peak=peak_primary_nm(1000.,ka,ks)
    assert 54<peak<55
    ratio=ternary_equilibrium(1000.,1000.,.001,ka,ks)/ternary_equilibrium(peak,1000.,.001,ka,ks)
    assert ratio<.99
    assert np.isclose(1000/peak,1+np.sqrt(ks/ka),rtol=.001)
    threshold=ka+np.sqrt(ka*ks)
    for s in (.5*threshold,2*threshold):
        assert (peak_primary_nm(s,ka,ks)<s)==(s>threshold)
