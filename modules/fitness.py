"""
fitness.py - Objective Fitness Evaluation & Economic Engine Module
===================================================================
Project: GA-TaPhoi-Equipment-Selection
Mining Site: Sector B, Tả Phời Copper Mine, Lào Cai, Vietnam
Target Journal: Acta Montanistica Slovaca (AMS)

This module implements the 12-year Life-of-Mine (LOM) dynamic Net Present Value (NPV)
evaluation function, incorporating shovel-truck pass match constraints, selective digging
limits, dynamic haul road expansion, capacity reallocation, and constraint penalty functions.
"""

import sys
import os
import numpy as np
import pandas as pd

# Handle path imports for standalone or package execution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PENALTY_RATES
from data_loader import load_database

# Load database tables and parameters
df_bang1, df_bang2, df_bang3, df_bang4, kinh_te, dia_chat = load_database()


def calculate_fitness(chromosome):
    """
    Evaluates the objective economic fitness (F_fitness = LOM NPV - Penalty Deductions)
    for an 8-gene chromosome vector representing a candidate fleet configuration.

    Chromosome Vector Encoding (Eq. 1 in AMS Manuscript):
      chromosome = [x1, x2, x3, x4, x5, x6, x7, x8]

      Overburden Waste Circuit:
        x1: Waste Shovel Model ID (0: PC1250, 1: PC650, 2: PC450, 3: EKG-8U)
        x2: Waste Shovel Fleet Size (units)
        x3: Waste Truck Model ID (0: Tonly, 1: HOWO, 2: MT95, 3: HD325-7)
        x4: Waste Trucks per Shovel ratio (trucks/shovel)

      Run-of-Mine (ROM) Copper Ore Circuit:
        x5: Ore Shovel Model ID (0: PC1250, 1: PC650, 2: PC450, 3: EKG-8U)
        x6: Ore Shovel Fleet Size (units)
        x7: Ore Truck Model ID (0: Tonly, 1: HOWO, 2: MT95, 3: HD325-7)
        x8: Ore Trucks per Shovel ratio (trucks/shovel)

    Returns:
      float: Adjusted Life-of-Mine Net Present Value (USD)
    """
    # 0. Decode chromosome vector
    x1, x2, x3, x4, x5, x6, x7, x8 = chromosome
    
    total_trucks_waste = x2 * x4
    total_trucks_ore = x6 * x8
    
    annual_penalty_deductions = 0.0

    # 1. Retrieve Equipment Specifications from Catalog Tables (Tab. 2 & Tab. 3)
    E_waste = float(df_bang2.loc[x1, 'E (m3)'])
    T_dig_waste = float(df_bang2.loc[x1, 'T_ck (s)'])
    Price_exc_waste = float(df_bang2.loc[x1, 'Giá mua (triệu VND)'])

    E_ore = float(df_bang2.loc[x5, 'E (m3)'])
    T_dig_ore = float(df_bang2.loc[x5, 'T_ck (s)'])
    Price_exc_ore = float(df_bang2.loc[x5, 'Giá mua (triệu VND)'])

    q_truck_waste = float(df_bang3.loc[x3, 'Tải trọng q (tấn)'])
    v_loaded_waste = float(df_bang3.loc[x3, 'V_ct (km/h)'])
    v_empty_waste = float(df_bang3.loc[x3, 'V_kt (km/h)'])
    Price_truck_waste = float(df_bang3.loc[x3, 'Giá mua (triệu VND)'])

    q_truck_ore = float(df_bang7_id if 'df_bang7_id' in locals() else df_bang3.loc[x7, 'Tải trọng q (tấn)'])
    v_loaded_ore = float(df_bang3.loc[x7, 'V_ct (km/h)'])
    v_empty_ore = float(df_bang3.loc[x7, 'V_kt (km/h)'])
    Price_truck_ore = float(df_bang3.loc[x7, 'Giá mua (triệu VND)'])

    # 2. Technological & Geotechnical Constraint Verification (Section 2.5)
    K_swell_waste = 1.30
    K_swell_ore = 1.40
    gamma_waste = 2.20  # t/m3
    gamma_ore = 2.65    # t/m3
    K_fill = 0.80

    # Shovel-truck pass match count calculations (Eq. 6 & Eq. 7)
    N_pass_waste = (q_truck_waste * K_swell_waste) / (E_waste * gamma_waste * K_fill)
    N_pass_ore = (q_truck_ore * K_swell_ore) / (E_ore * gamma_ore * K_fill)

    # Technological pass match window verification: 4 <= N_pass <= 6 (Eq. 8)
    if not (4.0 <= N_pass_waste <= 6.0):
        annual_penalty_deductions += PENALTY_RATES['P_tech']
    if not (4.0 <= N_pass_ore <= 6.0):
        annual_penalty_deductions += PENALTY_RATES['P_tech']

    # Geotechnical selective digging constraint: E_ore <= 3.0 m3 (Eq. 5)
    if E_ore > 3.0:
        annual_penalty_deductions += PENALTY_RATES['P_geo']

    # 3. Year 0 Capital Expenditure (CAPEX_0, Eq. 15)
    CAPEX_0 = (x2 * Price_exc_waste + total_trucks_waste * Price_truck_waste) + \
              (x6 * Price_exc_ore + total_trucks_ore * Price_truck_ore)

    # Convert Price from Million VND to USD (1 USD ~ 25,000 VND)
    vnd_to_usd = 1.0 / 25.0  # Million VND -> Thousand USD conversion factor
    CAPEX_0_USD = CAPEX_0 * 1000.0 * (1.0 / 25000.0)

    # 4. Multi-Period 12-Year Life-of-Mine Dynamic Kinematics & Cash Flows
    L0_waste = 5.25  # km: Initial Year 1 haul distance for waste
    L0_ore = 2.16    # km: Initial Year 1 haul distance for ore
    delta_L = 0.15   # km/yr: Annual bench deepening haul road extension
    
    A_waste_req = 4500000.0  # m3/yr: Overburden waste stripping target
    A_ore_req = 1000000.0    # tons/yr: ROM copper ore extraction target

    # Operating schedule parameters (Tab. 1)
    T_shift = 8.0     # hours/shift
    n_shift = 3.0     # shifts/day
    N_op = 299.0      # operating days/year
    eta = 0.80        # operational time utilization efficiency
    k_ramp = 1.20     # ramp acceleration/deceleration factor

    # Economic parameters (Tab. 4)
    c_diesel = 0.840   # USD/liter
    c_elec = 0.078     # USD/kWh
    w_EKG = 0.55       # kWh/m3 (specific electricity norm for electric shovel)
    g_PC = 0.25        # L/m3 (specific diesel norm for hydraulic excavators)
    g_truck = 0.22     # L/(t*km) (specific diesel norm for haul trucks)
    K_util = 0.75      # electrical power utilization factor
    
    S_truck = 480.0    # USD/month: Dump truck driver salary
    S_exc = 600.0      # USD/month: Excavator operator salary
    
    p_conc = 880.0     # USD/ton: Copper concentrate market price
    e_rec = 0.032      # Concentrate recovery yield ratio
    
    r_discount = 0.15  # Annual financial discount rate (15%)
    T_tax_rate = 0.25  # Corporate income tax rate (25%)
    T_res_rate = 0.02  # Natural resource royalty tax rate (2%)

    # Calculate Fixed Labor Overhead OPEX (Eq. 18)
    OPEX_fix = 12.0 * n_shift * ((x2 + x6) * S_exc + (total_trucks_waste + total_trucks_ore) * S_truck)

    # Calculate Annual Gross Revenue (Eq. 19)
    Gross_Revenue = A_ore_req * e_rec * p_conc

    discounted_cash_flows = []

    for t in range(1, 13):  # 12-year project lifespan
        # Spatial extension of haulage distances (Eq. 2)
        L_t_waste = L0_waste + (t - 1) * delta_L
        L_t_ore = L0_ore + (t - 1) * delta_L

        # Shovel loading durations (minutes)
        t_load_waste = (N_pass_waste * T_dig_waste) / 60.0
        t_load_ore = (N_pass_ore * T_dig_ore) / 60.0

        # Round-trip truck cycle times (Eq. 3)
        T_cycle_waste_t = t_load_waste + 60.0 * k_ramp * (L_t_waste / v_loaded_waste + L_t_waste / v_empty_waste) + 1.5 + 1.0
        T_cycle_ore_t = t_load_ore + 60.0 * k_ramp * (L_t_ore / v_loaded_ore + L_t_ore / v_empty_ore) + 1.5 + 1.0

        # Single-truck annual productivities (Eq. 9 & Eq. 10)
        V_truck_body_waste = q_truck_waste / gamma_waste
        W_truck_waste_t = (V_truck_body_waste * T_shift * n_shift * N_op * eta * 60.0) / T_cycle_waste_t
        W_truck_ore_t = (q_truck_ore * T_shift * n_shift * N_op * eta * 60.0) / T_cycle_ore_t

        # Primary circuit capacities (Eq. 11 & Eq. 12)
        Q_ore_t = total_trucks_ore * W_truck_ore_t
        
        # Dynamic surplus ore shovel capacity reallocation (Eq. 13)
        if Q_ore_t > A_ore_req:
            W_reallocated_t = max(0.0, (Q_ore_t - A_ore_req) / gamma_waste)
        else:
            W_reallocated_t = 0.0

        Q_waste_t = total_trucks_waste * W_truck_waste_t + W_reallocated_t

        # Production shortfall penalty check (Eq. 14)
        P_prod_t = 0.0
        if Q_waste_t < A_waste_req:
            P_prod_t += (A_waste_req - Q_waste_t) * PENALTY_RATES['U_penalty_waste']
        if Q_ore_t < A_ore_req:
            P_prod_t += (A_ore_req - Q_ore_t) * PENALTY_RATES['U_penalty_ore']

        # Transport work in ton-kilometers for variable OPEX
        TK_waste_t = A_waste_req * gamma_waste * L_t_waste
        TK_ore_t = A_ore_req * L_t_ore

        # Variable energy expenditure (Eq. 17)
        if x1 == 3:  # EKG-8U Electric Shovel
            electric_cost = A_waste_req * w_EKG * c_elec * K_util
            diesel_exc_cost = 0.0
        else:
            electric_cost = 0.0
            diesel_exc_cost = A_waste_req * g_PC * c_diesel

        diesel_truck_cost = g_truck * (TK_waste_t + TK_ore_t) * c_diesel
        OPEX_var_t = electric_cost + diesel_exc_cost + diesel_truck_cost

        # Total OPEX for Year t (Eq. 16)
        OPEX_t = OPEX_var_t + OPEX_fix

        # Taxation liabilities
        Tax_t = Gross_Revenue * T_res_rate + max(0.0, Gross_Revenue - OPEX_t) * T_tax_rate

        # Net cash flow after deducting OPEX, taxes, and operational penalties (Eq. 20)
        CF_t = Gross_Revenue - OPEX_t - Tax_t - (annual_penalty_deductions + P_prod_t)

        # Discounted net cash flow (Eq. 21)
        discounted_CF = CF_t / ((1.0 + r_discount) ** t)
        discounted_cash_flows.append(discounted_CF)

    # 5. Objective Fitness Function: Total Life-of-Mine Net Present Value (Eq. 21)
    LOM_NPV = sum(discounted_cash_flows) - CAPEX_0_USD
    return LOM_NPV


# Test module execution if run directly
if __name__ == "__main__":
    print("Executing fitness.py test with optimal chromosome configuration...")
    # Optimal chromosome vector: [3, 2, 2, 9, 1, 3, 1, 10]
    # (2 EKG-8U + 18 MT95 waste | 3 PC650 + 30 HOWO ore)
    optimal_chromosome = [3, 2, 2, 9, 1, 3, 1, 10]
    
    npv_result = calculate_fitness(optimal_chromosome)
    print(f"Optimal Chromosome Vector: {optimal_chromosome}")
    print(f"Evaluated LOM Net Present Value: ${npv_result/1e6:,.2f} Million USD")
