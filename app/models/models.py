from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
)
from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone, date
from sqlalchemy.types import Date, TIMESTAMP
import uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    relationship between users and expenses, income
    """

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    expenses = relationship(
        "Expenses",
        back_populates="users",
        passive_deletes=True,
    )

    tokens = relationship(
        "RefreshToken",
        back_populates="users",
        cascade="all, delete-orphan",
    )

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True


class Expenses(Base):
    """
    common table user -> expenses <- category, currency
    Fields:
        user_id
        category_id
        currency_id
        amount
        note
        expense_date
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("expenses_category.id", ondelete="SET NULL"),
        nullable=True,
    )
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(nullable=False)
    note: Mapped[str] = mapped_column(
        String(500), nullable=True, server_default=""
    )
    expense_date: Mapped[date] = mapped_column(Date)

    users = relationship("User", back_populates="expenses")
    categories = relationship("Category", back_populates="expenses")
    currencies = relationship("Currency", back_populates="expenses")


class Category(Base):
    """
    relationship category -> expanses
    """

    __tablename__ = "expenses_category"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    category_name: Mapped[str] = mapped_column()

    expenses = relationship(
        "Expenses", back_populates="categories", cascade="all, delete"
    )


class Currency(Base):
    """
    relationship currency -> expenses
    """

    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    code: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(50))
    symbol: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )

    expenses = relationship("Expenses", back_populates="currencies")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("null"),
    )

    users = relationship("User", back_populates="tokens")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
