import os
import logging
import psycopg2
from psycopg2 import sql, extras
from typing import Dict, Any, List, Optional
from functools import wraps

# Настройка логирования (как в задании)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Декоратор для обработки ошибок (оставляем как было)
def handle_db_errors(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except psycopg2.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper

class DatabaseManager:
    def __init__(self):
        # Получаем параметры подключения из переменных окружения (как требовалось)
        self.db_host = os.getenv('FSTR_DB_HOST', 'localhost')
        self.db_port = os.getenv('FSTR_DB_PORT', '5432')
        self.db_login = os.getenv('FSTR_DB_LOGIN', 'postgres')
        self.db_pass = os.getenv('FSTR_DB_PASS', 'password')
        self.db_name = os.getenv('FSTR_DB_NAME', 'pereval')
        self.conn = None

    # Остальные методы (connect, close) оставляем без изменений

    @handle_db_errors
    def add_pereval(self, pereval_data: Dict[str, Any], images_data: List[Dict[str, Any]],
                    activities: List[int]) -> Optional[int]:
        if not self.conn and not self.connect():
            logger.error("Cannot add pereval - no database connection")
            return None

        try:
            with self.conn.cursor() as cursor:
                # Сохраняем пользователя
                user = pereval_data['user']
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO users (email, phone, last_name, first_name, middle_name)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """),
                    (user['email'], user['phone'], user['fam'], user['name'], user.get('otc'))
                )
                user_id = cursor.fetchone()[0]

                # Сохраняем координаты
                coords = pereval_data['coords']
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO coords (latitude, longitude, height)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """),
                    (coords['latitude'], coords['longitude'], coords['height'])
                )
                coords_id = cursor.fetchone()[0]

                # Сохраняем уровень сложности
                level = pereval_data['level']
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO levels (winter, summer, autumn, spring)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """),
                    (level.get('winter', ''), level.get('summer', ''),
                     level.get('autumn', ''), level.get('spring', ''))
                )
                level_id = cursor.fetchone()[0]

                # Сохраняем перевал
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO pereval_added (
                            beauty_title, title, other_titles, connection,
                            user_id, coords_id, level_id, status
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING id
                    """),
                    (pereval_data['beautyTitle'], pereval_data['title'],
                     pereval_data['other_titles'], pereval_data['connect'],
                     user_id, coords_id, level_id, 'new')  # Устанавливаем статус 'new'
                )
                pereval_id = cursor.fetchone()[0]

                # Сохраняем изображения
                for image in images_data:
                    cursor.execute(
                        sql.SQL("""
                            INSERT INTO pereval_images (pereval_id, title, img_url)
                            VALUES (%s, %s, %s)
                        """),
                        (pereval_id, image['title'], image['img_url'])
                    )

                # Сохраняем виды деятельности
                if activities:
                    act_values = [(pereval_id, act_id) for act_id in activities]
                    extras.execute_values(
                        cursor,
                        "INSERT INTO pereval_activities (pereval_id, activity_id) VALUES %s",
                        act_values
                    )

                self.conn.commit()
                logger.info(f"Successfully added pereval with ID {pereval_id}")
                return pereval_id

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to add pereval: {e}")
            return None

    @handle_db_errors
    def get_pereval_by_id(self, pereval_id: int) -> Optional [Dict [str, Any]]:
        """Получает полные данные о перевале по ID"""
        if not self.conn and not self.connect():
            return None

        try:
            with self.conn.cursor() as cursor:
                # Основные данные перевала
                cursor.execute("""
                       SELECT pa.*, u.email, u.phone, u.last_name, u.first_name, u.middle_name,
                              c.latitude, c.longitude, c.height,
                              l.winter, l.summer, l.autumn, l.spring
                       FROM pereval_added pa
                       JOIN users u ON pa.user_id = u.id
                       JOIN coords c ON pa.coords_id = c.id
                       JOIN levels l ON pa.level_id = l.id
                       WHERE pa.id = %s
                   """, (pereval_id,))
                pereval = cursor.fetchone()

                if not pereval:
                    return None

                # Изображения перевала
                cursor.execute("""
                       SELECT title, img_url FROM pereval_images
                       WHERE pereval_id = %s
                   """, (pereval_id,))
                images = [{'title': row [0], 'img_url': row [1]} for row in cursor.fetchall()]

                # Виды деятельности
                cursor.execute("""
                       SELECT activity_id FROM pereval_activities
                       WHERE pereval_id = %s
                   """, (pereval_id,))
                activities = [row [0] for row in cursor.fetchall()]

                # Формируем ответ
                return {
                    'id': pereval [0],
                    'status': pereval [9],  # поле status
                    'beautyTitle': pereval [2],
                    'title': pereval [3],
                    'other_titles': pereval [4],
                    'connect': pereval [5],
                    'user': {
                        'email': pereval [10],
                        'phone': pereval [11],
                        'fam': pereval [12],
                        'name': pereval [13],
                        'otc': pereval [14]
                    },
                    'coords': {
                        'latitude': pereval [15],
                        'longitude': pereval [16],
                        'height': pereval [17]
                    },
                    'level': {
                        'winter': pereval [18],
                        'summer': pereval [19],
                        'autumn': pereval [20],
                        'spring': pereval [21]
                    },
                    'images': images,
                    'activities': activities
                }

        except Exception as e:
            logger.error(f"Error getting pereval {pereval_id}: {e}")
            return None

    @handle_db_errors
    def update_pereval(self, pereval_id: int, pereval_data: Dict [str, Any],
                       images_data: List [Dict [str, Any]], activities: List [int]) -> bool:
        """Обновляет данные перевала, если статус 'new'"""
        if not self.conn and not self.connect():
            return False

        try:
            with self.conn.cursor() as cursor:
                # Проверяем статус перевала
                cursor.execute("""
                       SELECT status FROM pereval_added WHERE id = %s
                   """, (pereval_id,))
                status = cursor.fetchone() [0]

                if status != 'new':
                    raise ValueError("Редактирование возможно только для записей со статусом 'new'")

                # Получаем ID связанных записей
                cursor.execute("""
                       SELECT coords_id, level_id FROM pereval_added WHERE id = %s
                   """, (pereval_id,))
                coords_id, level_id = cursor.fetchone()

                # Обновляем координаты
                cursor.execute("""
                       UPDATE coords SET latitude = %s, longitude = %s, height = %s
                       WHERE id = %s
                   """, (
                    pereval_data ['coords'] ['latitude'],
                    pereval_data ['coords'] ['longitude'],
                    pereval_data ['coords'] ['height'],
                    coords_id
                ))

                # Обновляем уровень сложности
                cursor.execute("""
                       UPDATE levels SET winter = %s, summer = %s, autumn = %s, spring = %s
                       WHERE id = %s
                   """, (
                    pereval_data ['level'].get('winter', ''),
                    pereval_data ['level'].get('summer', ''),
                    pereval_data ['level'].get('autumn', ''),
                    pereval_data ['level'].get('spring', ''),
                    level_id
                ))

                # Обновляем основные данные перевала
                cursor.execute("""
                       UPDATE pereval_added 
                       SET beauty_title = %s, title = %s, other_titles = %s, connection = %s
                       WHERE id = %s
                   """, (
                    pereval_data ['beautyTitle'],
                    pereval_data ['title'],
                    pereval_data ['other_titles'],
                    pereval_data ['connect'],
                    pereval_id
                ))

                # Удаляем старые изображения и добавляем новые
                cursor.execute("""
                       DELETE FROM pereval_images WHERE pereval_id = %s
                   """, (pereval_id,))

                for image in images_data:
                    cursor.execute("""
                           INSERT INTO pereval_images (pereval_id, title, img_url)
                           VALUES (%s, %s, %s)
                       """, (pereval_id, image ['title'], image ['img_url']))

                # Обновляем виды деятельности
                cursor.execute("""
                       DELETE FROM pereval_activities WHERE pereval_id = %s
                   """, (pereval_id,))

                if activities:
                    act_values = [(pereval_id, act_id) for act_id in activities]
                    extras.execute_values(
                        cursor,
                        "INSERT INTO pereval_activities (pereval_id, activity_id) VALUES %s",
                        act_values
                    )

                self.conn.commit()
                return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating pereval {pereval_id}: {e}")
            raise

    @handle_db_errors
    def get_perevals_by_email(self, email: str) -> List [Dict [str, Any]]:
        """Получает все перевалы пользователя по email"""
        if not self.conn and not self.connect():
            return []

        try:
            with self.conn.cursor() as cursor:
                # Находим все перевалы пользователя
                cursor.execute("""
                       SELECT pa.id, pa.title, pa.status, pa.date_added
                       FROM pereval_added pa
                       JOIN users u ON pa.user_id = u.id
                       WHERE u.email = %s
                       ORDER BY pa.date_added DESC
                   """, (email,))

                return [{
                    'id': row [0],
                    'title': row [1],
                    'status': row [2],
                    'date_added': row [3].isoformat() if row [3] else None
                } for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting perevals for email {email}: {e}")
            return []