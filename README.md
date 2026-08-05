# 🏨 Hotel POS System

A simple Windows desktop POS (Point of Sale) application for hotels.

## Features
- ✅ Room-based billing
- ✅ Menu item selection
- ✅ Bill tracking
- ✅ Payment processing
- ✅ Local SQLite database

## Setup

### 1. Install Python
Download Python 3.8+ from https://www.python.org/downloads/

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python main.py
```

## Usage

1. **Enter Room Number** - Select which room is ordering
2. **Select Items** - Choose from menu (Coffee, Tea, Food, Snacks, etc.)
3. **Set Quantity** - Default is 1
4. **Add to Bill** - Item appears in bill
5. **Process Payment** - Complete the transaction
6. **Print Bill** - Print receipt

## File Structure
```
Amed/
├── main.py              # Main app
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── hotel_pos.db        # Database (auto-created)
```

## Next Steps
- Add more menu items to database
- Customize prices
- Add receipt printing
- Add staff login
- Add reports/analytics
