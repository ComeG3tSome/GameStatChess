import os
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ChessRecord(Base):
    __tablename__ = 'chess_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opponent = Column(String)
    result = Column(String)  # 'Ganada' o 'Perdida' 
    date = Column(String)  # Store date as string for simplicity
    
    def __repr__(self):
        return f"<ChessRecord(id={self.id}, opponent='{self.opponent}', result='{self.result}', date='{self.date}')>"
    
# --- PostgreSQL with hardcoded password
DATABASE_URL = "postgresql+psycopg2://postgres:fireball967810211@localhost:5432/OnlineChessDB"

    
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) 