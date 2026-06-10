import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo

# =====================================================================
# 1. DATA LOADING AND PROCESSING
# =====================================================================
print("--- Starting data processing ---")
# Load the dataframe (Ensure 'beta_df.csv' is in your working directory)
csv_path = 'beta_df.csv' 
try:
    beta_df = pd.read_csv(csv_path)
except FileNotFoundError:
    # Dummy data in case the file does not exist locally to avoid errors
    print(f"File {csv_path} not found. Creating a dummy DataFrame...")
    # Note: 'Falla', 'Rele', 'Curva', 'Distancia' are kept in Spanish to match the CSV column headers
    data = {'Falla': ['F1']*12, 'Rele': ['R1','R1','R2','R2','R3','R3']*2, 
            'Curva': ['STI','SI','STI','SI','STI','SI']*2, 
            'Distancia': [0.1]*6 + [0.2]*6, 
            'Beta': [1.1, 6.2, 0.66, 3.8, 0.66, 3.8, 1.12, 6.3, 0.67, 3.86, 0.67, 3.86]}
    beta_df = pd.DataFrame(data)

# Filter out negative Beta values
filtered_df = beta_df[beta_df['Beta'] >= 0]

# System Sets Definition
R = ['R1', 'R2', 'R3']
C = ['STI', 'SI'] # Add 'VI', 'EI' if they exist in your actual CSV dataset
P = [('R2', 'R1'), ('R3', 'R1'), ('R3', 'R2')] # (Principal relay i, Backup relay j)
F = 'F1' # Target fault for coordination

# Dictionaries to store extracted parameters
k1_dict = {}
k2_dict = {}
beta0_dict = {}  # Nominal (mean) value of beta_jq
betaL_dict = {}  # Uncertainty limit (e.g., maximum absolute deviation)
beta_obj_dict = {} # Mean betas for the objective function

# 2. EXTRACTION OF k1, k2 AND NOMINAL PARAMETERS
for i, j in P:
    for c in C:     # Principal Curve
        for q in C: # Backup Curve
            
            # Filter DataFrames (using exact CSV column names: 'Rele', 'Curva', 'Falla')
            df_prin = filtered_df[(filtered_df['Rele'] == i) & (filtered_df['Curva'] == c) & (filtered_df['Falla'] == F)]
            df_back = filtered_df[(filtered_df['Rele'] == j) & (filtered_df['Curva'] == q) & (filtered_df['Falla'] == F)]
            
            # Align data points by distance ('Distancia')
            df_merged = pd.merge(df_prin, df_back, on='Distancia', suffixes=('_prin', '_back')).sort_values(by='Distancia')
            
            y = df_merged['Beta_prin'].to_numpy() # Principal
            x = df_merged['Beta_back'].to_numpy() # Backup
            
            # Linear interpolation (y = k2 * x + k1)
            if len(x) >= 2:
                k2, k1 = np.polyfit(x, y, 1)
            else:
                k2, k1 = 1.0, 0.0 # Default values if not enough data points exist
                
            k1_dict[(i, j, q, c)] = k1
            k2_dict[(i, j, q, c)] = k2
            
            # Extract nominal and limit bounds for the backup curve (q) if not already extracted
            if (j, q) not in beta0_dict:
                if len(x) > 0:
                    b0 = np.mean(x)
                    # betaL derived from the readings: maximum absolute deviation from the nominal mean
                    bl = np.max(np.abs(x - b0))
                    
                    # Minimum safety margin in case all measured betas are identical
                    if bl == 0:
                        bl = b0 * 0.01 
                else:
                    b0 = 1.0
                    bl = 0.1
                
                beta0_dict[(j, q)] = b0
                betaL_dict[(j, q)] = bl
                
# Extract mean betas for the objective function (sum of beta_ic * y_ic)
for i in R:
    for c in C:
        df_obj = filtered_df[(filtered_df['Rele'] == i) & (filtered_df['Curva'] == c)]
        beta_obj_dict[(i, c)] = df_obj['Beta'].mean() if not df_obj.empty else 1.0

# =====================================================================
# 3. PYOMO ROBUST MODEL CONSTRUCTION
# =====================================================================
print("--- Building Robust Model in Pyomo ---")

model = pyo.ConcreteModel(name="Robust_Coordination_V2")

# --- Sets ---
model.R = pyo.Set(initialize=R)
model.C = pyo.Set(initialize=C)
model.P = pyo.Set(dimen=2, initialize=P) # Pairs (Principal, Backup)

# --- Parameters ---
model.CTI = pyo.Param(initialize=0.2)
model.M   = pyo.Param(initialize=1000.0) # Big-M constant
model.y_lb = pyo.Param(initialize=0.0005)
model.y_ub = pyo.Param(initialize=1.2)

# C_c Parameter (Standard IEC/IEEE constants, 0 for STI and SI)
C_index = {"STI": 0.0, "SI": 0.0, "VI": 0.0, "EI": 0.0} 
def c_param_init(model, c):
    return C_index.get(c, 0.0)
