"""
/******************************************************************************/
/* API amedas data                                                            */
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

@router.get("/amedasData")
def get_amedas_data(request:Request, point_1:str = None, point_2:str = None, point_3:str = None, point_4:str = None, currentDate:str=None):
    """get_amedas_data function is get amedas data
    # Arguments
        request: リクエストインスタンス
        point_1: 四隅の座標1
        point_2: 四隅の座標2
        point_3: 四隅の座標3
        point_4: 四隅の座標4
        currentDate: 対象日時(YYYYMMDDHHMI)
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

    ext_query = " ST_Intersects(ST_MakePoint(ST_Y(location),ST_X(location)), ST_GeomFromText('POLYGON ( (" + ext_poly_str + ") )')) "

    ####################################################################
    # 日時
    ####################################################################
    if currentDate != None:
        # 長さによってフォーマットを決める
        if len(currentDate) == len('YYYYMMDDHHMI') and currentDate.isnumeric():
            # 分単位(データは10分単位で該当する１レコード)
            currentDate = currentDate[0:8] + " " + currentDate[8:11] + "0" # 分の１０の位まで
            where_sub_query = " datetime = cast('" + currentDate +"' as timestamp) "
        # elif len(currentDate) == len('YYYYMMDDHH') and currentDate.isnumeric():
        #     # 時間単位(データは00分に該当する１レコード)
        #     currentDate = currentDate[0:8] + " " + currentDate[8:10] + "00" # 00分
        #     where_sub_query = " am.datetime = cast('" + currentDate +"' as timestamp) "
        else:
            print("currentDate must be format(YYYYMMDDHHMI).")
            return {}
    else:
        print("currentDate is Null.")
        return {}

    ####################################################################
    # 1.最初に該当するprefnumberを取得
    ####################################################################
    query_1 = "SELECT "
    query_1 += " ST_AsGeoJSON(ST_SetSRID(ST_MakePoint(ST_Y(location),ST_X(location)), 4326)::geometry)::json as geometry,  "
    query_1 += " prefnumber, altitude, type, elems, kjname, knname, enname "
    query_1 += " FROM t_amedas_code_data "
    query_1 += " WHERE " + ext_query

    # 取得1
    # print("query_1:", query_1)
    dict_result_1 = fetch(request, query_1)
    if dict_result_1 == None or len(dict_result_1) == 0:
        # DBエラーまたは、データなし
        return {}

    prefnumbers = [] # 検索条件のための地域コード
    pref_info ={} # GeoJsonのための地域情報
    for row in dict_result_1:
        prefnumbers.append(str(row["prefnumber"]))
        pref_info[row["prefnumber"]] =  {
                        "geometry" : row["geometry"],
                        "altitude": row["altitude"],
                        "type": row["type"],
                        "elems": row["elems"],
                        "kjName": row["kjname"],
                        "knName": row["knname"],
                        "enName": row["enname"],
                        }

    where_pref = ",".join(prefnumbers)

    ####################################################################
    # 2.prefnumberをキーとしたアメダスデータを取得
    ####################################################################
    query = "SELECT * FROM t_amedas_data "
    query += " WHERE prefnumber IN (" + where_pref + ") AND " + where_sub_query 
    query += " ORDER BY prefnumber"

    # print("get_amedas_data query:", query)

    # 本取得
    dict_result = fetch(request, query)
    if dict_result == None :
        # DBエラー
        return {}

    ####################################################################
    # featuresを生成
    # (DecimalはJSONに格納できないので変換する)
    ####################################################################
    features = []
    for row in dict_result:
        pref =  row["prefnumber"]
        row_json = {"type": "Feature"}
        row_json["geometry"] = pref_info[pref]["geometry"]
        row_json["properties"]  = {
            # 下記は地域情報
            "prefnumber": pref,
            "altitude": pref_info[pref]["altitude"],
            "type": pref_info[pref]["type"],
            "elems": pref_info[pref]["elems"],
            "kjName": pref_info[pref]["kjName"],
            "knName": pref_info[pref]["knName"],
            "enName": pref_info[pref]["enName"],

            # 下記はアメダスデータ
            "datetime"   : str(row["datetime"]) ,
            "observationNumber": row["observationnumber"] if row["observationnumber"] != None else "",
            "pressure"       : float(row["pressure"]) if row["pressure"] != None else "",
            "normalpressure" : float(row["normalpressure"]) if row["normalpressure"] != None else "",
            "temp"           : float(row["temp"])     if row["temp"] != None else "",
            "humidity"       : float(row["humidity"]) if row["humidity"] != None else "",
            "sun10m"         : float(row["sun10m"])   if row["sun10m"] != None else "",
            "sun1h"          : float(row["sun1h"])    if row["sun1h"] != None else "",
            "precipitation10m" : float(row["precipitation10m"]) if row["precipitation10m"] != None else "",
            "precipitation1h"  : float(row["precipitation1h"])  if row["precipitation1h"] != None else "",
            "precipitation3h " : float(row["precipitation3h"])  if row["precipitation3h"] != None else "",
            "precipitation24h" : float(row["precipitation24h"]) if row["precipitation24h"] != None else "",
            "windDirection"    : float(row["winddirection"])    if row["winddirection"] != None else "",
            "wind"        : float(row["wind"])        if row["wind"] != None else "",
            "maxTempTime" : float(row["maxtemptime"]) if row["maxtemptime"] != None else "",
            "maxTemp"     : float(row["maxtemp"])     if row["maxtemp"] != None else "",
            "minTempTime" : float(row["mintemptime"]) if row["mintemptime"] != None else "",
            "minTemp"     : float(row["mintemp"])     if row["mintemp"] != None else "",
            "gustTime"    : float(row["gusttime"])    if row["gusttime"] != None else "",
            "gustDirection" : float(row["gustdirection"]) if row["gustdirection"] != None else "",
            "gust"    : float(row["gust"])    if row["gust"] != None else "",
            "snow"    : float(row["snow"])    if row["snow"] != None else "",
            "snow1h"  : float(row["snow1h"])  if row["snow1h"] != None else "",
            "snow3h"  : float(row["snow3h"])  if row["snow3h"] != None else "",
            "snow6h"  : float(row["snow6h"])  if row["snow6h"] != None else "",
            "snow12h" : float(row["snow12h"]) if row["snow12h"] != None else "",
            "snow24h" : float(row["snow24h"]) if row["snow24h"] != None else "",
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
