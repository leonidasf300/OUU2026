import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo

# =====================================================================
# 1. CARREGAMENTO E PROCESSAMENTO DE DADOS
# =====================================================================
print("--- Iniciando processamento de dados ---")
# Carregar o dataframe (Certifique-se de que 'beta_df.csv' está no seu ambiente)
csv_path = 'beta_df.csv' 
try:
    beta_df = pd.read_csv(csv_path)
except FileNotFoundError:
    # Dados de teste caso o arquivo não exista localmente para evitar erros
    print(f"Não foi encontrado {csv_path}. Criando um DataFrame de teste...")
    data = {'Falla': ['F1']*12, 'Rele': ['R1','R1','R2','R2','R3','R3']*2, 
            'Curva': ['STI','SI','STI','SI','STI','SI']*2, 
            'Distancia': [0.1]*6 + [0.2]*6, 
            'Beta': [1.1, 6.2, 0.66, 3.8, 0.66, 3.8, 1.12, 6.3, 0.67, 3.86, 0.67, 3.86]}
    beta_df = pd.DataFrame(data)

# Filtrar os valores negativos
df_filtrado = beta_df[beta_df['Beta'] >= 0]

# Definição de Conjuntos do Sistema
R = ['R1', 'R2', 'R3']
C = ['STI', 'SI'] # Adicione 'VI', 'EI' se existirem no seu CSV real
P = [('R2', 'R1'), ('R3', 'R1'), ('R3', 'R2')] # (Principal i, Backup j)
F = 'F1' # Falha alvo para coordenar

# Dicionários para armazenar parâmetros extraídos
k1_dict = {}
k2_dict = {}
beta0_dict = {}  # Valor nominal (médio) de beta_jq
betaL_dict = {}  # Incerteza (ex. desvio máximo)
beta_obj_dict = {} # Betas médios para a função objetivo

# 2. EXTRAÇÃO DE k1, k2 E PARÂMETROS NOMINAIS
for i, j in P:
    for c in C:     # Curva do Principal
        for q in C: # Curva do Backup
            
            # Filtrar DataFrames
            df_prin = df_filtrado[(df_filtrado['Rele'] == i) & (df_filtrado['Curva'] == c) & (df_filtrado['Falla'] == F)]
            df_back = df_filtrado[(df_filtrado['Rele'] == j) & (df_filtrado['Curva'] == q) & (df_filtrado['Falla'] == F)]
            
            # Alinhar por distância
            df_merged = pd.merge(df_prin, df_back, on='Distancia', suffixes=('_prin', '_back')).sort_values(by='Distancia')
            
            y = df_merged['Beta_prin'].to_numpy() # Principal
            x = df_merged['Beta_back'].to_numpy() # Backup
            
            # Interpolação linear (y = k2 * x + k1)
            if len(x) >= 2:
                k2, k1 = np.polyfit(x, y, 1)
            else:
                k2, k1 = 1.0, 0.0 # Valor padrão se não houver dados suficientes
                
            k1_dict[(i, j, q, c)] = k1
            k2_dict[(i, j, q, c)] = k2
            
            # Extrair nominal e limite para o backup (q) se ainda não existir
            if (j, q) not in beta0_dict:
                if len(x) > 0:
                    b0 = np.mean(x)
                    # betaL derivado da leitura: desvio absoluto máximo em relação ao nominal
                    bl = np.max(np.abs(x - b0))
                    
                    # Margem mínima de segurança caso todos os betas medidos sejam idênticos
                    if bl == 0:
                        bl = b0 * 0.01 
                else:
                    b0 = 1.0
                    bl = 0.1
                
                beta0_dict[(j, q)] = b0
                betaL_dict[(j, q)] = bl
                
# Extrair betas médios para a função objetivo (sum beta_ic * y_ic)
for i in R:
    for c in C:
        df_obj = df_filtrado[(df_filtrado['Rele'] == i) & (df_filtrado['Curva'] == c)]
        beta_obj_dict[(i, c)] = df_obj['Beta'].mean() if not df_obj.empty else 1.0

# =====================================================================
# 3. CONSTRUÇÃO DO MODELO NO PYOMO
# =====================================================================
print("--- Construindo Modelo Robusto no Pyomo ---")

model = pyo.ConcreteModel(name="Coordenacao_Robusta_V2")

# --- Sets ---
model.R = pyo.Set(initialize=R)
model.C = pyo.Set(initialize=C)
model.P = pyo.Set(dimen=2, initialize=P) # Pares (Principal, Backup)

# --- Parameters ---
model.CTI = pyo.Param(initialize=0.2)
model.M   = pyo.Param(initialize=1000.0) # Big-M
model.y_lb = pyo.Param(initialize=0.0005)
model.y_ub = pyo.Param(initialize=1.2)

# Parâmetro C_c (Constantes da norma, 0 para STI e SI)
C_index = {"STI": 0.0, "SI": 0.0, "VI": 0.0, "EI": 0.0} 
def c_param_init(model, c):
    return C_index.get(c, 0.0)
