import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT

def get_aer_simulator(threads: int = 4):
    """
    Returns a Qiskit Aer simulator explicitly configured for multithreading.
    """
    backend = AerSimulator(
        max_parallel_threads=threads,
        max_parallel_experiments=1,
        max_parallel_shots=1,
        statevector_parallel_threshold=10
    )
    return backend

def initialize_state(n: int, m: int):
    """
    Allocates n index qubits, m accumulator qubits, and 1 flag qubit.
    Applies Hadamard gates to the index register.
    """
    index_qubits = QuantumRegister(n, 'idx')
    accumulator_qubits = QuantumRegister(m, 'acc')
    flag_qubit = QuantumRegister(1, 'flag')
    
    qc = QuantumCircuit(index_qubits, accumulator_qubits, flag_qubit)
    
    # Initialize index qubits in uniform superposition
    qc.h(index_qubits)
    
    # Initialize flag qubit in |-> state
    qc.x(flag_qubit)
    qc.h(flag_qubit)
    
    return qc, index_qubits, accumulator_qubits, flag_qubit

def draper_qft_adder(qc: QuantumCircuit, index_qubits: QuantumRegister, accumulator_qubits: QuantumRegister, numbers: list[int], inverse: bool = False):
    """
    Applies the Oracle Core logic: Draper QFT adder.
    Adds the subset sum into the accumulator in the Fourier basis.
    """
    m = len(accumulator_qubits)
    n = len(index_qubits)
    
    if not inverse:
        # Apply QFT to accumulator
        qc.append(QFT(m, do_swaps=True).to_instruction(), accumulator_qubits)
        
        # Controlled-phase rotations
        for i in range(n):
            val = numbers[i]
            for j in range(m):
                phase = 2 * math.pi * val / (2 ** (m - j))
                if phase % (2*math.pi) != 0:
                    qc.cp(phase, index_qubits[i], accumulator_qubits[j])
        
        # Apply Inverse QFT
        qc.append(QFT(m, do_swaps=True, inverse=True).to_instruction(), accumulator_qubits)
    else:
        # Inverse operation: QFT -> Inv Phase Rotations -> IQFT
        qc.append(QFT(m, do_swaps=True).to_instruction(), accumulator_qubits)
        
        for i in reversed(range(n)):
            val = numbers[i]
            for j in reversed(range(m)):
                phase = -2 * math.pi * val / (2 ** (m - j))
                if phase % (2*math.pi) != 0:
                    qc.cp(phase, index_qubits[i], accumulator_qubits[j])
        
        qc.append(QFT(m, do_swaps=True, inverse=True).to_instruction(), accumulator_qubits)

def phase_kickback_and_uncompute(qc: QuantumCircuit, index_qubits: QuantumRegister, accumulator_qubits: QuantumRegister, flag_qubit: QuantumRegister, numbers: list[int], target: int):
    """
    Applies X gates framing the binary representation of target state t.
    Executes MCX gate across accumulator targeting the flag qubit.
    Uncomputes the accumulator back to |0>.
    """
    m = len(accumulator_qubits)
    
    # 1. Flip accumulator qubits where the target binary representation is 0.
    target_bin = bin(target)[2:].zfill(m)
    for j in range(m):
        bit_val = target_bin[m - 1 - j]
        if bit_val == '0':
            qc.x(accumulator_qubits[j])
            
    # 2. MCX gate across accumulator targeting flag
    qc.mcx(accumulator_qubits, flag_qubit[0])
    
    # 3. Un-flip the accumulator qubits
    for j in range(m):
        bit_val = target_bin[m - 1 - j]
        if bit_val == '0':
            qc.x(accumulator_qubits[j])
            
    # 4. Uncompute the addition
    draper_qft_adder(qc, index_qubits, accumulator_qubits, numbers, inverse=True)

def grover_diffuser(qc: QuantumCircuit, index_qubits: QuantumRegister):
    """
    Amplitude amplification operator 2|s><s| - I on index register.
    """
    n = len(index_qubits)
    qc.h(index_qubits)
    qc.x(index_qubits)
    
    qc.h(index_qubits[n-1])
    if n > 1:
        qc.mcx(index_qubits[:-1], index_qubits[n-1])
    else:
        qc.x(index_qubits[0])
    qc.h(index_qubits[n-1])
    
    qc.x(index_qubits)
    qc.h(index_qubits)

def build_subset_sum_circuit(numbers: list[int], target: int) -> QuantumCircuit:
    n = len(numbers)
    max_sum = sum(numbers)
    if max_sum == 0:
        m = 1
    else:
        m = math.ceil(math.log2(max_sum + 1))
        
    if target > max_sum or target < 0:
        m = max(m, math.ceil(math.log2(abs(target) + 1)))

    qc, index_qubits, accumulator_qubits, flag_qubit = initialize_state(n, m)
    
    # Optimal number of Grover iterations roughly (pi/4) * sqrt(N/M)
    # Here N = 2^n. M is unknown, but we assume 1.
    iterations = max(1, round(math.pi / 4 * math.sqrt(2**n)))
    
    for _ in range(iterations):
        draper_qft_adder(qc, index_qubits, accumulator_qubits, numbers, inverse=False)
        phase_kickback_and_uncompute(qc, index_qubits, accumulator_qubits, flag_qubit, numbers, target)
        grover_diffuser(qc, index_qubits)
        
    cr = ClassicalRegister(n, 'c')
    qc.add_register(cr)
    
    # Only measure the index qubits. Keep the bit order aligned.
    qc.measure(index_qubits, cr)
    
    return qc
