"""
Flight Management System CLI
Module: CM500292 - Databases Coursework
"""

import sqlite3
from datetime import datetime

DB_NAME = "FlightManagement.db"


def get_db_connection():
    """Establishes connection and enables SQLite foreign key constraint checks."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Creates tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Destinations (
            destination_code TEXT PRIMARY KEY,
            airport_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Pilots (
            pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            licence_number TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'On Leave', 'Suspended'))
        );

        CREATE TABLE IF NOT EXISTS Flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT UNIQUE NOT NULL,
            departure_airport TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            departure_datetime TEXT NOT NULL,
            arrival_datetime TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled' CHECK(status IN ('Scheduled', 'Boarding', 'Delayed', 'Departed', 'Completed', 'Cancelled')),
            FOREIGN KEY (destination_code) REFERENCES Destinations(destination_code) ON DELETE RESTRICT ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS FlightAssignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id INTEGER NOT NULL,
            pilot_id INTEGER NOT NULL,
            role TEXT NOT NULL DEFAULT 'Captain' CHECK(role IN ('Captain', 'First Officer')),
            assigned_date TEXT NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES Flights(flight_id) ON DELETE CASCADE,
            FOREIGN KEY (pilot_id) REFERENCES Pilots(pilot_id) ON DELETE RESTRICT,
            UNIQUE(flight_id, pilot_id)
        );
        """)
        conn.commit()


def seed_database():
    """Populates tables with 10-15 test records each if empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Destinations")
        if cursor.fetchone()[0] > 0:
            return  # Data already exists

        # 10 Destinations
        destinations = [
            ("LHR", "Heathrow Airport", "London", "United Kingdom"),
            ("JFK", "John F. Kennedy International", "New York", "United States"),
            ("CDG", "Charles de Gaulle Airport", "Paris", "France"),
            ("AMS", "Amsterdam Airport Schiphol", "Amsterdam", "Netherlands"),
            ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
            ("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates"),
            ("HND", "Tokyo Haneda Airport", "Tokyo", "Japan"),
            ("SIN", "Singapore Changi Airport", "Singapore", "Singapore"),
            ("MAD", "Adolfo Suarez Madrid-Barajas", "Madrid", "Spain"),
            ("DUB", "Dublin Airport", "Dublin", "Ireland")
        ]
        cursor.executemany("INSERT INTO Destinations VALUES (?, ?, ?, ?)", destinations)

        # 10 Pilots
        pilots = [
            ("Sarah Jenkins", "ATPL-9021", "+44 7700 900123", "Active"),
            ("David Miller", "ATPL-3312", "+44 7700 900456", "Active"),
            ("Elena Vance", "ATPL-7741", "+44 7700 900789", "Active"),
            ("Marcus Holloway", "ATPL-8820", "+44 7700 900321", "Active"),
            ("Chloe Price", "ATPL-1194", "+44 7700 900654", "On Leave"),
            ("Arthur Morgan", "ATPL-5542", "+44 7700 900987", "Active"),
            ("Amara Khan", "ATPL-6631", "+44 7700 900112", "Active"),
            ("Lucas Gray", "ATPL-4429", "+44 7700 900223", "Active"),
            ("Hannah Abbott", "ATPL-1102", "+44 7700 900334", "Active"),
            ("Leon Kennedy", "ATPL-8890", "+44 7700 900445", "Active")
        ]
        cursor.executemany("INSERT INTO Pilots (full_name, licence_number, phone, status) VALUES (?, ?, ?, ?)", pilots)

        # 10 Flights
        flights = [
            ("FL-101", "BHX", "AMS", "2026-11-01 07:30", "2026-11-01 09:45", "Scheduled"),
            ("FL-102", "BHX", "CDG", "2026-11-01 08:15", "2026-11-01 10:30", "Scheduled"),
            ("FL-103", "LHR", "JFK", "2026-11-01 10:00", "2026-11-01 13:30", "Delayed"),
            ("FL-104", "BHX", "DUB", "2026-11-01 11:20", "2026-11-01 12:25", "Scheduled"),
            ("FL-105", "LHR", "DXB", "2026-11-02 13:45", "2026-11-02 23:55", "Scheduled"),
            ("FL-106", "BHX", "FRA", "2026-11-02 14:00", "2026-11-02 16:40", "Scheduled"),
            ("FL-107", "LHR", "HND", "2026-11-03 09:10", "2026-11-04 07:45", "Scheduled"),
            ("FL-108", "LHR", "SIN", "2026-11-03 18:30", "2026-11-04 15:15", "Scheduled"),
            ("FL-109", "BHX", "MAD", "2026-11-04 06:15", "2026-11-04 09:45", "Scheduled"),
            ("FL-110", "LHR", "JFK", "2026-11-04 16:00", "2026-11-04 19:30", "Scheduled")
        ]
        cursor.executemany("INSERT INTO Flights (flight_number, departure_airport, destination_code, departure_datetime, arrival_datetime, status) VALUES (?, ?, ?, ?, ?, ?)", flights)

        # 10 Assignments
        assignments = [
            (1, 1, "Captain", "2026-10-15"),
            (1, 2, "First Officer", "2026-10-15"),
            (2, 3, "Captain", "2026-10-15"),
            (3, 4, "Captain", "2026-10-16"),
            (3, 6, "First Officer", "2026-10-16"),
            (4, 7, "Captain", "2026-10-16"),
            (5, 8, "Captain", "2026-10-17"),
            (6, 9, "Captain", "2026-10-17"),
            (7, 10, "Captain", "2026-10-18"),
            (8, 1, "Captain", "2026-10-18")
        ]
        cursor.executemany("INSERT INTO FlightAssignments (flight_id, pilot_id, role, assigned_date) VALUES (?, ?, ?, ?)", assignments)
        conn.commit()


# --- CLI Functionalities ---

def add_new_flight():
    """Inserts a new flight record."""
    print("\n[Add New Flight]")
    flight_number = input("Flight Number (e.g., FL-301): ").strip().upper()
    departure_airport = input("Departure Airport Code (e.g., BHX): ").strip().upper()
    destination_code = input("Destination Airport Code (e.g., AMS): ").strip().upper()
    dep_time = input("Departure Time (YYYY-MM-DD HH:MM): ").strip()
    arr_time = input("Arrival Time (YYYY-MM-DD HH:MM): ").strip()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Flights (flight_number, departure_airport, destination_code, departure_datetime, arrival_datetime)
                VALUES (?, ?, ?, ?, ?)
            """, (flight_number, departure_airport, destination_code, dep_time, arr_time))
            conn.commit()
            print(f"Success: Flight '{flight_number}' added with ID {cursor.lastrowid}.")
    except sqlite3.IntegrityError as e:
        print(f"Error adding flight: {e}")


