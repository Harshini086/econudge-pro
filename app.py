import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import numpy as np

# Import custom modules
from utils import (
    calculate_co2_emissions,
    calculate_water_waste,
    calculate_plastic_score,
    calculate_energy_consumption,
    calculate_eco_score,
    get_eco_category,
    generate_eco_nudges,
    generate_energy_nudges
)
from game import (
    initialize_game_state,
    update_streak,
    add_points,
    get_badge,
    display_game_stats
)
from ml_models import (
    initialize_ml_models,
    generate_simulated_history
)

# Page configuration
st.set_page_config(
    page_title="EcoNudge Pro",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'survey_completed' not in st.session_state:
        st.session_state.survey_completed = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    
    # Initialize ML models
    if 'ml_models' not in st.session_state:
        st.session_state.ml_models = initialize_ml_models()
    
    # Initialize user history for ML training
    if 'user_history' not in st.session_state:
        st.session_state.user_history = []
    
    # Initialize game state
    initialize_game_state()

# Navigation
def show_navigation():
    st.sidebar.title("🌱 EcoNudge Pro")
    st.sidebar.markdown("---")
    
    pages = {
        '🏠 Home': 'home',
        '📝 Eco & Energy Survey': 'survey',
        '📊 Impact Dashboard': 'dashboard',
        '🤖 ML Predictions': 'ml_predictions',
        '⚡ Energy Monitor': 'energy',
        '🎮 Game Zone': 'game',
        '🌍 Global Impact': 'global'
    }
    
    for label, page_key in pages.items():
        if st.sidebar.button(label, key=f"nav_{page_key}"):
            st.session_state.page = page_key
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Track. Improve. Sustain.")
    st.sidebar.success("🤖 ML-Powered Insights")

# HOME PAGE
def show_home():
    st.title("🌱 EcoNudge Pro")
    st.subheader("Turn Your Lifestyle Into Impact")
    st.markdown("**Track. Improve. Sustain.**")
    
    st.write("")
    
    st.info("""
    **EcoNudge Pro** is a behavioral change system that:
    
    - 📊 Analyzes your lifestyle and energy consumption
    - 🌍 Quantifies your environmental impact (CO2, water, plastic, energy)
    - 📈 Tracks your daily improvements
    - 🎮 Motivates you through gamification (streaks, points, badges)
    - 💡 Provides real-time personalized eco-nudges
    - ⚡ Alerts you when you exceed energy limits
    - 🤖 Uses ML models to predict future behavior
    """)
    
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("### 🤖\n**ML Predictions**\n\nAI-powered behavior forecasting & recommendations")
    
    with col2:
        st.success("### 🎮\n**Gamification**\n\nStreaks, points, and achievement badges")
    
    with col3:
        st.success("### 💡\n**Smart Nudges**\n\nPersonalized eco & energy recommendations")
    
    st.write("")
    
    if st.button("🚀 Start Your Eco Journey", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 30:
                status_text.text("🌱 Initializing eco engine...")
            elif i < 60:
                status_text.text("📊 Loading impact calculators...")
            elif i < 90:
                status_text.text("🎮 Setting up game zone...")
            else:
                status_text.text("✅ Ready to start!")
            time.sleep(0.01)
        
        time.sleep(0.5)
        st.session_state.page = 'survey'
        st.rerun()

# SURVEY PAGE
def show_survey():
    st.title("📝 Comprehensive Eco & Lifestyle Survey")
    st.write("Tell us about your detailed lifestyle habits for accurate environmental impact analysis and personalized nudges.")
    
    with st.form("eco_survey"):
        # SECTION 1: TRANSPORTATION
        st.markdown("### 🚗 Transportation & Travel")
        col1, col2 = st.columns(2)
        
        with col1:
            transport = st.selectbox(
                "Primary mode of transport:",
                ["Car (Petrol/Diesel)", "Car (Electric)", "Bike/Scooter", "Public Transport", "Walking/Cycling"]
            )
            
            daily_distance = st.number_input(
                "Daily commute distance (km):",
                min_value=0.0,
                max_value=200.0,
                value=10.0,
                step=0.5
            )
        
        with col2:
            weekly_car_trips = st.slider(
                "Car trips per week:",
                min_value=0,
                max_value=50,
                value=7
            )
            
            monthly_flights = st.slider(
                "Flights per month:",
                min_value=0,
                max_value=10,
                value=0
            )
        
        # SECTION 2: ENERGY CONSUMPTION
        st.markdown("### ⚡ Energy & Electricity")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            electricity = st.slider("Daily electricity usage (kWh):", 1, 50, 10)
            ac_hours = st.slider("AC usage (hours/day):", 0, 24, 2)
        
        with col2:
            heating_hours = st.slider("Heating usage (hours/day):", 0, 24, 0)
            device_hours = st.slider("Device usage (hours/day):", 0, 24, 6)
        
        with col3:
            laptop_hours = st.slider("Laptop usage (hours/day):", 0, 24, 8)
            tv_hours = st.slider("TV usage (hours/day):", 0, 12, 2)
        
        # SECTION 3: WATER USAGE
        st.markdown("### 💧 Water Consumption")
        col1, col2 = st.columns(2)
        
        with col1:
            water = st.slider("Daily water consumption (litres):", 50, 500, 150)
            shower_time = st.slider("Daily shower time (minutes):", 0, 60, 10)
        
        with col2:
            washing_machine_weekly = st.slider("Washing machine uses/week:", 0, 20, 3)
            dishwasher_weekly = st.slider("Dishwasher uses/week:", 0, 20, 2)
        
        # SECTION 4: FOOD & DIET
        st.markdown("### 🍽️ Food Habits & Ordering")
        col1, col2 = st.columns(2)
        
        with col1:
            food = st.selectbox(
                "Diet preference:",
                ["Vegetarian", "Vegan", "Mixed (Veg + Non-Veg)", "Pescatarian", "Non-Vegetarian"]
            )
            
            food_waste = st.slider(
                "Food waste per week (% of groceries):",
                min_value=0,
                max_value=50,
                value=10
            )
        
        with col2:
            food_delivery_weekly = st.slider(
                "Food delivery orders per week:",
                min_value=0,
                max_value=30,
                value=3
            )
            
            local_food = st.slider(
                "Local/organic food purchases (%):",
                min_value=0,
                max_value=100,
                value=30
            )
        
        st.write("**Common food ordering times:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            breakfast_delivery = st.checkbox("Breakfast (7-10 AM)")
        with col2:
            lunch_delivery = st.checkbox("Lunch (12-2 PM)", value=True)
        with col3:
            dinner_delivery = st.checkbox("Dinner (7-10 PM)", value=True)
        
        # SECTION 5: SHOPPING & CONSUMPTION
        st.markdown("### 🛍️ Shopping & Consumption Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            shopping_frequency = st.selectbox(
                "Grocery shopping frequency:",
                ["Daily", "2-3 times/week", "Weekly", "Bi-weekly", "Monthly"]
            )
            
            online_shopping_monthly = st.slider(
                "Online shopping orders/month:",
                min_value=0,
                max_value=50,
                value=5
            )
        
        with col2:
            fast_fashion_monthly = st.slider(
                "Fast fashion purchases/month:",
                min_value=0,
                max_value=20,
                value=2
            )
            
            electronics_yearly = st.slider(
                "Electronics purchases/year:",
                min_value=0,
                max_value=20,
                value=2
            )
        
        # SECTION 6: PLASTIC & WASTE
        st.markdown("### ♻️ Plastic & Waste Management")
        col1, col2 = st.columns(2)
        
        with col1:
            plastic = st.radio(
                "Plastic consumption level:",
                ["Low (Reusable bags, bottles)", "Medium (Occasional plastic)", "High (Frequent plastic use)"]
            )
            
            recycling_habit = st.selectbox(
                "Recycling frequency:",
                ["Always", "Usually", "Sometimes", "Rarely", "Never"]
            )
        
        with col2:
            single_use_plastic_weekly = st.slider(
                "Single-use plastic items/week:",
                min_value=0,
                max_value=100,
                value=10
            )
            
            composting = st.selectbox(
                "Do you compost organic waste?",
                ["Yes, always", "Sometimes", "No"]
            )
        
        # SECTION 7: DAILY BEHAVIOR PATTERNS
        st.markdown("### ⏰ Daily Behavior & Timing")
        col1, col2 = st.columns(2)
        
        with col1:
            wake_up_time = st.time_input("Typical wake up time:", value=datetime.strptime("07:00", "%H:%M").time())
            sleep_time = st.time_input("Typical sleep time:", value=datetime.strptime("23:00", "%H:%M").time())
        
        with col2:
            work_from_home = st.slider("Work from home days/week:", 0, 7, 2)
            outdoor_activities_weekly = st.slider("Outdoor activities/week:", 0, 20, 3)
        
        st.write("**Peak energy usage times:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            morning_peak = st.checkbox("Morning (6-9 AM)", value=True)
        with col2:
            afternoon_peak = st.checkbox("Afternoon (12-3 PM)")
        with col3:
            evening_peak = st.checkbox("Evening (6-9 PM)", value=True)
        with col4:
            night_peak = st.checkbox("Night (9 PM-12 AM)")
        
        # SECTION 8: LIFESTYLE CHOICES
        st.markdown("### 🌱 Eco-Friendly Practices")
        col1, col2 = st.columns(2)
        
        with col1:
            renewable_energy = st.selectbox(
                "Do you use renewable energy?",
                ["Yes, 100%", "Partially", "Planning to", "No"]
            )
            
            eco_products = st.slider(
                "Eco-friendly products usage (%):",
                min_value=0,
                max_value=100,
                value=30
            )
        
        with col2:
            plant_based_meals = st.slider(
                "Plant-based meals/week:",
                min_value=0,
                max_value=21,
                value=7
            )
            
            water_conservation = st.selectbox(
                "Water conservation efforts:",
                ["High (rainwater harvesting, etc.)", "Medium (mindful usage)", "Low (no special efforts)"]
            )
        
        submitted = st.form_submit_button("🌱 Calculate My Impact & Get Personalized Nudges", type="primary", use_container_width=True)
        
        if submitted:
            # Store comprehensive data
            st.session_state.user_data = {
                # Transportation
                'transport': transport,
                'daily_distance': daily_distance,
                'weekly_car_trips': weekly_car_trips,
                'monthly_flights': monthly_flights,
                
                # Energy
                'electricity': electricity,
                'ac_hours': ac_hours,
                'heating_hours': heating_hours,
                'device_hours': device_hours,
                'laptop_hours': laptop_hours,
                'tv_hours': tv_hours,
                
                # Water
                'water': water,
                'shower_time': shower_time,
                'washing_machine_weekly': washing_machine_weekly,
                'dishwasher_weekly': dishwasher_weekly,
                
                # Food
                'food': food,
                'food_waste': food_waste,
                'food_delivery_weekly': food_delivery_weekly,
                'local_food': local_food,
                'breakfast_delivery': breakfast_delivery,
                'lunch_delivery': lunch_delivery,
                'dinner_delivery': dinner_delivery,
                
                # Shopping
                'shopping_frequency': shopping_frequency,
                'online_shopping_monthly': online_shopping_monthly,
                'fast_fashion_monthly': fast_fashion_monthly,
                'electronics_yearly': electronics_yearly,
                
                # Plastic & Waste
                'plastic': plastic,
                'recycling_habit': recycling_habit,
                'single_use_plastic_weekly': single_use_plastic_weekly,
                'composting': composting,
                
                # Daily Behavior
                'wake_up_time': wake_up_time,
                'sleep_time': sleep_time,
                'work_from_home': work_from_home,
                'outdoor_activities_weekly': outdoor_activities_weekly,
                'morning_peak': morning_peak,
                'afternoon_peak': afternoon_peak,
                'evening_peak': evening_peak,
                'night_peak': night_peak,
                
                # Lifestyle
                'renewable_energy': renewable_energy,
                'eco_products': eco_products,
                'plant_based_meals': plant_based_meals,
                'water_conservation': water_conservation,
                
                'timestamp': datetime.now()
            }
            
            # Calculate eco score for history
            eco_score = calculate_eco_score(st.session_state.user_data)
            st.session_state.user_data['eco_score'] = eco_score
            
            st.session_state.survey_completed = True
            
            # Generate simulated history for ML model training
            if len(st.session_state.user_history) == 0:
                st.session_state.user_history = generate_simulated_history(
                    st.session_state.user_data, days=30
                )
            
            # Add current data to history
            st.session_state.user_history.append(st.session_state.user_data.copy())
            
            # Train ML models
            ml_models = st.session_state.ml_models
            ml_models['predictor'].train(st.session_state.user_history)
            ml_models['anomaly_detector'].set_baseline(st.session_state.user_history)
            
            # Add points for completing survey
            add_points(50, "Completed comprehensive eco survey")
            update_streak()
            
            st.success("✅ Comprehensive survey completed! ML models trained on your detailed behavior patterns.")
            st.info("🎯 Your personalized insights and time-based nudges are ready!")
            time.sleep(2)
            st.session_state.page = 'dashboard'
            st.rerun()

# DASHBOARD PAGE
def show_dashboard():
    if not st.session_state.survey_completed:
        st.warning("⚠️ Please complete the Eco Survey first!")
        if st.button("Go to Survey"):
            st.session_state.page = 'survey'
            st.rerun()
        return
    
    st.title("📊 Comprehensive Impact Dashboard")
    
    data = st.session_state.user_data
    
    # Import the new function
    from utils import get_behavioral_insights, generate_time_based_nudges
    
    # Calculate metrics
    co2 = calculate_co2_emissions(data)
    water_waste = calculate_water_waste(data)
    plastic_score = calculate_plastic_score(data)
    energy = calculate_energy_consumption(data)
    eco_score = calculate_eco_score(data)
    category = get_eco_category(eco_score)
    
    # Eco Score Display
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.success(f"### 🌱 Your Eco Score: {eco_score}/100")
        st.progress(eco_score / 100)
        st.info(f"**Category:** {category}")
    
    with col2:
        improvement_potential = 100 - eco_score
        st.metric("Improvement Potential", f"{improvement_potential} points")
        st.metric("Survey Completion", "100%")
    
    with col3:
        st.metric("Data Points Tracked", "40+")
        st.metric("Streak", f"{st.session_state.streak} days")
    
    st.write("")
    
    # COMPREHENSIVE METRICS
    st.subheader("📈 Detailed Environmental Impact")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🚗 Transport", "⚡ Energy", "🛍️ Lifestyle"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total CO2", f"{co2:.0f} kg/year", delta=f"-{co2*0.2:.0f} possible")
        with col2:
            st.metric("Water Waste", f"{water_waste:.0f} L/month", delta=f"-{water_waste*0.15:.0f} possible")
        with col3:
            st.metric("Plastic Score", f"{plastic_score}/100", delta="Lower is better")
        with col4:
            st.metric("Energy Usage", f"{energy:.0f} kWh/month", delta=f"-{energy*0.2:.0f} possible")
        
        # Impact Breakdown Chart
        st.write("**Environmental Footprint Breakdown**")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        categories = ['Transport', 'Energy', 'Food', 'Shopping', 'Waste']
        
        # Calculate component-wise CO2
        transport_co2 = data.get('daily_distance', 10) * 365 * 0.21 + data.get('monthly_flights', 0) * 180 * 12
        energy_co2 = (data.get('electricity', 10) + data.get('ac_hours', 2) * 1.5) * 365 * 0.5
        food_co2 = 800 + data.get('food_delivery_weekly', 3) * 52 * 2
        shopping_co2 = data.get('online_shopping_monthly', 5) * 12 + data.get('fast_fashion_monthly', 2) * 120
        waste_co2 = data.get('single_use_plastic_weekly', 10) * 26
        
        values = [transport_co2, energy_co2, food_co2, shopping_co2, waste_co2]
        colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#FF8B94']
        
        bars = ax.barh(categories, values, color=colors, alpha=0.8)
        ax.set_xlabel('CO2 Emissions (kg/year)', fontsize=12, fontweight='bold')
        ax.set_title('Carbon Footprint by Category', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2., 
                   f'{values[i]:.0f} kg',
                   ha='left', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        st.pyplot(fig)
    
    with tab2:
        st.write("**🚗 Transportation Impact**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Daily Distance", f"{data.get('daily_distance', 10)} km")
            st.metric("Primary Transport", data.get('transport', 'Car'))
        with col2:
            st.metric("Car Trips/Week", data.get('weekly_car_trips', 7))
            st.metric("Flights/Month", data.get('monthly_flights', 0))
        with col3:
            transport_co2 = data.get('daily_distance', 10) * 365 * 0.21
            st.metric("Transport CO2", f"{transport_co2:.0f} kg/year")
            potential_save = transport_co2 * 0.5
            st.metric("Potential Savings", f"{potential_save:.0f} kg")
    
    with tab3:
        st.write("**⚡ Energy Consumption Pattern**")
        
        # Energy breakdown by appliance
        appliances = ['Base Electricity', 'AC', 'Heating', 'Devices', 'Laptop', 'TV']
        usage = [
            data.get('electricity', 10) * 30,
            data.get('ac_hours', 2) * 1.5 * 30,
            data.get('heating_hours', 0) * 2 * 30,
            data.get('device_hours', 6) * 0.3 * 30,
            data.get('laptop_hours', 8) * 0.05 * 30,
            data.get('tv_hours', 2) * 0.1 * 30
        ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors_energy = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#C7CEEA', '#FFDAB9']
        wedges, texts, autotexts = ax.pie(usage, labels=appliances, colors=colors_energy, 
                                            autopct='%1.1f%%', startangle=90)
        ax.set_title('Monthly Energy Distribution (kWh)', fontsize=14, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        st.pyplot(fig)
        
        # Peak hour analysis
        st.write("**Peak Usage Hours:**")
        peak_times = []
        if data.get('morning_peak'):
            peak_times.append("Morning (6-9 AM)")
        if data.get('afternoon_peak'):
            peak_times.append("Afternoon (12-3 PM)")
        if data.get('evening_peak'):
            peak_times.append("Evening (6-9 PM)")
        if data.get('night_peak'):
            peak_times.append("Night (9 PM-12 AM)")
        
        if peak_times:
            for time in peak_times:
                st.warning(f"⚡ {time}")
        else:
            st.success("✅ No peak hour concentration - well distributed!")
    
    with tab4:
        st.write("**🛍️ Lifestyle & Shopping Impact**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Food Delivery/Week", data.get('food_delivery_weekly', 3))
            st.metric("Online Orders/Month", data.get('online_shopping_monthly', 5))
            st.metric("Fast Fashion/Month", data.get('fast_fashion_monthly', 2))
            st.metric("Food Waste", f"{data.get('food_waste', 10)}%")
        
        with col2:
            st.metric("Plant-Based Meals/Week", data.get('plant_based_meals', 7))
            st.metric("Local Food Purchases", f"{data.get('local_food', 30)}%")
            st.metric("Recycling Habit", data.get('recycling_habit', 'Sometimes'))
            st.metric("Single-Use Plastic/Week", data.get('single_use_plastic_weekly', 10))
    
    # BEHAVIORAL INSIGHTS
    st.subheader("🧠 Behavioral Insights & Patterns")
    
    insights = get_behavioral_insights(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if insights['high_impact_areas']:
            st.error("**⚠️ High Impact Areas:**")
            for item in insights['high_impact_areas']:
                st.write(f"• {item}")
        
        if insights['improvement_opportunities']:
            st.warning("**📈 Improvement Opportunities:**")
            for item in insights['improvement_opportunities']:
                st.write(f"• {item}")
    
    with col2:
        if insights['positive_habits']:
            st.success("**✅ Positive Habits:**")
            for item in insights['positive_habits']:
                st.write(f"• {item}")
        
        if insights['time_patterns']:
            st.info("**⏰ Time Patterns:**")
            for item in insights['time_patterns']:
                st.write(f"• {item}")
    
    # TIME-BASED NUDGES
    st.subheader("💡 Real-Time Personalized Nudges")
    
    time_nudges = generate_time_based_nudges(data)
    eco_nudges = generate_eco_nudges(data, co2, water_waste, plastic_score)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**⏰ Time-Specific Actions:**")
        for nudge in time_nudges:
            st.info(nudge)
    
    with col2:
        st.write("**🌱 General Eco Tips:**")
        for nudge in eco_nudges[:5]:
            st.success(nudge)
    
    # INTERACTIVE TREND VISUALIZATION
    st.subheader("📈 Your Progress & Predictions")
    
    # Historical + Predicted trend
    days_past = 30
    days_future = 30
    dates_past = [datetime.now() - timedelta(days=days_past-i) for i in range(days_past)]
    dates_future = [datetime.now() + timedelta(days=i) for i in range(1, days_future+1)]
    
    # Simulated historical trend
    base_score = max(eco_score - 15, 30)
    trend_past = [base_score + (i * (eco_score - base_score) / days_past) + ((-1)**i * 2) for i in range(days_past)]
    
    # ML prediction for future
    ml_models = st.session_state.ml_models
    if ml_models['predictor'].is_trained:
        trend_future = ml_models['predictor'].predict_trajectory(data, days=days_future)
    else:
        trend_future = [eco_score + (i * 0.3) + ((-1)**i * 1.5) for i in range(days_future)]
    
    # Combined visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Historical data
    ax.plot(dates_past, trend_past, marker='o', linewidth=2, markersize=3, 
            color='#4CAF50', label='Historical Data', alpha=0.7)
    ax.fill_between(dates_past, trend_past, alpha=0.2, color='#4CAF50')
    
    # Predicted data
    ax.plot(dates_future, trend_future, marker='s', linewidth=2, markersize=3, 
            color='#2196F3', label='ML Prediction', linestyle='--')
    ax.fill_between(dates_future, trend_future, alpha=0.2, color='#2196F3')
    
    # Add vertical line for today
    ax.axvline(x=datetime.now(), color='red', linestyle=':', linewidth=2, label='Today', alpha=0.7)
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Eco Score', fontsize=12, fontweight='bold')
    ax.set_title('60-Day Eco Score Trend: Historical + ML Forecast', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Prediction summary
    col1, col2, col3 = st.columns(3)
    with col1:
        if trend_future:
            st.metric("7-Day Forecast", f"{trend_future[6]:.1f}/100", 
                     delta=f"{trend_future[6] - eco_score:.1f}")
    with col2:
        if trend_future:
            st.metric("30-Day Forecast", f"{trend_future[-1]:.1f}/100",
                     delta=f"{trend_future[-1] - eco_score:.1f}")
    with col3:
        avg_improvement = (trend_future[-1] - eco_score) / 30 if trend_future else 0
        st.metric("Daily Improvement Rate", f"{avg_improvement:.2f} pts/day")

# ML PREDICTIONS PAGE (Simplified)
def show_ml_predictions():
    if not st.session_state.survey_completed:
        st.warning("⚠️ Please complete the Eco Survey first to train ML models!")
        if st.button("Go to Survey"):
            st.session_state.page = 'survey'
            st.rerun()
        return
    
    st.title("🤖 ML-Powered Predictions & Insights")
    st.write("Advanced machine learning models analyze your behavior and predict future trends")
    
    data = st.session_state.user_data
    ml_models = st.session_state.ml_models
    
    # ML Model Status
    st.subheader("🔬 ML Model Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🧠 Predictor", "✅ Trained" if ml_models['predictor'].is_trained else "❌ Not Trained")
    with col2:
        st.metric("🏷️ Classifier", "✅ Active")
    with col3:
        st.metric("⚠️ Anomaly Detector", "✅ Active")
    with col4:
        st.metric("💡 Recommender", "✅ Active")
    
    st.info(f"📊 Models trained on {len(st.session_state.user_history)} data points")
    
    # Behavior Classification
    st.subheader("🏷️ Behavior Classification (K-Means Clustering)")
    
    category, insights = ml_models['classifier'].classify_user(data)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if category == 'Eco Champion':
            st.success(f"## 🌟\n### {category}")
        elif category == 'Eco Improver':
            st.warning(f"## ⚡\n### {category}")
        else:
            st.info(f"## 🌱\n### {category}")
        
        st.write(insights['description'])
    
    with col2:
        st.write("**Your Strengths:**")
        for strength in insights['strengths']:
            st.success(f"✓ {strength}")
        
        st.write("**Next Steps:**")
        for step in insights['next_steps']:
            st.info(f"→ {step}")
    
    # Future Prediction
    st.subheader("📈 Future Eco Score Prediction (Linear Regression)")
    
    if ml_models['predictor'].is_trained:
        trajectory = ml_models['predictor'].predict_trajectory(data, days=30)
        
        if trajectory:
            dates = [(datetime.now() + timedelta(days=i)).strftime('%b %d') for i in range(1, 31)]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(dates[::3], trajectory[::3], marker='o', linewidth=3, 
                   markersize=8, color='#4CAF50', label='Predicted Eco Score')
            ax.fill_between(range(len(dates[::3])), trajectory[::3], alpha=0.3, color='#4CAF50')
            
            upper_bound = [min(100, score + 5) for score in trajectory[::3]]
            lower_bound = [max(0, score - 5) for score in trajectory[::3]]
            ax.fill_between(range(len(dates[::3])), lower_bound, upper_bound, 
                           alpha=0.2, color='#2196F3', label='Confidence Interval')
            
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Eco Score', fontsize=12, fontweight='bold')
            ax.set_title('30-Day Eco Score Forecast (ML Prediction)', fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(dates[::3])))
            ax.set_xticklabels(dates[::3], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            
            st.pyplot(fig)
            
            col1, col2 = st.columns(2)
            with col1:
                future_7d = ml_models['predictor'].predict_future_score(data, days_ahead=7)
                st.metric("7-Day Forecast", f"{future_7d:.1f}/100", 
                         delta=f"{future_7d - data.get('eco_score', 50):.1f}")
            with col2:
                future_30d = ml_models['predictor'].predict_future_score(data, days_ahead=30)
                st.metric("30-Day Forecast", f"{future_30d:.1f}/100",
                         delta=f"{future_30d - data.get('eco_score', 50):.1f}")
    
    # Anomaly Detection
    st.subheader("⚠️ Anomaly Detection (Statistical Analysis)")
    
    anomalies = ml_models['anomaly_detector'].detect_anomalies(data)
    
    if anomalies:
        st.warning(f"🚨 {len(anomalies)} anomal{'y' if len(anomalies) == 1 else 'ies'} detected!")
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                st.error(anomaly['message'])
            else:
                st.success(anomaly['message'])
    else:
        st.success("✅ No unusual patterns detected. Your consumption is within normal range.")
    
    # ML Recommendations
    st.subheader("💡 ML-Based Recommendations (Collaborative Filtering)")
    
    ml_recommendations = ml_models['recommender'].generate_ml_recommendations(data)
    
    if ml_recommendations:
        for rec in ml_recommendations:
            st.info(f"**{rec['category']}:** {rec['suggestion']}\n\n📊 Confidence: {rec['confidence']*100:.0f}% | Impact: {rec['impact']}")

# ENERGY MONITOR PAGE
def show_energy_monitor():
    if not st.session_state.survey_completed:
        st.warning("⚠️ Please complete the Eco Survey first!")
        if st.button("Go to Survey"):
            st.session_state.page = 'survey'
            st.rerun()
        return
    
    st.title("⚡ Energy Monitor")
    st.write("Real-time energy consumption analysis and alerts")
    
    data = st.session_state.user_data
    energy = calculate_energy_consumption(data)
    
    # Energy Status
    st.metric("Total Energy Consumption", f"{energy:.1f} kWh/month", 
             delta=f"{energy - 300:.1f} kWh from optimal")
    
    if energy < 250:
        st.success("✅ Excellent! Your energy usage is optimal.")
        st.progress(energy / 500)
    elif energy < 400:
        st.warning("⚠️ Moderate energy usage. Room for improvement.")
        st.progress(energy / 500)
    else:
        st.error("❌ High energy usage detected! Immediate action recommended.")
        st.progress(min(energy / 500, 1.0))
    
    # Energy breakdown
    st.subheader("🔍 Energy Breakdown")
    
    ac_energy = data['ac_hours'] * 1.5 * 30
    device_energy = data['device_hours'] * 0.3 * 30
    base_energy = data['electricity'] * 30
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("AC Usage", f"{ac_energy:.1f} kWh/month")
        if ac_energy > 100:
            st.error("❌ High AC usage!")
    
    with col2:
        st.metric("Device Usage", f"{device_energy:.1f} kWh/month")
        if device_energy > 150:
            st.warning("⚠️ High device usage")
    
    with col3:
        st.metric("Base Electricity", f"{base_energy:.1f} kWh/month")
    
    # Energy nudges
    st.subheader("💡 Energy Saving Nudges")
    energy_nudges = generate_energy_nudges(data, energy)
    
    for nudge in energy_nudges:
        st.info(f"⚡ {nudge}")

# GAME ZONE PAGE
def show_game_zone():
    st.title("🎮 Game Zone")
    st.write("Track your eco journey with streaks, points, and badges!")
    
    # Display game stats
    display_game_stats()
    
    st.markdown("---")
    
    # Daily Actions
    st.subheader("🎯 Daily Eco Actions")
    st.write("Log your eco-friendly activities to earn points!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚴 Used Public Transport"):
            add_points(15, "Used public transport")
            update_streak()
            st.success("✅ +15 points!")
            time.sleep(1)
            st.rerun()
        
        if st.button("♻️ Recycled Waste"):
            add_points(10, "Recycled waste")
            st.success("✅ +10 points!")
            time.sleep(1)
            st.rerun()
        
        if st.button("💧 Saved Water"):
            add_points(12, "Saved water")
            st.success("✅ +12 points!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("🌱 Planted a Tree"):
            add_points(25, "Planted a tree")
            update_streak()
            st.success("✅ +25 points!")
            time.sleep(1)
            st.rerun()
        
        if st.button("🛍️ Used Reusable Bags"):
            add_points(8, "Used reusable bags")
            st.success("✅ +8 points!")
            time.sleep(1)
            st.rerun()
        
        if st.button("💡 Switched Off Lights"):
            add_points(10, "Saved energy")
            st.success("✅ +10 points!")
            time.sleep(1)
            st.rerun()

# GLOBAL IMPACT PAGE
def show_global_impact():
    st.title("🌍 Global Impact")
    st.write("See how your actions contribute to a larger movement!")
    
    if st.session_state.survey_completed:
        data = st.session_state.user_data
        co2 = calculate_co2_emissions(data)
        water_waste = calculate_water_waste(data)
        energy = calculate_energy_consumption(data)
    else:
        co2 = 500
        water_waste = 1500
        energy = 350
    
    st.subheader("🌟 The Multiplier Effect")
    st.write("If 1,000 users follow your eco habits:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CO2 Saved", f"{(1000 - co2)*1000/1000:.1f} tons/year", 
                 delta="500 trees planted")
    
    with col2:
        st.metric("Water Saved", f"{(2000 - water_waste)*1000/1000:.0f}K liters/month",
                 delta="100 families")
    
    with col3:
        st.metric("Energy Saved", f"{(500 - energy)*1000/1000:.0f}K kWh/month",
                 delta="200 homes")
    
    st.success("""
    **Together, we can make a difference!**
    
    Every small action counts. By tracking your habits and making conscious choices, you:
    - 🌍 Reduce your environmental footprint
    - 🤝 Inspire others to take action
    - 🌱 Contribute to a sustainable future
    """)

# Main app
def main():
    init_session_state()
    show_navigation()
    
    # Route to pages
    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'survey':
        show_survey()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'ml_predictions':
        show_ml_predictions()
    elif st.session_state.page == 'energy':
        show_energy_monitor()
    elif st.session_state.page == 'game':
        show_game_zone()
    elif st.session_state.page == 'global':
        show_global_impact()

if __name__ == "__main__":
    main()