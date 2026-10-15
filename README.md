# Chess Record App

## Tracks chess wins and losses, supports CRUD operations, and synchronizes recent game results from the Chess.com API into a SQLAlchemy database.

## Features
* Chess.com API Integration: Connects to the Chess.com Public API to retrieve game history for a specified Chess.com username.
* Game Synchronization: Imports wins and losses from the most recent available monthly game archives, with a configurable number of archives to retrieve
* Game Record Management (CRUD): Allows users to manually add, view, edit, and delete chess game records.
* Win/Loss Statistics: Automatically calculates and displays the total number of wins and losses recorded in the database.
* PostgreSQL Database Integration: Uses PostgreSQL to store chess game records, including opponents, match results, and dates.
* SQLAlchemy ORM: Uses SQLAlchemy for database operations, including querying, inserting, updating, and deleting records.
* Duplicate Detection: Checks existing records before importing games to reduce duplicate entries based on opponent, result, and date.
* Graphical User Interface (GUI): Provides a desktop dashboard built with Python's Tkinter and ttk widgets, featuring an interactive table for viewing chess records.
* Input Validation: Validates match results and date formats when users manually add or edit records.
* Database Reset: Allows users to delete all stored chess records and reset record IDs after confirmation.
* Error Handling: Displays error messages for database failures, network issues, invalid usernames, and Chess.com API request errors.

## Live Demo

## Prerequisites
* **Python 3.10 or higher** — Required to run the application
* **PostgreSQL** — Relational database management system used to store chess game records
* **pip** — Python package manager used to install the required dependencies
* **Tkinter** — Python's standard GUI library, used to build the desktop interface. it is included with most Python installations but may require separate installation in some operating systems
* **Chess.com Account** — A Chess.com username with publicly accessible game history is needed to synchronize chess records.
* **Internet Connection** — Required to retrieve chess game data from the Chess.com Public API.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ComeG3tSome/GameStatChess
   cd GameStatChess
   ``` 
2.  Install the necessary Python packages required for the script to execute successfully:
```
    pip install sqlalchemy
    pip install psycopg2-binary
    pip install requests
```

3. Configure the PostgreSQL database:
```
    Ensure PostgreSQL is installed and running
    Create a database named OnlineChessDB (or any other name you prefer)
    Configure the database connection in models.py using your PostgreSQL credentials.
```
4. Run the application:
```
    python GameStatOnlineChess.py
```


   
