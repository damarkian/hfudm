import json
import numpy as np
import cirq

from openfermioncirq.experiments.hfvqe.gradient_hf import rhf_func_generator
from openfermioncirq.experiments.hfvqe.opdm_functionals import OpdmFunctional
from openfermioncirq.experiments.hfvqe.analysis import (compute_opdm,
                            mcweeny_purification,
                            resample_opdm,
                            fidelity_witness,
                            fidelity)
from openfermioncirq.experiments.hfvqe.third_party.higham import fixed_trace_positive_projection
from openfermioncirq.experiments.hfvqe.molecular_example_odd_qubits import make_h3_2_5

def helloh3():
    # Generate the input files, set up quantum resources, and set up the OpdmFunctional to make measurements. 

    rhf_objective, molecule, parameters, obi, tbi = make_h3_2_5()
    ansatz, energy, gradient = rhf_func_generator(rhf_objective)

    # settings for quantum resources

    qubits = [cirq.GridQubit(0, x) for x in range(molecule.n_orbitals)]
    sampler = cirq.Simulator(dtype=np.complex128)  # this can be a QuantumEngine

    # OpdmFunctional contains an interface for running experiments

    opdm_func = OpdmFunctional(qubits=qubits,
                            sampler=sampler,
                            constant=molecule.nuclear_repulsion,
                            one_body_integrals=obi,
                            two_body_integrals=tbi,
                            num_electrons=molecule.n_electrons // 2,  # only simulate spin-up electrons
                            clean_xxyy=True,
                            purification=True
                            )

    # Do measurements for a given set of parameters

    measurement_data = opdm_func.calculate_data(parameters)

    # Compute 1-RDM, variances, and purification

    opdm, var_dict = compute_opdm(measurement_data,
                                return_variance=True)
    opdm_pure = mcweeny_purification(opdm)

    # Compute energy, fidelities, and errorbars

    raw_energies = []
    raw_fidelity_witness = []
    purified_energies = []
    purified_fidelity_witness = []
    purified_fidelity = []
    true_unitary = ansatz(parameters)
    nocc = molecule.n_electrons // 2
    nvirt = molecule.n_orbitals - nocc

    initial_fock_state = [1] * nocc + [0] * nvirt
    for _ in range(1000):  # 1000 repetitions of the measurement
        new_opdm = resample_opdm(opdm, var_dict)
        raw_energies.append(opdm_func.energy_from_opdm(new_opdm))
        raw_fidelity_witness.append(
            fidelity_witness(target_unitary=true_unitary,
                            omega=initial_fock_state,
                            measured_opdm=new_opdm)
        )
        # fix positivity and trace of sampled 1-RDM if strictly outside
        # feasible set
        w, v = np.linalg.eigh(new_opdm)
        if len(np.where(w < 0)[0]) > 0:
            new_opdm = fixed_trace_positive_projection(new_opdm, nocc)

        new_opdm_pure = mcweeny_purification(new_opdm)
        purified_energies.append(opdm_func.energy_from_opdm(new_opdm_pure))
        purified_fidelity_witness.append(
            fidelity_witness(target_unitary=true_unitary,
                            omega=initial_fock_state,
                            measured_opdm=new_opdm_pure)
        )
        purified_fidelity.append(
            fidelity(target_unitary=true_unitary,
                    measured_opdm=new_opdm_pure)
        )

    jsondict = {}
    jsondict["canonicalHFEnergy"] = str(molecule.hf_energy)
    jsondict["trueEnergy"] = str(energy(parameters))
    jsondict["rawEnergy"] = str(opdm_func.energy_from_opdm(opdm))
    jsondict["rawEnergySd"] = str(np.std(raw_energies))
    jsondict["rawFidelityWitness"] = str(np.mean(raw_fidelity_witness))
    jsondict["rawFidelityWitnessSd"] = str(np.std(raw_fidelity_witness))

    jsondict["purifiedEnergy"] = str(opdm_func.energy_from_opdm(opdm_pure))
    jsondict["purifiedEnergySd"] = str(np.std(purified_energies))
    jsondict["purifiedFidelityWitness"] = str(np.mean(purified_fidelity_witness).real)
    jsondict["purifiedFidelityWitnessSd"] = str(np.std(purified_fidelity_witness))
    jsondict["purifiedFidelity"] = str(np.mean(purified_fidelity).real)
    jsondict["purifiedFidelitySd"] = str(np.std(purified_fidelity))
    jsondict["schema"] = "h3test-circuit-result"
    return jsondict



