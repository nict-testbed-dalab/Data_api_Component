# Data_api_Component
データ抽出取得機能

## 概要
WebGISアプリで利用するため、データベースに登録されているデータを抽出して取得し、GeoJson形式などに整形をして返却するコンポーネントです。

### データ取得API名一覧
- 人流データ
- アメダスデータ
- 人流データ（存在日付取得）
- アメダス前処理データ
- ごみ収集車前処理データ


### 人流データ
リクエストパラメータに記入された地図の領域と日時などに該当する人流データを取得し、GeoJsonとして返却する機能。

  * API名：peopleFlowData

  * URL:/api/t_people_flow_data

  * 引数  
 
|引数|説明|フォーマット|例|
| ---- | ---- | ---- | ---- |
|point1|領域における北西の位置情報|カンマ区切りの数値（経度,緯度）|139.4,35.7|
|point2|領域における北東の位置情報|カンマ区切りの数値（経度,緯度）|139.5,35.75|
|point3|領域における南東の位置情報|カンマ区切りの数値（経度,緯度）|139.6,35.8|
|point4|領域における南西の位置情報|カンマ区切りの数値（経度,緯度）|139.3,35.85|
|currentDate|対象とする年月日時分秒（日以下は省略可能）|YYYYMMDDHH24MISS（DD以下は省略可能）|20180404|


  * 取得処理
1. 人流データテーブルのlocationをX,Yを入れ替えて生成したgeometryが、リクエストパラメータのpoint_1,point_2,point_3,point_4で囲まれた領域内である。（CRSは4326）

2. 人流データテーブルのdatetimeがリクエストパラメータcurrentDateと一致する。ただし、リクエストパラメータcurrentDateの桁数（文字列長さ）と、比較するdatetimeの桁数（左から）は同一にする。

3. リクエストパラメータdeviceが指定された場合、人流データテーブルのdeviceと一致する。


  * 返却値（GeoJSON形式）

type：FeatureCollection

featuresの内容

|項目名|内容|
| ---- | ---- |
|geometry|人流データテーブルのlocation（経度,緯度に入れ替えて出力）|
|propertie|下記内容|

|項目名|内容|
| ---- | ---- |
|id|人流データテーブルのpeople_flow_base_id|
|people_flow_base_id|人流データテーブルのpeople_flow_base_id|
|device|人流データテーブルのdevice|
|rssi|人流データテーブルのrssi|
|datetime|人流データテーブルのdatetime|

リクエストパラメータエラーまたはDBエラーの場合は空欄のJSONを返却する

<BR>
<BR>

### アメダスデータ
リクエストパラメータに記入された地図の領域と日時に該当するアメダスデータを取得し、GeoJsonとして返却する機能。

  * API名：amedasData

  * URL:/api/t_amedas_data

  * 引数  
 
|引数|説明|フォーマット|例|
| ---- | ---- | ---- | ---- |
|point1|領域における北西の位置情報|カンマ区切りの数値（経度,緯度）|139.4,35.7|
|point2|領域における北東の位置情報|カンマ区切りの数値（経度,緯度）|139.5,35.75|
|point3|領域における南東の位置情報|カンマ区切りの数値（経度,緯度）|139.6,35.8|
|point4|領域における南西の位置情報|カンマ区切りの数値（経度,緯度）|139.3,35.85|
|currentDate|対象とする年月日時分|YYYYMMDDHH24MI|202201271512|


  * 取得処理

  下記は同一クエリ文ではなく、それぞれ順次実行する。

  1. アメダス観測所テーブルのlocationがリクエストパラメータのpoint_1,point_2,point_3,point_4で囲まれた領域内（CRSは4326）であるデータを取得。

  2. アメダスデータテーブルのprefNumberが、上記１．で取得したprefNumberであり、かつdatetimeがリクエストパラメータのcurrentDateと一致するデータを取得<BR>
　　・datetimeは10分刻であるため、currentDateの最後の１桁目を無視し０に変換して等号させる


  * 返却値（GeoJSON形式）