model.C_param = pyo.Param(model.C, initialize=c_param_init)

# Dictionaries passed as Pyomo parameters
model.k1    = pyo.Param(model.P, model.C, model.C, initialize=k1_dict)
model.k2    = pyo.Param(model.P, model.C, model.C, initialize=k2_dict)
model.beta0 = pyo.Param(model.R, model.C, initialize=beta0_dict, default=1.0)
model.betaL = pyo.Param(model.R, model.C, initialize=betaL_dict, default=0.1)
model.beta_obj = pyo.Param(model.R, model.C, initialize=beta_obj_dict)

# --- Variables ---
# y_ic: Continuous TMS (Time Multiplier Setting)
model.y = pyo.Var(model.R, model.C, domain=pyo.NonNegativeReals)
# x_ic: Binary Curve Selection
model.x = pyo.Var(model.R, model.C, domain=pyo.Binary)
# z_{i,j,q,c}: Robust auxiliary variable (Absolute value representation)
model.z = pyo.Var(model.P, model.C, model.C, domain=pyo.NonNegativeReals)

# --- Objective Function ---
# minimize sum( beta_fic * y_ic + x_ic * C_c )
def obj_rule(model):
    return sum(model.beta_obj[i, c] * model.y[i, c] + model.x[i, c] * model.C_param[c] 
               for i in model.R for c in model.C)
model.objective = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

# --- Constraints ---

# 1. Single curve selection per relay
def single_curve_rule(model, i):
    return sum(model.x[i, c] for c in model.C) == 1
model.single_curve = pyo.Constraint(model.R, rule=single_curve_rule)

# 2. TMS Bounds (Activated by x_ic binary variable)
def tms_lower_rule(model, i, c):
    return model.y[i, c] >= model.y_lb * model.x[i, c]
model.tms_lower = pyo.Constraint(model.R, model.C, rule=tms_lower_rule)

def tms_upper_rule(model, i, c):
    return model.y[i, c] <= model.y_ub * model.x[i, c]
model.tms_upper = pyo.Constraint(model.R, model.C, rule=tms_upper_rule)

# 3. Robust Constraints (Robust Counterpart - RC)
# i: Principal, j: Backup, c: Principal Curve, q: Backup Curve

# Base Equation (Nominal + z <= M(2 - x - x))
def rc_base_rule(model, i, j, q, c):
    nominal_part = (model.k1[i,j,q,c] * model.y[i,c] + 
                    model.k2[i,j,q,c] * model.beta0[j,q] * model.y[i,c] - 
                    model.beta0[j,q] * model.y[j,q] + 
                    model.C_param[c] - model.C_param[q] + model.CTI)
    
    return nominal_part + model.z[i,j,q,c] <= model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_base = pyo.Constraint(model.P, model.C, model.C, rule=rc_base_rule)

# Absolute Value Upper Bound (z >= Argument)
def rc_z_pos_rule(model, i, j, q, c):
    uncertainty = model.k2[i,j,q,c] * model.betaL[j,q] * model.y[i,c] - model.betaL[j,q] * model.y[j,q]
    return model.z[i,j,q,c] >= uncertainty - model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_z_pos = pyo.Constraint(model.P, model.C, model.C, rule=rc_z_pos_rule)

# Absolute Value Lower Bound (z >= -Argument)
def rc_z_neg_rule(model, i, j, q, c):
    uncertainty = model.k2[i,j,q,c] * model.betaL[j,q] * model.y[i,c] - model.betaL[j,q] * model.y[j,q]
    return model.z[i,j,q,c] >= -uncertainty - model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_z_neg = pyo.Constraint(model.P, model.C, model.C, rule=rc_z_neg_rule)

# =====================================================================
# 4. MODEL RESOLUTION
# =====================================================================
print("--- Starting Optimization ---")
try:
    # WARNING: Replace the path below with the exact directory where
    # you saved the highs.exe file.
    highs_path = r'D:\Programas\HiGHS\bin\highs.exe'
    
    # Calls the executable directly (Safe against Segmentation Faults)
    solver = pyo.SolverFactory('highs', executable=highs_path)
    
    results = solver.solve(model, tee=True)
    
    print("\nOptimization Status:", results.solver.status)
    print("Termination Condition:", results.solver.termination_condition)
    
    print("\n--- Optimal Results ---")
    for i in model.R:
        for c in model.C:
            if pyo.value(model.x[i, c]) > 0.5: # If the curve was selected
                print(f"Relay {i} -> Selected Curve: {c} | TMS (y) = {pyo.value(model.y[i, c]):.4f}")

except Exception as e:
    print(f"\nCould not solve the model.")
    print(f"Make sure to define the correct path ('executable=') pointing to the highs.exe file.")
    print(f"Detailed Error: {e}")