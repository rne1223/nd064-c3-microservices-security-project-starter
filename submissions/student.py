from typing import Optional, NamedTuple

from aiopg.connection import Connection

## Added SQLAlchemy ORM  boiler plate
from sqlalchemy as sa 
metadata = sa.MetaData()
tbl = sa.Table('students', metadata,
               sa.Column('id', sa.Integer, primary_key=True),
               sa.Column('val', sa.String(255)))

class Student(NamedTuple):
    id: int
    name: str

    @classmethod
    def from_raw(cls, raw: tuple):
        return cls(*raw) if raw else None

    @staticmethod
    async def get(conn: Connection, id_: int):
        async with conn.cursor() as cur:
            await cur.execute(
                'SELECT id, name FROM students WHERE id = %s',
                (id_,),
            )
            r = await cur.fetchone()
            return Student.from_raw(r)

    @staticmethod
    async def get_many(conn: Connection, limit: Optional[int] = None,
                       offset: Optional[int] = None):
        q = 'SELECT id, name FROM students'
        params = {}
        if limit is not None:
            q += ' LIMIT + %(limit)s '
            params['limit'] = limit
        if offset is not None:
            q += ' OFFSET + %(offset)s '
            params['offset'] = offset
        async with conn.cursor() as cur:
            await cur.execute(q, params)
            results = await cur.fetchall()
            return [Student.from_raw(r) for r in results]

    @staticmethod
    async def create(conn: Connection, name: str):
        # q = ("INSERT INTO students (name) "
        #      "VALUES ('%(name)s')")
        # params = {'name':name}

        ## Using ORM to medigate sql injection attacks
        async with conn.cursor() as cur:
            await cur.execute(tbl.insert().values(val=name))


