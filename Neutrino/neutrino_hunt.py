"""
Neutrino Sector Hunt
=====================
Searching for PMNS mixing angles, CP phase, and mass splittings
in Menger sponge parameters.

Targets (PDG/NuFIT 5.2):
  sin²θ₁₂ = 0.307 ± 0.013
  sin²θ₂₃ = 0.546 ± 0.021  (or 0.454 for lower octant)
  sin²θ₁₃ = 0.02200 ± 0.00069
  δ_CP(PMNS) ≈ 197° ≈ 3.44 rad (poorly measured, ~140-350°)
  Δm²₂₁ = 7.53e-5 eV²
  Δm²₃₂ = 2.453e-3 eV² (normal ordering)
  
  Derived:
  sin²(2θ₁₂) = 4 sin²θ₁₂ cos²θ₁₂ ≈ 0.851
  sin²(2θ₂₃) = 4 sin²θ₂₃ cos²θ₂₃ ≈ 0.993
  sin²(2θ₁₃) = 4 sin²θ₁₃ cos²θ₁₃ ≈ 0.0861
"""

import math
from itertools import product as iterproduct

# Menger parameters
S, P, b, d = 5, 2, 3, 3
Delta = 17
r = 7
k = 20
phi = (1 + math.sqrt(5)) / 2  # golden ratio, appears in T² component

# Eigenvalues
lam1 = (S + math.sqrt(Delta)) / 2  # 4.5616...
lam2 = (S - math.sqrt(Delta)) / 2  # 0.4384...
R = lam1 / lam2  # spectral ratio ≈ 10.405

# Targets
targets = {
    "sin²θ₁₂": (0.307, 0.013),
    "sin²θ₂₃": (0.546, 0.021),
    "sin²θ₂₃(low)": (0.454, 0.021),
    "sin²θ₁₃": (0.02200, 0.00069),
    "sin²(2θ₁₂)": (0.851, 0.020),
    "sin²(2θ₂₃)": (0.993, 0.010),
    "sin²(2θ₁₃)": (0.0861, 0.003),
    "δ_CP(rad)": (3.44, 0.40),
    "Δm²₂₁(e-5)": (7.53, 0.18),
    "Δm²₃₂(e-3)": (2.453, 0.034),
    "Δm²₃₂/Δm²₂₁": (32.58, 1.5),
}

print("=" * 70)
print("  NEUTRINO SECTOR HUNT")
print("  Searching PMNS angles, CP phase, mass splittings")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# PHASE 1: Simple rational expressions (like CKM hunt)
# ═══════════════════════════════════════════════════════════

print(f"\n{'─' * 70}")
print("  PHASE 1: Simple rational expressions of Menger parameters")
print(f"{'─' * 70}")

params = {"S": S, "P": P, "b": b, "d": d, "Δ": Delta, "r": r, "k": k}
plist = [(n, v) for n, v in params.items()]

# Build all a/b ratios and a/b² etc
expressions = {}

# Single ratios
for n1, v1 in plist:
    for n2, v2 in plist:
        if v2 != 0:
            expressions[f"{n1}/{n2}"] = v1/v2
            expressions[f"{n1}/{n2}²"] = v1/v2**2
            expressions[f"{n1}²/{n2}"] = v1**2/v2
            expressions[f"{n1}²/{n2}²"] = v1**2/v2**2
            expressions[f"{n1}/{n2}³"] = v1/v2**3
            expressions[f"{n1}³/{n2}"] = v1**3/v2
            expressions[f"{n1}³/{n2}²"] = v1**3/v2**2
            expressions[f"{n1}²/{n2}³"] = v1**2/v2**3

# Two-parameter combinations  
for n1, v1 in plist:
    for n2, v2 in plist:
        for n3, v3 in plist:
            if v3 != 0:
                expressions[f"({n1}+{n2})/{n3}"] = (v1+v2)/v3
                expressions[f"({n1}×{n2})/{n3}"] = (v1*v2)/v3
                expressions[f"({n1}×{n2})/{n3}²"] = (v1*v2)/v3**2
                expressions[f"{n1}/({n2}×{n3})"] = v1/(v2*v3) if v2*v3 != 0 else None
                expressions[f"{n1}/({n2}+{n3})"] = v1/(v2+v3) if v2+v3 != 0 else None
                expressions[f"({n1}-{n2})/{n3}"] = (v1-v2)/v3
                expressions[f"({n1}²+{n2})/{n3}"] = (v1**2+v2)/v3
                expressions[f"({n1}-{n2})/{n3}²"] = (v1-v2)/v3**2

