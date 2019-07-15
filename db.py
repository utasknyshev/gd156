from typing import Optional, List, Tuple
from time import sleep

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy.exc import OperationalError

from settings import Settings
from models import Base, Calculation


CONNECTION_TRIES = 3
TRIES_TIMEOUT = 1


class DBError(Exception):
    pass


class DatabaseHolder:

    def __init__(self, connection_string: Optional[str] = None):
        super().__init__()

        if connection_string is None:
            connection_string = '{engine}://{user}:{password}@{host}:{port}/{base}'.format(
                **Settings.conf['database'],
            )

        self.db = self.connect(connection_string)
        self.session_factory = sessionmaker()
        self.session_factory.configure(bind=self.db)

    def push(self, data: List[Tuple[float, float, float, float, bool]]) -> None:
        session = self.session_factory()

        try:
            session.add_all((
                Calculation(x=x, y=y, z=z, t=t, mode=mode) for x, y, z, t, mode in data
            ))
            session.commit()
        except Exception as error:
            raise DBError('DB error on push: {}'.format(error))

    def get_last_calculation(self) -> Optional[Tuple[float, float, float, float, bool]]:
        session = self.session_factory()

        try:
            fields = ['x', 'y', 'z', 't', 'mode']
            calculation = session.query(Calculation).options(
                load_only(*fields)
            ).order_by(
                desc(Calculation.t)
            ).first()

            if calculation:
                return calculation.x, calculation.y, calculation.z, calculation.t, calculation.mode
            return None
        except Exception as error:
            raise DBError('DB error on select: {}'.format(error))

    def clear(self) -> None:
        session = self.session_factory()

        try:
            session.query(Calculation).delete()
            session.commit()
        except Exception as error:
            raise DBError('DB error on push: {}'.format(error))

    def create_database(self) -> None:
        for tries in range(CONNECTION_TRIES):
            try:
                Base.metadata.create_all(self.db)
            except OperationalError:
                sleep(TRIES_TIMEOUT)
            else:
                break
        else:
            raise DBError('Database creation failed')

    def get_session(self):
        return self.session_factory()

    @staticmethod
    def connect(connection_string: str):
        for tries in range(CONNECTION_TRIES):
            try:
                return create_engine(
                    connection_string,
                    echo=False,
                    pool_pre_ping=True,
                )
            except OperationalError:
                sleep(TRIES_TIMEOUT)
        else:
            raise DBError('DB connection error')
