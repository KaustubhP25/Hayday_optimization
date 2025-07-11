import json
from collections import defaultdict
from utils.display import Display

def load_json(file_name):
    with open(f"data/{file_name}", "r") as f:
        return json.load(f)

produce_data = load_json("produce.json")
feed_data = load_json("feed.json")  # optional if needed


def calculate_crops_to_plant(production_schedule, check_interval):
    # production_schedule = list of dicts with product name, start time, cycles, etc.
    total_crop_needs = defaultdict(int)
    crops_data = load_json("crops.json")

    for task in production_schedule:
        product_name = task["product"]
        cycles = task.get("cycles", 1)  # or calculate based on schedule
        required_ingredients = flatten_ingredients(product_name, quantity=cycles)

        for item, qty in required_ingredients.items():
            if item in crops_data:
                total_crop_needs[item] += qty

    planting_plan = {}
    for crop, total_qty in total_crop_needs.items():
        crop_info = crops_data[crop]
        time = crop_info["time"]
        max_cycles = check_interval // time
        # Calculate how many units must be planted to keep up with demand
        units_to_plant = (total_qty + max_cycles - 1) // max_cycles  # ceiling division
        planting_plan[crop] = units_to_plant

    print("\n🌾 Crops to Plant to Sustain Production:")
    for crop, units in planting_plan.items():
        print(f"{crop}: Plant {units} units")

    return planting_plan



def flatten_ingredients(item_name, quantity=1, visited=None):
    if visited is None:
        visited = set()
    flattened = defaultdict(int)

    if item_name not in produce_data and item_name not in feed_data:
        flattened[item_name] += quantity
        return flattened

    if item_name in visited:
        return flattened
    visited.add(item_name)

    source = produce_data.get(item_name) or feed_data.get(item_name)
    if not source or "inputs" not in source:
        flattened[item_name] += quantity
        return flattened

    for input_name, input_qty in source["inputs"].items():
        sub_ingredients = flatten_ingredients(input_name, input_qty * quantity, visited.copy())
        for ingr, qty in sub_ingredients.items():
            flattened[ingr] += qty

    return dict(flattened)

def calc_silo_usage(ingredients):
    silo_items = {"Wheat", "Corn", "Soybean", "Sugarcane", "Carrot", "Pumpkin", "Cotton", "Indigo", "Chili Pepper"}
    return sum(qty for item, qty in ingredients.items() if item in silo_items)

def calc_barn_usage(ingredients):
    silo_usage = calc_silo_usage(ingredients)
    total = sum(ingredients.values())
    return total - silo_usage

def schedule_production(level, check_interval, silo_capacity, barn_capacity):
    levels = load_json("levels.json")
    machines = load_json("machine.json")
    produce = produce_data

    unlocked_products = set()
    for lv in levels:
        if int(lv) <= level:
            unlocked_products.update(levels[lv].get("products", []))

    machine_slots = {}
    machine_products = defaultdict(list)
    for machine, data in machines.items():
        machine_slots[machine] = data["slots"]
        for product in data["products"]:
            if product in unlocked_products and product in produce:
                prod_data = produce[product]
                ppm = prod_data["profit"] / prod_data["time"]
                machine_products[machine].append({
                    "name": product,
                    "time": prod_data["time"],
                    "profit": prod_data["profit"],
                    "ppm": ppm,
                })
        machine_products[machine].sort(key=lambda x: x["ppm"], reverse=True)

    machine_queues = {m: [0] * machine_slots[m] for m in machine_slots}

    used_silo = 0
    used_barn = 0
    production_schedule = []

    for minute in range(check_interval):
        for machine, queue in machine_queues.items():
            for i in range(len(queue)):
                if queue[i] <= minute:
                    for product in machine_products[machine]:
                        if product["time"] + minute <= check_interval:
                            required = flatten_ingredients(product["name"], quantity=1)
                            silo_need = calc_silo_usage(required)
                            barn_need = calc_barn_usage(required)

                            if (used_silo + silo_need <= silo_capacity) and (used_barn + barn_need <= barn_capacity):
                                queue[i] = minute + product["time"]
                                production_schedule.append({
                                    "start": minute,
                                    "machine": machine,
                                    "slot": i,
                                    "product": product["name"],
                                    "duration": product["time"],
                                    "profit": product["profit"],
                                    "ingredients": required
                                })
                                used_silo += silo_need
                                used_barn += barn_need
                                break

    total_profit = sum(p["profit"] for p in production_schedule)

    print(f"\n🛠️ Optimized Schedule for Level {level} (Checkback: {check_interval} mins)")
    print(f"📦 Total Profit: ₹{total_profit}")
    for task in production_schedule:
        print(f"[{task['start']:>3}m] {task['machine']} (slot {task['slot']}): {task['product']} → ₹{task['profit']}")
    calculate_crops_to_plant(production_schedule,check_interval)

    
def main():
    main_menu_options = ["Calculate profit", "Configuration", "Exit"]
    while True:
        Display.menu(main_menu_options)
        try:
            choice = int(input("Choose Option: "))
        except ValueError:
            print("Invalid input, please enter a number.")
            continue

        if choice == 1:
            try:
                level = int(input("What is your level: "))
                silo = int(input("Silo Capacity: "))
                barn = int(input("Barn Capacity: "))
                check_interval = int(input("Checkback Time (minutes): "))
            except ValueError:
                print("Please enter valid integer values.")
                continue

            schedule_production(level, check_interval, silo, barn)

        elif choice == 2:
            print("Configuration menu is under construction.")

        elif choice == 3:
            print("Exiting...")
            break

        else:
            print("Choose a valid input.")

if __name__ == "__main__":
    main()