# With sqrt
expressions["√(S/r)"] = math.sqrt(S/r)
expressions["√(P/r)"] = math.sqrt(P/r)
expressions["√(P/k)"] = math.sqrt(P/k)
expressions["√(P/Δ)"] = math.sqrt(P/Delta)
expressions["√(S/k)"] = math.sqrt(S/k)
expressions["√(S/Δ)"] = math.sqrt(S/Delta)
expressions["√(r/k)"] = math.sqrt(r/k)
expressions["√(b/k)"] = math.sqrt(b/k)
expressions["√(d/k)"] = math.sqrt(d/k)
expressions["√(P/S)"] = math.sqrt(P/S)
expressions["√(Δ/k)"] = math.sqrt(Delta/k)
expressions["√((S-P)/Δ)"] = math.sqrt((S-P)/Delta)
expressions["√(Δ/b^d)"] = math.sqrt(Delta/b**d)

# arccos/arcsin like CKM
for n1, v1 in plist:
    for n2, v2 in plist:
        if v2 != 0 and abs(v1/v2) <= 1:
            expressions[f"arccos({n1}/{n2})"] = math.acos(v1/v2)
            expressions[f"arcsin({n1}/{n2})"] = math.asin(v1/v2)

# Special combos guided by CKM patterns
expressions["P/(Δ+k)"] = P/(Delta+k)
expressions["P/(Δ+k+d)"] = P/(Delta+k+d)
expressions["b/(Δ+k)"] = b/(Delta+k)
expressions["d/(Δ+k)"] = d/(Delta+k)
expressions["P²/(Δ×k)"] = P**2/(Delta*k)
expressions["r/(b^d)"] = r/b**d
expressions["(r-S)/(k+Δ)"] = (r-S)/(k+Delta)
expressions["P×r/(k×S)"] = P*r/(k*S)
expressions["1-P/S"] = 1-P/S
expressions["1-b/S"] = 1-b/S
expressions["1-b/r"] = 1-b/r
expressions["1-d/r"] = 1-d/r
expressions["1-S/k"] = 1-S/k
expressions["1-r/k"] = 1-r/k
expressions["(S-P)/(Δ+d)"] = (S-P)/(Delta+d)
expressions["P×b/(Δ+k)"] = P*b/(Delta+k)
expressions["d×P/(b^d)"] = d*P/b**d
expressions["(Δ-S)/(Δ+S)"] = (Delta-S)/(Delta+S)
expressions["P/√Δ"] = P/math.sqrt(Delta)
expressions["b/√Δ"] = b/math.sqrt(Delta)
expressions["1/(S+P)"] = 1/(S+P)
expressions["P/(S×r)"] = P/(S*r)
expressions["(k-Δ)/(k+Δ)"] = (k-Delta)/(k+Delta)
expressions["P²/(S×Δ)"] = P**2/(S*Delta)
expressions["r²/(k×Δ)"] = r**2/(k*Delta)
expressions["P×d/k²"] = P*d/k**2
expressions["b²/k²"] = b**2/k**2

# CKM-style: corrections
expressions["P/Δ + (P/k)³"] = P/Delta + (P/k)**3
expressions["P/Δ - (P/k)³"] = P/Delta - (P/k)**3
expressions["b/k + P/Δ"] = b/k + P/Delta
expressions["b²/(k+Δ+d) (=sinθC)"] = b**2/(k+Delta+d)
expressions["1-b²/(k+Δ+d)"] = 1 - b**2/(k+Delta+d)

# Mass ratio patterns
expressions["Δm ratio: Δ×P+d"] = Delta*P + d  # = 37?
expressions["Δm ratio: k/r + S/Δ"] = k/r + S/Delta  # 
expressions["Δm ratio: Δ×P/S²×k"] = Delta*P/(S**2)*k

