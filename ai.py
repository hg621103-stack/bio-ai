from google import genai

# 1. AI CONFIGURATION 
# Make sure your API key is correct here!
API_KEY = "AIzaSyAIBJZsCRS5giHFPT_VpeCwHhvEmJyihDg"
client = genai.Client(api_key=API_KEY)

class BioprocessChecker:
    def __init__(self, substrate="Glucose", biomass="CH1.8O0.5N0.2"):
        self.gamma_s = 4.0  # Glucose
        self.gamma_x = 4.2  # Biomass

    def check_fermentation(self, s_in, x_out, p_out, co2_out, gen_type):
        # Carbon Balance logic
        carbon_in = s_in
        carbon_out = x_out + p_out + co2_out
        recovery = (carbon_out / carbon_in) * 100
        
        # 95% to 105% is considered a 'PASS' in lab conditions
        status = "PASS" if 95 <= recovery <= 105 else "FAIL"
        
        return {
            "recovery": round(recovery, 2),
            "status": status,
            "data": {
                "Substrate_In": s_in,
                "Biomass_Out": x_out,
                "CO2_Out": co2_out,
                "Generation_Mode": gen_type
            }
        }

def get_ai_reasoning(report):
    """Sends the failed mass balance to the AI for troubleshooting."""
    prompt = f"""
    You are a Bioprocess Expert. A Biotechnology student at NIT Jalandhar is checking a mass balance.
    
    SCENARIO DATA:
    - Recovery: {report['recovery']}%
    - Mode: {report['data']['Generation_Mode']}
    - Input: {report['data']['Substrate_In']} C-moles
    - Output: {report['data']['Biomass_Out']} (Biomass) + {report['data']['CO2_Out']} (CO2)
    
    TASK:
    If the status is FAIL, explain the biochemical error. 
    Focus on how the specific Generation Mode ({report['data']['Generation_Mode']}) affects metabolism. 
    Explain why they likely have missing or excess Carbon (e.g., unmeasured secondary metabolites 
    like acetate or ethanol, or high CO2 evolution for ATP maintenance).
    Keep the explanation technical but supportive.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI connection error: {str(e)}"

# --- INTERACTIVE TERMINAL APP ---
if __name__ == "__main__":
    print("\n==================================================")
    print("  AI-POWERED MASS BALANCE CHECKER (NIT JALANDHAR)")
    print("==================================================\n")
    
    try:
        # Prompting the user for inputs
        print("Please enter your fermentation data (in C-moles):")
        s_in = float(input("  -> Substrate Input (e.g., 10): "))
        x_out = float(input("  -> Biomass Output (e.g., 4.5): "))
        p_out = float(input("  -> Product Output (e.g., 0): "))
        co2_out = float(input("  -> CO2 Output (e.g., 2): "))
        
        print("\nWhat is the cell division mode?")
        gen_type = input("  -> Mode (e.g., 'Binary', '1-to-4 multiple fission'): ")
        
        # Run the calculations
        print("\n[System] Calculating mass balance...")
        checker = BioprocessChecker()
        my_data = checker.check_fermentation(s_in, x_out, p_out, co2_out, gen_type)

        # Output the mathematical report
        print("\n--- TECHNICAL REPORT ---")
        print(f"Status: {my_data['status']}")
        print(f"Carbon Recovery: {my_data['recovery']}%\n")

        # Trigger AI if the balance fails
        if my_data['status'] == "FAIL":
            print("--- AI BIOCHEMICAL TROUBLESHOOTING ---")
            print("[System] Consulting AI Expert... please wait...\n")
            print(get_ai_reasoning(my_data))
        else:
            print("--- AI VERDICT ---")
            print("Excellent work! Your carbon atoms are conserved, and the mass balance is valid.")
            
    except ValueError:
        print("\n[ERROR] Invalid input! Please enter numbers only for the C-moles.")