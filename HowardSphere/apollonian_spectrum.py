"""
Apollonian Gasket Spectrum
==========================
Build the contact graph of an Apollonian gasket at successive levels,
compute the graph Laplacian spectrum, and look for characteristic
polynomials / eigenvalue ratios analogous to x²-5x+2=0 for Menger.

Level 0: 3 mutually tangent circles + 1 outer = 4 circles
Level 1: Fill 4 gaps → 4 new circles = 8 total
Level 2: Fill 12 gaps → 12 new circles = 20 total
...

The Apollonian gasket ADDS where Menger REMOVES.
"""

import numpy as np
from itertools import combinations
from fractions import Fraction

# =============================================================================
# DESCARTES CIRCLE THEOREM
# =============================================================================
# If four mutually tangent circles have curvatures k1,k2,k3,k4:
# (k1+k2+k3+k4)² = 2(k1²+k2²+k3²+k4²)
# Given three, the fourth is:
# k4 = k1+k2+k3 + 2*sqrt(k1*k2 + k2*k3 + k3*k1)

def descartes_fourth(k1, k2, k3):
    """Given three mutually tangent circle curvatures, find the fourth."""
    s = k1 + k2 + k3
    p = k1*k2 + k2*k3 + k3*k1
    return s + 2*np.sqrt(p)

def descartes_fourth_inner(k1, k2, k3):
    """The inner (smaller) solution — the one that fits in the gap."""
    s = k1 + k2 + k3
    p = k1*k2 + k2*k3 + k3*k1
    # Two solutions: s ± 2√p
    # The larger curvature (smaller circle) is s + 2√p
    return s + 2*np.sqrt(p)

# =============================================================================
# BUILD APOLLONIAN GASKET
# =============================================================================

class ApollonianGasket:
    def __init__(self):
        # Start with the standard configuration:
        # Outer circle with curvature -1 (negative = contains others)
        # Three inner circles with curvature 2 each
        # These satisfy Descartes: (-1+2+2+2)² = 25, 2(1+4+4+4) = 26... 
        # Actually let's use the classic (−1, 2, 2, 3) or compute properly
        
        # Standard start: three mutually tangent unit circles
        # Curvatures: k_outer = -1, k1=k2=k3=2 doesn't work perfectly
        # Let me use the classic integral Apollonian: (-1, 2, 2, 3)
        # Check: (-1+2+2+3)² = 36, 2(1+4+4+9) = 36 ✓
        
        self.circles = []  # list of (curvature, level)
        self.tangencies = []  # list of (i, j) pairs
        self.triangles = []  # "gaps" = triples of mutually tangent circles
        
        # Level 0: four initial circles
        self.circles.append((-1, 0))  # outer
        self.circles.append((2, 0))   # inner 1
        self.circles.append((2, 0))   # inner 2  
        self.circles.append((3, 0))   # inner 3
        
        # All four are mutually tangent
        for i, j in combinations(range(4), 2):
            self.tangencies.append((i, j))
        
        # Four triangular gaps (each triple of the 4 circles)
        self.triangles = [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3),
        ]
        
        self.level = 0
    
    def iterate(self):
        """Fill all current triangular gaps with inscribed circles."""
        self.level += 1
        new_triangles = []
        
        for tri in self.triangles:
            i, j, k = tri
            ki = self.circles[i][0]
            kj = self.circles[j][0]
            kk = self.circles[k][0]
            
            # New circle curvature via Descartes
            k_new = ki + kj + kk + 2*np.sqrt(ki*kj + kj*kk + kk*ki)
            
            # Add new circle
            new_idx = len(self.circles)
            self.circles.append((k_new, self.level))
            
            # New circle is tangent to all three parents
            self.tangencies.append((new_idx, i))
            self.tangencies.append((new_idx, j))
            self.tangencies.append((new_idx, k))
            
            # Three new triangular gaps formed
            new_triangles.append((new_idx, i, j))
            new_triangles.append((new_idx, i, k))
            new_triangles.append((new_idx, j, k))
        
        self.triangles = new_triangles
    
    def adjacency_matrix(self):
        """Build adjacency matrix from tangency list."""
        n = len(self.circles)
        A = np.zeros((n, n))
        for i, j in self.tangencies:
            A[i, j] = 1
            A[j, i] = 1
        return A
    
    def laplacian_matrix(self):
        """L = D - A"""
        A = self.adjacency_matrix()
        D = np.diag(A.sum(axis=1))
        return D - A
    
    def normalized_laplacian(self):
        """L_norm = D^{-1/2} L D^{-1/2}"""
        A = self.adjacency_matrix()
        d = A.sum(axis=1)
        d_inv_sqrt = np.where(d > 0, 1.0/np.sqrt(d), 0)
        D_inv_sqrt = np.diag(d_inv_sqrt)
        L = np.diag(d) - A
        return D_inv_sqrt @ L @ D_inv_sqrt