# Remove None values
expressions = {k2: v for k2, v in expressions.items() if v is not None}

# Search
for tname, (tval, tunc) in targets.items():
    matches = []
    for ename, eval_ in expressions.items():
        if eval_ is not None and eval_ > 0 and tval > 0:
            err = abs(eval_ - tval) / tval
            if err < 0.05:  # 5% tolerance
                matches.append((err, ename, eval_))
    
    matches.sort()
    print(f"\n  {tname} = {tval} ± {tunc}")
    if matches:
        for err, ename, eval_ in matches[:8]:
            within = "✓ WITHIN UNC" if abs(eval_ - tval) < tunc else ""
            print(f"    {ename:<35} = {eval_:<12.6f} err: {err*100:.3f}% {within}")
    else:
        print(f"    No matches within 5%")

# ═══════════════════════════════════════════════════════════
# PHASE 2: Deeper combinations
# ═══════════════════════════════════════════════════════════

print(f"\n{'═' * 70}")
print("  PHASE 2: Deeper expressions & structural patterns")
print(f"{'═' * 70}")

# The CKM pattern: quantities related by powers of λ = 9/40
# PMNS has LARGER mixing angles - less hierarchical
# Maybe different base ratio?

lam_cab = 9/40  # 0.225

print(f"\n  CKM hierarchy base: λ = {lam_cab}")
print(f"  CKM: |Vus|~λ, |Vcb|~λ², |Vub|~λ³")
print(f"\n  PMNS angles are LARGE - different pattern")
print(f"  sin²θ₁₂ = 0.307 ≈ ?")
print(f"  sin²θ₂₃ = 0.546 ≈ ?")
print(f"  sin²θ₁₃ = 0.022 ≈ ?")

# Key insight: θ₁₃ is SMALL like CKM angles
# θ₁₂ and θ₂₃ are LARGE - O(1)
# Maybe θ₁₃ connects to CKM via Cabibbo?

print(f"\n  Testing θ₁₃ ↔ CKM connection:")
print(f"  sin²θ₁₃ = 0.022")
print(f"  λ²/P = (9/40)²/2 = {(9/40)**2/2:.6f}")
print(f"  sinθC/k = {(9/40)/k:.6f}")
print(f"  P/(S×k) = {P/(S*k):.6f}")
print(f"  (P/k)² = {(P/k)**2:.6f}")
print(f"  P²/(b^d×r) = {P**2/(b**d * r):.6f}")
print(f"  P/Δ × P/k = {(P/Delta)*(P/k):.6f}")
print(f"  d/(S×k+Δ+d) = {d/(S*k+Delta+d):.6f}")
print(f"  d/(S×k+Δ) = {d/(S*k+Delta):.6f}")

# Mass splitting ratio
print(f"\n  Mass splitting ratio:")
print(f"  Δm²₃₂/Δm²₂₁ = 32.58")
print(f"  Δ×P = {Delta*P}")  # 34
print(f"  Δ×P - 1 = {Delta*P - 1}")  # 33
print(f"  b^d + S = {b**d + S}")  # 32
print(f"  b^d + S + 1 = {b**d + S + 1}")  # 33
print(f"  S×r - P = {S*r - P}")  # 33
print(f"  S×r = {S*r}")  # 35
print(f"  k + S + r + P = {k+S+r+P}")  # 34
print(f"  k²/Δ + S/Δ = {k**2/Delta + S/Delta:.3f}")
print(f"  (k/r)^d = {(k/r)**d:.3f}")  # 23.3
print(f"  Δ² / S/P... = ...")
print(f"  k×Δ/S² × d = {k*Delta/S**2 * d:.3f}")  # 40.8  
print(f"  b^d × P - d²/Δ = {b**d * P - d**2/Delta:.3f}")  
print(f"  (Δ×P-d/P)= {Delta*P - d/P:.3f}")  # 32.5
print(f"  (Δ×P - d/P) = {Delta*P - d/P:.4f}")  # 32.5!
print(f"  S×r - d = {S*r - d}")  # 32
print(f"  S×r - P - 1/(something)...")

