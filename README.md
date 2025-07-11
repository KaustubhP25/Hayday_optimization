# HayDay Profit Optimizer

A Python-based optimizer tool for the mobile game **Hay Day** that helps you maximize profits by recommending the best crop planting strategy and production schedule based on your player level, silo and barn capacities, and preferred checkback interval.

---

## Features

- **Level-based item filtering:** Only suggests crops, animals, and products available at your current level.
- **Profit maximization:** Uses a greedy approach considering item profit, production time, and resource constraints.
- **Machine slot management:** Accounts for machine slots when scheduling product crafting.
- **Ingredient flattening:** Calculates total raw crop requirements by flattening multi-level production recipes.
- **Planting recommendations:** Provides exactly how many units of each crop to plant to sustain continuous production.
- **Configurable checkback interval:** Optimize your gameplay session duration to minimize game checks.
- **JSON-driven data:** Uses external JSON files (`levels.json`, `crops.json`, `produce.json`, `machines.json`, `feed.json`) for flexible, easy updates.

---

## Getting Started

### Prerequisites

- Python 3.7+
- Basic Python environment (no external libraries required)

### Project Structure

