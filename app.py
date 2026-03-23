"""
EcoNudge Pro 
----------------------------------------------
Single-file Streamlit app with:
- Session-state routing (no dead navigation)
- Smart Food Monitor (frequency + junk/healthy + late-night scoring)
- Multi-domain trackers: Energy, Travel, Utilities
- Advanced Nudge Engine: generate_nudge(user_data)
- Gamification: Eco Score, levels, badges, daily streak
- Expanded onboarding survey to initialize the user profile
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="🌱 EcoNudge Pro",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# UI: Neon Dark Theme + Cards
# -----------------------------
def load_css() -> None:
    st.markdown(
        r"""
        <style>
        :root{
            --bg:#0e1117;
            --panel:rgba(14,17,23,0.86);
            --panel2:rgba(10,13,19,0.92);
            --neon-cyan:#00ffff;
            --neon-green:#00ff41;
            --neon-purple:#8a2be2;
            --text:#e6f1ff;
            --muted:rgba(230,241,255,0.72);
            --border:rgba(0,255,65,0.28);
            --border2:rgba(0,255,255,0.24);
        }

        html, body, [class*="stApp"]{
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        /* Make Streamlit containers feel "neon" */
        .neo-card{
            background: linear-gradient(135deg, rgba(0,255,65,0.08) 0%, rgba(0,255,255,0.06) 45%, rgba(138,43,226,0.06) 100%),
                        rgba(12,15,21,0.88);
            border: 1px solid rgba(0,255,65,0.26);
            border-radius: 16px;
            padding: 16px 16px;
            box-shadow:
                0 0 0 1px rgba(0,255,255,0.08) inset,
                0 12px 30px rgba(0,0,0,0.35);
        }
        .neo-card-soft{
            background: rgba(12,15,21,0.72);
            border: 1px solid rgba(0,255,255,0.16);
            border-radius: 16px;
            padding: 16px;
        }
        .neo-title{
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
            font-weight: 900;
            letter-spacing: -0.5px;
        }
        .neo-glow{
            text-shadow:
                0 0 10px rgba(0,255,65,0.35),
                0 0 20px rgba(0,255,255,0.18);
        }

        /* Sidebar */
        [data-testid="stSidebar"]{
            background: linear-gradient(180deg, rgba(10,13,19,0.92) 0%, rgba(0,0,0,0.70) 100%) !important;
            border-right: 1px solid rgba(0,255,65,0.22);
        }
        [data-testid="stSidebar"] .neo-card{
            background: rgba(0,0,0,0.25);
            box-shadow: none;
        }

        /* Buttons: hover-like neon styling */
        .stButton>button{
            background: rgba(0,255,65,0.06) !important;
            border: 1px solid rgba(0,255,65,0.35) !important;
            color: rgba(0,255,65,0.95) !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            letter-spacing: 0.4px;
            padding: 0.6rem 1.0rem !important;
            text-transform: uppercase;
            box-shadow: 0 0 0 rgba(0,255,65,0.0);
            transition: all 0.18s ease !important;
        }
        .stButton>button:hover{
            border-color: rgba(0,255,65,0.65) !important;
            color: rgba(0,255,255,0.95) !important;
            box-shadow:
                0 0 0 2px rgba(0,255,65,0.12) inset,
                0 0 28px rgba(0,255,65,0.22) !important;
            transform: translateY(-1px);
        }

        /* Radio + select look */
        .stRadio>div{
            background: rgba(0,0,0,0.18) !important;
            border: 1px solid rgba(0,255,65,0.16);
            border-radius: 14px;
            padding: 12px 12px;
        }
        .stRadio label{
            color: var(--text) !important;
        }
        .stSelectbox>div>div{
            border-radius: 14px !important;
            background: rgba(0,0,0,0.24) !important;
            border: 1px solid rgba(0,255,255,0.18) !important;
            color: var(--text) !important;
        }
        .stSlider>div>div{
            border-radius: 14px !important;
        }

        /* Metric containers */
        [data-testid="metric-container"]{
            background: rgba(0,0,0,0.18) !important;
            border: 1px solid rgba(0,255,65,0.14);
            border-radius: 16px;
            padding: 14px 14px !important;
            box-shadow: 0 0 0 rgba(0,0,0,0.0);
        }
        [data-testid="metric-container"] label{
            color: rgba(0,255,65,0.95) !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricValue"]{
            color: rgba(0,255,255,0.95) !important;
            text-shadow: 0 0 18px rgba(0,255,255,0.16) !important;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial !important;
            font-weight: 900 !important;
        }

        /* Progress */
        .stProgress > div > div{
            background: linear-gradient(90deg, rgba(0,255,65,0.9) 0%, rgba(0,255,255,0.9) 100%) !important;
        }
        .stProgress{
            border-radius: 12px !important;
        }

        .footer-neon{
            color: rgba(0,255,65,0.9);
            border-top: 1px solid rgba(0,255,65,0.22);
            margin-top: 24px;
            padding-top: 16px;
            text-align: center;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Core Helpers / Scoring
# -----------------------------
def clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def iso_today() -> str:
    return date.today().isoformat()


def iso_yesterday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def get_profile_defaults() -> Dict[str, Any]:
    return {
        "transport_primary": "Public Transport",
        "commute_distance_km": 5.0,
        "electricity_kwh_daily": 10.0,
        "ac_hours_daily": 2.0,
        "device_hours_daily": 6.0,
        "fan_hours_daily": 1.5,
        "lights_hours_daily": 2.5,
        "water_liters_daily": 150.0,
        "waste_kg_daily": 1.0,
        "plastic_level": "Medium",  # Low/Medium/High
        "food_diet": "Mixed (Veg + Non-Veg)",
        # Expanded onboarding questions
        "order_daily": False,
        "ac_long_hours": False,
        "commute_mode_simple": "Public Transport",  # Walking/Bike, Car, Public Transport, Mixed
        "waste_food_frequency": "Sometimes",  # Never/Rarely/Sometimes/Often
        "recycle_frequency": "Sometimes",  # Always/Sometimes/Never
    }


def ensure_list_state(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = []


def ensure_dict_state(key: str, default: Dict[str, Any]) -> None:
    if key not in st.session_state:
        st.session_state[key] = default


def ensure_set_state(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = set()


def update_session_profile_from_survey(profile_updates: Dict[str, Any]) -> None:
    if "profile" not in st.session_state or not isinstance(st.session_state.profile, dict):
        st.session_state.profile = get_profile_defaults()
    for k, v in profile_updates.items():
        st.session_state.profile[k] = v


def compute_plastic_penalty(plastic_level: str) -> Tuple[float, float]:
    """
    Returns:
      (plastic_kg_per_day_estimate, penalty_strength_scalar)
    """
    level = (plastic_level or "").lower()
    if "low" in level:
        return 0.05, 0.25
    if "high" in level:
        return 0.30, 1.0
    return 0.15, 0.6


def energy_kwh_from_inputs(fan_h: float, ac_h: float, lights_h: float, devices_h: float) -> float:
    # Lightweight,  assumptions (kW*hours/day => kWh/day)
    fan_kw = 0.06
    ac_kw = 1.2
    lights_kw = 0.05
    devices_kw = 0.15
    return fan_h * fan_kw + ac_h * ac_kw + lights_h * lights_kw + devices_h * devices_kw


def energy_score_from_kwh_monthly(monthly_kwh: float) -> Tuple[float, str]:
    # Keep thresholds stable and explainable.
    # kWh range roughly: 120..600 => score 100..0
    min_kwh = 120.0
    max_kwh = 600.0
    score = clamp(100.0 * (max_kwh - monthly_kwh) / (max_kwh - min_kwh))
    if monthly_kwh < 250:
        tag = "Optimal"
    elif monthly_kwh < 400:
        tag = "Moderate"
    else:
        tag = "High"
    return score, tag


def travel_factor_kg_per_km(mode: str) -> float:
    # Approximate tail-end / lifecycle emissions per passenger km
    # (Intentionally simplified to keep app responsive.)
    m = (mode or "").lower()
    if "walking" in m or "walk" in m:
        return 0.0
    if "bike" in m or "scooter" in m:
        return 0.02
    if "bus" in m or "public" in m:
        return 0.055
    if "car" in m or "auto" in m or "petrol" in m:
        return 0.19
    return 0.11


def travel_score_from_co2_daily(co2_kg: float) -> float:
    # Daily CO2 range: 0..20kg => score 100..0
    max_co2 = 20.0
    score = clamp(100.0 * (max_co2 - co2_kg) / max_co2)
    return score


def utilities_scores(water_l: float, waste_kg: float, plastic_level: str, recycle_frequency: str) -> Tuple[float, Dict[str, float], str]:
    water_l = float(water_l)
    waste_kg = float(waste_kg)
    _, plastic_strength = compute_plastic_penalty(plastic_level)

    # Plastic reduction if user recycles frequently
    rf = (recycle_frequency or "").lower()
    recycle_multiplier = 1.0
    if "always" in rf:
        recycle_multiplier = 0.7
    elif "sometimes" in rf:
        recycle_multiplier = 0.88
    else:
        recycle_multiplier = 1.05

    plastic_penalty = plastic_strength * recycle_multiplier

    # Water: 120..300 => 100..0
    water_score = clamp(100.0 * (300.0 - water_l) / (300.0 - 120.0))
    # Waste: 0.5..2.0 => 100..0
    waste_score = clamp(100.0 * (2.0 - waste_kg) / (2.0 - 0.5))
    # Plastic: 0..1.0 penalty_strength => 100..0
    plastic_score = clamp(100.0 * (1.0 - plastic_penalty) / 1.0)

    # Weighted blend for final utilities score
    final = clamp(0.35 * water_score + 0.35 * waste_score + 0.30 * plastic_score)
    if final >= 75:
        tag = "Hydration & Waste Managed"
    elif final >= 50:
        tag = "Some Waste Discipline Needed"
    else:
        tag = "High Impact Utilities"
    breakdown = {"water_score": water_score, "waste_score": waste_score, "plastic_score": plastic_score}
    return final, breakdown, tag


def food_risk_thresholds(profile: Dict[str, Any], is_junk: bool) -> Tuple[int, int]:
    """
    Returns:
      (warn_threshold_orders_today, cancel_threshold_orders_today)
    """
    order_daily = bool(profile.get("order_daily", False))
    ac_long = bool(profile.get("ac_long_hours", False))
    recycle_frequency = profile.get("recycle_frequency", "Sometimes")

    base_warn = 3
    base_cancel = 4
    if order_daily:
        base_warn = 4
        base_cancel = 5
    if ac_long:
        # Encourage behavior changes more strongly if user signals "high comfort defaults".
        base_warn = max(2, base_warn - 1)
        base_cancel = max(3, base_cancel - 1)
    if is_junk:
        # Junk increases risk sensitivity.
        base_warn = max(2, base_warn - 1)
        base_cancel = max(3, base_cancel - 1)
    if isinstance(recycle_frequency, str) and "always" in recycle_frequency.lower():
        # If they recycle reliably, be slightly more forgiving on junk orders.
        base_warn += 1 if not is_junk else 0
        base_cancel += 1 if not is_junk else 0
    warn_threshold = int(base_warn)
    cancel_threshold = int(base_cancel)
    return warn_threshold, cancel_threshold


def estimate_food_emissions_kg(delivery_km: float, late_night: bool, junk: bool) -> Tuple[float, float, float]:
    """
    Returns:
      (co2_kg, kwh_energy_equivalent, waste_kg_estimate)
    """
    km = float(delivery_km)
    # Delivery emissions proxy
    base_co2_per_km = 0.40  # kg CO2 per km
    # Late night tends to use more energy (restaurants + logistics)
    mult = 1.35 if late_night else 1.0
    # Junk often correlates with heavier packaging
    junk_mult = 1.18 if junk else 1.0

    co2 = km * base_co2_per_km * mult * junk_mult
    # Energy + waste are simplified proxies for UI
    kwh = (0.18 * km) * mult * (1.10 if junk else 1.0)
    waste = (0.06 * km) * mult * (1.25 if junk else 1.0)
    return co2, kwh, waste


def compute_food_domain_score(order_history: List[Dict[str, Any]], for_date: str) -> Tuple[float, Dict[str, Any]]:
    orders = [o for o in order_history if o.get("date") == for_date]
    orders_today = len(orders)
    junk_orders = sum(
        1
        for o in orders
        if o.get("junk", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    )
    late_night_orders = sum(
        1
        for o in orders
        if o.get("late_night", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    )
    canceled_by_system = sum(1 for o in orders if o.get("final_status") == "cancelled_by_system")
    cancelled_by_user = sum(1 for o in orders if o.get("final_status") == "cancelled_by_user")
    override_proceeded = sum(1 for o in orders if o.get("final_status") == "override_proceeded")
    proceeded = sum(1 for o in orders if o.get("final_status") in {"proceeded", "proceeded_after_warning"})
    proceeded_after_warning = sum(1 for o in orders if o.get("final_status") == "proceeded_after_warning")

    # Core scoring penalties
    # Start at 100, deduct based on behavior impact.
    score = 100.0

    # Frequency penalty: each order beyond the first reduces score.
    if orders_today > 1:
        score -= min(40.0, (orders_today - 1) * 8.0)
    # Junk penalty
    score -= min(40.0, junk_orders * 10.0)
    # Late-night penalty
    score -= min(30.0, late_night_orders * 10.0)
    # Override penalty
    score -= min(35.0, override_proceeded * 18.0)
    # Ignoring nudges is explicitly worse than a normal proceed.
    score -= min(35.0, proceeded_after_warning * 14.0)
    # Cancelled behavior = positive: small bonus for each protected cancellation
    score += min(15.0, (canceled_by_system + cancelled_by_user) * 3.5)
    # If they proceeded despite a warning/cancel event, apply extra penalty
    if proceeded > 0 and (canceled_by_system > 0 or cancelled_by_user > 0):
        score -= 8.0

    return clamp(score), {
        "orders_today": orders_today,
        "junk_orders": junk_orders,
        "late_night_orders": late_night_orders,
        "canceled_by_system": canceled_by_system,
        "cancelled_by_user": cancelled_by_user,
        "override_proceeded": override_proceeded,
    }


def compute_domain_scores_for_date(stuff: Dict[str, Any], for_date: str) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    profile: Dict[str, Any] = stuff["profile"]
    order_history: List[Dict[str, Any]] = stuff.get("order_history", [])
    energy_logs: List[Dict[str, Any]] = stuff.get("energy_logs", [])
    travel_logs: List[Dict[str, Any]] = stuff.get("travel_logs", [])
    utilities_logs: List[Dict[str, Any]] = stuff.get("utilities_logs", [])

    # ENERGY
    today_energy = next((x for x in energy_logs if x.get("date") == for_date), None)
    if today_energy:
        energy_score = float(today_energy["energy_score"])
    else:
        monthly_kwh = float(profile.get("electricity_kwh_daily", 10.0)) * 30.0
        energy_score, _ = energy_score_from_kwh_monthly(monthly_kwh)

    # TRAVEL
    today_travel = next((x for x in travel_logs if x.get("date") == for_date), None)
    if today_travel:
        travel_score = float(today_travel["travel_score"])
    else:
        commute_mode = profile.get("commute_mode_simple", "Public Transport")
        commute_km = float(profile.get("commute_distance_km", 5.0))
        daily_co2 = commute_km * travel_factor_kg_per_km(commute_mode) * 2.0  # round-trip proxy
        travel_score = travel_score_from_co2_daily(daily_co2)

    # UTILITIES
    today_util = next((x for x in utilities_logs if x.get("date") == for_date), None)
    if today_util:
        utilities_score = float(today_util["utilities_score"])
    else:
        utilities_score, _, _ = utilities_scores(
            float(profile.get("water_liters_daily", 150.0)),
            float(profile.get("waste_kg_daily", 1.0)),
            str(profile.get("plastic_level", "Medium")),
            str(profile.get("recycle_frequency", "Sometimes")),
        )

    # FOOD
    food_score, food_breakdown = compute_food_domain_score(order_history, for_date)

    # Weighted Eco Score
    # Food tends to be the "unique feature", so it gets slightly more weight.
    eco_score = clamp(0.25 * energy_score + 0.25 * travel_score + 0.20 * utilities_score + 0.30 * food_score)

    scores = {
        "energy_score": float(energy_score),
        "travel_score": float(travel_score),
        "utilities_score": float(utilities_score),
        "food_score": float(food_score),
    }
    extra = {"food_breakdown": food_breakdown}
    return float(eco_score), scores, extra


def estimate_daily_co2_kg(profile: Dict[str, Any], for_date: str, energy_logs: List[Dict[str, Any]], travel_logs: List[Dict[str, Any]], order_history: List[Dict[str, Any]]) -> float:
    # Electricity -> CO2
    co2_per_kwh = 0.233  # kg CO2 per kWh (generic)
    energy = next((x for x in energy_logs if x.get("date") == for_date), None)
    if energy:
        monthly_kwh = float(energy["monthly_kwh"])
        daily_kwh = monthly_kwh / 30.0
    else:
        daily_kwh = float(profile.get("electricity_kwh_daily", 10.0))
    co2_energy = daily_kwh * co2_per_kwh

    # Travel
    travel = next((x for x in travel_logs if x.get("date") == for_date), None)
    if travel:
        co2_travel = float(travel["co2_kg_day"])
    else:
        commute_mode = profile.get("commute_mode_simple", "Public Transport")
        commute_km = float(profile.get("commute_distance_km", 5.0))
        co2_travel = commute_km * travel_factor_kg_per_km(commute_mode) * 2.0

    # Food (only count proceeded orders as "current footprint"; cancelled orders are "avoided")
    food_co2 = 0.0
    for o in order_history:
        if o.get("date") != for_date:
            continue
        if o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}:
            food_co2 += float(o.get("co2_kg_est", 0.0))

    return float(co2_energy + co2_travel + food_co2)


def badge_level_from_score(eco_score: float) -> str:
    if eco_score < 25:
        return "Beginner"
    if eco_score < 45:
        return "Eco Starter"
    if eco_score < 70:
        return "Green Hero"
    return "Sustainability Pro"


def next_level_target(eco_score: float) -> int:
    if eco_score < 25:
        return 25
    if eco_score < 45:
        return 45
    if eco_score < 70:
        return 70
    return 100


def daily_streak_update() -> None:
    today = iso_today()
    yesterday = iso_yesterday()

    # Ensure we always have these keys.
    if "last_positive_action_date" not in st.session_state:
        st.session_state.last_positive_action_date = None
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    if "badges" not in st.session_state:
        st.session_state.badges = []

    last = st.session_state.last_positive_action_date
    if last == today:
        return

    if last == yesterday:
        st.session_state.streak = int(st.session_state.streak) + 1
    else:
        st.session_state.streak = 1

    st.session_state.last_positive_action_date = today


def maybe_unlock_badges(for_date: str) -> None:
    if "badges" not in st.session_state:
        st.session_state.badges = []
    if "badge_set" not in st.session_state:
        st.session_state.badge_set = set(st.session_state.badges)

    order_history: List[Dict[str, Any]] = st.session_state.get("order_history", [])
    orders = [o for o in order_history if o.get("date") == for_date]
    junk_orders = [
        o
        for o in orders
        if o.get("junk", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    ]

    if not junk_orders:
        st.session_state.badge_set.add("No Junk Day")

    # Low Carbon Week badge: average eco score last 7 days >= 70
    eco_history: List[Dict[str, Any]] = st.session_state.get("eco_score_history", [])
    recent = [x["eco_score"] for x in eco_history if _safe_date(x.get("date")) >= _safe_date(for_date) - timedelta(days=6)]
    if recent:
        avg = sum(recent) / len(recent)
        if avg >= 70.0:
            st.session_state.badge_set.add("Low Carbon Week")

    st.session_state.badges = sorted(st.session_state.badge_set)


def _safe_date(d: Any) -> datetime:
    if isinstance(d, datetime):
        return d
    if isinstance(d, date):
        return datetime(d.year, d.month, d.day)
    if isinstance(d, str):
        try:
            dt = datetime.fromisoformat(d).date()
            return datetime(dt.year, dt.month, dt.day)
        except Exception:
            return datetime.now()
    return datetime.now()


def award_points(points: int, reason: str) -> None:
    # Keep points non-negative for a clean gamification experience.
    st.session_state.points = max(0, int(st.session_state.get("points", 0)) + int(points))
    st.session_state.last_award_reason = reason


def generate_nudge(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Advanced Nudge Engine
    ----------------------
    Analyze user behavior patterns and generate personalized nudges.
    Escalates tone based on repeated bad actions.

    Returns a structure:
      {
        "headline": str,
        "nudges": [{"category":..., "severity":..., "message":..., "action":...}, ...]
      }
    """
    profile = user_data.get("profile", {})
    order_history = user_data.get("order_history", [])
    energy_logs = user_data.get("energy_logs", [])
    travel_logs = user_data.get("travel_logs", [])
    utilities_logs = user_data.get("utilities_logs", [])

    today = user_data.get("today", iso_today())
    eco_score = float(user_data.get("eco_score", 50.0))
    scores = user_data.get("scores", {})

    # Signals
    today_orders = [o for o in order_history if o.get("date") == today]
    orders_today = len(today_orders)
    junk_orders = sum(
        1
        for o in today_orders
        if o.get("junk", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    )
    late_night_orders = sum(
        1
        for o in today_orders
        if o.get("late_night", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    )
    system_cancels = sum(1 for o in today_orders if o.get("final_status") == "cancelled_by_system")

    energy_score = float(scores.get("energy_score", 100.0))
    travel_score = float(scores.get("travel_score", 100.0))
    utilities_score = float(scores.get("utilities_score", 100.0))
    food_score = float(scores.get("food_score", 100.0))

    negative_streak = int(user_data.get("negative_streak", 0))
    food_ignore_count = int(user_data.get("food_ignore_count", 0))

    # Severity escalation
    severity_base = "mild"
    if negative_streak >= 3 or food_ignore_count >= 3:
        severity_base = "strict"
    elif negative_streak >= 1 or food_ignore_count >= 1:
        severity_base = "strong"

    # Build nudges
    nudges: List[Dict[str, str]] = []

    if orders_today >= 3 and junk_orders >= 1:
        msg = "You’re stacking junk orders. Try a home-cooked swap today 🌱"
        if severity_base == "strong":
            msg = "Order pattern detected: you’ve had multiple junk orders. Switch to healthier meals now."
        if severity_base == "strict":
            msg = "Strict eco mode: repeated junk ordering. Cancel delivery next time and cook something quick."
        nudges.append(
            {
                "category": "Smart Food",
                "severity": severity_base,
                "message": msg,
                "action": "Choose a healthy option or cancel your order.",
            }
        )
    elif late_night_orders >= 1:
        msg = "Late-night deliveries hit harder. Aim for earlier ordering (before 10 PM) ✅"
        if severity_base in {"strong", "strict"}:
            msg = "Late-night trend continues. Postpone delivery to a safer hour and reduce impact."
        nudges.append(
            {
                "category": "Smart Food",
                "severity": severity_base if severity_base != "mild" else "strong",
                "message": msg,
                "action": "Schedule your order earlier or cook instead.",
            }
        )
    elif system_cancels > 0:
        nudges.append(
            {
                "category": "Smart Food",
                "severity": "mild",
                "message": "Nice! Your system-protected cancellation reduced your footprint. Keep building that habit.",
                "action": "Log a healthy choice next.",
            }
        )

    if energy_score < 55:
        msg = "Energy is spiking. Try lowering AC by 1 hour and switching off idle devices."
        if severity_base == "strict":
            msg = "Strict energy mode: high usage detected. Reduce AC windows and lights intensity today."
        nudges.append(
            {
                "category": "Energy",
                "severity": severity_base,
                "message": msg,
                "action": "Trim 1-2 hours from AC or device usage.",
            }
        )
    elif travel_score < 55:
        msg = "Your travel pattern is carbon-heavy. Choose walking/bike for short trips (<3km)."
        if severity_base == "strict":
            msg = "Strict travel mode: carbon-heavy commute. Try public transport or bike for at least one trip."
        nudges.append(
            {
                "category": "Travel",
                "severity": severity_base,
                "message": msg,
                "action": "Pick a low-carbon mode for today’s commute.",
            }
        )
    elif utilities_score < 55:
        msg = "Utilities impact is rising. Reduce waste and keep plastic usage low—reuse what you can ♻️"
        if severity_base == "strict":
            msg = "Strict utilities mode: minimize plastic + waste today. Compost/avoid food waste if possible."
        nudges.append(
            {
                "category": "Utilities",
                "severity": severity_base,
                "message": msg,
                "action": "Lower waste and recycle more consistently.",
            }
        )

    if eco_score >= 70:
        nudges.append(
            {
                "category": "Momentum",
                "severity": "mild",
                "message": "You’re in a great zone. Keep your streak by logging one eco action today.",
                "action": "Log energy/travel/utilities once and earn points.",
            }
        )

    if not nudges:
        nudges.append(
            {
                "category": "Personalized",
                "severity": "mild",
                "message": "Small changes compound. Pick one habit today: healthier food, fewer late-night orders, or less AC.",
                "action": "Choose one improvement and log it.",
            }
        )

    # Headline
    if severity_base == "strict":
        headline = "Strict Eco Mode Activated"
    elif severity_base == "strong":
        headline = "Strong Nudge: Improve Today"
    else:
        headline = "Gentle Guidance: Stay On Track"

    return {"headline": headline, "nudges": nudges[:3]}


def compute_eco_score_and_update_history() -> None:
    """
    Recompute eco score for today based on current session logs.
    Updates eco_score_history and eco_breakdown_history.
    """
    today = iso_today()
    stuff = {
        "profile": st.session_state.profile,
        "order_history": st.session_state.order_history,
        "energy_logs": st.session_state.energy_logs,
        "travel_logs": st.session_state.travel_logs,
        "utilities_logs": st.session_state.utilities_logs,
    }
    eco_score, scores, extra = compute_domain_scores_for_date(stuff, today)
    st.session_state.last_scores = scores
    st.session_state.last_food_breakdown = extra.get("food_breakdown", {})

    # Carbon saved estimate: baseline (survey profile) vs current (logs + proceeded food)
    baseline_daily_co2 = estimate_daily_co2_kg(st.session_state.profile, today, [], [], [])  # no logs => baseline
    current_daily_co2 = estimate_daily_co2_kg(
        st.session_state.profile,
        today,
        st.session_state.energy_logs,
        st.session_state.travel_logs,
        st.session_state.order_history,
    )
    carbon_saved_kg = max(0.0, baseline_daily_co2 - current_daily_co2)
    st.session_state.last_carbon_saved_kg_today = carbon_saved_kg

    # Update history entries
    st.session_state.eco_score_history = _upsert_history_entry(
        st.session_state.eco_score_history,
        {"date": today, "eco_score": eco_score, "carbon_saved_kg": carbon_saved_kg},
        key="date",
    )
    st.session_state.eco_breakdown_history = _upsert_history_entry(
        st.session_state.eco_breakdown_history,
        {
            "date": today,
            "energy_score": scores["energy_score"],
            "travel_score": scores["travel_score"],
            "utilities_score": scores["utilities_score"],
            "food_score": scores["food_score"],
        },
        key="date",
    )


def _upsert_history_entry(history: List[Dict[str, Any]], entry: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    existing_idx = None
    for i, h in enumerate(history):
        if h.get(key) == entry.get(key):
            existing_idx = i
            break
    if existing_idx is None:
        history.append(entry)
    else:
        history[existing_idx] = entry
    history.sort(key=lambda x: x.get(key))
    return history


def init_session_state() -> None:
    # Routing
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Onboarding / profile
    if "profile" not in st.session_state:
        st.session_state.profile = get_profile_defaults()
    if "survey_completed" not in st.session_state:
        st.session_state.survey_completed = False

    # Gamification
    if "points" not in st.session_state:
        st.session_state.points = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    if "last_positive_action_date" not in st.session_state:
        st.session_state.last_positive_action_date = None
    if "badge_set" not in st.session_state:
        st.session_state.badge_set = set()
    if "badges" not in st.session_state:
        st.session_state.badges = []

    # Logs / histories
    ensure_list_state("order_history")
    ensure_list_state("energy_logs")
    ensure_list_state("travel_logs")
    ensure_list_state("utilities_logs")
    ensure_list_state("eco_score_history")
    ensure_list_state("eco_breakdown_history")

    # Behavioral counters
    if "negative_streak" not in st.session_state:
        st.session_state.negative_streak = 0
    if "food_ignore_count" not in st.session_state:
        st.session_state.food_ignore_count = 0

    # Food monitor state (pending decisions)
    ensure_dict_state(
        "food_decision_state",
        default={
            "pending": False,
            "pending_key": None,
            "pending_order": None,
            "pending_nudge_message": None,
            "pending_severity": "mild",
            "pending_thresholds": {"warn": 0, "cancel": 0},
        },
    )
    if "last_award_reason" not in st.session_state:
        st.session_state.last_award_reason = ""

    # Derived caches
    st.session_state.last_scores = st.session_state.get("last_scores", {})
    st.session_state.last_food_breakdown = st.session_state.get("last_food_breakdown", {})
    st.session_state.last_carbon_saved_kg_today = st.session_state.get("last_carbon_saved_kg_today", 0.0)

    # Seed some eco history if onboarding already completed
    if st.session_state.survey_completed and not st.session_state.eco_score_history:
        seed_history_from_profile()


def seed_history_from_profile() -> None:
    # Create a 7-day baseline using profile estimates.
    today = iso_today()
    for i in range(7):
        d = (date.today() - timedelta(days=(6 - i))).isoformat()
        # Use same baseline scoring (no module logs yet)
        stuff = {
            "profile": st.session_state.profile,
            "order_history": [],
            "energy_logs": [],
            "travel_logs": [],
            "utilities_logs": [],
        }
        eco_score, scores, _ = compute_domain_scores_for_date(stuff, d)
        baseline_daily_co2 = estimate_daily_co2_kg(st.session_state.profile, d, [], [], [])
        carbon_saved_kg = max(0.0, baseline_daily_co2 - baseline_daily_co2)
        st.session_state.eco_score_history.append({"date": d, "eco_score": eco_score, "carbon_saved_kg": carbon_saved_kg})
        st.session_state.eco_breakdown_history.append({"date": d, **scores})

    st.session_state.eco_score_history.sort(key=lambda x: x["date"])
    st.session_state.eco_breakdown_history.sort(key=lambda x: x["date"])


# -----------------------------
# UI Components
# -----------------------------
def neo_header(title: str, subtitle: Optional[str] = None, icon: str = "🌱") -> None:
    st.markdown(
        f"""
        <div class="neo-card" style="margin-bottom: 16px;">
            <div style="display:flex; align-items:flex-start; gap:14px;">
                <div style="font-size: 2rem; line-height: 1;">{icon}</div>
                <div>
                    <div class="neo-title neo-glow" style="font-size: 1.8rem;">{title}</div>
                    {"<div style='color:rgba(230,241,255,0.72);margin-top:6px;'>" + subtitle + "</div>" if subtitle else ""}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert_for_nudge(severity: str, message: str) -> None:
    # Use Streamlit alert blocks for readability.
    if severity == "strict":
        st.error(f"🚨 {message}")
    elif severity == "strong":
        st.warning(f"⚠️ {message}")
    else:
        st.info(f"💡 {message}")


def summarize_badges_and_streak() -> None:
    level = badge_level_from_score(get_current_eco_score())
    next_target = next_level_target(get_current_eco_score())
    if get_current_eco_score() < 100:
        progress_to_next = clamp(100.0 * (get_current_eco_score() - (next_target - (70 if next_target == 70 else 25))) / (next_target - (next_target - (70 if next_target == 70 else 25))), 0, 100)
    else:
        progress_to_next = 100.0

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("🔥 Daily Streak", f"{st.session_state.streak} days")
    with col2:
        st.metric("🎯 Current Level", level)
    with col3:
        st.metric("🏁 Points", f"{st.session_state.points}")


def get_current_eco_score() -> float:
    today = iso_today()
    if st.session_state.eco_score_history:
        last = next((x for x in reversed(st.session_state.eco_score_history) if x.get("date") == today), None)
        if last:
            return float(last.get("eco_score", 0.0))
    # fallback compute
    compute_eco_score_and_update_history()
    last_entry = next((x for x in reversed(st.session_state.eco_score_history) if x.get("date") == today), None)
    return float(last_entry.get("eco_score", 0.0)) if last_entry else 0.0


# -----------------------------
# Routing + Navigation
# -----------------------------
def show_navigation_sidebar() -> None:
    st.sidebar.markdown(
        """
        <div class="neo-card" style="padding:14px 14px;">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div>
                    <div class="neo-title neo-glow" style="font-size: 1.35rem;">🌱 EcoNudge Pro</div>
                    <div style="color: rgba(230,241,255,0.72); font-weight:700; font-size: 0.9rem; margin-top:4px;">
                        Smart nudges, real tracking.
                    </div>
                </div>
                <div style="font-size:1.5rem;">⚡</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    pages = [
        "Home",
        "Dashboard",
        "Smart Food Monitor",
        "Energy Tracker",
        "Travel Tracker",
        "Utilities Tracker",
        "Insights & Nudges",
    ]
    # Session-state routing
    selected = st.sidebar.radio(
        "Navigate",
        pages,
        index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
        horizontal=False,
    )
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    st.sidebar.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if st.session_state.survey_completed:
        # Make sure eco score is computed at least once for the sidebar.
        compute_eco_score_and_update_history()
        eco_score = get_current_eco_score()
        carbon_saved = float(st.session_state.last_carbon_saved_kg_today)
        level = badge_level_from_score(eco_score)

        st.sidebar.metric("Eco Score", f"{eco_score:.0f}/100")
        st.sidebar.metric("Carbon Saved", f"{carbon_saved:.1f} kg")
        st.sidebar.metric("Level", level)
    else:
        st.sidebar.info("Complete the onboarding survey to unlock everything.")


# -----------------------------
# Pages
# -----------------------------
def home_page() -> None:
    neo_header(
        "EcoNudge Pro",
        "Turn everyday habits into measurable eco impact with intelligent nudges.",
        icon="🌱",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            """
            <div class="neo-card-soft">
                <div class="neo-title neo-glow" style="font-size:1.2rem;">What makes it different</div>
                <div style="margin-top:10px;color: rgba(230,241,255,0.72);line-height:1.7;">
                    <div>✅ <strong>Smart Food Monitor</strong>: frequency + junk/healthy + late-night penalties.</div>
                    <div>✅ <strong>Auto-cancel + escalation</strong>: mild → strong → strict nudges.</div>
                    <div>✅ <strong>Multi-domain tracking</strong>: energy, travel, and utilities.</div>
                    <div>✅ <strong>Gamification</strong>: Eco Score, badges, and daily streaks.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if not st.session_state.survey_completed:
            if st.button("🚀 Start onboarding & unlock nudges", use_container_width=True):
                st.session_state.page = "Insights & Nudges"
                st.rerun()
        else:
            if st.button("📊 Jump to Dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
    with col2:
        st.markdown(
            """
            <div class="neo-card-soft">
                <div class="neo-title neo-glow" style="font-size:1.2rem;">How it works</div>
                <div style="margin-top:10px;color: rgba(230,241,255,0.72);line-height:1.7;">
                    <div>1) Answer the expanded survey (personalizes thresholds).</div>
                    <div>2) Log energy/travel/utilities and attempt food orders.</div>
                    <div>3) Eco Score updates with weekly trends + category breakdown.</div>
                    <div>4) The nudge engine escalates when bad patterns repeat.</div>
                </div>
                <div style="margin-top:14px; font-weight:900; color: rgba(0,255,65,0.95);">
                     Real interactions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # Quick feature highlights (cards)
    c1, c2, c3 = st.columns(3)
    features = [
        ("🍕 Smart Food Monitor", "Warnings, auto-cancel simulation, and eco penalties based on your behavior."),
        ("⚡ Energy Tracker", "Input fan/AC/lights/devices and get savings + score updates."),
        ("🌍 Travel Tracker", "Walking/bike/car/bus scoring with carbon-heavy penalties."),
        ("♻️ Utilities Tracker", "Water + waste + plastic tracking with smart suggestions."),
        ("💡 Insights & Nudges", "Advanced nudge engine with escalating tone."),
        ("🎮 Gamification", "Eco Score levels, badges, and daily streaks to keep momentum."),
    ]
    cards = [c1, c2, c3]
    for i, (title, desc) in enumerate(features):
        card_col = cards[i % 3]
        with card_col:
            st.markdown(
                f"""
                <div class="neo-card" style="margin-top:12px;">
                    <div style="font-size:1.6rem;">{title.split(' ')[0]}</div>
                    <div style="margin-top:6px;font-weight:900; font-size:1.05rem;" class="neo-glow">{title}</div>
                    <div style="margin-top:8px;color: rgba(230,241,255,0.72); line-height:1.6; font-weight:600;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def require_onboarding_or_route() -> bool:
    if not st.session_state.survey_completed:
        st.warning("Complete the onboarding survey first to unlock score tracking and personalized nudges.")
        if st.button("📝 Go to Insights & Onboarding", use_container_width=True):
            st.session_state.page = "Insights & Nudges"
            st.rerun()
        return False
    return True


def dashboard_page() -> None:
    neo_header("Dashboard", "Eco Score, category breakdown, and weekly trends.", icon="📊")

    if not require_onboarding_or_route():
        return

    compute_eco_score_and_update_history()

    eco_score = get_current_eco_score()
    level = badge_level_from_score(eco_score)
    carbon_saved_today = float(st.session_state.last_carbon_saved_kg_today)
    today = iso_today()

    # Progress section
    st.markdown(
        f"""
        <div class="neo-card-soft">
            <div style="display:flex; justify-content:space-between; gap:10px; align-items:center;">
                <div>
                    <div class="neo-title neo-glow" style="font-size:1.5rem;">Eco Score: {eco_score:.0f}/100</div>
                    <div style="color: rgba(230,241,255,0.72); font-weight:800; margin-top:6px;">Level: {level}</div>
                </div>
                <div style="text-align:right;">
                    <div style="color: rgba(0,255,65,0.95); font-weight:900; font-size:1.15rem;">{carbon_saved_today:.1f} kg carbon saved today</div>
                    <div style="color: rgba(230,241,255,0.72); font-weight:800; margin-top:6px;">Based on your logged habits</div>
                </div>
            </div>
            <div style="margin-top:12px;">
        """,
        unsafe_allow_html=True,
    )
    st.progress(eco_score / 100.0)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Metrics row
    scores = st.session_state.last_scores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚡ Energy Score", f"{scores.get('energy_score', 0):.0f}/100")
    with col2:
        st.metric("🚲 Travel Score", f"{scores.get('travel_score', 0):.0f}/100")
    with col3:
        st.metric("♻️ Utilities Score", f"{scores.get('utilities_score', 0):.0f}/100")
    with col4:
        st.metric("🍽️ Food Score", f"{scores.get('food_score', 0):.0f}/100")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Weekly trends
    eco_hist = st.session_state.eco_score_history
    last7 = [x for x in eco_hist if _safe_date(x.get("date")) >= _safe_date(today) - timedelta(days=6)]
    if not last7:
        last7 = eco_hist[-7:]
    dates = [x["date"] for x in last7]
    vals = [float(x["eco_score"]) for x in last7]
    carbon_vals = [float(x.get("carbon_saved_kg", 0.0)) for x in last7]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='neo-card'> <div class='neo-title neo-glow' style='font-size:1.1rem;'>Weekly Eco Score</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 4))
        neon_green_rgba = (0 / 255.0, 255 / 255.0, 65 / 255.0, 0.95)
        neon_cyan_rgba = (0 / 255.0, 255 / 255.0, 255 / 255.0, 0.85)
        ax.plot(dates, vals, marker="o", linewidth=2.8, color=neon_green_rgba)
        ax.fill_between(range(len(vals)), vals, alpha=0.18, color=neon_green_rgba)
        ax.set_title("Eco Score trend (7 days)", color="white")
        ax.set_ylabel("Eco Score", color="white")
        ax.grid(True, alpha=0.25, linestyle="--")
        fig.patch.set_facecolor("none")
        ax.tick_params(colors="white")
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='neo-card'> <div class='neo-title neo-glow' style='font-size:1.1rem;'>Weekly Carbon Saved</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 4))
        neon_cyan_rgba_bar = (0 / 255.0, 255 / 255.0, 255 / 255.0, 0.55)
        ax.bar(dates, carbon_vals, color=neon_cyan_rgba_bar, edgecolor="white", linewidth=1)
        ax.set_title("Carbon saved trend (7 days)", color="white")
        ax.set_ylabel("kg", color="white")
        ax.grid(True, axis="y", alpha=0.25, linestyle="--")
        fig.patch.set_facecolor("none")
        ax.tick_params(colors="white")
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    # Category breakdown (current day)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>Category Breakdown (Today)</div>", unsafe_allow_html=True)
    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            """
            <div style="margin-top:12px;color:rgba(230,241,255,0.72);font-weight:800;">
                Orders today: <span style="color:rgba(0,255,65,0.95)">{}</span>
            </div>
            <div style="margin-top:8px;color:rgba(230,241,255,0.72);font-weight:800;">
                Junk orders: <span style="color:rgba(0,255,65,0.95)">{}</span>
            </div>
            <div style="margin-top:8px;color:rgba(230,241,255,0.72);font-weight:800;">
                Late-night orders: <span style="color:rgba(0,255,65,0.95)">{}</span>
            </div>
            """.format(
                st.session_state.last_food_breakdown.get("orders_today", 0),
                st.session_state.last_food_breakdown.get("junk_orders", 0),
                st.session_state.last_food_breakdown.get("late_night_orders", 0),
            ),
            unsafe_allow_html=True,
        )
        if st.button("🍕 Log Smart Food Monitor", use_container_width=True):
            st.session_state.page = "Smart Food Monitor"
            st.rerun()

    with right:
        breakdown = [
            ("Energy", scores.get("energy_score", 0)),
            ("Travel", scores.get("travel_score", 0)),
            ("Utilities", scores.get("utilities_score", 0)),
            ("Food", scores.get("food_score", 0)),
        ]
        labels = [x[0] for x in breakdown]
        values = [float(x[1]) for x in breakdown]
        colors = ["rgba(0,255,65,0.7)", "rgba(0,255,255,0.55)", "rgba(138,43,226,0.55)", "rgba(0,255,65,0.35)"]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1)
        ax.set_title("Scores by category (0-100)", color="white")
        ax.set_ylim(0, 100)
        ax.grid(True, axis="y", alpha=0.25, linestyle="--")
        fig.patch.set_facecolor("none")
        ax.tick_params(colors="white")
        st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-neon'>🌱 EcoNudge Pro</div>", unsafe_allow_html=True)


def food_monitor_page() -> None:
    neo_header("Smart Food Monitor", "Track ordering behavior and trigger smart eco interventions.", icon="🍕")

    if not require_onboarding_or_route():
        return

    compute_eco_score_and_update_history()
    today = iso_today()

    # Initialize derived state
    if "order_attempt_id" not in st.session_state:
        st.session_state.order_attempt_id = 0

    # Current-time impact
    now = datetime.now()
    current_hour = now.hour
    late_night = current_hour >= 22 or current_hour <= 6

    # Compute current day ordering signals
    today_orders = [o for o in st.session_state.order_history if o.get("date") == today]
    orders_today = len(today_orders)
    junk_orders = sum(
        1
        for o in today_orders
        if o.get("junk", False) and o.get("final_status") in {"proceeded", "proceeded_after_warning", "override_proceeded"}
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Orders Today", str(orders_today))
    with c2:
        st.metric("Junk Orders", str(junk_orders))
    with c3:
        st.metric("Late-Night Zone", "Yes" if late_night else "No")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # If there is a pending decision, show it as a modal-like block (session state driven)
    if st.session_state.food_decision_state.get("pending", False):
        pending = st.session_state.food_decision_state
        order = pending.get("pending_order") or {}
        message = pending.get("pending_nudge_message") or "Decision required."
        severity = pending.get("pending_severity", "mild")
        thresholds = pending.get("pending_thresholds", {"warn": 0, "cancel": 0})

        st.markdown("<div class='neo-card' style='border:2px solid rgba(0,255,65,0.25);'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='neo-title neo-glow' style='font-size:1.2rem;'>🤖 AI Intervention</div>",
            unsafe_allow_html=True,
        )
        render_alert_for_nudge(severity, message)
        st.markdown(
            f"""
            <div style="margin-top:10px;color: rgba(230,241,255,0.72); font-weight:800;">
                Thresholds: warn at <span style="color:rgba(0,255,65,0.95)">{thresholds.get('warn')}</span>, auto-cancel at <span style="color:rgba(0,255,65,0.95)">{thresholds.get('cancel')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("🌱 Switch to cooking (cancel)", use_container_width=True):
                # Record a cancellation by user (positive)
                st.session_state.order_history.append(
                    {
                        "id": pending.get("pending_key"),
                        "date": today,
                        "ts": datetime.now().isoformat(),
                        "food_type": order.get("food_type"),
                        "junk": bool(order.get("junk")),
                        "late_night": bool(order.get("late_night")),
                        "delivery_km": float(order.get("delivery_km", 0.0)),
                        "final_status": "cancelled_by_user",
                        "co2_kg_est": float(order.get("co2_kg_est", 0.0)),
                    }
                )
                award_points(10, "Cancelled order after nudge")
                daily_streak_update()
                maybe_unlock_badges(today)
                # Decay negative streak
                st.session_state.negative_streak = max(0, int(st.session_state.negative_streak) - 1)
                st.session_state.food_ignore_count = max(0, int(st.session_state.food_ignore_count) - 1)

                # Clear pending
                st.session_state.food_decision_state.update({"pending": False, "pending_order": None})
                compute_eco_score_and_update_history()
                st.rerun()

        with colB:
            if st.button("⚠️ Proceed anyway (ignore nudge)", use_container_width=True):
                # Record proceed (negative)
                st.session_state.order_history.append(
                    {
                        "id": pending.get("pending_key"),
                        "date": today,
                        "ts": datetime.now().isoformat(),
                        "food_type": order.get("food_type"),
                        "junk": bool(order.get("junk")),
                        "late_night": bool(order.get("late_night")),
                        "delivery_km": float(order.get("delivery_km", 0.0)),
                        "final_status": "proceeded_after_warning",
                        "co2_kg_est": float(order.get("co2_kg_est", 0.0)),
                    }
                )

                st.session_state.food_ignore_count = int(st.session_state.food_ignore_count) + 1
                st.session_state.negative_streak = int(st.session_state.negative_streak) + 1
                award_points(-25, "Ignored smart food nudge")

                # Escalation: repeated ignores increase severity next time (tracked via food_ignore_count).
                maybe_unlock_badges(today)
                st.session_state.food_decision_state.update({"pending": False, "pending_order": None})
                compute_eco_score_and_update_history()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # AI auto-cancel state: if the user had cancelled previously by system, they can still override emergencies.
    # In this simplified version, we only require user decisions when a warning is triggered.

    st.markdown("<div class='neo-card' style='margin-top:12px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='neo-title neo-glow' style='font-size:1.2rem;'>🍽️ Attempt an Order</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:rgba(230,241,255,0.72); font-weight:800; margin-top:6px;'>Late-night impact is currently: <span style='color:rgba(0,255,65,0.95)'>{'ON' if late_night else 'OFF'}</span></div>",
        unsafe_allow_html=True,
    )

    with st.form("order_form", clear_on_submit=False):
        colL, colR = st.columns(2)
        with colL:
            food_type = st.selectbox(
                "Pick your meal",
                ["🍕 Junk Pizza", "🍔 Junk Burger", "🍜 Junk Asian Cuisine", "🌮 Junk Mexican", "🥗 Healthy Bowl", "🍝 Healthy Pasta"],
                index=0,
                help="Select whether this order is a junk or a healthy choice.",
            )

            order_time_choice = st.radio(
                "Order timing",
                ["Now (Immediate)", "Schedule for later"],
                index=0,
            )

        with colR:
            if order_time_choice == "Schedule for later":
                scheduled_hour = st.slider("Scheduled hour (24h)", 0, 23, 23)
                scheduled_time = now.replace(hour=int(scheduled_hour), minute=0, second=0, microsecond=0)
            else:
                scheduled_time = now

            delivery_km = st.slider("Delivery distance (km)", 1, 20, 5)

        submitted = st.form_submit_button("🚀 Place Order Attempt", use_container_width=True)

    if submitted:
        is_junk = "junk" in (food_type or "").lower() or "🍕" in food_type or "🍔" in food_type or "🌮" in food_type or "🍜" in food_type
        late = scheduled_time.hour >= 22 or scheduled_time.hour <= 6

        # Frequency logic (today)
        warn_threshold, cancel_threshold = food_risk_thresholds(st.session_state.profile, is_junk=is_junk)
        new_order_count_today = orders_today + 1

        # Calculate estimated emissions for display / scoring
        co2_kg_est, _, _ = estimate_food_emissions_kg(delivery_km, late, junk=is_junk)

        st.session_state.order_attempt_id = int(st.session_state.order_attempt_id) + 1
        attempt_id = f"order_{st.session_state.order_attempt_id}_{datetime.now().strftime('%H%M%S')}"

        # Cancel logic (auto-cancel when thresholds exceeded)
        if new_order_count_today >= cancel_threshold:
            # Auto-cancel
            st.session_state.order_history.append(
                {
                    "id": attempt_id,
                    "date": today,
                    "ts": datetime.now().isoformat(),
                    "food_type": food_type,
                    "junk": is_junk,
                    "late_night": late,
                    "delivery_km": float(delivery_km),
                    "final_status": "cancelled_by_system",
                    "co2_kg_est": float(co2_kg_est),
                }
            )
            award_points(15, "Auto-cancelled late/frequent order")
            daily_streak_update()
            maybe_unlock_badges(today)
            st.session_state.negative_streak = max(0, int(st.session_state.negative_streak) - 1)
            compute_eco_score_and_update_history()

            # Strong behavioral nudge popup
            st.markdown("<div class='neo-card' style='border:2px solid rgba(255,68,68,0.6); background: rgba(50,0,0,0.25);'>", unsafe_allow_html=True)
            st.error("⚠️ Order cancelled: You’re exceeding your sustainability goals.")
            st.markdown(
                f"""
                <div style="margin-top:8px; color: rgba(230,241,255,0.72); font-weight:800;">
                    Impact prevented (est.): <span style="color:rgba(0,255,65,0.95)">{co2_kg_est:.1f} kg CO2</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Optional override (counts as ignoring nudges)
            if st.button("Emergency override (Proceed)", use_container_width=True):
                st.session_state.order_history.append(
                    {
                        "id": attempt_id + "_override",
                        "date": today,
                        "ts": datetime.now().isoformat(),
                        "food_type": food_type,
                        "junk": is_junk,
                        "late_night": late,
                        "delivery_km": float(delivery_km),
                        "final_status": "override_proceeded",
                        "co2_kg_est": float(co2_kg_est),
                    }
                )
                st.session_state.food_ignore_count = int(st.session_state.food_ignore_count) + 2
                st.session_state.negative_streak = int(st.session_state.negative_streak) + 2
                award_points(-50, "Overrode auto-cancel protection")
                maybe_unlock_badges(today)
                compute_eco_score_and_update_history()
                st.rerun()

            return

        # Warn logic (show nudge and require decision)
        if new_order_count_today >= warn_threshold:
            # Determine base message and severity based on ignore count
            ignore = int(st.session_state.food_ignore_count)
            if ignore >= 2:
                severity = "strict"
            elif ignore >= 1:
                severity = "strong"
            else:
                severity = "mild"

            warn_msg = f"You've ordered {new_order_count_today} times today. Try cooking instead 🌱"
            if is_junk and late:
                warn_msg = f"High-impact pattern detected (late night + junk). Pause deliveries tonight 🌙"
            elif is_junk and not late:
                warn_msg = f"Multiple junk orders detected. Switch one meal to something healthier ✅"
            elif not is_junk and late:
                warn_msg = f"Late-night timing increases impact. Postpone to before 10 PM 🕙"
            elif not is_junk:
                warn_msg = "You’re close to your delivery threshold. Keep momentum with a home-cooked meal."

            # Store pending decision state (so buttons below render a decision UI)
            st.session_state.food_decision_state.update(
                {
                    "pending": True,
                    "pending_key": attempt_id,
                    "pending_order": {
                        "food_type": food_type,
                        "junk": is_junk,
                        "late_night": late,
                        "delivery_km": delivery_km,
                        "co2_kg_est": co2_kg_est,
                    },
                    "pending_nudge_message": warn_msg,
                    "pending_severity": severity,
                    "pending_thresholds": {"warn": warn_threshold, "cancel": cancel_threshold},
                }
            )
            st.rerun()

        # If no warning/cancel, we log directly as proceeded.
        st.session_state.order_history.append(
            {
                "id": attempt_id,
                "date": today,
                "ts": datetime.now().isoformat(),
                "food_type": food_type,
                "junk": is_junk,
                "late_night": late,
                "delivery_km": float(delivery_km),
                "final_status": "proceeded",
                "co2_kg_est": float(co2_kg_est),
            }
        )
        award_points(5 if not is_junk else -5, "Food order logged")
        # Junk orders count as negative streak signal.
        if is_junk or late:
            st.session_state.negative_streak = int(st.session_state.negative_streak) + 1
        else:
            daily_streak_update()
        maybe_unlock_badges(today)
        compute_eco_score_and_update_history()
        st.success("Order attempt logged. Your Eco Score has been updated.")

    st.markdown("</div>", unsafe_allow_html=True)

    # History table
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>Today’s Order Timeline</div>", unsafe_allow_html=True)
    orders_df = pd.DataFrame(
        [
            {
                "Time": (o.get("ts", "") or "")[:19],
                "Food": o.get("food_type"),
                "Type": "Junk" if o.get("junk") else "Healthy",
                "Late Night": "Yes" if o.get("late_night") else "No",
                "Result": o.get("final_status"),
                "CO2 (est.)": float(o.get("co2_kg_est", 0.0)),
                "Distance (km)": float(o.get("delivery_km", 0.0)),
            }
            for o in st.session_state.order_history
            if o.get("date") == today
        ]
    )
    if orders_df.empty:
        st.info("No orders logged today yet. Try placing an order attempt to see eco interventions.")
    else:
        st.dataframe(
            orders_df.sort_values(by="Time", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def energy_page() -> None:
    neo_header("Energy Tracker", "Log fan/AC/lights/devices and get score + savings suggestions.", icon="⚡")

    if not require_onboarding_or_route():
        return

    compute_eco_score_and_update_history()
    today = iso_today()

    prof = st.session_state.profile
    default_fan = float(prof.get("fan_hours_daily", 1.5))
    default_ac = float(prof.get("ac_hours_daily", 2.0))
    default_lights = float(prof.get("lights_hours_daily", 2.5))
    default_devices = float(prof.get("device_hours_daily", 6.0))

    existing = next((x for x in st.session_state.energy_logs if x.get("date") == today), None)

    with st.container():
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>⚙️ Energy Inputs (per day)</div>", unsafe_allow_html=True)
        with st.form("energy_log_form", clear_on_submit=False):
            colA, colB = st.columns(2)
            with colA:
                fan_h = st.slider("Fan usage (hours/day)", 0.0, 24.0, float(existing.get("fan_hours_day", default_fan) if existing else default_fan), 0.5)
                ac_h = st.slider("AC usage (hours/day)", 0.0, 24.0, float(existing.get("ac_hours_day", default_ac) if existing else default_ac), 0.5)
            with colB:
                lights_h = st.slider("Lights usage (hours/day)", 0.0, 24.0, float(existing.get("lights_hours_day", default_lights) if existing else default_lights), 0.5)
                devices_h = st.slider("Devices usage (TV/Laptop) (hours/day)", 0.0, 24.0, float(existing.get("devices_hours_day", default_devices) if existing else default_devices), 0.5)

            submitted = st.form_submit_button("✅ Log Energy & Update Eco Score", use_container_width=True)

        if submitted:
            kwh_day = energy_kwh_from_inputs(fan_h, ac_h, lights_h, devices_h)
            monthly_kwh = kwh_day * 30.0
            e_score, tag = energy_score_from_kwh_monthly(monthly_kwh)

            st.session_state.energy_logs = [
                x for x in st.session_state.energy_logs if x.get("date") != today
            ]  # replace today entry
            st.session_state.energy_logs.append(
                {
                    "date": today,
                    "ts": datetime.now().isoformat(),
                    "fan_hours_day": float(fan_h),
                    "ac_hours_day": float(ac_h),
                    "lights_hours_day": float(lights_h),
                    "devices_hours_day": float(devices_h),
                    "kwh_day": float(kwh_day),
                    "monthly_kwh": float(monthly_kwh),
                    "energy_score": float(e_score),
                    "tag": tag,
                }
            )

            # Points logic: reward if score is good
            if e_score >= 75:
                award_points(20, "Logged low energy usage")
                daily_streak_update()
            elif e_score >= 55:
                award_points(8, "Logged moderate energy usage")
            else:
                award_points(-15, "Logged high energy usage")
                st.session_state.negative_streak = int(st.session_state.negative_streak) + 1

            compute_eco_score_and_update_history()
            maybe_unlock_badges(today)

            st.success(f"Energy logged: {monthly_kwh:.0f} kWh/month · {tag} · Energy score {e_score:.0f}/100")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Nudge + breakdown
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    scores = st.session_state.last_scores
    energy_score = float(scores.get("energy_score", 0.0))
    profile = st.session_state.profile

    # Savings suggestion: reduce AC first if present
    today_energy = next((x for x in st.session_state.energy_logs if x.get("date") == today), None)
    if today_energy:
        kwh_day = float(today_energy["kwh_day"])
        monthly_kwh = float(today_energy["monthly_kwh"])
        suggestion = []
        if today_energy["ac_hours_day"] > 3.0:
            suggestion.append("Reduce AC by ~1 hour/day (cooling demand drops fast).")
        if today_energy["lights_hours_day"] > 4.0:
            suggestion.append("Cut lights by ~1 hour/day or switch to LEDs.")
        if today_energy["devices_hours_day"] > 8.0:
            suggestion.append("Lower device standby/usage by powering down idle periods.")
        if not suggestion:
            suggestion.append("Keep steady—log again tomorrow to protect your score.")
    else:
        monthly_kwh = float(profile.get("electricity_kwh_daily", 10.0)) * 30.0
        kwh_day = monthly_kwh / 30.0
        suggestion = ["Use your baseline as a reference—log today’s actual values to personalize savings."]

    # Generate personalized nudge
    compute_eco_score_and_update_history()
    user_data = {
        "profile": st.session_state.profile,
        "order_history": st.session_state.order_history,
        "energy_logs": st.session_state.energy_logs,
        "travel_logs": st.session_state.travel_logs,
        "utilities_logs": st.session_state.utilities_logs,
        "today": today,
        "eco_score": get_current_eco_score(),
        "scores": st.session_state.last_scores,
        "negative_streak": int(st.session_state.negative_streak),
        "food_ignore_count": int(st.session_state.food_ignore_count),
    }
    nudge = generate_nudge(user_data)

    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neo-title neo-glow' style='font-size:1.1rem;'>{nudge.get('headline')}</div>", unsafe_allow_html=True)
    for n in nudge.get("nudges", []):
        render_alert_for_nudge(n.get("severity", "mild"), n.get("message", ""))
        st.markdown(f"<div style='color:rgba(230,241,255,0.72);font-weight:800;margin-top:6px;'>Do: {n.get('action','')}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='neo-title neo-glow' style='font-size:1.05rem;'>💡 Suggested savings</div>", unsafe_allow_html=True)
    for s in suggestion[:3]:
        st.markdown(f"• {s}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-neon'>⚡ Energy Tracker</div>", unsafe_allow_html=True)


def travel_page() -> None:
    neo_header("Travel Tracker", "Choose a mode and distance; score is based on carbon emissions.", icon="🚲")

    if not require_onboarding_or_route():
        return

    compute_eco_score_and_update_history()
    today = iso_today()
    existing = next((x for x in st.session_state.travel_logs if x.get("date") == today), None)

    with st.container():
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>🧭 Travel Inputs (per day)</div>", unsafe_allow_html=True)
        with st.form("travel_log_form", clear_on_submit=False):
            colA, colB = st.columns(2)
            with colA:
                mode = st.selectbox(
                    "Transport mode",
                    ["Walking", "Bike/Scooter", "Bus/Public Transport", "Car"],
                    index=0 if not existing else (
                        0
                        if existing.get("mode") == "Walking"
                        else 1
                        if existing.get("mode") == "Bike/Scooter"
                        else 2
                        if existing.get("mode") == "Bus/Public Transport"
                        else 3
                    ),
                )
                distance_km = st.slider(
                    "Total distance (km) for the day",
                    0.0,
                    50.0,
                    float(existing.get("distance_km_day", 8.0) if existing else 8.0),
                    0.5,
                )
            with colB:
                round_trip = st.checkbox("Treat as round-trip?", value=True)
                submitted = st.form_submit_button("✅ Log Travel & Update Eco Score", use_container_width=True)

        if submitted:
            mult = 2.0 if round_trip else 1.0
            co2_kg = float(distance_km) * mult * travel_factor_kg_per_km(mode)
            t_score = travel_score_from_co2_daily(co2_kg)

            st.session_state.travel_logs = [x for x in st.session_state.travel_logs if x.get("date") != today]
            st.session_state.travel_logs.append(
                {
                    "date": today,
                    "ts": datetime.now().isoformat(),
                    "mode": mode,
                    "distance_km_day": float(distance_km),
                    "round_trip": bool(round_trip),
                    "co2_kg_day": float(co2_kg),
                    "travel_score": float(t_score),
                }
            )

            if t_score >= 75:
                award_points(20, "Logged low-carbon travel")
                daily_streak_update()
            elif t_score >= 55:
                award_points(8, "Logged moderate travel")
            else:
                award_points(-15, "Logged carbon-heavy travel")
                st.session_state.negative_streak = int(st.session_state.negative_streak) + 1
            compute_eco_score_and_update_history()
            maybe_unlock_badges(today)
            st.success(f"Travel logged: {co2_kg:.2f} kg CO2/day · Travel score {t_score:.0f}/100")
            st.rerun()

    # Nudge + chart
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    compute_eco_score_and_update_history()
    scores = st.session_state.last_scores
    travel_score = float(scores.get("travel_score", 0.0))

    # Nudge
    user_data = {
        "profile": st.session_state.profile,
        "order_history": st.session_state.order_history,
        "energy_logs": st.session_state.energy_logs,
        "travel_logs": st.session_state.travel_logs,
        "utilities_logs": st.session_state.utilities_logs,
        "today": today,
        "eco_score": get_current_eco_score(),
        "scores": st.session_state.last_scores,
        "negative_streak": int(st.session_state.negative_streak),
        "food_ignore_count": int(st.session_state.food_ignore_count),
    }
    nudge = generate_nudge(user_data)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='neo-title neo-glow' style='font-size:1.1rem;'>{nudge.get('headline')}</div>", unsafe_allow_html=True)
        for n in nudge.get("nudges", []):
            render_alert_for_nudge(n.get("severity", "mild"), n.get("message", ""))
            st.markdown(f"<div style='color:rgba(230,241,255,0.72);font-weight:800;margin-top:6px;'>Do: {n.get('action','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.05rem;'>📈 Carbon footprint impact</div>", unsafe_allow_html=True)
        # Show last few travel logs
        logs = st.session_state.travel_logs[-14:]
        if not logs:
            st.info("Log travel to see emissions history.")
        else:
            df = pd.DataFrame(logs)
            df = df.sort_values(by="date")
            fig, ax = plt.subplots(figsize=(7, 4))
            neon_cyan_rgba = (0 / 255.0, 255 / 255.0, 255 / 255.0, 0.85)
            ax.plot(df["date"], df["co2_kg_day"], marker="o", linewidth=2.6, color=neon_cyan_rgba)
            ax.set_title("CO2 (kg/day) — last 14 logs", color="white")
            ax.set_ylabel("kg CO2/day", color="white")
            ax.grid(True, alpha=0.25, linestyle="--")
            fig.patch.set_facecolor("none")
            ax.tick_params(colors="white")
            st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-neon'>🚲 Travel Tracker</div>", unsafe_allow_html=True)


def utilities_page() -> None:
    neo_header("Utilities Tracker", "Track water, waste, and plastic usage—score updates instantly.", icon="♻️")

    if not require_onboarding_or_route():
        return

    compute_eco_score_and_update_history()
    today = iso_today()
    existing = next((x for x in st.session_state.utilities_logs if x.get("date") == today), None)

    with st.container():
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>💧 Water + Waste + Plastic</div>", unsafe_allow_html=True)
        with st.form("utilities_log_form", clear_on_submit=False):
            colA, colB = st.columns(2)
            with colA:
                water_l = st.slider(
                    "Water usage (litres/day)",
                    30.0,
                    450.0,
                    float(existing.get("water_liters_day", st.session_state.profile.get("water_liters_daily", 150.0)) if existing else st.session_state.profile.get("water_liters_daily", 150.0)),
                    5.0,
                )
                waste_kg = st.slider(
                    "Waste generation (kg/day)",
                    0.2,
                    4.0,
                    float(existing.get("waste_kg_day", st.session_state.profile.get("waste_kg_daily", 1.0)) if existing else st.session_state.profile.get("waste_kg_daily", 1.0)),
                    0.1,
                )
            with colB:
                plastic_level = st.selectbox(
                    "Plastic consumption level",
                    ["Low (Reusable)", "Medium", "High (Frequent single-use)"],
                    index=0 if not existing else (
                        0 if existing.get("plastic_level") == "Low" else 1 if existing.get("plastic_level") == "Medium" else 2
                    ),
                )
                plastic_norm = "Low" if "Low" in plastic_level else "Medium" if "Medium" in plastic_level else "High"

                submitted = st.form_submit_button("✅ Log Utilities & Update Eco Score", use_container_width=True)

        if submitted:
            utilities_score, breakdown, tag = utilities_scores(
                water_l,
                waste_kg,
                plastic_norm,
                st.session_state.profile.get("recycle_frequency", "Sometimes"),
            )
            st.session_state.utilities_logs = [x for x in st.session_state.utilities_logs if x.get("date") != today]
            st.session_state.utilities_logs.append(
                {
                    "date": today,
                    "ts": datetime.now().isoformat(),
                    "water_liters_day": float(water_l),
                    "waste_kg_day": float(waste_kg),
                    "plastic_level": plastic_norm,
                    "utilities_score": float(utilities_score),
                    "tag": tag,
                    "breakdown": breakdown,
                }
            )
            if utilities_score >= 75:
                award_points(20, "Logged well-managed utilities")
                daily_streak_update()
            elif utilities_score >= 55:
                award_points(8, "Logged moderate utilities")
            else:
                award_points(-15, "Logged high-impact utilities")
                st.session_state.negative_streak = int(st.session_state.negative_streak) + 1
            compute_eco_score_and_update_history()
            maybe_unlock_badges(today)
            st.success(f"Utilities logged: {tag} · Utilities score {utilities_score:.0f}/100")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    scores = st.session_state.last_scores
    util_score = float(scores.get("utilities_score", 0.0))

    # Nudge + breakdown card
    user_data = {
        "profile": st.session_state.profile,
        "order_history": st.session_state.order_history,
        "energy_logs": st.session_state.energy_logs,
        "travel_logs": st.session_state.travel_logs,
        "utilities_logs": st.session_state.utilities_logs,
        "today": today,
        "eco_score": get_current_eco_score(),
        "scores": st.session_state.last_scores,
        "negative_streak": int(st.session_state.negative_streak),
        "food_ignore_count": int(st.session_state.food_ignore_count),
    }
    nudge = generate_nudge(user_data)

    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neo-title neo-glow' style='font-size:1.1rem;'>{nudge.get('headline')}</div>", unsafe_allow_html=True)
    for n in nudge.get("nudges", []):
        render_alert_for_nudge(n.get("severity", "mild"), n.get("message", ""))
        st.markdown(f"<div style='color:rgba(230,241,255,0.72);font-weight:800;margin-top:6px;'>Do: {n.get('action','')}</div>", unsafe_allow_html=True)

    # Show decomposition for this log if present
    today_util = next((x for x in st.session_state.utilities_logs if x.get("date") == today), None)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='neo-title neo-glow' style='font-size:1.05rem;'>📌 Utilities breakdown</div>", unsafe_allow_html=True)
    if today_util and isinstance(today_util.get("breakdown"), dict):
        b = today_util["breakdown"]
        st.markdown(
            f"""
            <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:8px;">
                <div style="min-width: 180px;" class="neo-card-soft">
                    <div style="font-weight:900; color:rgba(0,255,65,0.95);">Water score: {b.get('water_score', 0):.0f}/100</div>
                </div>
                <div style="min-width: 180px;" class="neo-card-soft">
                    <div style="font-weight:900; color:rgba(0,255,255,0.95);">Waste score: {b.get('waste_score', 0):.0f}/100</div>
                </div>
                <div style="min-width: 180px;" class="neo-card-soft">
                    <div style="font-weight:900; color:rgba(138,43,226,0.95);">Plastic score: {b.get('plastic_score', 0):.0f}/100</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Log utilities to unlock category breakdown.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer-neon'>♻️ Utilities Tracker</div>", unsafe_allow_html=True)


def insights_page() -> None:
    neo_header("Insights & Nudges", "Onboarding survey + advanced behavioral engine.", icon="💡")

    if not st.session_state.survey_completed:
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.1rem;'>🧠 Expanded Onboarding Survey</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color: rgba(230,241,255,0.72); font-weight:800; margin-top:8px;'>Your answers personalize thresholds for nudges and scoring.</div>",
            unsafe_allow_html=True,
        )

        with st.form("survey_form", clear_on_submit=False):
            # Transportation / commute
            st.markdown("<div class='neo-card-soft' style='margin-bottom:12px;'><div style='font-weight:900;color:rgba(0,255,65,0.95)'>🚗 Transportation</div>", unsafe_allow_html=True)
            transport = st.selectbox(
                "Primary mode of transport:",
                ["Car (Petrol/Diesel)", "Car (Electric)", "Bike/Scooter", "Public Transport", "Walking/Cycling"],
                index=3,
            )
            commute_distance = st.slider("Typical commute distance (one-way, km)", 0.5, 40.0, 5.0, 0.5)
            st.markdown("</div>", unsafe_allow_html=True)

            # Energy baseline
            st.markdown("<div class='neo-card-soft' style='margin-bottom:12px;'><div style='font-weight:900;color:rgba(0,255,65,0.95)'>⚡ Energy Baseline</div>", unsafe_allow_html=True)
            electricity_kwh_daily = st.slider("Daily electricity usage (kWh)", 1.0, 60.0, 10.0, 0.5)
            ac_hours_daily = st.slider("AC usage (hours/day)", 0.0, 24.0, 2.0, 0.5)
            device_hours_daily = st.slider("Devices usage (TV/Laptop) (hours/day)", 0.0, 24.0, 6.0, 0.5)
            fan_hours_daily = st.slider("Fan usage (hours/day)", 0.0, 24.0, 1.5, 0.5)
            lights_hours_daily = st.slider("Lights usage (hours/day)", 0.0, 24.0, 2.5, 0.5)
            st.markdown("</div>", unsafe_allow_html=True)

            # Utilities baseline
            st.markdown("<div class='neo-card-soft' style='margin-bottom:12px;'><div style='font-weight:900;color:rgba(0,255,65,0.95)'>💧 Utilities Baseline</div>", unsafe_allow_html=True)
            water_liters_daily = st.slider("Water consumption (litres/day)", 50.0, 450.0, 150.0, 5.0)
            waste_kg_daily = st.slider("Waste generation (kg/day)", 0.2, 4.0, 1.0, 0.1)
            plastic_level_ui = st.radio(
                "Plastic consumption level:",
                ["Low (Reusable bags, bottles)", "Medium (Occasional plastic)", "High (Frequent plastic use)"],
                index=1,
            )
            plastic_norm = "Low" if "Low" in plastic_level_ui else "High" if "High" in plastic_level_ui else "Medium"
            st.markdown("</div>", unsafe_allow_html=True)

            # Food baseline
            st.markdown("<div class='neo-card-soft' style='margin-bottom:12px;'><div style='font-weight:900;color:rgba(0,255,65,0.95)'>🍽️ Food Habits</div>", unsafe_allow_html=True)
            food_diet = st.selectbox(
                "Diet preference:",
                ["Vegetarian", "Mixed (Veg + Non-Veg)", "Non-Vegetarian"],
                index=1,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Expanded survey requirement questions
            st.markdown("<div class='neo-card-soft' style='margin-bottom:12px;'><div style='font-weight:900;color:rgba(0,255,65,0.95)'>🧩 Behavior Questions (Expanded)</div>", unsafe_allow_html=True)
            order_daily = st.radio(
                "Do you order food daily?",
                ["Yes", "No"],
                index=1,
            )
            waste_food_frequency = st.selectbox(
                "How often do you waste food?",
                ["Never", "Rarely", "Sometimes", "Often"],
                index=2,
            )
            ac_long_hours = st.radio(
                "Do you use AC for long hours?",
                ["Less than 2 hours", "2 to 5 hours", "More than 5 hours"],
                index=0,
            )
            recycle_frequency = st.selectbox(
                "How often do you recycle?",
                ["Always", "Sometimes", "Never"],
                index=1,
            )
            commute_simple = st.radio(
                "How do you commute most often?",
                ["Walking/Bike", "Car", "Public Transport", "Mixed"],
                index=2,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("🌱 Calculate Profile & Unlock EcoNudge Pro", use_container_width=True)

        if submitted:
            # Normalize expanded answers
            order_daily_bool = order_daily == "Yes"
            ac_long = "More than 5 hours" in ac_long_hours

            profile_updates = get_profile_defaults()
            # Transport normalization for baseline commute mode
            profile_updates["transport_primary"] = transport
            # Simple commute mode for travel scoring
            if "car (petrol" in transport.lower() or "car" in transport.lower():
                commute_mode_simple = "Car"
            elif "public" in transport.lower():
                commute_mode_simple = "Public Transport"
            elif "bike" in transport.lower():
                commute_mode_simple = "Walking/Bike"
            else:
                commute_mode_simple = "Walking/Bike"

            profile_updates["commute_distance_km"] = float(commute_distance)
            profile_updates["electricity_kwh_daily"] = float(electricity_kwh_daily)
            profile_updates["ac_hours_daily"] = float(ac_hours_daily)
            profile_updates["device_hours_daily"] = float(device_hours_daily)
            profile_updates["fan_hours_daily"] = float(fan_hours_daily)
            profile_updates["lights_hours_daily"] = float(lights_hours_daily)
            profile_updates["water_liters_daily"] = float(water_liters_daily)
            profile_updates["waste_kg_daily"] = float(waste_kg_daily)
            profile_updates["plastic_level"] = plastic_norm
            profile_updates["food_diet"] = food_diet

            # Behavior questions per requirement
            profile_updates["order_daily"] = bool(order_daily_bool)
            profile_updates["ac_long_hours"] = bool(ac_long)
            # Use commute_simple radio to influence nudges (as requested)
            profile_updates["commute_mode_simple"] = commute_simple
            profile_updates["waste_food_frequency"] = waste_food_frequency
            profile_updates["recycle_frequency"] = recycle_frequency

            update_session_profile_from_survey(profile_updates)

            # Initialize gamification + histories
            st.session_state.survey_completed = True
            if st.session_state.eco_score_history:
                st.session_state.eco_score_history = []
            if st.session_state.eco_breakdown_history:
                st.session_state.eco_breakdown_history = []
            st.session_state.points = int(st.session_state.points)  # keep
            st.session_state.negative_streak = 0
            st.session_state.food_ignore_count = 0

            seed_history_from_profile()
            compute_eco_score_and_update_history()

            award_points(30, "Completed onboarding survey")
            daily_streak_update()
            maybe_unlock_badges(iso_today())

            st.success("✅ Profile initialized! Your eco thresholds and nudges are now personalized.")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # If survey complete: show Insights + Nudges + Game Zone + Global impact
    compute_eco_score_and_update_history()
    today = iso_today()

    eco_score = get_current_eco_score()
    level = badge_level_from_score(eco_score)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Compute personalized nudges
    user_data = {
        "profile": st.session_state.profile,
        "order_history": st.session_state.order_history,
        "energy_logs": st.session_state.energy_logs,
        "travel_logs": st.session_state.travel_logs,
        "utilities_logs": st.session_state.utilities_logs,
        "today": today,
        "eco_score": eco_score,
        "scores": st.session_state.last_scores,
        "negative_streak": int(st.session_state.negative_streak),
        "food_ignore_count": int(st.session_state.food_ignore_count),
    }
    nudge = generate_nudge(user_data)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='neo-title neo-glow' style='font-size:1.2rem;'>{nudge.get('headline')}</div>", unsafe_allow_html=True)
        for item in nudge.get("nudges", []):
            render_alert_for_nudge(item.get("severity", "mild"), item.get("message", ""))
            st.markdown(f"<div style='color:rgba(230,241,255,0.72);font-weight:900;margin-top:6px;'>Action: {item.get('action','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.2rem;'>🎮 Gamification</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="margin-top:8px;color:rgba(230,241,255,0.72);font-weight:800;">
                Today you’re <span style="color:rgba(0,255,65,0.95)">{level}</span>.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(eco_score / 100.0)
        next_target = next_level_target(eco_score)
        st.markdown(f"<div style='margin-top:8px;color:rgba(230,241,255,0.72);font-weight:900;'>Next level target: {next_target}/100</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Badges row
        st.markdown("<div class='neo-title neo-glow' style='font-size:1.05rem;'>🏅 Badges</div>", unsafe_allow_html=True)
        if st.session_state.badges:
            cols = st.columns(3)
            for i, b in enumerate(st.session_state.badges[:6]):
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div class="neo-card-soft" style="text-align:center;">
                            <div style="font-size:1.2rem;font-weight:900;">🏅</div>
                            <div style="margin-top:6px;font-weight:900;">{b}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Badges unlock automatically as you build consistent eco habits.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Game Zone: daily eco actions
    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown("<div class='neo-title neo-glow' style='font-size:1.2rem;'>🎯 Daily Eco Actions</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(230,241,255,0.72);font-weight:800;'>Log an eco action to earn points and strengthen your streak.</div>", unsafe_allow_html=True)

    actions = [
        ("🚴", "Used low-carbon transit", 15, "Nice! You reduced commuting emissions."),
        ("🌳", "Prepared a home-cooked meal", 25, "Great choice. Cooking usually beats delivery impact."),
        ("♻️", "Recycled / reduced plastic", 10, "Every reuse helps. Plastic penalties will drop."),
        ("🛍️", "Used reusable bags", 8, "Small habit, real difference."),
        ("💧", "Saved water today", 12, "Water efficiency matters—great work."),
        ("💡", "Switched off idle devices", 10, "Energy saved is eco scored."),
    ]

    cols = st.columns(2)
    for i, (emoji, title, pts, msg) in enumerate(actions):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="neo-card-soft">
                    <div style="display:flex; gap:10px; align-items:flex-start;">
                        <div style="font-size:2rem; line-height:1;">{emoji}</div>
                        <div>
                            <div style="font-weight:900; color:rgba(0,255,65,0.95); font-size:1.05rem;">{title}</div>
                            <div style="margin-top:4px; color:rgba(230,241,255,0.72); font-weight:800;">+{pts} points</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Log: {title}", key=f"log_action_{i}", use_container_width=True):
                award_points(pts, title)
                daily_streak_update()
                maybe_unlock_badges(today)
                compute_eco_score_and_update_history()
                st.success(msg)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Global impact section (community pulse)
    st.markdown("<div class='neo-card'>", unsafe_allow_html=True)
    st.markdown("<div class='neo-title neo-glow' style='font-size:1.2rem;'>🌍 Community Pulse</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:rgba(230,241,255,0.72);font-weight:800;'>See how your logged progress can scale.</div>", unsafe_allow_html=True)

    # Compute last 7 days average eco score for community visuals
    last7 = [x for x in st.session_state.eco_score_history if _safe_date(x.get("date")) >= _safe_date(today) - timedelta(days=6)]
    avg = sum(x.get("eco_score", 0) for x in last7) / max(1, len(last7))
    co2_saved_week = sum(x.get("carbon_saved_kg", 0.0) for x in last7)

    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Weekly Carbon Saved", f"{co2_saved_week:.1f} kg")
    with colB:
        st.metric("Eco Trend Avg", f"{avg:.0f}/100")
    with colC:
        st.metric("Eco Level", level)

    # Community growth mini-chart
    fig, ax = plt.subplots(figsize=(10, 4))
    months = ["M1", "M2", "M3", "M4", "M5", "M6"]
    base = 100
    growth = [base + int(i * (1500 / 6)) for i in range(6)]
    # Add minor adjustment based on avg eco score (more eco => more "signal")
    signal = 0.85 + (avg / 100.0) * 0.35
    users = [int(v * signal) for v in growth]
    neon_green_rgba = (0 / 255.0, 255 / 255.0, 65 / 255.0, 0.95)
    ax.plot(months, users, marker="o", color=neon_green_rgba, linewidth=3)
    ax.fill_between(range(len(users)), users, alpha=0.2, color=neon_green_rgba)
    ax.set_title("EcoNudge Pro community growth (simulated)", color="white")
    ax.set_ylabel("Users", color="white")
    ax.grid(True, alpha=0.25, linestyle="--")
    fig.patch.set_facecolor("none")
    ax.tick_params(colors="white")
    st.pyplot(fig)

    # Real-world equivalents for carbon saved
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    trees = int(co2_saved_week / 21.0) if co2_saved_week > 0 else 0  # ~21kg CO2 per tree proxy (simplified)
    st.markdown(
        f"""
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <div class="neo-card-soft" style="min-width: 260px;">
                <div style="font-weight:900;color:rgba(0,255,65,0.95); font-size:1.05rem;">🌳 Equivalent to</div>
                <div style="margin-top:8px;font-weight:900;font-size:1.8rem;color:rgba(0,255,255,0.95);">{trees} trees</div>
                <div style="margin-top:6px;color:rgba(230,241,255,0.72);font-weight:800;">(Approx. weekly impact)</div>
            </div>
            <div class="neo-card-soft" style="min-width: 260px;">
                <div style="font-weight:900;color:rgba(0,255,65,0.95); font-size:1.05rem;">🚗 Avoided driving</div>
                <div style="margin-top:8px;font-weight:900;font-size:1.8rem;color:rgba(0,255,255,0.95);">{int(co2_saved_week * 0.21)} km</div>
                <div style="margin-top:6px;color:rgba(230,241,255,0.72);font-weight:800;">(Approx. weekly impact)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer-neon'>💡 Insights & Nudges</div>", unsafe_allow_html=True)


# -----------------------------
# App Entry / Router
# -----------------------------
def main() -> None:
    load_css()
    init_session_state()

    show_navigation_sidebar()

    pages_map = {
        "Home": home_page,
        "Dashboard": dashboard_page,
        "Smart Food Monitor": food_monitor_page,
        "Energy Tracker": energy_page,
        "Travel Tracker": travel_page,
        "Utilities Tracker": utilities_page,
        "Insights & Nudges": insights_page,
    }
    func = pages_map.get(st.session_state.page, home_page)
    func()

    # Global footer
    st.markdown(
        """
        <div class="footer-neon">
            🌱 EcoNudge Pro · Smart nudges + multi-domain tracking · Built for real interactions
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

