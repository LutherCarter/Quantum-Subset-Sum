import os
from qiskit import transpile
from qiskit.visualization import plot_histogram
from SubsetSum import build_subset_sum_circuit, get_aer_simulator

def run_demonstration():
    print("--- Quantum Subset Sum Demonstration ---")
    print("Please enter a comma-separated list of positive integers for the array:")
    arr_input = input("> ").strip()
    if not arr_input:
        print("No input provided. Using default array: 2, 3, 5, 7")
        numbers = [2, 3, 5, 7]
    else:
        numbers = [int(x.strip()) for x in arr_input.split(",")]
        
    print("Please enter the target sum (integer):")
    target_input = input("> ").strip()
    if not target_input:
        print("No target provided. Using default target: 10")
        target = 10
    else:
        target = int(target_input)
        
    shots = 1024
    
    print(f"Input Array: {numbers}")
    print(f"Target Sum:  {target}")
    print("\nBuilding quantum circuit...")
    
    qc = build_subset_sum_circuit(numbers, target)
    backend = get_aer_simulator(threads=4)
    
    print(f"Executing on Qiskit Aer Simulator ({shots} shots)...")
    t_qc = transpile(qc, backend)
    
    job = backend.run(t_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Analyze the results
    most_probable_state = max(counts, key=counts.get)
    highest_prob = counts[most_probable_state] / shots
    
    print("\n--- Execution Results ---")
    if highest_prob > 0.5:
        # Translate the measured bitstring back into the subset
        # Qiskit orders bitstrings from q_{n-1} (left) to q_0 (right).
        subset = []
        for i, bit in enumerate(reversed(most_probable_state)):
            if bit == '1':
                subset.append(numbers[i])
                
        print(f"Success! Found valid subset: {subset}")
        print(f"Measured state '{most_probable_state}' with {highest_prob*100:.1f}% probability.")
        print(f"Subset sum validates to: {sum(subset)}")
    else:
        print("No valid subset found with high probability.")
        print(f"The distribution is diffuse. Highest probability state '{most_probable_state}' was only {highest_prob*100:.1f}%.")
        
    print("\nGenerating histogram plot...")
    try:
        fig = plot_histogram(counts, title=f"Subset Sum Probability Distribution\nTarget: {target} | Array: {numbers}")
        filename = "histogram_results.png"
        fig.savefig(filename)
        print(f"Histogram successfully saved as '{filename}' in the current directory.")
    except ImportError:
        print("Note: 'matplotlib' is required to save the histogram image. Please install it using 'pip install matplotlib'.")

if __name__ == "__main__":
    run_demonstration()
