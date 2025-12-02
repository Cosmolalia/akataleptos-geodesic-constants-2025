#!/usr/bin/env python3
"""
TOPOLOGY AS WAVE GENERATOR - TEST SUITE
Tests whether ONE wave + topology generates wavelengths, not multiple inputs

Tests:
1. Single frequency (does topology generate harmonics?)
2. White noise (does topology select specific scales?)
3. Random vs structured frequencies (does order matter?)
4. Topology matters (simple vs fractal chamber boundaries)

Your 32-core machine will crush this in ~10 minutes!
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import json
from datetime import datetime

# ============================================================================
# RESONANCE CHAMBER - EXTENDED WITH TOPOLOGY
# ============================================================================

class ResonanceChamber:
    """1D resonance chamber with optional topological features"""
    
    def __init__(self, chamber_size, topology='simple', num_points=15000):
        self.chamber_size = chamber_size
        self.topology = topology
        self.num_points = num_points
        self.x = np.linspace(0, chamber_size, num_points)
        
        # Generate boundary geometry based on topology
        self.boundary_modulation = self._create_topology()
        
    def _create_topology(self):
        """Create boundary modulation based on topology type"""
        
        if self.topology == 'simple':
            # Flat boundaries - standard chamber
            return np.ones(len(self.x))
        
        elif self.topology == 'fractal':
            # Fractal boundary (simplified Menger-like)
            # Multiple scales of perturbation
            modulation = np.ones(len(self.x))
            for scale in [3, 7, 13, 21]:  # Prime-ish scales
                freq = 2 * np.pi * scale / self.chamber_size
                amplitude = 0.05 / scale  # Decreasing amplitude
                modulation += amplitude * np.sin(freq * self.x)
            return modulation
        
        elif self.topology == 'golden':
            # Golden ratio scaling
            phi = 1.618033988749895
            modulation = np.ones(len(self.x))
            for n in range(1, 6):
                freq = 2 * np.pi * (phi ** n) / self.chamber_size
                amplitude = 0.03 / n
                modulation += amplitude * np.sin(freq * self.x)
            return modulation
        
        elif self.topology == 'random':
            # Random perturbations (control)
            return 1.0 + 0.1 * np.random.randn(len(self.x))
        
        else:
            return np.ones(len(self.x))
    
    def generate_wave(self, wavelength, amplitude=1.0):
        """Generate wave with topology modulation"""
        k = 2 * np.pi / wavelength
        # Wave is modulated by boundary topology
        return amplitude * np.sin(k * self.x) * self.boundary_modulation
    
    def generate_single_frequency(self, frequency):
        """
        Generate SINGLE frequency and let topology do the work
        
        Key test: Does topology generate harmonics?
        """
        wavelength = self.chamber_size / frequency
        return self.generate_wave(wavelength)
    
    def generate_white_noise(self, amplitude=1.0):
        """
        Generate white noise (all frequencies) and let topology select
        
        Key test: Does topology select specific scales?
        """
        # Random phase at each point, but modulated by topology
        noise = amplitude * np.random.randn(len(self.x))
        return noise * self.boundary_modulation
    
    def compute_interference(self, wavelengths):
        """Standard multi-wavelength interference"""
        total_field = np.zeros(len(self.x))
        for wl in wavelengths:
            if wl > 0:
                total_field += self.generate_wave(wl)
        return total_field
    
    def extract_ratios(self, field):
        """Extract peak position ratios from field"""
        peaks, _ = find_peaks(np.abs(field), prominence=0.5)
        
        if len(peaks) < 2:
            return []
        
        peak_positions = self.x[peaks]
        ratios = []
        sample_size = min(200, len(peak_positions))
        sampled_peaks = peak_positions[::max(1, len(peak_positions)//sample_size)]
        
        for i in range(len(sampled_peaks)):
            for j in range(i+1, len(sampled_peaks)):
                ratio = sampled_peaks[j] / sampled_peaks[i]
                if 1.01 < ratio < 3000:
                    ratios.append(ratio)
        return ratios
    
    def find_best_match(self, ratios, target):
        """Find best ratio match to target constant"""
        if not ratios:
            return None, float('inf')
        differences = [abs(r - target) for r in ratios]
        min_diff = min(differences)
        best_ratio = ratios[differences.index(min_diff)]
        return best_ratio, min_diff
    
    def analyze_frequency_content(self, field):
        """
        Analyze frequency spectrum of field
        
        Key test: Does single frequency input generate multiple frequencies?
        """
        # FFT to see frequency content
        fft_vals = fft(field)
        fft_freqs = fftfreq(len(field), d=(self.x[1] - self.x[0]))
        
        # Get positive frequencies only
        pos_mask = fft_freqs > 0
        freqs = fft_freqs[pos_mask]
        power = np.abs(fft_vals[pos_mask]) ** 2
        
        # Find peaks in frequency domain
        freq_peaks, _ = find_peaks(power, prominence=np.max(power) * 0.01)
        
        return freqs, power, freq_peaks

# Target constants
CONSTANTS = {
    'fine_structure': 137.035999084,
    'phi': 1.618033988749895,
    'pi': 3.141592653589793,
    'e': 2.718281828459045,
    'proton_electron_mass': 1836.15267343,
}

def test_configuration(field, chamber, name):
    """Test a field configuration"""
    ratios = chamber.extract_ratios(field)
    
    accuracies = []
    for target in CONSTANTS.values():
        match, error = chamber.find_best_match(ratios, target)
        if match is not None:
            acc = 100 * (1 - error / target)
            accuracies.append(acc)
        else:
            accuracies.append(0.0)
    
    avg_acc = np.mean(accuracies)
    above_99 = sum(1 for a in accuracies if a >= 99.0)
    
    print(f"  {name:40s}: {avg_acc:7.4f}% avg, {above_99}/5 >99%")
    
    return avg_acc, above_99, accuracies

# ============================================================================
# TEST 1: SINGLE FREQUENCY
# ============================================================================

def test_single_frequency():
    """
    Does a SINGLE frequency input generate the constants?
    
    Hypothesis: Topology generates harmonics from single input
    """
    print("\n" + "="*80)
    print("TEST 1: SINGLE FREQUENCY INPUT")
    print("="*80)
    print("Hypothesis: Topology generates effective wavelengths from ONE input")
    print()
    
    L = 3000.0
    
    results = []
    
    for topology in ['simple', 'fractal', 'golden']:
        print(f"\nTopology: {topology}")
        print("-" * 40)
        
        chamber = ResonanceChamber(L, topology=topology)
        
        # Test different base frequencies
        test_freqs = [1, 2, 3, 5, 10, 20]
        
        for freq in test_freqs:
            field = chamber.generate_single_frequency(freq)
            
            # Analyze frequency content
            freqs, power, peaks = chamber.analyze_frequency_content(field)
            n_harmonics = len(peaks)
            
            # Test constants
            avg_acc, above_99, accs = test_configuration(
                field, chamber, f"  freq={freq}, harmonics={n_harmonics}"
            )
            
            results.append({
                'topology': topology,
                'input_frequency': freq,
                'n_harmonics': n_harmonics,
                'avg_accuracy': avg_acc,
                'above_99': above_99
            })
    
    # Find best
    best = max(results, key=lambda x: x['avg_accuracy'])
    
    print(f"\n{'='*80}")
    print("SINGLE FREQUENCY RESULTS:")
    print(f"{'='*80}")
    print(f"Best: topology={best['topology']}, freq={best['input_frequency']}")
    print(f"  Generated {best['n_harmonics']} harmonics")
    print(f"  Accuracy: {best['avg_accuracy']:.4f}%")
    print(f"  Constants >99%: {best['above_99']}/5")
    
    if best['avg_accuracy'] > 95:
        print("\n✓ HYPOTHESIS SUPPORTED: Single frequency + topology works!")
    else:
        print("\n✗ HYPOTHESIS NOT SUPPORTED: Need multiple frequencies")
    
    return results

# ============================================================================
# TEST 2: WHITE NOISE
# ============================================================================

def test_white_noise():
    """
    Does white noise + topology select specific scales?
    
    Hypothesis: Topology selects wavelengths from noise
    """
    print("\n" + "="*80)
    print("TEST 2: WHITE NOISE INPUT")
    print("="*80)
    print("Hypothesis: Topology selects specific scales from broadband noise")
    print()
    
    L = 3000.0
    
    results = []
    
    for topology in ['simple', 'fractal', 'golden', 'random']:
        print(f"\nTopology: {topology}")
        print("-" * 40)
        
        # Average over 5 trials (noise is random)
        trial_accs = []
        
        for trial in range(5):
            chamber = ResonanceChamber(L, topology=topology)
            field = chamber.generate_white_noise(amplitude=1.0)
            
            avg_acc, above_99, accs = test_configuration(
                field, chamber, f"  trial {trial+1}"
            )
            
            trial_accs.append(avg_acc)
        
        mean_acc = np.mean(trial_accs)
        std_acc = np.std(trial_accs)
        
        print(f"  Mean: {mean_acc:.4f}% ± {std_acc:.4f}%")
        
        results.append({
            'topology': topology,
            'mean_accuracy': mean_acc,
            'std_accuracy': std_acc
        })
    
    # Compare structured vs random topology
    structured = [r for r in results if r['topology'] in ['fractal', 'golden']]
    random_topo = [r for r in results if r['topology'] == 'random']
    
    structured_avg = np.mean([r['mean_accuracy'] for r in structured])
    random_avg = random_topo[0]['mean_accuracy'] if random_topo else 0
    
    print(f"\n{'='*80}")
    print("WHITE NOISE RESULTS:")
    print(f"{'='*80}")
    print(f"Structured topology (fractal/golden): {structured_avg:.4f}%")
    print(f"Random topology: {random_avg:.4f}%")
    
    if structured_avg > random_avg + 5:
        print("\n✓ HYPOTHESIS SUPPORTED: Structured topology selects scales!")
    else:
        print("\n✗ HYPOTHESIS NOT SUPPORTED: Topology doesn't select strongly")
    
    return results

# ============================================================================
# TEST 3: WAVELENGTH ORDER
# ============================================================================

def test_wavelength_order():
    """
    Does wavelength ORDER matter, or just the SET?
    
    Hypothesis: Only the scales matter, not the order
    """
    print("\n" + "="*80)
    print("TEST 3: WAVELENGTH ORDER INDEPENDENCE")
    print("="*80)
    print("Hypothesis: Order doesn't matter, only scales present")
    print()
    
    L = 3000.0
    s = 0.338
    
    # Base wavelengths
    base_wavelengths = list(range(1, 31))
    
    results = []
    
    for topology in ['simple', 'fractal']:
        print(f"\nTopology: {topology}")
        print("-" * 40)
        
        chamber = ResonanceChamber(L, topology=topology)
        
        # Test different orderings
        test_cases = [
            ("Ascending (1,2,3,...)", sorted(base_wavelengths)),
            ("Descending (30,29,28,...)", sorted(base_wavelengths, reverse=True)),
            ("Random order", np.random.permutation(base_wavelengths).tolist()),
            ("Alternating (1,30,2,29,...)", [base_wavelengths[i//2] if i%2==0 
                                             else base_wavelengths[-(i//2+1)] 
                                             for i in range(len(base_wavelengths))])
        ]
        
        for name, wavelengths in test_cases:
            scaled_wl = [w * s for w in wavelengths]
            field = chamber.compute_interference(scaled_wl)
            
            avg_acc, above_99, accs = test_configuration(
                field, chamber, f"  {name}"
            )
            
            results.append({
                'topology': topology,
                'order': name,
                'accuracy': avg_acc
            })
    
    # Check variance
    accs_by_topology = {}
    for r in results:
        topo = r['topology']
        if topo not in accs_by_topology:
            accs_by_topology[topo] = []
        accs_by_topology[topo].append(r['accuracy'])
    
    print(f"\n{'='*80}")
    print("ORDER INDEPENDENCE RESULTS:")
    print(f"{'='*80}")
    
    for topo, accs in accs_by_topology.items():
        variance = np.var(accs)
        print(f"{topo}: variance = {variance:.6f}%²")
        
        if variance < 0.01:
            print(f"  ✓ Order-independent (variance < 0.01)")
        else:
            print(f"  ✗ Order matters (variance > 0.01)")
    
    return results

# ============================================================================
# TEST 4: COMPARE TO BASELINE
# ============================================================================

def test_baseline_comparison():
    """
    Compare all methods to original multi-wavelength approach
    """
    print("\n" + "="*80)
    print("TEST 4: BASELINE COMPARISON")
    print("="*80)
    print("Comparing: Original vs Single-freq vs White-noise")
    print()
    
    L = 3000.0
    s = 0.338
    
    wavelengths = [w * s for w in range(1, 31)]
    
    results = {}
    
    for topology in ['simple', 'fractal', 'golden']:
        print(f"\nTopology: {topology}")
        print("-" * 40)
        
        chamber = ResonanceChamber(L, topology=topology)
        
        # Original: multiple wavelengths
        field_multi = chamber.compute_interference(wavelengths)
        acc_multi, _, _ = test_configuration(field_multi, chamber, "Multi-wavelength")
        
        # Single frequency (try a few, take best)
        acc_single_best = 0
        for freq in [3, 5, 10]:
            field_single = chamber.generate_single_frequency(freq)
            acc, _, _ = test_configuration(field_single, chamber, f"Single freq={freq}")
            acc_single_best = max(acc_single_best, acc)
        
        # White noise (average 3 trials)
        acc_noise_trials = []
        for trial in range(3):
            field_noise = chamber.generate_white_noise()
            acc, _, _ = test_configuration(field_noise, chamber, f"White noise trial {trial+1}")
            acc_noise_trials.append(acc)
        acc_noise = np.mean(acc_noise_trials)
        
        results[topology] = {
            'multi': acc_multi,
            'single': acc_single_best,
            'noise': acc_noise
        }
        
        print(f"\n  Summary for {topology}:")
        print(f"    Multi-wavelength: {acc_multi:.4f}%")
        print(f"    Single-frequency: {acc_single_best:.4f}%")
        print(f"    White noise:      {acc_noise:.4f}%")
    
    print(f"\n{'='*80}")
    print("OVERALL COMPARISON:")
    print(f"{'='*80}")
    
    for method in ['multi', 'single', 'noise']:
        avg = np.mean([r[method] for r in results.values()])
        print(f"{method:20s}: {avg:.4f}% average across topologies")
    
    # Best topology
    best_topo = max(results.keys(), key=lambda t: results[t]['multi'])
    print(f"\nBest topology: {best_topo}")
    print(f"  Multi: {results[best_topo]['multi']:.4f}%")
    
    return results

# ============================================================================
# MAIN TEST SUITE
# ============================================================================

def run_all_tests():
    """Run complete test suite"""
    
    print("="*80)
    print("TOPOLOGY AS WAVE GENERATOR - COMPLETE TEST SUITE")
    print("="*80)
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    print()
    print("Testing whether ONE wave + topology generates wavelengths...")
    print()
    
    all_results = {}
    
    # Test 1: Single frequency
    print("\n" + "█" * 80)
    all_results['single_frequency'] = test_single_frequency()
    
    # Test 2: White noise
    print("\n" + "█" * 80)
    all_results['white_noise'] = test_white_noise()
    
    # Test 3: Order independence
    print("\n" + "█" * 80)
    all_results['order_independence'] = test_wavelength_order()
    
    # Test 4: Baseline comparison
    print("\n" + "█" * 80)
    all_results['baseline_comparison'] = test_baseline_comparison()
    
    # Save results
    output_file = 'topology_wave_tests.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print("ALL TESTS COMPLETE")
    print(f"{'='*80}")
    print(f"End: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Results saved to: {output_file}")
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY - KEY FINDINGS:")
    print("="*80)
    
    # Check if single frequency works
    single_best = max(all_results['single_frequency'], 
                     key=lambda x: x['avg_accuracy'])
    print(f"\n1. Single Frequency:")
    print(f"   Best: {single_best['avg_accuracy']:.2f}% with {single_best['topology']} topology")
    if single_best['avg_accuracy'] > 95:
        print("   ✓ Can generate constants from ONE frequency!")
    else:
        print("   ✗ Needs multiple frequencies")
    
    # Check if topology matters
    noise_structured = [r for r in all_results['white_noise'] 
                       if r['topology'] in ['fractal', 'golden']]
    noise_random = [r for r in all_results['white_noise'] 
                   if r['topology'] == 'random']
    
    if noise_structured and noise_random:
        structured_avg = np.mean([r['mean_accuracy'] for r in noise_structured])
        random_avg = noise_random[0]['mean_accuracy']
        
        print(f"\n2. Topology Matters:")
        print(f"   Structured: {structured_avg:.2f}%")
        print(f"   Random: {random_avg:.2f}%")
        if structured_avg > random_avg + 5:
            print("   ✓ Topology significantly affects results!")
        else:
            print("   ✗ Topology doesn't matter much")
    
    print("\n" + "="*80)
    print("Ready for next steps!")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()