def view_flights_by_criteria():
    """Retrieves flights based on criteria (Destination, Status, or All)."""
    print("\n[View Flights]")
    print("1. Filter by Destination")
    print("2. Filter by Flight Status")
    print("3. View All Flights")
    choice = input("Select an option (1-3): ").strip()

    query = """
        SELECT f.flight_id, f.flight_number, f.departure_airport, f.destination_code, 
               d.city, f.departure_datetime, f.arrival_datetime, f.status
        FROM Flights f
        JOIN Destinations d ON f.destination_code = d.destination_code
    """
    params = ()

    if choice == "1":
        dest = input("Enter Destination Code (e.g. AMS): ").strip().upper()
        query += " WHERE f.destination_code = ?"
        params = (dest,)
    elif choice == "2":
        status = input("Enter Status (Scheduled, Delayed, Completed, Cancelled): ").strip()
        query += " WHERE f.status = ?"
        params = (status,)
    elif choice != "3":
        print("Invalid choice.")
        return

    query += " ORDER BY f.departure_datetime ASC"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            print("No matching flights found.")
            return

        print(f"\n{'ID':<4} {'Flight':<10} {'Route':<12} {'Destination City':<18} {'Departure Time':<18} {'Status':<10}")
        print("-" * 75)
        for r in rows:
            route = f"{r['departure_airport']} -> {r['destination_code']}"
            print(f"{r['flight_id']:<4} {r['flight_number']:<10} {route:<12} {r['city']:<18} {r['departure_datetime']:<18} {r['status']:<10}")


def update_flight_information():
    """Modifies departure time or status of an existing flight."""
    print("\n[Update Flight Information]")
    flight_id = input("Enter Flight ID to update: ").strip()
    new_time = input("New Departure Datetime (YYYY-MM-DD HH:MM) [Press Enter to keep unchanged]: ").strip()
    new_status = input("New Status (Scheduled, Delayed, Completed, Cancelled) [Press Enter to keep unchanged]: ").strip()

    updates = []
    params = []
    if new_time:
        updates.append("departure_datetime = ?")
        params.append(new_time)
    if new_status:
        updates.append("status = ?")
        params.append(new_status)

    if not updates:
        print("No changes provided.")
        return

    params.append(flight_id)
    sql = f"UPDATE Flights SET {', '.join(updates)} WHERE flight_id = ?"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Flight ID {flight_id} updated successfully.")
        else:
            print("Flight ID not found.")