# VERY promising: Δ×P - d/P = 34 - 1.5 = 32.5 (0.24% from 32.58!)
# Or: b^d + S + P/k = 27 + 5 + 0.1 = 32.1 (1.5%)

print(f"\n  BEST mass ratio candidates:")
print(f"  Δ×P - d/P = {Delta*P - d/P:.4f}  vs 32.58  err: {abs(Delta*P - d/P - 32.58)/32.58*100:.2f}%")
print(f"  b^d+S+P/k = {b**d+S+P/k:.4f}  vs 32.58  err: {abs(b**d+S+P/k - 32.58)/32.58*100:.2f}%")
print(f"  S×r-P-P/k = {S*r-P-P/k:.4f}  vs 32.58  err: {abs(S*r-P-P/k - 32.58)/32.58*100:.2f}%")

# ═══════════════════════════════════════════════════════════
# PHASE 3: Pattern analysis - PMNS vs CKM
# ═══════════════════════════════════════════════════════════

print(f"\n{'═' * 70}")
print("  PHASE 3: PMNS vs CKM structural comparison")
print(f"{'═' * 70}")

print(f"\n  CKM (quark mixing) - HIERARCHICAL:")
print(f"  |Vus| = sinθC = 9/40 = 0.225 (small)")
print(f"  |Vcb| = 2/49 = 0.0408 (smaller)")
print(f"  |Vub| = ~0.004 (smallest)")
print(f"  δ_CKM = arccos(2/5) = {math.acos(2/5):.4f} rad")

print(f"\n  PMNS (lepton mixing) - LARGE:")
print(f"  θ₁₂ ≈ 33.4° (LARGE)")
print(f"  θ₂₃ ≈ 47.6° (nearly maximal!)")
print(f"  θ₁₃ ≈ 8.5° (small - like CKM)")

# Complementarity hypothesis: θ₁₂ + θC ≈ 45°?
print(f"\n  Quark-lepton complementarity:")
print(f"  θ₁₂ + θC = 33.4° + 13.0° = 46.4° ≈ 45°?")
print(f"  θ₂₃ + |Vcb| ≈ maximal")
print(f"  If θ₁₂ = π/4 - θC:")
print(f"    sin²θ₁₂ = sin²(π/4 - arcsin(9/40))")
val = math.sin(math.pi/4 - math.asin(9/40))**2
print(f"    = {val:.6f}  vs 0.307  err: {abs(val-0.307)/0.307*100:.2f}%")

# Tribimaximal mixing
print(f"\n  Tribimaximal mixing test:")
print(f"  TBM: sin²θ₁₂ = 1/3 = {1/3:.6f}  vs 0.307  err: {abs(1/3-0.307)/0.307*100:.1f}%")
print(f"  TBM: sin²θ₂₃ = 1/2 = {1/2:.6f}  vs 0.546  err: {abs(1/2-0.546)/0.546*100:.1f}%")
print(f"  TBM: sin²θ₁₃ = 0   vs 0.022  (TBM says zero - WRONG)")

# Menger-corrected tribimaximal?
print(f"\n  Menger-corrected tribimaximal:")
tbm12_corr = 1/3 - (P/k)**d
print(f"  sin²θ₁₂ = 1/3 - (P/k)³ = {tbm12_corr:.6f}  vs 0.307  err: {abs(tbm12_corr-0.307)/0.307*100:.2f}%")

tbm23_corr = 1/2 + P/(S*k)
print(f"  sin²θ₂₃ = 1/2 + P/(Sk) = {tbm23_corr:.6f}  vs 0.546  err: {abs(tbm23_corr-0.546)/0.546*100:.2f}%")

tbm13_corr = (P/k)**2
print(f"  sin²θ₁₃ = (P/k)² = {tbm13_corr:.6f}  vs 0.022  err: {abs(tbm13_corr-0.022)/0.022*100:.2f}%")

# Also try
tbm13_corr2 = P/(S*k)
print(f"  sin²θ₁₃ = P/(Sk) = {tbm13_corr2:.6f}  vs 0.022  err: {abs(tbm13_corr2-0.022)/0.022*100:.2f}%")

