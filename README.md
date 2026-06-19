# Quantum Subset Sum Solver

This project implements a quantum algorithm to solve the Subset Sum problem using a combination of the Draper Quantum Fourier Transform (QFT) adder and Grover's search algorithm. It is built entirely in Qiskit.

## Algorithm Overview

The solver uses a quantum oracle to evaluate all possible subsets simultaneously using superposition. It adds the values of the included subset elements into an accumulator register in the Fourier basis. If the accumulator matches the desired target value $t$, a phase kickback flips the sign of the corresponding basis state. Finally, a Grover diffusion operator amplifies the probability amplitude of the marked state(s).

The circuit architecture consists of $n$ index qubits (representing subset inclusion), $m$ accumulator qubits where $m = \lceil \log_2(\sum x_i) \rceil$, and $1$ flag qubit for phase kickback.

## Mathematical Formalism

### 1. State Initialization
We initialize the $n$ index qubits in a uniform superposition:

```math
| \psi_0 \rangle = H^{\otimes n} |0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{k=0}^{2^n-1} |k\rangle
