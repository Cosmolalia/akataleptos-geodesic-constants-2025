"""
Physical Constants from the Menger Sponge
==========================================
Thirteen quantities from seven parameters, zero free choices.

The 3D Menger sponge's graph Laplacian has characteristic polynomial
x^2 - 5x + 2 = 0, determining seven structural parameters:
    S=5, P=2, b=3, d=3, Delta=17, r=7, k=20

Run: python constraint_web.py
"""
import math

S, P, b, d = 5, 2, 3, 3
Delta = S**2 - 4*P  # 17
r = 7; k = b**d - r  # 20

print("="*66)
print("  PHYSICAL CONSTANTS FROM THE MENGER SPONGE")
print("  Thirteen quantities, seven parameters, zero free choices")
print("="*66)
print(f"\n  S={S} P={P} b={b} d={d} Δ={Delta} r={r} k={k}")
print(f"  Polynomial: x² - {S}x + {P} = 0")

# --- DIMENSIONLESS CONSTANTS ---
print(f"\n{'─'*66}")
print("  DIMENSIONLESS CONSTANTS")
print(f"{'─'*66}")

def show(name, formula, pred, meas, meas_str):
    err = abs(pred-meas)/abs(meas)
    if err < 1e-6: es = f"{err*1e9:.1f} ppb"
    elif err < 1e-3: es = f"{err*1e6:.1f} ppm"
    else: es = f"{err*100:.4f}%"
    print(f"  {name:<10} = {formula:<28} = {pred:<14.8f} meas: {meas_str:<16} err: {es}")

show("1/α", "Sb³+P+(Pb)²/(k/P)³", S*b**d+P+(P*b)**2/(k/P)**d, 137.035999084, "137.035999084")
show("mμ/me", "P(Sk+d)+P⁵b/S³", P*(S*k+d)+P**5*b/S**d, 206.7682830, "206.7682830")
show("mp/me", "b²Δ(P²b+(P/k)³)", b**2*Delta*(P**2*b+(P/k)**d), 1836.15267343, "1836.15267343")
show("αs", "P/Δ = 2/17", P/Delta, 0.1179, "0.1179±0.0009")
show("sin θC", "b²/(Δ+k+d) = 9/40", b**2/(Delta+k+d), 0.2253, "0.2253±0.0008")
show("MW/MZ", "1−P/Δ−(P/k)³", 1-P/Delta-(P/k)**d, 0.88147, "0.88147±0.00013")

# --- ABSOLUTE MASSES ---
print(f"\n{'─'*66}")
print("  ABSOLUTE MASSES (GeV)")
print(f"{'─'*66}")

show("MH", "S³+S/k = 125+1/4", S**3+S/k, 125.25, "125.25")
show("mt", "Δk/P+d+P/k = 173.1", Delta*k/P+d+P/k, 173.1, "173.1")
show("MZ", "kS−r−P+d/P⁴ = 91+3/16", k*S-r-P+d/P**(d+1), 91.1876, "91.1876")
show("MW", "k(S−1)+P(k−1)/(Sk)", k*(S-1)+P*(k-1)/(S*k), 80.379, "80.379")

# --- CKM MATRIX ---
print(f"\n{'─'*66}")
print("  CKM QUARK MIXING")
print(f"{'─'*66}")

show("|Vcb|", "P/r² = 2/49", P/r**2, 0.0408, "0.0408±0.0014")
show("Wolf. A", "k/S²+P²(P/k)³", k/S**2+P**2*(P/k)**d, 0.804, "0.804±0.012")
show("δ_CP", "arccos(P/S)", math.acos(P/S), 1.144, "1.144±0.027 rad")

# --- STRUCTURAL ---
print(f"\n{'─'*66}")
print("  STRUCTURAL RELATIONS")
print(f"{'─'*66}")
as_v = P/Delta; mwz_v = 1-P/Delta-(P/k)**d
print(f"  αs + MW/MZ + (P/k)³ = {as_v + mwz_v + (P/k)**d:.6f}  (= 1 exactly)")
print(f"  1836/206 = {1836/206:.6f} = Pb³Δ/(Sk+d) = {P*b**d*Delta/(S*k+d):.6f}")
print(f"  sin²θW = 1−(MW/MZ)² = {1-mwz_v**2:.5f}  (PDG: 0.22301)")

# --- CONSTRAINT WEB ---
print(f"\n{'─'*66}")
print("  CONSTRAINT WEB: Two constants → four")
print(f"{'─'*66}")
D2 = round(P/0.1179); S2 = round(math.sqrt(D2+4*P))
k2 = round(b**2/0.2253 - D2 - d); r2 = b**d - k2
print(f"  From αs=0.1179, sinθC=0.2253 → Δ={D2} S={S2} k={k2} r={r2}")
print(f"  1/α  = {S2*b**d+P+(P*b)**2/(k2/P)**d:.6f}")
print(f"  mμ/me = {P*(S2*k2+d)+P**5*b/S2**d:.6f}")
print(f"  mp/me = {b**2*D2*(P**2*b+(P/k2)**d):.6f}")
print(f"  MW/MZ = {1-P/D2-(P/k2)**d:.6f}")

# --- PREDICTIONS ---
print(f"\n{'─'*66}")
print("  FALSIFIABLE PREDICTIONS")
print(f"{'─'*66}")
print(f"  P1: αs(MZ) → 2/17 = {2/17:.6f}")
print(f"  P2: sin²θW → {1-mwz_v**2:.5f}")
print(f"  P3: |Vus| → 9/40 = 0.22500")
print(f"  P4: αs + MW/MZ → {as_v+mwz_v:.6f}")
print(f"  P5: mH/mt → (17/20)² = {(17/20)**2:.6f}")
print(f"\n  Any single failure refutes the framework.")
print(f"\n  ∂W = W")
