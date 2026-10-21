# GA-TaPhoi-Equipment-Selection

Open-source Python implementation of the multi-period dynamic **Genetic Algorithm (GA)** model for Life-of-Mine (LOM) surface mining equipment selection and scheduling at Sector B of the **Tả Phời Copper Mine**, Lào Cai, Vietnam.

---

## 📌 Project Overview

This repository provides the complete, fully reproducible source code accompanying the research article:
> **"Application of Genetic Algorithm for equipment selection at area B of Ta Phoi Copper mine, Vietnam"**  
> Published in *Acta Montanistica Slovaca* (AMS), Volume 31 (2026).

### Key Features
- **Dynamic 12-Year Kinematics:** Models expanding haul route distances ($\Delta L = 0.15\text{ km/yr}$) and time-dependent truck productivity decay.
- **Constraint Enforcement:** Incorporates hard operational penalty functions for pass-match synchronization ($4 \le N_{\text{pass}} \le 6$) and selective ore digging bucket limits ($E_{\text{ore}} \le 3.0\text{ m}^3$).
- **Inter-Circuit Capacity Reallocation:** Dynamically reallocates surplus ore excavator capacity ($\sim1.26 \times 10^6\text{ m}^3/\text{year}$) to overburden waste stripping.
- **Electrification Economics:** Evaluates grid power ($0.078\text{ USD/kWh}$) vs. commercial diesel ($0.840\text{ USD/L}$) trade-offs for LOM Net Present Value (NPV) maximization.

---

## 📁 Repository Structure

```text
GA-TaPhoi-Equipment-Selection/
├── README.md              # Project overview, installation, and usage
├── requirements.txt       # Python dependencies
├── config.py              # Hyperparameters & 8-gene search bounds
├── main.py                # Main GA evolutionary execution loop
└── modules/
    ├── __init__.py
    ├── data_loader.py     # Database ingestion & Google Sheets connector
    └── fitness.py         # LOM NPV evaluation engine & penalty calculator
```

---

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.10+
* Git

### Step-by-Step Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/dtrongvu/GA-TaPhoi-Equipment-Selection.git
   cd GA-TaPhoi-Equipment-Selection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run

Execute the main optimization workflow from the command line:

```bash
python main.py
```

### Expected Console Output
```text
================================================================================
🚀 STARTING GENETIC ALGORITHM FLEET OPTIMIZATION
Site: Sector B, Tả Phời Copper Mine | Horizon: 12-Year Life-of-Mine
================================================================================
⚙️ GA Hyperparameters: Population=50 | Generations=100 | Mutation=0.1 | Crossover=0.8
--------------------------------------------------------------------------------
Gen   1/100 | Best Fitness (NPV): $    847.00 M USD | Current Vector: [3, 2, 2, 9, 1, 3, 1, 10]
Gen  10/100 | Best Fitness (NPV): $   1434.00 M USD | Current Vector: [3, 2, 2, 9, 1, 3, 1, 10]
...
Gen 100/100 | Best Fitness (NPV): $   1439.68 M USD | Current Vector: [3, 2, 2, 9, 1, 3, 1, 10]

================================================================================
✅ OPTIMIZATION COMPLETE
================================================================================
🏆 Optimal Chromosome Vector: [3, 2, 2, 9, 1, 3, 1, 10]
💰 Projected 12-Year LOM Net Present Value (NPV): $1439.68 Million USD
```

---

## 📄 Citation

If you use this codebase or model in your research, please cite:

```bibtex
@article{Vu2026_TaPhoi_GA,
  author  = {Vu, Doan Trong and Ha, Huy Manh and Nguyen, Tan Viet},
  title   = {Application of Genetic Algorithm for equipment selection at area B of Ta Phoi Copper mine, Vietnam},
  journal = {Acta Montanistica Slovaca},
  volume  = {31},
  year    = {2026},
  publisher = {Technical University of Košice}
}
```
