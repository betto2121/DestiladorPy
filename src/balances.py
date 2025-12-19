# src/balances.py
"""
Módulo 1: Balances Globales de Materia.
Convierte la capacidad de producción en flujos para el diseño.
"""
import json

def calculate_mass_flows(design_specs_path='data/design_specs.json'):
    """Calcula los flujos F (alimentación), D (destilado), B (fondos)."""
    
    # 1. Cargar las especificaciones desde el JSON
    with open(design_specs_path, 'r') as f:
        specs = json.load(f)
    
    basis = specs['basis']
    
    # 2. Extraer parámetros
    D_kg_per_day = basis['product_rate_L_per_day'] * basis['density_ethanol_kg_per_L']
    xD = basis['distillate_composition_xD']
    xF = basis['feed_composition_xF']
    xB = basis['bottoms_composition_xB']
    
    # 3. Resolver el sistema de ecuaciones lineales
    # De:  F = D + B
    #      F*xF = D*xD + B*xB
    # Se deriva:
    D = D_kg_per_day  # Destilado [kg/día]
    B = D * (xD - xF) / (xF - xB)  # Fondos [kg/día]
    F = D + B  # Alimentación [kg/día]
    
    # 4. Convertir a kg/h (unidad más útil para diseño)
    hours_per_day = 24
    results = {
        'F_kg_per_h': round(F / hours_per_day, 2),
        'D_kg_per_h': round(D / hours_per_day, 2),
        'B_kg_per_h': round(B / hours_per_day, 2),
        'F_kg_per_day': round(F, 2),
        'D_kg_per_day': round(D, 2),
        'B_kg_per_day': round(B, 2),
        'feed_composition_xF': xF,
        'distillate_composition_xD': xD,
        'bottoms_composition_xB': xB
    }
    return results

if __name__ == "__main__":
    # Ejecutar y mostrar resultados
    flows = calculate_mass_flows()
    print("=== BALANCES GLOBALES DE MATERIA ===")
    print(f"Alimentación (F): {flows['F_kg_per_h']} kg/h ({flows['F_kg_per_day']:,.0f} kg/día)")
    print(f"Destilado (D):    {flows['D_kg_per_h']} kg/h ({flows['D_kg_per_day']:,.0f} kg/día)")
    print(f"Fondos (B):       {flows['B_kg_per_h']} kg/h ({flows['B_kg_per_day']:,.0f} kg/día)")
    print(f"\nComposiciones:")
    print(f"  xF (Alimentación):  {flows['feed_composition_xF']}")
    print(f"  xD (Destilado):     {flows['distillate_composition_xD']}")
    print(f"  xB (Fondos):        {flows['bottoms_composition_xB']}")
