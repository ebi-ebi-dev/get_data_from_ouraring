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

## 各指標と作成されるCSV
本リポジトリでは下記の指標をCSVとして出力するソースを用意しています。
|指標|スクリプト名|出力されるCSV|
----|----|----
|daily_activity|daily_activity.py|yyyy-MM-dd\~yyyy-MM-dd.csv<br>yyyy-MM-dd\~yyyy-MM-dd_per5min.csv|
|daily_readiness|daily_readiness.py|daily_readiness_yyyy-MM-dd~yyyy-MM-dd.csv|
|daily_sleep|daily_sleep.py|daily_sleep_yyyy-MM-dd~yyyy-MM-dd.csv|
|daily_spo2|daily_spo2.py|daily_spo2_yyyy-MM-dd~yyyy-MM-dd.csv|
|sleep_time|sleep_time.py|sleep_time_yyyy-MM-dd~yyyy-MM-dd.csv|
|sleep|sleep.py|sleep_yyyy-MM-dd~yyyy-MM-dd.csv<br>sleep_hartrate_and_hrv_yyyy-MM-dd~yyyy-MM-dd.csv<br>sleep_movement30sec_yyyy-MM-dd~yyyy-MM-dd.csv<br>sleep_sleepphase5min_yyyy-MM-dd~yyyy-MM-dd.csv|
|workout|workout.py|workout_yyyy-MM-dd~yyyy-MM-dd.csv|

それぞれの指標の意味はこちらの記事が非常に参考になります。

[Oura API V2: エンドポイントとデータの詳細解説](https://the-learning-canvas.com/2023/12/05/oura-api-v2-endpoint/)

このうち、指標に紐づく下記のデータに関してはデータ分析での利用を想定して加工を行い、別のCSVファイルとして出力されます。
* daily_activity
    * class_5_min
* sleep
    * heart_rate/items
    * hrv/items（heart_rate/itemと同じCSVに包含）
    * movement_30_sec
    * sleep_phase_5_min

## 加工の例
例えば、daily_activityのclass_5_minは日中の活動状態を5分間隔で0~5の番号の**羅列**で表現されます。
```
class_5_min: "001122334455"
```
公式によると、各番号が意味するところは以下です。
|番号|ステータス|
|----|----|
|0|non wear|
|1|rest|
|2|inactive|
|3|low activity|
|4|medium activity|
|5|high activity|

したがって、下記のように加工しています。

|id|start_recording|end_recording|status_number|
|----|----|----|----|
|a1b2c3d4|2024-08-02 00:00:00|2024-08-02 00:05:00|0|
|a1b2c3d4|2024-08-02 00:05:00|2024-08-02 00:10:00|0|
|a1b2c3d4|2024-08-02 00:10:00|2024-08-02 00:15:00|1|
|a1b2c3d4|2024-08-02 00:15:00|2024-08-02 00:20:00|1|
|a1b2c3d4|2024-08-02 00:20:00|2024-08-02 00:25:00|2|
|a1b2c3d4|2024-08-02 00:25:00|2024-08-02 00:30:00|2|
|a1b2c3d4|2024-08-02 00:30:00|2024-08-02 00:35:00|3|
|a1b2c3d4|2024-08-02 00:35:00|2024-08-02 00:40:00|3|
|a1b2c3d4|2024-08-02 00:40:00|2024-08-02 00:45:00|4|
|a1b2c3d4|2024-08-02 00:45:00|2024-08-02 00:50:00|4|
|a1b2c3d4|2024-08-02 00:50:00|2024-08-02 00:55:00|5|
|a1b2c3d4|2024-08-02 00:55:00|2024-08-02 01:00:00|5|
...

こちらを「yyyy-MM-dd~yyyy-MM-dd_per5min.csv」として出力します。

## ステータス番号のマスタデータ
outputフォルダに各status_numberとその意味の対応表を用意しています。
分析する際は、下記CSVの**idカラムを紐づけて**分析してみてください。
|CSV|対応するマスタデータ|
|----|----|
|yyyy-MM-dd~yyyy-MM-dd_per5min.csv|M_dailyactivity_class5min.csv|
|sleep_movement30sec_yyyy-MM-dd~yyyy-MM-dd.csv|M_sleep_movement30sec.csv|
|sleep_sleepphase5min_yyyy-MM-dd~yyyy-MM-dd.csv|M_sleep_sleepphase5min.csv|

