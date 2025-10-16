import os
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Base de SQLAlchemy - De aquí heredarán los modelos (tablas)
Base = declarative_base()

# MODELO / TABLA: ChessRecord
#   - Representa un registro de partida con:
#       id  : clave primaria autoincremental
#       opponent : nombre del oponente (opcional, string)
#       result : 'Ganada' o 'Perdida' (string)
#       date : fecha de la partida (string, formato YYYY-MM-DD)
class ChessRecord(Base):
    __tablename__ = 'chess_records' # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opponent = Column(String)
    result = Column(String)  # 'Ganada' o 'Perdida' 
    date = Column(String)  # Store date as string for simplicity
    
    def __repr__(self):
        # Representación útil al imprimir objetos del modelo (debug/Logs)
        return f"<ChessRecord(id={self.id}, opponent='{self.opponent}', result='{self.result}', date='{self.date}')>"
    
# --- CONFIGURACION DE CONEXION A LA BASE DE DATOS
# IMPORTANTE: aquí estás usando PostgreSQL con usuario 'postgres'
# contraseña 'fireball967810211' y base de datos 'OnlineChessDB'
# Nota: mantener la contraseña en código no es seguro para producción 
# Se suele usar variable de entorno para producción
DATABASE_URL = "postgresql+psycopg2://postgres:fireball967810211@localhost:5432/OnlineChessDB"

# CREACIÓN DE ENGINE (motor de conexión a la BD)
#  - echo=False: no loguea todas las consultas SQL (True para debug)
#  - future=True: usa la nueva API 2.0 de SQLAlchemy
#  - pool_pre_ping=True: verifica conexiones antes de usarlas (evita errores por conexiones caídas)  
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# PRUEBA TEMPRANA DE CONEXIÓN
# - Intenta ejecutar un SELECT 1. Si hay problema de conexión/credenciales,
#   aquí fallará y verás el error claro al inicio
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

# CREACIÓN DE TABLAS
# - Crea las tablas definidas en los modelos si no existen.
# - En este caso, creará 'chess_records' según la clase ChessRecord
Base.metadata.create_all(engine)

# FABRICADOR DE SESIONES
# - Session es una "fábrica" para crear instancias de sesión
# - autoflush=False: no envía automáticamente cambios a la BD (control manual)
# - autocommit=False: no hace commit automáticamente (control manual)
# - future=True: usa la nueva API 2.0 de SQLAlchemy 
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) 