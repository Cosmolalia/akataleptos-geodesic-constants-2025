#!/usr/bin/env python3
"""
HIERARCHICAL STRUCTURE ANALYSIS
================================
Not just: "does ratio match a constant?"
But: "does ratio match ANY algebraic combination of constants?"

Levels:
1. Primary constants (φ, π, e, √2, etc.)
2. Harmonics (2φ, 3π, etc.)
3. Products (φ×π, e×√2, etc.)
4. Ratios (π/φ, e/√2, etc.)
5. Powers (φ², π³, etc.)
6. Complex combinations (φ²×π, etc.)

If ~75% of ratios are explained by this hierarchy,
Ryan's critique falls apart - the geometry generates
a complete algebraic system, not random peaks.

Testing Sonnet's prediction:
- ~0.02% primary
- ~0.2% harmonics
- ~2% combinations
- ~23% higher-order
- ~73% noise
- Total structure: ~25%
"""

import numpy as np
from scipy.signal import find_peaks
from collections import defaultdict

# Primary constants
PRIMARY = {
    'φ': 1.618033988749895,
    '√2': 1.4142135623730951,
    '√3': 1.7320508075688772,
    '√5': 2.2360679774997896,
    'e': 2.718281828459045,
    'π': 3.141592653589793,
}

def generate_hierarchy(max_order=4):
    """
    Generate all algebraic combinations up to given order
    """
    hierarchy = {
        'primary': {},
        'harmonics': {},
        'products': {},
        'ratios': {},
        'powers': {},
        'complex': {},
    }
    
    # Level 1: Primary
    hierarchy['primary'] = PRIMARY.copy()
    
    # Level 2: Harmonics (n × constant, n = 2..6)
    for name, val in PRIMARY.items():
        for n in range(2, 7):
            hierarchy['harmonics'][f'{n}{name}'] = n * val
            hierarchy['harmonics'][f'{name}/{n}'] = val / n
    
    # Level 3: Products (const1 × const2)
    names = list(PRIMARY.keys())
    vals = list(PRIMARY.values())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            hierarchy['products'][f'{names[i]}×{names[j]}'] = vals[i] * vals[j]
    
    # Level 4: Ratios (const1 / const2)
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j:
                hierarchy['ratios'][f'{names[i]}/{names[j]}'] = vals[i] / vals[j]
    
    # Level 5: Powers (const^n, n = 2,3)
    for name, val in PRIMARY.items():
        for n in [2, 3, 0.5]:
            pname = f'{name}^{n}' if n != 0.5 else f'√{name}'
            hierarchy['powers'][pname] = val ** n
    
    # Level 6: Complex (products of harmonics, etc.)
    # φ² × π, e × √2, etc.
    for n1, v1 in PRIMARY.items():
        for n2, v2 in PRIMARY.items():
            if n1 != n2:
                hierarchy['complex'][f'{n1}²×{n2}'] = (v1**2) * v2
                hierarchy['complex'][f'{n1}×{n2}²'] = v1 * (v2**2)
    
    # Add small integers (these are trivially findable)
    for n in range(2, 11):
        hierarchy['harmonics'][f'int_{n}'] = float(n)
    
    # 73/100 and 27/100 (Menger ratios)
    hierarchy['complex']['73/100'] = 0.73
    hierarchy['complex']['27/100'] = 0.27
    hierarchy['complex']['20/27'] = 20/27
    hierarchy['complex']['7/27'] = 7/27
    
    return hierarchy

