-- Создание таблицы users
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100)
);

-- Создание таблицы coords
CREATE TABLE IF NOT EXISTS public.coords (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    height INTEGER NOT NULL
);

-- Создание таблицы levels
CREATE TABLE IF NOT EXISTS public.levels (
    id SERIAL PRIMARY KEY,
    winter VARCHAR(10),
    summer VARCHAR(10),
    autumn VARCHAR(10),
    spring VARCHAR(10)
);

-- Создание таблицы pereval_added
CREATE TABLE IF NOT EXISTS public.pereval_added (
    id SERIAL PRIMARY KEY,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    beauty_title VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    other_titles VARCHAR(255),
    connection TEXT, -- Изменили имя с 'connect' на 'connection'
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    coords_id INTEGER REFERENCES coords(id) ON DELETE CASCADE,
    level_id INTEGER REFERENCES levels(id) ON DELETE CASCADE,
    status VARCHAR(10) NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'pending', 'accepted', 'rejected'))
);

-- Создание индекса для статуса (исправленный синтаксис)
CREATE INDEX IF NOT EXISTS idx_status ON pereval_added (status);

-- Создание таблицы pereval_images
CREATE TABLE IF NOT EXISTS public.pereval_images (
    id SERIAL PRIMARY KEY,
    pereval_id INTEGER REFERENCES pereval_added(id) ON DELETE CASCADE,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255),
    img_url TEXT NOT NULL
);

-- Создание таблицы spr_activities_types
CREATE TABLE IF NOT EXISTS public.spr_activities_types (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);

-- Создание таблицы pereval_activities
CREATE TABLE IF NOT EXISTS public.pereval_activities (
    pereval_id INTEGER REFERENCES pereval_added(id) ON DELETE CASCADE,
    activity_id INTEGER REFERENCES spr_activities_types(id) ON DELETE CASCADE,
    PRIMARY KEY (pereval_id, activity_id)
);