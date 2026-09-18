"""Finite-volume reaction/transport model. Concentrations nM; time hours.

All defaults are illustrative assumptions, not estimates for any real reagent.
Receptor kinetics are a fixed-population approximation (no death feedback).
"""
from dataclasses import dataclass, asdict, replace
from collections import namedtuple
import numpy as np
from scipy.integrate import solve_ivp

NA = 6.02214076e23
# Per shell: extracellular A,S,C; surface R,B,T; endosomal U,V,W;
# intracellular payload P; damage Q; live L; committed E; permeable D;
# inaccessible reporter X; destroyed primary LA; destroyed secondary LS;
# cumulative delivered payload J; extracellular LDH-like reporter H.
NAMES = ("A","S","C","R","B","T","U","V","W","P","Q","L","E","D","X","LA","LS","J","H")
N = len(NAMES)
I = {name: i for i, name in enumerate(NAMES)}
A_,S_,C_,R_,B_,T_,U_,V_,W_,P_,Q_,L_,E_,D_,X_,LA_,LS_,J_,H_ = range(N)

@dataclass(frozen=True)
class Parameters:
    shells: int = 3
    radius_um: float = 150
    organoids: int = 20
    bath_ul: float = 100
    extracellular_fraction: float = 0.2
    cells_per_tissue_um3: float = 1 / 2000
    copies_per_cell: float = 1e5
    core_copy_ratio: float = 1.0
    diffusion_um2_s: float = 3.0
    complex_diffusion_ratio: float = 0.65
    kon_a: float = 0.36       # nM^-1 h^-1
    kd_a_nm: float = 1.0
    kon_s: float = 0.36
    kd_s_nm: float = 0.3
    solution_binding: bool = True
    kint_free: float = 0.04
    kint_primary: float = 0.12
    kint_ternary: float = 0.12
    krecycle: float = 0.06
    receptor_half_life_h: float = 12
    payload_yield: float = 1.0
    release_efficiency: float = 0.2
    payload_half_life_h: float = 12
    payload_p50: float = 1000
    damage_rate_h: float = 0.15
    protein_recovery_half_life_h: float = 24
    death_rate_h: float = 0.12
    damage_half: float = 0.45
    hill: float = 3
    membrane_delay_h: float = 6
    reporter_loss_h: float = 0.0
    ldh_loss_h: float = 0.03
    optical_core_weight: float = 0.7
    fluorescence_saturation: float = 0.0
    atp_suppression: float = 0.35

    def validate(self):
        for key,value in asdict(self).items():
            if isinstance(value, bool):
                continue
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{key} must be finite and nonnegative")
        if not isinstance(self.shells,int) or not 1 <= self.shells <= 30:
            raise ValueError("shells must be an integer in [1,30]")
        if not isinstance(self.organoids,int) or self.organoids < 1:
            raise ValueError("organoids must be a positive integer")
        positive=("radius_um","bath_ul","cells_per_tissue_um3","extracellular_fraction",
                  "kd_a_nm","kd_s_nm","receptor_half_life_h","payload_half_life_h",
                  "payload_p50","protein_recovery_half_life_h","damage_half","hill",
                  "membrane_delay_h","complex_diffusion_ratio")
        for key in positive:
            if getattr(self,key)<=0: raise ValueError(f"{key} must be positive")
        for key in ("extracellular_fraction","release_efficiency","optical_core_weight","atp_suppression"):
            if getattr(self,key)>1: raise ValueError(f"{key} must not exceed 1")

def geometry(p):
    edges=np.linspace(0,p.radius_um,p.shells+1)
    centers=(edges[1:]+edges[:-1])/2
    tissue=4*np.pi/3*np.diff(edges**3)*p.organoids
    volumes=tissue*p.extracellular_fraction*1e-15 # liters
    cells=tissue*p.cells_per_tissue_um3
    beta=cells/(NA*volumes)*1e9 # nM per molecule/cell
    copies=p.copies_per_cell*np.linspace(p.core_copy_ratio,1,p.shells)
    r0=beta*copies
    # Interface conductance in L/h; center no-flux and finite bath.
    areas=4*np.pi*edges[1:]**2*p.organoids
    distances=np.r_[np.diff(centers),p.radius_um-centers[-1]]
    conductance=p.diffusion_um2_s*3600*areas/distances*1e-15*p.extracellular_fraction
    return volumes,cells,beta,r0,conductance

def initial_state(p):
    volumes,cells,beta,r0,g=geometry(p)
    y=np.zeros(3+p.shells*N)
    z=y[3:].reshape(p.shells,N)
    z[:,I["R"]]=r0
    kd=np.log(2)/p.receptor_half_life_h
    z[:,I["U"]]=p.kint_free*r0/(p.krecycle+kd)
    z[:,I["L"]]=1
    return y

NumericParameters = namedtuple("NumericParameters", Parameters.__dataclass_fields__)

