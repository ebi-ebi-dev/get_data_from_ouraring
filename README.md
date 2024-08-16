# get_data_from_ouraring

oura ringから特定期間のデータを抽出するPythonスクリプトです。
必要なライブラリは適宜インストールしてください。

## 使い方
```
python .\daily_activity.py 
    -configfile_path "C:/Workspace/python/oura_ring/config/config.ini" 
    -start_date 2024-08-01 
    -end_date 2024-08-10 
    -output_path "C:/Workspace/python/oura_ring/output"
```
* cofigfile_path
ouraringのデータへアクセスるためのAPIアクセストークン及び、ログ情報を出力するパスを記載したコンフィグファイルのパスを指定します。
書き方はconfig/template.iniをご覧ください。「XXXXXX…」の部分にアクセストークンを記載ください。

* start_date/end_date
「yyyy-MM-dd」の書式でデータを取得する範囲を指定します。
APIの都合で、start_date + 1～end_dateまでのデータを取得します。

* output_path
取得したデータをCSVとして吐き出すための出力先を指定します。