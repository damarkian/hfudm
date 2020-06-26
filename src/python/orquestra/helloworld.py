import json
import cirq

def helloqubit():
    # Pick a qubit.
    qubit = cirq.GridQubit(0, 0)

    # Create a circuit
    circuit = cirq.Circuit(
        cirq.X(qubit)**0.5,  # Square root of NOT.
        cirq.measure(qubit, key='m')  # Measurement.
    )
    print("Circuit:")
    print(circuit)

    # Simulate the circuit several times.
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=20)
    print("Results:")
    print(result)

def hellocircuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, key='m1'),
        cirq.measure(q1, key='m2')
    )
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=50)
    output = [circuit, result]
    return output

def outputjson(_circuit, _result, jsonfile):
    _jsondict = {}
    _jsondict['circuit'] = str(_circuit)
    _jsondict['result'] = str(_result)
    with open(jsonfile, 'w') as f:
        f.write(json.dumps(_jsondict))
