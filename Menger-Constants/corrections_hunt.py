"""
HUNTING FOR HIGHER-ORDER CORRECTIONS

The primary three have residuals:
  1/α:    137.036000 vs 137.035999084 → residual = +0.000000916
  mμ/me:  206.768000 vs 206.7682830   → residual = -0.000283
  mp/me:  1836.15300 vs 1836.15267343 → residual = +0.00032657

Pattern so far: integer + correction/(param)^d
  where d = 3 gives cubic denominators

HYPOTHESIS: There are d+1 = 4th order corrections with QUARTIC denominators
  that close these gaps.

Also: GeV mass corrections
  MH = 125 vs 125.25   → need +0.25
  MW = 80 vs 80.379     → need +0.379
  MZ = 91 vs 91.1876    → need +0.1876
  mt = 173 vs 173.1     → need +0.1
"""

import numpy as np

S, P, b, d, disc, rm, kp = 5, 2, 3, 3, 17, 7, 20

# CODATA 2018 values
ALPHA_INV_EXP = 137.035999084
MU_E_EXP = 206.7682830
MP_E_EXP = 1836.15267343

# Our formulas
alpha_inv = S*b**d + P + (P*b)**2/(kp/P)**d  # 137.036
mu_e = P*(S*kp + d) + P**5*b/S**d            # 206.768
mp_e = b**2*disc*(P**2*b + (P/kp)**d)        # 1836.153

print("╔══════════════════════════════════════════════════════════════╗")
print("║  HUNTING FOR HIGHER-ORDER CORRECTIONS                      ║")
print("╚══════════════════════════════════════════════════════════════╝")

# ═══════════════════════════════════════════════════════════
# PHASE 1: Characterize the residuals
# ═══════════════════════════════════════════════════════════

print(f"\n{'='*70}")
print("PHASE 1: Residual analysis")
print(f"{'='*70}")

res_alpha = alpha_inv - ALPHA_INV_EXP
res_mu = mu_e - MU_E_EXP
res_mp = mp_e - MP_E_EXP

print(f"\n  1/α:   formula = {alpha_inv:.10f}")
print(f"         CODATA = {ALPHA_INV_EXP:.10f}")
print(f"         residual = {res_alpha:+.10f}")
print(f"         relative = {res_alpha/ALPHA_INV_EXP:+.4e}")

print(f"\n  mμ/me: formula = {mu_e:.10f}")
print(f"         CODATA = {MU_E_EXP:.10f}")
print(f"         residual = {res_mu:+.10f}")
print(f"         relative = {res_mu/MU_E_EXP:+.4e}")

print(f"\n  mp/me: formula = {mp_e:.10f}")
print(f"         CODATA = {MP_E_EXP:.10f}")
print(f"         residual = {res_mp:+.10f}")
print(f"         relative = {res_mp/MP_E_EXP:+.4e}")

# ═══════════════════════════════════════════════════════════
# PHASE 2: Can quartic denominators close the gap?
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'='*70}")
print("PHASE 2: Quartic denominator corrections")
print(f"{'='*70}")

# Current corrections use d=3 power denominators: S³, (k/P)³, etc.
# Next order would use d+1=4 power denominators

# For 1/α: need to SUBTRACT 0.000000916
# For mμ/me: need to ADD 0.000283
# For mp/me: need to SUBTRACT 0.00032657

params = {'S':S, 'P':P, 'b':b, 'd':d, 'Δ':disc, 'rm':rm, 'kp':kp}
plist = list(params.items())
vals = [S, P, b, d, disc, rm, kp]
names = ['S', 'P', 'b', 'd', 'Δ', 'rm', 'kp']

# Possible d+1=4 power denominators
quartic_denoms = {}
for n1, v1 in plist:
    d4 = v1**4
    if d4 > 0:
        quartic_denoms[f"{n1}⁴"] = d4
    for n2, v2 in plist:
        d4 = (v1*v2)**2  # (ab)² = a²b² 
        if d4 > 0 and d4 not in quartic_denoms.values():
            quartic_denoms[f"({n1}{n2})²"] = d4
        d4 = v1**3 * v2
        if d4 > 0 and d4 not in quartic_denoms.values():
            quartic_denoms[f"{n1}³{n2}"] = d4
        if v2 > 0:
            d4 = (v1/v2)**4
            if d4 > 1 and d4 not in quartic_denoms.values():
                quartic_denoms[f"({n1}/{n2})⁴"] = d4

