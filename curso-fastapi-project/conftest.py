import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from app.main import app
from db import get_session

#Se usa una custom base de datos para pruebas

sqlite_name = "db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread":False},
                        poolclass=StaticPool)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session: #creando nueva sesión con motor de prueba
        yield session

    SQLModel.metadata.drop_all(engine) #para limpiar memoria y evitar que hayan datos en la base


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
