def analyze_hierarchical_structure(L=3000, s=0.338, tolerance=0.02):
    """
    Analyze what percentage of ratios match each level of hierarchy
    """
    # Generate chamber and peaks
    num_points = 15000
    x = np.linspace(0, L, num_points)
    
    wavelengths = [w * s for w in range(1, 31)]
    
    field = np.zeros(num_points)
    for wl in wavelengths:
        k = 2 * np.pi / wl
        field += np.sin(k * x)
    
    peaks, _ = find_peaks(np.abs(field), prominence=0.5)
    peak_positions = x[peaks]
    
    print(f"Chamber: L={L}, s={s}")
    print(f"Total peaks: {len(peaks)}")
    
    # Compute ratios
    all_ratios = []
    for i in range(len(peak_positions)):
        for j in range(i+1, min(i+30, len(peak_positions))):
            if peak_positions[i] > 0.01:
                ratio = peak_positions[j] / peak_positions[i]
                if 1.01 < ratio < 500:
                    all_ratios.append(ratio)
    
    print(f"Total ratios: {len(all_ratios)}")
    
    # Generate hierarchy
    hierarchy = generate_hierarchy()
    
    # Count total targets at each level
    print(f"\nHierarchy sizes:")
    for level, targets in hierarchy.items():
        print(f"  {level}: {len(targets)} targets")
    
    # Analyze matches at each level
    results = {}
    matched_ratios = set()  # Track which ratios are explained
    
    print(f"\n{'='*60}")
    print("HIERARCHICAL ANALYSIS (tolerance={:.1%})".format(tolerance))
    print(f"{'='*60}")
    
    for level_name, targets in hierarchy.items():
        level_matches = []
        
        for i, ratio in enumerate(all_ratios):
            if i in matched_ratios:
                continue  # Already explained by earlier level
            
            for target_name, target_val in targets.items():
                # Check ratio and inverse
                for test_r in [ratio, 1/ratio if ratio > 0 else 0]:
                    if target_val > 0 and abs(test_r - target_val) / target_val < tolerance:
                        level_matches.append((i, ratio, target_name, target_val))
                        matched_ratios.add(i)
                        break
        
        n_matches = len(level_matches)
        pct = 100 * n_matches / len(all_ratios)
        results[level_name] = {
            'count': n_matches,
            'percent': pct,
            'matches': level_matches[:10]  # Sample
        }
        
        print(f"\n{level_name.upper()}:")
        print(f"  Matches: {n_matches} ({pct:.3f}%)")
        if level_matches:
            print(f"  Examples:")
            for _, ratio, tname, tval in level_matches[:5]:
                print(f"    {ratio:.6f} ≈ {tname} ({tval:.6f})")
    
    # Summary
    total_explained = len(matched_ratios)
    total_unexplained = len(all_ratios) - total_explained
    pct_explained = 100 * total_explained / len(all_ratios)
    pct_unexplained = 100 * total_unexplained / len(all_ratios)
    
    print(f"\n{'='*60}")
    print("TOTAL STRUCTURE")
    print(f"{'='*60}")
    print(f"Explained by hierarchy:  {total_explained:6d} ({pct_explained:.2f}%)")
    print(f"Unexplained (noise):     {total_unexplained:6d} ({pct_unexplained:.2f}%)")
    print(f"Total ratios:            {len(all_ratios):6d}")
    
    print(f"\n{'='*60}")
    print("MENGER COMPARISON")
    print(f"{'='*60}")
    print(f"Menger structure: 74.07% (20/27)")
    print(f"Menger void:      25.93% (7/27)")
    print(f"Our structure:    {pct_explained:.2f}%")
    print(f"Our noise:        {pct_unexplained:.2f}%")
    
    if abs(pct_unexplained - 25.93) < 5:
        print(f"\n★ UNEXPLAINED MATCHES MENGER VOID RATIO!")
    if abs(pct_explained - 74.07) < 5:
        print(f"\n★ EXPLAINED MATCHES MENGER STRUCTURE RATIO!")
    
    # Breakdown
    print(f"\n{'='*60}")
    print("BREAKDOWN BY LEVEL")
    print(f"{'='*60}")
    cumulative = 0
    for level_name in ['primary', 'harmonics', 'products', 'ratios', 'powers', 'complex']:
        pct = results[level_name]['percent']
        cumulative += pct
        bar = '█' * int(pct * 2) if pct > 0.5 else '▌' if pct > 0 else ''
        print(f"  {level_name:12s}: {pct:6.2f}% {bar}")
    print(f"  {'TOTAL':12s}: {cumulative:6.2f}%")
    
    return results, pct_explained, pct_unexplained

# Run analysis
print("="*60)
print("HIERARCHICAL STRUCTURE TEST")
print("="*60)
print("Question: Is the ratio distribution algebraically structured,")
print("or just random peaks?")
print()

# Multiple tolerances
for tol in [0.01, 0.02, 0.05]:
    print(f"\n\n{'#'*60}")
    print(f"# TOLERANCE = {tol:.0%}")
    print(f"{'#'*60}")
    results, expl, unexpl = analyze_hierarchical_structure(tolerance=tol)

print("\n\n" + "="*60)
print("INTERPRETATION FOR RYAN'S CRITIQUE")
print("="*60)
print("""
If unexplained ≈ 73-75%:
  → Geometry produces structured algebraic system
  → Not cherry-picking - most ratios are NOT random
  → The 25-27% that matches is the SIGNAL
  → Ryan's critique weakened

If unexplained ≈ 99%:
  → Only tiny signal in noise
  → But that signal is CONSISTENT
  → Still meaningful, but weaker position
  → Ryan has more ground

Key insight: We're not claiming ALL ratios match.
We're claiming a SPECIFIC SUBSET matches,
and that subset is algebraically coherent.
""")