type：FeatureCollection

featuresの内容

|項目名|内容|
| ---- | ---- |
|geometry|アメダス観測所テーブルのlocation（経度,緯度に入れ替えて出力）|
|propertie|下記内容|

|項目名|内容|
| ---- | ---- |
|prefNumber       |アメダス観測所テーブルの地域コード|
|altitude         |アメダス観測所テーブルの高度|
|type             |アメダス観測所テーブルの種別|
|elems            |アメダス観測所テーブルの属性値|
|kjName           |アメダス観測所テーブルの漢字名|
|knName           |アメダス観測所テーブルのカタカナ名|
|enName           |アメダス観測所テーブルの英名|
|datetime         |アメダスデータテーブルのデータ取得日時|
|observationNumber|アメダスデータテーブルのデータ観測値コード|
|pressure         |アメダスデータテーブルの現地気圧|
|normalPressure   |アメダスデータテーブルの海面更正気圧|
|temp             |アメダスデータテーブルの気温|
|humidity         |アメダスデータテーブルの湿度|
|sun10m           |アメダスデータテーブルの１０分間日射時間|
|sun1h            |アメダスデータテーブルのタ１時間日射時間|
|precipitation10m |アメダスデータテーブルの前１０分間降水量|
|precipitation1h  |アメダスデータテーブルの前１時間降水量|
|precipitation3h  |アメダスデータテーブルの前３時間降水量|
|precipitation24h |アメダスデータテーブルの前２４時間降水量|
|windDirection    |アメダスデータテーブルの風向|
|wind             |アメダスデータテーブルの風速|
|maxTempTime      |アメダスデータテーブルのこの時間までの日最高気温が出た時刻|
|maxTemp          |アメダスデータテーブルのこの時間までの日最高気温|
|minTempTime      |アメダスデータテーブルのこの時間までの日最低気温が出た時刻|
|minTemp          |アメダスデータテーブルのこの時間までの日最低気温|
|gustTime         |アメダスデータテーブルの日最大風の時刻|
|gustDirection    |アメダスデータテーブルの日最大風速の風向|
|gust             |アメダスデータテーブルの日最大風速|
|snow             |アメダスデータテーブルの積雪深|
|snow1h           |アメダスデータテーブルの１時間降雪量|
|snow3h           |アメダスデータテーブルの３時間降雪量|
|snow6h           |アメダスデータテーブルの６時間降雪量|
|snow12h          |アメダスデータテーブルの１２時間降雪量|
|snow24h          |アメダスデータテーブルの２４時間降雪量|


リクエストパラメータエラーまたはDBエラーの場合は空欄のJSONを返却する

<BR>
<BR>

### 人流データの存在日付
データベースに登録されている人流データの日付と該当する場所を取得し、Jsonとして返却する機能。

  * API名：peopleExistDate

  * URL:/api/t_people_exist_date


  * 引数  
   なし

  * 取得処理

      人流データテーブルに人流ベーステーブルを外部結合（キー：people_flow_base_id）し、datetimeとplaceで集約する。

  * 返却値

|項目名|内容|
| ---- | ---- |
|t_people_flow_dataのdatetime（フォーマット：YYYYMMDD)|該当するt_people_flow_base_datのplace|


リクエストパラメータエラーまたはDBエラーの場合は空欄のJSONを返却する

<BR>
<BR>

### アメダス前処理データ
データベースに登録されている人流データの日付と該当する場所を取得し、Jsonとして返却する機能。

  * API名：peopleExistDate

  * URL:/api/t_preprocessing_amedas_data

  * 引数  