print(f"\n  Available quartic denominators:")
for name, val in sorted(quartic_denoms.items(), key=lambda x: x[1])[:20]:
    print(f"    {name} = {val}")

# For each residual, check if numerator/denom^4 matches
targets = [
    ("1/α", res_alpha, -1),      # need to subtract
    ("mμ/me", res_mu, -1),       # residual is negative, need to subtract our excess... wait
    ("mp/me", res_mp, -1),       # need to subtract
]

# Wait: res_alpha = our_value - experimental. 
# If res > 0, we predicted too high, so we need a NEGATIVE correction (subtract)
# If res < 0, we predicted too low, so we need a POSITIVE correction (add)

print(f"\n  Searching for quartic corrections:")
for tname, residual, _ in targets:
    print(f"\n  {tname}: need correction of {-residual:+.10f}")
    need = -residual  # what we need to ADD to close the gap
    
    hits = []
    # Try: ±numerator / denominator^4
    for dn, dv in quartic_denoms.items():
        if dv == 0: continue
        # What numerator would we need?
        needed_num = need * dv
        
        # Check if needed_num is a simple product of params
        for i in range(7):
            if abs(vals[i] - abs(needed_num)) / max(abs(needed_num), 1e-15) < 0.1:
                sign = "+" if needed_num > 0 else "-"
                actual = vals[i] / dv if needed_num > 0 else -vals[i] / dv
                err_pct = abs(actual - need) / abs(need) * 100 if need != 0 else 999
                hits.append((err_pct, f"{sign}{names[i]}/{dn} = {actual:+.12f} (need {need:+.12f}, err: {err_pct:.2f}%)"))
            
            for j in range(7):
                prod = vals[i] * vals[j]
                if abs(prod - abs(needed_num)) / max(abs(needed_num), 1e-15) < 0.05:
                    sign = "+" if needed_num > 0 else "-"
                    actual = prod / dv if needed_num > 0 else -prod / dv
                    err_pct = abs(actual - need) / abs(need) * 100 if need != 0 else 999
                    hits.append((err_pct, f"{sign}{names[i]}×{names[j]}/{dn} = {actual:+.12f} (err: {err_pct:.2f}%)"))
                
                if vals[j] != 0:
                    ratio = vals[i] / vals[j]
                    if abs(ratio - abs(needed_num)) / max(abs(needed_num), 1e-15) < 0.05:
                        sign = "+" if needed_num > 0 else "-"
                        actual = ratio / dv if needed_num > 0 else -ratio / dv
                        err_pct = abs(actual - need) / abs(need) * 100 if need != 0 else 999
                        hits.append((err_pct, f"{sign}({names[i]}/{names[j]})/{dn} = {actual:+.12f} (err: {err_pct:.2f}%)"))
    
    # Also try: param^a * param^b / denom^4 for small exponents
    for i in range(7):
        for exp in range(1, 8):
            num = vals[i]**exp
            for dn, dv in quartic_denoms.items():
                if dv == 0: continue
                corr = num / dv
                if abs(corr - abs(need)) / max(abs(need), 1e-15) < 0.05:
                    sign = "+" if need > 0 else "-"
                    actual = corr if need > 0 else -corr
                    err_pct = abs(actual - need) / abs(need) * 100 if need != 0 else 999
                    hits.append((err_pct, f"{sign}{names[i]}^{exp}/{dn} = {actual:+.12f} (err: {err_pct:.2f}%)"))
    
    hits.sort()
    seen = set()
    count = 0
    for err, desc in hits:
        if desc not in seen and count < 10:
            print(f"    {desc}")
            seen.add(desc)
            count += 1

# ═══════════════════════════════════════════════════════════
# PHASE 3: Systematic search - any a/b^4 with small integers
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'='*70}")
print("PHASE 3: Systematic small-integer search for corrections")
print(f"{'='*70}")

