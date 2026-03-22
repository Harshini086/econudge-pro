"""
Utility functions for EcoNudge Pro
Handles all environmental impact calculations
"""

from datetime import datetime

def calculate_co2_emissions(data):
    """
    Calculate annual CO2 emissions in kg based on comprehensive user habits
    """
    co2 = 0
    
    # TRANSPORTATION EMISSIONS (significantly enhanced)
    transport = data.get('transport', 'Car (Petrol/Diesel)')
    daily_distance = data.get('daily_distance', 10)
    weekly_car_trips = data.get('weekly_car_trips', 7)
    monthly_flights = data.get('monthly_flights', 0)
    
    # Base transport emissions
    if 'Car (Petrol/Diesel)' in transport:
        # 0.21 kg CO2 per km for petrol car
        co2 += daily_distance * 365 * 0.21
    elif 'Car (Electric)' in transport:
        # 0.05 kg CO2 per km for electric car (considering power generation)
        co2 += daily_distance * 365 * 0.05
    elif 'Bike/Scooter' in transport:
        # 0.06 kg CO2 per km for scooter
        co2 += daily_distance * 365 * 0.06
    elif 'Public Transport' in transport:
        # 0.04 kg CO2 per km for public transport
        co2 += daily_distance * 365 * 0.04
    else:  # Walking/Cycling
        co2 += 0
    
    # Additional car trips impact
    co2 += weekly_car_trips * 52 * 5 * 0.21  # Assuming 5km per trip
    
    # Flight emissions (90 kg CO2 per hour of flight, average 2 hours per flight)
    co2 += monthly_flights * 12 * 180
    
    # ENERGY EMISSIONS (enhanced)
    electricity = data.get('electricity', 10)
    ac_hours = data.get('ac_hours', 2)
    heating_hours = data.get('heating_hours', 0)
    device_hours = data.get('device_hours', 6)
    laptop_hours = data.get('laptop_hours', 8)
    tv_hours = data.get('tv_hours', 2)
    
    # Electricity CO2 (0.5 kg CO2 per kWh)
    electricity_annual = electricity * 365 * 0.5
    co2 += electricity_annual
    
    # AC usage (1.5 kW)
    ac_emissions = ac_hours * 1.5 * 365 * 0.5
    co2 += ac_emissions
    
    # Heating usage (2 kW)
    heating_emissions = heating_hours * 2 * 365 * 0.5
    co2 += heating_emissions
    
    # Device usage (0.3 kW average)
    device_emissions = device_hours * 0.3 * 365 * 0.5
    co2 += device_emissions
    
    # Laptop usage (0.05 kW)
    laptop_emissions = laptop_hours * 0.05 * 365 * 0.5
    co2 += laptop_emissions
    
    # TV usage (0.1 kW)
    tv_emissions = tv_hours * 0.1 * 365 * 0.5
    co2 += tv_emissions
    
    # FOOD EMISSIONS (enhanced)
    food = data.get('food', 'Mixed')
    food_delivery_weekly = data.get('food_delivery_weekly', 3)
    food_waste = data.get('food_waste', 10)
    local_food = data.get('local_food', 30)
    plant_based_meals = data.get('plant_based_meals', 7)
    
    # Base food emissions
    if 'Vegan' in food:
        co2 += 200
    elif 'Vegetarian' in food:
        co2 += 400
    elif 'Pescatarian' in food:
        co2 += 600
    elif 'Mixed' in food:
        co2 += 800
    else:  # Non-Vegetarian
        co2 += 1500
    
    # Food delivery impact (packaging + transport: 2kg per order)
    co2 += food_delivery_weekly * 52 * 2
    
    # Food waste impact (1kg CO2 per % of waste)
    co2 += food_waste * 10
    
    # Local food reduces emissions
    co2 -= (local_food / 100) * 100
    
    # Plant-based meals reduction (save 2kg CO2 per meal)
    co2 -= plant_based_meals * 52 * 2
    
    # SHOPPING EMISSIONS
    online_shopping_monthly = data.get('online_shopping_monthly', 5)
    fast_fashion_monthly = data.get('fast_fashion_monthly', 2)
    electronics_yearly = data.get('electronics_yearly', 2)
    
    # Online shopping (packaging + delivery: 1kg per order)
    co2 += online_shopping_monthly * 12 * 1
    
    # Fast fashion (10kg CO2 per item)
    co2 += fast_fashion_monthly * 12 * 10
    
    # Electronics (50kg CO2 per device)
    co2 += electronics_yearly * 50
    
    # WASTE & PLASTIC
    single_use_plastic_weekly = data.get('single_use_plastic_weekly', 10)
    recycling_habit = data.get('recycling_habit', 'Sometimes')
    composting = data.get('composting', 'No')
    
    # Single-use plastic (0.5kg CO2 per item)
    co2 += single_use_plastic_weekly * 52 * 0.5
    
    # Recycling benefits
    recycling_map = {
        'Always': -100,
        'Usually': -50,
        'Sometimes': -20,
        'Rarely': 0,
        'Never': 50
    }
    co2 += recycling_map.get(recycling_habit, 0)
    
    # Composting benefits
    if 'Yes' in composting:
        co2 -= 50
    
    # RENEWABLE ENERGY BENEFIT
    renewable_energy = data.get('renewable_energy', 'No')
    if '100%' in renewable_energy:
        co2 *= 0.5  # 50% reduction
    elif 'Partially' in renewable_energy:
        co2 *= 0.75  # 25% reduction
    
    return max(0, round(co2, 2))


