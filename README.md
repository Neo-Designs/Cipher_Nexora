# NovaCore University Copilot

##Project Overview
Nexora Campus Copilot is an intelligent AI assistant built for NovaCore University. Designed as a student support chatbot, Nexora provides real-time, personalized assistance with class schedules, cafeteria menus, campus bus times, and upcoming events, all powered by GroqAI and a live university database. Nexora blends conversational AI with structured data using Retrieval-Augmented Generation (RAG) to give students fast, helpful, and accurate answers.

## Features
##Core Features

Chat interface powered by Groq's LLaMA API
- Database-Driven RAG (Retrieval-Augmented Generation): Fuses SQL Server queries with AI-generated answers for precision.
- Secure Login: Email-based login system with role-based access (Student/Admin).
- Protected Data Access: Only authenticated users can access university info.
- Class Schedules: Retrieve accurate timetable info based on a student's program and batch.
- Cafeteria Menus: View daily meal options based on dietary preferences.
- Bus Schedules: Get bus stop and route info of buses arriving to and departing from campus.
- Event Listings: Stay informed about academic and campus events.



## Additional Features

- Voice-to-Text Input
- Dark/Light Mode Toggle
- Admin Dashboard to manage users, update schedules, bus routes, menus, and events.
- Custom Prompt for optimized university-specific responses.

##Tech Stack
Backend: Python (Flask), SQL Server (Microsoft), GroqAI API, RAG (Retrieval-Augmented Generation)
Frontend: HTML/CSS (with TailwindCSS), JavaScript
Database: MS SQL EXPRESS SERVER
Prerequisites: 
- System Requirements:- Python 3.10+ ,Microsoft SQL EXPRESS Server (with the NovaCoreUniversity DB setup), ODBC driver for SQL Server (e.g., ODBC Driver 18)
- Python Packages:- flask, python-dotenv, bcrypt, pyodbc, groq

## Screenshots and demo video
Will also be uploaded into repo under file demo&screenshots. demo video link ->  https://drive.google.com/file/d/18jcBlqnB6G-bVfyxpbTvgdFyzPz0AQvR/view?usp=drivesdk
![verification_and_light_mode](https://github.com/user-attachments/assets/1296f348-e27f-42b6-b2e3-8b10e22f973b)
![user_specific_replies](https://github.com/user-attachments/assets/391b49f7-5243-4445-b5c4-f3830f3c7bce)
![update_menu](https://github.com/user-attachments/assets/7fd9ae28-2303-4fed-89be-952c2e82ab98)
![update_busSchedule](https://github.com/user-attachments/assets/23604cc0-8541-4c87-9738-b1377561fa31)
![register_user](https://github.com/user-attachments/assets/8321ac70-236e-45de-9877-cb986dfdf16d)
![nexora_vs_vexora_character](https://github.com/user-attachments/assets/7688ecde-7c9c-4c9d-a239-b3dd0a073d89)
![nexora_typing_indicator](https://github.com/user-attachments/assets/dbfb09a1-8516-4656-894e-6c28fd0a2a00)
![login_page](https://github.com/user-attachments/assets/3caccaa9-0498-4c52-845f-b3ab7d46bf29)
![initial_screen](https://github.com/user-attachments/assets/6c59e262-b472-40ad-b984-56147b999e26)
![general_questions](https://github.com/user-attachments/assets/0fb4efb5-1367-4fe4-b274-062bd7bc11ff)
![admin_dashboard](https://github.com/user-attachments/assets/b0540ab1-ffc9-4819-9c68-537d277ab15c)
![add_event](https://github.com/user-attachments/assets/af643825-0337-4e04-82dc-900e5ad86fbd)


# Setup Instructions
Setup Instructions

1. Clone the Repository

git clone https://github.com/Neo-Designs/Cipher_Nexora.git
cd Cipher_Nexora/nexora

2. Install Dependencies
pip install (python packages metioned in prerequisits above, and any other pip install packages required by laptop)

3. Set up Database 
Restore the database using the .bak file.
Make sure that SQL EXPRESS Server is running locally and the database NovaCoreUniversity exists.
Update db_connect.py if server or driver differs

4. Run application
use python app.py to run application on http://localhost:5000. then open http://localhost:5000 on google browser to view nexora.

##Team
- Neola Udeshi Silva : groq AI connection, voice input feature, UI/UX design, admin dashboard, enforcing restrictions for guest users
- Panchalee Hewage: database connection, RAG architecture, user login, AI fallback prompts