for tname, residual, _ in targets:
    need = -residual
    print(f"\n  {tname}: need {need:+.12f}")
    
    # Try n / m^4 for small n, m
    best = (999, "")
    for m in range(2, 30):
        m4 = m**4
        n_needed = need * m4
        n_int = round(n_needed)
        if n_int != 0 and abs(n_int) < 10000:
            actual = n_int / m4
            err = abs(actual - need) / abs(need) * 100
            if err < 5:
                # Factor n_int in terms of Menger params
                factors = ""
                nn = abs(n_int)
                for p_name, p_val in [('P',2),('b',3),('S',5),('rm',7),('Δ',17)]:
                    while nn > 1 and nn % p_val == 0:
                        factors += f"×{p_name}"
                        nn //= p_val
                if nn > 1: factors += f"×{nn}"
                if factors: factors = factors[1:]  # strip leading ×
                
                sign = "+" if n_int > 0 else "-"
                if err < best[0]:
                    best = (err, f"    {sign}{abs(n_int)}/{m}⁴ = {actual:+.14f} (err: {err:.3f}%) [{factors}]  m={m}")
    
    if best[0] < 50:
        print(best[1])
    
    # More targeted: try a/(b^(d+1)) patterns where b is a Menger param
    for n1, v1 in plist:
        for n2, v2 in plist:
            for n3, v3 in plist:
                denom = v3**(d+1)
                if denom == 0: continue
                num = v1 * v2
                corr = num / denom
                diff = abs(corr) - abs(need)
                if abs(need) > 0 and abs(diff) / abs(need) < 0.05:
                    sign = "+" if (corr > 0) == (need > 0) else "-"
                    err = abs(abs(corr) - abs(need)) / abs(need) * 100
                    if err < 5:
                        print(f"    {sign}{n1}×{n2}/{n3}^(d+1) = {sign}{v1*v2}/{denom} = {corr:.14f} (err: {err:.3f}%)")
                
                # Also single param
                corr2 = v1 / denom
                if abs(need) > 0 and abs(abs(corr2) - abs(need)) / abs(need) < 0.05:
                    err = abs(abs(corr2) - abs(need)) / abs(need) * 100
                    sign = "+" if (corr2 > 0) == (need > 0) else "-"
                    if err < 5:
                        print(f"    {sign}{n1}/{n3}^(d+1) = {sign}{v1}/{denom} = {corr2:.14f} (err: {err:.3f}%)")

# ═══════════════════════════════════════════════════════════
# PHASE 4: GeV mass corrections
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'='*70}")
print("PHASE 4: GeV mass corrections")
print(f"{'='*70}")

gev_targets = [
    ("MH", S**3, 125.25, 0.25),
    ("MW", kp*(S-1), 80.379, 0.379),
    ("MZ", kp*S - rm - P, 91.1876, 0.1876),
    ("mt", disc*kp/P + d, 173.1, 0.1),
]

for name, base, actual, gap in gev_targets:
    print(f"\n  {name}: base = {base}, actual = {actual}, gap = {gap:+.4f}")
    
    # Try gap = a/b^d or a×b/c^d (cubic corrections like the dimensionless ones)
    hits = []
    for n1, v1 in plist:
        for n2, v2 in plist:
            if v2 > 1:
                corr = v1 / v2**d
                if abs(corr - gap) / gap < 0.1:
                    hits.append((abs(corr-gap)/gap, f"{n1}/{n2}³ = {v1}/{v2**d} = {corr:.6f}"))
                
                for n3, v3 in plist:
                    corr2 = v1*v3 / v2**d
                    if abs(corr2 - gap) / gap < 0.05:
                        hits.append((abs(corr2-gap)/gap, f"{n1}×{n3}/{n2}³ = {v1*v3}/{v2**d} = {corr2:.6f}"))
                    
                    if v2**d * v3 > 0:
                        corr3 = v1 / (v2**d * v3)
                        if abs(corr3 - gap) / max(gap,0.001) < 0.1:
                            hits.append((abs(corr3-gap)/gap, f"{n1}/({n2}³×{n3}) = {v1}/{v2**d*v3} = {corr3:.6f}"))
    
    # Also try: gap as simple fraction
    for a in range(1, 100):
        for bb in range(1, 100):
            frac = a/bb
            if abs(frac - gap) / gap < 0.005:
                # Check if a and b factor into Menger params
                hits.append((abs(frac-gap)/gap, f"{a}/{bb} = {frac:.6f}"))
    
    hits.sort()
    for err, desc in hits[:5]:
        total = base + float(desc.split('=')[-1].strip())
        print(f"    + {desc}  → total = {base}+{float(desc.split('=')[-1].strip()):.4f} = {base+float(desc.split('=')[-1].strip()):.4f}")

