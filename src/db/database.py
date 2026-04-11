# データベース接続の設定とセッション管理を行うモジュール

import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からデータベース接続情報を取得（デフォルト値付き）
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "python_subject")

# MySQLへの接続URLを組み立てる（pymysqlドライバを使用）
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# SQLAlchemyエンジンを作成（データベースへの接続プールを管理する）
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    """SQLModelで定義された全テーブルをデータベースに作成する"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPIの依存性注入で使用するセッションジェネレータ"""
    with Session(engine) as session:
        yield session
