from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sqlite3
from uuid import uuid4
from pathlib import Path

DB_PATH = os.getenv("SQLITE_PATH", "/data/appointments.db")
Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Appointment Service")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_conn()
# create table if not exists
conn.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY,
    name TEXT,
    date TEXT
)
""")
conn.commit()

class AppointmentIn(BaseModel):
    name: str | None = None
    date: str | None = None

class AppointmentOut(BaseModel):
    appointment_id: str
    name: str | None = None
    date: str | None = None

@app.post("/appointments", status_code=201, response_model=AppointmentOut)
def create_appointment(appt: AppointmentIn):
    if not appt.name:
        appt.name = "Unknown"
    if not appt.date:
        appt.date = "TBD"
    appt_id = str(uuid4())
    conn.execute("INSERT INTO appointments (id, name, date) VALUES (?, ?, ?)",
                 (appt_id, appt.name, appt.date))
    conn.commit()
    return {"appointment_id": appt_id, "name": appt.name, "date": appt.date}

@app.get("/appointments/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str):
    cur = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return {"appointment_id": row["id"], "name": row["name"], "date": row["date"]}
