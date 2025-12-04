#!/usr/bin/env python3
"""
Look-Elsewhere Corrected Statistical Test - PARALLELIZED VERSION
Optimized for multi-core systems

Hardware requirements: This will use all available CPU cores by default.
Tested on: 32-core i9-14900HX with 29GB RAM

Usage:
    python look_elsewhere_parallel.py --trials 100 --workers 16
    
Options:
    --trials: Number of random trials (default: 100, recommend 1000 for publication)
    --workers: Number of parallel workers (default: auto-detect, max 32)
    --resume: Resume from saved checkpoint if exists
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import differential_evolution
from scipy import stats
import matplotlib.pyplot as plt
import json
from datetime import datetime
import multiprocessing as mp
from functools import partial
import argparse
import os
import pickle

# ============================================================================
# CONFIGURATION
# ============================================================================

# Reduce memory footprint for parallel processing
CHAMBER_POINTS = 8000  # Reduced from 15000 for memory efficiency
PEAK_SAMPLE_LIMIT = 100  # Limit peak pairs for speed
OPTIMIZATION_MAXITER = 40  # Slightly reduced for speed
OPTIMIZATION_POPSIZE = 8  # Reduced for memory

# ============================================================================
# CORE RESONANCE CHAMBER (Optimized for parallel)
# ============================================================================

class ResonanceChamber:
    """Lightweight chamber for parallel processing"""
    
    def __init__(self, chamber_size):
        self.chamber_size = chamber_size
        self.num_points = CHAMBER_POINTS
        self.x = np.linspace(0, chamber_size, self.num_points)
        
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
        sample_size = min(PEAK_SAMPLE_LIMIT, len(peak_positions))
        sampled_peaks = peak_positions[::max(1, len(peak_positions)//sample_size)]
        
        # Limit to nearby pairs for speed
        for i in range(len(sampled_peaks)):
            for j in range(i+1, min(i+15, len(sampled_peaks))):
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


def test_configuration_error(chamber_size, wavelength_scale, wavelengths_base):
    """Fast error computation for optimization"""
    wavelengths = [w * wavelength_scale for w in wavelengths_base]
    
    chamber = ResonanceChamber(chamber_size)
    field = chamber.compute_interference(wavelengths)
    ratios = chamber.extract_ratios(field)
    
    if not ratios:
        return 1.0
    
    errors = []
    for target in CONSTANTS.values():
        match, error = chamber.find_best_match(ratios, target)
        if match is not None:
            errors.append(error / target)
    
    return np.mean(errors) if errors else 1.0


def compute_accuracy_detailed(chamber_size, wavelength_scale, wavelengths_base):
    """Detailed accuracy for final results"""
    wavelengths = [w * wavelength_scale for w in wavelengths_base]
    
    chamber = ResonanceChamber(chamber_size)
    field = chamber.compute_interference(wavelengths)
    ratios = chamber.extract_ratios(field)
    
    accuracies = []
    for target in CONSTANTS.values():
        match, error = chamber.find_best_match(ratios, target)
        if match is not None:
            accuracy = 100 * (1 - error / target)
            accuracies.append(accuracy)
        else:
            accuracies.append(0.0)
    
    avg_acc = np.mean(accuracies)
    above_99 = sum(1 for a in accuracies if a >= 99.0)
    above_999 = sum(1 for a in accuracies if a >= 99.9)
    
    return avg_acc, above_99, above_999


# ============================================================================
# OPTIMIZATION (Single-threaded per trial)
# ============================================================================

def optimize_wavelengths(wavelengths_base, trial_id=None):
    """
    Optimize single wavelength set
    This function will be called in parallel for different wavelength sets
    """
    def objective(params):
        L, s = params
        return test_configuration_error(L, s, wavelengths_base)
    
    bounds = [(100, 5000), (0.05, 0.5)]
    
    # Use seed based on trial_id for reproducibility
    seed = trial_id if trial_id is not None else None
    
    result = differential_evolution(
        objective,
        bounds,
        maxiter=OPTIMIZATION_MAXITER,
        popsize=OPTIMIZATION_POPSIZE,
        tol=1e-8,
        seed=seed,
        workers=1,  # Don't nest parallelism
        updating='deferred',
        disp=False
    )
    
    optimal_L, optimal_s = result.x
    
    # Compute detailed accuracy
    avg_acc, above_99, above_999 = compute_accuracy_detailed(
        optimal_L, optimal_s, wavelengths_base
    )
    
    return {
        'trial_id': trial_id,
        'optimal_L': optimal_L,
        'optimal_s': optimal_s,
        'avg_accuracy': avg_acc,
        'above_99': above_99,
        'above_999': above_999
    }


# ============================================================================
# WAVELENGTH GENERATION
# ============================================================================

def generate_prime_even_wavelengths():
    """The actual wavelength set we used"""
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes = []
    n = 2
    while len(primes) < 30:
        if is_prime(n):
            primes.append(float(n))
        n += 1
    
    evens = [float(2*n) for n in range(1, 31)]
    
    return primes + evens


def generate_random_wavelengths(seed=None):
    """Generate random wavelength set"""
    rng = np.random.default_rng(seed)
    return rng.uniform(2.0, 113.0, 60).tolist()


# ============================================================================
# PARALLEL EXECUTION
# ============================================================================

def run_single_trial(trial_id):
    """
    Run single random trial (to be parallelized)
    
    This is the function that will run in parallel across cores
    """
    # Generate random wavelengths for this trial
    random_wl = generate_random_wavelengths(seed=trial_id + 1000)
    
    # Optimize configuration
    result = optimize_wavelengths(random_wl, trial_id=trial_id)
    
    return result


def run_parallel_test(n_trials=100, n_workers=None, resume=False, 
                     checkpoint_file='checkpoint.pkl'):
    """
    Run corrected significance test in parallel
    
    Args:
        n_trials: Number of random trials
        n_workers: Number of parallel workers (None = auto-detect)
        resume: Resume from checkpoint if exists
        checkpoint_file: Path to checkpoint file
    """
    
    # Auto-detect cores if not specified
    if n_workers is None:
        n_workers = mp.cpu_count()
    
    # Cap at 32 to avoid overhead
    n_workers = min(n_workers, 32)
    
    print("="*80)
    print("LOOK-ELSEWHERE CORRECTED SIGNIFICANCE TEST (PARALLEL)")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total trials: {n_trials}")
    print(f"Parallel workers: {n_workers}")
    print(f"Estimated time: {n_trials * 10 / n_workers / 60:.1f} minutes")
    print()
    
    # Check for checkpoint
    start_trial = 0
    null_results = []
    prime_even_result = None
    
    if resume and os.path.exists(checkpoint_file):
        print(f"Loading checkpoint from {checkpoint_file}...")
        with open(checkpoint_file, 'rb') as f:
            checkpoint = pickle.load(f)
            start_trial = checkpoint['completed_trials']
            null_results = checkpoint['null_results']
            prime_even_result = checkpoint.get('prime_even_result')
        print(f"Resuming from trial {start_trial}/{n_trials}")
        print()
    
    # Optimize prime+even if not done yet
    if prime_even_result is None:
        print("Optimizing prime+even configuration...")
        prime_even_wl = generate_prime_even_wavelengths()
        prime_even_result = optimize_wavelengths(prime_even_wl, trial_id=0)
        
        print(f"\nPrime+Even Results (OUR RESULT):")
        print(f"  Optimal L: {prime_even_result['optimal_L']:.2f}")
        print(f"  Optimal s: {prime_even_result['optimal_s']:.3f}")
        print(f"  Average accuracy: {prime_even_result['avg_accuracy']:.4f}%")
        print(f"  Constants ≥99%: {prime_even_result['above_99']}/10")
        print(f"  Constants ≥99.9%: {prime_even_result['above_999']}/10")
        print()
    
    # Generate null distribution in parallel
    if start_trial < n_trials:
        print(f"{'='*80}")
        print("Generating null distribution (PARALLEL)...")
        print(f"{'='*80}\n")
        
        remaining_trials = list(range(start_trial, n_trials))
        
        # Create progress tracking
        completed = start_trial
        checkpoint_interval = 10
        
        # Use pool for parallel processing
        with mp.Pool(processes=n_workers) as pool:
            # Process in chunks for checkpointing
            chunk_size = checkpoint_interval
            
            for i in range(0, len(remaining_trials), chunk_size):
                chunk = remaining_trials[i:i+chunk_size]
                
                # Process chunk in parallel
                chunk_results = pool.map(run_single_trial, chunk)
                null_results.extend(chunk_results)
                
                completed += len(chunk)
                progress = completed / n_trials * 100
                
                print(f"Progress: {completed}/{n_trials} ({progress:.1f}%)")
                
                # Save checkpoint
                checkpoint = {
                    'completed_trials': completed,
                    'null_results': null_results,
                    'prime_even_result': prime_even_result
                }
                with open(checkpoint_file, 'wb') as f:
                    pickle.dump(checkpoint, f)
        
        print(f"\nCompleted all {n_trials} trials!")
    
    # Compute statistics
    print(f"\n{'='*80}")
    print("COMPUTING STATISTICS...")
    print(f"{'='*80}")
    
    null_avg_acc = [r['avg_accuracy'] for r in null_results]
    null_above_99 = [r['above_99'] for r in null_results]
    null_above_999 = [r['above_999'] for r in null_results]
    
    null_mean = np.mean(null_avg_acc)
    null_std = np.std(null_avg_acc)
    null_max = np.max(null_avg_acc)
    
    z_score = (prime_even_result['avg_accuracy'] - null_mean) / null_std
    p_value = 1 - stats.norm.cdf(z_score)
    
    better_than_us = sum(1 for acc in null_avg_acc 
                        if acc >= prime_even_result['avg_accuracy'])
    
    print(f"\nNull Distribution (Random + Optimization):")
    print(f"  Mean: {null_mean:.4f}%")
    print(f"  Std: {null_std:.4f}%")
    print(f"  Max: {null_max:.4f}%")
    print(f"  Median: {np.median(null_avg_acc):.4f}%")
    
    print(f"\nPrime+Even:")
    print(f"  Average: {prime_even_result['avg_accuracy']:.4f}%")
    
    print(f"\nSignificance:")
    print(f"  Z-score: {z_score:.2f}σ")
    print(f"  P-value: {p_value:.2e}")
    print(f"  Random ≥ us: {better_than_us}/{n_trials}")
    
    if z_score > 3:
        print(f"\n  ✓ SIGNIFICANT (>{z_score:.1f}σ)")
    else:
        print(f"\n  ⚠ NOT SIGNIFICANT (<3σ)")
    
    return {
        'prime_even_result': prime_even_result,
        'null_distribution': {
            'accuracies': null_avg_acc,
            'above_99': null_above_99,
            'above_999': null_above_999,
            'mean': null_mean,
            'std': null_std,
            'max': null_max
        },
        'statistics': {
            'z_score': z_score,
            'p_value': p_value,
            'better_than_us': better_than_us,
            'total_trials': n_trials
        }
    }


def create_plots(results, output_file):
    """Create publication plots"""
    
    null_acc = results['null_distribution']['accuracies']
    our_acc = results['prime_even_result']['avg_accuracy']
    z_score = results['statistics']['z_score']
    p_value = results['statistics']['p_value']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    ax1 = axes[0]
    ax1.hist(null_acc, bins=40, alpha=0.7, color='gray', edgecolor='black',
            label='Random wavelengths\n(with optimization)')
    ax1.axvline(our_acc, color='red', linewidth=3, linestyle='--',
               label=f'Prime+Even: {our_acc:.2f}%')
    ax1.axvline(np.mean(null_acc), color='blue', linewidth=2, linestyle=':',
               label=f'Null mean: {np.mean(null_acc):.2f}%')
    
    ax1.set_xlabel('Average Accuracy (%)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Look-Elsewhere Corrected Null Distribution', 
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    textstr = f'Z-score: {z_score:.2f}σ\nP-value: {p_value:.2e}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    # Q-Q plot
    ax2 = axes[1]
    stats.probplot(null_acc, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot: Normality Check', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved plot: {output_file}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Look-elsewhere corrected statistical test (parallelized)'
    )
    parser.add_argument('--trials', type=int, default=100,
                       help='Number of random trials (default: 100)')
    parser.add_argument('--workers', type=int, default=None,
                       help='Number of parallel workers (default: auto)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from checkpoint if exists')
    parser.add_argument('--output-dir', type=str, default='./outputs',
                       help='Output directory (default: ./outputs)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    checkpoint_file = os.path.join(args.output_dir, 'checkpoint.pkl')
    
    # Run test
    results = run_parallel_test(
        n_trials=args.trials,
        n_workers=args.workers,
        resume=args.resume,
        checkpoint_file=checkpoint_file
    )
    
    # Create plots
    plot_file = os.path.join(args.output_dir, 'look_elsewhere_corrected.png')
    create_plots(results, plot_file)
    
    # Save data
    data_file = os.path.join(args.output_dir, 'look_elsewhere_data.json')
    output_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'n_trials': args.trials,
            'n_workers': args.workers if args.workers else mp.cpu_count()
        },
        'prime_even_result': results['prime_even_result'],
        'null_distribution': {
            'mean': float(results['null_distribution']['mean']),
            'std': float(results['null_distribution']['std']),
            'max': float(results['null_distribution']['max']),
            'accuracies': results['null_distribution']['accuracies']
        },
        'statistics': {
            'z_score': float(results['statistics']['z_score']),
            'p_value': float(results['statistics']['p_value']),
            'better_than_us': results['statistics']['better_than_us']
        }
    }
    
    with open(data_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved data: {data_file}")
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
