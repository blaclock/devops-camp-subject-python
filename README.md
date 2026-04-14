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
curl -X POST "http://localhost:8000/reservations/" \
  -H "Content-Type: application/json" \
  -d '{"name":"鈴木二郎","email":"test2_mail@test.com","date":"2026-01-01T10:00:00","status":"pending","message":"テスト予約2です"}'
```

### 静的解析

#### Flakeの実行
````
python3 -m flake8 src/
````

#### Blackの実行
````
python3 -m black src/
````

#### mypyの実行
````
python3 -m mypy src/
````

### 自動テスト

#### 単体テスト
````
python3 -m pytest tests/unit/ -v --html=report.html
````

#### 結合テスト
````
python3 -m pytest tests/integration/ -v --html=report.html
````
