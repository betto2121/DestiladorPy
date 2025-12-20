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
# Añade estas funciones al final de src/thermo.py, ANTES del "if __name__ ..."

def calculate_vapor_composition(x_ethanol, T, P_total=1.0):
    """
    Calcula la composición del vapor en equilibrio (y) para un líquido dado.
    Ley de Raoult: y_i = (x_i * P_sat_i(T)) / P_total
    """
    P_sat_eth = antoine_pressure(T, 'ethanol')
    P_sat_wat = antoine_pressure(T, 'water')
    y_ethanol = (x_ethanol * P_sat_eth) / P_total
    # y_water se calcularía como (1 - x_ethanol) * P_sat_wat / P_total
    return y_ethanol

def generate_equilibrium_curve(num_points=51, P_total=1.0):
    """
    Genera la curva de equilibrio x-y para el sistema etanol-agua.
    Returns:
        x_list (list): Fracciones molares de etanol en líquido.
        y_list (list): Fracciones molares de etanol en vapor en equilibrio.
        T_list (list): Temperaturas de burbuja correspondientes [°C].
    """
    import csv
    import os

    x_list = []
    y_list = []
    T_list = []

    print(f"Generando curva de equilibrio con {num_points} puntos...")
    for i in range(num_points):
        x = i / (num_points - 1)  # De 0 a 1 inclusive
        try:
            T_bubble = bubble_temperature_raoult(x_ethanol=x, P_total=P_total)
            y = calculate_vapor_composition(x_ethanol=x, T=T_bubble, P_total=P_total)
            x_list.append(x)
            y_list.append(y)
            T_list.append(T_bubble)
        except Exception as e:
            print(f"  Advertencia en x={x:.3f}: {e}")

    # Guardar datos en CSV
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)  # Asegura que la carpeta existe
    csv_path = os.path.join(data_dir, 'equilibrium_curve.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x_ethanol', 'y_ethanol', 'T_bubble_C'])
        for x_val, y_val, t_val in zip(x_list, y_list, T_list):
            writer.writerow([f"{x_val:.6f}", f"{y_val:.6f}", f"{t_val:.4f}"])
    print(f"✅ Datos guardados en: {csv_path}")

    return x_list, y_list, T_list

def plot_equilibrium_curve(x_list, y_list):
    """Genera y muestra un gráfico de la curva de equilibrio."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib no está instalado. Instala con: pip install matplotlib")
        return

    plt.figure(figsize=(8, 6))
    plt.plot(x_list, y_list, 'b-', linewidth=2, label='Curva de Equilibrio (Ley de Raoult)')
    plt.plot([0, 1], [0, 1], 'k--', label='Línea de 45° (x = y)')
    plt.xlabel('Fracción molar de etanol en LÍQUIDO (x)')
    plt.ylabel('Fracción molar de etanol en VAPOR (y)')
    plt.title('Diagrama de Equilibrio Líquido-Vapor\nSistema Etanol-Agua (Ideal)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.axis('equal')
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    # Guardar la figura
    plot_path = 'data/equilibrium_curve_plot.png'
    plt.savefig(plot_path, dpi=150)
    print(f"✅ Gráfico guardado en: {plot_path}")
    plt.show()
# === BLOQUE PRINCIPAL CORREGIDO (¡La indentación aquí es clave!) ===
if __name__ == "__main__":
    print("=== PRUEBA DEL MÓDULO TERMODINÁMICO ===")
    test1 = test_antoine()
    test2 = test_bubble_temperature()

    if test1 and test2:
        print("\n✅ PRUEBAS BÁSICAS PASADAS. Generando curva de equilibrio...\n")
        # GENERAR Y PLOTEAR LA CURVA
        x_vals, y_vals, T_vals = generate_equilibrium_curve(num_points=21)
        plot_equilibrium_curve(x_vals, y_vals)
        # Mostrar algunos valores clave
        print("\n🔍 Puntos clave de la curva:")
        print("   x      y       T(°C)")
        for x, y, t in zip(x_vals[::4], y_vals[::4], T_vals[::4]):  # Cada 4 puntos
            print(f"  {x:.3f}   {y:.3f}   {t:.2f}")
    else:
        print("\n⚠️  Pruebas básicas fallaron. No se genera la curva.")