# =============================================================================
# COMPUTE AND ANALYZE
# =============================================================================

print("="*70)
print("  APOLLONIAN GASKET: SPECTRAL ANALYSIS")
print("  The expansion complement to Menger's void")
print("="*70)

for max_level in range(6):
    g = ApollonianGasket()
    for _ in range(max_level):
        g.iterate()
    
    n = len(g.circles)
    n_edges = len(g.tangencies)
    n_gaps = len(g.triangles)
    
    A = g.adjacency_matrix()
    L = g.laplacian_matrix()
    
    # Eigenvalues
    eigs_A = np.sort(np.linalg.eigvalsh(A))[::-1]  # descending
    eigs_L = np.sort(np.linalg.eigvalsh(L))  # ascending
    
    print(f"\n{'─'*70}")
    print(f"  Level {max_level}: {n} circles, {n_edges} tangencies, {n_gaps} gaps")
    print(f"{'─'*70}")
    
    # Curvatures
    curvs = [c[0] for c in g.circles]
    print(f"  Curvatures: {[f'{k:.1f}' for k in curvs[:20]]}")
    if n > 20:
        print(f"    ...({n-20} more)")
    
    # Degree sequence
    degrees = A.sum(axis=1).astype(int)
    unique_degs, counts = np.unique(degrees, return_counts=True)
    print(f"  Degree sequence: {dict(zip(unique_degs, counts))}")
    
    # Adjacency spectrum
    print(f"  Adjacency eigenvalues (top 10):")
    for i, e in enumerate(eigs_A[:min(10, n)]):
        print(f"    λ_A[{i}] = {e:.8f}")
    
    # Laplacian spectrum  
    print(f"  Laplacian eigenvalues (first 10):")
    for i, e in enumerate(eigs_L[:min(10, n)]):
        print(f"    λ_L[{i}] = {e:.8f}")
    
    # KEY RATIOS
    if n > 2:
        nonzero_L = eigs_L[eigs_L > 1e-10]
        if len(nonzero_L) >= 2:
            print(f"\n  KEY RATIOS:")
            print(f"    λ_L[1]/λ_L[0] (first nonzero) = --")
            print(f"    λ_L[1] = {nonzero_L[0]:.8f}")
            if len(nonzero_L) >= 2:
                print(f"    λ_L[2]/λ_L[1] = {nonzero_L[1]/nonzero_L[0]:.8f}")
            print(f"    λ_A[0] (spectral radius) = {eigs_A[0]:.8f}")
            if abs(eigs_A[-1]) > 1e-10:
                print(f"    λ_A[0]/|λ_A[-1]| = {eigs_A[0]/abs(eigs_A[-1]):.8f}")
            
            # Sum and product of first two nonzero Laplacian eigenvalues
            if len(nonzero_L) >= 2:
                s = nonzero_L[0] + nonzero_L[1]
                p = nonzero_L[0] * nonzero_L[1]
                print(f"\n    First two nonzero Laplacian eigenvalues:")
                print(f"    Sum  S = {s:.8f}")
                print(f"    Prod P = {p:.8f}")
                print(f"    Polynomial: x² - {s:.6f}x + {p:.6f} = 0")
                disc = s**2 - 4*p
                print(f"    Discriminant Δ = {disc:.8f}")

print(f"\n{'='*70}")
print("  MENGER COMPARISON")
print(f"{'='*70}")
print(f"  Menger Level 1: x² - 5x + 2 = 0")
print(f"  S=5, P=2, Δ=17")
print(f"  Roots: {(5+np.sqrt(17))/2:.8f}, {(5-np.sqrt(17))/2:.8f}")