def _rhs(t,y,p,volumes,beta,r0,g,synthesis,bath):
    kd=np.log(2)/p.receptor_half_life_h
    diff=np.array([1,1,p.complex_diffusion_ratio])
    koff_a=p.kon_a*p.kd_a_nm
    koff_s=p.kon_s*p.kd_s_nm
    dy=np.zeros_like(y)
    z=y[3:].reshape(p.shells,N)
    dz=dy[3:].reshape(p.shells,N)
    # Counterfactual ablation removes association, never dissociation of C
    # released from T. This deliberately breaks equilibrium detailed balance.
    solution_on=p.kon_s if p.solution_binding else 0.
    fb=solution_on*y[0]*y[1]-koff_s*y[2]
    dy[:3]+=np.array([-fb,-fb,fb])
    f=solution_on*z[:,0]*z[:,1]-koff_s*z[:,2]
    dz[:,:3]+=f[:,None]*np.array([-1,-1,1])
    for j in range(p.shells):
        outside=z[j+1,:3] if j+1<p.shells else y[:3]
        flux=g[j]*diff*(outside-z[j,:3])
        dz[j,:3]+=flux/volumes[j]
        if j+1<p.shells:
            dz[j+1,:3]-=flux/volumes[j+1]
        else:
            dy[:3]-=flux/bath
    A,S,C,R,B,T,U,V,W,P,Q,L,E,D,X,LA,LS,J,H=z.T
    f1=p.kon_a*A*R-koff_a*B
    f2=p.kon_s*S*B-koff_s*T
    f3=p.kon_a*C*R-koff_a*T
    dz[:,A_]-=f1
    dz[:,S_]-=f2
    dz[:,C_]-=f3
    dz[:,R_]+=synthesis-f1-f3-p.kint_free*R+p.krecycle*U
    dz[:,B_]+=f1-f2-p.kint_primary*B+p.krecycle*V
    dz[:,T_]+=f2+f3-p.kint_ternary*T+p.krecycle*W
    dz[:,U_]+=p.kint_free*R-(p.krecycle+kd)*U
    dz[:,V_]+=p.kint_primary*B-(p.krecycle+kd)*V
    dz[:,W_]+=p.kint_ternary*T-(p.krecycle+kd)*W
    delivery=kd*W/beta*p.payload_yield*p.release_efficiency
    dz[:,P_]+=delivery-np.log(2)/p.payload_half_life_h*P
    dz[:,J_]+=delivery
    dz[:,LA_]+=kd*(V+W)
    dz[:,LS_]+=kd*W
    dz[:,Q_]+=p.damage_rate_h*P/(p.payload_p50+P)*(1-Q)-np.log(2)/p.protein_recovery_half_life_h*Q
    hazard=p.death_rate_h*np.maximum(Q,0)**p.hill/(p.damage_half**p.hill+np.maximum(Q,0)**p.hill)
    commit=hazard*L
    permeabilize=E/p.membrane_delay_h
    dz[:,L_]-=commit
    dz[:,E_]+=commit-permeabilize
    dz[:,D_]+=permeabilize-p.reporter_loss_h*D
    dz[:,X_]+=p.reporter_loss_h*D
    dz[:,H_]+=permeabilize-p.ldh_loss_h*H
    return dy

try:
    from numba import njit
    _rhs_fast = njit(cache=True)(_rhs)
except ImportError:
    _rhs_fast = _rhs

def make_rhs(p):
    volumes,cells,beta,r0,g=geometry(p)
    bath=p.bath_ul*1e-6
    kd=np.log(2)/p.receptor_half_life_h
    synthesis=kd*p.kint_free*r0/(p.krecycle+kd)
    numeric=NumericParameters(**asdict(p))
    return lambda t,y: _rhs_fast(t,y,numeric,volumes,beta,r0,g,synthesis,bath)

def precomplex_amount(a,s,kd):
    """Stable positive quadratic root for 1:1 equilibrium, in nM."""
    total=a+s+kd
    return 2*a*s/(total+np.sqrt(max(0,total*total-4*a*s))) if a*s else 0.

