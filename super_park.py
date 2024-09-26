import sqlite3
import time
import os

price = 0
tickets = 0
cart = {'tickets': 0, 'total_price': 0, 'membership_upgrade': False}
balance = 0
membership_type = None
username = None
bookings = []

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_database():
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT,
                        membership TEXT,
                        balance REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        username TEXT,
                        tickets INTEGER,
                        date TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('user1', 'pass1', 'basic', 100.0)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('user2', 'pass2', 'premium', 200.0)")
    conn.commit()
    conn.close()

def login():
    global membership_type, username, balance
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()

    username = input("\nUsername: ").strip()
    time.sleep(0.5)
    password = input("Password: ").strip()
    time.sleep(0.5)

    cursor.execute("SELECT membership, balance FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        membership_type = user[0]
        balance = user[1]
        print(f"\nLogged in as {membership_type} member.\n")
        time.sleep(1)
        show_menu()
    else:
        print("\nWrong credentials. Try again.\n")
        time.sleep(1)
        login()

    conn.close()

def create_account():
    global username, balance
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()

    print("\nCreating a new account...\n")
    time.sleep(0.5)
    username = input("New username: ").strip()
    password = input("New password: ").strip()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("\nUsername taken. Try again.\n")
        time.sleep(1)
        create_account()
        return

    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, password, 'basic', 0.0))
    conn.commit()
    print(f"\nAccount created. You are a basic member.\n")
    time.sleep(1)
    membership_type = 'basic'
    balance = 0
    conn.close()
    show_menu()

def show_menu():
    clear_terminal()
    time.sleep(0.5)

    print(f"\n{'*' * 50}")
    print("HOME".center(50))
    print(f"{'*' * 50}")
    print(f"User: {username} | Membership: {membership_type} | Balance: £{balance:.2f}")
    print(f"Cart: {cart['tickets']} items | Total: £{cart['total_price']:.2f}")
    print(f"{'*' * 50}\n")

    print("1. Book Tickets")
    print("2. Manage Membership")
    print("3. Manage Balance")
    print(f"4. View Cart ({cart['tickets']} items)")
    print("5. Account Settings\n")

    option = input("Choose an option (1-5): ").strip()

    if option == '1':
        ticket_menu()
    elif option == '2':
        manage_membership()
    elif option == '3':
        manage_balance()
    elif option == '4':
        view_cart()
    elif option == '5':
        account_settings()
    else:
        print("\nInvalid option. Try again.\n")
        time.sleep(0.5)
        show_menu()

def ticket_menu():
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("BOOK TICKETS".center(50))
    print(f"{'*' * 50}\n")
    
    print("1. Add Tickets")
    print("2. Booking Info")
    print("3. View Active Bookings")
    print("4. Back\n")
    
    option = input("Choose an option (1-4): ").strip()

    if option == '1':
        add_ticket()
    elif option == '2':
        booking_info()
    elif option == '3':
        view_bookings()
    elif option == '4':
        show_menu()
    else:
        print("\nInvalid option. Try again.\n")
        time.sleep(0.5)
        ticket_menu()

def booking_info():
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("BOOKING INFO".center(50))
    print(f"{'*' * 50}\n")

    info = (
        "Ticket purchases are available for users aged 6 to 100. All users "
        "must be physically fit to participate in park activities. Please consult "
        "with a physician if you have any underlying health conditions. Super Park is "
        "not liable for any accidents that occur during your visit. Enjoy responsibly!"
    )
    print(info)

    input("\nPress Enter to go back...")
    ticket_menu()

def view_bookings():
    global bookings
    clear_terminal()

    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tickets, date FROM bookings WHERE username = ?", (username,))
    bookings = cursor.fetchall()

    print(f"\n{'*' * 50}")
    print("ACTIVE BOOKINGS".center(50))
    print(f"{'*' * 50}\n")

    if bookings:
        for idx, booking in enumerate(bookings):
            print(f"{idx + 1}. Tickets: {booking[0]}, Date: {booking[1]}")
        print("\nChoose a booking to cancel or press 0 to go back.")
        choice = input("Enter number: ").strip()

        if choice.isdigit() and 0 <= int(choice) <= len(bookings):
            if int(choice) == 0:
                ticket_menu()
            else:
                cancel_booking(int(choice) - 1)
        else:
            print("\nInvalid option. Try again.\n")
            time.sleep(1)
            view_bookings()
    else:
        print("\nNo active bookings.\n")
        input("\nPress Enter to go back...")
        ticket_menu()

