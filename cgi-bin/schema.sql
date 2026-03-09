PRAGMA foreign_keys = ON;

-- ФАКУЛЬТЕТЫ
CREATE TABLE faculties (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    short_name TEXT,
    history TEXT,
    phone TEXT,
    email TEXT,
    description TEXT
);

-- КАФЕДРЫ
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id INTEGER NOT NULL,

    name TEXT NOT NULL,
    short_name TEXT,

    address TEXT,
    phone TEXT,
    email TEXT,

    description TEXT,

    FOREIGN KEY (faculty_id)
        REFERENCES faculties(faculty_id)
        ON DELETE CASCADE
);

-- СОТРУДНИКИ (преподаватели и администрация)
CREATE TABLE staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,

    faculty_id INTEGER,

    name TEXT NOT NULL,
    short_name TEXT,

    position TEXT NOT NULL,

    email TEXT,
    phone TEXT,

    is_teacher INTEGER DEFAULT 0,

    FOREIGN KEY (faculty_id)
        REFERENCES faculties(faculty_id)
);

-- ЧАСЫ ПРИЁМА
CREATE TABLE reception_hours (
    reception_id INTEGER PRIMARY KEY AUTOINCREMENT,

    staff_id INTEGER NOT NULL,

    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),
    time TEXT NOT NULL,

    FOREIGN KEY (staff_id)
        REFERENCES staff(staff_id)
        ON DELETE CASCADE
);

-- НАПРАВЛЕНИЯ ПОДГОТОВКИ
CREATE TABLE programs (
    program_id INTEGER PRIMARY KEY AUTOINCREMENT,

    department_id INTEGER NOT NULL,

    code TEXT NOT NULL,
    name TEXT NOT NULL,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE CASCADE
);

-- УЧЕБНЫЕ ГРУППЫ
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,

    program_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE,

    FOREIGN KEY (program_id)
        REFERENCES programs(program_id)
        ON DELETE CASCADE
);

-- ДИСЦИПЛИНЫ
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- АУДИТОРИИ
CREATE TABLE rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- ВРЕМЯ ПАР
CREATE TABLE time_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_no INTEGER NOT NULL UNIQUE,
    time TEXT NOT NULL
);

-- РАСПИСАНИЕ
CREATE TABLE schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,

    group_id INTEGER NOT NULL,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 1 AND 7),

    slot_id INTEGER NOT NULL,

    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,

    FOREIGN KEY (group_id)
        REFERENCES groups(group_id)
        ON DELETE CASCADE,

    FOREIGN KEY (slot_id)
        REFERENCES time_slots(slot_id),

    FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),

    FOREIGN KEY (teacher_id)
        REFERENCES staff(staff_id),

    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)
);