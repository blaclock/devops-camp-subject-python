### パッケージインストール
```
pip3 install fastapi uvicorn sqlmodel pymysql python-dotenv
```


### データベースの作成
```
mysql -u root -p -e "CREATE DATABASE python_subject;"
```

### テーブルの作成
ルートディレクトリで下記のコマンドを実行
```
PYTHONPATH=src python3 -m db.setup_db
```

### API動作確認
```
curl -X POST 'http://localhost:8000/reservations/' \
  -H 'Content-Type: application/json' \
  -d '{"name":"鈴木一郎","email":"test_mail@test.com","date":"2025-01-01T10:00:00","message":"テスト予約です"}'
```
