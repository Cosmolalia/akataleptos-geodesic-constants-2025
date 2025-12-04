#!/usr/bin/env python3
"""
Hamiltonian Path Integration + Brute Force Perfect Point Finder

Goal: Find the configuration that gives 100% accuracy on ALL constants

Strategy:
1. Start from known good points
2. Use Hamiltonian dynamics to explore local landscape
3. Brute force grid search in promising regions
4. Look for the mythical 100.000% on all 10 constants

This is computationally expensive but your 32-core machine can handle it!
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.integrate import odeint
import multiprocessing as mp
from functools import partial
import json
from datetime import datetime
import argparse

# ============================================================================
# RESONANCE CHAMBER (Optimized)
# ============================================================================

class ResonanceChamber:
    def __init__(self, chamber_size, num_points=12000):  # Slightly reduced for speed
        self.chamber_size = chamber_size
        self.num_points = num_points
        self.x = np.linspace(0, chamber_size, num_points)
        
    def generate_wave(self, wavelength):
        k = 2 * np.pi / wavelength
        return np.sin(k * self.x)
    
    def compute_interference(self, wavelengths):
        total_field = np.zeros(len(self.x))
        for wl in wavelengths:
            if wl > 0:
                total_field += self.generate_wave(wl)
        return total_field
    
    def extract_ratios(self, field):
        peaks, _ = find_peaks(np.abs(field), prominence=0.5)
        if len(peaks) < 2:
            return []
        
        peak_positions = self.x[peaks]
        ratios = []
        sample_size = min(150, len(peak_positions))
        sampled_peaks = peak_positions[::max(1, len(peak_positions)//sample_size)]
        
        for i in range(len(sampled_peaks)):
            for j in range(i+1, min(i+20, len(sampled_peaks))):
                ratio = sampled_peaks[j] / sampled_peaks[i]
                if 1.01 < ratio < 3000:
                    ratios.append(ratio)
        return ratios
    
    def find_best_match(self, ratios, target):
        if not ratios:
            return None, float('inf')
        differences = [abs(r - target) for r in ratios]
        min_diff = min(differences)
        best_ratio = ratios[differences.index(min_diff)]
        return best_ratio, min_diff

# Target constants
CONSTANTS = {
    'fine_structure': 137.035999084,
    'phi': 1.618033988749895,
    'pi': 3.141592653589793,
    'e': 2.718281828459045,
    'proton_electron_mass': 1836.15267343,
    'weak_mixing_angle': 28.74,
    'muon_electron_mass': 206.7682830,
    'sqrt_2': 1.414213562373095,
    'sqrt_3': 1.732050807568877,
    'sqrt_5': 2.236067977499790,
}

# Simple integer wavelengths (we now know this works!)
WAVELENGTHS = list(range(1, 31))

def compute_accuracy_vector(L, s):
    """
    Compute accuracy for ALL constants at given (L, s)
    Returns: (avg_accuracy, min_accuracy, accuracies_dict, all_perfect)
    """
    wavelengths = [w * s for w in WAVELENGTHS]
    
    chamber = ResonanceChamber(L)
    field = chamber.compute_interference(wavelengths)
    ratios = chamber.extract_ratios(field)
    
    if not ratios:
        return 0.0, 0.0, {}, False
    
    accuracies = {}
    for name, target in CONSTANTS.items():
        match, error = chamber.find_best_match(ratios, target)
        if match is not None:
            acc = 100 * (1 - error / target)
            accuracies[name] = acc
        else:
            accuracies[name] = 0.0
    
    avg_acc = np.mean(list(accuracies.values()))
    min_acc = np.min(list(accuracies.values()))
    all_perfect = all(a >= 99.9999 for a in accuracies.values())  # 99.9999% = essentially perfect
    
    return avg_acc, min_acc, accuracies, all_perfect

# ============================================================================
# HAMILTONIAN DYNAMICS
# ============================================================================

def compute_gradient(L, s, h=0.1):
    """
    Compute gradient of average accuracy w.r.t. (L, s)
    Using finite differences
    """
    # Center point
    acc_center, _, _, _ = compute_accuracy_vector(L, s)
    
    # Gradients
    acc_L_plus, _, _, _ = compute_accuracy_vector(L + h, s)
    acc_L_minus, _, _, _ = compute_accuracy_vector(L - h, s)
    acc_s_plus, _, _, _ = compute_accuracy_vector(L, s + h*0.001)  # Smaller step for s
    acc_s_minus, _, _, _ = compute_accuracy_vector(L, s - h*0.001)
    
    grad_L = (acc_L_plus - acc_L_minus) / (2 * h)
    grad_s = (acc_s_plus - acc_s_minus) / (2 * h * 0.001)
    
    return np.array([grad_L, grad_s])

def hamiltonian_step(state, dt=0.1, friction=0.1):
    """
    One step of Hamiltonian dynamics
    
    state = [L, s, p_L, p_s]  (position and momentum)
    
    Hamiltonian: H = K(p) + V(L,s)
    where V = -accuracy (we want to maximize accuracy = minimize -accuracy)
    
    Returns: new_state
    """
    L, s, p_L, p_s = state
    
    # Compute force (negative gradient of potential)
    grad = compute_gradient(L, s)
    force_L, force_s = grad  # Positive gradient means go uphill (maximize accuracy)
    
    # Update momenta (with friction)
    p_L_new = (1 - friction) * p_L + force_L * dt
    p_s_new = (1 - friction) * p_s + force_s * dt
    
    # Update positions
    L_new = L + p_L_new * dt
    s_new = s + p_s_new * dt
    
    # Bounds
    L_new = np.clip(L_new, 500, 5000)
    s_new = np.clip(s_new, 0.05, 0.5)
    
    return np.array([L_new, s_new, p_L_new, p_s_new])

def hamiltonian_trajectory(L_start, s_start, n_steps=50, dt=0.1):
    """
    Follow Hamiltonian trajectory from starting point
    Returns: list of (L, s, accuracy) tuples
    """
    print(f"  Starting Hamiltonian trajectory from L={L_start:.1f}, s={s_start:.3f}")
    
    state = np.array([L_start, s_start, 0.0, 0.0])  # Start with zero momentum
    trajectory = []
    
    for step in range(n_steps):
        L, s = state[0], state[1]
        avg_acc, min_acc, accs, perfect = compute_accuracy_vector(L, s)
        
        trajectory.append({
            'L': L,
            's': s,
            'avg_accuracy': avg_acc,
            'min_accuracy': min_acc,
            'accuracies': accs,
            'all_perfect': perfect
        })
        
        if perfect:
            print(f"    ★ PERFECT POINT FOUND at L={L:.3f}, s={s:.4f}!")
            break
        
        if step % 10 == 0:
            print(f"    Step {step}: L={L:.1f}, s={s:.3f}, avg={avg_acc:.4f}%, min={min_acc:.4f}%")
        
        # Take Hamiltonian step
        state = hamiltonian_step(state, dt=dt)
    
    return trajectory

# ============================================================================
# BRUTE FORCE GRID SEARCH
# ============================================================================

def grid_search_local(L_center, s_center, L_range=50, s_range=0.02, L_steps=21, s_steps=21):
    """
    Fine grid search around a promising point
    """
    print(f"  Grid searching around L={L_center:.1f}, s={s_center:.3f}")
    print(f"    L range: [{L_center-L_range:.1f}, {L_center+L_range:.1f}]")
    print(f"    s range: [{s_center-s_range:.3f}, {s_center+s_range:.3f}]")
    
    L_vals = np.linspace(L_center - L_range, L_center + L_range, L_steps)
    s_vals = np.linspace(s_center - s_range, s_center + s_range, s_steps)
    
    best_avg = 0
    best_min = 0
    best_L = L_center
    best_s = s_center
    best_accs = {}
    perfect_found = False
    
    total = len(L_vals) * len(s_vals)
    count = 0
    
    for L in L_vals:
        for s in s_vals:
            count += 1
            if count % 50 == 0:
                print(f"    Progress: {count}/{total} ({100*count/total:.1f}%)")
            
            avg_acc, min_acc, accs, perfect = compute_accuracy_vector(L, s)
            
            if perfect:
                print(f"    ★ PERFECT POINT: L={L:.3f}, s={s:.4f}")
                return L, s, avg_acc, min_acc, accs, True
            
            # Track best by minimum accuracy (want all constants high)
            if min_acc > best_min:
                best_min = min_acc
                best_avg = avg_acc
                best_L = L
                best_s = s
                best_accs = accs
    
    print(f"    Best found: L={best_L:.3f}, s={best_s:.4f}, avg={best_avg:.4f}%, min={best_min:.4f}%")
    
    return best_L, best_s, best_avg, best_min, best_accs, perfect_found

# ============================================================================
# MULTI-START STRATEGY
# ============================================================================

def find_perfect_point(starting_points, use_hamiltonian=True, use_grid=True):
    """
    Multi-strategy search for perfect 100% point
    
    Strategy:
    1. Start from multiple known good points
    2. Use Hamiltonian dynamics to explore landscape
    3. Do fine grid search around promising regions
    4. Look for the perfect configuration
    """
    
    print("="*80)
    print("SEARCHING FOR PERFECT 100% CONFIGURATION")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Starting points: {len(starting_points)}")
    print(f"Strategies: Hamiltonian={'YES' if use_hamiltonian else 'NO'}, Grid={'YES' if use_grid else 'NO'}")
    print()
    
    all_results = []
    perfect_points = []
    
    for i, (L_start, s_start) in enumerate(starting_points):
        print(f"\n{'='*80}")
        print(f"STARTING POINT {i+1}/{len(starting_points)}: L={L_start}, s={s_start}")
        print(f"{'='*80}")
        
        # Initial evaluation
        avg_acc, min_acc, accs, perfect = compute_accuracy_vector(L_start, s_start)
        print(f"Initial: avg={avg_acc:.4f}%, min={min_acc:.4f}%")
        
        if perfect:
            print("★ ALREADY PERFECT!")
            perfect_points.append((L_start, s_start, avg_acc, accs))
            continue
        
        # Hamiltonian exploration
        if use_hamiltonian:
            print("\nPhase 1: Hamiltonian trajectory...")
            trajectory = hamiltonian_trajectory(L_start, s_start, n_steps=30, dt=0.5)
            
            # Find best point along trajectory
            best_traj = max(trajectory, key=lambda x: x['min_accuracy'])
            
            if best_traj['all_perfect']:
                print("★ PERFECT FOUND IN TRAJECTORY!")
                perfect_points.append((
                    best_traj['L'],
                    best_traj['s'],
                    best_traj['avg_accuracy'],
                    best_traj['accuracies']
                ))
                continue
            
            L_best, s_best = best_traj['L'], best_traj['s']
            print(f"Best trajectory point: L={L_best:.3f}, s={s_best:.4f}, min={best_traj['min_accuracy']:.4f}%")
        else:
            L_best, s_best = L_start, s_start
        
        # Grid refinement around best point
        if use_grid:
            print("\nPhase 2: Fine grid search...")
            L_final, s_final, avg_final, min_final, accs_final, perfect = grid_search_local(
                L_best, s_best,
                L_range=25,
                s_range=0.01,
                L_steps=21,
                s_steps=21
            )
            
            if perfect:
                print("★ PERFECT FOUND IN GRID!")
                perfect_points.append((L_final, s_final, avg_final, accs_final))
            
            all_results.append({
                'start_L': L_start,
                'start_s': s_start,
                'final_L': L_final,
                'final_s': s_final,
                'avg_accuracy': avg_final,
                'min_accuracy': min_final,
                'accuracies': accs_final,
                'perfect': perfect
            })
    
    # Summary
    print("\n" + "="*80)
    print("SEARCH COMPLETE")
    print("="*80)
    
    if perfect_points:
        print(f"\n★★★ FOUND {len(perfect_points)} PERFECT POINT(S)! ★★★")
        for L, s, avg, accs in perfect_points:
            print(f"\n  L = {L:.6f}")
            print(f"  s = {s:.6f}")
            print(f"  Average accuracy: {avg:.8f}%")
            print(f"  All constants:")
            for name, acc in sorted(accs.items(), key=lambda x: x[1], reverse=True):
                print(f"    {name:25s}: {acc:.8f}%")
    else:
        print("\n✗ No perfect 100% point found")
        print("\nBest results:")
        best = max(all_results, key=lambda x: x['min_accuracy'])
        print(f"  L = {best['final_L']:.6f}")
        print(f"  s = {best['final_s']:.6f}")
        print(f"  Average: {best['avg_accuracy']:.6f}%")
        print(f"  Minimum: {best['min_accuracy']:.6f}%")
        print(f"\n  Constants:")
        for name, acc in sorted(best['accuracies'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {name:25s}: {acc:.8f}%")
    
    return all_results, perfect_points

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Find perfect 100% configuration')
    parser.add_argument('--no-hamiltonian', action='store_true',
                       help='Skip Hamiltonian dynamics (grid only)')
    parser.add_argument('--no-grid', action='store_true',
                       help='Skip grid search (Hamiltonian only)')
    parser.add_argument('--output', type=str, default='./perfect_point_search.json',
                       help='Output file for results')
    
    args = parser.parse_args()
    
    # Known good starting points
    starting_points = [
        (2997.0, 0.338),   # Dual optimization result
        (2997.0, 0.291),   # Best from sensitivity scan
        (1836.0, 0.1),     # Master constant
        (3000.0, 0.333),   # Round numbers
        (2970.8, 0.340),   # 1836 × φ, e/8
        (3236.8, 0.291),   # Best chamber from sensitivity
        (147.97, 0.1),     # Original optimization
    ]
    
    results, perfect = find_perfect_point(
        starting_points,
        use_hamiltonian=not args.no_hamiltonian,
        use_grid=not args.no_grid
    )
    
    # Save results
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'starting_points': starting_points,
        'all_results': results,
        'perfect_points': [(p[0], p[1], p[2], p[3]) for p in perfect],
        'found_perfect': len(perfect) > 0
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to: {args.output}")
    print(f"End time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
