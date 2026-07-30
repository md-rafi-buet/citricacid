import os
from datetime import datetime
from pgraph import Material, Operation, StructuralModel

def run_citric_acid_option_a():
    print("=== P-Graph Citric Acid Biorefinery (Option A: Explicit Multifunctional Flows) ===\n")

    # ---------------------------------------------------------
    # 1. Define Materials
    # ---------------------------------------------------------
    # --- Target Product ---
    packed_citric_acid = Material("Packed Citric Acid")

    # --- Feedstocks ---
    molasses = Material("Molasses")
    corn = Material("Corn")
    crude_glycerol = Material("Crude Glycerol")

    # --- Auxiliary Inputs (Will be auto-augmented by the framework) ---
    water = Material("Water")
    acid = Material("Acid (pH/Acidulation)")
    alkali = Material("Alkali (pH/Neutralization)")
    milk_of_lime = Material("Milk of Lime")
    enzymes = Material("Enzymes")

    # --- Shared Convergence Intermediate ---
    # All 3 pretreatment lines will ultimately produce this to feed the fermenter
    sterilized_medium = Material("Sterilized Medium")

    # =========================================================
    # A. Molasses Line Intermediates & Wastes
    # =========================================================
    m_screened = Material("Screened Molasses")
    m_diluted = Material("Diluted Molasses")
    m_clarified = Material("Clarified Molasses")
    m_centrifuged = Material("Centrifuged Molasses")
    m_ph_adj = Material("pH Adjusted Molasses")
    m_carbon_filt = Material("Carbon Filtered Molasses")
    m_ion_ex = Material("Ion-Exchanged Molasses")
    
    # Molasses Wastes
    screening_rejects = Material("Screening Rejects")
    clarifier_sludge_m = Material("Clarifier Sludge (Molasses)")
    centrifuge_sludge_m = Material("Centrifuge Sludge (Molasses)")
    spent_carbon_m = Material("Spent Carbon (Molasses)")
    ion_ex_waste_m = Material("Ion-Exchange Regenerant Waste")

    # =========================================================
    # B. Corn / Starch Line Intermediates & Wastes
    # =========================================================
    c_cleaned = Material("Cleaned Corn")
    c_milled = Material("Milled Corn Meal")
    c_slurry = Material("Starch Slurry")
    c_gelatinized = Material("Gelatinized Slurry")
    c_liquefied = Material("Liquefied Mash")
    c_saccharified = Material("Saccharified Liquor")
    c_clarified = Material("Clarified Glucose Liquor")
    
    # Corn Wastes
    husk_fiber_bran = Material("Husk / Fiber / Bran")
    germ_oil_fraction = Material("Germ / Oil Fraction")
    insoluble_solids = Material("Insoluble Solids")
    steam_condensate = Material("Steam Condensate")

    # =========================================================
    # C. Crude Glycerol Line Intermediates & Wastes
    # =========================================================
    g_filtered = Material("Filtered Glycerol")
    g_acidified = Material("Acidified Glycerol")
    g_phase_sep = Material("Phase-Separated Glycerol")
    g_stripped = Material("Methanol-Stripped Glycerol")
    g_neutral = Material("Neutralized Glycerol")
    g_polished = Material("Polished Glycerol")
    
    # Glycerol Wastes
    suspended_solids = Material("Suspended Solids")
    soap_layer = Material("Soap Layer")
    ffa_layer = Material("Free Fatty Acid Layer")
    methanol_condensate = Material("Methanol Vapor / Condensate")
    salt_rich_purge = Material("Salt-Rich Aqueous Purge")

    # =========================================================
    # D. Fermentation & Primary Separation Intermediates & Wastes
    # =========================================================
    fermentation_broth = Material("Fermentation Broth")
    clarified_fermentation_liquor = Material("Clarified Fermentation Liquor")
    
    # Wastes
    co2_off_gas = Material("CO2 Off-Gas")
    biomass_mycelium = Material("Biomass / Mycelial Cake")
    vent_gas_foam = Material("Vent Gas / Foam")
    wash_filtrate = Material("Wash Filtrate")

    # =========================================================
    # E. Downstream Processing (Precipitation) Intermediates & Wastes
    # =========================================================
    calcium_citrate_slurry = Material("Calcium Citrate Slurry")
    calcium_citrate_cake = Material("Calcium Citrate Cake")
    citric_acid_solution = Material("Citric Acid Solution")
    
    # Wastes
    depleted_broth = Material("Mother Liquor / Depleted Broth")
    cake_wash_water = Material("Cake Wash Water")
    gypsum_cake = Material("Gypsum Cake (CaSO4·2H2O)")
    acid_mist = Material("Acid Mist / Vent")

    # =========================================================
    # F. Purification, Recovery, and Finishing Intermediates & Wastes
    # =========================================================
    decolorized_liquor = Material("Decolorized Citric Acid")
    polished_liquor = Material("Polished Citric Acid")
    concentrated_liquor = Material("Concentrated Citric Acid")
    crystal_slurry = Material("Crystal Slurry")
    wet_crystals = Material("Wet Citric Acid Crystals")
    dry_crystals = Material("Dry Citric Acid")
    
    # Wastes
    spent_carbon_d = Material("Spent Activated Carbon (Downstream)")
    resin_effluent = Material("Resin Regeneration Effluent")
    evap_condensate = Material("Evaporator Condensate")
    recycle_mother_liquor = Material("Recycle Mother Liquor / Fines")
    centrifuge_liquor = Material("Centrifuge Mother Liquor")
    dryer_exhaust = Material("Dryer Exhaust Air / Vapor")
    bag_dust = Material("Bag Dust / Off-Spec Fines")

    # ---------------------------------------------------------
    # 2. Define Operations (Explicit Multifunctional Nodes)
    # ---------------------------------------------------------
    O = set()

    # --- Pretreatment A: Molasses ---
    O.add(Operation("Vibrating Screen", m_in={molasses}, m_out={m_screened, screening_rejects}))
    O.add(Operation("Dilution Tank", m_in={m_screened, water}, m_out={m_diluted}))
    O.add(Operation("Clarifier (Molasses)", m_in={m_diluted}, m_out={m_clarified, clarifier_sludge_m}))
    O.add(Operation("Disc-Stack Centrifuge (Molasses)", m_in={m_clarified}, m_out={m_centrifuged, centrifuge_sludge_m}))
    O.add(Operation("pH Adjustment", m_in={m_centrifuged, acid, alkali}, m_out={m_ph_adj}))
    O.add(Operation("Activated Carbon Filter (Molasses)", m_in={m_ph_adj}, m_out={m_carbon_filt, spent_carbon_m}))
    O.add(Operation("Ion-Exchange (Molasses)", m_in={m_carbon_filt}, m_out={m_ion_ex, ion_ex_waste_m}))
    O.add(Operation("Sterilizer (Molasses)", m_in={m_ion_ex}, m_out={sterilized_medium, vent_gas_foam}))

    # --- Pretreatment B: Corn / Starch ---
    O.add(Operation("Grain Cleaner", m_in={corn}, m_out={c_cleaned, husk_fiber_bran}))
    O.add(Operation("Hammer Mill", m_in={c_cleaned}, m_out={c_milled}))
    O.add(Operation("Slurry Tank", m_in={c_milled, water}, m_out={c_slurry}))
    O.add(Operation("Jet Cooker / Gelatinization", m_in={c_slurry}, m_out={c_gelatinized, steam_condensate}))
    O.add(Operation("Liquefaction", m_in={c_gelatinized, enzymes}, m_out={c_liquefied}))
    O.add(Operation("Saccharification", m_in={c_liquefied, enzymes}, m_out={c_saccharified, germ_oil_fraction}))
    O.add(Operation("Clarifier & Filter Press (Corn)", m_in={c_saccharified}, m_out={c_clarified, insoluble_solids}))
    O.add(Operation("Sterilizer (Corn)", m_in={c_clarified}, m_out={sterilized_medium}))

    # --- Pretreatment C: Crude Glycerol ---
    O.add(Operation("Cartridge Filter", m_in={crude_glycerol}, m_out={g_filtered, suspended_solids}))
    O.add(Operation("Acidification Tank", m_in={g_filtered, acid}, m_out={g_acidified}))
    O.add(Operation("Decanter & Centrifuge", m_in={g_acidified}, m_out={g_phase_sep, soap_layer, ffa_layer}))
    O.add(Operation("Methanol Stripper", m_in={g_phase_sep}, m_out={g_stripped, methanol_condensate}))
    O.add(Operation("Neutralization Tank", m_in={g_stripped, alkali}, m_out={g_neutral, salt_rich_purge}))
    O.add(Operation("Carbon & Ion-Ex (Glycerol)", m_in={g_neutral}, m_out={g_polished, spent_carbon_m, ion_ex_waste_m}))
    O.add(Operation("Sterilizer (Glycerol)", m_in={g_polished}, m_out={sterilized_medium}))

    # --- Fermentation ---
    O.add(Operation("Fermentation (A. niger)", 
                    m_in={sterilized_medium}, 
                    m_out={fermentation_broth, biomass_mycelium, co2_off_gas}))

    # --- Primary Separation (2 Alternatives to show Interchangeability) ---
    O.add(Operation("Primary Sep: Rotary Vacuum Filter", 
                    m_in={fermentation_broth, water}, 
                    m_out={clarified_fermentation_liquor, biomass_mycelium, wash_filtrate}))
    O.add(Operation("Primary Sep: Disc-Stack Centrifuge", 
                    m_in={fermentation_broth}, 
                    m_out={clarified_fermentation_liquor, biomass_mycelium}))

    # --- Downstream Processing: Precipitation Route ---
    O.add(Operation("Lime Precipitation Reactor", 
                    m_in={clarified_fermentation_liquor, milk_of_lime}, 
                    m_out={calcium_citrate_slurry, depleted_broth}))
    O.add(Operation("Solid-Liquid Separation (Filter Press)", 
                    m_in={calcium_citrate_slurry, water}, 
                    m_out={calcium_citrate_cake, cake_wash_water}))
    O.add(Operation("Acidulation Tank", 
                    m_in={calcium_citrate_cake, acid}, 
                    m_out={citric_acid_solution, gypsum_cake, acid_mist}))

    # --- Purification, Recovery, and Finishing ---
    O.add(Operation("Decolorization (Activated Carbon)", 
                    m_in={citric_acid_solution}, 
                    m_out={decolorized_liquor, spent_carbon_d}))
    O.add(Operation("Polishing (Ion-Exchange)", 
                    m_in={decolorized_liquor}, 
                    m_out={polished_liquor, resin_effluent}))
    O.add(Operation("Multiple-Effect Evaporator", 
                    m_in={polished_liquor}, 
                    m_out={concentrated_liquor, evap_condensate}))
    O.add(Operation("Vacuum Crystallizer", 
                    m_in={concentrated_liquor}, 
                    m_out={crystal_slurry, recycle_mother_liquor}))
    O.add(Operation("Crystal Centrifuge", 
                    m_in={crystal_slurry, water}, 
                    m_out={wet_crystals, centrifuge_liquor}))
    
    # --- Drying (2 Alternatives to show Interchangeability) ---
    O.add(Operation("Fluidized Bed Dryer", 
                    m_in={wet_crystals}, 
                    m_out={dry_crystals, dryer_exhaust}))
    O.add(Operation("Rotary Dryer", 
                    m_in={wet_crystals}, 
                    m_out={dry_crystals, dryer_exhaust}))

    O.add(Operation("Sieving & Packaging", 
                    m_in={dry_crystals}, 
                    m_out={packed_citric_acid, bag_dust}))

    # ---------------------------------------------------------
    # 3. Setup the P-Graph Structural Model
    # ---------------------------------------------------------
    P = {packed_citric_acid}
    R = {molasses, corn, crude_glycerol} 
    
    # Initialize the Structural Model
    # Note: P-Graph will automatically augment 'water', 'acid', 'alkali', 'enzymes', etc., into the Raw Materials!
    model = StructuralModel(P, R, O)

    print(f"Target Product: {P.pop().name}")
    P = {packed_citric_acid}
    
    print("\n[INFO] Augmented Raw Materials List:")
    for raw_mat in model.R:
        print(f"   - {raw_mat.name}")

    # ---------------------------------------------------------
    # 4. Generate Maximal Structure (Superstructure)
    # ---------------------------------------------------------
    ms = model.generate_maximal_structure()
    print(f"\n[SUCCESS] Superstructure generated with {len(ms.o)} operations and {len(ms.m)} materials.")

    # ---------------------------------------------------------
    # 5. Generate Solution Structures (SSG) - Irreducible Pathways
    # ---------------------------------------------------------
    # pathways_only=True guarantees we get pure chemical flowsheets without messy overlapping combinations
    print("[INFO] Running SSG to extract interchangeable flowsheets...")
    pathways = model.generate_solution_structures(pathways_only=True)
    
    print(f"\n[SUCCESS] Found exactly {len(pathways)} distinct, irreducible chemical pathways!")
    print("          (Logic: 3 Feedstocks x 2 Primary Separations x 1 Downstream Route x 2 Dryers = 12 pathways)\n")

    # ---------------------------------------------------------
    # 6. Export Visualizations using GraphViz
    # ---------------------------------------------------------
    output_folder = os.path.join("graphs_citric_acid_Option_A", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(output_folder, exist_ok=True)
    
    # Export Superstructure
    ms.write_png_pydot(os.path.join(output_folder, '00_Citric_Acid_Superstructure.png'))
    
    # Export individual flowsheets and trace their interchangeable modules
    print("--- Breakdown of Interchangeable Pathways ---")
    for i, path in enumerate(pathways, 1):
        filename = os.path.join(output_folder, f'pathway_{i:02d}.png')
        path.write_png_pydot(filename)
        
        # Determine which specific interchangeable choices were made for this route
        feedstock = [m.name for m in path.m if m in {molasses, corn, crude_glycerol}][0]
        primary_sep = [o.name for o in path.o if "Primary Sep" in o.name][0]
        dryer = [o.name for o in path.o if "Dryer" in o.name][0]
        
        print(f"Pathway {i:02d}: [{feedstock}] -> [{primary_sep}] -> [{dryer}]")

    print(f"\n[DONE] All {len(pathways)} flowsheets and the superstructure have been saved to '{output_folder}'.")
    print("If you open the PNG files, you will explicitly see Wastes (Gypsum, Effluent, etc.) branching out as dead-end circles!")

if __name__ == "__main__":
    run_citric_acid_option_a()