def cancel_booking(index):
    global bookings
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    booking = bookings[index]
    cursor.execute("DELETE FROM bookings WHERE username = ? AND date = ?", (username, booking[1]))
    conn.commit()
    conn.close()
    print(f"\nBooking on {booking[1]} canceled.\n")
    bookings.pop(index)
    time.sleep(1)
    view_bookings()

def add_ticket():
    global tickets, price, cart
    clear_terminal()
    while True:
        print("\n1. Add a Ticket")
        print("2. View Cart")
        print("3. Cancel\n")
        add_ticket_input = input("Choose an option (1-3): ").strip()

        if add_ticket_input == "1":
            tickets += 1
            determine_age_group()
            choose_booking_date()
            print(f"\nTotal tickets: {tickets}")
            print(f"Total ticket price so far: £{price:.2f}\n")
        elif add_ticket_input == "2":
            cart['tickets'] = tickets
            cart['total_price'] = price
            print("\nTickets added to cart.\n")
            time.sleep(1)
            show_menu()
        elif add_ticket_input == "3":
            tickets = 0
            price = 0
            print("\nTickets canceled.\n")
            time.sleep(1)
            show_menu()
        else:
            print("\nInvalid option.\n")
            time.sleep(0.5)

def choose_booking_date():
    global bookings
    day = input("\nEnter the day (1-31): ").strip()
    month = input("Enter the month (1-12): ").strip()
    year = input("Enter the year: ").strip()

    booking_date = f"{day}/{month}/{year}"
    bookings.append({'tickets': tickets, 'date': booking_date})

    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings VALUES (?, ?, ?)", (username, tickets, booking_date))
    conn.commit()
    conn.close()

    print(f"\nBooking for {booking_date} added.\n")
    time.sleep(1)

def determine_age_group():
    global price
    try:
        age = int(input("Enter your age: "))
    except ValueError:
        print("\nInvalid age. Please enter a valid number.\n")
        time.sleep(0.5)
        determine_age_group()
        return

    if age < 6:
        print("\nYou must be over 6 years old to purchase a ticket.\n")
        time.sleep(1)
    elif 6 <= age <= 12:
        price += 10
        print("Child ticket for £10 added.\n")
    elif 13 <= age <= 60:
        price += 20
        print("Adult ticket for £20 added.\n")
    elif age > 60:
        price += 5
        print("Senior ticket for £5 added.\n")
    time.sleep(1)

def manage_membership():
    global cart, membership_type, balance
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("MANAGE MEMBERSHIP".center(50))
    print(f"{'*' * 50}\nCurrent Membership: {membership_type}\n")
    
    if membership_type == 'basic':
        upgrade_option = input("Upgrade to premium for £50? (1: yes, 2: no): ").strip()
        if upgrade_option == '1':
            cart['membership_upgrade'] = True
            print("\nPremium membership added to your cart.\n")
            time.sleep(1)
        else:
            print("\nNo changes made to membership.\n")
            time.sleep(1)
    elif membership_type == 'premium':
        downgrade_option = input("Downgrade to basic membership? (1: yes, 2: no): ").strip()
        if downgrade_option == '1':
            cart['membership_upgrade'] = False
            refund = 50 * 0.25
            balance += refund
            update_balance_in_db()
            print(f"\nYou will be downgraded to basic membership. £{refund:.2f} refunded.\n")
            time.sleep(1)
        else:
            print("\nNo changes made to membership.\n")
            time.sleep(1)
    show_menu()

def manage_balance():
    global balance
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("MANAGE BALANCE".center(50))
    print(f"{'*' * 50}\nCurrent balance: £{balance:.2f}\n")

    print("1. Add money to balance")
    print("2. Withdraw money from balance")
    print("3. Back\n")
    option = input("Choose an option (1-3): ").strip()

    if option == '1':
        add_money()
    elif option == '2':
        withdraw_money()
    elif option == '3':
        show_menu()
    else:
        print("\nInvalid option. Try again.\n")
        time.sleep(0.5)
        manage_balance()

def add_money():
    global balance
    try:
        add_balance = float(input("Enter amount to add: "))
        balance += add_balance
        print(f"\n£{add_balance:.2f} has been added to your balance.\n")
        update_balance_in_db()
    except ValueError:
        print("\nInvalid amount. Try again.\n")
    time.sleep(1)
    manage_balance()

