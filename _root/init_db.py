import hashlib

from utils import database


async def create_tables(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            """CREATE TABLE `message` (
                `id` bigint NOT NULL AUTO_INCREMENT,
                `from` bigint DEFAULT NULL,
                `to` bigint DEFAULT NULL,
                `on` datetime DEFAULT NULL,
                `message` text,
                PRIMARY KEY (`id`),
            KEY `to_from_on_idx` (`to`,`from`,`on`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;""")


async def sample_data(conn):
    async with conn.cursor() as cur:
        await cur.execute(
            f"""INSERT INTO users (login, password) 
                values ('admin', '{hashlib.sha3_256('password'.encode()).hexdigest()}');""")
        await conn.commit()


async def main(app):
    async with database(app):
        async with app['db'].acquire() as conn:
            await create_tables(conn)
            await sample_data(conn)
            conn.close()
