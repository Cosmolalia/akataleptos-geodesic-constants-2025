"""
Deep dive into Apollonian Level 1 spectrum.
The eigenvalues at level 1 are:
  4.854, 0.618(×3), -1.618(×3), -1.854

0.618 = 1/φ = φ-1
1.618 = φ

Let's find the characteristic polynomials.
"""

import numpy as np
from itertools import combinations
import sympy as sp

# Rebuild level 1 adjacency matrix explicitly
# 4 original circles (all mutually tangent) + 4 new circles (one per gap)
# Original: 0(outer,-1), 1(inner,2), 2(inner,2), 3(inner,3)
# New: 4(gap 012), 5(gap 013), 6(gap 023), 7(gap 123)

# Tangencies:
# Original: 0-1, 0-2, 0-3, 1-2, 1-3, 2-3
# New circle 4 (in gap 0,1,2): tangent to 0,1,2
# New circle 5 (in gap 0,1,3): tangent to 0,1,3
# New circle 6 (in gap 0,2,3): tangent to 0,2,3
# New circle 7 (in gap 1,2,3): tangent to 1,2,3

n = 8
A = np.zeros((n, n))
# Original tangencies
for i, j in combinations(range(4), 2):
    A[i,j] = A[j,i] = 1
# New tangencies
for new_idx, parents in [(4,[0,1,2]), (5,[0,1,3]), (6,[0,2,3]), (7,[1,2,3])]:
    for p in parents:
        A[new_idx, p] = A[p, new_idx] = 1

print("Adjacency matrix:")
print(A.astype(int))
print()

# Eigenvalues
eigs = np.sort(np.linalg.eigvalsh(A))[::-1]
print("Eigenvalues:")
for e in eigs:
    print(f"  {e:.10f}")

print()

# Check: are the extreme pair roots of x² - 3x - 9 = 0?
phi = (1 + np.sqrt(5))/2
print("φ = ", phi)
print("1/φ = ", 1/phi)
print()

e_max = eigs[0]
e_min = eigs[-1]
print(f"Extreme pair: {e_max:.10f}, {e_min:.10f}")
print(f"  Sum  = {e_max + e_min:.10f}")
print(f"  Prod = {e_max * e_min:.10f}")
print(f"  → x² - {e_max+e_min:.6f}x + {e_max*e_min:.6f} = 0")
print(f"  Discriminant = {(e_max+e_min)**2 - 4*e_max*e_min:.10f}")
print(f"  √Δ = {np.sqrt((e_max+e_min)**2 - 4*e_max*e_min):.10f}")
print(f"  3√5 = {3*np.sqrt(5):.10f}")
print()

# Check x² - 3x - 9 = 0
print("Roots of x² - 3x - 9 = 0:")
print(f"  (3+3√5)/2 = {(3+3*np.sqrt(5))/2:.10f}  vs  λ_max = {e_max:.10f}")
print(f"  (3-3√5)/2 = {(3-3*np.sqrt(5))/2:.10f}  vs  λ_min = {e_min:.10f}")
print()

# Middle eigenvalues: ±φ stuff
e_mid_pos = eigs[1]  # should be 1/φ
e_mid_neg = eigs[4]  # should be -φ
print(f"Middle pair: {e_mid_pos:.10f}, {e_mid_neg:.10f}")
print(f"  Sum  = {e_mid_pos + e_mid_neg:.10f}")
print(f"  Prod = {e_mid_pos * e_mid_neg:.10f}")
print(f"  → x² + x - 1 = 0  (the GOLDEN RATIO equation!)")
print(f"  Discriminant = {(e_mid_pos+e_mid_neg)**2 - 4*e_mid_pos*e_mid_neg:.10f}")
print(f"  = 5")
print()

print("="*70)
print("  APOLLONIAN LEVEL 1 CHARACTERISTIC POLYNOMIALS")
print("="*70)
print()
print("  The adjacency spectrum factors into TWO quadratics:")
print()
print("  EXTREMAL:  x² - 3x - 9 = 0     (S=3, P=-9, Δ=45)")
print("  INTERIOR:  x² + x - 1 = 0       (S=-1, P=-1, Δ=5)")
print()
print("  Full char poly = (x² - 3x - 9)(x² + x - 1)³")
print()

# Verify
x = sp.Symbol('x')
full_poly = (x**2 - 3*x - 9) * (x**2 + x - 1)**3
expanded = sp.expand(full_poly)
print(f"  Expanded: {expanded}")
print()

# Verify numerically
coeffs = sp.Poly(full_poly, x).all_coeffs()
print(f"  Coefficients: {coeffs}")

# Now compare with actual char poly of A
char_poly_numerical = np.poly(A)
print(f"  Numerical char poly coeffs: {[f'{c:.4f}' for c in char_poly_numerical]}")
print()

print("="*70)
print("  COMPARISON: MENGER vs APOLLONIAN")
print("="*70)
print()
print("  MENGER SPONGE Level 1:")
print("    Characteristic: x² - 5x + 2 = 0")
print(f"    S = 5, P = 2, Δ = 17 (prime)")
print(f"    Roots: {(5+np.sqrt(17))/2:.6f}, {(5-np.sqrt(17))/2:.6f}")
print(f"    Parameters: b=3, d=3, r=7, k=20")
print()
print("  APOLLONIAN GASKET Level 1:")
print("    Extremal: x² - 3x - 9 = 0")
print(f"    S = 3, P = -9, Δ = 45 = 9×5")
print(f"    Roots: {(3+3*np.sqrt(5))/2:.6f}, {(3-3*np.sqrt(5))/2:.6f}")
print()
print("    Interior: x² + x - 1 = 0  ← THE GOLDEN RATIO EQUATION")
print(f"    S = -1, P = -1, Δ = 5 (prime)")
print(f"    Roots: φ-1 = {1/phi:.6f}, -φ = {-phi:.6f}")
print()

