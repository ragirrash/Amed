import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta
import os

# Set modern theme and colors
sg.theme('DarkBlue3')
sg.set_options(font=('Segoe UI', 10))

# Color scheme
HEADER_COLOR = '#2C3E50'
BUTTON_COLOR = ('#FFFFFF', '#3498DB')
BUTTON_HOVER = ('#FFFFFF', '#2980B9')
TEXT_COLOR = '#2C3E50'

# Initialize database
def init_db():
    if not os.path.exists('hotel_pos.db'):
        conn = sqlite3.connect('hotel_pos.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE apartments (
            id INTEGER PRIMARY KEY,
            room_number TEXT UNIQUE,
            room_name TEXT,
            status TEXT,
            created_at TIMESTAMP
        )''')
        
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
    
    c.execute('SELECT SUM(booking_price) FROM bookings WHERE strftime("%Y-%m", check_in) = ?', (year_month,))
    booking_total = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(amount) FROM daily_charges WHERE strftime("%Y-%m", charge_date) = ?', (year_month,))
    daily_total = c.fetchone()[0] or 0
    
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
        [sg.Text('🏠 APARTMENT MANAGEMENT', font=('Segoe UI', 13, 'bold'), text_color=HEADER_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Room Number:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(12,), key='APT_ROOM_NUM', font=('Segoe UI', 10))],
        [sg.Text('Room Name:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(20,), key='APT_ROOM_NAME', font=('Segoe UI', 10))],
        [sg.Button('➕ Add Apartment', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR), 
         sg.Button('🔄 Refresh List', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Room List:', font=('Segoe UI', 10, 'bold'))],
        [sg.Multiline(size=(60, 18), key='APT_LIST', disabled=True, font=('Courier', 9))],
    ]
    
    # TAB 2: Bookings
    booking_tab = [
        [sg.Text('🛏️ BOOKING MANAGEMENT', font=('Segoe UI', 13, 'bold'), text_color=HEADER_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Room Number:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(12,), key='BOOK_ROOM', font=('Segoe UI', 10))],
        [sg.Text('Guest Name:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(25,), key='BOOK_GUEST', font=('Segoe UI', 10))],
        [sg.Text('Check-in:', font=('Segoe UI', 10, 'bold')), 
         sg.InputText(size=(15,), key='BOOK_CHECKIN', readonly=True, font=('Segoe UI', 10)), 
         sg.Button('📅', key='BOOK_CHECKIN_BTN', size=(2,1), font=('Segoe UI', 12))],
        [sg.Text('Check-out:', font=('Segoe UI', 10, 'bold')), 
         sg.InputText(size=(15,), key='BOOK_CHECKOUT', readonly=True, font=('Segoe UI', 10)), 
         sg.Button('📅', key='BOOK_CHECKOUT_BTN', size=(2,1), font=('Segoe UI', 12))],
        [sg.Text('Booking Price (₹):', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(12,), key='BOOK_PRICE', font=('Segoe UI', 10))],
        [sg.Button('✅ Add Booking', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR), 
         sg.Button('📋 View Bookings', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Booking List:', font=('Segoe UI', 10, 'bold'))],
        [sg.Multiline(size=(60, 12), key='BOOKING_LIST', disabled=True, font=('Courier', 9))],
    ]
    
    # TAB 3: Daily Charges
    charge_tab = [
        [sg.Text('💰 DAILY CHARGES', font=('Segoe UI', 13, 'bold'), text_color=HEADER_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Room Number:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(12,), key='CHARGE_ROOM', font=('Segoe UI', 10))],
        [sg.Text('Description:', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(25,), key='CHARGE_DESC', font=('Segoe UI', 10))],
        [sg.Text('Amount (₹):', font=('Segoe UI', 10, 'bold')), sg.InputText(size=(12,), key='CHARGE_AMOUNT', font=('Segoe UI', 10))],
        [sg.Text('Date:', font=('Segoe UI', 10, 'bold')), 
         sg.InputText(size=(15,), key='CHARGE_DATE', readonly=True, font=('Segoe UI', 10)), 
         sg.Button('📅', key='CHARGE_DATE_BTN', size=(2,1), font=('Segoe UI', 12))],
        [sg.Button('➕ Add Charge', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR), 
         sg.Button('📊 View Charges', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Recent Charges:', font=('Segoe UI', 10, 'bold'))],
        [sg.Multiline(size=(60, 15), key='CHARGE_LIST', disabled=True, font=('Courier', 9))],
    ]
    
    # TAB 4: Monthly Analytics
    analytics_tab = [
        [sg.Text('📊 MONTHLY INCOME REPORT', font=('Segoe UI', 13, 'bold'), text_color=HEADER_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Select Month:', font=('Segoe UI', 10, 'bold')), 
         sg.InputText(size=(12,), key='REPORT_MONTH', default_text=datetime.now().strftime('%Y-%m'), readonly=True, font=('Segoe UI', 10)), 
         sg.Button('📅', key='REPORT_MONTH_BTN', size=(2,1), font=('Segoe UI', 12))],
        [sg.Button('📈 Generate Report', size=(16,1), font=('Segoe UI', 10, 'bold'), button_color=BUTTON_COLOR)],
        [sg.HSeparator()],
        [sg.Text('Report:', font=('Segoe UI', 10, 'bold'))],
        [sg.Multiline(size=(60, 25), key='REPORT_DISPLAY', disabled=True, font=('Courier', 10))],
    ]
    
    # Create tabbed layout
    layout = [
        [sg.Text('🏨 MOTEL MANAGEMENT SYSTEM', font=('Segoe UI', 16, 'bold'), text_color=HEADER_COLOR, justification='center')],
        [sg.HSeparator()],
        [sg.TabGroup([[
            sg.Tab('🏠 Apartments', apt_tab, font=('Segoe UI', 11)),
            sg.Tab('🛏️ Bookings', booking_tab, font=('Segoe UI', 11)),
            sg.Tab('💰 Charges', charge_tab, font=('Segoe UI', 11)),
            sg.Tab('📊 Analytics', analytics_tab, font=('Segoe UI', 11)),
        ]], key='TABS', font=('Segoe UI', 11, 'bold'))],
        [sg.Button('❌ Exit', size=(15,1), font=('Segoe UI', 10, 'bold'), button_color=('#FFFFFF', '#E74C3C'))],
    ]
    
    window = sg.Window('MOTEL MANAGEMENT SYSTEM', layout, size=(750, 750), finalize=True)
    
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == '❌ Exit':
            break
        
        # APARTMENT TAB EVENTS
        if event == '➕ Add Apartment':
            room_num = values['APT_ROOM_NUM'].strip()
            room_name = values['APT_ROOM_NAME'].strip()
            if room_num and room_name:
                if add_apartment(room_num, room_name):
                    sg.popup_ok('✅ Apartment added successfully!', title='Success')
                    window['APT_ROOM_NUM'].update('')
                    window['APT_ROOM_NAME'].update('')
                else:
                    sg.popup_error('❌ Room number already exists!', title='Error')
            else:
                sg.popup_error('❌ Please fill all fields!', title='Error')
        
        if event == '🔄 Refresh List':
            apts = get_apartments()
            apt_text = '  Room #  │    Room Name      │    Status\n' + '─'*55 + '\n'
            for apt in apts:
                apt_text += f"  {apt[0]:<7} │ {apt[1]:<17} │ {apt[2]}\n"
            window['APT_LIST'].update(apt_text if apts else "No apartments added yet.")
        
        # BOOKING TAB DATE PICKERS
        if event == 'BOOK_CHECKIN_BTN':
            date = sg.popup_get_date(title='📅 Select Check-in Date')
            if date:
                window['BOOK_CHECKIN'].update(f"{date[2]:04d}-{date[0]:02d}-{date[1]:02d}")
        
        if event == 'BOOK_CHECKOUT_BTN':
            date = sg.popup_get_date(title='📅 Select Check-out Date')
            if date:
                window['BOOK_CHECKOUT'].update(f"{date[2]:04d}-{date[0]:02d}-{date[1]:02d}")
        
        # BOOKING TAB EVENTS
        if event == '✅ Add Booking':
            try:
                room = values['BOOK_ROOM'].strip()
                guest = values['BOOK_GUEST'].strip()
                checkin = values['BOOK_CHECKIN'].strip()
                checkout = values['BOOK_CHECKOUT'].strip()
                price = float(values['BOOK_PRICE'].strip())
                
                if room and guest and checkin and checkout and price > 0:
                    add_booking(room, guest, checkin, checkout, price)
                    sg.popup_ok('✅ Booking added successfully!', title='Success')
                    window['BOOK_ROOM'].update('')
                    window['BOOK_GUEST'].update('')
                    window['BOOK_CHECKIN'].update('')
                    window['BOOK_CHECKOUT'].update('')
                    window['BOOK_PRICE'].update('')
                else:
                    sg.popup_error('❌ Please fill all fields with valid data!', title='Error')
            except:
                sg.popup_error('❌ Invalid price format!', title='Error')
        
        if event == '📋 View Bookings':
            bookings = get_bookings()
            if bookings:
                book_text = '  Room# │ Guest Name    │ Check-in   │ Check-out  │ Price\n' + '─'*60 + '\n'
                for book in bookings:
                    book_text += f"  {book[0]:<5} │ {book[1]:<13} │ {book[2]} │ {book[3]} │ ₹{book[4]}\n"
            else:
                book_text = "No bookings yet."
            window['BOOKING_LIST'].update(book_text)
        
        # DAILY CHARGES DATE PICKER
        if event == 'CHARGE_DATE_BTN':
            date = sg.popup_get_date(title='📅 Select Charge Date')
            if date:
                window['CHARGE_DATE'].update(f"{date[2]:04d}-{date[0]:02d}-{date[1]:02d}")
        
        # DAILY CHARGES TAB EVENTS
        if event == '➕ Add Charge':
            try:
                room = values['CHARGE_ROOM'].strip()
                desc = values['CHARGE_DESC'].strip()
                amount = float(values['CHARGE_AMOUNT'].strip())
                date = values['CHARGE_DATE'].strip() or datetime.now().strftime('%Y-%m-%d')
                
                if room and desc and amount > 0:
                    add_daily_charge(room, desc, amount, date)
                    sg.popup_ok('✅ Charge added successfully!', title='Success')
                    window['CHARGE_ROOM'].update('')
                    window['CHARGE_DESC'].update('')
                    window['CHARGE_AMOUNT'].update('')
                    window['CHARGE_DATE'].update('')
                else:
                    sg.popup_error('❌ Please fill all fields with valid data!', title='Error')
            except:
                sg.popup_error('❌ Invalid amount format!', title='Error')
        
        if event == '📊 View Charges':
            conn = sqlite3.connect('hotel_pos.db')
            c = conn.cursor()
            c.execute('SELECT room_number, charge_date, description, amount FROM daily_charges ORDER BY charge_date DESC LIMIT 50')
            charges = c.fetchall()
            conn.close()
            
            if charges:
                charge_text = '  Room# │ Date       │ Description    │ Amount\n' + '─'*60 + '\n'
                for charge in charges:
                    charge_text += f"  {charge[0]:<5} │ {charge[1]} │ {charge[2]:<14} │ ₹{charge[3]:.2f}\n"
            else:
                charge_text = "No charges recorded yet."
            window['CHARGE_LIST'].update(charge_text)
        
        # ANALYTICS MONTH DATE PICKER
        if event == 'REPORT_MONTH_BTN':
            date = sg.popup_get_date(title='📅 Select Month')
            if date:
                window['REPORT_MONTH'].update(f"{date[2]:04d}-{date[0]:02d}")
        
        # ANALYTICS TAB EVENTS
        if event == '📈 Generate Report':
            month = values['REPORT_MONTH'].strip()
            if month:
                summary = get_monthly_summary(month)
                
                report = f"\n{'═'*65}\n"
                report += f"  MONTHLY INCOME REPORT - {month}\n"
                report += f"{'═'*65}\n\n"
                
                report += f"  💼 BOOKING INCOME:          ₹ {summary['booking_total']:>10,.2f}\n"
                report += f"  💰 DAILY CHARGES INCOME:    ₹ {summary['daily_total']:>10,.2f}\n"
                report += f"  {'-'*65}\n"
                report += f"  📊 TOTAL INCOME:            ₹ {summary['total']:>10,.2f}\n"
                report += f"{'═'*65}\n\n"
                
                report += "  BREAKDOWN BY ROOM:\n"
                report += "  " + "-"*63 + "\n"
                report += "  Room# │ Booking Income │ Daily Income │ Total Income\n"
                report += "  " + "-"*63 + "\n"
                
                all_rooms = set()
                for room, amount in summary['room_bookings']:
                    all_rooms.add(room)
                for room, amount in summary['room_daily']:
                    all_rooms.add(room)
                
                total_booking = 0
                total_daily = 0
                for room in sorted(all_rooms):
                    booking = next((x[1] for x in summary['room_bookings'] if x[0] == room), 0)
                    daily = next((x[1] for x in summary['room_daily'] if x[0] == room), 0)
                    total = booking + daily
                    total_booking += booking
                    total_daily += daily
                    report += f"  {room:<5} │ ₹{booking:>13,.2f} │ ₹{daily:>10,.2f} │ ₹{total:>10,.2f}\n"
                
                report += "  " + "-"*63 + "\n"
                report += f"  TOTAL │ ₹{total_booking:>13,.2f} │ ₹{total_daily:>10,.2f} │ ₹{summary['total']:>10,.2f}\n"
                report += f"{'═'*65}\n"
                
                window['REPORT_DISPLAY'].update(report)
            else:
                sg.popup_error('❌ Please select a month!', title='Error')
    
    window.close()

if __name__ == '__main__':
    main()
