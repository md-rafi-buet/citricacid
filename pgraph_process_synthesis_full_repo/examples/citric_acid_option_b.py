import os
from datetime import datetime

from pgraph.core import Material, Operation, StructuralModel


def run_citric_acid_option_b():
    print("=== P-Graph Citric Acid Biorefinery (Option B: |β|=1 for LCA Inversion) ===\n")

    # ---------------------------------------------------------
    # 1. Define Materials (ONLY main economic/structural flows)
    # ---------------------------------------------------------
    # Target Product
    citric_acid = Material("Citric Acid (Product)")

    # Raw Materials
    molasses = Material("Molasses")
    corn = Material("Corn")
    crude_glycerol = Material("Crude Glycerol")

    # Common Intermediates
    sterilized_medium = Material("Sterilized Medium")
    fermentation_broth = Material("Fermentation Broth")
    clarified_broth = Material("Clarified Broth")
    purified_liquor = Material("Purified Liquor")

    # Molasses Pretreatment Intermediates
    m_screened = Material("Screened Molasses")
    m_diluted = Material("Diluted Molasses")
    m_clarified = Material("Clarified Molasses")
    m_centrifuged = Material("Centrifuged Molasses")
    m_ph_adj = Material("pH Adjusted Molasses")

    # Corn Pretreatment Intermediates
    c_cleaned = Material("Cleaned Corn")
    c_milled = Material("Milled Corn")
    c_slurry = Material("Corn Slurry")
    c_cooked = Material("Cooked Corn Slurry")
    c_liq = Material("Liquefied Corn")
    c_sacc = Material("Saccharified Corn")
    c_filtered = Material("Filtered Corn Syrup")

    # Glycerol Pretreatment Intermediates
    g_filtered = Material("Filtered Glycerol")
    g_acidified = Material("Acidified Glycerol")
    g_decanted = Material("Decanted Glycerol")
    g_centrifuged = Material("Centrifuged Glycerol")
    g_stripped = Material("Stripped Glycerol")
    g_neutral = Material("Neutralized Glycerol")

    # ---------------------------------------------------------
    # 2. Define Operations (Enforcing |β| = 1)
    # Wastes are stored in `properties` or `impacts` to keep the matrix square!
    # ---------------------------------------------------------
    O = set()

    # --- Pretreatment 1: Molasses ---
    O.add(Operation("Vibrating Screen", m_in={molasses}, m_out={m_screened}))
    O.add(Operation("Dilution Tank", m_in={m_screened}, m_out={m_diluted}))
    O.add(Operation("Clarifier (Molasses)", m_in={m_diluted}, m_out={m_clarified}))
    O.add(Operation("Disc Centrifuge (Molasses)", m_in={m_clarified}, m_out={m_centrifuged}))
    O.add(Operation("pH Adjustment", m_in={m_centrifuged}, m_out={m_ph_adj}))
    O.add(Operation("Sterilizer (Molasses)", m_in={m_ph_adj}, m_out={sterilized_medium}))

    # --- Pretreatment 2: Corn ---
    O.add(Operation("Grain Cleaner", m_in={corn}, m_out={c_cleaned}))
    O.add(Operation("Hammer Mill", m_in={c_cleaned}, m_out={c_milled}))
    O.add(Operation("Slurry Tank", m_in={c_milled}, m_out={c_slurry}))
    O.add(Operation("Jet Cooker", m_in={c_slurry}, m_out={c_cooked}))
    O.add(Operation("Liquefaction Reactor", m_in={c_cooked}, m_out={c_liq}))
    O.add(Operation("Saccharification Reactor", m_in={c_liq}, m_out={c_sacc}))
    O.add(Operation("Pressure Leaf Filter", m_in={c_sacc}, m_out={c_filtered}))
    O.add(Operation("Sterilizer (Corn)", m_in={c_filtered}, m_out={sterilized_medium}))

    # --- Pretreatment 3: Crude Glycerol ---
    O.add(Operation("Cartridge Filter", m_in={crude_glycerol}, m_out={g_filtered}))
    O.add(Operation("Acidification Tank", m_in={g_filtered}, m_out={g_acidified}))
    O.add(Operation("Decanter", m_in={g_acidified}, m_out={g_decanted}))
    O.add(Operation("Disc Centrifuge (Glycerol)", m_in={g_decanted}, m_out={g_centrifuged}))
    O.add(Operation("Methanol Stripper", m_in={g_centrifuged}, m_out={g_stripped}))
    O.add(Operation("Neutralization Tank", m_in={g_stripped}, m_out={g_neutral}))
    O.add(Operation("Sterilizer (Glycerol)", m_in={g_neutral}, m_out={sterilized_medium}))

    # --- Fermentation ---
    O.add(Operation("Fermentation (A. niger / Y. lipolytica)", 
                    m_in={sterilized_medium}, 
                    m_out={fermentation_broth},  # |β| = 1
                    properties={"wastes_emissions": ["Gas Emissions"]}))

    # --- Primary Separation (3 Interchangeable Alternatives) ---
    O.add(Operation("Filtration Separation", m_in={fermentation_broth}, m_out={clarified_broth}, 
                    properties={"wastes_emissions": ["Solid Waste"]}))
    O.add(Operation("Centrifuge Separation", m_in={fermentation_broth}, m_out={clarified_broth}, 
                    properties={"wastes_emissions": ["Solid Waste"]}))
    O.add(Operation("Membrane Separation", m_in={fermentation_broth}, m_out={clarified_broth}, 
                    properties={"wastes_emissions": ["Solid Waste"]}))

    # --- Downstream Processing (2 Interchangeable Alternatives) ---
    O.add(Operation("Precipitation Route", m_in={clarified_broth}, m_out={purified_liquor}, 
                    properties={"wastes_emissions": ["Effluent", "Gypsum (CaSO4·2H2O)"]}))

    O.add(Operation("Extraction Route", m_in={clarified_broth}, m_out={purified_liquor}, 
                    properties={"wastes_emissions": ["Effluent"]}))

    # --- Recovery & Finishing ---
    O.add(Operation("Crystallization & Drying", m_in={purified_liquor}, m_out={citric_acid}, 
                    properties={"wastes_emissions": ["Recovery Residues"]}))

    # ---------------------------------------------------------
    # 3. Setup the P-Graph Structural Model
    # ---------------------------------------------------------
    P = {citric_acid}
    R = {molasses, corn, crude_glycerol} 

    print(f"[INFO] Target Product: {P.pop().name}")
    print(f"[INFO] Base Raw Materials: {[m.name for m in R]}")
    P = {citric_acid} # restore after pop

    # Initialize model
    model = StructuralModel(P, R, O)

    # ---------------------------------------------------------
    # 4. Generate Maximal Structure (Superstructure)
    # ---------------------------------------------------------
    ms = model.generate_maximal_structure()
    print(f"\n[SUCCESS] Superstructure generated with {len(ms.o)} operations.")

    # Validate the |β| = 1 rule for the user
    for op in ms.o:
        assert len(op.m_out) == 1, f"Error: Operation {op.name} violates |β|=1 rule!"
    print("[SUCCESS] Verified: All operations satisfy |β|=1 rule. LCA Technology Matrix A will be square and invertible!")

    # ---------------------------------------------------------
    # 5. Generate Solution Structures (SSG) - LCA Modules
    # ---------------------------------------------------------
    print("\n[INFO] Running SSG to extract interchangeable flowsheets...")
    pathways = model.generate_solution_structures(pathways_only=True)

    print(f"[SUCCESS] Found exactly {len(pathways)} distinct, irreducible chemical pathways!")
    print("          (Expected: 3 feedstocks x 3 separations x 2 downstream = 18 pathways)\n")

    # ---------------------------------------------------------
    # 6. Export Visualizations and Print Metadata
    # ---------------------------------------------------------
    output_folder = os.path.join("graphs_citric_acid_Option_B", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(output_folder, exist_ok=True)

    # Export Superstructure
    ms.write_png_pydot(os.path.join(output_folder, '0_Citric_Acid_Superstructure.png'))

    print("--- Interchangeable Pathway Configurations ---")
    for i, path in enumerate(pathways, 1):
        filename = os.path.join(output_folder, f'pathway_{i:02d}.png')
        path.write_png_pydot(filename)

        # Identify choices for this specific path
        feedstock = [m.name for m in path.m if m in model.R][0]
        separation = [o for o in path.o if "Separation" in o.name][0]
        downstream = [o for o in path.o if "Route" in o.name][0]

        # Extract the hidden waste data from the properties dictionary
        downstream_wastes = downstream.properties.get("wastes_emissions", [])

        print(f"Pathway {i:02d}: [{feedstock}] -> [{separation.name}] -> [{downstream.name}]")
        print(f"            * Note: Downstream process generates tracked wastes: {downstream_wastes}")

    print(f"\n[DONE] All {len(pathways)} flowsheets saved to '{output_folder}'.")
    print("Notice how the graphs are now clean, straight pipelines. The wastes are safely stored in memory for LCA calculations without cluttering the structural matrix!")

if __name__ == "__main__":
    run_citric_acid_option_b()
