# Venture: Adaptive Multi-Source Reliability-Aware Environmental Hazard Forecasting and Recommendation System

## Overview

Venture is a mobile-based intelligent environmental hazard forecasting and decision-support platform developed as part of the IT342 Final Year Research Project.

The system combines multiple environmental, social, and historical hazard information sources to provide reliable hazard forecasting, risk awareness, and personalized recommendations. The platform addresses the limitations of traditional hazard forecasting systems by incorporating reliability-aware data fusion, social hazard intelligence, machine learning forecasting, and user-centric recommendation generation.

The system is designed to support travellers, hikers, outdoor enthusiasts, local authorities, and the general public by providing timely environmental risk insights and adaptive recommendations.

---

# Problem Statement

Traditional environmental hazard forecasting systems primarily rely on environmental sensor data and weather observations. However, they often overlook valuable information present in social media discussions, public reports, and community observations.

Additionally, different information sources vary significantly in reliability and quality. As a result, hazard warnings generated from multiple sources may contain uncertainty and inconsistencies.

This research aims to develop a reliability-aware multi-source forecasting system capable of:

- Integrating environmental and social information sources
- Assessing source credibility
- Detecting emerging hazard signals
- Generating adaptive hazard forecasts
- Providing actionable recommendations through a mobile application

---

# Research Objectives

## Main Objective

Develop an adaptive multi-source environmental hazard forecasting and recommendation system that combines environmental data, historical hazard records, and social intelligence using reliability-aware data fusion techniques.

## Specific Objectives

### Objective 01

Collect, process, and integrate environmental and historical hazard datasets.

### Objective 02

Develop an adaptive reliability-aware data fusion framework to improve forecasting accuracy.

### Objective 03

Analyze social media and public reports to identify emerging environmental hazards.

### Objective 04

Generate intelligent recommendations and visualizations to support user decision-making.

---

# Research Components

## Component 01 – Environmental Data Processing Module

### Responsibilities

- Weather data collection
- Environmental feature generation
- Historical data integration
- Environmental risk extraction
- Data preprocessing

### Inputs

- Rainfall
- Temperature
- Humidity
- Wind Speed
- Atmospheric Pressure

### Outputs

- Environmental Feature Set
- Risk Indicators

---

## Component 02 – Adaptive Reliability-Aware Multi-Source Fusion Module

### Responsibilities

- Reliability assessment
- Credibility scoring
- Confidence estimation
- Dynamic weighting
- Multi-source information fusion
- Hazard forecasting

### Inputs

- Environmental features
- Social signals
- Hazard history

### Outputs

- Reliability scores
- Fused risk vectors
- Hazard predictions

---

## Component 03 – Social Hazard Intelligence Module

### Responsibilities

- Social data collection
- NLP analysis
- Hazard signal detection
- Topic modelling
- Information extraction

### Inputs

- Social media content
- News articles
- Community reports

### Outputs

- Hazard indicators
- Social risk signals
- Confidence scores

---

## Component 04 – Recommendation and Visualization Module

### Responsibilities

- Recommendation generation
- Risk communication
- Hazard visualization
- User support features
- Interactive heatmaps

### Outputs

- Personalised recommendations
- Safety alerts
- Visual analytics
- Risk maps

---

# End-to-End System Workflow

```text
Environmental Data Sources
            │
            ▼

Data Collection Layer

            │
            ▼

Data Preprocessing Layer

            │

 ┌──────────┴──────────┐

 ▼                     ▼

Component 01     Component 03
Environmental    Social Hazard
Processing       Detection

        │         │

        └────┬────┘

             ▼

Component 02
Reliability Assessment

             ▼

Adaptive Data Fusion

             ▼

Hazard Prediction Engine

             ▼

Component 04
Recommendation Engine

             ▼

PostgreSQL Storage

             ▼

FastAPI APIs

             ▼

React Native Mobile App

             ▼

User Dashboard & Heatmaps
```

---

# Technology Stack

## Mobile Application

- React Native
- Expo
- TypeScript
- Axios
- React Navigation
- React Native Maps

## Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic

## Database

- PostgreSQL
- PostGIS (Planned)

## Machine Learning

- Scikit-Learn
- XGBoost
- LightGBM
- PyTorch
- Transformers (BERT)

## Data Processing

- Pandas
- NumPy
- NLTK
- SpaCy

## Visualization

- Leaflet
- OpenStreetMap
- Recharts

## Version Control

- Git
- GitHub

---

# Repository Structure

```text
J26-IT-342

├── frontend/
│   └── venture_mobileApp/
│
├── backend/
│
├── ML_models/
│   ├── component_1/
│   ├── component_2/
│   ├── component_3/
│   ├── component_4/
│   └── shared/
│
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── final/
│
├── database/
│   ├── schema/
│   ├── seed_data/
│   └── backups/
│
├── deployment/
│
├── docs/
│
├── tests/
│
└── README.md
```

---

# Database Design

## Core Tables

```text
users

weather_data

social_data

hazard_history

processed_weather

processed_social

reliability_scores

fusion_results

prediction_results

recommendations

alerts
```

---

# API Modules

## Weather API

```http
GET /weather
```

## Social Analysis API

```http
POST /analyze-social
```

## Reliability API

```http
POST /reliability
```

## Forecast API

```http
POST /predict
```

## Recommendation API

```http
GET /recommendation
```

## Dashboard API

```http
GET /dashboard
```

---

# Development Workflow

## Branching Strategy

### Main

```text
main
```

Stable codebase.

### Development

```text
develop
```

System integration.

### Component Branches

```text
feature/component-1
feature/component-2
feature/component-3
feature/component-4
```

Individual development branches.

---

# Setup Instructions

## Clone Repository

```bash
git clone <repository-url>
```

```bash
cd J26-IT-342
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Mobile Setup

```bash
cd frontend/venture_mobileApp

npm install

npx expo start
```

---

# Current Development Status

## Completed

- Repository Initialization
- React Native Setup
- FastAPI Setup
- Development Environment Configuration
- GitHub Integration

## Ongoing

- Dataset Collection
- PostgreSQL Integration
- API Development
- Model Development
- Mobile Interface Development
- Component Integration

---

# Expected Outcomes

The final system will provide:

- Environmental hazard forecasting
- Social hazard intelligence
- Reliability-aware risk predictions
- Adaptive multi-source information fusion
- Personalized recommendations
- Interactive mobile visualizations
- Real-time situational awareness

---

# Academic Context

This project is developed as part of the IT342 Research and Development Project and follows the proposed architecture, objectives, and deliverables specified within the approved research proposal and Technical Assessment Form (TAF).

---

# License

This repository is intended solely for academic and research purposes.