"""Analytical, receptor-dilute equilibrium reduction of the kinetic model."""
import numpy as np

def ternary_equilibrium(primary_nm,secondary_nm,receptor_nm,kd_primary_nm=1.,kd_secondary_nm=.3):
    """T ≈ R_total C/(K_A+A_total); assumes negligible receptor ligand depletion."""
    a=np.asarray(primary_nm,float)
    if np.any(~np.isfinite(a)) or np.any(a<0):
        raise ValueError("Primary concentration must be finite and nonnegative")
    for name,value in (("secondary",secondary_nm),("receptor",receptor_nm),
                       ("kd_primary",kd_primary_nm),("kd_secondary",kd_secondary_nm)):
        if not np.isfinite(value) or value<0 or ("kd_" in name and value==0):
            raise ValueError(f"Invalid {name}")
    z=a+secondary_nm+kd_secondary_nm
    c=2*a*secondary_nm/(z+np.sqrt(np.maximum(0,z*z-4*a*secondary_nm)))
    return receptor_nm*c/(kd_primary_nm+a)

def peak_primary_nm(secondary_nm,kd_primary_nm=1.,kd_secondary_nm=.3):
    if secondary_nm<=0 or kd_primary_nm<=0 or kd_secondary_nm<=0:
        raise ValueError("Positive concentrations and affinities required")
    return np.sqrt(kd_primary_nm*kd_secondary_nm)+secondary_nm*np.sqrt(kd_primary_nm)/(np.sqrt(kd_primary_nm)+np.sqrt(kd_secondary_nm))