# Now: structural parameters from Apollonian
print("="*70)
print("  APOLLONIAN STRUCTURAL PARAMETERS")
print("="*70)
print()

# Level 0: 4 circles, 6 edges, 4 gaps
# Level 1: 4 new circles (one per gap)
# Each new circle creates 3 new gaps from 1 old gap
# So gaps: 4 → 12 → 36 → 108 (multiply by 3 each time)
# Circles: 4, 8, 20, 56, 164 (add 4, 12, 36, 108...)

print("  Growth pattern:")
print("  Level 0: 4 circles, 4 gaps")
print("  Level 1: 8 circles, 12 gaps   (+4 circles, gaps ×3)")
print("  Level 2: 20 circles, 36 gaps  (+12 circles, gaps ×3)")
print("  Level 3: 56 circles, 108 gaps (+36 circles, gaps ×3)")
print()
print("  New circles per level: 4, 12, 36, 108 = 4 × 3^n")
print("  Total circles: 4, 8, 20, 56, 164 = 4 + 4(3^n - 1)/2")
print()

# The key numbers
print("  BASE NUMBERS:")
print(f"  Initial circles: 4 (tetrahedron)")
print(f"  Gaps per circle: 3 (triangulation)")  
print(f"  Growth factor: 3 (each gap → 3 sub-gaps)")
print()

# What does the extremal polynomial encode?
S_A = 3   # sum of extremal eigenvalues
P_A = -9  # product of extremal eigenvalues
D_A = 45  # discriminant

print("  EXTREMAL POLYNOMIAL PARAMETERS:")
print(f"  S = {S_A} = growth factor = gaps per parent gap")
print(f"  P = {P_A} = -3² = -(growth factor)²")
print(f"  Δ = {D_A} = 9 × 5 = S² × 5")
print(f"  √Δ = 3√5")
print()

# Key ratios
print("  KEY RATIOS:")
print(f"  λ_max / |λ_min| = {e_max/abs(e_min):.10f}")
print(f"  φ² = {phi**2:.10f}")
print(f"  RATIO = φ²  !!!!")
print()

# So: λ_max = φ² × |λ_min|
# And λ_max + λ_min = 3
# And λ_max × λ_min = -9
# So λ_max = 3φ²/(φ²+1) ... let me check

print("  λ_max / |λ_min| = φ² = (3+√5)/2")
print(f"  Verify: {e_max/abs(e_min):.10f} vs {(3+np.sqrt(5))/2:.10f}")
print()

# Now: what about the LAPLACIAN?
L = np.diag(A.sum(axis=1)) - A
eigs_L = np.sort(np.linalg.eigvalsh(L))
print("="*70)
print("  LAPLACIAN SPECTRUM (Level 1)")
print("="*70)
for e in eigs_L:
    print(f"  {e:.10f}")
print()

# Nonzero Laplacian eigenvalues
nz = eigs_L[eigs_L > 1e-10]
print(f"  Nonzero Laplacian eigenvalues:")
unique_nz = np.unique(np.round(nz, 6))
for u in unique_nz:
    mult = np.sum(np.abs(nz - u) < 0.001)
    print(f"    {u:.10f}  (multiplicity {mult})")

print()
print(f"  Note: 2.76393202 = 3 - 1/φ² = 3 - (3-√5)/2 = (3+√5)/2 = φ²")
print(f"  Verify: φ² = {phi**2:.10f}")
print(f"  Hmm, 2.7639 ≠ 2.618...")
print()
print(f"  Actually: 3 - φ/φ = ... let me check")
print(f"  5 - √5 = {5 - np.sqrt(5):.10f}")
print(f"  (5 - √5)/2 = {(5-np.sqrt(5))/2:.10f} nope")
print(f"  3 + 1/φ - φ = {3 + 1/phi - phi:.10f} nope")

# Let's just check what polynomial the Laplacian eigenvalues satisfy
lap_nz_1 = 2.76393202
lap_nz_2 = 7.23606798
print(f"\n  Laplacian nonzero pair: {lap_nz_1}, {lap_nz_2}")
print(f"  Sum = {lap_nz_1 + lap_nz_2:.10f}")
print(f"  Prod = {lap_nz_1 * lap_nz_2:.10f}")
print(f"  Sum = 10.0!")
print(f"  Prod = 20.0!")
print(f"  → x² - 10x + 20 = 0")
print(f"  Δ = 100 - 80 = 20")
print(f"  √20 = 2√5 = {2*np.sqrt(5):.10f}")
print()
print(f"  Roots = (10 ± 2√5)/2 = 5 ± √5")
print(f"  5 + √5 = {5+np.sqrt(5):.10f}")
print(f"  5 - √5 = {5-np.sqrt(5):.10f}")

# And there's a 6.0 eigenvalue too
print(f"\n  The third distinct Laplacian eigenvalue: 6.0")
print(f"  Degree of original nodes: 6")
print(f"  This is the degree eigenvalue!")

