import sqlalchemy
from sqlalchemy import insert, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/shop_db")

class CRUD:

    session = sessionmaker(engine)()

    def save(self):
        table = self.__table__
        data = self.__dict__
        data = {k:v for k,v in data.items() if v != None}
        insert_query = insert(table).values(data)
        self.session.execute(insert_query)
        self.session.commit()