def assign_pilot_to_flight():
    """Assigns a pilot to a flight in the bridge table."""
    print("\n[Assign Pilot to Flight]")
    flight_id = input("Enter Flight ID: ").strip()
    pilot_id = input("Enter Pilot ID: ").strip()
    role = input("Enter Role (Captain / First Officer) [Default: Captain]: ").strip() or "Captain"
    assigned_date = datetime.now().strftime("%Y-%m-%d")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO FlightAssignments (flight_id, pilot_id, role, assigned_date)
                VALUES (?, ?, ?, ?)
            """, (flight_id, pilot_id, role, assigned_date))
            conn.commit()
            print("Pilot successfully assigned to flight.")
    except sqlite3.IntegrityError as e:
        print(f"Assignment failed: {e}")


def view_pilot_schedule():
    """Queries flight assignments for a specific pilot."""
    print("\n[View Pilot Schedule]")
    pilot_id = input("Enter Pilot ID: ").strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.full_name, f.flight_number, f.departure_airport, f.destination_code,
                   f.departure_datetime, fa.role
            FROM FlightAssignments fa
            JOIN Pilots p ON fa.pilot_id = p.pilot_id
            JOIN Flights f ON fa.flight_id = f.flight_id
            WHERE p.pilot_id = ?
            ORDER BY f.departure_datetime ASC
        """, (pilot_id,))
        rows = cursor.fetchall()

        if not rows:
            print(f"No assignments found for Pilot ID {pilot_id}.")
            return

        print(f"\nRoster for: {rows[0]['full_name']}")
        print(f"{'Flight':<10} {'Route':<12} {'Departure Time':<18} {'Role':<15}")
        print("-" * 55)
        for r in rows:
            route = f"{r['departure_airport']} -> {r['destination_code']}"
            print(f"{r['flight_number']:<10} {route:<12} {r['departure_datetime']:<18} {r['role']:<15}")


def destination_management():
    """View destinations or register a new one."""
    print("\n[Destination Management]")
    print("1. View All Destinations")
    print("2. Add New Destination")
    choice = input("Select an option (1-2): ").strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        if choice == "1":
            cursor.execute("SELECT destination_code, airport_name, city, country FROM Destinations ORDER BY destination_code ASC")
            rows = cursor.fetchall()
            print(f"\n{'Code':<6} {'Airport Name':<32} {'City':<16} {'Country':<16}")
            print("-" * 75)
            for r in rows:
                print(f"{r['destination_code']:<6} {r['airport_name']:<32} {r['city']:<16} {r['country']:<16}")
        elif choice == "2":
            code = input("IATA Code (3 chars): ").strip().upper()
            name = input("Airport Name: ").strip()
            city = input("City: ").strip()
            country = input("Country: ").strip()
            try:
                cursor.execute("INSERT INTO Destinations VALUES (?, ?, ?, ?)", (code, name, city, country))
                conn.commit()
                print(f"Destination '{code}' successfully created.")
            except sqlite3.IntegrityError as e:
                print(f"Error adding destination: {e}")


def summary_reports():
    """Executes aggregate queries for business insight."""
    print("\n[Summary & Analytics Reports]")
    print("1. Total Flights by Destination")
    print("2. Total Flights Assigned per Pilot")
    choice = input("Select an option (1-2): ").strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        if choice == "1":
            cursor.execute("""
                SELECT d.destination_code, d.city, COUNT(f.flight_id) AS flight_count
                FROM Destinations d
                LEFT JOIN Flights f ON d.destination_code = f.destination_code
                GROUP BY d.destination_code, d.city
                ORDER BY flight_count DESC
            """)
            rows = cursor.fetchall()
            print(f"\n{'Code':<6} {'City':<16} {'Flight Count':<12}")
            print("-" * 38)
            for r in rows:
                print(f"{r['destination_code']:<6} {r['city']:<16} {r['flight_count']:<12}")
        elif choice == "2":
            cursor.execute("""
                SELECT p.pilot_id, p.full_name, COUNT(fa.flight_id) AS total_assignments
                FROM Pilots p
                LEFT JOIN FlightAssignments fa ON p.pilot_id = fa.pilot_id
                GROUP BY p.pilot_id, p.full_name
                ORDER BY total_assignments DESC
            """)
            rows = cursor.fetchall()
            print(f"\n{'ID':<4} {'Pilot Name':<20} {'Assignments':<12}")
            print("-" * 40)
            for r in rows:
                print(f"{r['pilot_id']:<4} {r['full_name']:<20} {r['total_assignments']:<12}")


def main():
    initialize_database()
    seed_database()

    while True:
        print("\n==========================================")
        print("      FLIGHT MANAGEMENT SYSTEM (CLI)     ")
        print("==========================================")
        print("1. Add a New Flight")
        print("2. View Flights by Criteria")
        print("3. Update Flight Information")
        print("4. Assign Pilot to Flight")
        print("5. View Pilot Schedule")
        print("6. View/Update Destination Information")
        print("7. Summary & Analytics Reports")
        print("8. Exit")

        choice = input("\nSelect an option (1-8): ").strip()
        if choice == "1":
            add_new_flight()
        elif choice == "2":
            view_flights_by_criteria()
        elif choice == "3":
            update_flight_information()
        elif choice == "4":
            assign_pilot_to_flight()
        elif choice == "5":
            view_pilot_schedule()
        elif choice == "6":
            destination_management()
        elif choice == "7":
            summary_reports()
        elif choice == "8":
            print("Exiting application.")
            break
        else:
            print("Invalid selection. Please choose an option between 1 and 8.")


if __name__ == "__main__":
    main()