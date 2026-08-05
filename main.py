import PySimpleGUI as sg
import sqlite3
from datetime import datetime
import os

# Set theme
sg.theme('DarkBlue3')

# Initialize database
def init_db():
    if not os.path.exists('hotel_pos.db'):
        conn = sqlite3.connect('hotel_pos.db')
        c = conn.cursor()
        
        # Guests table
        c.execute('''CREATE TABLE guests (
            id INTEGER PRIMARY KEY,
            room_number TEXT UNIQUE,
            name TEXT,
            created_at TIMESTAMP
        )''')
        
        # Menu items table
        c.execute('''CREATE TABLE menu_items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL
        )''')
        
        # Orders table
        c.execute('''CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            room_number TEXT,
            item_name TEXT,
            quantity INTEGER,
            price REAL,
            total REAL,
            order_date TIMESTAMP
        )''')
        
        # Insert sample menu
        menu = [
            ('Coffee', 'Beverages', 2.50),
            ('Tea', 'Beverages', 2.00),
            ('Breakfast', 'Food', 8.00),
            ('Lunch', 'Food', 12.00),
            ('Snacks', 'Food', 5.00),
        ]
        c.executemany('INSERT INTO menu_items (name, category, price) VALUES (?, ?, ?)', menu)
        
        conn.commit()
        conn.close()

# Get menu items
def get_menu_items():
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    c.execute('SELECT name, price, category FROM menu_items ORDER BY category')
    items = c.fetchall()
    conn.close()
    return items

# Add order to database
def add_order(room_number, item_name, quantity, price):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    total = quantity * price
    c.execute('INSERT INTO orders (room_number, item_name, quantity, price, total, order_date) VALUES (?, ?, ?, ?, ?, ?)',
              (room_number, item_name, quantity, price, total, datetime.now()))
    conn.commit()
    conn.close()

# Get orders for a room
def get_room_bill(room_number):
    conn = sqlite3.connect('hotel_pos.db')
    c = conn.cursor()
    c.execute('SELECT item_name, quantity, total FROM orders WHERE room_number = ?', (room_number,))
    orders = c.fetchall()
    conn.close()
    return orders

# Main window
def main():
    init_db()
    menu_items = get_menu_items()
    
    # Layout
    layout = [
        [sg.Text('🏨 HOTEL POS SYSTEM', font=('Arial', 16, 'bold'))],
        [sg.Separator()],
        
        # Room Input
        [sg.Text('Room Number:', font=('Arial', 10)), 
         sg.InputText(size=(15,), key='ROOM_NUM')],
        
        [sg.Separator()],
        
        # Menu Selection
        [sg.Text('Select Item:', font=('Arial', 10))],
        [sg.Combo([item[0] for item in menu_items], key='ITEM_SELECT', size=(20,))],
        [sg.Text('Quantity:', font=('Arial', 10)), 
         sg.InputText('1', size=(5,), key='QUANTITY')],
        
        [sg.Button('Add to Bill', size=(15,)), sg.Button('Clear Bill', size=(15,))],
        
        [sg.Separator()],
        
        # Bill Display
        [sg.Text('Current Bill:', font=('Arial', 10, 'bold'))],
        [sg.Multiline(size=(40, 12), key='BILL_DISPLAY', disabled=True)],
        
        [sg.Separator()],
        
        # Total & Payment
        [sg.Text('Total:', font=('Arial', 12, 'bold')), 
         sg.Text('0.00', font=('Arial', 12, 'bold'), key='TOTAL')],
        
        [sg.Button('Print Bill', size=(15,)), 
         sg.Button('Process Payment', size=(15,)), 
         sg.Button('Exit', size=(15,))],
    ]
    
    window = sg.Window('Hotel POS', layout)
    bill_items = []
    
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        
        room_num = values['ROOM_NUM'].strip()
        
        if event == 'Add to Bill':
            if not room_num:
                sg.popup_error('Enter Room Number!')
                continue
            if not values['ITEM_SELECT']:
                sg.popup_error('Select an Item!')
                continue
            
            item_name = values['ITEM_SELECT']
            quantity = int(values['QUANTITY']) if values['QUANTITY'].isdigit() else 1
            
            # Get price
            price = next((item[1] for item in menu_items if item[0] == item_name), 0)
            
            add_order(room_num, item_name, quantity, price)
            bill_items.append((item_name, quantity, quantity * price))
            
            # Update bill display
            bill_text = f"Room: {room_num}\n{'-'*35}\n"
            total = 0
            for item, qty, subtotal in bill_items:
                bill_text += f"{item:<20} {qty:>3} x ${subtotal/qty:>6.2f} = ${subtotal:>7.2f}\n"
                total += subtotal
            
            window['BILL_DISPLAY'].update(bill_text)
            window['TOTAL'].update(f'{total:.2f}')
        
        elif event == 'Clear Bill':
            bill_items = []
            window['BILL_DISPLAY'].update('')
            window['TOTAL'].update('0.00')
        
        elif event == 'Print Bill':
            if not bill_items:
                sg.popup_error('Bill is empty!')
            else:
                sg.popup('Bill printed!', 'Receipt sent to printer')
        
        elif event == 'Process Payment':
            if not bill_items:
                sg.popup_error('Bill is empty!')
            else:
                total = sum(item[2] for item in bill_items)
                sg.popup(f'Payment Processed\n\nRoom: {room_num}\nTotal: ${total:.2f}')
                bill_items = []
                window['BILL_DISPLAY'].update('')
                window['TOTAL'].update('0.00')
    
    window.close()

if __name__ == '__main__':
    main()
