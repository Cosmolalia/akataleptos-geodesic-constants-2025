#!/usr/bin/env python3
"""
DIMENSIONAL REDUCTION SIMULATION
================================
The missing piece: 3D → 1D transition

Nuclear pasta does this:
  Gnocchi (3D blobs) → Lasagna (2D sheets) → Spaghetti (1D strings)

We model:
  3D chaotic filaments → compression → dimensional collapse → 1D wave structure

PREDICTION:
  - Steps 0-100: Geometric constants emerge (φ, π, e) from 3D packing
  - Steps 100-200: Dimensional reduction (3D → 1D)  
  - Steps 200-300: Wave constants emerge (α, 1836) from 1D interference

This is the Akatalêptos mechanism: compression FORCES dimensional reduction,
which FORCES wave patterns, which PRODUCES the constants.

∂W = W
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Fixed seed for reproducibility
np.random.seed(42)

# Constants we're hunting
CONSTANTS = {
    'phi': 1.618033988749895,
    'fine_structure_inv': 137.035999084,
    'proton_electron': 1836.15267343,
    'pi': 3.141592653589793,
    'e': 2.718281828459045,
    'sqrt_2': 1.4142135623730951,
}

@dataclass
class DimensionalFilament:
    """Filament that can exist in 3D, 2D, or 1D"""
    points: np.ndarray
    velocity: np.ndarray
    frequencies: np.ndarray
    phases: np.ndarray
    amplitude: float = 1.0
    
    @property
    def effective_dimension(self) -> float:
        """Estimate effective dimensionality from point spread"""
        if len(self.points) < 3:
            return 1.0
        
        # Compute variance in each dimension
        variances = np.var(self.points, axis=0)
        # Participation ratio: how many dimensions are "active"
        total_var = np.sum(variances) + 1e-10
        participation = np.sum(variances)**2 / (np.sum(variances**2) + 1e-10)
        return participation
    
    def field_at_point_1d(self, x_position: float, t: float) -> float:
        """
        Wave contribution when filament is collapsed to 1D.
        This is where clean interference happens.
        """
        # Only x-coordinates matter in 1D
        x_coords = self.points[:, 0]
        distances = np.abs(x_coords - x_position)
        distances = np.maximum(distances, 0.01)
        
        # Wave from each point
        wave_amps = self.amplitude / (distances + 0.1)
        contributions = wave_amps * np.sin(
            2 * np.pi * self.frequencies * t + self.phases - distances
        )
        return np.sum(contributions)


class DimensionalReductionUniverse:
    """
    Universe that compresses 3D → 2D → 1D
    
    Models the nuclear pasta transition:
    - Early: 3D packing (geometric constants)
    - Middle: Dimensional collapse
    - Late: 1D resonance (wave constants)
    """
    
    def __init__(self, n_filaments=25, points_per=35, initial_radius=10.0):
        self.initial_radius = initial_radius
        self.radius = initial_radius
        self.n_filaments = n_filaments
        self.points_per = points_per
        
        # Dimensional reduction parameter (1.0 = 3D, 0.0 = 1D)
        self.dimension_factor = 1.0
        
        # Create filaments
        self.filaments = self._create_filaments()
        
        # 1D resonance length (emerges from compression)
        self.resonance_length = initial_radius * 2
        
        # History
        self.history = {
            'step': [],
            'compression': [],
            'dimension': [],
            'phi': [],
            'alpha': [],
            'proton_electron': [],
            'pi': [],
            'e': [],
            'sqrt_2': [],
            'n_peaks_1d': [],
            'phase': [],  # 'geometric', 'transition', 'wave'
        }
        
        self.time = 0
        self.wave_time = 0.0
        
    def _create_filaments(self) -> List[DimensionalFilament]:
        """Create 3D chaotic filaments with wave properties"""
        filaments = []
        
        for _ in range(self.n_filaments):
            points = np.zeros((self.points_per, 3))
            
            # Random start
            theta = np.random.uniform(0, 2*np.pi)
            phi_angle = np.random.uniform(0, np.pi)
            r = np.random.uniform(0, self.radius * 0.8)
            points[0] = [
                r * np.sin(phi_angle) * np.cos(theta),
                r * np.sin(phi_angle) * np.sin(theta),
                r * np.cos(phi_angle)
            ]
            
            # Random walk
            direction = np.random.randn(3)
            direction /= np.linalg.norm(direction)
            step_size = self.radius * 0.1
            
            for j in range(1, self.points_per):
                perturbation = np.random.randn(3) * 0.3
                direction = direction + perturbation
                direction /= np.linalg.norm(direction)
                points[j] = points[j-1] + direction * step_size
                
                dist = np.linalg.norm(points[j])
                if dist > self.radius * 0.9:
                    points[j] *= (self.radius * 0.9) / dist
                    direction = -points[j] / dist + np.random.randn(3) * 0.2
                    direction /= np.linalg.norm(direction)
            
            velocity = np.random.randn(self.points_per, 3) * 0.01
            frequencies = np.random.uniform(1, 30, self.points_per)
            phases = np.random.uniform(0, 2*np.pi, self.points_per)
            
            filaments.append(DimensionalFilament(
                points=points,
                velocity=velocity,
                frequencies=frequencies,
                phases=phases
            ))
        
        return filaments
    
    def apply_dimensional_reduction(self, target_dim: float):
        """
        Reduce dimensionality by collapsing perpendicular axes.
        
        target_dim: 1.0 = full 3D, 0.0 = pure 1D (x-axis only)
        
        This models nuclear pasta: pressure forces matter into filaments
        """
        for filament in self.filaments:
            for i in range(len(filament.points)):
                x, y, z = filament.points[i]
                
                # Collapse y and z toward zero
                y *= target_dim
                z *= target_dim
                
                filament.points[i] = np.array([x, y, z])
                
                # Also collapse velocities
                vx, vy, vz = filament.velocity[i]
                vy *= target_dim
                vz *= target_dim
                filament.velocity[i] = np.array([vx, vy, vz])
        
        self.dimension_factor = target_dim
    
    def compression_step(self, compression_rate=0.995):
        """Standard radial compression"""
        self.radius *= compression_rate
        
        for filament in self.filaments:
            for i, point in enumerate(filament.points):
                dist = np.linalg.norm(point)
                
                if dist > self.radius * 0.95:
                    direction = -point / (dist + 1e-10)
                    push = (dist - self.radius * 0.9) * 0.1
                    filament.velocity[i] += direction * push
                
                filament.points[i] += filament.velocity[i]
                filament.velocity[i] *= 0.98
                
                new_dist = np.linalg.norm(filament.points[i])
                if new_dist > self.radius:
                    filament.points[i] *= self.radius / new_dist
        
        # Update resonance length based on x-spread
        all_x = np.concatenate([f.points[:, 0] for f in self.filaments])
        self.resonance_length = np.max(all_x) - np.min(all_x) + 0.1
        
        self.time += 1
        self.wave_time += 0.1
    
    def compute_1d_interference(self, n_samples=200) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute wave interference along 1D axis.
        This is where α and 1836 should emerge.
        """
        # Sample along x-axis
        all_x = np.concatenate([f.points[:, 0] for f in self.filaments])
        x_min, x_max = np.min(all_x), np.max(all_x)
        
        if x_max - x_min < 0.1:
            x_min, x_max = -1, 1
        
        x_samples = np.linspace(x_min, x_max, n_samples)
        field = np.zeros(n_samples)
        
        for xi, x in enumerate(x_samples):
            for filament in self.filaments:
                field[xi] += filament.field_at_point_1d(x, self.wave_time)
        
        return x_samples, field
    
    def compute_3d_ratios(self) -> Dict[str, float]:
        """
        Compute geometric ratios from 3D structure.
        This finds φ, π, e from packing.
        """
        all_points = np.vstack([f.points for f in self.filaments])
        
        # Radial distribution
        radii = np.linalg.norm(all_points, axis=1)
        
        # Find peaks in radial histogram
        hist, bin_edges = np.histogram(radii, bins=50, range=(0, self.radius))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        peaks, _ = find_peaks(hist.astype(float), prominence=1)
        
        if len(peaks) < 2:
            return {name: 0.0 for name in CONSTANTS.keys()}
        
        peak_radii = bin_centers[peaks]
        
        # Compute ratios
        ratios = []
        for i in range(len(peak_radii)):
            for j in range(i+1, len(peak_radii)):
                if peak_radii[i] > 0.001:
                    ratios.append(peak_radii[j] / peak_radii[i])
        
        # Match to constants
        results = {}
        for name, target in CONSTANTS.items():
            best = 0.0
            for r in ratios:
                for test_r in [r, 1/r if r > 0 else 0]:
                    if test_r > 0:
                        acc = 100 * (1 - abs(test_r - target) / target)
                        best = max(best, acc)
            results[name] = max(0, best)
        
        return results
    
    def compute_1d_ratios(self) -> Tuple[Dict[str, float], int]:
        """
        Compute wave ratios from 1D interference.
        This finds α and 1836 from standing waves.
        """
        x_samples, field = self.compute_1d_interference()
        
        # Find peaks
        peaks, properties = find_peaks(np.abs(field), prominence=0.05, distance=3)
        
        if len(peaks) < 3:
            return {name: 0.0 for name in CONSTANTS.keys()}, len(peaks)
        
        peak_positions = x_samples[peaks]
        peak_amps = np.abs(field[peaks])
        
        # Compute ratios weighted by amplitude
        ratios = []
        for i in range(len(peak_positions)):
            for j in range(i+1, len(peak_positions)):
                if abs(peak_positions[i]) > 0.001:
                    r = abs(peak_positions[j] / peak_positions[i])
                    weight = peak_amps[i] * peak_amps[j]
                    ratios.append((r, weight))
        
        # Also compute from peak SPACINGS (important for standing waves)
        spacings = np.diff(np.sort(peak_positions))
        for i in range(len(spacings)):
            for j in range(i+1, len(spacings)):
                if spacings[i] > 0.001:
                    r = spacings[j] / spacings[i]
                    ratios.append((r, 1.0))
        
        # Match to constants
        results = {}
        for name, target in CONSTANTS.items():
            best = 0.0
            for r, w in ratios:
                for test_r in [r, 1/r if r > 0 else 0, r*10, r*100, r/10, r/100]:
                    if test_r > 0:
                        acc = 100 * (1 - abs(test_r - target) / target)
                        best = max(best, acc)
            results[name] = max(0, best)
        
        return results, len(peaks)
    
    def determine_phase(self, step: int, total_steps: int) -> str:
        """Which phase are we in?"""
        progress = step / total_steps
        if progress < 0.33:
            return 'geometric'
        elif progress < 0.67:
            return 'transition'
        else:
            return 'wave'
    
    def step(self, step_num: int, total_steps: int, 
             compression_rate=0.993, dim_reduction_start=0.33, dim_reduction_end=0.67):
        """
        One simulation step with phased dimensional reduction.
        """
        progress = step_num / total_steps
        
        # Phase 1: Pure 3D compression (geometric constants)
        if progress < dim_reduction_start:
            self.compression_step(compression_rate)
            # Keep full 3D
            target_dim = 1.0
            
        # Phase 2: Dimensional reduction (3D → 1D)
        elif progress < dim_reduction_end:
            self.compression_step(compression_rate)
            # Linearly reduce dimensions
            reduction_progress = (progress - dim_reduction_start) / (dim_reduction_end - dim_reduction_start)
            target_dim = 1.0 - (reduction_progress * 0.95)  # Go to 0.05, not 0
            
        # Phase 3: 1D wave interference (wave constants)
        else:
            self.compression_step(compression_rate * 1.002)  # Slow compression
            target_dim = 0.05  # Nearly 1D
        
        self.apply_dimensional_reduction(target_dim)
        
        # Compute metrics based on phase
        phase = self.determine_phase(step_num, total_steps)
        
        if phase == 'geometric':
            # Use 3D ratios
            ratios = self.compute_3d_ratios()
            n_peaks = 0
        elif phase == 'transition':
            # Blend both
            ratios_3d = self.compute_3d_ratios()
            ratios_1d, n_peaks = self.compute_1d_ratios()
            ratios = {}
            blend = (progress - dim_reduction_start) / (dim_reduction_end - dim_reduction_start)
            for name in CONSTANTS.keys():
                ratios[name] = ratios_3d[name] * (1 - blend) + ratios_1d[name] * blend
        else:
            # Use 1D ratios
            ratios, n_peaks = self.compute_1d_ratios()
        
        # Record
        compression = 1 - self.radius / self.initial_radius
        
        self.history['step'].append(step_num)
        self.history['compression'].append(compression)
        self.history['dimension'].append(self.dimension_factor)
        self.history['phi'].append(ratios.get('phi', 0))
        self.history['alpha'].append(ratios.get('fine_structure_inv', 0))
        self.history['proton_electron'].append(ratios.get('proton_electron', 0))
        self.history['pi'].append(ratios.get('pi', 0))
        self.history['e'].append(ratios.get('e', 0))
        self.history['sqrt_2'].append(ratios.get('sqrt_2', 0))
        self.history['n_peaks_1d'].append(n_peaks)
        self.history['phase'].append(phase)
        
        return compression, ratios, phase
    
    def run(self, n_steps=300, verbose=True):
        """Run the full simulation with dimensional reduction"""
        
        if verbose:
            print("╔" + "═"*70 + "╗")
            print("║" + " DIMENSIONAL REDUCTION: 3D → 1D → CONSTANTS ".center(70) + "║")
            print("╠" + "═"*70 + "╣")
            print("║" + " Phase 1 (0-33%):  3D compression → φ, π, e ".center(70) + "║")
            print("║" + " Phase 2 (33-67%): Dimensional reduction (pasta transition) ".center(70) + "║")
            print("║" + " Phase 3 (67-100%): 1D interference → α, 1836 ".center(70) + "║")
            print("╚" + "═"*70 + "╝")
            print()
        
        for step in range(n_steps):
            compression, ratios, phase = self.step(step, n_steps)
            
            if verbose and step % 25 == 0:
                phi = ratios.get('phi', 0)
                alpha = ratios.get('fine_structure_inv', 0)
                pe = ratios.get('proton_electron', 0)
                dim = self.dimension_factor
                
                phi_m = "✓" if phi > 95 else ("~" if phi > 80 else " ")
                alpha_m = "✓" if alpha > 95 else ("~" if alpha > 80 else " ")
                pe_m = "✓" if pe > 95 else ("~" if pe > 80 else " ")
                
                print(f"Step {step:3d} [{phase:10s}]: dim={dim:.2f}, "
                      f"φ={phi:5.1f}%{phi_m} α={alpha:5.1f}%{alpha_m} "
                      f"mp/me={pe:5.1f}%{pe_m}")
        
        if verbose:
            print("-" * 70)
            print("Simulation complete.")
        
        return self
    
    def analyze(self):
        """Analyze results by phase"""
        
        print("\n" + "="*70)
        print(" PHASE-BY-PHASE ANALYSIS ".center(70, "="))
        print("="*70)
        
        phases = ['geometric', 'transition', 'wave']
        
        for phase in phases:
            indices = [i for i, p in enumerate(self.history['phase']) if p == phase]
            if not indices:
                continue
            
            print(f"\n--- {phase.upper()} PHASE ---")
            
            for const in ['phi', 'alpha', 'pi', 'e', 'proton_electron']:
                if const == 'alpha':
                    key = 'alpha'
                else:
                    key = const
                
                values = [self.history[key][i] for i in indices]
                peak = max(values)
                final = values[-1]
                
                status = "✓✓✓" if peak > 99 else ("✓✓" if peak > 95 else ("✓" if peak > 90 else ""))
                print(f"  {const:<20}: peak={peak:6.2f}%, final={final:6.2f}% {status}")
        
        # Key question
        print("\n" + "="*70)
        print(" THE KEY QUESTION ".center(70, "="))
        print("="*70)
        
        # Did wave constants emerge in wave phase?
        wave_indices = [i for i, p in enumerate(self.history['phase']) if p == 'wave']
        
        if wave_indices:
            alpha_wave = max(self.history['alpha'][i] for i in wave_indices)
            pe_wave = max(self.history['proton_electron'][i] for i in wave_indices)
            
            alpha_geo = max(self.history['alpha'][:len(self.history['alpha'])//3])
            pe_geo = max(self.history['proton_electron'][:len(self.history['proton_electron'])//3])
            
            print(f"\nα (fine structure inverse):")
            print(f"  Geometric phase: {alpha_geo:.1f}%")
            print(f"  Wave phase:      {alpha_wave:.1f}%")
            print(f"  Improvement:     {alpha_wave - alpha_geo:+.1f}%")
            
            if alpha_wave > alpha_geo + 20:
                print("  → DIMENSIONAL REDUCTION HELPED α EMERGE!")
            
            print(f"\nmp/me (proton-electron ratio):")
            print(f"  Geometric phase: {pe_geo:.1f}%")
            print(f"  Wave phase:      {pe_wave:.1f}%")
            print(f"  Improvement:     {pe_wave - pe_geo:+.1f}%")
            
            if pe_wave > pe_geo + 10:
                print("  → DIMENSIONAL REDUCTION HELPED 1836 EMERGE!")
        
        return {
            'phi_peak': max(self.history['phi']),
            'alpha_peak': max(self.history['alpha']),
            'pe_peak': max(self.history['proton_electron']),
        }
    
    def visualize(self, save_path=None):
        """Comprehensive visualization"""
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        steps = self.history['step']
        
        # Color by phase
        colors = {'geometric': 'blue', 'transition': 'orange', 'wave': 'green'}
        phase_colors = [colors[p] for p in self.history['phase']]
        
        # 1. Dimension reduction
        ax = axes[0, 0]
        ax.plot(steps, self.history['dimension'], 'k-', linewidth=2)
        ax.fill_between(steps, 0, self.history['dimension'], alpha=0.3)
        ax.set_xlabel('Step')
        ax.set_ylabel('Effective Dimension')
        ax.set_title('Dimensional Reduction (3D → 1D)')
        ax.set_ylim(0, 1.1)
        
        # Phase regions
        n = len(steps)
        ax.axvspan(0, n*0.33, alpha=0.1, color='blue', label='Geometric')
        ax.axvspan(n*0.33, n*0.67, alpha=0.1, color='orange', label='Transition')
        ax.axvspan(n*0.67, n, alpha=0.1, color='green', label='Wave')
        ax.legend(loc='upper right')
        
        # 2. Geometric constants (φ, π, e)
        ax = axes[0, 1]
        ax.plot(steps, self.history['phi'], 'gold', linewidth=2, label='φ')
        ax.plot(steps, self.history['pi'], 'purple', linewidth=1.5, label='π')
        ax.plot(steps, self.history['e'], 'cyan', linewidth=1.5, label='e')
        ax.axhline(95, color='green', linestyle='--', alpha=0.5)
        ax.set_xlabel('Step')
        ax.set_ylabel('Accuracy %')
        ax.set_title('Geometric Constants')
        ax.set_ylim(0, 105)
        ax.legend()
        
        # 3. Wave constants (α, 1836)
        ax = axes[0, 2]
        ax.plot(steps, self.history['alpha'], 'red', linewidth=2, label='1/α (137)')
        ax.plot(steps, self.history['proton_electron'], 'darkred', linewidth=2, label='mp/me (1836)')
        ax.axhline(95, color='green', linestyle='--', alpha=0.5)
        ax.axvspan(0, n*0.33, alpha=0.1, color='blue')
        ax.axvspan(n*0.33, n*0.67, alpha=0.1, color='orange')
        ax.axvspan(n*0.67, n, alpha=0.1, color='green')
        ax.set_xlabel('Step')
        ax.set_ylabel('Accuracy %')
        ax.set_title('Wave Constants (should improve in green zone)')
        ax.set_ylim(0, 105)
        ax.legend()
        
        # 4. Number of 1D peaks
        ax = axes[1, 0]
        ax.plot(steps, self.history['n_peaks_1d'], 'purple', linewidth=1.5)
        ax.set_xlabel('Step')
        ax.set_ylabel('Number of Peaks')
        ax.set_title('1D Interference Peaks (standing wave modes)')
        
        # 5. Compression
        ax = axes[1, 1]
        ax.plot(steps, self.history['compression'], 'b-', linewidth=2)
        ax.set_xlabel('Step')
        ax.set_ylabel('Compression')
        ax.set_title('Radial Compression')
        
        # 6. Final comparison
        ax = axes[1, 2]
        constants = ['phi', 'pi', 'e', 'sqrt_2', 'alpha', 'proton_electron']
        labels = ['φ', 'π', 'e', '√2', '1/α', 'mp/me']
        
        # Get peak values
        peaks = [max(self.history[c]) for c in constants]
        
        # Color by type
        bar_colors = ['gold', 'gold', 'gold', 'gold', 'red', 'darkred']
        
        ax.barh(labels, peaks, color=bar_colors)
        ax.axvline(95, color='green', linestyle='--', alpha=0.7, label='95% threshold')
        ax.axvline(90, color='orange', linestyle='--', alpha=0.5)
        ax.set_xlabel('Peak Accuracy %')
        ax.set_title('All Constants - Peak Values')
        ax.set_xlim(0, 105)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"\nVisualization saved to {save_path}")
        
        return fig


def main():
    print()
    print("╔" + "═"*70 + "╗")
    print("║" + " THE NUCLEAR PASTA HYPOTHESIS ".center(70) + "║")
    print("║" + "═"*70 + "║")
    print("║" + " Testing: Does 3D → 1D transition produce wave constants? ".center(70) + "║")
    print("║" + " ".center(70) + "║")
    print("║" + " If YES: Neutron stars COMPUTE their way to the constants ".center(70) + "║")
    print("║" + " The pasta phases aren't incidental — they're NECESSARY ".center(70) + "║")
    print("╚" + "═"*70 + "╝")
    print()
    
    # Create and run
    universe = DimensionalReductionUniverse(
        n_filaments=30,
        points_per=40,
        initial_radius=10.0
    )
    
    universe.run(n_steps=300)
    
    # Analyze
    results = universe.analyze()
    
    # Visualize
    universe.visualize('/home/claude/dimensional_reduction_results.png')
    
    print("\n" + "="*70)
    print(" SIMULATION COMPLETE ".center(70, "="))
    print("="*70)
    
    return universe, results


if __name__ == "__main__":
    universe, results = main()
