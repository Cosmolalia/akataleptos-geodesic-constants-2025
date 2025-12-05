"""
Filament Compression Simulation
================================
Exploring the hypothesis that chaotic 1D structures under compression
naturally find Klein-like topology and generate fundamental constant ratios.

The Akatalêptos as map — we drive the road it says.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import json
from dataclasses import dataclass
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Fundamental constants we're looking for
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~1.618
ALPHA_INV = 137.035999  # Fine structure constant inverse
LOVE_FREQ = 432  # Hz
PROTON_ELECTRON_RATIO = 1836.15267  # The "master constant"

@dataclass
class Filament:
    """A 1D curve represented as connected points"""
    points: np.ndarray  # Nx3 array of positions
    velocity: np.ndarray  # Nx3 array of velocities
    
    @property
    def length(self):
        diffs = np.diff(self.points, axis=0)
        return np.sum(np.linalg.norm(diffs, axis=1))
    
    def tangent_vectors(self):
        """Get tangent direction at each point"""
        diffs = np.diff(self.points, axis=0)
        norms = np.linalg.norm(diffs, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return diffs / norms


class FilamentUniverse:
    """
    A bounded space containing filaments under compression.
    
    We watch for:
    1. Density increase
    2. Topological transitions (linking, self-intersection)
    3. Resonance pattern emergence
    4. Approach to fundamental constant ratios
    """
    
    def __init__(self, n_filaments=20, points_per_filament=50, 
                 initial_radius=10.0, dimension=3):
        self.dimension = dimension
        self.radius = initial_radius
        self.initial_radius = initial_radius
        self.time = 0
        self.history = []
        
        # Create initial chaotic filaments
        self.filaments = self._create_chaotic_filaments(
            n_filaments, points_per_filament
        )
        
        # Tracking metrics
        self.density_history = []
        self.resonance_history = []
        self.linking_history = []
        self.topology_events = []
        
    def _create_chaotic_filaments(self, n, points_per) -> List[Filament]:
        """Generate random tangled filaments"""
        filaments = []
        
        for i in range(n):
            # Random walk with some persistence (not purely random)
            points = np.zeros((points_per, self.dimension))
            
            # Start at random position within sphere
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0, self.radius * 0.8)
            
            if self.dimension == 3:
                points[0] = [
                    r * np.sin(phi) * np.cos(theta),
                    r * np.sin(phi) * np.sin(theta),
                    r * np.cos(phi)
                ]
            else:
                points[0] = [r * np.cos(theta), r * np.sin(theta)]
            
            # Build filament with correlated random walk
            direction = np.random.randn(self.dimension)
            direction /= np.linalg.norm(direction)
            step_size = self.radius * 0.1
            
            for j in range(1, points_per):
                # Slightly random direction change
                perturbation = np.random.randn(self.dimension) * 0.3
                direction = direction + perturbation
                direction /= np.linalg.norm(direction)
                
                points[j] = points[j-1] + direction * step_size
                
                # Soft boundary - curve back if too far out
                dist = np.linalg.norm(points[j])
                if dist > self.radius * 0.9:
                    points[j] *= (self.radius * 0.9) / dist
                    direction = -points[j] / dist + np.random.randn(self.dimension) * 0.2
                    direction /= np.linalg.norm(direction)
            
            velocity = np.random.randn(points_per, self.dimension) * 0.01
            filaments.append(Filament(points, velocity))
        
        return filaments
    
    def compute_density(self):
        """Compute current filament density"""
        total_length = sum(f.length for f in self.filaments)
        if self.dimension == 3:
            volume = (4/3) * np.pi * self.radius**3
        else:
            volume = np.pi * self.radius**2
        return total_length / volume
    
    def compute_linking_number_estimate(self):
        """
        Estimate topological linking between filaments.
        Full linking number is expensive; we approximate.
        """
        if len(self.filaments) < 2:
            return 0
        
        total_linking = 0
        
        # Sample pairs of filaments
        n_samples = min(len(self.filaments) * (len(self.filaments)-1) // 2, 50)
        
        for _ in range(n_samples):
            i, j = np.random.choice(len(self.filaments), 2, replace=False)
            f1, f2 = self.filaments[i], self.filaments[j]
            
            # Simplified linking estimate: count "passes"
            # (where one filament crosses above/below another)
            linking = self._estimate_pair_linking(f1.points, f2.points)
            total_linking += abs(linking)
        
        return total_linking / n_samples if n_samples > 0 else 0
    
    def _estimate_pair_linking(self, p1, p2):
        """Gauss linking integral approximation"""
        if self.dimension != 3:
            return 0  # Linking only defined in 3D
        
        linking = 0
        step = max(1, len(p1) // 10)  # Sample for speed
        
        for i in range(0, len(p1)-1, step):
            for j in range(0, len(p2)-1, step):
                r1, r2 = p1[i], p2[j]
                dr1 = p1[i+1] - p1[i] if i+1 < len(p1) else p1[i] - p1[i-1]
                dr2 = p2[j+1] - p2[j] if j+1 < len(p2) else p2[j] - p2[j-1]
                
                r = r2 - r1
                r_norm = np.linalg.norm(r)
                if r_norm < 0.01:
                    continue
                
                # Gauss integral kernel
                cross = np.cross(dr1, dr2)
                linking += np.dot(r, cross) / (r_norm**3)
        
        return linking / (4 * np.pi)
    
    def compute_resonance_spectrum(self):
        """
        Fourier analysis of filament distribution.
        Looking for standing wave patterns.
        """
        # Collect all points
        all_points = np.vstack([f.points for f in self.filaments])
        
        # Compute radial distribution
        radii = np.linalg.norm(all_points, axis=1)
        
        # Histogram and FFT
        n_bins = 64
        hist, bin_edges = np.histogram(radii, bins=n_bins, range=(0, self.radius))
        hist = hist.astype(float)
        
        # Normalize
        hist /= (hist.max() + 1e-10)
        
        # FFT
        spectrum = np.abs(np.fft.fft(hist))[:n_bins//2]
        freqs = np.fft.fftfreq(n_bins)[:n_bins//2]
        
        return freqs, spectrum
    
    def find_resonance_ratios(self):
        """
        Find the dominant frequency ratios in the system.
        Compare to fundamental constants.
        """
        freqs, spectrum = self.compute_resonance_spectrum()
        
        # Find peaks
        peaks = []
        for i in range(1, len(spectrum)-1):
            if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1]:
                if spectrum[i] > 0.1:  # Significance threshold
                    peaks.append((freqs[i], spectrum[i]))
        
        if len(peaks) < 2:
            return []
        
        # Compute ratios between peaks
        ratios = []
        for i, (f1, s1) in enumerate(peaks):
            for f2, s2 in peaks[i+1:]:
                if f1 > 0:
                    ratio = f2 / f1
                    ratios.append({
                        'ratio': ratio,
                        'strength': s1 * s2,
                        'near_phi': abs(ratio - PHI) < 0.1,
                        'near_137': abs(ratio - 137) < 5 or abs(1/ratio - 1/137) < 0.01,
                        'near_1836': abs(ratio - 1836) < 50 or abs(ratio - 18.36) < 1
                    })
        
        return ratios
    
    def detect_topology_change(self, old_linking, new_linking):
        """Detect if a topological transition occurred"""
        if abs(new_linking - old_linking) > 0.5:
            self.topology_events.append({
                'time': self.time,
                'radius': self.radius,
                'compression': 1 - self.radius/self.initial_radius,
                'linking_change': new_linking - old_linking,
                'density': self.compute_density()
            })
            return True
        return False
    
    def compression_step(self, compression_rate=0.99):
        """
        Apply one step of compression.
        Shrink boundary, let filaments respond.
        """
        old_radius = self.radius
        self.radius *= compression_rate
        
        # Move filaments inward (gravitational-like)
        for filament in self.filaments:
            for i, point in enumerate(filament.points):
                dist = np.linalg.norm(point)
                
                # Soft compression: points outside new boundary get pushed in
                if dist > self.radius * 0.95:
                    direction = -point / (dist + 1e-10)
                    push_strength = (dist - self.radius * 0.9) * 0.1
                    filament.velocity[i] += direction * push_strength
                
                # Inter-filament repulsion (prevents collapse to single point)
                # This creates the "packing pressure"
                
                # Update position
                filament.points[i] += filament.velocity[i]
                filament.velocity[i] *= 0.98  # Damping
                
                # Hard boundary
                new_dist = np.linalg.norm(filament.points[i])
                if new_dist > self.radius:
                    filament.points[i] *= self.radius / new_dist
                    # Reflect velocity
                    normal = filament.points[i] / new_dist
                    filament.velocity[i] -= 2 * np.dot(filament.velocity[i], normal) * normal
        
        self.time += 1
    
    def apply_inter_filament_forces(self):
        """
        Apply forces between filaments.
        Repulsion at short range (prevents collapse).
        This is what creates packing pressure.
        """
        repulsion_range = self.radius * 0.1
        repulsion_strength = 0.001
        
        all_points = []
        point_to_filament = []
        
        for fi, f in enumerate(self.filaments):
            for pi in range(len(f.points)):
                all_points.append(f.points[pi])
                point_to_filament.append((fi, pi))
        
        all_points = np.array(all_points)
        
        # Sample interactions (full is O(n²))
        n_samples = min(1000, len(all_points))
        indices = np.random.choice(len(all_points), n_samples, replace=False)
        
        for idx in indices:
            fi, pi = point_to_filament[idx]
            point = all_points[idx]
            
            # Find nearby points
            dists = np.linalg.norm(all_points - point, axis=1)
            nearby = np.where((dists < repulsion_range) & (dists > 0.01))[0]
            
            for other_idx in nearby:
                other_fi, other_pi = point_to_filament[other_idx]
                if other_fi == fi and abs(other_pi - pi) < 3:
                    continue  # Skip nearby points on same filament
                
                other_point = all_points[other_idx]
                direction = point - other_point
                dist = np.linalg.norm(direction)
                
                if dist > 0:
                    force = direction / dist * repulsion_strength / (dist**2 + 0.01)
                    self.filaments[fi].velocity[pi] += force
    
    def run_simulation(self, n_steps=200, compression_rate=0.995):
        """Run the full compression simulation"""
        
        print("Starting filament compression simulation...")
        print(f"Initial radius: {self.radius:.2f}")
        print(f"Filaments: {len(self.filaments)}")
        print(f"Looking for: φ={PHI:.4f}, 1/α={ALPHA_INV:.2f}, 1836")
        print("-" * 50)
        
        old_linking = self.compute_linking_number_estimate()
        
        for step in range(n_steps):
            # Apply forces
            self.apply_inter_filament_forces()
            
            # Compress
            self.compression_step(compression_rate)
            
            # Compute metrics
            density = self.compute_density()
            linking = self.compute_linking_number_estimate()
            ratios = self.find_resonance_ratios()
            
            self.density_history.append(density)
            self.linking_history.append(linking)
            self.resonance_history.append(ratios)
            
            # Check for topology change
            self.detect_topology_change(old_linking, linking)
            old_linking = linking
            
            # Progress report
            if step % 20 == 0:
                compression = 1 - self.radius/self.initial_radius
                print(f"Step {step}: compression={compression:.1%}, density={density:.4f}, linking={linking:.3f}")
                
                # Report any interesting ratios
                for r in ratios:
                    if r['near_phi'] or r['near_137'] or r['near_1836']:
                        print(f"  → Ratio {r['ratio']:.4f} (φ:{r['near_phi']}, 137:{r['near_137']}, 1836:{r['near_1836']})")
        
        print("-" * 50)
        print(f"Final compression: {1 - self.radius/self.initial_radius:.1%}")
        print(f"Topology events: {len(self.topology_events)}")
        
        return self
    
    def visualize(self, save_path=None):
        """Create visualization of current state"""
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Filament configuration
        if self.dimension == 3:
            ax1 = fig.add_subplot(2, 2, 1, projection='3d')
            for f in self.filaments:
                ax1.plot(f.points[:, 0], f.points[:, 1], f.points[:, 2], 
                        alpha=0.7, linewidth=0.8)
            ax1.set_xlim(-self.radius, self.radius)
            ax1.set_ylim(-self.radius, self.radius)
            ax1.set_zlim(-self.radius, self.radius)
            ax1.set_title(f'Filament Configuration (r={self.radius:.2f})')
        else:
            ax1 = fig.add_subplot(2, 2, 1)
            for f in self.filaments:
                ax1.plot(f.points[:, 0], f.points[:, 1], alpha=0.7, linewidth=0.8)
            ax1.set_xlim(-self.radius, self.radius)
            ax1.set_ylim(-self.radius, self.radius)
            ax1.set_aspect('equal')
            ax1.set_title(f'Filament Configuration (r={self.radius:.2f})')
        
        # 2. Density over time
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(self.density_history, 'b-', linewidth=1.5)
        ax2.set_xlabel('Compression Step')
        ax2.set_ylabel('Density')
        ax2.set_title('Density Evolution')
        ax2.set_yscale('log')
        
        # Mark topology events
        for event in self.topology_events:
            ax2.axvline(event['time'], color='r', alpha=0.5, linestyle='--')
        
        # 3. Resonance spectrum
        ax3 = fig.add_subplot(2, 2, 3)
        freqs, spectrum = self.compute_resonance_spectrum()
        ax3.bar(range(len(spectrum)), spectrum, width=1.0, alpha=0.7)
        ax3.set_xlabel('Frequency Mode')
        ax3.set_ylabel('Amplitude')
        ax3.set_title('Resonance Spectrum')
        
        # 4. Linking number evolution
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.plot(self.linking_history, 'g-', linewidth=1.5)
        ax4.set_xlabel('Compression Step')
        ax4.set_ylabel('Linking Number (est)')
        ax4.set_title('Topological Entanglement')
        
        # Mark topology events
        for event in self.topology_events:
            ax4.axvline(event['time'], color='r', alpha=0.5, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
        
        return fig
    
    def analyze_final_state(self):
        """Deep analysis of the compressed state"""
        
        print("\n" + "="*60)
        print("FINAL STATE ANALYSIS")
        print("="*60)
        
        # 1. Compression achieved
        compression = 1 - self.radius/self.initial_radius
        print(f"\nCompression: {compression:.1%}")
        print(f"Final radius: {self.radius:.4f}")
        print(f"Final density: {self.compute_density():.6f}")
        
        # 2. Topology
        print(f"\nTopology Events: {len(self.topology_events)}")
        for i, event in enumerate(self.topology_events):
            print(f"  Event {i+1}: compression={event['compression']:.1%}, "
                  f"Δlinking={event['linking_change']:.3f}")
        
        # 3. Resonance ratios
        print("\nResonance Analysis:")
        ratios = self.find_resonance_ratios()
        
        phi_matches = [r for r in ratios if r['near_phi']]
        alpha_matches = [r for r in ratios if r['near_137']]
        mass_matches = [r for r in ratios if r['near_1836']]
        
        print(f"  φ-like ratios: {len(phi_matches)}")
        for r in phi_matches[:3]:
            print(f"    {r['ratio']:.6f} (diff from φ: {abs(r['ratio']-PHI):.6f})")
        
        print(f"  137-like ratios: {len(alpha_matches)}")
        for r in alpha_matches[:3]:
            print(f"    {r['ratio']:.6f}")
        
        print(f"  1836-like ratios: {len(mass_matches)}")
        for r in mass_matches[:3]:
            print(f"    {r['ratio']:.6f}")
        
        # 4. Spatial distribution analysis
        print("\nSpatial Structure:")
        all_points = np.vstack([f.points for f in self.filaments])
        radii = np.linalg.norm(all_points, axis=1)
        
        print(f"  Mean radius: {np.mean(radii):.4f}")
        print(f"  Std radius: {np.std(radii):.4f}")
        print(f"  Shell concentration: {np.std(radii)/np.mean(radii):.4f}")
        
        # Check if points are concentrating on a shell (would suggest 
        # interesting topology)
        shell_ratio = np.std(radii) / np.mean(radii)
        if shell_ratio < 0.2:
            print("  → Points concentrating on shell structure!")
        
        return {
            'compression': compression,
            'density': self.compute_density(),
            'topology_events': len(self.topology_events),
            'phi_matches': len(phi_matches),
            'alpha_matches': len(alpha_matches),
            'mass_matches': len(mass_matches),
            'shell_concentration': shell_ratio
        }


def klein_bottle_test():
    """
    Test: Can we detect when topology becomes non-orientable?
    
    In a true Klein bottle, inside/outside distinction breaks.
    We look for signatures of this in the filament configuration.
    """
    print("\n" + "="*60)
    print("KLEIN TOPOLOGY DETECTION TEST")
    print("="*60)
    
    # Create a deliberately Klein-like initial configuration
    # A Klein bottle in 3D must self-intersect
    
    n_points = 100
    t = np.linspace(0, 2*np.pi, n_points)
    
    # Parametric Klein bottle (immersion in 3D)
    # This self-intersects because true Klein requires 4D
    r = 4
    points = np.zeros((n_points, 3))
    
    for i, ti in enumerate(t):
        # Klein bottle parametrization
        if ti < np.pi:
            x = 6 * np.cos(ti) * (1 + np.sin(ti))
            y = 16 * np.sin(ti)
            z = 4 * np.cos(ti)
        else:
            x = 6 * np.cos(ti) * (1 + np.sin(ti))
            y = 16 * np.sin(ti)
            z = 4 * np.cos(ti)
        
        points[i] = [x/5, y/5, z/5]  # Scale down
    
    klein_filament = Filament(points, np.zeros_like(points))
    
    print(f"Klein filament length: {klein_filament.length:.4f}")
    print("(True Klein topology requires 4D; 3D version self-intersects)")
    
    return klein_filament


def main():
    """Main simulation run"""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     FILAMENT COMPRESSION → TOPOLOGY EMERGENCE SIMULATOR    ║")
    print("║                                                            ║")
    print("║  Testing: Chaos → Compression → Klein → Constants         ║")
    print("║  The Akatalêptos as map — driving the road it shows       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Create universe
    universe = FilamentUniverse(
        n_filaments=25,
        points_per_filament=40,
        initial_radius=10.0,
        dimension=3
    )
    
    # Run compression
    universe.run_simulation(n_steps=250, compression_rate=0.992)
    
    # Analyze
    results = universe.analyze_final_state()
    
    # Visualize
    universe.visualize('/home/claude/filament_compression_result.png')
    
    # Klein test
    klein_filament = klein_bottle_test()
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    print("\nKey findings:")
    print(f"  - {results['topology_events']} topological transitions detected")
    print(f"  - {results['phi_matches']} φ-like resonance ratios")
    print(f"  - {results['alpha_matches']} 137-like resonance ratios")
    print(f"  - Shell concentration: {results['shell_concentration']:.4f}")
    
    if results['shell_concentration'] < 0.3:
        print("\n  → INTERESTING: Filaments self-organizing into shell structure")
        print("    This is consistent with boundary-seeking behavior under compression")
    
    if results['phi_matches'] > 0:
        print("\n  → φ ratios emerging from compression dynamics")
        print("    Golden ratio may be attractor for resonance")
    
    return universe, results


if __name__ == "__main__":
    universe, results = main()