def calculate_water_waste(data):
    """
    Calculate monthly water waste in litres based on comprehensive usage patterns
    """
    # Base daily water
    daily_water = data.get('water', 150)
    monthly_water = daily_water * 30
    
    # Shower water usage (8 liters per minute)
    shower_time = data.get('shower_time', 10)
    shower_water = shower_time * 8 * 30
    
    # Washing machine (50 liters per use)
    washing_machine_weekly = data.get('washing_machine_weekly', 3)
    washing_water = washing_machine_weekly * 4 * 50
    
    # Dishwasher (15 liters per use)
    dishwasher_weekly = data.get('dishwasher_weekly', 2)
    dishwasher_water = dishwasher_weekly * 4 * 15
    
    # Total monthly consumption
    total_monthly = monthly_water + shower_water + washing_water + dishwasher_water
    
    # Calculate waste based on conservation efforts
    water_conservation = data.get('water_conservation', 'Medium (mindful usage)')
    
    if 'High' in water_conservation:
        waste_factor = 0.10  # Only 10% waste
    elif 'Medium' in water_conservation:
        waste_factor = 0.20  # 20% waste
    else:  # Low
        waste_factor = 0.35  # 35% waste
    
    # Adjust for high usage
    if daily_water > 300:
        waste_factor += 0.15
    
    water_waste = total_monthly * waste_factor
    
    return round(water_waste, 2)


def calculate_plastic_score(data):
    """
    Calculate plastic usage score (0-100, higher is worse)
    """
    plastic = data['plastic']
    
    if 'Low' in plastic:
        return 20
    elif 'Medium' in plastic:
        return 50
    else:  # High
        return 80


def calculate_energy_consumption(data):
    """
    Calculate monthly energy consumption in kWh
    """
    # Base electricity
    base = data['electricity'] * 30
    
    # AC usage (1.5 kW average)
    ac = data['ac_hours'] * 1.5 * 30
    
    # Device usage (0.3 kW average)
    devices = data['device_hours'] * 0.3 * 30
    
    total_energy = base + ac + devices
    
    return round(total_energy, 2)


def calculate_eco_score(data):
    """
    Calculate overall eco score (0-100, higher is better)
    """
    score = 100
    
    # Transport penalty
    transport = data['transport']
    if 'Car (Petrol/Diesel)' in transport:
        score -= 25
    elif 'Car (Electric)' in transport:
        score -= 10
    elif 'Bike/Scooter' in transport:
        score -= 15
    elif 'Public Transport' in transport:
        score -= 5
    # Walking/Cycling: no penalty
    
    # Electricity penalty
    if data['electricity'] > 20:
        score -= 20
    elif data['electricity'] > 10:
        score -= 10
    
    # AC penalty
    if data['ac_hours'] > 8:
        score -= 15
    elif data['ac_hours'] > 4:
        score -= 8
    
    # Water penalty
    if data['water'] > 300:
        score -= 15
    elif data['water'] > 200:
        score -= 8
    
    # Plastic penalty
    plastic = data['plastic']
    if 'High' in plastic:
        score -= 20
    elif 'Medium' in plastic:
        score -= 10
    
    # Food penalty
    food = data['food']
    if 'Non-Vegetarian' in food:
        score -= 15
    elif 'Mixed' in food:
        score -= 8
    
    # Ensure score is in range
    score = max(0, min(100, score))
    
    return score


