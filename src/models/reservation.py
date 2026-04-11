# 予約（Reservation）に関するデータモデル定義モジュール

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text, TIMESTAMP, text
from sqlmodel import SQLModel, Field


class Reservation(SQLModel, table=True):
    __tablename__ = "reservations"
    id: Optional[int] = Field(default=None, primary_key=True)  # 主キー（自動採番）
    name: str  # 予約者名
    email: str  # メールアドレス
    date: datetime  # 予約日時
    message: str = Field(sa_column=Column(Text))  # メッセージ
    # レコード作成日時（データベース側で自動設定）
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    )
    # レコード更新日時（更新時にデータベース側で自動更新）
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )


class ReservationCreate(SQLModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    date: datetime = Field(nullable=False)
    message: str = Field(max_length=255)


class ReservationUpdate(SQLModel):
    name: str = Field(max_length=255, nullable=True)
    email: str = Field(max_length=255, nullable=True)
    date: datetime = Field(nullable=True)
    message: str = Field(max_length=255, nullable=True)
