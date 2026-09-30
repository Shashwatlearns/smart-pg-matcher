def calculate_pg_match_score(student: dict, pg: dict) -> dict:
    # 1. Budget Score (reward savings, penalize overages)
    budget = student['budget']
    rent = pg['rent']
    if rent > budget:
        penalty = ((rent - budget) / budget) * 100
        budget_score = max(0.0, 100.0 - (penalty * 1.5))
    else:
        savings_ratio = (budget - rent) / budget
        budget_score = 80.0 + (savings_ratio * 20.0)

    # 2. Distance Score (reward closer PGs, penalize far ones)
    max_dist = student['max_distance_km']
    actual_dist = pg['distance_km']
    if actual_dist > max_dist:
        penalty = ((actual_dist - max_dist) / max_dist) * 100
        distance_score = max(0.0, 100.0 - (penalty * 1.5))
    else:
        closeness_ratio = (max_dist - actual_dist) / max_dist
        distance_score = 80.0 + (closeness_ratio * 20.0)

    # 3. Area Match (all or nothing)
    if student['preferred_area'].lower() == pg['area'].lower():
        area_score = 100.0
    else:
        area_score = 0.0

    # 4. Amenities Score
    # AC is stored in its own column (ac_available), not inside amenities_set.
    # Copy the set, then add "AC" so a student asking for AC can match it.
    req_amenities = set(student['amenities_set'])
    pg_amenities = set(pg['amenities_set'])
    if pg.get('ac_available'):
        pg_amenities.add("AC")

    if not req_amenities:
        amenities_score = 100.0
    else:
        satisfied = req_amenities & pg_amenities
        amenities_score = (len(satisfied) / len(req_amenities)) * 100.0

    # 5. Food Preference Score
    s_food = student['food_pref']
    p_food = pg['food_offered']
    if s_food == "Any" or p_food == "Any" or s_food == p_food:
        food_score = 100.0
    else:
        food_score = 0.0

    overall_score = (
        (budget_score * 0.35) +
        (distance_score * 0.20) +
        (area_score * 0.20) +
        (amenities_score * 0.15) +
        (food_score * 0.10)
    )

    return {
        "overall_score": round(overall_score, 2),
        "breakdown": {
            "budget_score": round(budget_score, 2),
            "distance_score": round(distance_score, 2),
            "area_score": round(area_score, 2),
            "amenities_score": round(amenities_score, 2),
            "food_score": round(food_score, 2)
        }
    }


def calculate_flatmate_match_score(student1: dict, student2: dict) -> float:
    """
    Flatmate compatibility between two students, from 0.0 to 100.0.
    """
    # 1. Budget Compatibility
    max_budget = max(student1['budget'], student2['budget'])
    budget_diff = abs(student1['budget'] - student2['budget'])
    budget_score = 100.0 - ((budget_diff / max_budget) * 100)

    # 2. Habits (Jaccard similarity: shared / total unique)
    habits1 = set(student1['habits_set'])
    habits2 = set(student2['habits_set'])
    union_habits = habits1 | habits2
    if not union_habits:
        habits_score = 100.0
    else:
        shared_habits = habits1 & habits2
        habits_score = (len(shared_habits) / len(union_habits)) * 100.0

    # 3. Sleep Schedule
    s1_sleep = student1['sleep_schedule']
    s2_sleep = student2['sleep_schedule']
    if s1_sleep == s2_sleep:
        sleep_score = 100.0
    elif s1_sleep == "Flexible" or s2_sleep == "Flexible":
        sleep_score = 75.0
    else:
        sleep_score = 0.0

    # 4. Food
    s1_food = student1['food_pref']
    s2_food = student2['food_pref']
    if s1_food == s2_food or s1_food == "Any" or s2_food == "Any":
        food_score = 100.0
    else:
        food_score = 0.0

    overall_score = (
        (budget_score * 0.25) +
        (habits_score * 0.35) +
        (sleep_score * 0.25) +
        (food_score * 0.15)
    )

    return round(overall_score, 2)