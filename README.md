# 🌱 EcoNudge Pro - Gamified Sustainability Tracker

## Overview

**EcoNudge Pro** is a production-level Streamlit web application that transforms sustainability tracking into an engaging, game-like experience. It's designed to change user behavior through behavioral psychology, real-time feedback, and gamification.

## 🎯 Key Features

### 1. **Comprehensive Impact Tracking**
- CO2 emissions calculation
- Water waste monitoring
- Plastic usage scoring
- Energy consumption analysis

### 2. **Energy Monitoring System**
- Real-time energy usage alerts
- Threshold-based warnings
- Detailed consumption breakdown
- Energy-saving recommendations

### 3. **Gamification Engine**
- Daily streak tracking
- Points system for eco-friendly actions
- Achievement badges and milestones
- Level progression system
- Global leaderboard

### 4. **Smart Eco Nudges**
- Personalized recommendations based on user habits
- Energy-saving tips
- Actionable, specific suggestions
- Real-world impact equivalents

### 5. **Visual Analytics**
- Interactive charts and graphs
- Impact comparison visualizations
- Trend analysis over time
- Good vs bad habit breakdown

### 6. **Global Impact View**
- Multiplier effect calculations
- Community impact visualization
- Real-world equivalents (trees, electricity, etc.)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or download the project files**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Access the app**
Open your browser and navigate to:
```
http://localhost:8501
```

## 📂 Project Structure

```
econudge-pro/
│
├── app.py                 # Main Streamlit application
├── utils.py              # Impact calculation functions
├── game.py               # Gamification logic
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎮 How to Use

### Step 1: Home Page
- Start on the landing page
- Click "Start Your Eco Journey"

### Step 2: Complete the Survey
- Navigate to "📝 Eco & Energy Survey"
- Fill in your lifestyle and energy habits:
  - Transportation method
  - Electricity usage
  - AC and device usage
  - Water consumption
  - Plastic usage
  - Food preferences

### Step 3: View Your Impact
- Go to "📊 Impact Dashboard"
- See your Eco Score (0-100)
- View detailed metrics
- Get personalized eco-nudges

### Step 4: Monitor Energy
- Visit "⚡ Energy Monitor"
- Check your energy consumption status
- Receive alerts if usage is high
- Get energy-saving recommendations

### Step 5: Play the Game
- Navigate to "🎮 Game Zone"
- Log daily eco-friendly activities
- Earn points and maintain streaks
- Unlock achievement badges
- Compete on the global leaderboard

### Step 6: See Global Impact
- Check "🌍 Global Impact"
- Understand the multiplier effect
- See community growth
- View real-world equivalents

## 🧠 Behavioral Psychology Features

The app leverages proven psychological triggers:

1. **Curiosity** → Eco Score + detailed insights
2. **Motivation** → Streaks, points, and rewards
3. **Awareness** → Impact metrics and comparisons
4. **Habit Formation** → Daily tracking and nudges

## 📊 Calculation Logic

### CO2 Emissions
- Transport: Car (2400 kg/year) → Public transport (400 kg/year)
- Electricity: 0.5 kg CO2 per kWh
- Food: Vegetarian (300 kg) → Non-veg (1200 kg)

### Water Waste
- 10-35% of daily usage considered waste
- Higher usage = higher waste percentage

### Energy Consumption
- Base electricity + AC (1.5 kW) + Devices (0.3 kW)
- Monthly totals calculated

### Eco Score
- Starts at 100
- Penalties for high-impact behaviors
- Rewards for eco-friendly choices

## 🎨 Design Philosophy

- **Light Theme**: Soft green, white, and blue
- **Card-Based Layout**: Clean, organized sections
- **Rounded UI**: Modern, friendly appearance
- **Smart Use of Emojis**: Visual appeal without clutter
- **Progress Indicators**: Visual feedback everywhere

## 🏆 Gamification System

### Points
- Survey completion: +20 points
- Public transport: +15 points
- Planting a tree: +25 points
- Recycling: +10 points
- Water saving: +12 points

### Badges
- **First Century**: 100+ points
- **Eco Champion**: 500+ points
- **7-Day Warrior**: 7-day streak
- **Monthly Master**: 30-day streak

### Levels
- Level 1-10 based on total points
- Progress bars show advancement

## 🌍 Real-World Impact

The app calculates:
- Tons of CO2 saved if 1,000 users follow your habits
- Litres of water conserved
- kWh of energy saved
- Equivalent trees planted

## 💡 Smart Nudges Examples

- "Switch to public transport twice a week → save 25kg CO2/year"
- "Reduce AC usage by 1 hour → save 30 kWh/month"
- "Try 'Meatless Mondays' → reduce CO2 by 50kg/year"
- "Fix leaky taps to prevent water waste"

## 🚨 Technical Notes

- Built with Streamlit for rapid development
- Uses matplotlib for charts
- Pandas for data handling
- Session state for game persistence
- Custom CSS for polished UI

## 🎯 Target Audience

- Individuals wanting to track their environmental impact
- People interested in sustainable living
- Eco-conscious users looking for behavior change
- Hackathon judges seeking innovative solutions

## 🌟 What Makes It Stand Out

1. **Not just a calculator** - It's a complete behavioral change system
2. **Game-like experience** - Streaks, points, badges, levels
3. **Energy monitoring** - Real-time alerts and thresholds
4. **Personalized nudges** - AI-like recommendations
5. **Visual appeal** - Polished, professional design
6. **Production-ready** - Clean code, error-free, modular

## 🔧 Troubleshooting

### App won't start
```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Run with explicit Python
python -m streamlit run app.py
```

### Charts not showing
- Ensure matplotlib is properly installed
- Check for any import errors in console

### Data not persisting
- Session state resets on page reload (expected behavior)
- Game stats persist during active session

## 📈 Future Enhancements

- User authentication and database
- Social sharing features
- Mobile app version
- Integration with smart home devices
- Community challenges
- Carbon offset marketplace

## 👥 Credits

Built with ❤️ for sustainability and behavior change.

## 📄 License

This project is created for educational and hackathon purposes.

---

**Remember: Every small action counts. Together, we can make a difference! 🌍**
