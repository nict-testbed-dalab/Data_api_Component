"""
/******************************************************************************/
/* API people flow data                                                       */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.requests import Request

from geo_util.str_util import make_extent_str
from db_util.db_conn import fetch

router = APIRouter()

@router.get("/peopleFlowData")
def get_people_flow_data(request:Request, point_1:str = None, point_2:str = None, point_3:str = None, point_4:str = None, currentDate:str=None, device:str=None):
    """get_people_flow_data function is get people-flow data
    # Arguments
        request: リクエストインスタンス
        point_1: 四隅の座標1
        point_2: 四隅の座標2
        point_3: 四隅の座標3
        point_4: 四隅の座標4
        currentDate: 対象日時
        device: デバイスID
    # Returns
        json : geojson
    """
    where_sub_query = ""
 
    ####################################################################
    # 領域取得
    ####################################################################
    # 領域取得
    ext_poly_str = make_extent_str(point_1, point_2, point_3, point_4)
    if ext_poly_str == None:
        # エラーの場合はNoneが返却される
        return {}

    ext_query = " ST_Intersects(ST_MakePoint(ST_Y(location),ST_X(location)), 'POLYGON ( (" + ext_poly_str + ") )'::geometry)"

    ####################################################################
    # 他のパラメータのチェック
    ####################################################################
    if currentDate == None or not(currentDate.isnumeric()):
        print("'currentDate' must not bet null.")
        return {}

    # if(device != None and not(device.isnumeric())):
    #     print("device is not validate.")
    #     return {}

    ####################################################################
    # device
    ####################################################################
    bind = {}
    if device != None:
        where_sub_query += " AND device = %s"
        bind =  (str(device), ) # タプルにする
    
    ####################################################################
    # 日時
    ####################################################################
    # 長さによってフォーマットを決める
    if len(currentDate) == len('YYYYMMDDHHMISS'):
        # 秒単位
        where_sub_query += " AND TO_CHAR(datetime,'YYYYMMDDHH24MISS') = '" + currentDate +"'"
    elif len(currentDate) == len('YYYYMMDDHHMI'):
        # 分単位
        where_sub_query += " AND TO_CHAR(datetime,'YYYYMMDDHH24MI') = '" + currentDate +"'"
    elif len(currentDate) == len('YYYYMMDDHH'):
        # 時間単位
        where_sub_query += " AND TO_CHAR(datetime,'YYYYMMDDHH24') = '" + currentDate +"'"
    elif len(currentDate) == len('YYYYMMDD'):
        # 日単位
        where_sub_query += " AND TO_CHAR(datetime,'YYYYMMDD') = '" + currentDate +"'"
    elif len(currentDate) == len('YYYYMM'):
        # 月単位
        where_sub_query += " AND TO_CHAR(datetime,'YYYYMM') = '" + currentDate +"'"

    # fetchに渡すクエリ文を生成
    # GNSS(GPS)は緯度経度で登録されているので逆にする
    query = "SELECT people_flow_data_id as id, people_flow_base_id, " 
    query += " ST_AsGeoJSON(ST_SetSRID(ST_MakePoint(ST_Y(location),ST_X(location)), 4326)::geometry)::json as geometry,  "
    query += " datetime, device, rssi"
    query += " FROM t_people_flow_data "
    query += " WHERE " + ext_query
    query += where_sub_query
    query += " ORDER BY datetime"

    ####################################################################
    # 取得実行
    ####################################################################
    dict_result = fetch(request, query, bind)

    if dict_result == None:
        # DBエラー（正常でデータがない場合は空のJSON)
        return {}

    ####################################################################
    # featuresを生成
    ####################################################################
    features = []
    for row in dict_result:
        row_json = {"type": "Feature"}
        row_json["geometry"] = row["geometry"]
        row_json["properties"] = {
            "id"         : row["id"], 
            "people_flow_base_id" : row["people_flow_base_id"],
            "device"     : row["device"],
            "rssi"       : row["rssi"] ,
            "datetime"   : str(row["datetime"]) , # Not Null
            }
        features.append(row_json)
    
    ####################################################################
    # GeoJsonに整形
    ####################################################################
    ret_geojson = {
                "type": "FeatureCollection",
                "features": features
                }

    return JSONResponse(ret_geojson)


@router.get("/peopleExistDate")
def get_people_exist_date(request:Request):
    """get_people_flow_data function is get people-flow data
    # Arguments
        request: リクエストインスタンス
    # Returns
        json : geojson
    """

    # fetchに渡すクエリ文を生成
    query = "SELECT TO_CHAR(datetime,'YYYYMMDD') as datetime, base.place as place from t_people_flow_data as dt " 
    query += " LEFT JOIN t_people_flow_base_data as base ON(base.people_flow_base_id = dt.people_flow_base_id)" 
    query += " GROUP BY TO_CHAR(datetime,'YYYYMMDD'), base.place "
    query += " ORDER BY datetime"

    ####################################################################
    # 取得実行
    ####################################################################
    dict_result = fetch(request, query)

    if dict_result == None:
        # DBエラー（正常でデータがない場合は空のJSON)
        return {}

    row_json = {}
    for row in dict_result:
        row_json[row["datetime"]] = row["place"]
    
    return JSONResponse(row_json)