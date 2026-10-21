"""
main.py - Main Genetic Algorithm Execution Engine
=================================================
Project: GA-TaPhoi-Equipment-Selection
Mining Site: Sector B, Tả Phời Copper Mine, Lào Cai, Vietnam
Target Journal: Acta Montanistica Slovaca (AMS)

This is the main entry point for executing the multi-period dynamic Genetic
Algorithm (GA) optimization model for Life-of-Mine (LOM) open-pit equipment fleet
selection and scheduling.
"""

import sys
import os
import time
import random
import numpy as np
import pandas as pd

# Import local modules
from config import (
    POPULATION_SIZE,
    MAX_GENERATIONS,
    MUTATION_RATE,
    CROSSOVER_RATE,
    ELITISM_COUNT,
    TOURNAMENT_SIZE,
    bounds,
    create_individual,
    crossover,
    mutate
)
from data_loader import load_database
from fitness import calculate_fitness


def tournament_selection(population, fitness_scores, tournament_size=TOURNAMENT_SIZE):
    """
    Selects one parent individual from the population using Tournament Selection.
    Picks `tournament_size` random candidates and returns the one with highest fitness.
    """
    selected_indices = random.sample(range(len(population)), tournament_size)
    best_idx = max(selected_indices, key=lambda idx: fitness_scores[idx])
    return population[best_idx]


def decode_chromosome(chromosome, df_bang2, df_bang3):
    """
    Decodes an 8-gene chromosome vector into a structured equipment configuration summary.
    
    Chromosome structure C = [x1, x2, x3, x4, x5, x6, x7, x8]
    """
    x1, x2, x3, x4, x5, x6, x7, x8 = chromosome

    # Retrieve equipment model names
    ex_w_model = df_bang2.loc[x1, 'Loại máy']
    ex_w_bucket = df_bang2.loc[x1, 'E (m3)']
    tr_w_model = df_bang3.loc[x3, 'Loại xe']
    tr_w_payload = df_bang3.loc[x3, 'Tải trọng q (tấn)']

    ex_o_model = df_bang2.loc[x5, 'Loại máy']
    ex_o_bucket = df_bang2.loc[x5, 'E (m3)']
    tr_o_model = df_bang3.loc[x7, 'Loại xe']
    tr_o_payload = df_bang3.loc[x7, 'Tải trọng q (tấn)']

    total_tr_w = x2 * x4
    total_tr_o = x6 * x8

    summary = {
        "Overburden Waste Circuit": {
            "Shovel Model": f"{ex_w_model} ({ex_w_bucket:.1f} m³ bucket)",
            "Shovel Count": f"{x2} units",
            "Truck Model": f"{tr_w_model} ({tr_w_payload:.0f}-ton payload)",
            "Truck Count": f"{total_tr_w} units ({x4} trucks/shovel)"
        },
        "Copper Ore Circuit": {
            "Shovel Model": f"{ex_o_model} ({ex_o_bucket:.1f} m³ bucket)",
            "Shovel Count": f"{x6} units",
            "Truck Model": f"{tr_o_model} ({tr_o_payload:.0f}-ton payload)",
            "Truck Count": f"{total_tr_o} units ({x8} trucks/shovel)"
        },
        "Total Fleet Sizing": {
            "Total Shovels": f"{x2 + x6} units",
            "Total Trucks": f"{total_tr_w + total_tr_o} units"
        }
    }
    return summary


def run_ga_optimization():
    """
    Executes the main Genetic Algorithm evolutionary loop across MAX_GENERATIONS.
    """
    print("================================================================================")
    print("🚀 STARTING GENETIC ALGORITHM FLEET OPTIMIZATION")
    print("Site: Sector B, Tả Phời Copper Mine | Horizon: 12-Year Life-of-Mine")
    print("================================================================================\n")

    # 1. Load database tables
    df_bang1, df_bang2, df_bang3, df_bang4, kinh_te, dia_chat = load_database()

    # 2. Initialize Population
    start_time = time.time()
    population = [create_individual() for _ in range(POPULATION_SIZE)]
    
    best_overall_individual = None
    best_overall_fitness = -float('inf')
    fitness_history = []

    print(f"⚙️ GA Hyperparameters: Population={POPULATION_SIZE} | Generations={MAX_GENERATIONS} | Mutation={MUTATION_RATE} | Crossover={CROSSOVER_RATE}")
    print("--------------------------------------------------------------------------------")

    # 3. Main Evolutionary Loop
    for generation in range(1, MAX_GENERATIONS + 1):
        # Evaluate fitness for current population
        fitness_scores = [calculate_fitness(ind) for ind in population]

        # Identify best individual in current generation
        gen_best_idx = np.argmax(fitness_scores)
        gen_best_fitness = fitness_scores[gen_best_idx]
        gen_best_ind = population[gen_best_idx]

        # Update overall best
        if gen_best_fitness > best_overall_fitness:
            best_overall_fitness = gen_best_fitness
            best_overall_individual = gen_best_ind.copy()

        fitness_history.append(best_overall_fitness)

        # Print progress every 10 generations (and generation 1 & MAX_GENERATIONS)
        if generation == 1 or generation % 10 == 0 or generation == MAX_GENERATIONS:
            print(f"Gen {generation:3d}/{MAX_GENERATIONS:3d} | Best Fitness (NPV): ${best_overall_fitness/1e6:10.2f} M USD | Current Vector: {gen_best_ind}")

        # 4. Generate Next Generation
        next_population = []

        # Elitism: Retain top ELITISM_COUNT individuals
        sorted_indices = np.argsort(fitness_scores)[::-1]
        for e in range(ELITISM_COUNT):
            next_population.append(population[sorted_indices[e]].copy())

        # Fill remaining population with Crossover & Mutation
        while len(next_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitness_scores)
            parent2 = tournament_selection(population, fitness_scores)
            
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)

            next_population.append(child1)
            if len(next_population) < POPULATION_SIZE:
                next_population.append(child2)

        population = next_population

    elapsed_time = time.time() - start_time

    # 5. Display Final Results
    print("\n================================================================================")
    print("✅ OPTIMIZATION COMPLETE")
    print(f"⏱️ Total Execution Time: {elapsed_time:.2f} seconds")
    print("================================================================================")
    print(f"🏆 Optimal Chromosome Vector: {best_overall_individual}")
    print(f"💰 Projected 12-Year LOM Net Present Value (NPV): ${best_overall_fitness/1e6:.2f} Million USD")
    print("--------------------------------------------------------------------------------")

    # Decode final optimal fleet
    fleet_summary = decode_chromosome(best_overall_individual, df_bang2, df_bang3)
    
    print("\n📋 DECODED OPTIMAL FLEET CONFIGURATION (Tab. 8 in AMS Manuscript):")
    for circuit, specs in fleet_summary.items():
        print(f"\n  🔹 {circuit}:")
        for key, val in specs.items():
            print(f"     • {key:20s}: {val}")

    print("\n================================================================================")
    return best_overall_individual, best_overall_fitness, fitness_history


if __name__ == "__main__":
    run_ga_optimization()
