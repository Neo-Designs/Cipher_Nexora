from db_queries import *
import datetime
from flask import session

def retrieve_relevant_data(user_message):
    message = user_message.lower()

    schedule_keywords = ["class", "classes", "schedule", "timetable", "class schedule"]
    bus_keywords = ["bus", "bus schedule", "route", "bus time"]
    cafeteria_keywords = ["cafeteria", "canteen", "food", "meal", "menu", "lunch", "breakfast", "snack", "drink"]
    if any(kw in message for kw in map(str.lower, schedule_keywords)):
        user_id = session.get('user_id')
        user_role = session.get('role')

        if not user_id or user_role != 'student':
            return "🔒 Please log in as a student to access your schedule."

        schedule = get_student_schedule(user_id)
        if not schedule:
            return "No classes found in your schedule."

        lines = []
        for row in schedule:
            course_name, day, start, end, building, room = row
            line = f"{course_name} - {day} {start}-{end} in {building} room {room}"
            lines.append(line)
        return "\n".join(lines)

    elif any(kw in message for kw in map(str.lower, bus_keywords)):

        user_id = session.get('user_id')
        user_role = session.get('role')

        route_id = None
        if user_id and user_role in ('student', 'professor'):
            if user_role == 'student':
                route_id = get_student_bus_route_id(user_id)
            else:
                route_id = get_professor_bus_route_id(user_id)

        bus_schedule = get_bus_schedule(route_id)

        if not bus_schedule:
            return "No bus schedules found."

        route_name = next(iter(bus_schedule))
        stops = bus_schedule[route_name]

        stop_names = list(stops.keys())
        first_stop = stop_names[0]
        last_stop = stop_names[-1]

        def get_first_time(times_list):
            times = [t for t in times_list if isinstance(t, datetime.time)]
            return min(times).strftime("%H:%M") if times else None

        def get_last_time(times_list):
            times = [t for t in times_list if isinstance(t, datetime.time)]
            return max(times).strftime("%H:%M") if times else None

        start_time = get_first_time(stops[first_stop]['Departing']) or get_first_time(stops[first_stop]['Arriving'])
        end_time = get_last_time(stops[last_stop]['Arriving']) or get_last_time(stops[last_stop]['Departing'])

        intermediate = ', '.join(stop_names[1:-1])
        if intermediate:
            stop_phrase = f"makes stops including {intermediate}, "
        else:
            stop_phrase = ""

        reply = (
            f"The {route_name} bus starts at {first_stop} around {start_time}, "
            f"{stop_phrase}and ends at {last_stop} around {end_time}."
        )


        return reply

    elif any(kw in message for kw in map(str.lower, cafeteria_keywords)):
        day = datetime.datetime.today().strftime("%A")

        dietary_preference = None
        user_id = session.get('user_id')
        user_role = session.get('role')
        if user_id and user_role in ('student', 'professor'):
            if user_role == 'student':
                dietary_preference = get_student_dietary_preference(user_id)
            else:
                dietary_preference = get_professor_dietary_preference(user_id)

        items = get_cafeteria_menu(day, dietary_preference)

        if not items:
            return f"No cafeteria menu found for {day}."

        menus = {}
        for cafeteria_name, item_name, category, price, dietary in items:
            menus.setdefault(cafeteria_name, {}).setdefault(category, []).append((item_name, price))

        lines = []
        for caf_name, categories in menus.items():
            lines.append(f"Menu at {caf_name} for {day}:")
            for cat, item_list in categories.items():
                lines.append(f"  {cat.capitalize()}:")
                for item_name, price in item_list:
                    lines.append(f"    - {item_name} (${price:.2f})")
            lines.append("")

        return "\n".join(lines)


    elif "event" in message or "what's happening" in message:
        events = get_upcoming_events()
        if not events:
            return "No upcoming events."
        return "\n".join(
            f"{row.EventName} on {row.EventDate.strftime('%A, %b %d')} at {row.EventTime.strftime('%H:%M')} in {row.Venue} — Hosted by {row.HostedBy}: {row.Description}"
            for row in events
        )

    return "I'm not sure how to help with that yet. You can ask me about classes, bus schedules, cafeteria menus, or events!"

