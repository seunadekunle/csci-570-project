import sys
import time
import psutil # external library referenced in assignment document

DELTA = 30

ALPHA = {
    'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
    'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
    'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
    'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
}

def process_memory():
    """
    Uses the psutil library to measure the memory usage of the current process.

    Returns:
        int: Memory usage in MB
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed

def time_wrapper(call_algorithm):
    """
    Measurses the execution time of a callable function

    Args:
        call_algorithm (callable): Executed function

    Returns:
        tuple: (time_taken, result)
    """
    start_time = time.time()
    result = call_algorithm()
    end_time = time.time()
    time_taken = (end_time - start_time) * 1000
    return time_taken, result

def generate_string(base_string, indices):
    """
    Generate a DNA string using iterative self-insertion

    Args:
        base_string (str): Initial DNA sequence.
        indices (list[int]): Positions used for expansion

    Returns:
        str: Fully expanded DNA sequence
    """
    current_string = base_string
    for idx in indices:
        current_string = current_string[:idx+1] + current_string + current_string[idx+1:]
    return current_string

def parse_input(input_file):
    """
    Parse the custom DNA input file and generate two expanded sequence

    Args:
        input_file (str): Path to input file

    Returns:
        tuple: (expanded_string_s, expanded_string_t)
    """
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    separator_idx = 0
    for i in range(1, len(lines)):
        if lines[i] and lines[i][0] in ['A', 'C', 'G', 'T']:
            separator_idx = i
            break
    
    # first string generation
    s0 = lines[0]
    s_indices = [int(lines[i]) for i in range(1, separator_idx)]
    s = generate_string(s0, s_indices)
    
    # second string generation
    t0 = lines[separator_idx]
    t_indices = [int(lines[i]) for i in range(separator_idx + 1, len(lines))]
    t = generate_string(t0, t_indices)
    
    return s, t

def basic_alignment(x, y):
    """
    Computes optimal global alignment of two sequences

    Recurrence:
        OPT(i, j) = min(
            OPT(i-1, j-1) + alpha(x_i, y_j),
            OPT(i-1, j) + delta,
            OPT(i, j-1) + delta
        )
        
    Args:
        x (str): First DNA sequence
        y (str): Second DNA sequence

    Returns:
        tuple: (cost, aligned_x, aligned_y)
    """
    m, n = len(x), len(y)
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i * DELTA  
    for j in range(n + 1):
        dp[0][j] = j * DELTA 
    
    # filling bottom up
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # recurrence 
            match_cost = ALPHA[x[i-1]][y[j-1]] + dp[i-1][j-1]  
            gap_x = DELTA + dp[i-1][j] 
            gap_y = DELTA + dp[i][j-1] 
            
            dp[i][j] = min(match_cost, gap_x, gap_y)
    
    # top down backtracking for aligning
    aligned_x = []
    aligned_y = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            match_cost = ALPHA[x[i-1]][y[j-1]] + dp[i-1][j-1]
            gap_x = DELTA + dp[i-1][j]
            gap_y = DELTA + dp[i][j-1]
            
            if dp[i][j] == gap_y:
                aligned_x.append('_')
                aligned_y.append(y[j-1])
                j -= 1
            elif dp[i][j] == gap_x:
                aligned_x.append(x[i-1])
                aligned_y.append('_')
                i -= 1
            else:
                aligned_x.append(x[i-1])
                aligned_y.append(y[j-1])
                i -= 1
                j -= 1
        elif i > 0:
            aligned_x.append(x[i-1])
            aligned_y.append('_')
            i -= 1
        else:
            aligned_x.append('_')
            aligned_y.append(y[j-1])
            j -= 1
    
    aligned_x.reverse()
    aligned_y.reverse()
    
    cost = dp[m][n]
    return cost, ''.join(aligned_x), ''.join(aligned_y)

def main():
    """
    Program entry point
    
    Loads input file, calls alignment algorithm, and writes output to file

    Exists if required arguments are missing
    """
    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    x, y = parse_input(input_file)
    
    memory_before = process_memory()

    def call_algorithm():
        return basic_alignment(x, y)
    
    time_taken, (cost, aligned_x, aligned_y) = time_wrapper(call_algorithm)
    
    memory_after = process_memory()
    
    memory_used = float(memory_after - memory_before)
    
    with open(output_file, 'w') as f:
        f.write(f"{cost}\n")
        f.write(f"{aligned_x}\n")
        f.write(f"{aligned_y}\n")
        f.write(f"{time_taken}\n")
        f.write(f"{memory_used}\n")

if __name__ == "__main__":
    main()