|引数|説明|フォーマット|例|
| ---- | ---- | ---- | ---- |
|target_data|t_amedas_dataのカラム名|英数字|precipitation24h、tempなど|
|point1|領域における北西の位置情報|カンマ区切りの数値（経度,緯度）|139.4,35.7|
|point2|領域における北東の位置情報|カンマ区切りの数値（経度,緯度）|139.5,35.75|
|point3|領域における南東の位置情報|カンマ区切りの数値（経度,緯度）|139.6,35.8|
|point4|領域における南西の位置情報|カンマ区切りの数値（経度,緯度）|139.3,35.85|
|start_date|対象とする開始日時|YYYYMMDDHH24MI|202201271512|
|end_date|対象とする終了日時|YYYYMMDDHH24MI|202201271512|
|granularity |時間粒度（数値を含む）|英数字|5minutes, 10second（補間）、1year, 1month, 5day, 2hour（集約）|
|proc_type|前処理の方法|英数字|spline、linear（補間）、avg, max, min, sum（集約）|
|center_point|地図の中心座標（ファイル読み込み時のUIへの復元用）|カンマ区切りの数値（経度,緯度）|139.766,35.681|
|zoom_level|地図のズーム値（ファイル読み込み時のUIへの復元用）|数値|13.1|
|pitch|地図の仰俯角度（ファイル読み込み時のUIへの復元用）|数値|55.02|
|bearing|地図の回転角度（ファイル読み込み時のUIへの復元用）|数値|36.8|


  * 取得処理

1. 入力チェック
    - 上記必須項目の必須チェック
    - 時間粒度および前処理の方法が、指定された文字列であるか
    - 前処理の方法と時間粒度の組み合わせが正しいか（前処理の方法が「集約」の場合、時間粒度が「秒」でないこと）
    - カラム名がテーブルに存在するものであるか

2. 前処理の方法に該当するユーザ定義関数を指定したSQLクエリを実行する
    
    ユーザ定義関数は、「アメダスデータ向け補間処理関数」または「アメダスデータ向け集約処理関数」
   
   ユーザ定義関数に渡す「前処理の方法」は、リサンプル処理に該当する文字列に変換する

3. SQLクエリ結果から取得したデータを整形して返却

   形式は返却値の通り。


  * 返却値

|項目名|内容|
| ---- | ---- |
|start_date|前処理期間の開始時刻（ファイル読み込み時のUIへの復元用） |
|end_date|前処理期間の終了時刻（ファイル読み込み時のUIへの復元用） |
|map_center|地図の中心座標（ファイル読み込み時のUIへの復元用）|
|map_zoom|地図のズーム値（ファイル読み込み時のUIへの復元用）|
|map_pitch|地図の仰俯角度（ファイル読み込み時のUIへの復元用）|
|map_bearing|地図の回転角度（ファイル読み込み時のUIへの復元用）|
|granularity |時間粒度（ファイル読み込み時のUIへの復元用）|
|proc_type|前処理方法（ファイル読み込み時のUIへの復元用）|
|target_data|前処理対象のデータ（ファイル読み込み時のUIへの復元用）|
|data_array|下記の内容の通り（配列）|

|項目名|内容|
| ---- | ---- |
|type|FeatureCollection|
|features|下記の内容の通り|

|項目名|内容|
| ---- | ---- |
|geometry|type：Point<BR>coordinates：観測所の座標配列（配列であるが観測所のため固定）|
|properties| id： アメダス観測所のアメダス地点コード<BR>kjname：アメダス観測所の名称<BR>datetime:時間粒度による時刻の配列<BR>target_dataで指定したカラム名：該当時刻の前処理済みデータ配列|


・リクエストパラメータエラーの場合

  リクエストパラメータのエラーメッセージを 「{"error":メッセージ内容}」として返却する。

・DBエラーの場合

  空欄のJSONを返却する

<BR>
<BR>

### ごみ収集車前処理データ
リクエストパラメータに記入された地図の領域、指定期間、時間粒度、前処理方法で日進市のごみ収集車データを処理したデータを取得し、時空間データを補間、集約したデータを返却する機能。

  * API名：garbagetruckData

  * URL：/api/t_preprocessing_garbagetruck_data

  * 引数  

