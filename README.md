# Chess Desktop Match Tracking App

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
[![Chess Dashboard App](https://github.com/ComeG3tSome/GameStatChess/blob/main/ChessDashboard.png)](https://www.youtube.com/watch?v=2l-8jVkEXDk)

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

## Configuration
Before running the application, configure the following settings:

1) PostgreSQL Database Configuration
```
   1) Ensure that the PostgreSQL server is running.
   2) Create a PostgreSQL database
   3) Set the DATABASE_URL environment variable with your PostgreSQL credentials:
   postgresql+psycopg2://(POSTGRESQL-USERNAME):(PASSWORD)@localhost:5432/(Database name)
   4) Update models.py to read the database connection string from the environment variable:

   import os

   DATABASE_URL = os.environ["DATABASE_URL"]
```
2) Chess.com API Configuration

In GameStatOnlineChess.py configure the following constants:
```   
   USER_AGENT = "ChessRecordApp/1.0 (contact: your-email@example.com)"
   MONTHS_TO_FETCH = 1
```
* **USER_AGENT**: Identifies the application when making requests to the Chess.com Public API.
* **MONTHS_TO_FETCH**: Specifies how many of the most recent available monthly game archives the application retrieves during synchronization. For example, setting MONTHS_TO_FETCH = 3 retrieves games from the three most recent available monthly archives.

3) Chess.com Username

When using the **Synchronize Chess.com** button: 
```
1) Enter a valid Chess.com username.
2) The application retrieves the player's game history from the Chess.com Public API.
3) Wins and losses are imported into the PostgreSQL database.
4) The dashboard updates to display the synchronized records and win/loss totals.
```

**Note:** Draws are currently excluded from synchronization

## Usage
1. Ensure that the PostgreSQL server is running and the database connection is properly configured.
2. Run the application.
3. The Chess Desktop Match Tracking app's dashboard opens, displaying a table with the following columns:
   * **ID:** Unique identifier assigned to each chess game record.
   * **Date:** Date of the chess match.
   * **Opponent:** Username or name of the opponent
   * **Result:** Outcome of the match (Win or Loss)..
4. To manually add a chess game record:
   * Click **Add Win** or **Add Loss**.
   * Enter the opponent's name and the match date in YYYY-MM-DD format.
   * Select the match result and click **Save** to save the record.
5. To modify an existing record:
   * Select a record from the table.
   * Click **Edit**.
   * Modify the match result, opponent's name, or date.
   * Click **Save** to save the changes.
6. To delete a specific record:
   * Select the record from the table
   * Click **Delete**.
   * Confirm the deletion
7. To synchronize chess games from Chess.com
   * Click **Synchronize Chess.com**.
   * Enter a valid Chess.com username when prompted.
   * The application retrieves the player's games from the most recent available monthly archives, according to the MONTHS_TO_FETCH setting.
   * Only wins and losses are processed; draws are currently excluded.
   * The application checks for existing records based on the opponent, match result, and date to reduce duplicate entries
   * New records are stored in the PostgreSQL database and displayed in the dashboard.
8. After synchronization, the application displays a summary containing:
   * Total games scanned
   * Wins and losses detected.
   * Number of new records inserted.
   * Draws detected (currently not counted by the implementation)
9. The dashboard automatically updates the total number of wins and losses whenever records are added, edited, deleted, or synchronized.
10. To delete all stored chess game records:
   * Click **Reset (Delete everything)**.
   * Confirm the operation
   * The application deletes all records and resets their IDs.
11. Close the application using the window's close button. The database session is automatically closed.

**Note:** In the current implementation, the application also resets the database every time it starts. Remove the reset_chess_records(start_at_zero=False) call from the startup code if you want records to persist between launches.


## Dependencies
The Chess Desktop Match Tracking App's dashboard uses the following Python libraries and technologies: 
* **Python 3.10+**: Programming language used to develop the application.
* **tkinter**: Python's standard GUI library used to build the desktop dashboard.
* **requests**: Handles HTTP requests to retrieve chess game data from the Chess.com Public API
* **sqlalchemy**: Object-Relational Mapping (ORM) library used to manage database operations.
* **psycopg2-binary**: PostgreSQL database adapter that enables communication between Python and PostgreSQL.
* **PostgreSQL**: Relational database management system used to store chess game records.




## Projects structure

```text
GameStatChess/
│
├── GameStatOnlineChess.py   # Main application and Tkinter GUI
├── models.py                # PostgreSQL database models and SQLAlchemy configuration
├── OnlineChessAPI.py        # Chess.com API game result processing
├── requirement.txt          # Required Python dependencies
├── .gitignore               # Specifies files and folders Git should ignore
├── __pycache__/             # Python-generated bytecode cache files
└── README.md                # Project documentation
```

## Licensing 
This project is licensed under the [MIT License](https://opensource.org/license/mit).
