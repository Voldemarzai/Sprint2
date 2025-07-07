-- Виды деятельности
INSERT INTO public.spr_activities_types (id, title) VALUES
(1, 'пешком'),
(2, 'лыжи'),
(3, 'катамаран'),
(4, 'байдарка'),
(5, 'плот'),
(6, 'сплав'),
(7, 'велосипед'),
(8, 'автомобиль'),
(9, 'мотоцикл'),
(10, 'парус'),
(11, 'верхом');

-- Пример перевала (для тестов)
DO $$
DECLARE
    user_id INT;
    coords_id INT;
    level_id INT;
    pereval_id INT;
BEGIN
    -- Добавляем пользователя
    INSERT INTO public.users (email, phone, last_name, first_name, middle_name)
    VALUES ('test@example.com', '79001234567', 'Иванов', 'Иван', 'Иванович')
    RETURNING id INTO user_id;

    -- Добавляем координаты
    INSERT INTO public.coords (latitude, longitude, height)
    VALUES (45.3842, 7.1525, 1200)
    RETURNING id INTO coords_id;

    -- Добавляем уровень сложности
    INSERT INTO public.levels (winter, summer, autumn, spring)
    VALUES ('', '1А', '1А', '')
    RETURNING id INTO level_id;

    -- Добавляем перевал
    INSERT INTO public.pereval_added (
        beauty_title, title, other_titles, connect,
        user_id, coords_id, level_id, status
    )
    VALUES (
        'пер. ', 'Пхия', 'Триев', '',
        user_id, coords_id, level_id, 'accepted'
    )
    RETURNING id INTO pereval_id;

    -- Добавляем изображения
    INSERT INTO public.pereval_images (pereval_id, title, img_url)
    VALUES
        (pereval_id, 'Седловина', 'https://example.com/sedlovina.jpg'),
        (pereval_id, 'Подъем', 'https://example.com/podem.jpg');

    -- Добавляем виды деятельности
    INSERT INTO public.pereval_activities (pereval_id, activity_id)
    VALUES
        (pereval_id, 1),
        (pereval_id, 2);
END $$;