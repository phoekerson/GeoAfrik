# 🌍 SURUWA - Flood Prevention Desktop App for Africa

**SURUWA** is a desktop application built with Python and Tkinter, designed to **predict, alert, and protect African populations from flood risks**. It was developed during a hackathon and integrates real-time weather data and interactive maps to empower both citizens and crisis managers.

---
<img width="1590" height="857" alt="Dashboard_suruwa" src="https://github.com/user-attachments/assets/258c07b6-40b0-4d90-a75c-7663127cfe2d" />


## 🔍 Why "SURUWA"?

> "Suruwa" combines the Yoruba word *“Suru”* (protection/prevention) and *“Wa”* (to come), symbolizing a **proactive alert system that comes to you before disaster strikes**.

Africa faces recurring floods every year, leading to loss of lives, mass displacement, and economic damage. **SURUWA** aims to anticipate such events and deliver timely alerts, even in areas with limited internet or infrastructure.

---

## 💡 Features

### 🧍 For Citizens:
- Real-time local weather forecast (via OpenWeatherMap API)
- Visual flood risk indicator (Green, Orange, Red)
- Interactive map showing the selected location
- Offline-friendly interface
- Simple and multilingual-friendly design

### 🛠️ For Administrators:
- Manual alert broadcasting by region and severity
- Custom message editor
- Risk level selector
- Future-ready design for satellite/IoT/weather data integration

---

## 🖥️ Technologies Used
- `Python 3.x`
- `Tkinter` for GUI
- `Folium` for interactive maps
- `OpenWeatherMap API` for real-time weather
- `tkhtmlview` to integrate HTML maps in GUI
- `PyInstaller` for `.exe` file generation

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/suruwasoft.git
cd suruwasoft
pip install -r requirements.txt
python suruwasoft.py
