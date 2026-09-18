import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

import security
from main import app


@pytest.fixture()
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[security.get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()