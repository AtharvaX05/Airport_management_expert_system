# =============================================
# FILE: app.py (DIAGNOSTIC VERSION)
# =============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import db_config
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database connections
print("🔌 Establishing database connections...")
try:
    chatbot_conn = db_config.get_chatbot_connection()
    chatbot_cursor = chatbot_conn.cursor(dictionary=True)
    print("✅ Chatbot DB connected")
except Exception as e:
    print(f"❌ Chatbot DB connection failed: {e}")
    chatbot_conn = None
    chatbot_cursor = None

try:
    airline_conn = db_config.get_airline_connection()
    airline_cursor = airline_conn.cursor(dictionary=True)
    print("✅ Airline DB connected")
except Exception as e:
    print(f"❌ Airline DB connection failed: {e}")
    airline_conn = None
    airline_cursor = None

# Simple in-memory context storage
user_contexts = {}


# ======================
# ✅ TEST DATABASE CONNECTION
# ======================

def test_database_connection():
    """Test if we can actually query the database."""
    print("\n" + "="*60)
    print("🧪 TESTING DATABASE CONNECTION")
    print("="*60)
    
    if not airline_cursor:
        print("❌ Airline cursor is None!")
        return False
    
    try:
        # Test 1: Simple query
        print("\n📝 Test 1: SELECT 1")
        airline_cursor.execute("SELECT 1 as test")
        result = airline_cursor.fetchone()
        print(f"   Result: {result}")
        
        # Test 2: Count aircraft
        print("\n📝 Test 2: COUNT(*) FROM Aircraft")
        airline_cursor.execute("SELECT COUNT(*) as count FROM Aircraft")
        result = airline_cursor.fetchone()
        print(f"   Total aircraft: {result}")
        
        # Test 3: Get first aircraft
        print("\n📝 Test 3: SELECT * FROM Aircraft LIMIT 1")
        airline_cursor.execute("SELECT * FROM Aircraft LIMIT 1")
        result = airline_cursor.fetchone()
        print(f"   First aircraft: {result}")
        
        # Test 4: Search for specific model
        print("\n📝 Test 4: Search for 'Airbus A320'")
        airline_cursor.execute("SELECT * FROM Aircraft WHERE Model = 'Airbus A320' LIMIT 1")
        result = airline_cursor.fetchone()
        print(f"   Result: {result}")
        
        # Test 5: Search with UPPER
        print("\n📝 Test 5: Search with UPPER")
        airline_cursor.execute("SELECT * FROM Aircraft WHERE UPPER(Model) = UPPER('Airbus A320') LIMIT 1")
        result = airline_cursor.fetchone()
        print(f"   Result: {result}")
        
        # Test 6: Show all models
        print("\n📝 Test 6: List all aircraft models")
        airline_cursor.execute("SELECT Model FROM Aircraft LIMIT 10")
        results = airline_cursor.fetchall()
        print("   Available models:")
        for r in results:
            print(f"      - '{r['Model']}'")
        
        print("\n✅ All database tests passed!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return False


# Run test on startup
test_database_connection()


# ======================
# Parser Functions
# ======================

def extract_flight_number(text):
    """Extract flight number like AA101, BA456, etc."""
    match = re.search(r'\b([A-Z]{2}\d{2,4})\b', text.upper())
    if match:
        return match.group(1)
    return None


def extract_aircraft_model(text):
    """Extract aircraft model."""
    # Pattern 1: Full manufacturer + model
    match = re.search(r'\b(Airbus|Boeing|Embraer)\s+(A\d{3}[-\s]?\d{0,3}[A-Z]*|B?\d{3}[-\s]?\d{0,3}[A-Z]*)\b', text, re.IGNORECASE)
    if match:
        manufacturer = match.group(1).title()
        model = match.group(2).strip()
        return f"{manufacturer} {model}"
    
    # Pattern 2: Just model code
    match = re.search(r'\b(A\d{3}|B?\d{3})\b', text, re.IGNORECASE)
    if match:
        code = match.group(1).upper()
        if code.startswith('A'):
            return f"Airbus {code}"
        else:
            return f"Boeing {code}"
    
    return None


def is_asking_about_aircraft(text):
    """Determine if user is asking about an aircraft."""
    aircraft_keywords = ['aircraft', 'plane', 'airplane', 'model', 'airbus', 'boeing', 'embraer']
    return any(keyword in text.lower() for keyword in aircraft_keywords)


# ======================
# ✅ DETAILED Aircraft Query
# ======================

def query_aircraft(model):
    """Query aircraft with detailed logging."""
    print("\n" + "="*60)
    print(f"🔍 AIRCRAFT QUERY STARTED")
    print("="*60)
    print(f"📝 Input: '{model}'")
    
    if not airline_cursor:
        print("❌ ERROR: airline_cursor is None!")
        return None
    
    try:
        # Try exact match first
        sql = "SELECT * FROM Aircraft WHERE Model = %s LIMIT 1"
        print(f"\n📊 SQL Query: {sql}")
        print(f"📊 Parameters: ('{model}',)")
        
        airline_cursor.execute(sql, (model,))
        result = airline_cursor.fetchone()
        
        print(f"📊 Cursor description: {airline_cursor.description}")
        print(f"📊 Row count: {airline_cursor.rowcount}")
        print(f"📊 Result: {result}")
        
        if result:
            print("✅ FOUND with exact match!")
            print("="*60 + "\n")
            return result
        
        print("❌ No exact match, trying case-insensitive...")
        
        # Try case-insensitive
        sql = "SELECT * FROM Aircraft WHERE UPPER(Model) = UPPER(%s) LIMIT 1"
        print(f"\n📊 SQL Query: {sql}")
        print(f"📊 Parameters: ('{model}',)")
        
        airline_cursor.execute(sql, (model,))
        result = airline_cursor.fetchone()
        
        print(f"📊 Result: {result}")
        
        if result:
            print("✅ FOUND with case-insensitive match!")
            print("="*60 + "\n")
            return result
        
        print("❌ No case-insensitive match, trying LIKE...")
        
        # Try LIKE
        sql = "SELECT * FROM Aircraft WHERE Model LIKE %s LIMIT 1"
        print(f"\n📊 SQL Query: {sql}")
        print(f"📊 Parameters: ('%{model}%',)")
        
        airline_cursor.execute(sql, (f"%{model}%",))
        result = airline_cursor.fetchone()
        
        print(f"📊 Result: {result}")
        
        if result:
            print("✅ FOUND with LIKE match!")
            print("="*60 + "\n")
            return result
        
        print("❌ NO MATCH FOUND")
        print("="*60 + "\n")
        return None
        
    except Exception as e:
        print(f"\n❌ EXCEPTION in query_aircraft: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return None


def get_all_aircraft_models():
    """Get all aircraft models from database."""
    try:
        if not airline_cursor:
            return []
        
        airline_cursor.execute("SELECT DISTINCT Model FROM Aircraft ORDER BY Model LIMIT 20")
        results = airline_cursor.fetchall()
        return [row['Model'] for row in results]
    except Exception as e:
        print(f"❌ Error getting aircraft list: {e}")
        return []


def query_flight(flight_number):
    """Query flight details from database."""
    try:
        if not airline_cursor:
            print("❌ airline_cursor is None!")
            return None
        
        sql = """
            SELECT 
                f.FlightNumber,
                f.ScheduledDeparture,
                f.ScheduledArrival,
                oa.AirportCode AS Origin,
                da.AirportCode AS Destination,
                a.Model AS Aircraft,
                a.CapacityPassengers AS Capacity,
                f.Status
            FROM Flights f
            JOIN Airports oa ON f.OriginAirportID = oa.AirportID
            JOIN Airports da ON f.DestinationAirportID = da.AirportID
            JOIN Aircraft a ON f.AircraftID = a.AircraftID
            WHERE f.FlightNumber = %s
            ORDER BY f.ScheduledDeparture DESC
            LIMIT 1
        """
        
        print(f"\n🔍 Querying flight: {flight_number}")
        airline_cursor.execute(sql, (flight_number,))
        result = airline_cursor.fetchone()
        print(f"✅ Flight result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ======================
# Response Formatters
# ======================

def format_flight_info(data):
    """Format flight data into readable text."""
    if not data:
        return None
    
    return f"""✈️ Flight {data['FlightNumber']}

🛫 Departure: {data['ScheduledDeparture']} from {data['Origin']}
🛬 Arrival: {data['ScheduledArrival']} at {data['Destination']}
✈️ Aircraft: {data['Aircraft']} (Capacity: {data['Capacity']} passengers)
📊 Status: {data['Status']}"""


def format_aircraft_info(data):
    """Format aircraft data into readable text."""
    if not data:
        return None
    
    return f"""✈️ Aircraft {data['Model']}

🔢 Registration: {data['RegistrationNumber']}
🧍 Passenger Capacity: {data['PassengerCapacity']}
📦 Cargo Capacity: {data['CargoCapacityKg']} kg
📊 Status: {data['Status']}"""


# ======================
# Main Chat Logic
# ======================

def process_message(message, session_id="default"):
    """Process user message and return response."""
    
    print("\n" + "="*60)
    print(f"📨 NEW MESSAGE")
    print("="*60)
    print(f"Message: {message}")
    print(f"Session: {session_id}")
    
    # Initialize context
    if session_id not in user_contexts:
        user_contexts[session_id] = {}
    
    context = user_contexts[session_id]
    
    # Extract entities
    flight_num = extract_flight_number(message)
    aircraft = extract_aircraft_model(message)
    
    print(f"\n🔍 PARSING RESULTS:")
    print(f"   Flight Number: {flight_num}")
    print(f"   Aircraft Model: {aircraft}")
    
    # Determine intent
    asking_aircraft = is_asking_about_aircraft(message)
    print(f"   Asking about aircraft: {asking_aircraft}")
    
    # Check for follow-up
    followup_words = ['what about', 'how about', 'tell me about', 'show me', 'check']
    is_followup = any(word in message.lower() for word in followup_words)
    print(f"   Is follow-up: {is_followup}")
    
    # ===== Handle Aircraft =====
    if aircraft or asking_aircraft:
        search_term = aircraft if aircraft else message.strip()
        print(f"\n🛩️ AIRCRAFT QUERY MODE")
        print(f"   Search term: '{search_term}'")
        
        aircraft_data = query_aircraft(search_term)
        
        if aircraft_data:
            user_contexts[session_id] = {
                'type': 'aircraft',
                'model': search_term,
                'data': aircraft_data
            }
            
            response = format_aircraft_info(aircraft_data)
            print(f"\n✅ SUCCESS - Returning aircraft info")
            print("="*60 + "\n")
            return response
        else:
            all_models = get_all_aircraft_models()
            models_list = "\n".join([f"  • {m}" for m in all_models[:5]])
            
            print(f"\n❌ NOT FOUND - Showing available models")
            print("="*60 + "\n")
            
            return f"""Sorry, I couldn't find '{search_term}'.

Available aircraft models:
{models_list}

Try one of these!"""
    
    # ===== Handle Flight =====
    elif flight_num:
        print(f"\n✈️ FLIGHT QUERY MODE")
        print(f"   Flight number: {flight_num}")
        
        flight_data = query_flight(flight_num)
        
        if flight_data:
            user_contexts[session_id] = {
                'type': 'flight',
                'flight_number': flight_num,
                'data': flight_data
            }
            
            response = format_flight_info(flight_data)
            print(f"\n✅ SUCCESS - Returning flight info")
            print("="*60 + "\n")
            return response
        else:
            print(f"\n❌ NOT FOUND")
            print("="*60 + "\n")
            return f"Sorry, I couldn't find flight {flight_num}."
    
    # ===== Follow-up =====
    elif is_followup and context:
        if context.get('type') == 'flight':
            return format_flight_info(context['data'])
        elif context.get('type') == 'aircraft':
            return format_aircraft_info(context['data'])
    
    # ===== Fallback =====
    print("\n❓ FALLBACK MODE")
    print("="*60 + "\n")
    
    return """I can help you with:
• Flight info - "What is flight AA101?"
• Aircraft details - "Tell me about Airbus A320"

What would you like to know?"""


# ======================
# API Routes
# ======================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default")
        
        if not message:
            return jsonify({"reply": "Please send a message!"})
        
        reply = process_message(message, session_id)
        
        return jsonify({
            "reply": reply,
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"\n❌ EXCEPTION in /chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "Sorry, an error occurred."})


@app.route("/test-db", methods=["GET"])
def test_db():
    """Manual database test endpoint."""
    success = test_database_connection()
    return jsonify({"success": success})


@app.route("/debug/aircraft", methods=["GET"])
def debug_aircraft():
    """Show all aircraft in database."""
    try:
        if not airline_cursor:
            return jsonify({"error": "Database cursor is None"})
        
        airline_cursor.execute("SELECT * FROM Aircraft LIMIT 10")
        aircraft_list = airline_cursor.fetchall()
        return jsonify(aircraft_list)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 FLASK SERVER STARTING")
    print("="*60)
    print("📡 Endpoints:")
    print("   POST /chat")
    print("   GET /test-db")
    print("   GET /debug/aircraft")
    print("="*60 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)