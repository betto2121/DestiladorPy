# src/thermo.py
"""
Módulo 2: Núcleo Termodinámico.
Calcula propiedades de equilibrio para el sistema Etanol-Agua.
"""

# 1. CONSTANTES DE ANTOINE (P en mmHg, T en °C)
ANTOINE_CONSTANTS = {
    'ethanol': {'A': 8.20417, 'B': 1642.89, 'C': 230.300},
    'water':   {'A': 8.07131, 'B': 1730.63, 'C': 233.426}
}

def antoine_pressure(T, component):
    """Calcula la presión de vapor de un componente puro usando la ecuación de Antoine."""
    if component not in ANTOINE_CONSTANTS:
        raise ValueError(f"Componente '{component}' no definido. Usa 'ethanol' o 'water'.")
    const = ANTOINE_CONSTANTS[component]
    P_sat_mmHg = 10**(const['A'] - const['B'] / (T + const['C']))
    P_sat_atm = P_sat_mmHg / 760.0
    return P_sat_atm

def test_antoine():
    """Prueba rápida: el agua debe hervir a ~100°C a 1 atm."""
    T_test = 100.0
    P_sat_water = antoine_pressure(T_test, 'water')
    print(f"P_sat del agua a {T_test}°C: {P_sat_water:.4f} atm")
    print(f"¿Es cercano a 1 atm? (Error: {abs(P_sat_water - 1.0):.4f} atm)")
    return abs(P_sat_water - 1.0) < 0.01

def bubble_temperature_raoult(x_ethanol, P_total=1.0, T_guess=80.0):
    """
    Calcula la temperatura de burbuja para una mezcla binaria etanol-agua.
    Supone mezcla ideal (Ley de Raoult).
    """
    from scipy.optimize import newton

    def equation_to_solve(T):
        P_ethanol = antoine_pressure(T, 'ethanol')
        P_water = antoine_pressure(T, 'water')
        P_calculated = x_ethanol * P_ethanol + (1 - x_ethanol) * P_water
        return P_total - P_calculated

    try:
        T_solution = newton(equation_to_solve, T_guess, tol=1e-6, maxiter=50)
        return T_solution
    except RuntimeError as e:
        raise RuntimeError(f"El solver no converge para x={x_ethanol}, P={P_total}. Error: {e}")

def test_bubble_temperature():
    """Prueba con puntos conocidos."""
    print("\n=== PRUEBA DE TEMPERATURA DE BURBUJA ===")
    T_bubble_water = bubble_temperature_raoult(x_ethanol=0.0, P_total=1.0)
    print(f"1. Agua pura (x=0.0): T_burbuja = {T_bubble_water:.2f} °C (Esperado ~100.0 °C)")
    T_bubble_ethanol = bubble_temperature_raoult(x_ethanol=1.0, P_total=1.0)
    print(f"2. Etanol puro (x=1.0): T_burbuja = {T_bubble_ethanol:.2f} °C (Esperado ~78.4 °C)")
    T_bubble_mix = bubble_temperature_raoult(x_ethanol=0.5, P_total=1.0)
    print(f"3. Mezcla 50% (x=0.5): T_burbuja = {T_bubble_mix:.2f} °C (Debe estar entre 78.4 y 100 °C)")
    success = (abs(T_bubble_water - 100.0) < 0.5 and
               abs(T_bubble_ethanol - 78.4) < 0.5 and
               78.4 < T_bubble_mix < 100.0)
    return success

# === BLOQUE PRINCIPAL CORREGIDO (¡La indentación aquí es clave!) ===
if __name__ == "__main__":
    print("=== PRUEBA DEL MÓDULO TERMODINÁMICO ===")
    test1 = test_antoine()
    test2 = test_bubble_temperature()

    if test1 and test2:
        print("\n✅ TODAS LAS PRUEBAS PASARON. Módulo listo.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar constantes o implementación.")
