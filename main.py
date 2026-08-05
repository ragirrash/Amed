import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta
import os

# Set theme
sg.theme('DarkBlue3')

# Initialize database
def init_db():
    if not os.path.exists('hotel_pos.db'):
        conn = sqlite3.connect('hotel_pos.db')
        c = conn.cursor()
        
        # Apartments/Rooms table
        c.execute('''CREATE TABLE apartments (
            id INTEGER PRIMARY KEY,
            room_number TEXT UNIQUE,
            room_name TEXT,
            status TEXT,
            created_at TIMESTAMP
        )''')
        
        # Bookings table
        c.execute('''CREATE TABLE bookings (
            id INTEGER PRIMARY KEY,
            room_number TEXT,
            guest_name TEXT,
            check_in DATE,
            check_out DATE,
            booking_price REAL,
            status TEXT,
            created_at TIMESTAMP
        )''')
        
        # Daily charges table
        c.execute('''CREATE TABLE daily_charges (
            id INTEGER PRIMARY KEY,
            room_number TEXT,
            charge_date DATE,
            description TEXT,
            amount REAL,
            created_at TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()

# Get all apartments
def get_apartments():
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    c.execute('SELECT room_number, room_name, status FROM apartments ORDER BY room_number')
    apts = c.fetchall()
    conn.close()
    return apts

# Add apartment
def add_apartment(room_number, room_name):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO apartments (room_number, room_name, status) VALUES (?, ?, ?)',
                  (room_number, room_name, 'Available'))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Add booking
def add_booking(room_number, guest_name, check_in, check_out, price):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    c.execute('INSERT INTO bookings (room_number, guest_name, check_in, check_out, booking_price, status) VALUES (?, ?, ?, ?, ?, ?)',
              (room_number, guest_name, check_in, check_out, price, 'Active'))
    conn.commit()
    conn.close()

# Get bookings
def get_bookings(month=None):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    if month:
        c.execute('SELECT room_number, guest_name, check_in, check_out, booking_price FROM bookings WHERE strftime("%Y-%m", check_in) = ?', (month,))
    else:
        c.execute('SELECT room_number, guest_name, check_in, check_out, booking_price FROM bookings ORDER BY check_in DESC')
    bookings = c.fetchall()
    conn.close()
    return bookings

# Add daily charge
def add_daily_charge(room_number, description, amount, charge_date):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    c.execute('INSERT INTO daily_charges (room_number, charge_date, description, amount) VALUES (?, ?, ?, ?)',
              (room_number, charge_date, description, amount))
    conn.commit()
    conn.close()

# Get monthly summary
def get_monthly_summary(year_month):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    
    # Booking income for the month
    c.execute('SELECT SUM(booking_price) FROM bookings WHERE strftime("%Y-%m", check_in) = ?', (year_month,))
    booking_total = c.fetchone()[0] or 0
    
    # Daily charges for the month
    c.execute('SELECT SUM(amount) FROM daily_charges WHERE strftime("%Y-%m", charge_date) = ?', (year_month,))
    daily_total = c.fetchone()[0] or 0
    
    # Get breakdown by room
    c.execute('''SELECT room_number, SUM(booking_price) as booking_income FROM bookings 
                 WHERE strftime("%Y-%m", check_in) = ? GROUP BY room_number''', (year_month,))
    room_bookings = c.fetchall()
    
    c.execute('''SELECT room_number, SUM(amount) as daily_income FROM daily_charges 
                 WHERE strftime("%Y-%m", charge_date) = ? GROUP BY room_number''', (year_month,))
    room_daily = c.fetchall()
    
    conn.close()
    
    return {
        'booking_total': booking_total,
        'daily_total': daily_total,
        'total': booking_total + daily_total,
        'room_bookings': room_bookings,
        'room_daily': room_daily
    }

# Main window with tabs
def main():
    init_db()
    
    # TAB 1: Apartment Management
    apt_tab = [
        [sg.Text('APARTMENT MANAGEMENT', font=('Arial', 12, 'bold'))],
        [sg.HSeparator()],
        [sg.Text('Room Number:'), sg.InputText(size=(10,), key='APT_ROOM_NUM')],
        [sg.Text('Room Name:'), sg.InputText(size=(15,), key='APT_ROOM_NAME')],
        [sg.Button('Add Apartment', size=(15,)), sg.Button('Refresh', size=(15,))],
        [sg.HSeparator()],
        [sg.Multiline(size=(50, 15), key='APT_LIST', disabled=True)],
    ]
    
    # TAB 2: Bookings
    booking_tab = [
        [sg.Text('ADD BOOKING', font=('Arial', 12, 'bold'))],
        [sg.HSeparator()],
        [sg.Text('Room Number:'), sg.InputText(size=(10,), key='BOOK_ROOM')],
        [sg.Text('Guest Name:'), sg.InputText(size=(20,), key='BOOK_GUEST')],
        [sg.Text('Check-in (YYYY-MM-DD):'), sg.InputText(size=(15,), key='BOOK_CHECKIN')],
        [sg.Text('Check-out (YYYY-MM-DD):'), sg.InputText(size=(15,), key='BOOK_CHECKOUT')],
        [sg.Text('Booking Price:'), sg.InputText(size=(10,), key='BOOK_PRICE')],
        [sg.Button('Add Booking', size=(15,)), sg.Button('View Bookings', size=(15,))],
        [sg.HSeparator()],
        [sg.Multiline(size=(50, 15), key='BOOKING_LIST', disabled=True)],
    ]
    
    # TAB 3: Daily Charges
    charge_tab = [
        [sg.Text('ADD DAILY CHARGE', font=('Arial', 12, 'bold'))],
        [sg.HSeparator()],
        [sg.Text('Room Number:'), sg.InputText(size=(10,), key='CHARGE_ROOM')],
        [sg.Text('Description:'), sg.InputText(size=(20,), key='CHARGE_DESC')],
        [sg.Text('Amount:'), sg.InputText(size=(10,), key='CHARGE_AMOUNT')],
        [sg.Text('Date (YYYY-MM-DD):'), sg.InputText(size=(15,), key='CHARGE_DATE')],
        [sg.Button('Add Charge', size=(15,)), sg.Button('View Charges', size=(15,))],
        [sg.HSeparator()],
        [sg.Multiline(size=(50, 15), key='CHARGE_LIST', disabled=True)],
    ]
    
    # TAB 4: Monthly Analytics
    analytics_tab = [
        [sg.Text('MONTHLY INCOME REPORT', font=('Arial', 12, 'bold'))],
        [sg.HSeparator()],
        [sg.Text('Select Month (YYYY-MM):'), sg.InputText(size=(10,), key='REPORT_MONTH', default_text=datetime.now().strftime('%Y-%m'))],
        [sg.Button('Generate Report', size=(15,))],
        [sg.HSeparator()],
        [sg.Multiline(size=(50, 25), key='REPORT_DISPLAY', disabled=True)],
    ]
    
    # Create tabbed layout
    layout = [
        [sg.TabGroup([[
            sg.Tab('Apartments', apt_tab),
            sg.Tab('Bookings', booking_tab),
            sg.Tab('Daily Charges', charge_tab),
            sg.Tab('Analytics', analytics_tab),
        ]], key='TABS')],
        [sg.Button('Exit', size=(15,))],
    ]
    
    window = sg.Window('MOTEL MANAGEMENT SYSTEM', layout, size=(600, 600))
    
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        
        # APARTMENT TAB EVENTS
        if event == 'Add Apartment':
            room_num = values['APT_ROOM_NUM'].strip()
            room_name = values['APT_ROOM_NAME'].strip()
            if room_num and room_name:
                if add_apartment(room_num, room_name):
                    sg.popup_ok('Apartment added successfully!')
                    window['APT_ROOM_NUM'].update('')
                    window['APT_ROOM_NAME'].update('')
                else:
                    sg.popup_error('Room number already exists!')
            else:
                sg.popup_error('Fill all fields!')
        
        if event == 'Refresh':
            apts = get_apartments()
            apt_text = 'Room #    |    Name           |    Status\n' + '-'*50 + '\n'
            for apt in apts:
                apt_text += f"{apt[0]:<8} | {apt[1]:<18} | {apt[2]}\n"
            window['APT_LIST'].update(apt_text)
        
        # BOOKING TAB EVENTS
        if event == 'Add Booking':
            try:
                room = values['BOOK_ROOM'].strip()
                guest = values['BOOK_GUEST'].strip()
                checkin = values['BOOK_CHECKIN'].strip()
                checkout = values['BOOK_CHECKOUT'].strip()
                price = float(values['BOOK_PRICE'].strip())
                
                if room and guest and checkin and checkout and price:
                    add_booking(room, guest, checkin, checkout, price)
                    sg.popup_ok('Booking added!')
                    window['BOOK_ROOM'].update('')
                    window['BOOK_GUEST'].update('')
                    window['BOOK_CHECKIN'].update('')
                    window['BOOK_CHECKOUT'].update('')
                    window['BOOK_PRICE'].update('')
                else:
                    sg.popup_error('Fill all fields!')
            except:
                sg.popup_error('Invalid price format!')
        
        if event == 'View Bookings':
            bookings = get_bookings()
            book_text = 'Room# | Guest         | Check-in   | Check-out  | Price\n' + '-'*60 + '\n'
            for book in bookings:
                book_text += f"{book[0]:<5} | {book[1]:<13} | {book[2]} | {book[3]} | ${book[4]}\n"
            window['BOOKING_LIST'].update(book_text)
        
        # DAILY CHARGES TAB EVENTS
        if event == 'Add Charge':
            try:
                room = values['CHARGE_ROOM'].strip()
                desc = values['CHARGE_DESC'].strip()
                amount = float(values['CHARGE_AMOUNT'].strip())
                date = values['CHARGE_DATE'].strip() or datetime.now().strftime('%Y-%m-%d')
                
                if room and desc and amount:
                    add_daily_charge(room, desc, amount, date)
                    sg.popup_ok('Charge added!')
                    window['CHARGE_ROOM'].update('')
                    window['CHARGE_DESC'].update('')
                    window['CHARGE_AMOUNT'].update('')
                    window['CHARGE_DATE'].update('')
                else:
                    sg.popup_error('Fill all fields!')
            except:
                sg.popup_error('Invalid amount format!')
        
        if event == 'View Charges':
            month = datetime.now().strftime('%Y-%m')
            summary = get_monthly_summary(month)
            
            conn = sqlite3.connect('hotel_pos.db')
            c = conn.cursor()
            c.execute('SELECT room_number, charge_date, description, amount FROM daily_charges ORDER BY charge_date DESC LIMIT 50')
            charges = c.fetchall()
            conn.close()
            
            charge_text = 'Room# | Date       | Description    | Amount\n' + '-'*60 + '\n'
            for charge in charges:
                charge_text += f"{charge[0]:<5} | {charge[1]} | {charge[2]:<14} | ${charge[3]:.2f}\n"
            window['CHARGE_LIST'].update(charge_text)
        
        # ANALYTICS TAB EVENTS
        if event == 'Generate Report':
            month = values['REPORT_MONTH'].strip()
            if month:
                summary = get_monthly_summary(month)
                
                report = f"\n{'='*60}\n"
                report += f"MONTHLY INCOME REPORT - {month}\n"
                report += f"{'='*60}\n\n"
                
                report += f"BOOKING INCOME:        ${summary['booking_total']:.2f}\n"
                report += f"DAILY CHARGES INCOME:  ${summary['daily_total']:.2f}\n"
                report += f"{'-'*60}\n"
                report += f"TOTAL INCOME:          ${summary['total']:.2f}\n"
                report += f"{'='*60}\n\n"
                
                report += "BREAKDOWN BY ROOM:\n"
                report += "-"*60 + "\n"
                report += "Room# | Booking Income | Daily Income | Total\n"
                report += "-"*60 + "\n"
                
                all_rooms = set()
                for room, amount in summary['room_bookings']:
                    all_rooms.add(room)
                for room, amount in summary['room_daily']:
                    all_rooms.add(room)
                
                for room in sorted(all_rooms):
                    booking = next((x[1] for x in summary['room_bookings'] if x[0] == room), 0)
                    daily = next((x[1] for x in summary['room_daily'] if x[0] == room), 0)
                    total = booking + daily
                    report += f"{room:<5} | ${booking:>13.2f} | ${daily:>11.2f} | ${total:>7.2f}\n"
                
                window['REPORT_DISPLAY'].update(report)
            else:
                sg.popup_error('Enter a month (YYYY-MM)!')
    
    window.close()

if __name__ == '__main__':
    main()