|引数|説明|フォーマット|例|
| ---- | ---- | ---- | ---- |
|target_data|ゴミ収集車テーブルのカラム名|英数字|speed, pm25など|
|point1|領域における北西の位置情報|カンマ区切りの数値（経度,緯度）|139.4,35.7|
|point2|領域における北東の位置情報|カンマ区切りの数値（経度,緯度）|139.5,35.75|
|point3|領域における南東の位置情報|カンマ区切りの数値（経度,緯度）|139.6,35.8|
|point4|領域における南西の位置情報|カンマ区切りの数値（経度,緯度）|139.3,35.85|
|start_date|対象とする開始日時|YYYYMMDDHH24MI|202201271512|
|end_date|対象とする終了日時|YYYYMMDDHH24MI|202201271512|
|granularity |時間粒度（数値を含む）|英数字|10second（補間）、1year, 1month, 5day, 2hour, 5minutes（集約）|
|proc_type|前処理の方法|英数字|spline、linear（補間）、avg, max, min, sum（集約）|
|center_point|地図の中心座標（ファイル読み込み時のUIへの復元用）|カンマ区切りの数値（経度,緯度）|139.766,35.681|
|zoom_level|地図のズーム値（ファイル読み込み時のUIへの復元用）|数値|13.1|
|pitch|地図の仰俯角度（ファイル読み込み時のUIへの復元用）|数値|55.02|
|bearing|地図の回転角度（ファイル読み込み時のUIへの復元用）|数値|36.8|


  * 取得処理

1. 入力チェック
    - 上記必須項目の必須チェック
    - 時間粒度および前処理の方法が、指定された文字列であるか
    - 前処理の方法と時間粒度の組み合わせが正しいか（前処理の方法が「集約」の場合、時間粒度が「秒」でないこと、「補間」の場合、時間度が「秒」であること）
    - カラム名がテーブルに存在するものであるか

2. 前処理の方法に該当するユーザ定義関数を指定したSQLクエリを実行する

    ユーザ定義関数は「日進市ごみ収集車データ向け補間処理関数」または「日進市ごみ収集車データ向け集約処理関数」
   
    ユーザ定義関数に渡す「前処理の方法」は、リサンプル処理に該当する文字列に変換する

3. SQLクエリ結果から取得したデータを整形して返却

   形式は返却値の通り。


  * 返却値

|項目名|内容|
| ---- | ---- |
|start_date|前処理期間の開始時刻（ファイル読み込み時のUIへの復元用） |
|end_date|前処理期間の終了時刻（ファイル読み込み時のUIへの復元用） |
|map_center|地図の中心座標（ファイル読み込み時のUIへの復元用）|
|map_zoom|地図のズーム値（ファイル読み込み時のUIへの復元用）|
|map_pitch|地図の仰俯角度（ファイル読み込み時のUIへの復元用）|
|map_bearing|地図の回転角度（ファイル読み込み時のUIへの復元用）|
|granularity |時間粒度（ファイル読み込み時のUIへの復元用）|
|proc_type|前処理方法（ファイル読み込み時のUIへの復元用）|
|target_data|前処理対象のデータ（ファイル読み込み時のUIへの復元用）|
|data_array|下記の内容の通り（配列）|

|項目名|内容|
| ---- | ---- |
|type|FeatureCollection|
|features|下記の内容の通り|

|項目名|内容|
| ---- | ---- |
|geometry|type：Point<BR>coordinates：該当時刻の位置座標配列（時系列順）|
|properties| id： ごみ収集車のID <BR>identifier：ごみ収集車単位のインデックス<BR>direction：該当時刻のごみ収集車の向き（時系列順）<BR>datetime：時間粒度による時刻の配列<BR>target_dataで指定したカラム名：該当時刻の前処理済みデータ配列（時系列順）|


・リクエストパラメータエラーの場合

  リクエストパラメータのエラーメッセージを 「{"error":メッセージ内容}」として返却する。

・DBエラーの場合

  空欄のJSONを返却する