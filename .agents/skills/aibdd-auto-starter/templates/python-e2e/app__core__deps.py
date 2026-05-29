from sqlalchemy.orm import Session, sessionmaker

_session_factory: sessionmaker | None = None


def set_session_factory(factory: sessionmaker) -> None:
    global _session_factory
    _session_factory = factory


def get_db():
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    session: Session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
