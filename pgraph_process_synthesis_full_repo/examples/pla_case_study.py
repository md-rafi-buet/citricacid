import os
from datetime import datetime

from pgraph.core import Material, Operation, StructuralModel


def run_example():
    print("=== P-Graph Chemical Process System Framework ===")

    # ---------------------------------------------------------
    # 1. Define Materials (Chemicals, Intermediates, Products)
    # ---------------------------------------------------------
    corn = Material("Corn")
    cane = Material("Sugarcane")
    glucose = Material("Glucose")
    lactic_acid = Material("Lactic Acid")
    lactide = Material("Lactide")
    pla = Material("PLA (Product)")
    ethanol = Material("Ethanol (Waste)")
    catalyst = Material("Catalyst")

    # ---------------------------------------------------------
    # 2. Define Operations (Chemical Processes)
    # ---------------------------------------------------------
    # Pathway A start: Extracting glucose from Corn
    op1 = Operation("Corn Milling", m_in={corn}, m_out={glucose})

    # Pathway B start: Extracting glucose from Sugarcane
    op2 = Operation("Cane Crushing", m_in={cane}, m_out={glucose})

    # Shared Intermediate step: Fermenting glucose into Lactic Acid
    op3 = Operation("Fermentation", m_in={glucose}, m_out={lactic_acid})

    # Pathway Option 1: Convert Lactic Acid to Lactide, then to PLA (Requires Catalyst)
    op4 = Operation("Lactide Synthesis", m_in={lactic_acid, catalyst}, m_out={lactide})
    op5 = Operation("Ring-Opening Polymerization", m_in={lactide}, m_out={pla})

    # Pathway Option 2: Direct conversion to PLA
    op6 = Operation("Direct Polycondensation", m_in={lactic_acid}, m_out={pla})

    # Distraction/Dead-end: A process making Ethanol, which we don't need for PLA
    op7 = Operation("Ethanol Fermentation", m_in={glucose}, m_out={ethanol})

    # ---------------------------------------------------------
    # 3. Setup the P-Graph Structural Model
    # ---------------------------------------------------------
    P = {pla}  # Our Target Product
    R = {corn, cane}  # Our assumed raw materials (Notice we FORGOT the Catalyst!)
    O = {op1, op2, op3, op4, op5, op6, op7}

    print(f"\n[INFO] Initial Target Product: {[m.name for m in P]}")
    print(f"[INFO] Initial Raw Materials: {[m.name for m in R]}")

    # Initialize the model (This automatically runs Raw Material Augmentation)
    model = StructuralModel(P, R, O)

    print(f"[SUCCESS] Augmented Raw Materials: {[m.name for m in model.R]}")
    if catalyst in model.R:
        print("   -> Notice how 'Catalyst' was automatically found and added!")

    # ---------------------------------------------------------
    # 4. Generate Maximal Structure (MSG)
    # ---------------------------------------------------------
    ms = model.generate_maximal_structure()

    print(f"\n[INFO] Original Operations Count: {len(O)}")
    print(f"[SUCCESS] Maximal Structure Operations Count: {len(ms.o)}")
    if op7 not in ms.o:
        print("   -> Notice how 'Ethanol Fermentation' was pruned out as a dead-end!")

    # ---------------------------------------------------------
    # 5. Generate Solution Structures (SSG - Pathways Only)
    # ---------------------------------------------------------
    # Setting pathways_only=True ensures we only get irreducible chemical flowsheets!
    pathways = model.generate_solution_structures(pathways_only=True)

    print(f"\n[SUCCESS] Found {len(pathways)} distinct, irreducible chemical pathways!")

    # ---------------------------------------------------------
    # 6. Export Visualizations using GraphViz
    # ---------------------------------------------------------
    output_folder = os.path.join("graphs", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(output_folder, exist_ok=True)

    # Export Maximal Structure
    ms.write_png_pydot(os.path.join(output_folder, '0_maximal_structure.png'))

    # Export individual pathways
    for i, path in enumerate(pathways, 1):
        filename = os.path.join(output_folder, f'pathway_{i}.png')
        path.write_png_pydot(filename)

        # Print out the recipe for each pathway
        print(f"\n--- Pathway {i} ---")
        print(f"   Operations: {[o.name for o in path.o]}")
        print(f"   Required Inputs: {[m.name for m in path.m if m in model.R]}")

    print(f"\n[INFO] Done! Graphs have been saved to the '{output_folder}' directory.")
    print("Please check the images to verify the flowsheets visually.")

if __name__ == "__main__":
    run_example()
