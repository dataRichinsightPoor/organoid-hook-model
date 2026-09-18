from dataclasses import replace, asdict
import numpy as np
import pytest
from organoid_hook import Parameters, simulate, summarize, hook_metrics
from organoid_hook.model import (
    initial_state, make_rhs, geometry, ligand_inventory, N, I,
    precomplex_amount, _rhs, _rhs_fast, NumericParameters,
)

@pytest.mark.parametrize("primary,secondary",[(0,0),(0,10),(10,0)])
def test_negative_controls(primary,secondary):
    s=summarize(simulate(primary,secondary,times=[72]))
    assert abs(s["committed_fraction"][0])<1e-9
    assert abs(s["permeability_fluorescence"][0])<1e-9

def test_receptor_baseline_stationary():
    p=Parameters()
    assert np.max(np.abs(make_rhs(p)(0,initial_state(p))))<1e-10

@pytest.mark.parametrize("order",["simultaneous","primary_first","secondary_first","precomplexed"])
def test_mass_conservation_and_nonnegativity(order):
    r=simulate(10,3,order=order)
    a,s=ligand_inventory(r)
    volumes,*_=geometry(Parameters())
    total=Parameters().bath_ul*1e-6+sum(volumes)
    mask=r["times"]>=6.1
    assert np.allclose(a[mask],10*total,rtol=2e-5,atol=1e-12)
    assert np.allclose(s[mask],3*total,rtol=2e-5,atol=1e-12)
    assert r["states"].min()>-1e-6
    z=r["states"][3:].reshape(Parameters().shells,N,-1)
    assert np.allclose(z[:,I["L"]]+z[:,I["E"]]+z[:,I["D"]]+z[:,I["X"]],1,atol=2e-7)

def test_accumulation_no_reporter_loss():
    s=summarize(simulate())
    assert np.diff(s["permeability_fluorescence"]).min()>-1e-9
    assert np.diff(s["delivered_payload_cumulative"]).min()>-1e-6

@pytest.mark.parametrize("loss",[0.0,0.1])
def test_article_fluorescence_history_integral(loss):
    """The article's history integral reproduces the implemented observation."""
    from scipy.integrate import trapezoid
    p=replace(Parameters(),reporter_loss_h=loss,fluorescence_saturation=0)
    times=np.linspace(0,72,7201)
    result=simulate(8.25404185268019,3,p=p,times=times,rtol=2e-8,atol=1e-11)
    z=result["states"][3:].reshape(p.shells,N,-1)
    _,cells,*_=geometry(p)
    weights=cells/cells.sum()
    optical=np.linspace(p.optical_core_weight,1,p.shells)
    omega=weights*optical/np.dot(weights,optical)
    for endpoint in (12,24,48,72):
        selected=times<=endpoint
        u=times[selected]
        entry=z[:,I["E"],selected]/p.membrane_delay_h
        history=trapezoid(entry*np.exp(-loss*(endpoint-u)),x=u,axis=1)
        expected=np.dot(omega,history)
        actual=summarize(result)["permeability_fluorescence"][selected][-1]
        assert np.isclose(expected,actual,atol=2e-6,rtol=0)

def test_zero_receptors():
    s=summarize(simulate(p=replace(Parameters(),copies_per_cell=0),times=[72]))
    assert abs(s["permeability_fluorescence"][0])<1e-9

def test_no_internalization():
    p=replace(Parameters(),kint_free=0,kint_primary=0,kint_ternary=0)
    assert summarize(simulate(p=p,times=[72]))["payload_copies"][0]==0

def test_no_release():
    p=replace(Parameters(),release_efficiency=0)
    assert summarize(simulate(p=p,times=[72]))["committed_fraction"][0]==0

def test_hook_and_rescue_in_tested_window():
    x=np.logspace(-2,3,13)
    low=[summarize(simulate(a,1,times=[72]))["permeability_fluorescence"][0] for a in x]
    high=[summarize(simulate(a,100,times=[72]))["permeability_fluorescence"][0] for a in x]
    assert hook_metrics(x,low)["hook_flag"]
    assert not hook_metrics(x,high)["hook_flag"]
    assert high[-1]>low[-1]+0.5

def test_solution_association_ablation_attenuates_but_does_not_require_zero_hook():
    p=replace(Parameters(),solution_binding=False)
    x=np.logspace(-2,3,13)
    y=[summarize(simulate(a,1,p=p,times=[72]))["permeability_fluorescence"][0] for a in x]
    # R+C remains a productive route. Its competition with A can leave a
    # residual hook; an ablation must not be forced to fit a preferred story.
    assert y[-1] > .75
    assert hook_metrics(x,y)["hook_depth"] < .25

def test_dose_zero_delay_orders_equivalent():
    a=simulate(order="simultaneous",times=[72])["states"]
    for order in ("primary_first","secondary_first"):
        b=simulate(order=order,delay_h=0,times=[72])["states"]
        assert np.allclose(a,b)

def test_tighter_solver_tolerance():
    a=summarize(simulate(100,3,times=[24,48,72]))
    b=summarize(simulate(100,3,times=[24,48,72],rtol=2e-8,atol=1e-11))
    assert np.allclose(a["permeability_fluorescence"],b["permeability_fluorescence"],atol=2e-4)

def test_python_accelerated_rhs_parity():
    p=Parameters()
    v,c,beta,r0,g=geometry(p)
    kd=np.log(2)/p.receptor_half_life_h
    synth=kd*p.kint_free*r0/(p.krecycle+kd)
    y=initial_state(p)+np.random.default_rng(42).uniform(0,0.1,3+p.shells*N)
    args=(0,y,NumericParameters(**asdict(p)),v,beta,r0,g,synth,p.bath_ul*1e-6)
    assert np.allclose(_rhs(*args),_rhs_fast(*args),atol=1e-10)

def test_precomplex_root():
    c=precomplex_amount(10,3,0.3)
    assert 0<c<3
    assert np.isclose((10-c)*(3-c),0.3*c)

@pytest.mark.parametrize("changes",[{"copies_per_cell":-1},{"radius_um":0},{"shells":1.5},{"release_efficiency":1.2},{"kon_a":float("nan")}])
def test_invalid_parameters(changes):
    with pytest.raises(ValueError):simulate(p=replace(Parameters(),**changes))

def test_invalid_times():
    with pytest.raises(ValueError):simulate(times=[0,2,1])

@pytest.mark.parametrize("order",["primary_first","secondary_first"])
def test_endpoint_only_after_delayed_addition(order):
    a=simulate(order=order,times=[72])["states"]
    b=simulate(order=order)["states"][:,-1:]
    assert np.allclose(a,b)

def test_invalid_order():
    with pytest.raises(ValueError):simulate(order="washed")

def test_hook_low_signal_not_flagged():
    assert not hook_metrics([1,2,3],[0,0.001,0])["hook_flag"]

def test_reporter_loss_does_not_change_killing():
    a=summarize(simulate(p=Parameters(),times=[72]))
    b=summarize(simulate(p=replace(Parameters(),reporter_loss_h=.1),times=[72]))
    assert np.allclose(a["committed_fraction"],b["committed_fraction"],atol=1e-6)
    assert a["permeability_fluorescence"][0]>b["permeability_fluorescence"][0]

def test_saturation_cannot_create_hook():
    x=np.linspace(0,1,101)
    for sat in (0,1,100):
        assert np.all(np.diff((1+sat)*x/(1+sat*x))>=0)