model.C_param = pyo.Param(model.C, initialize=c_param_init)

# Dicionários passados como parâmetros do Pyomo
model.k1    = pyo.Param(model.P, model.C, model.C, initialize=k1_dict)
model.k2    = pyo.Param(model.P, model.C, model.C, initialize=k2_dict)
model.beta0 = pyo.Param(model.R, model.C, initialize=beta0_dict, default=1.0)
model.betaL = pyo.Param(model.R, model.C, initialize=betaL_dict, default=0.1)
model.beta_obj = pyo.Param(model.R, model.C, initialize=beta_obj_dict)

# --- Variables ---
# y_ic: TMS (Time Multiplier Setting) contínuo
model.y = pyo.Var(model.R, model.C, domain=pyo.NonNegativeReals)
# x_ic: Seleção de curva (Binária)
model.x = pyo.Var(model.R, model.C, domain=pyo.Binary)
# z_{i,j,q,c}: Variável auxiliar robusta (Valor absoluto)
model.z = pyo.Var(model.P, model.C, model.C, domain=pyo.NonNegativeReals)

# --- Objective Function ---
# minimize sum( beta_fic * y_ic + x_ic * C_c )
def obj_rule(model):
    return sum(model.beta_obj[i, c] * model.y[i, c] + model.x[i, c] * model.C_param[c] 
               for i in model.R for c in model.C)
model.objective = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

# --- Constraints ---

# 1. Seleção única de curva por relé
def single_curve_rule(model, i):
    return sum(model.x[i, c] for c in model.C) == 1
model.single_curve = pyo.Constraint(model.R, rule=single_curve_rule)

# 2. Limites do TMS (Ativados por x_ic)
def tms_lower_rule(model, i, c):
    return model.y[i, c] >= model.y_lb * model.x[i, c]
model.tms_lower = pyo.Constraint(model.R, model.C, rule=tms_lower_rule)

def tms_upper_rule(model, i, c):
    return model.y[i, c] <= model.y_ub * model.x[i, c]
model.tms_upper = pyo.Constraint(model.R, model.C, rule=tms_upper_rule)

# 3. Restrições Robustas (Contraparte Robusta RC)
# i: Principal, j: Backup, c: Curva Principal, q: Curva Backup

# Equação Base (Nominal + z <= M(2 - x - x))
def rc_base_rule(model, i, j, q, c):
    nominal_part = (model.k1[i,j,q,c] * model.y[i,c] + 
                    model.k2[i,j,q,c] * model.beta0[j,q] * model.y[i,c] - 
                    model.beta0[j,q] * model.y[j,q] + 
                    model.C_param[c] - model.C_param[q] + model.CTI)
    
    return nominal_part + model.z[i,j,q,c] <= model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_base = pyo.Constraint(model.P, model.C, model.C, rule=rc_base_rule)

# Limite superior do Valor Absoluto (z >= Argumento)
def rc_z_pos_rule(model, i, j, q, c):
    uncertainty = model.k2[i,j,q,c] * model.betaL[j,q] * model.y[i,c] - model.betaL[j,q] * model.y[j,q]
    return model.z[i,j,q,c] >= uncertainty - model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_z_pos = pyo.Constraint(model.P, model.C, model.C, rule=rc_z_pos_rule)

# Limite inferior do Valor Absoluto (z >= -Argumento)
def rc_z_neg_rule(model, i, j, q, c):
    uncertainty = model.k2[i,j,q,c] * model.betaL[j,q] * model.y[i,c] - model.betaL[j,q] * model.y[j,q]
    return model.z[i,j,q,c] >= -uncertainty - model.M * (2 - model.x[j,q] - model.x[i,c])
model.rc_z_neg = pyo.Constraint(model.P, model.C, model.C, rule=rc_z_neg_rule)

# =====================================================================
# 4. RESOLUÇÃO DO MODELO
# =====================================================================
print("--- Iniciando Solução ---")
try:
    # ATENÇÃO: Substitua o caminho abaixo pelo diretório correto onde
    # você salvou o highs.exe que acabou de baixar.
    caminho_highs = r'D:\Programas\HiGHS\bin\highs.exe'
    
    # Chama o executável diretamente (100% seguro contra crashes do Python 3.13)
    solver = pyo.SolverFactory('highs', executable=caminho_highs)
    
    results = solver.solve(model, tee=True)
    
    print("\nEstado da otimização:", results.solver.status)
    print("Condição de término:", results.solver.termination_condition)
    
    print("\n--- Resultados Otimizados ---")
    for i in model.R:
        for c in model.C:
            if pyo.value(model.x[i, c]) > 0.5: # Se a curva foi selecionada
                print(f"Relé {i} -> Curva Selecionada: {c} | TMS (y) = {pyo.value(model.y[i, c]):.4f}")

except Exception as e:
    print(f"\nNão foi possível resolver o modelo.")
    print(f"Certifique-se de definir o caminho correto ('executable=') apontando para o arquivo highs.exe.")
    print(f"Erro detalhado: {e}")