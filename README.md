# Venture: Explainable Multi-Modal AI for Risk-Aware Personalized Hiking in Sri Lanka

## Overview

Venture is an integrated, explainable, multi-modal AI framework developed as part of the IT4010 Final Year Research Project (Project ID: J26-IT-342). 

Hiking and nature-based tourism in Sri Lanka is rapidly growing, yet existing systems primarily provide static trail information and basic navigation. Venture addresses these limitations by supporting the entire hiking lifecycle—from pre-hike planning and environmental awareness to real-time monitoring and emergency response. The platform integrates user preferences, environmental intelligence, physiological monitoring, and emergency response into a unified, modular decision-support system to enhance safety, experience quality, and real-time decision-making for hikers.

---

# Problem Statement

Existing hiking and outdoor tourism support systems focus heavily on navigation, trail discovery, and basic user reviews. They remain largely static, offering limited personalization and minimal consideration of real-time environmental risks or user physiological states. 

Furthermore, explainability is largely missing, making it difficult for users to understand why recommendations or risk predictions are generated. The lack of integrated multi-modal AI systems that combine recommendation, hazard prediction, health monitoring, and emergency response leads to safety risks and poor decision-making, especially for inexperienced users unfamiliar with local Sri Lankan terrain.

---

# Research Objectives

## Main Objective
To develop an Explainable Multi-modal AI framework for personalized, risk-aware hiking recommendation and adventure optimization in Sri Lanka, capable of integrating user preferences, environmental intelligence, physiological monitoring, and emergency response into a unified yet modular decision-support system.

## Specific Objectives

### Objective 01 (Component 1)
Develop an explainable personalized hiking trail recommendation system using hybrid filtering, multi-output ML models (XGBoost/SHAP), and live NLP sentiment analysis for offline-resilient planning.

### Objective 02 (Component 2)
Develop an environmental and social hazard forecasting system by fusing meteorological data with NLP-extracted social media and news signals.

### Objective 03 (Component 3)
Develop a multimodal physiological and performance monitoring system using deep learning to predict fatigue, dehydration, and physical strain in real-time.

### Objective 04 (Component 4)
Develop a context-aware emergency detection and response recommendation system to provide actionable evacuation strategies and rescue guidance.

---

# Research Components

## Component 01 – Pre-Hike Explainable Trail Recommendation Engine
**Developer:** Athulathmudali A.U.N. (IT23156456)

### Responsibilities
- Collect user demographic and preference data via structured questionnaires.
- Build a hiking trail dataset mapping difficulty, distance, elevation, and scenic attributes.
- Train multi-output ML models (XGBoost) to predict suitability, enjoyment, and completion probability.
- Generate explainable outputs using SHAP/LIME for recommendation justification.
- Extract real-time social sentiment and hazard penalties using NLP (VADER) from Reddit and Google News feeds.

### Inputs
- User & Profile Data (Demographics, Fitness level, Preferences, Historical ratings)
- Trail Attributes (Distance, Elevation, Terrain, Difficulty)
- Live Web Feeds (Reddit, Google News RSS)

### Outputs
- Top-N Personalized Trail Recommendations
- Suitability Score, Enjoyment Level, and Completion Probability
- Explainable AI Justifications (SHAP)
- Social Metadata (Sentiment Score, Hazard Penalties, Crowd Levels)

---

## Component 02 – Environmental and Social Hazard Forecasting System
**Developer:** Karunarathne K.D.N.S. (IT23259584)

### Responsibilities
- Collect weather, terrain, and historical disaster data.
- Scrape social media, news, and review-based hazard indicators.
- Apply NLP models (BERT/topic modeling) for hazard extraction.
- Train ML/Deep Learning models for hazard probability and trend forecasting.

### Inputs
- Environmental Data (Weather API, Terrain/Elevation, Sensors, Disaster history)
- Social & Crowd Data (Social media posts, News & reports, Crowdsourced info)

### Outputs
- Environmental Risk Alerts (Hazard type, Risk probability, Risk trend, Risk heat map)

---

## Component 03 – Multimodal Physiological and Performance Monitoring System
**Developer:** Kariyawasam K.L.A.N. (IT23366718)

