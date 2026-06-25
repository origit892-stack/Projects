from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from trading_ai.models import SignalStatus, TradeSignal


class Base(DeclarativeBase):
    pass


class SignalRecord(Base):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("symbol", "timeframe", "created_at", "pattern", name="uq_signal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    timeframe: Mapped[str] = mapped_column(String(16))
    pattern: Mapped[str] = mapped_column(String(64))
    direction: Mapped[str] = mapped_column(String(12))
    entry: Mapped[float] = mapped_column(Float)
    target: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    risk_reward: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default=SignalStatus.ACTIVE.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    chart_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)


class Database:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, future=True)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)

    def create_all(self) -> None:
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Session:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def save_signal(session: Session, signal: TradeSignal) -> bool:
    existing = (
        session.query(SignalRecord)
        .filter_by(symbol=signal.symbol, timeframe=signal.timeframe, created_at=signal.created_at, pattern=signal.pattern)
        .first()
    )
    if existing:
        return False

    session.add(
        SignalRecord(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            pattern=signal.pattern,
            direction=signal.direction.value,
            entry=signal.entry,
            target=signal.target,
            stop_loss=signal.stop_loss,
            risk_reward=signal.risk_reward,
            status=signal.status.value,
            created_at=signal.created_at,
            chart_path=signal.chart_path,
        )
    )
    return True


def update_active_signals(session: Session, symbol: str, current_price: float) -> None:
    active = session.query(SignalRecord).filter_by(symbol=symbol, status=SignalStatus.ACTIVE.value).all()
    for signal in active:
        if signal.direction == "LONG":
            if current_price >= signal.target:
                signal.status = SignalStatus.SUCCESS.value
                signal.closed_at = datetime.utcnow()
            elif current_price <= signal.stop_loss:
                signal.status = SignalStatus.FAILED.value
                signal.closed_at = datetime.utcnow()
        else:
            if current_price <= signal.target:
                signal.status = SignalStatus.SUCCESS.value
                signal.closed_at = datetime.utcnow()
            elif current_price >= signal.stop_loss:
                signal.status = SignalStatus.FAILED.value
                signal.closed_at = datetime.utcnow()
