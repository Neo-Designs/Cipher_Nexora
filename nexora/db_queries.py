from db_connect import get_connection
from datetime import datetime

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_student_schedule(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ReferenceID FROM Users WHERE UserID = ? AND Role = 'student'", (user_id,))
    ref_row = cursor.fetchone()
    if not ref_row:
        conn.close()
        return []

    student_id = ref_row[0]

    cursor.execute("SELECT Batch, ProgramID FROM Students WHERE StudentID = ?", (student_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []

    student_batch, program_id = row

    cursor.execute("SELECT DepartmentID FROM Programs WHERE ProgramID = ?", (program_id,))
    dept_row = cursor.fetchone()
    if not dept_row:
        conn.close()
        return []

    department_id = dept_row[0]

    cursor.execute("""
        SELECT 
            c.CourseName, 
            t.DayOfWeek, 
            t.StartTime, 
            t.EndTime, 
            r.BuildingName, 
            r.RoomNumber
        FROM CourseOfferings co
        JOIN Courses c ON co.CourseID = c.CourseID
        JOIN TimeSlots t ON co.TimeSlotID = t.TimeSlotID
        JOIN Rooms r ON co.RoomID = r.RoomID
        WHERE co.Batch = ? AND c.DepartmentID = ?
    """, (student_batch, department_id))

    schedule = cursor.fetchall()
    conn.close()
    return schedule

def get_student_bus_route_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.BusRouteID
        FROM Students s
        JOIN Users u ON s.StudentID = u.ReferenceID
        WHERE u.UserID = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_professor_bus_route_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.BusRouteID
        FROM Professors p
        JOIN Users u ON p.ProfessorID = u.ReferenceID
        WHERE u.UserID = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_bus_schedule(route_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if route_id:
        cursor.execute("""
            SELECT br.RouteName, bs.StopName, bss.Direction, bss.Time
            FROM BusRoutes br
            JOIN BusStops bs ON br.RouteID = bs.RouteID
            JOIN BusStopSchedules bss ON bss.RouteID = br.RouteID AND bss.StopID = bs.StopID
            WHERE br.RouteID = ?
            ORDER BY bs.StopOrder, bss.Direction DESC, bss.Time
        """, (route_id,))
    else:
        cursor.execute("""
            SELECT br.RouteName, bs.StopName, bss.Direction, bss.Time
            FROM BusRoutes br
            JOIN BusStops bs ON br.RouteID = bs.RouteID
            JOIN BusStopSchedules bss ON bss.RouteID = br.RouteID AND bss.StopID = bs.StopID
            ORDER BY br.RouteName, bs.StopOrder, bss.Direction DESC, bss.Time
        """)

    results = cursor.fetchall()
    conn.close()

    schedule = {}
    for route_name, stop_name, direction, time in results:
        route = schedule.setdefault(route_name, {})
        stop = route.setdefault(stop_name, {'Arriving': [], 'Departing': []})
        stop[direction].append(time)

    return schedule

def get_student_dietary_preference(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.DietaryPreference
        FROM Students s
        JOIN Users u ON s.StudentID = u.ReferenceID
        WHERE u.UserID = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_professor_dietary_preference(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.DietaryPreference
        FROM Professors p
        JOIN Users u ON p.ProfessorID = u.ReferenceID
        WHERE u.UserID = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_cafeteria_menu(day_of_week, dietary_preference=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    if dietary_preference:
        cursor.execute("""
            SELECT c.Name, m.ItemName, m.Category, m.Price, m.Dietary_Preference
            FROM DailyMenus d
            JOIN Cafeterias c ON d.CafeteriaID = c.CafeteriaID
            JOIN MenuItems m ON d.ItemID = m.ItemID
            WHERE d.AvailableDay = ?
            AND (m.Dietary_Preference IS NULL OR m.Dietary_Preference = '' OR m.Dietary_Preference = ?)
        """, (day_of_week, dietary_preference))
    else:
        cursor.execute("""
            SELECT c.Name, m.ItemName, m.Category, m.Price, m.Dietary_Preference
            FROM DailyMenus d
            JOIN Cafeterias c ON d.CafeteriaID = c.CafeteriaID
            JOIN MenuItems m ON d.ItemID = m.ItemID
            WHERE d.AvailableDay = ?
        """, (day_of_week,))

    data = cursor.fetchall()
    conn.close()
    return data

def get_upcoming_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EventName, EventDate, EventTime, Venue, HostedBy, Description
        FROM Events
        WHERE EventDate >= CAST(GETDATE() AS DATE)
        ORDER BY EventDate, EventTime
    """)
    events = cursor.fetchall()
    conn.close()
    return events

def get_knowledge_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Title, Content, Tags FROM KnowledgeBase")
    entries = cursor.fetchall()
    conn.close()
    return entries

def get_programs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ProgramID, ProgramName, DegreeLevel FROM Programs")
    programs = cursor.fetchall()
    conn.close()
    return programs

def get_student_name(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName FROM Students WHERE StudentID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return f"{row.FirstName} {row.LastName}" if row else "Unknown Student"

def get_professor_name(prof_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName, LastName FROM Professors WHERE ProfessorID = ?", (prof_id,))
    row = cursor.fetchone()
    conn.close()
    return f"{row.FirstName} {row.LastName}" if row else "Unknown Professor"

def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT RoomID, RoomNumber FROM Rooms")
    return [{'RoomID': row[0], 'RoomNumber': row[1]} for row in cursor.fetchall()]

def get_all_timeslots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TimeSlotID, DayOfWeek, StartTime, EndTime FROM TimeSlots")
    return [{'TimeSlotID': str(row[0]), 'DayOfWeek': row[1], 'StartTime': row[2], 'EndTime': row[3]} for row in cursor.fetchall()]

def get_all_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Courses")
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_students():
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_all_professors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Professors")
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments")
    return [{'DepartmentID': row[0], 'DepartmentName': row[1]} for row in cursor.fetchall()]

def get_courses_by_department(dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CourseID, CourseCode, CourseName FROM Courses WHERE DepartmentID = ?", (dept_id,))
    return [{'CourseID': row[0], 'CourseCode': row[1], 'CourseName': row[2]} for row in cursor.fetchall()]

def get_professors_by_department(dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ProfessorID, FirstName, LastName FROM Professors WHERE DepartmentID = ?", (dept_id,))
    return [{'ProfessorID': row[0], 'FirstName': row[1], 'LastName': row[2]} for row in cursor.fetchall()]

def insert_course_offering(course_id, professor_id, timeslot_id, room_id, batch):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO CourseOfferings (CourseID, ProfessorID, TimeSlotID, RoomID, Batch) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (course_id, professor_id, timeslot_id, room_id, batch))
    conn.commit()
    cursor.close()
    conn.close()

def get_existing_schedule():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT co.TimeSlotID, co.RoomID, ts.DayOfWeek, r.RoomNumber,
               c.CourseID, c.CourseCode, c.CourseName, c.DepartmentID,
               p.ProfessorID, p.FirstName, p.LastName, co.Batch
        FROM CourseOfferings co
        JOIN TimeSlots ts ON co.TimeSlotID = ts.TimeSlotID
        JOIN Rooms r ON co.RoomID = r.RoomID
        JOIN Courses c ON co.CourseID = c.CourseID
        JOIN Professors p ON co.ProfessorID = p.ProfessorID
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def get_all_cafeterias():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT CafeteriaID, Name, Location FROM Cafeterias ORDER BY Name"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def insert_menu_item(name, category, price, diet):
    conn = get_connection()
    cursor = conn.cursor()

    select_query = "SELECT ItemID FROM MenuItems WHERE ItemName = ? AND Category = ? AND Price = ? AND Dietary_Preference = ?"
    cursor.execute(select_query, (name, category, price, diet))
    existing = cursor.fetchone()

    if existing:
        item_id = existing[0]
    else:
        insert_query = """
            INSERT INTO MenuItems (ItemName, Category, Price, Dietary_Preference)
            OUTPUT INSERTED.ItemID
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_query, (name, category, price, diet))
        item_id = cursor.fetchone()[0]
        conn.commit()

    cursor.close()
    conn.close()
    return item_id

def insert_daily_menu(cafeteria_id, item_id, available_day):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO DailyMenus (CafeteriaID, ItemID, AvailableDay) VALUES (?, ?, ?)"
    cursor.execute(query, (cafeteria_id, item_id, available_day))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_bus_routes():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT r.RouteID, r.RouteName, s.StopID, s.StopName, s.StopOrder, sch.Direction, sch.Time
    FROM BusRoutes r
    JOIN BusStops s ON r.RouteID = s.RouteID
    JOIN BusStopSchedules sch ON sch.RouteID = r.RouteID AND sch.StopID = s.StopID
    ORDER BY r.RouteID, s.StopOrder
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    routes = {}
    for row in rows:
        route_id, route_name, stop_id, stop_name, stop_order, direction, time = row

        time_str = time.strftime('%H:%M:%S') if time else None

        if route_id not in routes:
            routes[route_id] = {
                'routeID': route_id,
                'routeName': route_name,
                'direction': direction,
                'stops': []
            }

        routes[route_id]['stops'].append({
            'stopID': stop_id,
            'stopName': stop_name,
            'time': time_str,
            'order': stop_order
        })

    cursor.close()
    conn.close()
    return list(routes.values())


def insert_bus_route(route_name, direction, stops):
    conn = get_connection()
    cursor = conn.cursor()

    insert_route = """
        INSERT INTO BusRoutes (RouteName)
        OUTPUT INSERTED.RouteID
        VALUES (?)
    """
    cursor.execute(insert_route, (route_name,))
    route_id = cursor.fetchone()[0]

    for index, stop in enumerate(stops):
        insert_stop = """
            INSERT INTO BusStops (RouteID, StopName, StopOrder)
            OUTPUT INSERTED.StopID
            VALUES (?, ?, ?)
        """
        cursor.execute(insert_stop, (route_id, stop['stopName'], index + 1))
        stop_id = cursor.fetchone()[0]

        insert_schedule = """
            INSERT INTO BusStopSchedules (RouteID, StopID, Direction, Time)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_schedule, (route_id, stop_id, direction, stop['time']))

    conn.commit()
    cursor.close()
    conn.close()
    return route_id


def update_bus_route(route_id, route_name, direction, stops):
    conn = get_connection()
    cursor = conn.cursor()

    delete_schedules = "DELETE FROM BusStopSchedules WHERE RouteID = ?"
    delete_stops = "DELETE FROM BusStops WHERE RouteID = ?"
    cursor.execute(delete_schedules, (route_id,))
    cursor.execute(delete_stops, (route_id,))

    update_route = "UPDATE BusRoutes SET RouteName = ? WHERE RouteID = ?"
    cursor.execute(update_route, (route_name, route_id))

    for index, stop in enumerate(stops):
        insert_stop = """
            INSERT INTO BusStops (RouteID, StopName, StopOrder)
            OUTPUT INSERTED.StopID
            VALUES (?, ?, ?)
        """
        cursor.execute(insert_stop, (route_id, stop['stopName'], index + 1))
        stop_id = cursor.fetchone()[0]

        insert_schedule = """
            INSERT INTO BusStopSchedules (RouteID, StopID, Direction, Time)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_schedule, (route_id, stop_id, direction, stop['time']))

    conn.commit()
    cursor.close()
    conn.close()
    return True


def delete_bus_route(route_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM BusStopSchedules WHERE RouteID = ?", (route_id,))
    cursor.execute("DELETE FROM BusStops WHERE RouteID = ?", (route_id,))
    cursor.execute("DELETE FROM BusRoutes WHERE RouteID = ?", (route_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return True

def insert_event(name, date, time, venue, host, description):
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO Events (EventName, EventDate, EventTime, Venue, HostedBy, Description)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (name, date, time, venue, host, description))
    conn.commit()

    cursor.close()
    conn.close()