def simulate(primary_nm=10.,secondary_nm=1.,duration_h=72.,order="simultaneous",
             delay_h=6.,p=None,times=None,rtol=2e-6,atol=1e-9):
    p=p or Parameters()
    p.validate()
    for key,value in dict(primary_nm=primary_nm,secondary_nm=secondary_nm,duration_h=duration_h,delay_h=delay_h).items():
        if not np.isfinite(value) or value<0: raise ValueError(f"{key} must be finite and nonnegative")
    if duration_h<=0: raise ValueError("duration_h must be positive")
    if order not in ("simultaneous","primary_first","secondary_first","precomplexed"):
        raise ValueError("Unknown order of addition")
    if order in ("primary_first","secondary_first") and delay_h>=duration_h:
        raise ValueError("Second addition must precede endpoint")
    if order=="precomplexed" and not p.solution_binding:
        raise ValueError("Precomplexing requires solution binding")
    # Doses are nominal final well concentrations. Negligible injection volume.
    volumes,*_=geometry(p)
    factor=(p.bath_ul*1e-6+sum(volumes))/(p.bath_ul*1e-6)
    a,s=primary_nm*factor,secondary_nm*factor
    y=initial_state(p)
    events=[]
    if order=="precomplexed":
        c=precomplex_amount(a,s,p.kd_s_nm)
        y[:3]=[a-c,s-c,c]
    elif order=="simultaneous" or delay_h==0:
        y[:3]=[a,s,0]
    elif order=="primary_first":
        y[0]=a
        events=[(delay_h,1,s)]
    else:
        y[1]=s
        events=[(delay_h,0,a)]
    times=np.asarray(times if times is not None else np.linspace(0,duration_h,145),float)
    if times.ndim!=1 or len(times)==0 or np.any(np.diff(times)<=0) or times[0]<0 or times[-1]>duration_h:
        raise ValueError("times must increase strictly within [0,duration_h]")
    rhs=make_rhs(p)
    collected=np.zeros((len(y),len(times)))
    bounds=[0]+[e[0] for e in events]+[duration_h]
    for k,(start,end) in enumerate(zip(bounds[:-1],bounds[1:])):
        sol=solve_ivp(rhs,(start,end),y,method="LSODA",rtol=rtol,atol=atol,dense_output=True)
        if not sol.success: raise RuntimeError(sol.message)
        mask=(times>=start)&(times<=end)
        if np.any(mask):
            collected[:,mask]=sol.sol(times[mask])
        y=sol.y[:,-1]
        if k<len(events):
            _,species,amount=events[k]
            y[species]+=amount
    return {"times":times,"states":collected,"parameters":asdict(p),
            "design":{"primary_nm":primary_nm,"secondary_nm":secondary_nm,"order":order,
                      "delay_h":delay_h,"duration_h":duration_h}}

def summarize(result):
    p=Parameters(**result["parameters"])
    volumes,cells,beta,r0,g=geometry(p)
    z=result["states"][3:].reshape(p.shells,N,-1)
    weights=cells/cells.sum()
    avg=lambda v: np.einsum("s,st->t",weights,v)
    optical=np.linspace(p.optical_core_weight,1,p.shells)
    # Reference to complete permeabilization of initial cells, same optical weighting.
    raw=np.einsum("s,s,st->t",weights,optical,z[:,I["D"]])/np.dot(weights,optical)
    sat=p.fluorescence_saturation
    fluorescence=(1+sat)*raw/(1+sat*raw)
    output={
        "time_h":result["times"],
        "live_fraction":avg(z[:,I["L"]]),
        "committed_fraction":1-avg(z[:,I["L"]]),
        "membrane_compromised_cumulative":avg(z[:,I["D"]]+z[:,I["X"]]),
        "permeability_fluorescence":fluorescence,
        "atp_proxy":avg((z[:,I["L"]]+z[:,I["E"]])*(1-p.atp_suppression*z[:,I["Q"]])),
        "caspase_proxy":avg(z[:,I["E"]]),
        "ldh_proxy":avg(z[:,I["H"]]),
        "surface_complex_copies":avg(z[:,I["T"]]/beta[:,None]),
        "internalized_complex_copies":avg(z[:,I["W"]]/beta[:,None]),
        "payload_copies":avg(z[:,I["P"]]),
        "delivered_payload_cumulative":avg(z[:,I["J"]]),
        "damage":avg(z[:,I["Q"]]),
        "core_committed":1-z[0,I["L"]],
        "rim_committed":1-z[-1,I["L"]],
    }
    return {k:np.asarray(v) for k,v in output.items()}

def ligand_inventory(result):
    """Amount inventories, including destroyed antibody; units nM*L."""
    p=Parameters(**result["parameters"])
    volumes,*_=geometry(p)
    y=result["states"]
    z=y[3:].reshape(p.shells,N,-1)
    primary=y[0]+y[2]
    secondary=y[1]+y[2]
    for field in ("A","C","B","T","V","W","LA"):
        primary=primary+np.einsum("s,st->t",volumes,z[:,I[field]])/(p.bath_ul*1e-6)
    for field in ("S","C","T","W","LS"):
        secondary=secondary+np.einsum("s,st->t",volumes,z[:,I[field]])/(p.bath_ul*1e-6)
    return primary*p.bath_ul*1e-6,secondary*p.bath_ul*1e-6

def hook_metrics(doses,response,threshold=0.10,min_peak=0.05):
    x,y=np.asarray(doses,float),np.asarray(response,float)
    if x.ndim!=1 or y.shape!=x.shape or len(x)<3 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or np.any(np.diff(x)<=0) or np.any(x<=0):
        raise ValueError("Need >=3 finite responses and positive increasing doses")
    if not 0<=threshold<=1 or min_peak<0:
        raise ValueError("Invalid descriptive thresholds")
    i=int(np.argmax(y)); peak=float(y[i])
    depth=max(0.,1-float(y[-1])/peak) if peak>0 else 0.
    resolved=0<i<len(x)-1 and peak>=min_peak
    return {"peak_dose_nm":float(x[i]),"peak":peak,"top_dose_response":float(y[-1]),
            "hook_depth":depth,"interior_peak":0<i<len(x)-1,
            "hook_flag":bool(resolved and depth>=threshold),
            "status":"descriptive hook" if resolved and depth>=threshold else
                     "low signal / uninformative" if peak<min_peak else "no resolved hook in tested range"}
