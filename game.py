"""
Game logic for EcoNudge Pro
Handles streaks, points, badges, and gamification features
"""

import streamlit as st
from datetime import datetime, timedelta


def initialize_game_state():
    """
    Initialize game-related session state variables
    """
    if 'points' not in st.session_state:
        st.session_state.points = 0
    
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    
    if 'last_activity_date' not in st.session_state:
        st.session_state.last_activity_date = None
    
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    if 'badges' not in st.session_state:
        st.session_state.badges = []
    
    if 'username' not in st.session_state:
        st.session_state.username = 'EcoWarrior'


def update_streak():
    """
    Update the daily streak counter
    """
    today = datetime.now().date()
    
    if st.session_state.last_activity_date is None:
        # First activity
        st.session_state.streak = 1
        st.session_state.last_activity_date = today
    else:
        last_date = st.session_state.last_activity_date
        
        if last_date == today:
            # Already logged today, no change
            pass
        elif last_date == today - timedelta(days=1):
            # Consecutive day
            st.session_state.streak += 1
            st.session_state.last_activity_date = today
        else:
            # Streak broken
            st.session_state.streak = 1
            st.session_state.last_activity_date = today
    
    # Check for streak badges
    check_streak_badges()


def add_points(points, activity):
    """
    Add points for eco-friendly activities
    """
    st.session_state.points += points
    
    # Log the activity
    activity_entry = {
        'date': datetime.now(),
        'activity': activity,
        'points': points
    }
    st.session_state.activity_log.append(activity_entry)
    
    # Check for point-based badges
    check_point_badges()


def check_streak_badges():
    """
    Award badges based on streak milestones
    """
    streak = st.session_state.streak
    
    badges = []
    
    if streak >= 7 and '7-Day Warrior' not in st.session_state.badges:
        badges.append('7-Day Warrior')
    
    if streak >= 14 and '2-Week Champion' not in st.session_state.badges:
        badges.append('2-Week Champion')
    
    if streak >= 30 and 'Monthly Master' not in st.session_state.badges:
        badges.append('Monthly Master')
    
    if streak >= 100 and 'Century Legend' not in st.session_state.badges:
        badges.append('Century Legend')
    
    # Add new badges
    for badge in badges:
        if badge not in st.session_state.badges:
            st.session_state.badges.append(badge)


def check_point_badges():
    """
    Award badges based on point milestones
    """
    points = st.session_state.points
    
    badges = []
    
    if points >= 100 and 'First Century' not in st.session_state.badges:
        badges.append('First Century')
    
    if points >= 500 and 'Eco Champion' not in st.session_state.badges:
        badges.append('Eco Champion')
    
    if points >= 1000 and 'Eco Master' not in st.session_state.badges:
        badges.append('Eco Master')
    
    if points >= 2000 and 'Eco Legend' not in st.session_state.badges:
        badges.append('Eco Legend')
    
    # Add new badges
    for badge in badges:
        if badge not in st.session_state.badges:
            st.session_state.badges.append(badge)


def get_badge():
    """
    Get current badge level based on points and streak
    """
    points = st.session_state.points
    streak = st.session_state.streak
    
    if points >= 1000 or streak >= 30:
        return "🌟 Eco Hero"
    elif points >= 500 or streak >= 14:
        return "⚡ Eco Champion"
    elif points >= 100 or streak >= 7:
        return "🌱 Eco Improver"
    else:
        return "🌿 Eco Beginner"


def get_level():
    """
    Calculate user level based on points
    """
    points = st.session_state.points
    
    if points < 100:
        return 1
    elif points < 250:
        return 2
    elif points < 500:
        return 3
    elif points < 750:
        return 4
    elif points < 1000:
        return 5
    elif points < 1500:
        return 6
    elif points < 2000:
        return 7
    elif points < 3000:
        return 8
    elif points < 4000:
        return 9
    else:
        return 10


def display_game_stats():
    """
    Display game statistics in a nice format
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("🔥 Daily Streak", f"{st.session_state.streak} days")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("🎯 Total Points", st.session_state.points)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        level = get_level()
        st.metric("📊 Level", level)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        badge = get_badge()
        st.metric("🏆 Badge", badge)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Streak message
    if st.session_state.streak > 0:
        if st.session_state.streak == 1:
            st.success(f"🔥 Great start! You're on a {st.session_state.streak}-day eco streak!")
        elif st.session_state.streak < 7:
            st.success(f"🔥 You're on a {st.session_state.streak}-day eco streak! Keep it going!")
        elif st.session_state.streak < 30:
            st.success(f"🔥 Amazing! {st.session_state.streak}-day streak! You're building a habit!")
        else:
            st.success(f"🔥 Incredible! {st.session_state.streak}-day streak! You're an eco legend!")
    
    # Badge showcase
    if st.session_state.badges:
        st.markdown("### 🎖️ Your Badges")
        badge_cols = st.columns(min(len(st.session_state.badges), 4))
        
        badge_emojis = {
            '7-Day Warrior': '🔥',
            '2-Week Champion': '⚡',
            'Monthly Master': '🌟',
            'Century Legend': '👑',
            'First Century': '💯',
            'Eco Champion': '🏆',
            'Eco Master': '🎖️',
            'Eco Legend': '⭐'
        }
        
        for idx, badge in enumerate(st.session_state.badges[:4]):
            with badge_cols[idx]:
                emoji = badge_emojis.get(badge, '🎖️')
                st.info(f"{emoji} {badge}")
    
    # Progress to next level
    level = get_level()
    if level < 10:
        next_level_points = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000][level - 1]
        points_needed = next_level_points - st.session_state.points
        progress = st.session_state.points / next_level_points
        
        st.markdown("### 📈 Progress to Next Level")
        st.progress(min(progress, 1.0))
        st.write(f"🎯 {points_needed} points needed to reach Level {level + 1}")


def get_activity_summary():
    """
    Get a summary of recent activities
    """
    if not st.session_state.activity_log:
        return []
    
    # Get last 5 activities
    recent = st.session_state.activity_log[-5:]
    recent.reverse()
    
    return recent
