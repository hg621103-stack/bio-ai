
class BioprocessChecker:
    def __init__(self, substrate="Glucose", biomass="CH1.8O0.5N0.2"):
        self.gamma_s = 4.0  
        self.gamma_x = 4.2 

    def check_fermentation(self, s_in, x_out, p_out, co2_out, gen_type):
        carbon_in = s_in
        carbon_out = x_out + p_out + co2_out
        
        if carbon_in == 0:
            return {"status": "ERROR", "msg": "Substrate input cannot be zero."}
            
        recovery = (carbon_out / carbon_in) * 100
        status = "PASS" if 95 <= recovery <= 105 else "FAIL"
        
        return {
            "recovery": round(recovery, 2),
            "status": status,
            "data": {
                "Substrate_In": s_in,
                "Biomass_Out": x_out,
                "CO2_Out": co2_out,
                "Generation_Mode": gen_type.lower()
            }
        }

def get_expert_reasoning(report):
    """An offline rule-based system that replaces the AI API."""
    recovery = report['recovery']
    mode = report['data']['Generation_Mode']
    
    explanation = "### BIOCHEMICAL DIAGNOSTIC REPORT ###\n"
    
    if recovery < 95:
        explanation += f"Error: Missing Carbon ({recovery}% Recovery). Carbon has been lost from the system.\n\n"
        
        if "1-to-4" in mode or "multiple" in mode:
            explanation += (
                "DIAGNOSIS (1-to-4 Fission):\n"
                "- High ATP Demand: Synthesizing four cells simultaneously requires massive ATP.\n"
                "- Hidden Respiration: You are likely underestimating CO2 evolution. The cells "
                "are oxidizing substrate purely for maintenance energy, not biomass.\n"
                "- Overflow Metabolism: The glycolysis rate is likely outpacing the TCA cycle. "
                "Check the broth for unmeasured secondary metabolites like Acetate or Ethanol."
            )
        else:
            explanation += (
                "DIAGNOSIS (Standard Growth):\n"
                "- Check for unmeasured volatile products stripping out in the off-gas.\n"
                "- Verify if secondary organic acids (lactate, formate) are accumulating in the broth."
            )
            
    elif recovery > 105:
        explanation += f"Error: Excess Carbon ({recovery}% Recovery). Matter cannot be created.\n\n"
        explanation += (
            "DIAGNOSIS:\n"
            "- Measurement Error: Substrate concentration might have been calculated incorrectly.\n"
            "- Evaporation: If the reactor volume decreased due to evaporation, the concentration "
            "of outputs will falsely appear higher than theoretical maximums.\n"
            "- Biomass Composition: The standard assumption of CH1.8O0.5N0.2 may be incorrect for this strain."
        )
        
    return explanation

if __name__ == "__main__":
    print("\n==================================================")
    print("  EXPERT MASS BALANCE CHECKER (NIT JALANDHAR)")
    print("==================================================\n")
    
    try:
        print("Please enter your fermentation data (in C-moles):")
        s_in = float(input("  -> Substrate Input (e.g., 10): "))
        x_out = float(input("  -> Biomass Output (e.g., 4.5): "))
        p_out = float(input("  -> Product Output (e.g., 0): "))
        co2_out = float(input("  -> CO2 Output (e.g., 2): "))
        
        print("\nWhat is the cell division mode?")
        gen_type = input("  -> Mode (e.g., 'Binary', '1-to-4'): ")
        
        print("\n[System] Calculating mass balance...")
        checker = BioprocessChecker()
        my_data = checker.check_fermentation(s_in, x_out, p_out, co2_out, gen_type)

        if my_data.get("status") == "ERROR":
            print(f"\n[ERROR] {my_data['msg']}")
        else:
            print("\n--- TECHNICAL REPORT ---")
            print(f"Status: {my_data['status']}")
            print(f"Carbon Recovery: {my_data['recovery']}%\n")

            if my_data['status'] == "FAIL":
                print(get_expert_reasoning(my_data))
            else:
                print("--- VERDICT ---")
                print("Excellent work! Your carbon atoms are conserved, and the mass balance is valid.")
            
    except ValueError:
        print("\n[ERROR] Invalid input! Please enter numbers only for the C-moles.")
