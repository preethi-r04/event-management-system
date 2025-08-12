-- schema.sql
-- Create table for Event Management System
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT,
  venue TEXT,
  description TEXT
);

-- sample data
INSERT INTO events (title, date, time, venue, description) VALUES
('Orientation Session', '2025-08-20', '10:00', 'Auditorium A', 'Orientation for new students.'),
('Tech Talk: IoT', '2025-09-01', '15:30', 'Seminar Hall', 'Guest lecture on IoT applications.');