def get_eco_category(score):
    """
    Get eco category based on score
    """
    if score >= 70:
        return "🌟 Eco Hero"
    elif score >= 40:
        return "⚡ Eco Improver"
    else:
        return "❌ Eco Beginner"


def generate_eco_nudges(data, co2, water_waste, plastic_score):
    """
    Generate personalized eco-friendly suggestions based on comprehensive data
    """
    nudges = []
    
    # TRANSPORTATION NUDGES
    transport = data.get('transport', 'Car')
    daily_distance = data.get('daily_distance', 10)
    weekly_car_trips = data.get('weekly_car_trips', 7)
    monthly_flights = data.get('monthly_flights', 0)
    
    if 'Car' in transport and 'Electric' not in transport:
        savings = daily_distance * 365 * 0.16  # 0.21 - 0.05 = 0.16 kg saved if switched to electric
        nudges.append(f"🚗 Switch to electric vehicle → save {savings:.0f}kg CO2/year")
        nudges.append(f"🚴 Walk/bike for trips under 3km → reduce {weekly_car_trips * 3} trips/year")
    
    if daily_distance > 20:
        nudges.append(f"🚌 Use public transport 2 days/week → save {daily_distance * 2 * 52 * 0.17:.0f}kg CO2/year")
    
    if monthly_flights > 0:
        nudges.append(f"✈️ Reduce {monthly_flights} flights by video conferencing → save {monthly_flights * 180:.0f}kg CO2/month")
    
    # ENERGY NUDGES (TIME-BASED)
    electricity = data.get('electricity', 10)
    ac_hours = data.get('ac_hours', 2)
    heating_hours = data.get('heating_hours', 0)
    morning_peak = data.get('morning_peak', False)
    evening_peak = data.get('evening_peak', False)
    night_peak = data.get('night_peak', False)
    
    if electricity > 15:
        savings = (electricity - 12) * 30 * 0.5
        nudges.append(f"⚡ Reduce daily electricity by 3 kWh → save {savings:.0f}kg CO2/month")
    
    if ac_hours > 4:
        nudges.append(f"❄️ Reduce AC by 1 hour/day → save {1.5 * 30 * 0.5:.0f}kg CO2/month")
        nudges.append("🌡️ Set AC to 24°C instead of 18°C → save 30% energy")
    
    if morning_peak and evening_peak and night_peak:
        nudges.append("⏰ Avoid triple peak hours → switch heavy appliances to off-peak (10 PM-6 AM)")
    
    # FOOD & ORDERING NUDGES (TIME-BASED)
    food_delivery_weekly = data.get('food_delivery_weekly', 3)
    breakfast_delivery = data.get('breakfast_delivery', False)
    lunch_delivery = data.get('lunch_delivery', False)
    dinner_delivery = data.get('dinner_delivery', False)
    food_waste = data.get('food_waste', 10)
    plant_based_meals = data.get('plant_based_meals', 7)
    
    if food_delivery_weekly > 5:
        nudges.append(f"🍳 Reduce food delivery from {food_delivery_weekly} to 3 orders/week → save {(food_delivery_weekly - 3) * 52 * 2:.0f}kg CO2/year")
    
    if breakfast_delivery or lunch_delivery or dinner_delivery:
        times = []
        if breakfast_delivery:
            times.append("breakfast")
        if lunch_delivery:
            times.append("lunch")
        if dinner_delivery:
            times.append("dinner")
        nudges.append(f"🥗 Meal prep for {', '.join(times)} → save delivery emissions & plastic packaging")
    
    if food_waste > 20:
        nudges.append(f"♻️ Reduce food waste from {food_waste}% to 10% → save {(food_waste - 10) * 10:.0f}kg CO2/year")
    
    if plant_based_meals < 10:
        nudges.append(f"🌱 Add 3 more plant-based meals/week → save {3 * 52 * 2:.0f}kg CO2/year")
    
    # SHOPPING NUDGES
    online_shopping_monthly = data.get('online_shopping_monthly', 5)
    fast_fashion_monthly = data.get('fast_fashion_monthly', 2)
    shopping_frequency = data.get('shopping_frequency', 'Weekly')
    
    if online_shopping_monthly > 10:
        nudges.append(f"📦 Batch online orders → reduce from {online_shopping_monthly} to 5 orders/month")
    
    if fast_fashion_monthly > 3:
        nudges.append(f"👕 Reduce fast fashion by 50% → save {fast_fashion_monthly * 6 * 10:.0f}kg CO2/year")
    
    if shopping_frequency == 'Daily':
        nudges.append("🛒 Switch to weekly grocery shopping → reduce transport emissions")
    
    # WATER NUDGES
    shower_time = data.get('shower_time', 10)
    washing_machine_weekly = data.get('washing_machine_weekly', 3)
    
    if shower_time > 10:
        nudges.append(f"🚿 Reduce shower time by 2 min → save {2 * 8 * 30:.0f}L water/month")
    
    if washing_machine_weekly > 5:
        nudges.append("👔 Batch laundry loads → reduce water & energy usage")
    
    # PLASTIC NUDGES
    single_use_plastic_weekly = data.get('single_use_plastic_weekly', 10)
    recycling_habit = data.get('recycling_habit', 'Sometimes')
    
    if single_use_plastic_weekly > 15:
        nudges.append(f"♻️ Cut single-use plastic from {single_use_plastic_weekly} to 5 items/week")
    
    if recycling_habit != 'Always':
        nudges.append("📋 Start consistent recycling → reduce {:.0f}kg CO2/year".format(100 if recycling_habit == 'Never' else 50))
    
    # GENERAL NUDGES
    renewable_energy = data.get('renewable_energy', 'No')
    eco_products = data.get('eco_products', 30)
    
    if 'No' in renewable_energy:
        nudges.append("☀️ Switch to renewable energy → cut emissions by 50%")
    
    if eco_products < 50:
        nudges.append(f"🌿 Increase eco-friendly products from {eco_products}% to 70%")
    
    return nudges[:8]  # Return top 8 nudges