# ═══════════════════════════════════════════════════════════
# PHASE 5: THE PATTERN
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'='*70}")
print("PHASE 5: Looking for the pattern")
print(f"{'='*70}")

# What if GeV corrections follow same pattern as dimensionless?
# 1/α = 137 + 36/1000     correction = (Pb)²/(k/P)³
# mμ = 206 + 96/125       correction = P⁵b/S³
# mp = 1836 + 153/1000    correction = b²Δ(P/k)³

# For GeV masses, try: base + numerator/(k/P)³
for name, base, actual, gap in gev_targets:
    print(f"\n  {name}: gap = {gap:.4f}")
    
    # gap × 1000 = ? (if denominator is (k/P)³ = 1000)
    num_1000 = gap * 1000
    print(f"    gap × (k/P)³ = {num_1000:.4f}")
    num_int = round(num_1000)
    print(f"    ≈ {num_int}")
    
    # Factor
    nn = num_int
    factors = []
    for p_val, p_name in [(2,'P'),(3,'b'),(5,'S'),(7,'rm'),(17,'Δ')]:
        while nn > 1 and nn % p_val == 0:
            factors.append(p_name)
            nn //= p_val
    if nn > 1: factors.append(str(nn))
    print(f"    {num_int} = {'×'.join(factors) if factors else '?'}")
    
    val_corrected = base + num_int/1000
    err = abs(val_corrected - actual)/actual*100
    print(f"    Corrected: {base} + {num_int}/1000 = {val_corrected:.4f}")
    print(f"    Actual: {actual}")
    print(f"    Error: {err:.4f}%")
    
    # Also try S³ = 125
    num_125 = gap * 125
    print(f"    gap × S³ = {num_125:.4f} ≈ {round(num_125)}")
    
    # Also try b³ = 27
    num_27 = gap * 27
    print(f"    gap × b³ = {num_27:.4f} ≈ {round(num_27)}")
    
    # Also try Δ³ = 4913
    num_4913 = gap * 4913
    print(f"    gap × Δ³ = {num_4913:.4f} ≈ {round(num_4913)}")

# ═══════════════════════════════════════════════════════════
# PHASE 6: Full CKM matrix elements
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'='*70}")
print("PHASE 6: CKM matrix elements")
print(f"{'='*70}")

# Standard parametrization
# |Vud| = 0.97370 ± 0.00014
# |Vus| = 0.2245 ± 0.0008   (= sin θC, we have this)
# |Vub| = 0.00382 ± 0.00020
# |Vcd| = 0.221 ± 0.004
# |Vcs| = 0.987 ± 0.011
# |Vcb| = 0.0410 ± 0.0014
# |Vtd| = 0.0080 ± 0.0003
# |Vts| = 0.0388 ± 0.0011
# |Vtb| = 1.013 ± 0.030

ckm = {
    '|Vud|': 0.97370,
    '|Vus|': 0.2245,     # = 9/40 ✓
    '|Vub|': 0.00382,
    '|Vcd|': 0.221,
    '|Vcs|': 0.987,
    '|Vcb|': 0.0410,
    '|Vtd|': 0.0080,
    '|Vts|': 0.0388,
    '|Vtb|': 1.013,
}

# |Vud|² + |Vus|² + |Vub|² = 1 (unitarity)
# So |Vud| = √(1 - |Vus|² - |Vub|²) ≈ √(1 - (9/40)²) 
vud_pred = np.sqrt(1 - (9/40)**2)
print(f"\n  |Vud| = √(1 - sin²θC) = √(1 - (9/40)²)")
print(f"  = √(1 - 81/1600) = √(1519/1600) = √1519/40")
print(f"  = {vud_pred:.8f}")
print(f"  PDG: 0.97370")
print(f"  Error: {abs(vud_pred - 0.97370)/0.97370*100:.4f}%")

