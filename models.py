import os
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# SQL Alchemy Base - From here you inherit the models (tables)
Base = declarative_base()

# MODEL / TABLE: ChessRecord
#   Represents a match record with:
#       id  : auto-incrementing primary key
#       opponent : opponent's name (optional, string)
#       result : 'Won" or "Lost" (string)
#       date : match date (string, YYYY-MM-DD format)
class ChessRecord(Base):
    __tablename__ = 'chess_records' # Name of table in the database
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opponent = Column(String)
    result = Column(String)  # 'Ganada' o 'Perdida' 
    date = Column(String)  # Store date as string for simplicity
    
    def __repr__(self):
        # Useful representation when printing model objects (debug/Logs)
        return f"<ChessRecord(id={self.id}, opponent='{self.opponent}', result='{self.result}', date='{self.date}')>"
    
# --- DATABASE CONNECTION CONFIGURATION 
# IMPORTANT: Here you are using PostgreSQL with user 'postgres'
# password '(password)' and database '(name of database)'
# Note: keeping the password in the code is not secure for production 
# Environment variables are typically used for production
DATABASE_URL = "postgresql+psycopg2://postgres:fireball967810211@localhost:5432/OnlineChessDB"

# ENGINE CREATION (database connection engine)
#  - echo=False: does not log all SQL queries (True for debugging)
#  - future=True: uses the new SQLAlchemy 2.0 API
#  - pool_pre_ping=True: verifies connections before use (prevents errors due to dropped connections)  
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# EARLY CONNECTION TEST
# - Try executing a SELECT 1. If there is a connection or credential issue,
#   it will fail here and you will see a clear error right at the start
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

# TABLE CREATION
# - Creates the tables defined in the models if they do not exist.
# - In this case, it will create 'chess_records' based on the ChessRecord class
Base.metadata.create_all(engine)

# SESSION FACTORY
# - Session is a "factory" for creating session instances
# - autoflush=False: does not automatically send changes to the DB (manual control)
# - autocommit=False: does not automatically commit (manual control)
# - future=True: uses the new SQLAlchemy 2.0 API
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def reset_chess_records(start_at_zero: bool = False) -> None:
    """
    Deletes all records and resets the ID sequence.
    - start_at_zero=False -> the sequence restarts at 1 (recommended)
    - start_at_zero=True -> the sequence restarts at 0 (uncommon, but possible)
    """
    with engine.begin() as conn:
        # Deletes all records
        conn.execute(text("TRUNCATE TABLE chess_records RESTART IDENTITY"))
        
        # Reset the ID sequence
        if start_at_zero:
            # Get the actual sequence name for 'chess_records.id'
            seq_name = conn.execute(
                text("SELECT pg_get_serial_sequence('chess_records', 'id')")
            ).scalar()

            if seq_name:
                # 1) Allow 0 at least
                conn.execute(text(f"ALTER SEQUENCE {seq_name} MINVALUE 1"))
                # 2) Restart the sequence so that the next id is 0
                conn.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
            
