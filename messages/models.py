from utils import select, last_id


class Message:
    @staticmethod
    async def get_by_receiver_and_sender(conn, receiver_id, sender_id, page=0, page_size=100):
        offset = page * page_size
        profiles = await select(
            conn,
            """SELECT * FROM message 
            WHERE 
                (`to`=%(to)s AND `from`=%(from)s) 
                OR 
                (`to`=%(from)s AND `from`=%(to)s)  
            ORDER BY `on` DESC LIMIT %(limit)s OFFSET %(offset)s;""",
            {'to': int(receiver_id), 'from': int(sender_id), 'limit': page_size, 'offset': offset})
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