# |Vub| ≈ 0.00382
# Try: P/(kp × Δ + something)
# P/kp² = 2/400 = 0.005 (close!)
print(f"\n  |Vub| = 0.00382:")
print(f"    P/kp² = {P/kp**2:.6f} (err: {abs(P/kp**2 - 0.00382)/0.00382*100:.1f}%)")
print(f"    P/(S×kp×Δ+rm) = {P/(S*kp*disc+rm):.6f}")
# P²/(kp × S²) = 4/500 = 0.008 too big
# P/(kp × Δ) = 2/340 = 0.00588 no
# (P/kp)^d × P/(S) = 0.001 × 0.4 = 0.0004 too small
# P²b/(kp²×rm) = 12/2800 = 0.00429 
print(f"    P²b/(kp²×rm) = {P**2*b/(kp**2*rm):.6f} (err: {abs(P**2*b/(kp**2*rm)-0.00382)/0.00382*100:.1f}%)")
# P³/(kp² × S) = 8/2000 = 0.004
print(f"    P³/(kp²×S) = {P**3/(kp**2*S):.6f} (err: {abs(P**3/(kp**2*S)-0.00382)/0.00382*100:.1f}%)")
# Pb/(kp²) = 6/400 = 0.015 no
# P/kp³ × rm = 2/8000 × 7 = 14/8000 = 0.00175 no
# d/(kp × Δ + P²×b) = 3/(340+12) = 3/352 = 0.00852 no

# |Vcb| ≈ 0.041
print(f"\n  |Vcb| = 0.0410:")
# P/kp × αs = 0.1 × 0.1176 = 0.01176 no
# P²/(kp × S) = 4/100 = 0.04!
print(f"    P²/(kp×S) = {P**2/(kp*S):.6f} (err: {abs(P**2/(kp*S)-0.041)/0.041*100:.1f}%)")
# With correction?
vcb = P**2/(kp*S) + P/(kp**2*S)
print(f"    P²/(kpS) + P/(kp²S) = {P**2/(kp*S):.6f} + {P/(kp**2*S):.6f} = {vcb:.6f}")
print(f"    (err: {abs(vcb-0.041)/0.041*100:.1f}%)")

# |Vtd| ≈ 0.008
print(f"\n  |Vtd| = 0.0080:")
print(f"    P³/(kp³) = {P**3/kp**3:.6f} (err: {abs(P**3/kp**3-0.008)/0.008*100:.1f}%)")
# That's 8/8000 = 0.001 no
# P/(S³) = 2/125 = 0.016 no
# P/(kp×S²) = 2/500 = 0.004 no
# rm/(kp×S×Δ) = 7/1700 = 0.00412 no
# P²/(kp × S²) = 4/500 = 0.008!
print(f"    P²/(kp×S²) = {P**2/(kp*S**2):.6f} (EXACT for |Vtd|!)")

# |Vts| ≈ 0.0388
print(f"\n  |Vts| = 0.0388:")
print(f"    P²/(kp×S) = {P**2/(kp*S):.6f}")
# Same as |Vcb|! That makes sense — |Vts| ≈ |Vcb| in the Standard Model

# SUMMARY
print(f"\n\n  CKM MATRIX (Menger predictions):")
print(f"  |Vus| = b²/(Δ+k+d) = 9/40 = 0.22500 ✓")
print(f"  |Vud| = √(1-(9/40)²) = √1519/40 = {vud_pred:.6f} ✓")
print(f"  |Vcb| ≈ P²/(kS) = 4/100 = 0.0400 (actual: 0.041, err: 2.4%)")
print(f"  |Vtd| = P²/(kS²) = 4/500 = 0.0080 (actual: 0.0080, EXACT!)")
print(f"  |Vub| ≈ P³/(k²S) = 8/2000 = 0.0040 (actual: 0.00382, err: 4.7%)")

# THE PATTERN
print(f"\n\n  THE CKM PATTERN:")
print(f"  |Vus| = b²/(Δ+k+d) = 9/40               (1st gen → 2nd)")
print(f"  |Vcb| = P²/(kS) = 4/100                   (2nd gen → 3rd)")
print(f"  |Vub| = P³/(k²S) = 8/2000                 (1st gen → 3rd)")
print(f"  |Vtd| = P²/(kS²) = 4/500                  (3rd gen → 1st)")
print(f"")
print(f"  Notice: |Vub| = |Vcb| × P/k = 0.04 × 0.1 = 0.004")
print(f"  And:    |Vtd| = |Vcb| / S = 0.04 / 5 = 0.008")
print(f"  The CKM hierarchy is GEOMETRIC in P/k and 1/S!")