def withdraw_money():
    global balance
    try:
        withdraw_balance = float(input("Enter amount to withdraw: "))
        if withdraw_balance > balance:
            print("\nInsufficient balance to withdraw this amount.\n")
        else:
            balance -= withdraw_balance
            print(f"\n£{withdraw_balance:.2f} has been withdrawn from your balance.\n")
            update_balance_in_db()
    except ValueError:
        print("\nInvalid amount. Try again.\n")
    time.sleep(1)
    manage_balance()

def view_cart():
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("YOUR CART".center(50))
    print(f"{'*' * 50}\nUser: {username} | Membership: {membership_type} | Balance: £{balance:.2f}\n")
    print(f"Tickets: {cart['tickets']}")
    print(f"Total ticket price: £{cart['total_price']:.2f}")
    if cart['membership_upgrade']:
        print("Premium membership upgrade: £50.00")
    print(f"Cart total: £{cart['total_price'] + (50 if cart['membership_upgrade'] else 0):.2f}\n")

    if cart['tickets'] == 0 and not cart['membership_upgrade']:
        print("\nYour cart is empty. Please add items before proceeding to checkout.\n")
        time.sleep(1)
        show_menu()
        return

    checkout_option = input("Proceed to checkout? (1: yes, 2: no): ").strip()
    if checkout_option == '1':
        checkout()

def checkout():
    global price, tickets, membership_type, balance, cart
    clear_terminal()
    total_cost = cart['total_price'] + (50 if cart['membership_upgrade'] else 0)

    if balance >= total_cost:
        balance -= total_cost
        update_balance_in_db()

        if cart['membership_upgrade']:
            membership_type = 'premium'
            update_membership_in_db()

        print(f"\nPayment successful! £{total_cost:.2f} has been deducted from your balance.\n")
        print(f"Remaining balance: £{balance:.2f}")
        cart = {'tickets': 0, 'total_price': 0, 'membership_upgrade': False}
        tickets = 0
        price = 0
        time.sleep(2)
        show_menu()  # Go back to home after checkout
    else:
        print(f"\nInsufficient balance! You need £{total_cost - balance:.2f} more to complete this purchase.\n")
        time.sleep(2)
        show_menu()  # Go back to home after failed checkout

def update_balance_in_db():
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (balance, username))
    conn.commit()
    conn.close()

def update_membership_in_db():
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET membership = ? WHERE username = ?", (membership_type, username))
    conn.commit()
    conn.close()

def account_settings():
    clear_terminal()
    print(f"\n{'*' * 50}")
    print("ACCOUNT SETTINGS".center(50))
    print(f"{'*' * 50}\nUser: {username} | Membership: {membership_type}\n")

    print("1. Change Username")
    print("2. Change Password")
    print("3. Switch Account")
    print("4. Logout")
    print("5. Back\n")
    
    option = input("Choose an option (1-5): ").strip()

    if option == '1':
        change_username()
    elif option == '2':
        change_password()
    elif option == '3':
        switch_account()
    elif option == '4':
        logout()
    elif option == '5':
        show_menu()
    else:
        print("\nInvalid option. Try again.\n")
        time.sleep(0.5)
        account_settings()

def change_username():
    global username
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()

    new_username = input("Enter new username: ").strip()
    cursor.execute("SELECT * FROM users WHERE username = ?", (new_username,))
    if cursor.fetchone():
        print("\nUsername already taken. Try again.\n")
    else:
        cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, username))
        conn.commit()
        username = new_username
        print(f"\nUsername changed successfully to {username}.\n")

    conn.close()
    time.sleep(1)
    show_menu()

def change_password():
    conn = sqlite3.connect('super_park.db')
    cursor = conn.cursor()

    new_password = input("Enter new password: ").strip()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()

    print("\nPassword changed successfully.\n")
    conn.close()
    time.sleep(1)
    show_menu()

def switch_account():
    print("\nSwitching account...\n")
    time.sleep(1)
    main()

def logout():
    print("\nYou have successfully logged out. Goodbye!\n")
    time.sleep(1)
    exit()

def main():
    setup_database()
    print("\nWELCOME TO SUPER PARK\n")
    time.sleep(1)

    choice = input("Log in (1) or Create account (2): ").strip()
    if choice == '1':
        login()
    elif choice == '2':
        create_account()
    else:
        print("\nInvalid option.\n")
        time.sleep(0.5)
        main()

main()