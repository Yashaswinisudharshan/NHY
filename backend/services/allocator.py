def get_inflation_multiplier(inflation_rate: float) -> float:
    """
    Adjusts the allocation upward based on inflation.
    
    Why? If inflation is 6%, then last year's ₹1L budget is now worth only ₹94K 
    in real terms. So we need to give MORE money just to maintain the same 
    purchasing power.
    
    Example: inflation_rate = 6.0 → multiplier = 1.06
    Meaning the department needs 6% more just to stay at the same level.
    """
    return 1 + (inflation_rate / 100)


def get_efficiency_score(amount_allocated_last_year: float, 
                          amount_utilized: float) -> float:
    """
    Measures how well a department used last year's budget.
    
    Why does this matter? 
    - If a dept got ₹10L and used ₹9.5L (95%) → they clearly needed it, give more
    - If a dept got ₹10L and used ₹4L (40%) → they over-asked, be conservative
    
    Score range: 0.4 to 1.0
    - We never go below 0.4 (even bad depts get something)
    - We never go above 1.0 (efficiency alone can't inflate the budget)
    
    Formula: utilization ratio, clipped between 0.4 and 1.0
    """
    if amount_allocated_last_year <= 0:
        return 0.7  # no history = neutral score
    
    utilization = amount_utilized / amount_allocated_last_year
    return round(max(0.4, min(utilization, 1.0)), 2)


def get_priority_weight(priority_score: float) -> float:
    """
    Converts a 1-10 admin-set priority into a multiplier.
    
    Priority 1  → weight 0.55 (low priority, get 55% of adjusted request)
    Priority 5  → weight 0.75 (medium)
    Priority 10 → weight 1.0  (critical dept, get full adjusted request)
    
    Formula: linear scale from 0.55 to 1.0
    """
    return round(0.55 + (priority_score / 10) * 0.45, 2)


def generate_ai_recommendation(dept_name: str, requested: float, 
                                 final_allocation: float, inflation_rate: float,
                                 efficiency_score: float, 
                                 priority_score: float) -> str:
    """
    Generates a human-readable policy recommendation explaining WHY 
    this allocation was made.
    
    This is rule-based AI — we use if/else logic based on the scores
    to generate intelligent-sounding, accurate policy text.
    
    Why rule-based instead of a model? 
    - Faster, no API needed, fully explainable
    - For government systems, explainability > black box ML
    """
    
    lines = []
    
    # Inflation commentary
    if inflation_rate > 7:
        lines.append(
            f"High inflation ({inflation_rate}%) significantly impacts {dept_name}'s "
            f"purchasing power, requiring a larger allocation to maintain service levels."
        )
    elif inflation_rate > 4:
        lines.append(
            f"Moderate inflation ({inflation_rate}%) has been factored into the "
            f"allocation to preserve {dept_name}'s operational capacity."
        )
    else:
        lines.append(
            f"Inflation remains low ({inflation_rate}%), minimizing cost-pressure "
            f"on {dept_name}'s budget."
        )
    
    # Efficiency commentary
    if efficiency_score >= 0.85:
        lines.append(
            f"{dept_name} demonstrated strong budget utilization ({int(efficiency_score*100)}%), "
            f"indicating high operational efficiency and genuine need."
        )
    elif efficiency_score >= 0.6:
        lines.append(
            f"{dept_name} showed moderate utilization ({int(efficiency_score*100)}%). "
            f"Allocation has been adjusted to encourage better fund usage."
        )
    else:
        lines.append(
            f"{dept_name} had low utilization ({int(efficiency_score*100)}%) last year. "
            f"Allocation is conservative until efficiency improves."
        )
    
    # Priority commentary
    if priority_score >= 8:
        lines.append(
            f"As a high-priority department (score: {priority_score}/10), "
            f"{dept_name} receives preferential budget treatment."
        )
    elif priority_score >= 5:
        lines.append(
            f"{dept_name} holds medium priority (score: {priority_score}/10) "
            f"in the current fiscal plan."
        )
    else:
        lines.append(
            f"{dept_name} is currently low priority (score: {priority_score}/10). "
            f"Budget has been allocated conservatively."
        )
    
    # Final verdict
    coverage = round((final_allocation / requested) * 100, 1) if requested > 0 else 0
    lines.append(
        f"Recommended allocation: ₹{final_allocation:,.2f} "
        f"({coverage}% of requested ₹{requested:,.2f})."
    )
    
    return " ".join(lines)


def calculate_allocation(requested_amount: float, priority_score: float,
                          annual_budget_limit: float, 
                          amount_allocated_last_year: float,
                          amount_utilized_last_year: float,
                          inflation_rate: float) -> dict:
    """
    Master allocation function — brings all factors together.
    
    Returns a dict with:
    - final_allocation: the actual number
    - inflation_multiplier: how much inflation pushed it up
    - efficiency_score: how well they used last year's budget
    - priority_weight: how important this dept is
    - recommendation: AI-generated policy text
    """
    
    # Step 1: Start with what they asked for
    base = requested_amount
    
    # Step 2: Adjust for inflation (prices went up, so give more)
    inflation_mult = get_inflation_multiplier(inflation_rate)
    inflation_adjusted = base * inflation_mult
    
    # Step 3: Apply efficiency score (did they actually use last year's budget?)
    efficiency = get_efficiency_score(amount_allocated_last_year, amount_utilized_last_year)
    efficiency_adjusted = inflation_adjusted * efficiency
    
    # Step 4: Apply priority weight (how critical is this department?)
    priority_w = get_priority_weight(priority_score)
    final = efficiency_adjusted * priority_w
    
    # Step 5: Hard cap — never exceed annual budget limit
    final = round(min(final, annual_budget_limit), 2)
    
    return {
        "final_allocation": final,
        "inflation_multiplier": inflation_mult,
        "efficiency_score": efficiency,
        "priority_weight": priority_w,
        "breakdown": {
            "step1_requested": requested_amount,
            "step2_after_inflation": round(inflation_adjusted, 2),
            "step3_after_efficiency": round(efficiency_adjusted, 2),
            "step4_after_priority": round(final, 2)
        }
    }