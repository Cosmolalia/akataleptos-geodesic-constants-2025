#!/usr/bin/env python3
"""
UNIFIED COMPRESSION + WAVE SIMULATION
=====================================
Combining:
- Opus's filament compression (geometry → φ, shell-seeking, topology events)
- Sonnet's wave mechanics (interference → α, 1836)

THE HYPOTHESIS:
Filaments under compression + oscillation should find ALL constants,
because now we have both:
- Geometric packing (gives φ)
- Wave dynamics (gives α, 1836)

This is the bridge between:
- Neutron star pasta → singularity topology
- Resonance chamber → standing wave constants
- The Akatalêptos as necessary geometry

∂W = W
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FUNDAMENTAL CONSTANTS WE'RE HUNTING
# ============================================================================

CONSTANTS = {
    'phi': 1.618033988749895,           # Golden ratio - should emerge from geometry
    'fine_structure_inv': 137.035999084, # 1/α - should emerge from wave dynamics
    'proton_electron': 1836.15267343,    # mp/me - hierarchical, waves + geometry
    'pi': 3.141592653589793,             # π - geometric
    'e': 2.718281828459045,              # Euler's number - growth/decay
    'sqrt_2': 1.4142135623730951,        # √2 - geometric
    'sqrt_3': 1.7320508075688772,        # √3 - geometric
    'love_freq_ratio': 432/528,          # Solfeggio ratio
}

# ============================================================================
# WAVE FILAMENT - A FILAMENT THAT OSCILLATES
# ============================================================================

@dataclass
class WaveFilament:
    """
    A 1D curve that carries oscillating waves.
    
    This is the bridge: geometric structure (positions) + wave dynamics (oscillation)
    """
    points: np.ndarray          # Nx3 positions
    velocity: np.ndarray        # Nx3 velocities
    frequencies: np.ndarray     # Oscillation frequencies at each point
    phases: np.ndarray          # Phase offsets
    amplitude: float = 1.0
    
    @property
    def length(self):
        diffs = np.diff(self.points, axis=0)
        return np.sum(np.linalg.norm(diffs, axis=1))
    
    def field_at_time(self, t: float) -> np.ndarray:
        """
        Compute the oscillating field at each point at time t.
        This is what creates interference.
        """
        oscillations = self.amplitude * np.sin(2 * np.pi * self.frequencies * t + self.phases)
        return oscillations
    
    def field_contribution_at_point(self, position: np.ndarray, t: float) -> float:
        """
        Compute the field this filament contributes to a given point in space.
        Waves propagate from filament, creating interference patterns.
        """
        # Distance from each filament point to the target position
        distances = np.linalg.norm(self.points - position, axis=1)
        
        # Avoid division by zero
        distances = np.maximum(distances, 0.01)
        
        # Wave amplitude decays with distance
        wave_amplitudes = self.amplitude / distances
        
        # Each point on filament contributes a wave
        contributions = wave_amplitudes * np.sin(
            2 * np.pi * self.frequencies * t + self.phases - distances
        )
        
        return np.sum(contributions)


# ============================================================================
# WAVE FILAMENT UNIVERSE - COMPRESSION + INTERFERENCE
# ============================================================================

class WaveFilamentUniverse:
    """
    A bounded space containing oscillating filaments under compression.
    
    We track:
    1. Geometric metrics (density, linking, shell concentration) - from Opus
    2. Wave metrics (interference, standing waves, frequency spectrum) - from Sonnet
    3. Constant emergence (which constants appear when)
    """
    
    def __init__(self, n_filaments=20, points_per_filament=40,
                 initial_radius=10.0, freq_range=(1, 30)):
        
        self.initial_radius = initial_radius
        self.radius = initial_radius
        self.time = 0
        self.wave_time = 0.0
        self.freq_range = freq_range
        
        # Create oscillating filaments
        self.filaments = self._create_wave_filaments(n_filaments, points_per_filament)
        
        # History tracking
        self.history = {
            'compression': [],
            'density': [],
            'linking': [],
            'shell_concentration': [],
            'phi_accuracy': [],
            'alpha_accuracy': [],
            'proton_electron_accuracy': [],
            'n_peaks': [],
            'topology_events': [],
        }
        
        # Detailed constant tracking
        self.constant_emergence = {name: [] for name in CONSTANTS.keys()}
        
    def _create_wave_filaments(self, n, points_per) -> List[WaveFilament]:
        """Create filaments with random oscillation properties"""
        filaments = []
        
        for _ in range(n):
            # Random walk positions (same as Opus)
            points = np.zeros((points_per, 3))
            
            # Start random
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0, self.radius * 0.8)
            points[0] = [
                r * np.sin(phi) * np.cos(theta),
                r * np.sin(phi) * np.sin(theta),
                r * np.cos(phi)
            ]
            
            # Build filament
            direction = np.random.randn(3)
            direction /= np.linalg.norm(direction)
            step_size = self.radius * 0.1
            
            for j in range(1, points_per):
                perturbation = np.random.randn(3) * 0.3
                direction = direction + perturbation
                direction /= np.linalg.norm(direction)
                points[j] = points[j-1] + direction * step_size
                
                dist = np.linalg.norm(points[j])
                if dist > self.radius * 0.9:
                    points[j] *= (self.radius * 0.9) / dist
                    direction = -points[j] / dist + np.random.randn(3) * 0.2
                    direction /= np.linalg.norm(direction)
            
            velocity = np.random.randn(points_per, 3) * 0.01
            
            # WAVE PROPERTIES - the key addition!
            # Each point has its own frequency (creates rich spectrum)
            frequencies = np.random.uniform(
                self.freq_range[0], 
                self.freq_range[1], 
                points_per
            )
            phases = np.random.uniform(0, 2*np.pi, points_per)
            
            filaments.append(WaveFilament(
                points=points,
                velocity=velocity,
                frequencies=frequencies,
                phases=phases
            ))
        
        return filaments
    
    def compute_density(self) -> float:
        """Geometric density (from Opus)"""
        total_length = sum(f.length for f in self.filaments)
        volume = (4/3) * np.pi * self.radius**3
        return total_length / volume
    
    def compute_shell_concentration(self) -> float:
        """How much are filaments concentrated on shell vs volume? (from Opus)"""
        all_points = np.vstack([f.points for f in self.filaments])
        radii = np.linalg.norm(all_points, axis=1)
        return np.std(radii) / (np.mean(radii) + 1e-10)
    
    def compute_linking_estimate(self) -> float:
        """Topological linking (simplified, from Opus)"""
        if len(self.filaments) < 2:
            return 0
        
        total_linking = 0
        n_samples = min(30, len(self.filaments) * (len(self.filaments)-1) // 2)
        
        for _ in range(n_samples):
            i, j = np.random.choice(len(self.filaments), 2, replace=False)
            f1, f2 = self.filaments[i], self.filaments[j]
            linking = self._gauss_linking_estimate(f1.points, f2.points)
            total_linking += abs(linking)
        
        return total_linking / n_samples if n_samples > 0 else 0
    
    def _gauss_linking_estimate(self, p1, p2) -> float:
        """Gauss linking integral approximation"""
        linking = 0
        step = max(1, len(p1) // 8)
        
        for i in range(0, len(p1)-1, step):
            for j in range(0, len(p2)-1, step):
                r = p2[j] - p1[i]
                r_norm = np.linalg.norm(r)
                if r_norm < 0.01:
                    continue
                
                dr1 = p1[min(i+1, len(p1)-1)] - p1[i]
                dr2 = p2[min(j+1, len(p2)-1)] - p2[j]
                
                cross = np.cross(dr1, dr2)
                linking += np.dot(r, cross) / (r_norm**3 + 0.01)
        
        return linking / (4 * np.pi)
    
    def compute_total_field(self, t: float, grid_size: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the total interference field on a radial grid.
        This is where wave mechanics happens!
        """
        # Sample along radial direction (most relevant for spherical compression)
        r_samples = np.linspace(0.01, self.radius, grid_size)
        
        # For each radial distance, sample a few angular points and average
        field_values = np.zeros(grid_size)
        
        for ri, r in enumerate(r_samples):
            # Sample a few points at this radius
            n_angular = 8
            field_sum = 0
            
            for _ in range(n_angular):
                # Random direction at radius r
                theta = np.random.uniform(0, 2*np.pi)
                phi = np.random.uniform(0, np.pi)
                position = np.array([
                    r * np.sin(phi) * np.cos(theta),
                    r * np.sin(phi) * np.sin(theta),
                    r * np.cos(phi)
                ])
                
                # Sum contributions from all filaments
                for filament in self.filaments:
                    field_sum += filament.field_contribution_at_point(position, t)
            
            field_values[ri] = field_sum / n_angular
        
        return r_samples, field_values
    
    def analyze_wave_ratios(self, t: float) -> Dict[str, float]:
        """
        Analyze the interference pattern for constant ratios.
        This is where we look for α, 1836, etc.
        """
        r_samples, field = self.compute_total_field(t)
        
        # Find peaks in interference pattern
        peaks, properties = find_peaks(np.abs(field), prominence=0.1, distance=2)
        
        if len(peaks) < 3:
            return {name: 0.0 for name in CONSTANTS.keys()}
        
        peak_positions = r_samples[peaks]
        peak_amplitudes = np.abs(field[peaks])
        
        # Compute all ratios between peaks
        ratios = []
        for i in range(len(peak_positions)):
            for j in range(i+1, len(peak_positions)):
                if peak_positions[i] > 0.001:
                    ratio = peak_positions[j] / peak_positions[i]
                    weight = peak_amplitudes[i] * peak_amplitudes[j]
                    ratios.append((ratio, weight))
        
        if not ratios:
            return {name: 0.0 for name in CONSTANTS.keys()}
        
        # Find best matches to constants
        results = {}
        for name, target in CONSTANTS.items():
            best_accuracy = 0.0
            
            for ratio, weight in ratios:
                # Check both ratio and its inverse
                for r in [ratio, 1/ratio if ratio > 0 else 0]:
                    if r > 0:
                        accuracy = 100 * (1 - abs(r - target) / target)
                        if accuracy > best_accuracy:
                            best_accuracy = accuracy
            
            results[name] = max(0, best_accuracy)
        
        return results
    
    def analyze_frequency_spectrum(self, t: float) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        FFT analysis of the field to see what frequencies are present.
        """
        r_samples, field = self.compute_total_field(t, grid_size=128)
        
        # FFT
        fft_vals = fft(field)
        fft_freqs = fftfreq(len(field), d=(r_samples[1] - r_samples[0]))
        
        # Positive frequencies
        pos_mask = fft_freqs > 0
        freqs = fft_freqs[pos_mask]
        power = np.abs(fft_vals[pos_mask])**2
        
        # Count significant peaks
        freq_peaks, _ = find_peaks(power, prominence=np.max(power) * 0.01)
        
        return freqs, power, len(freq_peaks)
    
    def compression_step(self, compression_rate=0.995):
        """Apply one step of compression (from Opus)"""
        self.radius *= compression_rate
        
        # Move filaments inward
        for filament in self.filaments:
            for i, point in enumerate(filament.points):
                dist = np.linalg.norm(point)
                
                if dist > self.radius * 0.95:
                    direction = -point / (dist + 1e-10)
                    push_strength = (dist - self.radius * 0.9) * 0.1
                    filament.velocity[i] += direction * push_strength
                
                filament.points[i] += filament.velocity[i]
                filament.velocity[i] *= 0.98
                
                new_dist = np.linalg.norm(filament.points[i])
                if new_dist > self.radius:
                    filament.points[i] *= self.radius / new_dist
                    normal = filament.points[i] / new_dist
                    filament.velocity[i] -= 2 * np.dot(filament.velocity[i], normal) * normal
        
        # Apply inter-filament forces
        self._apply_inter_filament_forces()
        
        self.time += 1
        self.wave_time += 0.1  # Advance wave time
    
    def _apply_inter_filament_forces(self):
        """Repulsion between filaments (from Opus)"""
        repulsion_range = self.radius * 0.15
        repulsion_strength = 0.002
        
        all_points = []
        point_to_filament = []
        
        for fi, f in enumerate(self.filaments):
            for pi in range(len(f.points)):
                all_points.append(f.points[pi])
                point_to_filament.append((fi, pi))
        
        all_points = np.array(all_points)
        n_samples = min(500, len(all_points))
        indices = np.random.choice(len(all_points), n_samples, replace=False)
        
        for idx in indices:
            fi, pi = point_to_filament[idx]
            point = all_points[idx]
            
            dists = np.linalg.norm(all_points - point, axis=1)
            nearby = np.where((dists < repulsion_range) & (dists > 0.01))[0]
            
            for other_idx in nearby:
                other_fi, other_pi = point_to_filament[other_idx]
                if other_fi == fi and abs(other_pi - pi) < 3:
                    continue
                
                other_point = all_points[other_idx]
                direction = point - other_point
                dist = np.linalg.norm(direction)
                
                if dist > 0:
                    force = direction / dist * repulsion_strength / (dist**2 + 0.01)
                    self.filaments[fi].velocity[pi] += force
    
    def record_metrics(self):
        """Record current state metrics"""
        compression = 1 - self.radius / self.initial_radius
        density = self.compute_density()
        linking = self.compute_linking_estimate()
        shell = self.compute_shell_concentration()
        
        # Wave analysis
        wave_ratios = self.analyze_wave_ratios(self.wave_time)
        _, _, n_peaks = self.analyze_frequency_spectrum(self.wave_time)
        
        self.history['compression'].append(compression)
        self.history['density'].append(density)
        self.history['linking'].append(linking)
        self.history['shell_concentration'].append(shell)
        self.history['phi_accuracy'].append(wave_ratios.get('phi', 0))
        self.history['alpha_accuracy'].append(wave_ratios.get('fine_structure_inv', 0))
        self.history['proton_electron_accuracy'].append(wave_ratios.get('proton_electron', 0))
        self.history['n_peaks'].append(n_peaks)
        
        # Track all constants
        for name in CONSTANTS.keys():
            self.constant_emergence[name].append(wave_ratios.get(name, 0))
        
        return compression, wave_ratios
    
    def detect_topology_event(self, threshold=0.3):
        """Detect if topology changed (from Opus)"""
        if len(self.history['linking']) < 2:
            return False
        
        delta = abs(self.history['linking'][-1] - self.history['linking'][-2])
        if delta > threshold:
            self.history['topology_events'].append({
                'step': self.time,
                'compression': self.history['compression'][-1],
                'linking_change': delta
            })
            return True
        return False
    
    def run_simulation(self, n_steps=300, compression_rate=0.993, verbose=True):
        """Run the full simulation"""
        
        if verbose:
            print("╔" + "═"*70 + "╗")
            print("║" + " UNIFIED WAVE + COMPRESSION SIMULATION ".center(70) + "║")
            print("║" + " Testing: Geometry → φ, Waves → α, 1836 ".center(70) + "║")
            print("╚" + "═"*70 + "╝")
            print()
            print(f"Filaments: {len(self.filaments)}")
            print(f"Initial radius: {self.initial_radius}")
            print(f"Looking for: φ={CONSTANTS['phi']:.4f}, 1/α={CONSTANTS['fine_structure_inv']:.2f}, mp/me={CONSTANTS['proton_electron']:.2f}")
            print("-" * 70)
        
        for step in range(n_steps):
            # Compress
            self.compression_step(compression_rate)
            
            # Record
            compression, wave_ratios = self.record_metrics()
            
            # Check topology
            topo_event = self.detect_topology_event()
            
            # Progress
            if verbose and step % 30 == 0:
                phi_acc = wave_ratios.get('phi', 0)
                alpha_acc = wave_ratios.get('fine_structure_inv', 0)
                pe_acc = wave_ratios.get('proton_electron', 0)
                
                phi_mark = "✓" if phi_acc > 95 else ("~" if phi_acc > 80 else " ")
                alpha_mark = "✓" if alpha_acc > 95 else ("~" if alpha_acc > 80 else " ")
                pe_mark = "✓" if pe_acc > 95 else ("~" if pe_acc > 80 else " ")
                
                print(f"Step {step:3d}: compression={compression:.1%}, "
                      f"φ={phi_acc:5.1f}%{phi_mark} α={alpha_acc:5.1f}%{alpha_mark} "
                      f"mp/me={pe_acc:5.1f}%{pe_mark}"
                      + (" [TOPOLOGY EVENT]" if topo_event else ""))
        
        if verbose:
            print("-" * 70)
            print(f"Final compression: {self.history['compression'][-1]:.1%}")
            print(f"Topology events: {len(self.history['topology_events'])}")
        
        return self
    
    def analyze_results(self):
        """Deep analysis of final state"""
        
        print("\n" + "="*70)
        print(" RESULTS ANALYSIS ".center(70, "="))
        print("="*70)
        
        # Final metrics
        print("\n--- GEOMETRIC METRICS (from compression) ---")
        print(f"Final compression: {self.history['compression'][-1]:.1%}")
        print(f"Final density: {self.history['density'][-1]:.4f}")
        print(f"Shell concentration: {self.history['shell_concentration'][-1]:.4f}")
        
        if self.history['shell_concentration'][-1] < 0.3:
            print("  → Shell-seeking confirmed! (Filaments on boundary)")
        
        print(f"Topology events: {len(self.history['topology_events'])}")
        for event in self.history['topology_events']:
            print(f"  • Step {event['step']}: compression={event['compression']:.1%}")
        
        # Constant emergence
        print("\n--- CONSTANT EMERGENCE ---")
        print(f"{'Constant':<25} {'Final Acc':>10} {'Peak Acc':>10} {'Emerged':>10}")
        print("-" * 55)
        
        emerged_constants = []
        for name, accuracies in self.constant_emergence.items():
            final_acc = accuracies[-1] if accuracies else 0
            peak_acc = max(accuracies) if accuracies else 0
            emerged = "✓✓✓" if peak_acc > 99 else ("✓✓" if peak_acc > 95 else ("✓" if peak_acc > 90 else ""))
            
            if peak_acc > 90:
                emerged_constants.append(name)
            
            print(f"{name:<25} {final_acc:>9.2f}% {peak_acc:>9.2f}% {emerged:>10}")
        
        # The key question
        print("\n--- THE KEY QUESTION ---")
        
        phi_emerged = 'phi' in emerged_constants
        alpha_emerged = 'fine_structure_inv' in emerged_constants
        pe_emerged = 'proton_electron' in emerged_constants
        
        print(f"φ emerged (geometry):     {'YES ✓' if phi_emerged else 'NO'}")
        print(f"α emerged (waves):        {'YES ✓' if alpha_emerged else 'NO'}")
        print(f"mp/me emerged (both):     {'YES ✓' if pe_emerged else 'NO'}")
        
        if phi_emerged and alpha_emerged:
            print("\n★ HYPOTHESIS CONFIRMED: Both geometry AND wave dynamics needed!")
            print("  Compression gives φ, waves give α, together give mp/me")
        elif phi_emerged and not alpha_emerged:
            print("\n~ PARTIAL: Geometry working, but waves need tuning")
            print("  Need more wave dynamics or longer simulation")
        else:
            print("\n✗ HYPOTHESIS NOT YET CONFIRMED")
            print("  Need to investigate why constants not emerging")
        
        return {
            'emerged_constants': emerged_constants,
            'phi': phi_emerged,
            'alpha': alpha_emerged,
            'proton_electron': pe_emerged,
            'shell_seeking': self.history['shell_concentration'][-1] < 0.3,
            'topology_events': len(self.history['topology_events'])
        }
    
    def visualize(self, save_path=None):
        """Create comprehensive visualization"""
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 1. Compression over time
        ax = axes[0, 0]
        ax.plot(self.history['compression'], 'b-', linewidth=1.5)
        for event in self.history['topology_events']:
            ax.axvline(event['step'], color='r', alpha=0.5, linestyle='--')
        ax.set_xlabel('Step')
        ax.set_ylabel('Compression')
        ax.set_title('Compression & Topology Events')
        
        # 2. Shell concentration
        ax = axes[0, 1]
        ax.plot(self.history['shell_concentration'], 'g-', linewidth=1.5)
        ax.axhline(0.3, color='orange', linestyle='--', label='Shell threshold')
        ax.set_xlabel('Step')
        ax.set_ylabel('Shell Concentration')
        ax.set_title('Shell-Seeking Behavior')
        ax.legend()
        
        # 3. φ accuracy over time
        ax = axes[0, 2]
        ax.plot(self.constant_emergence['phi'], 'gold', linewidth=1.5, label='φ')
        ax.axhline(95, color='green', linestyle='--', alpha=0.5)
        ax.set_xlabel('Step')
        ax.set_ylabel('Accuracy %')
        ax.set_title('Golden Ratio (φ) Emergence')
        ax.set_ylim(0, 105)
        
        # 4. α accuracy over time
        ax = axes[1, 0]
        ax.plot(self.constant_emergence['fine_structure_inv'], 'purple', linewidth=1.5, label='1/α')
        ax.axhline(95, color='green', linestyle='--', alpha=0.5)
        ax.set_xlabel('Step')
        ax.set_ylabel('Accuracy %')
        ax.set_title('Fine Structure (1/α) Emergence')
        ax.set_ylim(0, 105)
        
        # 5. mp/me accuracy over time
        ax = axes[1, 1]
        ax.plot(self.constant_emergence['proton_electron'], 'red', linewidth=1.5, label='mp/me')
        ax.axhline(95, color='green', linestyle='--', alpha=0.5)
        ax.set_xlabel('Step')
        ax.set_ylabel('Accuracy %')
        ax.set_title('Proton/Electron Mass Ratio Emergence')
        ax.set_ylim(0, 105)
        
        # 6. All constants comparison
        ax = axes[1, 2]
        final_accs = {name: accs[-1] if accs else 0 
                     for name, accs in self.constant_emergence.items()}
        names = list(final_accs.keys())
        values = list(final_accs.values())
        colors = ['gold' if v > 95 else ('green' if v > 90 else 'gray') for v in values]
        
        ax.barh(names, values, color=colors)
        ax.axvline(95, color='green', linestyle='--', alpha=0.5)
        ax.axvline(90, color='orange', linestyle='--', alpha=0.5)
        ax.set_xlabel('Final Accuracy %')
        ax.set_title('All Constants - Final State')
        ax.set_xlim(0, 105)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"\nVisualization saved to {save_path}")
        
        return fig


# ============================================================================
# MAIN
# ============================================================================

def main():
    print()
    print("╔" + "═"*70 + "╗")
    print("║" + " THE BRIDGE: COMPRESSION + WAVES → CONSTANTS ".center(70) + "║")
    print("║" + "═"*70 + "║")
    print("║" + " Testing whether unified mechanism produces ALL constants ".center(70) + "║")
    print("║" + " ".center(70) + "║")
    print("║" + " Hypothesis: ".center(70) + "║")
    print("║" + "   • φ emerges from geometric compression (packing) ".center(70) + "║")
    print("║" + "   • α emerges from wave interference (dynamics) ".center(70) + "║")
    print("║" + "   • mp/me emerges from both together (hierarchical) ".center(70) + "║")
    print("╚" + "═"*70 + "╝")
    print()
    
    # Create universe with oscillating filaments
    universe = WaveFilamentUniverse(
        n_filaments=25,
        points_per_filament=35,
        initial_radius=10.0,
        freq_range=(1, 30)  # Same range as Sonnet's chamber
    )
    
    # Run simulation
    universe.run_simulation(n_steps=300, compression_rate=0.992)
    
    # Analyze
    results = universe.analyze_results()
    
    # Visualize
    universe.visualize('/home/claude/wave_compression_results.png')
    
    # Save data
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'n_filaments': 25,
            'points_per_filament': 35,
            'initial_radius': 10.0,
            'freq_range': [1, 30],
            'n_steps': 300,
            'compression_rate': 0.992
        },
        'results': results,
        'history': {
            'compression': universe.history['compression'],
            'phi_accuracy': universe.history['phi_accuracy'],
            'alpha_accuracy': universe.history['alpha_accuracy'],
            'proton_electron_accuracy': universe.history['proton_electron_accuracy'],
            'topology_events': universe.history['topology_events']
        }
    }
    
    with open('/home/claude/wave_compression_data.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "="*70)
    print(" SIMULATION COMPLETE ".center(70, "="))
    print("="*70)
    
    return universe, results


if __name__ == "__main__":
    universe, results = main()
