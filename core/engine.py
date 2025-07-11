def run_optimizer(level, silo, storage, time_limit, game_data):
    produce = game_data["produce"]
    levels = game_data["levels"]
    animals = game_data["animals"]

    # Step 1: Get unlocked crops, animals, products
    unlocked = {
        "crops": set(),
        "animals": set(),
        "products": set()
    }

    for lvl in range(1, level + 1):
        lvl_data = levels.get(str(lvl), {})
        unlocked["crops"].update(lvl_data.get("crops", []))
        unlocked["animals"].update(lvl_data.get("animals", []))
        unlocked["products"].update(lvl_data.get("products", []))

    # Step 2: Build list of valid produce
    valid_items = []

    for name, item in produce.items():
        if name not in unlocked["crops"] and name not in unlocked["products"]:
            continue  # Skip locked items

        total_time = item["time"]
        total_inputs = item.get("inputs", {})
        feasible = True

        # Step 3: Check animal products (Egg, Milk, etc.)
        for input_item in total_inputs:
            if input_item in [animals[a]["produces"] for a in unlocked["animals"] if a in animals]:
                # This input comes from an animal
                animal = next((a for a in animals if animals[a]["produces"] == input_item), None)
                if not animal:
                    feasible = False
                    break

                feed_name = f"{animal} feed"
                feed_recipe = produce.get(feed_name)
                if not feed_recipe:
                    feasible = False
                    break

                feed_time = feed_recipe["time"]
                animal_time = animals[animal]["time"]
                feed_ingredients = feed_recipe["inputs"]

                # Check if feed ingredients are unlocked crops
                for crop in feed_ingredients:
                    if crop not in unlocked["crops"]:
                        feasible = False
                        break

                if not feasible:
                    break

                # Add feed + animal time
                total_time += feed_time + animal_time

        if not feasible or total_time > time_limit:
            continue

        value_per_min = item["profit"] / total_time if total_time else 0

        valid_items.append({
            "name": name,
            "profit": item["profit"],
            "time": total_time,
            "barn_space": item.get("barn_space", 1),
            "value_per_min": round(value_per_min, 3)
        })

    # Step 4: Greedy selection by profit/time
    valid_items.sort(key=lambda x: x["value_per_min"], reverse=True)
    barn_capacity = storage * 25
    used_space = 0
    plan = []

    for item in valid_items:
        space_left = barn_capacity - used_space
        max_units = space_left // item["barn_space"]
        if max_units > 0:
            plan.append(f"{item['name']} x{max_units} (each profit: {item['profit']}, total: {item['profit'] * max_units})")
            used_space += max_units * item["barn_space"]

    if not plan:
        plan.append("No viable items found within time and storage constraints.")

    return plan
