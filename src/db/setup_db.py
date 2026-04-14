# データベースの初期セットアップスクリプト
# テーブルの作成と初期データの投入を行う

from sqlalchemy import text

from database import create_db_and_tables, engine


# データベースに接続し、reservationsテーブルが存在するか確認する
with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES LIKE 'reservations'")).fetchone()

# テーブルが存在しない場合は作成する
if result is None:
    create_db_and_tables()
    print("テーブル reservations が作成されました")
else:
    print("テーブル reservations はすでに存在します")
