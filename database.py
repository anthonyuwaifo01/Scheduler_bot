"""
Simple Database for MVP Scheduler Bot
Handles all SQLite database operations
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name='bookings.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def create_appointment(self, telegram_id: int, service: str, date: str, 
                          time: str, name: str, phone: str) -> int:
        """Create new appointment and return ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO appointments (telegram_id, name, phone, service, date, time, status)
                VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
            ''', (telegram_id, name, phone, service, date, time))
            
            appointment_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created appointment #{appointment_id} for user {telegram_id}")
            return appointment_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating appointment: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_appointments(self, telegram_id: int) -> List[Dict]:
        """Get all upcoming appointments for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM appointments
            WHERE telegram_id = ? AND date >= ? AND status = 'confirmed'
            ORDER BY date, time
        ''', (telegram_id, today))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return appointments
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Get all appointments for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM appointments
            WHERE date = ? AND status = 'confirmed'
            ORDER BY time
        ''', (date,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return appointments
    
    def get_booked_slots(self, date: str) -> List[tuple]:
        """Get all booked time slots for a date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT time, service FROM appointments
            WHERE date = ? AND status = 'confirmed'
        ''', (date,))
        
        slots = cursor.fetchall()
        conn.close()
        
        return [(row['time'], row['service']) for row in slots]
    
    def is_slot_available(self, date: str, time: str, duration: int, 
                         booked_slots: List[tuple]) -> bool:
        """Check if a time slot is available"""
        slot_time = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
        slot_end = slot_time + timedelta(minutes=duration)
        
        # Service durations
        service_durations = {
            'haircut': 30,
            'beard': 20,
            'color': 90,
            'style': 45
        }
        
        for booked_time_str, booked_service in booked_slots:
            booked_time = datetime.strptime(f"{date} {booked_time_str}", '%Y-%m-%d %H:%M')
            booked_duration = service_durations.get(booked_service, 30)
            booked_end = booked_time + timedelta(minutes=booked_duration)
            
            # Check for time overlap
            if (slot_time < booked_end and slot_end > booked_time):
                return False
        
        return True