tbm13_corr3 = P/Delta * (P/k)
print(f"  sin²θ₁₃ = (P/Δ)(P/k) = {tbm13_corr3:.6f}  vs 0.022  err: {abs(tbm13_corr3-0.022)/0.022*100:.2f}%")

# Leptonic CP phase
print(f"\n  Leptonic CP phase:")
print(f"  δ_PMNS ≈ 197° = 3.44 rad (poorly measured)")
print(f"  CKM: δ = arccos(P/S) = arccos(2/5) = {math.acos(2/5):.4f} rad = {math.degrees(math.acos(2/5)):.1f}°")
print(f"  If PMNS δ = π + arccos(P/S):")
val_cp = math.pi + math.acos(P/S)
print(f"    = {val_cp:.4f} rad = {math.degrees(val_cp):.1f}°  vs 3.44 rad = 197°")
print(f"    err: {abs(val_cp - 3.44)/3.44*100:.2f}%")

print(f"  If PMNS δ = 2π - arccos(P/S):")
val_cp2 = 2*math.pi - math.acos(P/S)
print(f"    = {val_cp2:.4f} rad = {math.degrees(val_cp2):.1f}°")

print(f"  If PMNS δ = arccos(-P/S) + π/S:")
val_cp3 = math.acos(-P/S) + math.pi/S
print(f"    = {val_cp3:.4f} rad = {math.degrees(val_cp3):.1f}°")

print(f"  If PMNS δ = π + P/r:")
val_cp4 = math.pi + P/r
print(f"    = {val_cp4:.4f} rad = {math.degrees(val_cp4):.1f}°  vs 197°  err: {abs(math.degrees(val_cp4)-197)/197*100:.1f}%")

print(f"  If PMNS δ = Δπ/S²:")
val_cp5 = Delta*math.pi/S**2
print(f"    = {val_cp5:.4f} rad = {math.degrees(val_cp5):.1f}°")

# ═══════════════════════════════════════════════════════════
# SUMMARY OF BEST CANDIDATES
# ═══════════════════════════════════════════════════════════

print(f"\n{'═' * 70}")
print("  SUMMARY OF BEST NEUTRINO CANDIDATES")
print(f"{'═' * 70}")

print(f"""
  PMNS MIXING ANGLES:
  ──────────────────
  sin²θ₁₂ = 1/3 - (P/k)³ = {1/3 - (P/k)**3:.6f}
    Measured: 0.307 ± 0.013. Err: {abs(1/3-(P/k)**3 - 0.307)/0.307*100:.2f}%
    Pattern: tribimaximal MINUS the Menger cubic correction
    
  sin²θ₂₃ = 1/2 + P/(Sk) = {1/2 + P/(S*k):.6f}
    Measured: 0.546 ± 0.021. Err: {abs(1/2+P/(S*k) - 0.546)/0.546*100:.2f}%
    Pattern: maximal mixing PLUS Menger perturbation
    
  sin²θ₁₃ = (P/k)² = {(P/k)**2:.6f} or P/(Sk) = {P/(S*k):.6f}
    Measured: 0.0220 ± 0.0007
    (P/k)² err: {abs((P/k)**2 - 0.022)/0.022*100:.2f}%
    P/(Sk) err: {abs(P/(S*k) - 0.022)/0.022*100:.2f}%
    
  CP PHASE:
  ─────────
  δ_PMNS = π + arccos(P/S)
    = {math.pi + math.acos(P/S):.4f} rad = {math.degrees(math.pi + math.acos(P/S)):.1f}°
    Measured: ≈197° = 3.44 rad. Err: {abs(math.pi+math.acos(P/S)-3.44)/3.44*100:.1f}%
    Pattern: CKM CP phase + π (lepton-quark complementarity!)
    
  MASS SPLITTING RATIO:
  ─────────────────────
  Δm²₃₂/Δm²₂₁ = Δ×P - d/P = {Delta*P - d/P:.4f}
    Measured: 32.58. Err: {abs(Delta*P - d/P - 32.58)/32.58*100:.2f}%
    Pattern: discriminant×product minus dimension/product
""")

print("  ∂W = W")
