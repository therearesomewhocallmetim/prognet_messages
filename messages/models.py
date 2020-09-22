from utils import select, last_id


class Message:
    @staticmethod
    async def get_by_receiver_and_sender(conn, receiver_id, sender_id, page=0, page_size=100):
        offset = page * page_size
        profiles = await select(
            conn,
            "SELECT * FROM message WHERE `to`=%s AND `from`=%s ORDER BY `on` DESC LIMIT %s OFFSET %s;",
            [int(receiver_id), int(sender_id), page_size, offset])
        return profiles


    @staticmethod
    async def save(conn, data):
        statement = """
            INSERT INTO message 
                (`from`, `to`, `on`, `message`)
            values 
                (%(from)s, %(to)s, NOW(), %(message)s)
            """

        async with conn.cursor() as cur:
            await cur.execute(
                statement, args=data)
