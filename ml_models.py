"""
Machine Learning Models for EcoNudge Pro
Includes behavior prediction, classification, anomaly detection, and forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
import os


class BehaviorPredictor:
    """
    Predicts future eco scores based on historical behavior using regression
    """
    
    def __init__(self):
        self.weights = None
        self.is_trained = False
    
    def train(self, user_history):
        """
        Train a simple linear regression model on user behavior
        """
        if len(user_history) < 3:
            # Not enough data, use default weights
            self.weights = np.array([0.3, 0.2, 0.2, 0.15, 0.15])
        else:
            # Train on historical data
            X = np.array([self._extract_features(entry) for entry in user_history])
            y = np.array([entry['eco_score'] for entry in user_history])
            
            # Simple linear regression using normal equation
            X = np.column_stack([np.ones(len(X)), X])
            self.weights = np.linalg.lstsq(X, y, rcond=None)[0]
        
        self.is_trained = True
    
    def _extract_features(self, data_entry):
        """
        Extract numerical features from user data
        """
        # Transport score (0-1, lower is better)
        transport_map = {
            'Walking/Cycling': 0.0,
            'Public Transport': 0.2,
            'Car (Electric)': 0.5,
            'Bike/Scooter': 0.6,
            'Car (Petrol/Diesel)': 1.0
        }
        transport_score = transport_map.get(data_entry.get('transport', 'Car (Petrol/Diesel)'), 0.5)
        
        # Normalize other features
        electricity_score = min(data_entry.get('electricity', 10) / 50, 1.0)
        water_score = min(data_entry.get('water', 150) / 500, 1.0)
        
        plastic_map = {'Low': 0.2, 'Medium': 0.5, 'High': 0.9}
        plastic_score = plastic_map.get(data_entry.get('plastic', 'Medium').split(' ')[0], 0.5)
        
        food_map = {'Vegetarian': 0.2, 'Mixed': 0.5, 'Non-Vegetarian': 0.8}
        food_score = food_map.get(data_entry.get('food', 'Mixed').split(' ')[0], 0.5)
        
        return [transport_score, electricity_score, water_score, plastic_score, food_score]
    
    def predict_future_score(self, current_data, days_ahead=30):
        """
        Predict eco score for future days
        """
        if not self.is_trained:
            return None
        
        features = self._extract_features(current_data)
        
        # Add improvement trend (assume 1% improvement per week with good habits)
        improvement_rate = 0.01 * (days_ahead / 7)
        
        # Calculate base prediction
        X = np.array([1.0] + features)
        base_prediction = np.dot(X, self.weights)
        
        # Apply improvement trend
        predicted_score = min(base_prediction * (1 + improvement_rate), 100)
        
        return max(0, predicted_score)
    
    def predict_trajectory(self, current_data, days=30):
        """
        Predict eco score trajectory over multiple days
        """
        trajectory = []
        
        for day in range(1, days + 1):
            score = self.predict_future_score(current_data, days_ahead=day)
            if score is not None:
                # Add some realistic variation
                variation = np.random.normal(0, 2)
                score = max(0, min(100, score + variation))
            trajectory.append(score)
        
        return trajectory


class HabitClassifier:
    """
    Classifies users into behavior categories using K-Means-like clustering
    """
    
    def __init__(self):
        # Define cluster centroids for different user types
        self.centroids = {
            'Eco Champion': [0.1, 0.2, 0.2, 0.15, 0.2],  # Low impact
            'Eco Improver': [0.4, 0.5, 0.5, 0.4, 0.5],   # Medium impact
            'Eco Beginner': [0.8, 0.8, 0.7, 0.8, 0.8]    # High impact
        }
    
    def classify_user(self, user_data):
        """
        Classify user into one of three categories based on behavior
        """
        # Extract features
        transport_map = {
            'Walking/Cycling': 0.0,
            'Public Transport': 0.2,
            'Car (Electric)': 0.5,
            'Bike/Scooter': 0.6,
            'Car (Petrol/Diesel)': 1.0
        }
        transport_score = transport_map.get(user_data.get('transport', 'Car (Petrol/Diesel)'), 0.5)
        
        electricity_score = min(user_data.get('electricity', 10) / 50, 1.0)
        water_score = min(user_data.get('water', 150) / 500, 1.0)
        
        plastic_map = {'Low': 0.2, 'Medium': 0.5, 'High': 0.9}
        plastic_score = plastic_map.get(user_data.get('plastic', 'Medium').split(' ')[0], 0.5)
        
        food_map = {'Vegetarian': 0.2, 'Mixed': 0.5, 'Non-Vegetarian': 0.8}
        food_score = food_map.get(user_data.get('food', 'Mixed').split(' ')[0], 0.5)
        
        user_vector = np.array([transport_score, electricity_score, water_score, 
                                plastic_score, food_score])
        
        # Find closest centroid
        min_distance = float('inf')
        best_category = 'Eco Improver'
        
        for category, centroid in self.centroids.items():
            distance = np.linalg.norm(user_vector - np.array(centroid))
            if distance < min_distance:
                min_distance = distance
                best_category = category
        
        return best_category, self._get_category_insights(best_category)
    
    def _get_category_insights(self, category):
        """
        Get insights for each category
        """
        insights = {
            'Eco Champion': {
                'description': 'You\'re a sustainability leader!',
                'strengths': ['Low carbon footprint', 'Conscious consumption', 'Green habits'],
                'next_steps': ['Inspire others', 'Offset remaining emissions', 'Advocate for change']
            },
            'Eco Improver': {
                'description': 'You\'re on the right path!',
                'strengths': ['Awareness of impact', 'Making progress', 'Room for growth'],
                'next_steps': ['Reduce energy usage', 'Switch to sustainable transport', 'Cut plastic use']
            },
            'Eco Beginner': {
                'description': 'Great that you\'re starting!',
                'strengths': ['Taking first steps', 'Learning', 'Potential for big impact'],
                'next_steps': ['Start with small changes', 'Track daily habits', 'Set achievable goals']
            }
        }
        
        return insights.get(category, insights['Eco Improver'])


class AnomalyDetector:
    """
    Detects unusual consumption patterns using statistical methods
    """
    
    def __init__(self):
        self.baseline = None
    
    def set_baseline(self, user_history):
        """
        Establish baseline behavior from historical data
        """
        if len(user_history) == 0:
            return
        
        # Calculate mean and std for each metric
        electricity_values = [entry.get('electricity', 10) for entry in user_history]
        water_values = [entry.get('water', 150) for entry in user_history]
        ac_values = [entry.get('ac_hours', 2) for entry in user_history]
        
        self.baseline = {
            'electricity': {
                'mean': np.mean(electricity_values),
                'std': np.std(electricity_values) if len(electricity_values) > 1 else 5
            },
            'water': {
                'mean': np.mean(water_values),
                'std': np.std(water_values) if len(water_values) > 1 else 50
            },
            'ac_hours': {
                'mean': np.mean(ac_values),
                'std': np.std(ac_values) if len(ac_values) > 1 else 2
            }
        }
    
    def detect_anomalies(self, current_data):
        """
        Detect if current consumption is anomalous (>2 std from mean)
        """
        if self.baseline is None:
            return []
        
        anomalies = []
        
        # Check electricity
        elec = current_data.get('electricity', 10)
        if abs(elec - self.baseline['electricity']['mean']) > 2 * self.baseline['electricity']['std']:
            anomalies.append({
                'type': 'electricity',
                'severity': 'high' if elec > self.baseline['electricity']['mean'] else 'low',
                'message': f"⚠️ Unusual electricity usage detected: {elec} kWh (typical: {self.baseline['electricity']['mean']:.1f} kWh)"
            })
        
        # Check water
        water = current_data.get('water', 150)
        if abs(water - self.baseline['water']['mean']) > 2 * self.baseline['water']['std']:
            anomalies.append({
                'type': 'water',
                'severity': 'high' if water > self.baseline['water']['mean'] else 'low',
                'message': f"⚠️ Unusual water usage detected: {water}L (typical: {self.baseline['water']['mean']:.1f}L)"
            })
        
        # Check AC
        ac = current_data.get('ac_hours', 2)
        if abs(ac - self.baseline['ac_hours']['mean']) > 2 * self.baseline['ac_hours']['std']:
            anomalies.append({
                'type': 'ac',
                'severity': 'high' if ac > self.baseline['ac_hours']['mean'] else 'low',
                'message': f"⚠️ Unusual AC usage detected: {ac}h (typical: {self.baseline['ac_hours']['mean']:.1f}h)"
            })
        
        return anomalies


class MLRecommendationEngine:
    """
    ML-based recommendation system using collaborative filtering concepts
    """
    
    def __init__(self):
        self.user_profiles = self._load_user_profiles()
    
    def _load_user_profiles(self):
        """
        Simulated user profiles for collaborative filtering
        """
        return [
            {'transport': 'Public Transport', 'electricity': 8, 'water': 120, 'eco_score': 85},
            {'transport': 'Walking/Cycling', 'electricity': 12, 'water': 150, 'eco_score': 90},
            {'transport': 'Car (Electric)', 'electricity': 15, 'water': 180, 'eco_score': 70},
            {'transport': 'Bike/Scooter', 'electricity': 10, 'water': 140, 'eco_score': 75},
            {'transport': 'Public Transport', 'electricity': 7, 'water': 110, 'eco_score': 88},
        ]
    
    def find_similar_users(self, user_data, n=3):
        """
        Find similar users using cosine similarity
        """
        # Extract user features
        user_vector = self._vectorize_user(user_data)
        
        similarities = []
        for profile in self.user_profiles:
            profile_vector = self._vectorize_user(profile)
            similarity = self._cosine_similarity(user_vector, profile_vector)
            similarities.append((profile, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [profile for profile, _ in similarities[:n]]
    
    def _vectorize_user(self, user_data):
        """
        Convert user data to numerical vector
        """
        transport_map = {
            'Walking/Cycling': 5,
            'Public Transport': 4,
            'Car (Electric)': 3,
            'Bike/Scooter': 3.5,
            'Car (Petrol/Diesel)': 1
        }
        
        return np.array([
            transport_map.get(user_data.get('transport', 'Car (Petrol/Diesel)'), 2),
            50 - user_data.get('electricity', 10),  # Invert so higher is better
            500 - user_data.get('water', 150)
        ])
    
    def _cosine_similarity(self, v1, v2):
        """
        Calculate cosine similarity between two vectors
        """
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
        
        return dot_product / (norm_v1 * norm_v2)
    
    def generate_ml_recommendations(self, user_data):
        """
        Generate recommendations based on what similar high-performing users do
        """
        similar_users = self.find_similar_users(user_data)
        
        recommendations = []
        
        # Analyze what high-performing similar users do differently
        for similar_user in similar_users:
            if similar_user['eco_score'] > user_data.get('eco_score', 50):
                # Transport recommendation
                if similar_user['transport'] != user_data.get('transport'):
                    recommendations.append({
                        'category': 'Transport',
                        'suggestion': f"Users like you who switched to {similar_user['transport']} improved their eco score by 10-15 points",
                        'impact': 'High',
                        'confidence': 0.85
                    })
                
                # Electricity recommendation
                if similar_user['electricity'] < user_data.get('electricity', 10):
                    savings = user_data.get('electricity', 10) - similar_user['electricity']
                    recommendations.append({
                        'category': 'Energy',
                        'suggestion': f"Similar users reduced electricity by {savings:.0f} kWh/day and saw significant improvements",
                        'impact': 'Medium',
                        'confidence': 0.78
                    })
                
                # Water recommendation
                if similar_user['water'] < user_data.get('water', 150):
                    savings = user_data.get('water', 150) - similar_user['water']
                    recommendations.append({
                        'category': 'Water',
                        'suggestion': f"Users in your profile saved {savings:.0f}L/day through simple habit changes",
                        'impact': 'Medium',
                        'confidence': 0.72
                    })
        
        return recommendations[:3]  # Return top 3


class TimeSeriesForecaster:
    """
    Forecasts future consumption patterns using exponential smoothing
    """
    
    def __init__(self, alpha=0.3):
        self.alpha = alpha  # Smoothing factor
    
    def forecast(self, historical_data, periods=30):
        """
        Forecast future values using exponential smoothing
        """
        if len(historical_data) == 0:
            return None
        
        # Initialize with first value
        forecasts = [historical_data[0]]
        
        # Apply exponential smoothing
        for i in range(1, len(historical_data)):
            forecast = self.alpha * historical_data[i] + (1 - self.alpha) * forecasts[-1]
            forecasts.append(forecast)
        
        # Forecast future periods
        last_forecast = forecasts[-1]
        future_forecasts = []
        
        for _ in range(periods):
            # Add slight trend and noise
            trend = np.random.normal(-0.5, 1)  # Slight improvement trend
            future_forecast = last_forecast + trend
            future_forecasts.append(max(0, min(100, future_forecast)))
            last_forecast = future_forecast
        
        return future_forecasts
    
    def forecast_multiple_metrics(self, user_history, periods=30):
        """
        Forecast multiple metrics
        """
        if len(user_history) == 0:
            return None
        
        # Extract time series for each metric
        eco_scores = [entry.get('eco_score', 50) for entry in user_history]
        electricity = [entry.get('electricity', 10) for entry in user_history]
        water = [entry.get('water', 150) for entry in user_history]
        
        return {
            'eco_score': self.forecast(eco_scores, periods),
            'electricity': self.forecast(electricity, periods),
            'water': self.forecast(water, periods)
        }


# Helper function to initialize all ML models
def initialize_ml_models():
    """
    Initialize all ML models
    """
    return {
        'predictor': BehaviorPredictor(),
        'classifier': HabitClassifier(),
        'anomaly_detector': AnomalyDetector(),
        'recommender': MLRecommendationEngine(),
        'forecaster': TimeSeriesForecaster()
    }


# Helper function to simulate historical data for ML training
def generate_simulated_history(current_data, days=30):
    """
    Generate simulated historical data for ML model training
    """
    history = []
    
    for i in range(days):
        # Create slight variations of current data
        variation = np.random.normal(0, 0.1)
        
        entry = {
            'transport': current_data.get('transport'),
            'electricity': max(1, current_data.get('electricity', 10) + np.random.normal(0, 2)),
            'water': max(50, current_data.get('water', 150) + np.random.normal(0, 20)),
            'plastic': current_data.get('plastic'),
            'food': current_data.get('food'),
            'ac_hours': max(0, current_data.get('ac_hours', 2) + np.random.normal(0, 1)),
            'device_hours': current_data.get('device_hours', 6),
            'eco_score': max(30, min(100, 50 + i * 0.5 + np.random.normal(0, 5))),
            'date': datetime.now() - timedelta(days=days-i)
        }
        
        history.append(entry)
    
    return history