### Responsibilities
- Acquire and preprocess multimodal wearable sensor datasets.
- Develop deep learning models (LSTM/Transformer fusion) for time-series data.
- Predict fatigue, dehydration, and physical strain levels.
- Generate real-time safety alerts based on physiological thresholds.

### Inputs
- Physiological & Context Data (Heart rate, Accelerometer, GPS/Location, Temperature, Humidity)

### Outputs
- Physiological Health Insights (Fatigue level, Dehydration risk, Physical strain index, Safety alerts)

---

## Component 04 – Context-Aware Emergency Detection and Response Recommendation System
**Developer:** Mihiranga U.G.P.G. (IT23309142)

### Responsibilities
- Collect historical accident and emergency datasets.
- Build multi-class classification models for emergency identification.
- Estimate severity and rescue urgency levels of incidents.
- Develop an explainable AI response recommendation engine.

### Inputs
- Incident & Resource Data (Incident reports, Rescue resources, Hospital locations, Road & terrain data)

### Outputs
- Emergency Response Guidance (Emergency severity, Rescue urgency, Evacuation strategy, Nearest resources, Recommended actions)

---

# End-to-End System Workflow

```text
USER & ENVIRONMENT INPUTS
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│            PROPOSED SYSTEM (MODULAR AI)                 │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ Component 01 │   │ Component 02 │   │ Component 03 │ │
│  │ Trail Recomm.│   │ Hazard Fcst. │   │ Physio Mon.  │ │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘ │
│         │                  │                  │         │
│         └─────────┬────────┴────────┬─────────┘         │
│                   ▼                 ▼                   │
│              DATA FUSION & CONTEXT INTEGRATION          │
│                                                         │
│                       ┌──────────────┐                  │
│                       │ Component 04 │                  │
│                       │ Emergency Rec│                  │
│                       └──────┬───────┘                  │
│                              │                          │
│             EXPLAINABILITY & TRANSPARENCY LAYER (XAI)   │
└─────────────────────────────┬───────────────────────────┘
                              ▼
                     UNIFIED DASHBOARDS
        (Recommendations, Alerts, Evacuation Guidance)
```

---

# Technology Stack

## Mobile Application
- React Native

## Backend
- FastAPI (Python)
- PostgreSQL

## Machine Learning & AI
- **Component 01:** XGBoost, Collaborative Filtering, SHAP/LIME, VADER NLP
- **Component 02:** BERT, Topic Modeling, Scikit-Learn
- **Component 03:** LSTM, Transformer Fusion Architectures
- **Component 04:** Multi-class Classification, Rule-based Reasoning

---

# Database Design

## Component 01
- `users`
- `user_profile`
- `trails`
- `recommendations`

## Component 02

## Component 03
- hiking_sessions
- wearable_sensor_readings
- environmental_readings
- physiological_risk_estimates
- safety_recommendations
- safety_notifications

## Component 04

---

# API Modules

## Component 01
- `GET /profile`
- `POST /recommend`
- `POST /sync-fitness-model`

## Component 02

## Component 03
- GET /weather
- GET /hiking-sessions
- POST /hiking-sessions
- POST /hiking-sessions/{session_id}/end
- POST /ai/predict
- GET /safety-recommendations
- GET /hiking-sessions/{session_id}/summary

## Component 04

---

# Repository Structure

```text
J26-IT-342
├── ML_models/
│   ├── component01/
│   ├── component02/
│   ├── component03/
│   └── component04/
├── backend/
├── database/
├── datasets/
├── deployment/
├── docs/
├── frontend/
│   └── venture_mobileapp/
│       ├── android/
│       ├── ios/
│       ├── lib/
│       ├── linux/
│       └── macos/
├── tests/
└── README.md
```

---

# Current Development Status

## Ongoing
- ML Models training completed.
- Currently integrating the finalized Machine Learning models with the React Native Mobile App via API.

---

# Academic Context
This research project belongs to the Centre of Excellence for AI (COEAI) under the Information Technology (IT) specialization at SLIIT. The system is designed to support SDGs such as Good Health and Well-being (SDG 3), Industry, Innovation and Infrastructure (SDG 9), and Sustainable Cities and Communities (SDG 11).

# License
This repository is intended solely for academic and research purposes at SLIIT University.