def generate_energy_nudges(data, total_energy):
    """
    Generate personalized energy-saving suggestions
    """
    nudges = []
    
    # AC-specific nudges
    if data.get('ac_hours', 2) > 6:
        nudges.append("Set AC to 24°C instead of 18°C → save 30% energy")
        nudges.append("Use ceiling fans alongside AC to reduce runtime by 2 hours")
    elif data.get('ac_hours', 2) > 3:
        nudges.append("Clean AC filters monthly for 15% better efficiency")
    
    # Device nudges
    if data.get('device_hours', 6) > 8:
        nudges.append("Enable power-saving mode on all devices")
        nudges.append("Unplug chargers when not in use → prevent phantom power drain")
    
    # General energy nudges
    if data.get('electricity', 10) > 15:
        nudges.append("Switch to 5-star rated appliances for long-term savings")
        nudges.append("Use natural light during daytime to reduce electricity usage")
    
    # Time-of-day nudges
    nudges.append("Run heavy appliances during off-peak hours (10 PM - 6 AM)")
    nudges.append("Install a smart meter to track real-time energy consumption")
    
    # Solar suggestion
    if total_energy > 400:
        nudges.append("Consider installing solar panels → reduce bills by 70%")
    
    return nudges[:5]


def generate_time_based_nudges(data):
    """
    Generate time-specific behavioral nudges based on user's daily patterns
    """
    nudges = []
    current_hour = datetime.now().hour
    
    # Get user's behavior patterns
    wake_up_time = data.get('wake_up_time', datetime.strptime("07:00", "%H:%M").time())
    sleep_time = data.get('sleep_time', datetime.strptime("23:00", "%H:%M").time())
    breakfast_delivery = data.get('breakfast_delivery', False)
    lunch_delivery = data.get('lunch_delivery', False)
    dinner_delivery = data.get('dinner_delivery', False)
    food_delivery_weekly = data.get('food_delivery_weekly', 3)
    
    # Morning nudges (6 AM - 12 PM)
    if 6 <= current_hour < 12:
        if breakfast_delivery:
            nudges.append("☀️ MORNING TIP: Prepare breakfast at home instead of ordering → save packaging & emissions")
        
        nudges.append("💡 Turn off lights and devices you left on overnight")
        
        if wake_up_time.hour < 7 and current_hour >= 7:
            nudges.append("🌅 Good morning! Start your day with a sustainable choice")
    
    # Afternoon nudges (12 PM - 5 PM)
    elif 12 <= current_hour < 17:
        if lunch_delivery:
            nudges.append("🍱 LUNCH TIME: Pack lunch or eat local → reduce {:.0f}kg CO2/year".format(food_delivery_weekly * 52 * 0.5))
        
        nudges.append("☀️ Use natural light instead of indoor lights")
        nudges.append("🌡️ Avoid using AC during cooler afternoon hours")
    
    # Evening nudges (5 PM - 10 PM)
    elif 17 <= current_hour < 22:
        if dinner_delivery:
            nudges.append("🍽️ DINNER TIME: Home-cooked meal → saves delivery emissions & healthier!")
        
        peak_usage = data.get('evening_peak', False)
        if peak_usage:
            nudges.append("⚡ PEAK HOUR ALERT: You're in your high-energy usage window")
            nudges.append("💡 Postpone heavy appliances (washing machine, dishwasher) to after 10 PM")
        
        nudges.append("🔋 Charge devices now for use during off-peak hours")
    
    # Night nudges (10 PM - 6 AM)
    else:
        if current_hour >= 22:
            nudges.append("🌙 NIGHT TIP: Switch to energy-saving mode on all devices")
            nudges.append("💤 Unplug unnecessary devices before sleep")
            
            if sleep_time.hour <= current_hour:
                nudges.append("🛏️ Bedtime reminder: Turn off all lights and AC")
        
        nudges.append("⚡ OFF-PEAK HOURS: Best time to run washing machine & dishwasher")
    
    # Day-specific nudges
    day_of_week = datetime.now().strftime('%A')
    
    if day_of_week == 'Monday':
        nudges.append("🌱 MEATLESS MONDAY: Try a plant-based meal today!")
    elif day_of_week == 'Wednesday':
        nudges.append("🚴 BIKE WEDNESDAY: Use sustainable transport today")
    elif day_of_week == 'Friday':
        nudges.append("♻️ RECYCLING DAY: Sort your recyclables this weekend")
    
    # Shopping behavior nudges
    online_shopping = data.get('online_shopping_monthly', 5)
    if online_shopping > 10:
        nudges.append("📦 Batch your online orders this week instead of daily purchases")
    
    return nudges[:5]


