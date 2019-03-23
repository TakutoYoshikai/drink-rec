# drink-rec

# 使い方
ライブラリをインストール
```
pip install -r requirements.txt
```
ドリンク情報のスクレイピング（現段階ではサントリーのみ）
画像とドリンク情報のjsonをダウンロードします
```
python scraping.py
```

ダウンロードした画像のリサイズ
```
python image.py
```

各種apiの起動方法

```
gunicorn -b 0.0.0.0:3000 <pythonのファイル名拡張子抜き>:app
```

herokuのデプロイ用にドリンク情報と12種類の画像のセットは一時的にgit管理しています
