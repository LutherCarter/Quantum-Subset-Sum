import pytest
from qiskit import transpile
from SubsetSum import build_subset_sum_circuit, get_aer_simulator

def run_subset_sum_experiment(numbers, target, shots=1000):
    qc = build_subset_sum_circuit(numbers, target)
    backend = get_aer_simulator(threads=4)
    
    t_qc = transpile(qc, backend)
    
    job = backend.run(t_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    return counts

def test_trivial_case():
    """
    n=2, numbers=[1, 2], target=3. 
    Valid subset: [1, 2] -> index '11'
    """
    numbers = [1, 2]
    target = 3
    counts = run_subset_sum_experiment(numbers, target, shots=1000)
    
    assert '11' in counts
    prob = counts.get('11', 0) / 1000.0
    assert prob > 0.9

def test_boundary_case():
    """
    n=4, numbers=[7, 7, 7, 7], target=28.
    Valid subset: [7, 7, 7, 7] -> index '1111'
    """
    numbers = [7, 7, 7, 7]
    target = 28
    counts = run_subset_sum_experiment(numbers, target, shots=1000)
    
    assert '1111' in counts
    prob = counts.get('1111', 0) / 1000.0
    assert prob > 0.9

def test_null_case():
    """
    n=3, numbers=[2, 4, 6], target=5
    No subset sums to 5.
    """
    numbers = [2, 4, 6]
    target = 5
    counts = run_subset_sum_experiment(numbers, target, shots=1000)
    
    max_count = max(counts.values())
    max_prob = max_count / 1000.0
    assert max_prob < 0.5 
