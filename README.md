# 🚦 AI Traffic Controller - Smart Traffic Management System

[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-green.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-2.0-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered traffic management system for 4-way intersections that detects vehicles in real-time using YOLOv8 and controls traffic signals with clockwise flow and emergency priority.

## 📸 Screenshots
*Add your dashboard screenshots here*

## ✨ Features

- ✅ **Real-time vehicle detection** using YOLOv8 AI model
- ✅ **Live traffic monitoring** with backend API
- ✅ **Clockwise signal flow** (North → East → South → West)
- ✅ **3 seconds per vehicle** rule for signal timing
- ✅ **Emergency vehicle priority** - selected road gets GREEN, others RED
- ✅ **Auto-return to normal flow** after emergency
- ✅ **Snapshot-based simulation** - captures current traffic data
- ✅ **Beautiful glass-morphism dashboard** with animations

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Glass-morphism UI)
- **Backend**: Python, Flask, Flask-CORS
- **AI/ML**: YOLOv8, Ultralytics, OpenCV
- **Tracking**: ByteTrack (Kalman filter based)

## 📋 Project Structure
AI-Traffic-Controller/
├── 📁 backend/
│ └── 📄 app.py # Flask backend API
├── 📁 cv/
│ └── 📄 yolo_vehicle_count.py # YOLO AI detection
├── 📁 data/
│ └── 📄 traffic.mp4 # Your traffic video
└── 📄 dashboard.html # Main dashboard UI
