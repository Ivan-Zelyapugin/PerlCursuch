PRAGMA foreign_keys = ON;

--  Сотрудники
CREATE TABLE IF NOT EXISTS people (
  person_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  short     TEXT NOT NULL,
  role      TEXT NOT NULL,
  email     TEXT,
  phone     TEXT
);

-- Часы приёма (
CREATE TABLE IF NOT EXISTS reception_hours (
  hour_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  weekday   INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
  time      TEXT NOT NULL,     
  note      TEXT NOT NULL DEFAULT '',
  FOREIGN KEY (person_id) REFERENCES people(person_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Учебные группы
CREATE TABLE IF NOT EXISTS groups (
  group_id INTEGER PRIMARY KEY,
  name     TEXT NOT NULL UNIQUE,
  track    TEXT NOT NULL       
);

-- Справочник преподавателей 
CREATE TABLE IF NOT EXISTS teachers (
  teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL UNIQUE
);

-- Справочник дисциплин
CREATE TABLE IF NOT EXISTS subjects (
  subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL UNIQUE
);

-- Справочник аудиторий
CREATE TABLE IF NOT EXISTS rooms (
  room_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name    TEXT NOT NULL UNIQUE
);

-- Слоты времени пар 
CREATE TABLE IF NOT EXISTS time_slots (
  slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pair_no INTEGER NOT NULL UNIQUE CHECK (pair_no BETWEEN 1 AND 20),
  time    TEXT NOT NULL
);

-- Расписание
CREATE TABLE IF NOT EXISTS schedule_entries (
  entry_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id   INTEGER NOT NULL,
  weekday    INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
  pair_no    INTEGER NOT NULL,
  subject_id INTEGER NOT NULL,
  teacher_id INTEGER NOT NULL,
  room_id    INTEGER NOT NULL,
  note       TEXT NOT NULL DEFAULT '',
  FOREIGN KEY (group_id)   REFERENCES groups(group_id)   ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (room_id)    REFERENCES rooms(room_id)     ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (pair_no)    REFERENCES time_slots(pair_no)ON UPDATE CASCADE ON DELETE RESTRICT,
  UNIQUE(group_id, weekday, pair_no)
);

CREATE INDEX IF NOT EXISTS idx_reception_person   ON reception_hours(person_id);
CREATE INDEX IF NOT EXISTS idx_schedule_group_day ON schedule_entries(group_id, weekday);