BUS_TYPE_MULTIPLIERS = {
    'Non-AC Standard': 1.0,
    'Express': 1.2,
    'AC Standard': 1.5,
    'Luxury Sleeper': 1.8
}

PASS_TYPE_FARES = {
    'DAILY': 150.0,
    'WEEKLY': 800.0,
    'MONTHLY': 2500.0
}

def calculate_ticket_fare(distance_km, base_price, bus_type='Express', has_active_pass=False):
    """
    Calculates ticket fare based on distance, bus pricing, and active pass discount.
    """
    multiplier = BUS_TYPE_MULTIPLIERS.get(bus_type, 1.0)
    calculated = (base_price + (distance_km * 1.5)) * multiplier
    
    if has_active_pass:
        # Pass holders get a 50% discount on single ride bookings
        calculated = calculated * 0.5
        
    return round(max(calculated, 20.0), 2)

def calculate_pass_fare(pass_type):
    """
    Returns standard fixed fare for daily, weekly, or monthly bus passes.
    """
    return PASS_TYPE_FARES.get(pass_type.upper(), 500.0)
