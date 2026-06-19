# Quantum Subset Sum Solver

This project implements a quantum algorithm to solve the Subset Sum problem using a combination of the Draper Quantum Fourier Transform (QFT) adder and Grover's search algorithm. It is built entirely in Qiskit.

## Algorithm Overview

The solver uses a quantum oracle to evaluate all possible subsets simultaneously using superposition. It adds the values of the included subset elements into an accumulator register in the Fourier basis. If the accumulator matches the desired target value $t$, a phase kickback flips the sign of the corresponding basis state. Finally, a Grover diffusion operator amplifies the probability amplitude of the marked state(s).

The circuit architecture consists of $n$ index qubits (representing subset inclusion), $m$ accumulator qubits where $m = \lceil \log_2(\sum x_i) \rceil$, and $1$ flag qubit for phase kickback.

## Mathematical Formalism

### 1. State Initialization
We initialize the $n$ index qubits in a uniform superposition:
$$ | \psi_0 \rangle = H^{\otimes n} |0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{k=0}^{2^n-1} |k\rangle $$
Each computational basis state $|k\rangle$ corresponds to a unique subset of the input array.

### 2. The Oracle (Draper QFT Adder)
To compute the sum without destroying the superposition, we utilize a Draper adder on the accumulator register (initially $|0\rangle$).

We apply the QFT to the accumulator:
$$ \text{QFT} |0\rangle^{\otimes m} = \frac{1}{\sqrt{2^m}} \sum_{y=0}^{2^m-1} |y\rangle $$

Then, for each element $x_i$ in the input array, controlled by the $i$-th index qubit, we apply controlled-phase shifts to the accumulator. The phase applied to the $j$-th qubit (where $j=0$ is the most significant phase bit in Qiskit's convention, or $j \in [0, m-1]$ from LSB to MSB in standard binary notation) is defined by the rotation operator:
$$ R_Z \left( \frac{2\pi x_i}{2^{m-j}} \right) $$

These rotations effectively add $x_i$ to the accumulator in the phase representation:
$$
|y\rangle \rightarrow \exp\left( \frac{2\pi i \cdot x_i \cdot y}{2^m} \right) |y\rangle
$$

An Inverse QFT (IQFT) maps the accumulator back to the computational basis, revealing the exact sum $s_k$ for each subset $|k\rangle$.

### 3. Phase Kickback and Uncomputation
We verify if the computed sum $s_k$ equals the target $t$. We apply $X$ gates framing the bitwise limits of $t$:
$$
X^{\text{where } t_j = 0}
$$
A multi-controlled $X$ (MCX) gate targets the flag qubit (initialized to $|-\rangle$), applying a $-1$ phase shift if the sum equals $t$.

We then precisely reverse the Oracle operations (QFT $\rightarrow$ Inverse Phase Rotations $\rightarrow$ IQFT) to perfectly uncompute the accumulator, returning it to $|0\rangle^{\otimes m}$ while preserving quantum interference and avoiding entanglement between the index and accumulator registers.

### 4. Grover Diffusion Operator
The standard amplitude amplification operator is applied to the index register:
$$
U_s = 2|s\rangle\langle s| - I
$$
Where $|s\rangle$ is the uniform superposition state.

### Complexity
The quantum algorithm finds a solution in $\mathcal{O}(\sqrt{2^n})$ evaluations, representing a quadratic speedup over classical brute-force search ($\mathcal{O}(2^n)$).

## Benchmarking & Validation

The algorithm incorporates a headless testing suite constructed via `pytest`. The validation framework uses the `Qiskit Aer` multi-threaded simulator to handle dense statevector calculations.

The suite verifies:
- **Trivial cases:** Small inputs ($n=2$) to ensure baseline phase alignment.
- **Boundary cases:** Maximum bounds (e.g. $n=4, x_i=7, t=28$).
- **Null cases:** Unsolvable targets result in diffuse, near-uniform probability distributions instead of collapsing to a false positive.

### Running Tests
To run the automated tests locally, use `pytest`:
```bash
pytest test_subset_sum.py -v
```
To achieve optimal statevector benchmarking performance, the backend strictly configures CPU threading.

## Interactive Demonstration

In addition to the headless testing suite, the project includes an interactive demonstration script.

You can run the script using Python:
```bash
python run_demo.py
```

The `run_demo.py` script allows you to:
1. Interactively input a custom array of integers and a target sum.
2. Build and execute the full Grover-QFT subset sum circuit on the Qiskit Aer backend.
3. Automatically parse the results and translate the highest probability state back into human-readable subset values.
4. Generate and save a visual bar chart (`histogram_results.png`) plotting the subset probability distribution (requires `matplotlib`).