def get_behavioral_insights(data):
    """
    Generate comprehensive behavioral insights based on patterns
    """
    insights = {
        'high_impact_areas': [],
        'positive_habits': [],
        'improvement_opportunities': [],
        'time_patterns': []
    }
    
    # Analyze high impact areas
    if data.get('monthly_flights', 0) > 2:
        insights['high_impact_areas'].append("✈️ Frequent flying is your biggest carbon contributor")
    
    if data.get('food_delivery_weekly', 3) > 7:
        insights['high_impact_areas'].append("🍕 Daily food delivery significantly increases your footprint")
    
    if data.get('ac_hours', 2) > 8:
        insights['high_impact_areas'].append("❄️ Extended AC usage is a major energy consumer")
    
    # Identify positive habits
    if data.get('plant_based_meals', 7) > 10:
        insights['positive_habits'].append("🌱 Excellent plant-based meal frequency!")
    
    if data.get('work_from_home', 2) > 4:
        insights['positive_habits'].append("🏠 Working from home reduces commute emissions")
    
    if 'Always' in data.get('recycling_habit', ''):
        insights['positive_habits'].append("♻️ Consistent recycling habits - great job!")
    
    if data.get('renewable_energy', 'No') != 'No':
        insights['positive_habits'].append("☀️ Using renewable energy - fantastic!")
    
    # Improvement opportunities
    if data.get('single_use_plastic_weekly', 10) > 15:
        insights['improvement_opportunities'].append("Reduce single-use plastic by carrying reusable items")
    
    if data.get('food_waste', 10) > 20:
        insights['improvement_opportunities'].append("Meal planning can significantly reduce food waste")
    
    if data.get('fast_fashion_monthly', 2) > 5:
        insights['improvement_opportunities'].append("Consider sustainable fashion alternatives")
    
    # Time pattern analysis
    peak_count = sum([
        data.get('morning_peak', False),
        data.get('afternoon_peak', False),
        data.get('evening_peak', False),
        data.get('night_peak', False)
    ])
    
    if peak_count >= 3:
        insights['time_patterns'].append("⚡ High energy usage across multiple time periods")
    
    if data.get('breakfast_delivery', False) and data.get('lunch_delivery', False) and data.get('dinner_delivery', False):
        insights['time_patterns'].append("🍽️ Food delivery pattern: All three meals - high impact")
    
    return insights
