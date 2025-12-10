#!/usr/bin/env python3
"""
Plotting script for CSCI 570 Sequence Alignment Project.
Runs both basic and efficient algorithms on datapoints and generates:
1. CPU Time vs Problem Size plot
2. Memory Usage vs Problem Size plot
"""

import subprocess
import os
import sys

# Try to import matplotlib, provide instructions if not available
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: matplotlib not installed.")
    print("To install: pip3 install matplotlib --break-system-packages")
    print("Or use a virtual environment.")
    print("\nGenerating CSV data instead...\n")


def get_problem_size(input_file):
    """Calculate the problem size (m + n) from input file."""
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Find separator (second base string)
    separator_idx = 0
    for i in range(1, len(lines)):
        if lines[i] and lines[i][0] in ['A', 'C', 'G', 'T']:
            separator_idx = i
            break
    
    # Generate first string
    s = lines[0]
    for i in range(1, separator_idx):
        idx = int(lines[i])
        s = s[:idx+1] + s + s[idx+1:]
    
    # Generate second string
    t = lines[separator_idx]
    for i in range(separator_idx + 1, len(lines)):
        idx = int(lines[i])
        t = t[:idx+1] + t + t[idx+1:]
    
    return len(s) + len(t)


def run_algorithm(script, input_file, output_file):
    """Run an algorithm and return (time_ms, memory_kb)."""
    try:
        result = subprocess.run(
            ['python3', script, input_file, output_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"Error running {script} on {input_file}: {result.stderr}")
            return None, None
        
        # Read output file to get time and memory
        with open(output_file, 'r') as f:
            lines = f.readlines()
            time_ms = float(lines[3].strip())
            memory_kb = float(lines[4].strip())
        
        return time_ms, memory_kb
    
    except subprocess.TimeoutExpired:
        print(f"Timeout running {script} on {input_file}")
        return None, None
    except Exception as e:
        print(f"Exception running {script} on {input_file}: {e}")
        return None, None


def collect_data(datapoints_dir):
    """Collect performance data for all datapoints."""
    # Get all input files sorted by number
    input_files = sorted(
        [f for f in os.listdir(datapoints_dir) if f.startswith('in') and f.endswith('.txt')],
        key=lambda x: int(x[2:-4])  # Extract number from 'inX.txt'
    )
    
    results = {
        'problem_sizes': [],
        'basic_time': [],
        'basic_memory': [],
        'efficient_time': [],
        'efficient_memory': []
    }
    
    for input_file in input_files:
        input_path = os.path.join(datapoints_dir, input_file)
        problem_size = get_problem_size(input_path)
        
        print(f"Processing {input_file} (problem size: {problem_size})...")
        
        # Run basic algorithm
        basic_time, basic_memory = run_algorithm(
            'basic.py', input_path, 'temp_basic_output.txt'
        )
        
        # Run efficient algorithm
        efficient_time, efficient_memory = run_algorithm(
            'efficient.py', input_path, 'temp_efficient_output.txt'
        )
        
        if basic_time is not None and efficient_time is not None:
            results['problem_sizes'].append(problem_size)
            results['basic_time'].append(basic_time)
            results['basic_memory'].append(basic_memory)
            results['efficient_time'].append(efficient_time)
            results['efficient_memory'].append(efficient_memory)
            
            print(f"  Basic:     Time={basic_time:.2f}ms, Memory={basic_memory:.2f}KB")
            print(f"  Efficient: Time={efficient_time:.2f}ms, Memory={efficient_memory:.2f}KB")
    
    # Cleanup temp files
    for temp_file in ['temp_basic_output.txt', 'temp_efficient_output.txt']:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return results


def save_csv(results, filename='results.csv'):
    """Save results to CSV file."""
    with open(filename, 'w') as f:
        f.write("ProblemSize,BasicTime(ms),EfficientTime(ms),BasicMemory(KB),EfficientMemory(KB)\n")
        for i in range(len(results['problem_sizes'])):
            f.write(
                f"{results['problem_sizes'][i]},"
                f"{results['basic_time'][i]:.4f},"
                f"{results['efficient_time'][i]:.4f},"
                f"{results['basic_memory'][i]:.4f},"
                f"{results['efficient_memory'][i]:.4f}\n"
            )
    print(f"\nResults saved to {filename}")


def plot_results(results):
    """Generate CPU and Memory plots."""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot generate plots without matplotlib.")
        return
    
    problem_sizes = results['problem_sizes']
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # CPU Time Plot
    ax1.plot(problem_sizes, results['basic_time'], 'b-o', label='Basic', linewidth=2, markersize=6)
    ax1.plot(problem_sizes, results['efficient_time'], 'r-s', label='Efficient', linewidth=2, markersize=6)
    ax1.set_xlabel('Problem Size (m + n)', fontsize=12)
    ax1.set_ylabel('Time (milliseconds)', fontsize=12)
    ax1.set_title('CPU Time vs Problem Size', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Memory Usage Plot
    ax2.plot(problem_sizes, results['basic_memory'], 'b-o', label='Basic', linewidth=2, markersize=6)
    ax2.plot(problem_sizes, results['efficient_memory'], 'r-s', label='Efficient', linewidth=2, markersize=6)
    ax2.set_xlabel('Problem Size (m + n)', fontsize=12)
    ax2.set_ylabel('Memory (KB)', fontsize=12)
    ax2.set_title('Memory Usage vs Problem Size', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plots
    plt.savefig('CPUPlot.png', dpi=150, bbox_inches='tight')
    plt.savefig('MemoryPlot.png', dpi=150, bbox_inches='tight')
    
    # Also save individual plots
    fig1, ax = plt.subplots(figsize=(8, 6))
    ax.plot(problem_sizes, results['basic_time'], 'b-o', label='Basic', linewidth=2, markersize=6)
    ax.plot(problem_sizes, results['efficient_time'], 'r-s', label='Efficient', linewidth=2, markersize=6)
    ax.set_xlabel('Problem Size (m + n)', fontsize=12)
    ax.set_ylabel('Time (milliseconds)', fontsize=12)
    ax.set_title('CPU Time vs Problem Size', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.savefig('CPUPlot.png', dpi=150, bbox_inches='tight')
    plt.close(fig1)
    
    fig2, ax = plt.subplots(figsize=(8, 6))
    ax.plot(problem_sizes, results['basic_memory'], 'b-o', label='Basic', linewidth=2, markersize=6)
    ax.plot(problem_sizes, results['efficient_memory'], 'r-s', label='Efficient', linewidth=2, markersize=6)
    ax.set_xlabel('Problem Size (m + n)', fontsize=12)
    ax.set_ylabel('Memory (KB)', fontsize=12)
    ax.set_title('Memory Usage vs Problem Size', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.savefig('MemoryPlot.png', dpi=150, bbox_inches='tight')
    plt.close(fig2)
    
    print("\nPlots saved:")
    print("  - CPUPlot.png")
    print("  - MemoryPlot.png")


def main():
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    datapoints_dir = os.path.join(script_dir, 'data', 'Datapoints')
    
    if not os.path.exists(datapoints_dir):
        print(f"Error: Datapoints directory not found at {datapoints_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("CSCI 570 Sequence Alignment - Performance Analysis")
    print("=" * 60)
    print()
    
    # Collect data
    results = collect_data(datapoints_dir)
    
    if not results['problem_sizes']:
        print("No data collected. Exiting.")
        sys.exit(1)
    
    # Save CSV
    save_csv(results)
    
    # Generate plots
    if MATPLOTLIB_AVAILABLE:
        plot_results(results)
    else:
        print("\nTo generate plots, install matplotlib and run this script again.")


if __name__ == "__main__":
    main()
