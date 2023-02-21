"""
/******************************************************************************/
/* API garbagetruck preprocessing data                                        */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""
import math
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.requests import Request

from geo_util.str_util import make_extent_str, RESAMPLE_MAP
from db_util.db_conn import fetch

router = APIRouter()
@router.get("/garbagetruckData")
def get_prepro_garbagetruck_data(request:Request,
        center_point:str = None, zoom_level:str = None, bearing:str = None, pitch:str = None,
        target_data:str = None, point_1:str = None, point_2:str = None, point_3:str = None, point_4:str = None, 
        start_date:str=None, end_date:str=None, granularity:str=None, proc_type:str=None):
    """get_prepro_garbagetruck_data function is get garbagetruck data
    # Arguments
        request: リクエストインスタンス
        center_point, zoom_level, bearing, pitch : 復元用の地図情報
        target_data: 前処理対象のカラム(speed, pm25等)
        point_1: 四隅の座標1
        point_2: 四隅の座標2
        point_3: 四隅の座標3
        point_4: 四隅の座標4
        start_date: 対象とする開始日時
        end_date: 対象とする終了日時
        granularity: 時間粒度(1year, 1month, 1day, 1hour, 5minute, 30sec)
        proc_type: 前処理の方法(spline, linear, avg, max, min)
    # Returns
        json
    """

    # 入力チェック
    if point_1 == None:
        return {'error': "領域[point_1]が未入力です。"}
    if point_2 == None:
        return {'error': "領域[point_2]が未入力です。"}
    if point_3 == None:
        return {'error': "領域[point_3]が未入力です。"}
    if point_4 == None:
        return {'error': "領域[point_4]が未入力です。"}

    ext_poly_str = make_extent_str(point_1, point_2, point_3, point_4)
    if ext_poly_str == None:
        return {'error': "領域に誤りがあります。"}

    if target_data == None:
        return {'error': "データカラム名リスト[target_data]が未入力です。"}
    if start_date == None:
        return {'error': "開始日[start_date]が未入力です。"}
    if end_date == None:
        return {'error': "終了日[end_date]が未入力です。"}
    if proc_type == None:
        return {'error': "処理方法[proc_type]が未入力です。"}
    if granularity == None:
        return {'error': "時間粒度[granularity]が未入力です。"}
    if len(start_date) != len('YYYYMMDDHHMI') or start_date.isnumeric() == False:
        return {'error': "開始日が適切な形式ではありません。[" + start_date + "]"}
    if len(end_date) != len('YYYYMMDDHHMI') or end_date.isnumeric() == False:
        return {'error': "終了日が適切な形式ではありません。[" + end_date + "]"}

    # 空白は削除しておく
    proc_type = proc_type.replace(' ', '')
    granularity = granularity.replace(' ', '')
    target_data = target_data.replace(' ', '')

    # UDFに渡す時刻はyyyy-MM-dd hh:miにする
    dt_startDate = start_date[0:4] + "-" + start_date[4:6] + "-" + start_date[6:8] + " " + start_date[8:10] + ":" + start_date[10:] + ":00"
    dt_endDate   = end_date[0:4] + "-" + end_date[4:6] + "-" + end_date[6:8] + " " + end_date[8:10] + ":" + end_date[10:] + ":00"

    # 時間粒度の固定文字
    gr_year = granularity.endswith("year")
    gr_month = granularity.endswith("month")
    gr_day = granularity.endswith("day")
    gr_hour = granularity.endswith("hour")
    gr_minute = granularity.endswith("minute")
    gr_sec = granularity.endswith("sec")

    # 時間粒度と処理タイプの有効チェック
    if proc_type not in ["spline", "linear", "avg", "max", "min"] :
        return  { "error": "処理方法が正しくありません。[" + proc_type + "]"}

    if gr_year == False and gr_month == False and gr_day == False and gr_hour == False and gr_minute == False and gr_sec == False:
        return  { "error": "時間粒度が正しくありません。[" + granularity + "]"}

    if (proc_type in ["avg", "max", "min"]):
        if gr_sec == True:
            return { "error": "処理内容と時間粒度の組み合わせが正しくありません。(集約)[" + proc_type + "," + granularity + "]"}

    if proc_type in ["spline", "linear"] : 
        if gr_sec == False:
            return { "error": "処理内容と時間粒度の組み合わせが正しくありません。(補間)[" + proc_type + "," + granularity + "]"}

    # カラム名の有効チェック
    if (validate_columns(request, target_data) == False):
        return  { "error": "取得項目が正しくありません。[" + target_data + "]"}

    # 変換
    for key in RESAMPLE_MAP:
        if key in granularity:
            gr = granularity.replace(key, RESAMPLE_MAP[key])
            break

    ####################################################################
    # 関数を呼び出す
    ####################################################################
    db_datas = None
    if proc_type in ["spline", "linear"]:
        ####################################################################
        # 補間
        db_datas =  get_garbagetruck_interpolate(request, target_data, point_1, point_2, point_3, point_4, dt_startDate, dt_endDate, gr, proc_type)
    elif proc_type in ["avg", "max", "min"]:
        ####################################################################
        # 集約
        db_datas =  get_garbagetruck_aggregate(request, target_data, point_1, point_2, point_3, point_4, dt_startDate, dt_endDate, gr, proc_type)

    if db_datas != None:
        ret_json = generate_json(db_datas, target_data)
    else:
        ret_json = {}

    # 復元用の値
    if center_point != None:
        ret_json['map_center'] = center_point
    if zoom_level != None:
        ret_json['map_zoom'] = zoom_level
    if pitch != None:
        ret_json['map_pitch'] = pitch
    if bearing != None:
        ret_json['map_bearing'] = bearing
    
    # 以下は必須パラメータ
    ret_json['target_data'] = target_data
    ret_json['start_date'] = start_date
    ret_json['end_date'] = end_date
    ret_json['granularity'] = granularity
    ret_json['proc_type'] = proc_type

    # print("---ret_geojson", ret_geojson)

    return JSONResponse(ret_json)

def validate_columns(request:Request, target_colmns):
    """
    # Arguments
        request: リクエストインスタンス
        target_colmns: 対象カラム    
    """

    for col in target_colmns.split(","):
        query = "SELECT column_name FROM information_schema.columns "
        query += " WHERE table_name= 't_nisshin_garbage_data' and UPPER(column_name) = UPPER('" + col + "')"

        # 取得
        dict_result = fetch(request, query)
        if dict_result == None or len(dict_result) == 0:
            # ひとつでもなければFalseを返して終了
            return False

    # すべて有効
    return True


def get_garbagetruck_interpolate(request:Request, target_colmns, point_1, point_2, point_3, point_4, startDate, endDate, granularity, proc_type):
    """get_garbagetruck_interpolate : 地図の領域、指定期間、時間粒度、前処理方法でアメダスデータを補間処理し、返却
    # Arguments
        request: リクエストインスタンス
        target_colmns: 取得項目(speed, pm25等)
        point_1: 四隅の座標1
        point_2: 四隅の座標2
        point_3: 四隅の座標3
        point_4: 四隅の座標4
        startDate: 対象とする開始日時
        endDate: 対象とする終了日時
        granularity: 時間粒度
        proc_type: 処理方法
    # Returns
        json : 
    """

    print("get_garbagetruck_interpolate start")

    col = target_colmns.split(",")[0]
    query = " SELECT * FROM tb_gis_garbagetruck_interpolate('" + str(col).upper() + "', " + str(point_1) + ", " + str(point_2) + "," + str(point_3)  + ", " + str(point_4) + ","
    query += "'" + str(startDate) + "', '" + str(endDate) + "', '" + str(granularity) + "', '" + proc_type + "') ORDER BY id, datetime"

    print("---interpolate query:", query)

    # 取得
    dict_result = fetch(request, query)

    return dict_result


def get_garbagetruck_aggregate(request:Request, target_colmns, point_1, point_2, point_3, point_4, startDate, endDate, granularity, proc_type):
    """get_garbagetruck_aggregate : 地図の領域、指定期間、時間粒度、前処理方法でアメダスデータを集約処理し、返却
    # Arguments
        request: リクエストインスタンス
        target_colmns: 取得項目(speed, pm25等)
        point_1: 四隅の座標1
        point_2: 四隅の座標2
        point_3: 四隅の座標3
        point_4: 四隅の座標4
        startDate: 対象とする開始日時
        endDate: 対象とする終了日時
        granularity: 時間粒度
        proc_type: 処理方法
    # Returns
        json : 
    """

    print("get_garbagetruck_aggregate start")

    col = target_colmns.split(",")[0] # 大文字にする必要がある
    query = " SELECT * FROM tb_gis_garbagetruck_aggregate('" + str(col).upper() + "', " + str(point_1) + ", " + str(point_2) + "," + str(point_3)  + ", " + str(point_4) + ","
    query += "'" + str(startDate) + "', '" + str(endDate) + "', '" + str(granularity) + "', '" + proc_type + "') ORDER BY id, datetime"

    print("---aggregate query:", query)

    # 取得
    dict_result = fetch(request, query)

    return dict_result


def generate_json(db_datas, target_colmns):
    """generate_json : 取得したデータを返却用Json形式に変換する。
    # Arguments
        db_datas: 取得したデータ
        target_colmns: 取得項目（カラム）
    # Returns
        json : 
    """

    ret_json = {}
    # 登録済みの車体
    vehicles = []

    identifier = 1
    for data_row in db_datas:
        # 返却用JSON生成

        # 位置がNanの場合は格納しない。
        if math.isnan(data_row[2]) or math.isnan(data_row[3]):
            continue

        # 日時
        _datetime = data_row[1].strftime('%Y%m%d%H%M%S')

        # # 数値
        # # 現時点ではdirectionとdataのみ
        colmns = target_colmns.split(",")

        ##########################################
        # geojsonを生成
        ##########################################
        # 個別単位のMF-JSON
        mf_json = None

        # 登録済みMF-JSONを取得
        for vihecle in vehicles:
            if data_row[0] == vihecle["features"][0]["properties"]["id"]: # id
                mf_json = vihecle
                break


        # 数値を取得
        try:
            direction = float(data_row[4])
            if math.isnan(direction):
                direction = 0
        except ValueError:
            direction = 0

        try:
            data = float(data_row[6])
            if math.isnan(data) == False:
                # 小数第2位まで
                data = math.floor(data * 100) /100
            else:
                data = 0
        except ValueError:
            data = 0

        if mf_json == None:
            # 新規の場合
            ##########################################
            # featuresの生成
            ##########################################
            features = {}
            features["type"] = "Feature"
            features["geometry"] = {}
            features["geometry"]["type"] = "Point"


            features["geometry"]["coordinates"] = [[data_row[2], data_row[3]]] # 位置情報

            mf_json = {"type" : "FeatureCollection"}
            mf_json['features'] = [{
                "type" : "Feature",
                "geometry":features["geometry"]
            }]
            mf_json['features'][0]["properties"] = {
                    "id": data_row[0] ,
                    "datetime":[_datetime],
                    # "timezone":str(data_row[1].tzinfo),
                    "identifier": identifier,
                    } 
            # identifierを増やす
            identifier += 1

            # 数値を格納
            mf_json['features'][0]["properties"]['direction'] = [direction]
            mf_json['features'][0]["properties"][colmns[0]] = [data]

            vehicles.append(mf_json)

        else:
            mf_json['features'][0]["geometry"]["coordinates"].append([data_row[2], data_row[3]])
            mf_json['features'][0]["properties"]["datetime"].append(_datetime)

            # 数値を格納
            mf_json['features'][0]["properties"]['direction'].append(direction)
            mf_json['features'][0]["properties"][colmns[0]].append(data)


    ret_json['data_array'] =  vehicles

    return ret_json