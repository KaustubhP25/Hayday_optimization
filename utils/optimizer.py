class Optimizer:
    @staticmethod
    def expand_product(product_name, quantity, produce_data, feed_data, crops_data):
        from collections import defaultdict

        def helper(product, qty):
            inputs = produce_data[product]["inputs"]
            time = produce_data[product]["time"] * qty

            required_crops = defaultdict(int)
            required_feeds = defaultdict(int)
            intermediate = defaultdict(int)

            for item, count in inputs.items():
                total_count = count * qty

                # If it's a crop
                if item in crops_data:
                    required_crops[item] += total_count

                # If it's an animal product → resolve via feed
                elif "Feed" in item:
                    # directly a feed (unlikely)
                    required_feeds[item] += total_count

                elif item in feed_data:
                    # it's a feedable animal product (like Milk, Eggs, etc.)
                    feed_name = None
                    if item == "Milk":
                        feed_name = "Cow Feed"
                    elif item == "Eggs":
                        feed_name = "Chicken Feed"
                    elif item == "Bacon":
                        feed_name = "Pig Feed"
                    elif item == "Wool":
                        feed_name = "Sheep Feed"

                    if feed_name:
                        required_feeds[feed_name] += total_count
                        # Now get crops needed for that feed
                        feed_recipe = feed_data[feed_name]["inputs"]
                        for crop, amt in feed_recipe.items():
                            required_crops[crop] += amt * total_count

                elif item in produce_data:
                    # It's an intermediate product
                    sub_result = helper(item, total_count)
                    time += sub_result["time"]
                    for k, v in sub_result["crops"].items():
                        required_crops[k] += v
                    for k, v in sub_result["feeds"].items():
                        required_feeds[k] += v
                    for k, v in sub_result["intermediate"].items():
                        intermediate[k] += v
                    intermediate[item] += total_count

            return {
                "time": time,
                "crops": dict(required_crops),
                "feeds": dict(required_feeds),
                "intermediate": dict(intermediate)
            }

        return helper(product_name, quantity)

    @staticmethod
    def get_profitable_products(level, check_interval, produce_data, feed_data, crops_data, levels_data):
        available_products = []
        for lv in levels_data:
            if int(lv) <= level:
                available_products += levels_data[lv].get("products", [])

        profitable = []
        for product in set(available_products):
            if product not in produce_data:
                continue

            result = Optimizer.expand_product(product, 1, produce_data, feed_data, crops_data)
            total_time = result["time"]
            profit = produce_data[product]["profit"]
            if total_time <= check_interval:
                ppm = profit / total_time if total_time else 0
                profitable.append({
                    "product": product,
                    "profit": profit,
                    "time": total_time,
                    "ppm": ppm,
                    "ingredients": result
                })

        # Sort by profit per minute
        profitable.sort(key=lambda x: x["ppm"], reverse=True)
        return profitable
