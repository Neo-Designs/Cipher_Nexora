import os
import bcrypt
from dotenv import load_dotenv
from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from groq import Groq
from rag_engine import retrieve_relevant_data
from db_connect import get_connection
from datetime import datetime, timedelta
from db_queries import *
from functools import wraps


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
with open("prompt.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read().strip()

app = Flask(__name__)
client = Groq(api_key=GROQ_API_KEY)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=24)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('chat'))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    user_name = session.get('name')
    return render_template('index.html', user_name=user_name)

@app.route("/chat/message", methods=["POST"])
def process_chat():
    try:
        user_message = request.json.get("message")

        restricted_keywords = [
            "lunch menu", "lunch", "menu", "cafeteria", "bus", "schedule", "bus time",
            "timetable", "lecture", "class", "exam", "module", "faculty", "university"
        ]
        lower_msg = user_message.lower()
        if any(keyword in lower_msg for keyword in restricted_keywords):
            if 'user_id' not in session:
                return jsonify({"response": "🔒 Please log in to access university-specific info like schedules, menus, and classes."})

        response = get_ai_response(user_message)
        return jsonify({"response": response})
    except Exception as e:
        print("Error in /chat/message route:", str(e))
        return jsonify({"response": "Oops! Nexora encountered a server issue."}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_row = get_user_by_email(email)
        if user_row:
            stored_hash = user_row.PasswordHash.encode('utf-8')
            entered_pw = password.encode('utf-8')

            if bcrypt.checkpw(entered_pw, stored_hash):
                session.permanent = True
                session['user_id'] = user_row.UserID
                session['email'] = user_row.Email
                session['role'] = user_row.Role
                session['reference_id'] = user_row.ReferenceID
                session['chat_id'] = str(user_row.UserID) + '_' + datetime.now().strftime("%Y%m%d")

                if user_row.Role == 'student':
                    session['name'] = get_student_name(user_row.ReferenceID)
                elif user_row.Role == 'professor':
                    session['name'] = get_professor_name(user_row.ReferenceID)
                else:
                    session['name'] = "Admin"

                if user_row.Role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('chat'))

        flash("Invalid login.")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin')
@admin_only
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/nexora')
@login_required
def chat():
    user_id = session['user_id']
    user_name = session.get('name')
    return render_template('index.html', user_name=user_name)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def get_ai_response(user_message):
    try:
        context = retrieve_relevant_data(user_message)
        if context:
            system_prompt = SYSTEM_PROMPT + f"\n\nRelevant Data:\n{context}"
        else:
            system_prompt = SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        chat = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print("Groq API error:", str(e))
        return "Nexora ran into a glitch while processing your request."

@app.route('/admin/get_user_details')
@admin_only
def get_user_details():
    role = request.args.get('role')
    email = request.args.get('email')
    if role not in ('student','professor'): return {}
    tab = 'Students' if role=='student' else 'Professors'
    cur = get_connection().cursor()
    cur.execute(f"""
        SELECT {tab}.FirstName, {tab}.LastName, {tab}.Address, b.RouteName AS BusRoute, {tab}.DietaryPreference
        FROM {tab}
        LEFT JOIN 
        BusRoutes b ON {tab}.BusRouteID = b.RouteID
        WHERE {tab}.Email = ?
    """, (email,))
    row = cur.fetchone()
    if row:
        return jsonify({
            'name': f"{row.FirstName} {row.LastName}",
            'address': row.Address,
            'bus_route': row.BusRoute,
            'diet': row.DietaryPreference
        })
    else:
        return {}

