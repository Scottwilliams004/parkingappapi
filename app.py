from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database Connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),  # Default to localhost if not set
            user=os.environ.get('DB_USER'),  # Default to root if not set
            password=os.environ.get('DB_PASSWORD'),          # No default, ensure this is set in .env
            database=os.environ.get('DB_NAME')  # Default to ParkingAppdatabase if not set
        )
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

# Check Parking Spot Availability
@app.route('/check_availability', methods=['GET'])
def check_availability():
    carparkname = request.args.get('carparkname')
    carparkbay = request.args.get('carparkbay')

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        query = """
            SELECT baystatus FROM carpark 
            WHERE carparkname = %s AND carparkbay = %s
        """
        cursor.execute(query, (carparkname, carparkbay))
        baystatus = cursor.fetchone()
        while cursor.nextset():  # Ensure all results are read
            pass
        cursor.close()
        connection.close()
        if baystatus is not None:
            is_available = baystatus[0] == 0
            return jsonify({"is_available": is_available})
        else:
            return jsonify({"error": "Parking spot not found"}), 404
    else:
        return jsonify({"error": "Database connection failed"}), 500

# Make a Reservation
@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    carparkname = request.json['carparkname']
    carparkbay = request.json['carparkbay']

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()

        # Check availability first
        cursor.execute("""
            SELECT baystatus FROM carpark 
            WHERE carparkname = %s AND carparkbay = %s
        """, (carparkname, carparkbay))
        baystatus = cursor.fetchone()
        while cursor.nextset():  # Ensure all results are read
            pass
        if baystatus is None or baystatus[0] != 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "Spot not available"}), 409

        # Update the spot status to Reserved
        cursor.execute("""
            UPDATE carpark SET baystatus = 1 
            WHERE carparkname = %s AND carparkbay = %s
        """, (carparkname, carparkbay))
        connection.commit()

        cursor.close()
        connection.close()
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Database connection failed"}), 500

# Add a New Parking Spot via GET (not recommended for production use)
@app.route('/add_parking_spot', methods=['GET'])
def add_parking_spot():
    carparkname = request.args.get('carparkname')
    carparkbay = request.args.get('carparkbay')
    location_x = request.args.get('location_x')
    location_y = request.args.get('location_y')
    baystatus = request.args.get('baystatus')

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()

        # Convert 'null' string to actual NULL value
        location_x = None if location_x == 'null' else location_x
        location_y = None if location_y == 'null' else location_y

        # Insert the new parking spot
        cursor.execute("""
            INSERT INTO carpark (carparkname, carparkbay, location_x, location_y, baystatus) 
            VALUES (%s, %s, %s, %s, %s)
        """, (carparkname, carparkbay, location_x, location_y, baystatus))
        connection.commit()

        cursor.close()
        connection.close()
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Database connection failed"}), 500

# New route for the root URL
@app.route('/')
def index():
    return "Welcome to ParkPal Backend"

if __name__ == '__main__':
    app.run(debug=True)
