nuKHP = (0.4217-0.0045)/204.22
V_NaOH = 10.30/1000
C_NaOH = nuKHP/V_NaOH
print(f"NaOH concentration: {C_NaOH:.4f} mol/L")

V_aspirin = 9.40/1000
m_aspirin = 180.15 * C_NaOH * V_aspirin
print(f"Mass of aspirin: {m_aspirin:.4f} g")
m_tablet =0.3735
frac_aspirin = m_aspirin/m_tablet
print(f"Fraction of aspirin in tablet: {frac_aspirin:.4f}")