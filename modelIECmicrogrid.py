import pandapower as pp
import pandapower.shortcircuit as sc
import numpy as np
import warnings

def create_iec_microgrid_exact():
    # 1. Crear red vacía a 60 Hz
    net = pp.create_empty_network(f_hz=60.0)

    # ================= BUSES =================
    bus_utility = pp.create_bus(net, vn_kv=120.0, name="Utility 120kV")
    bus_pcc = pp.create_bus(net, vn_kv=25.0, name="PCC B1")
    bus2 = pp.create_bus(net, vn_kv=25.0, name="BUS 2")
    bus3 = pp.create_bus(net, vn_kv=25.0, name="BUS 3")
    bus4 = pp.create_bus(net, vn_kv=25.0, name="BUS 4")
    bus5 = pp.create_bus(net, vn_kv=25.0, name="BUS 5")
    bus6 = pp.create_bus(net, vn_kv=25.0, name="BUS 6")

    # Buses de Generadores (Baja Tensión)
    bus_dg1 = pp.create_bus(net, vn_kv=2.4, name="Terminal DG1")
    bus_dg2 = pp.create_bus(net, vn_kv=2.4, name="Terminal DG2")
    bus_dg3 = pp.create_bus(net, vn_kv=0.575, name="Terminal DG3")
    bus_dg4 = pp.create_bus(net, vn_kv=0.575, name="Terminal DG4")

    # ================= GRID EXTERNO =================
    pp.create_ext_grid(net, bus_utility, s_sc_max_mva=1000.0, rx_max=0.1, name="Utility Grid")

    # ================= TRANSFORMADORES (CORREGIDOS al 10%) =================
    # R1 = 0.00375 pu -> vkr = 0.375%
    # X1 = 0.1 pu -> vk = sqrt(0.00375^2 + 0.1^2) * 100 = 10.007%
    vkr_val = 0.00375 * 100
    vk_val = np.sqrt(0.00375**2 + 0.1**2) * 100

    # TR-1: 15 MVA, 120/25 kV
    pp.create_transformer_from_parameters(net, hv_bus=bus_utility, lv_bus=bus_pcc, sn_mva=15.0,
                                          vn_hv_kv=120.0, vn_lv_kv=25.0, vkr_percent=vkr_val,
                                          vk_percent=vk_val, pfe_kw=30, i0_percent=0.2828, name="TR-1")
    # TR-2: 12 MVA, 25/2.4 kV
    pp.create_transformer_from_parameters(net, hv_bus=bus2, lv_bus=bus_dg1, sn_mva=12.0,
                                          vn_hv_kv=25.0, vn_lv_kv=2.4, vkr_percent=vkr_val,
                                          vk_percent=vk_val, pfe_kw=24, i0_percent=0.2828, name="TR-2")
    # TR-3: 12 MVA, 25/2.4 kV
    pp.create_transformer_from_parameters(net, hv_bus=bus3, lv_bus=bus_dg2, sn_mva=12.0,
                                          vn_hv_kv=25.0, vn_lv_kv=2.4, vkr_percent=vkr_val,
                                          vk_percent=vk_val, pfe_kw=24, i0_percent=0.2828, name="TR-3")
    # TR-4: 10 MVA, 25/0.575 kV
    pp.create_transformer_from_parameters(net, hv_bus=bus4, lv_bus=bus_dg3, sn_mva=10.0,
                                          vn_hv_kv=25.0, vn_lv_kv=0.575, vkr_percent=vkr_val,
                                          vk_percent=vk_val, pfe_kw=20, i0_percent=0.2828, name="TR-4")
    # TR-5: 10 MVA, 25/0.575 kV
    pp.create_transformer_from_parameters(net, hv_bus=bus6, lv_bus=bus_dg4, sn_mva=10.0,
                                          vn_hv_kv=25.0, vn_lv_kv=0.575, vkr_percent=vkr_val,
                                          vk_percent=vk_val, pfe_kw=20, i0_percent=0.2828, name="TR-5")

    # ================= LÍNEAS DE DISTRIBUCIÓN (30 km) =================
    line_params = {
        "r_ohm_per_km": 0.413,
        "x_ohm_per_km": 1.251,
        "c_nf_per_km": 5.01,
        "r0_ohm_per_km": 0.1153,
        "x0_ohm_per_km": 0.396,
        "c0_nf_per_km": 11.33,
        "max_i_ka": 1.0
    }

    # ACTIVADAS TODAS LAS LÍNEAS ORIGINALES
    pp.create_line_from_parameters(net, from_bus=bus_pcc, to_bus=bus3, length_km=30.0, name="DL-1", **line_params)
    pp.create_line_from_parameters(net, from_bus=bus_pcc, to_bus=bus2, length_km=30.0, name="DL-2", **line_params)
    pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus4, length_km=30.0, name="DL-3", **line_params)
    pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus5, length_km=30.0, name="DL-4", **line_params)
    pp.create_line_from_parameters(net, from_bus=bus5, to_bus=bus6, length_km=30.0, name="DL-5", **line_params)

    # ================= INTERRUPTORES DE LAZO (Cerrados para topología de red del artículo) =================
    # Conectar los lazos enclavados para permitir el paso de las corrientes de falla conjuntas
    pp.create_switch(net, bus=bus2, element=bus4, et="b", closed=True, name="CB_LOOP 1")
    pp.create_switch(net, bus=bus4, element=bus6, et="b", closed=True, name="CB_LOOP 2")

    # ================= GENERADORES DISTRIBUIDOS (Habilitados) =================
    # Parámetro xdss_pu mapea directamente al comportamiento subtransitorio en sc.calc_sc
    pp.create_gen(net, bus_dg1, p_mw=8.1, vm_pu=1.0, sn_mva=9.0, vn_kv=2.4, xdss_pu=0.177, name="DG1")
    pp.create_gen(net, bus_dg2, p_mw=8.1, vm_pu=1.0, sn_mva=9.0, vn_kv=2.4, xdss_pu=0.177, name="DG2")
    pp.create_gen(net, bus_dg3, p_mw=5.4, vm_pu=1.0, sn_mva=6.0, vn_kv=0.575, xdss_pu=0.252, name="DG3")
    pp.create_gen(net, bus_dg4, p_mw=8.1, vm_pu=1.0, sn_mva=9.0, vn_kv=0.575, xdss_pu=0.34, name="DG4")

    # ================= CARGAS =================
    p_load = 22.0 / 6.0
    q_load = 10.0 / 6.0
    for b in [bus_pcc, bus2, bus3, bus4, bus5, bus6]:
        pp.create_load(net, b, p_mw=p_load, q_mvar=q_load)

    return net

# Inicializar y correr simulación según la norma IEC 60909
net = create_iec_microgrid_exact()

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    sc.calc_sc(net, case="max", ip=True, ith=True, branch_results=True)

print("--- Nuevas Corrientes de Cortocircuito en Buses (kA) ---")
print(net.res_bus_sc[['ikss_ka']])
