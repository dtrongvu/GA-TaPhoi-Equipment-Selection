"""
config.py - Genetic Algorithm Hyperparameters & Configuration Settings
========================================================================
Project: GA-TaPhoi-Equipment-Selection
Mining Site: Sector B, Tả Phời Copper Mine, Lào Cai, Vietnam
Target Journal: Acta Montanistica Slovaca (AMS), 2026

This configuration module establishes the genetic operators, hyperparameter
tuning settings, and 8-gene chromosome search space bounds for the dynamic
Life-of-Mine (LOM) fleet selection optimization model.
"""

import random

# ==============================================================================
# 1. GA CONTROL HYPERPARAMETERS (Tab. 6 in AMS Manuscript)
# ==============================================================================
POPULATION_SIZE = 50       # Total candidate fleet configurations per generation
MAX_GENERATIONS = 100       # Termination condition / total evolutionary iterations
MUTATION_RATE = 0.10       # Probability of random gene mutation (10%)
CROSSOVER_RATE = 0.80      # Probability of parent gene recombination (80%)
ELITISM_COUNT = 1          # Number of top-performing elite individuals preserved unchanged
TOURNAMENT_SIZE = 3        # Mating pool selection pressure size for Tournament Selection

# ==============================================================================
# 2. CHROMOSOME STRUCTURE & SEARCH SPACE BOUNDS (Eq. 1 in AMS Manuscript)
# ==============================================================================
# The chromosome vector C = [x1, x2, x3, x4, x5, x6, x7, x8] encodes the complete
# pit equipment fleet configuration across two primary production circuits:
#
# Overburden Waste Stripping Circuit:
#   x1 (Gene 0): Waste Excavator Model ID (0..3 -> Tab. 2 catalog)
#   x2 (Gene 1): Waste Excavator Unit Count (1..5 units)
#   x3 (Gene 2): Waste Truck Model ID (0..3 -> Tab. 3 catalog)
#   x4 (Gene 3): Waste Trucks per Excavator ratio (2..10 trucks/shovel)
#
# Run-of-Mine (ROM) Copper Ore Extraction Circuit:
#   x5 (Gene 4): Ore Excavator Model ID (0..3 -> Tab. 2 catalog)
#   x6 (Gene 5): Ore Excavator Unit Count (1..3 units)
#   x7 (Gene 6): Ore Truck Model ID (0..3 -> Tab. 3 catalog)
#   x8 (Gene 7): Ore Trucks per Excavator ratio (2..10 trucks/shovel)

bounds = [
    (0, 3),   # Gene 0: x1 - Waste Shovel Model ID [0: PC1250, 1: PC650, 2: PC450, 3: EKG-8U]
    (1, 5),   # Gene 1: x2 - Waste Shovel Fleet Size (1 to 5 units)
    (0, 3),   # Gene 2: x3 - Waste Truck Model ID [0: Tonly, 1: HOWO, 2: MT95, 3: HD325-7]
    (2, 10),  # Gene 3: x4 - Waste Trucks-to-Shovel Ratio (2 to 10 trucks/shovel)
    (0, 3),   # Gene 4: x5 - Ore Shovel Model ID [0: PC1250, 1: PC650, 2: PC450, 3: EKG-8U]
    (1, 3),   # Gene 5: x6 - Ore Shovel Fleet Size (1 to 3 units)
    (0, 3),   # Gene 6: x7 - Ore Truck Model ID [0: Tonly, 1: HOWO, 2: MT95, 3: HD325-7]
    (2, 10)   # Gene 7: x8 - Ore Trucks-to-Shovel Ratio (2 to 10 trucks/shovel)
]

# ==============================================================================
# 3. UNIT CONSTRAINT PENALTY RATES (Tab. 7 in AMS Manuscript)
# ==============================================================================
# Financial penalties deducted from objective NPV during fitness evaluation when
# candidate fleet solutions violate operational or geomechanical constraints.

PENALTY_RATES = {
    'U_penalty_waste': 400.00,      # USD/m3: Waste production deficit penalty
    'U_penalty_ore': 4000.00,       # USD/ton: Ore production deficit penalty
    'P_tech': 200000.00,            # USD/event: Pass match out of range (N_pass < 4 or N_pass > 6)
    'P_geo': 400000.00              # USD/event: Ore shovel bucket capacity exceeds limit (E_ore > 3.0 m3)
}

# ==============================================================================
# 4. HELPER GENETIC OPERATOR FUNCTIONS
# ==============================================================================
def create_individual():
    """
    Generates a single random 8-gene integer chromosome vector within
    the predefined search space bounds.
    
    Returns:
        list[int]: An 8-element list representing a candidate fleet configuration.
    """
    return [random.randint(b[0], b[1]) for b in bounds]


def mutate(individual, rate=MUTATION_RATE):
    """
    Applies stochastic single-gene mutation to a chromosome vector.
    Each gene position has a probability `rate` of being randomly reassigned
    to a valid integer within its defined search bounds.
    
    Args:
        individual (list[int]): The 8-gene chromosome vector to mutate.
        rate (float): Mutation probability per gene (default 0.10).
        
    Returns:
        list[int]: Mutated 8-gene chromosome vector.
    """
    mutated = individual.copy()
    for idx in range(len(mutated)):
        if random.random() < rate:
            mutated[idx] = random.randint(bounds[idx][0], bounds[idx][1])
    return mutated


def crossover(parent1, parent2, rate=CROSSOVER_RATE):
    """
    Executes single-point crossover between two parent chromosome vectors
    to produce two offspring.
    
    Args:
        parent1 (list[int]): First parent chromosome.
        parent2 (list[int]): Second parent chromosome.
        rate (float): Crossover probability (default 0.80).
        
    Returns:
        tuple[list[int], list[int]]: Two offspring chromosome vectors.
    """
    if random.random() < rate:
        cut_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:cut_point] + parent2[cut_point:]
        child2 = parent2[:cut_point] + parent1[cut_point:]
        return child1, child2
    return parent1.copy(), parent2.copy()
