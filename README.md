# 🏨 Motel Management System

A simple Windows desktop application for managing motel/apartment bookings and income tracking.

## Features

### 📋 **Apartment Management**
- Add and manage apartments/rooms
- Track room status (Available, Booked, etc.)
- Organize apartments by room number

### 🏨 **Booking System**
- Record guest bookings with check-in/check-out dates
- Track booking price for each reservation
- View all bookings by date

### 💰 **Daily Charges**
- Record daily charges/services for each apartment
- Add descriptions for charges (Food, Laundry, Services, etc.)
- Track daily income separately from bookings

### 📊 **Monthly Analytics**
- Generate monthly income reports
- View total income (Bookings + Daily Charges)
- See breakdown by apartment
- Track income trends

## Setup

### 1. Install Python
Download Python 3.8+ from https://www.python.org/downloads/

### 2. Clone the Repository
```bash
git clone https://github.com/ragirrash/Amed.git
cd Amed
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python main.py
```

## Usage

### **Tab 1: Apartments**
- Enter Room Number (e.g., 101, 102)
- Enter Room Name (e.g., Deluxe Room)
- Click "Add Apartment"
- Click "Refresh" to see all apartments

### **Tab 2: Bookings**
- Room Number: Which apartment is being booked
- Guest Name: Who is booking
- Check-in: Booking start date (YYYY-MM-DD)
- Check-out: Booking end date (YYYY-MM-DD)
- Booking Price: How much they paid
- Click "Add Booking"
- Click "View Bookings" to see all

### **Tab 3: Daily Charges**
- Room Number: Which apartment
- Description: What charge (Coffee, Food, Services, etc.)
- Amount: How much ($)
- Date: When (auto-fills today if empty)
- Click "Add Charge"
- Click "View Charges" to see recent charges

### **Tab 4: Analytics**
- Enter Month: (YYYY-MM format, e.g., 2024-08)
- Click "Generate Report"
- See:
  - Total booking income
  - Total daily charges income
  - **Total combined income**
  - Breakdown by each apartment

## Database

The app creates `hotel_pos.db` automatically with tables for:
- `apartments` - Room information
- `bookings` - Guest reservations and prices
- `daily_charges` - Daily income/charges per room

## File Structure
```
Amed/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── hotel_pos.db        # Database (auto-created on first run)
```

## Example Workflow

1. **Day 1:** Add 5 apartments (101, 102, 103, etc.)
2. **Day 2:** Guest books room 101 for $50/night
3. **Daily:** Record charges (breakfast $5, service $10, etc.)
4. **Month End:** Generate report to see total income

## Data Format

- **Dates:** Use YYYY-MM-DD format (e.g., 2024-08-06)
- **Prices:** Use numbers (e.g., 100 for $100)
- **Month:** Use YYYY-MM format (e.g., 2024-08)

## Support

For issues or questions, check the code or modify as needed!