@app.route('/admin/register_user', methods=['GET','POST'])
@admin_only
def register_user():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form.get('email')
        pwd = request.form['password']
        conf = request.form['confirm_password']
        if pwd != conf:
            flash("Passwords don't match")
            return redirect('register_user')

        ref = None
        if role in ('student','professor'):
            conn = get_connection()
            tab = 'Students' if role=='student' else 'Professors'
            cur = conn.cursor()
            cur.execute(f"SELECT {'StudentID' if role=='student' else 'ProfessorID'} "
                        f"FROM {tab} WHERE Email=?", (email,))
            row = cur.fetchone(); conn.close()
            if row:
                ref = row[0]
            else:
                flash("Email not found")
                return redirect('register_user')

        elif role == 'admin':
            ref = None

        hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode('utf-8')

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Users (Email, PasswordHash, Role, ReferenceID) VALUES (?, ?, ?, ?)",
                    (email, hashed, role, ref))
        conn.commit()
        conn.close()
        flash("User registered!")
        return redirect(url_for('admin_dashboard'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Email FROM Students WHERE Email NOT IN (SELECT Email FROM Users)")
    students = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT Email FROM Professors WHERE Email NOT IN (SELECT Email FROM Users)")
    professors = [r[0] for r in cur.fetchall()]
    conn.close()
    newsletters = list(set(students + professors))
    return render_template('register_user.html', students=students, professors=professors, uni_emails=newsletters)

@app.route('/admin/update_schedule', methods=['GET', 'POST'])
@admin_only
def update_schedule():
    if request.method == 'POST':
        data = request.form
        department_id = data.get('department')
        insert_count = 0

        for key in data:
            if key == 'department':
                continue
        
            try:
                day_part, room_part, slot_part, field_type = key.replace(']', '').split('[')
                entry_key = f"{day_part}|{room_part}|{slot_part}"
            except ValueError:
                continue

            if 'schedule_entries' not in locals():
                schedule_entries = {}

            if entry_key not in schedule_entries:
                schedule_entries[entry_key] = {}

            schedule_entries[entry_key][field_type] = data[key]

        for entry_key, fields in schedule_entries.items():
            try:
                day, room_number, slot_id = entry_key.split('|')
                batch = fields.get('batch')
                course_id = fields.get('subject')
                professor_id = fields.get('lecturer')

                if not all([batch, course_id, professor_id]):
                    continue

                rooms = get_all_rooms()
                room = next((r for r in rooms if str(r['RoomNumber']) == str(room_number)), None)
                if not room:
                    continue
                room_id = room['RoomID']

                insert_course_offering(course_id, professor_id, slot_id, room_id, batch)
                insert_count += 1
            except Exception as e:
                print(f"Skipping entry due to error: {e}")

        flash(f"{insert_count} schedule entries saved.", "success")
        return redirect(url_for('update_schedule'))

    existing_schedule = get_existing_schedule()
    existing_schedule_map = {
        f"{row['DayOfWeek'].lower()}|{row['RoomNumber']}|{row['TimeSlotID']}": row
        for row in existing_schedule
    }

    courses = get_all_courses()
    professors = get_all_professors()

    departments = get_all_departments()
    rooms = get_all_rooms()
    timeslots = get_all_timeslots()

    batches = ['25.1', '24.2', '24.1', '23.2', '23.1', '22.2', '22.1']

    slots_by_day = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        slots_by_day[day.lower()] = [slot for slot in timeslots if slot['DayOfWeek'].lower() == day.lower()]

    selected_department = request.args.get('department', type=int)

    if not selected_department:
        existing_schedule_map = {}
    else:
        filtered_schedule = [row for row in existing_schedule if row['DepartmentID'] == selected_department]
        existing_schedule_map = {
            f"{row['DayOfWeek'].lower()}|{row['RoomNumber']}|{row['TimeSlotID']}": row
            for row in filtered_schedule
        }

    return render_template('update_schedule.html', departments=departments, lecture_halls=rooms, time_slots_by_day=slots_by_day, courses=courses, professors=professors, batches=batches, existing_schedule=existing_schedule_map)

@app.route('/admin/get_department_data/<int:department_id>')
@admin_only
def get_department_data(department_id):
    courses = get_courses_by_department(department_id)
    professors = get_professors_by_department(department_id)
    return jsonify({'courses': courses, 'professors': professors})

@app.route('/admin/get_department_schedule/<int:department_id>')
@admin_only
def get_department_schedule(department_id):
    full_schedule = get_existing_schedule()
    filtered = [row for row in full_schedule if row['DepartmentID'] == department_id]
    schedule_map = {
        f"{row['DayOfWeek'].lower()}|{row['RoomNumber']}|{row['TimeSlotID']}": row
        for row in filtered
    }
    return jsonify(schedule_map)

@app.route('/admin/update_menu', methods=['GET'])
@admin_only
def update_menu():
    cafeterias = get_all_cafeterias()
    return render_template('update_menu.html', cafeterias=cafeterias)

@app.route('/admin/update_menu', methods=['POST'])
@admin_only
def save_menu_items():
    cafeteria_id = request.form['cafeteria_id']

    items = {}

    for key, value in request.form.items():
        if key.startswith("item_"):
            parts = key.split("_")
            if len(parts) == 5:
                day, meal, idx, field = parts[1], parts[2], parts[3], parts[4]
                item_key = f"{day}_{meal}_{idx}"
                if item_key not in items:
                    items[item_key] = {'day': day, 'meal': meal}
                items[item_key][field] = value

    for item in items.values():
        name = item.get('name')
        price = item.get('price')
        diet = item.get('diet')
        day = item.get('day')
        meal = item.get('meal')

        if name and price and diet:
            item_id = insert_menu_item(name, meal, price, diet)
            insert_daily_menu(cafeteria_id, item_id, day)

    return redirect('/admin/update_menu?success=1')

@app.route('/admin/update_bus', methods=['GET'])
@admin_only
def update_bus():
    return render_template('update_bus.html')

@app.route('/admin/bus_routes')
def get_all_bus_routes():
    routes = fetch_all_bus_routes()
    return jsonify(routes)

@app.route('/admin/bus_routes', methods=['POST'])
@admin_only
def create_bus_route():
    data = request.get_json()
    route_name = data['routeName']
    direction = data['direction']
    stops = data['stops']
    route_id = insert_bus_route(route_name, direction, stops)
    return jsonify({'message': 'Route created', 'routeID': route_id}), 201

@app.route('/admin/bus_routes/<int:route_id>', methods=['PUT'])
@admin_only
def edit_bus_route(route_id):
    data = request.get_json()
    route_name = data['routeName']
    direction = data['direction']
    stops = data['stops']
    update_bus_route(route_id, route_name, direction, stops)
    return jsonify({'message': 'Route updated'})

@app.route('/admin/bus_routes/<int:route_id>', methods=['DELETE'])
@admin_only
def remove_bus_route(route_id):
    delete_bus_route(route_id)
    return jsonify({'message': 'Route deleted'})

@app.route('/admin/update_events', methods=['GET'])
@admin_only
def update_events():
    return render_template('update_events.html')


@app.route('/admin/update_events', methods=['POST'])
@admin_only
def save_event():
    event_name = request.form['event_name']
    event_date = request.form['event_date']
    event_time = request.form['event_time']
    venue = request.form['venue']
    hosted_by = request.form['hosted_by']
    description = request.form['description']

    insert_event(event_name, event_date, event_time, venue, hosted_by, description)

    return redirect('/admin/update_events?success=1')

if __name__ == "__main__":
    app.run(debug=True)

