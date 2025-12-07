import sys
import time
import psutil

DELTA = 30

ALPHA = {
    'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
    'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
    'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
    'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
}

def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed

def time_wrapper(call_algorithm):
    start_time = time.time()
    result = call_algorithm()
    end_time = time.time()
    time_taken = (end_time - start_time) * 1000
    return time_taken, result

def generate_string(base_string, indices):
    current_string = base_string
    for idx in indices:
        current_string = current_string[:idx+1] + current_string + current_string[idx+1:]
    return current_string

def parse_input(input_file):
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    separator_idx = 0
    for i in range(1, len(lines)):
        if lines[i] and lines[i][0] in ['A', 'C', 'G', 'T']:
            separator_idx = i
            break
    
    # First string generation
    s0 = lines[0]
    s_indices = [int(lines[i]) for i in range(1, separator_idx)]
    s = generate_string(s0, s_indices)
    
    # Second string generation
    t0 = lines[separator_idx]
    t_indices = [int(lines[i]) for i in range(separator_idx + 1, len(lines))]
    t = generate_string(t0, t_indices)
    
    return s, t

def space_efficient_alignment_cost(x, y):
    """
    Space-efficient DP to compute alignment costs. Only keeps two rows at a time: O(min(m,n)) space instead of O(mn).
    Uses the same recurrence as basic DP but with space optimization.
    
    Returns an array where result[j] = cost of aligning x with y[0:j]
    """
    m, n = len(x), len(y)
    
    # only keep two rows (prev and curr) instead of full table
    prev = [j * DELTA for j in range(n + 1)]  
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        curr[0] = i * DELTA  
        for j in range(1, n + 1):
            # recurrence 
            match_cost = ALPHA[x[i-1]][y[j-1]] + prev[j-1]
            gap_x = DELTA + prev[j]
            gap_y = DELTA + curr[j-1]
            curr[j] = min(match_cost, gap_x, gap_y)
        prev, curr = curr, prev  # prev becomes curr for next itr
    return prev

def find_optimal_split(x, y):
    """
    Find the optimal split point using space-efficient DP.
    Divide step: Split X in half, find optimal split point in Y.
    
    Forward pass: Compute costs for X^L (left part) with 
    substrings of Y ending with y_j.
    Backward pass: Compute costs for X^R (right part) with 
    substrings of Y starting from y_i.
    
    Returns the index in y where we should split.
    """
    m, n = len(x), len(y)
    mid = m // 2  
    
    forward = space_efficient_alignment_cost(x[:mid], y)
    
    x_suffix_rev = x[mid:][::-1] 
    y_rev = y[::-1] 
    
    backward_rev = space_efficient_alignment_cost(x_suffix_rev, y_rev)
    
    backward = [backward_rev[n - j] for j in range(n + 1)]
    
    min_cost = float('inf')
    split_idx = 0
    
    for j in range(n + 1):
        total_cost = forward[j] + backward[j]
        if total_cost < min_cost:
            min_cost = total_cost
            split_idx = j
    
    return split_idx

def efficient_alignment(x, y):
    """
    Memory-efficient alignment using divide-and-conquer 
    High-level solution based on divide and conquer 
    
    Complexity: Time O(mn), Space O(min(m,n))
    Total operations = cmn + ½cmn + ¼cmn + ... = 2cmn = Θ(mn) 
    
    Returns: (cost, aligned_x, aligned_y)
    """
    m, n = len(x), len(y)
    
    if m == 0:
        return n * DELTA, '_' * n, y
    if n == 0:
        return m * DELTA, x, '_' * m
   
    if m <= 10 or n <= 10:
        return basic_alignment_small(x, y)
    
    mid = m // 2
    split_idx = find_optimal_split(x, y)
    
    cost1, x1, y1 = efficient_alignment(x[:mid], y[:split_idx])
    cost2, x2, y2 = efficient_alignment(x[mid:], y[split_idx:])
    
    return cost1 + cost2, x1 + x2, y1 + y2

def basic_alignment_small(x, y):
   
    m, n = len(x), len(y)
    
    if m == 0:
        return n * DELTA, '_' * n, y
    if n == 0:
        return m * DELTA, x, '_' * m
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i * DELTA
    for j in range(n + 1):
        dp[0][j] = j * DELTA
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match_cost = ALPHA[x[i-1]][y[j-1]] + dp[i-1][j-1]
            gap_x = DELTA + dp[i-1][j]
            gap_y = DELTA + dp[i][j-1]
            dp[i][j] = min(match_cost, gap_x, gap_y)
    
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
    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    x, y = parse_input(input_file)
    
    memory_before = process_memory()
    
    def call_algorithm():
        return efficient_alignment(x, y)
    
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

