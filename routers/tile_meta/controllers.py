"""
/******************************************************************************/
/* API tile base data                                                       */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.requests import Request

from db_util.db_conn import fetch

router = APIRouter()

@router.get("/tileMetaData")
def get_tile_meta_data(request:Request):
    """get_tile_meta_data function is get t_tile_meta_data and t_tile_base_data  data
    # Arguments
        request: リクエストインスタンス
    # Returns
        json : vector_tile_idをキー
    """

    # fetchに渡すクエリ文を生成
    query = "SELECT * FROM t_tile_base_data as bs LEFT JOIN t_tile_meta_data as mt on (mt.vector_tile_id = bs.vector_tile_id) order by mt.vector_tile_id"

    ####################################################################
    # 取得実行
    ####################################################################
    dict_result = fetch(request, query)

    if dict_result == None:
        # DBエラー（正常でデータがない場合は空のJSON)
        return {}
    
    ####################################################################
    # 整形
    ####################################################################
    row_json = {}
    # print("dict_result", dict_result)
    for row in dict_result:

        if row["vector_tile_id"] not in row_json:
            row_json[row["vector_tile_id"]] = {}
            row_json[row["vector_tile_id"]]["vector_tile_id"]  = row["vector_tile_id"]
            row_json[row["vector_tile_id"]]["data_type"]  = row["data_type"]
            row_json[row["vector_tile_id"]]["data_name"]  = row["data_name"]
            row_json[row["vector_tile_id"]]["tile_type"]  = row["tile_type"]

        if ("meta_data" not in row_json[row["vector_tile_id"]]):
            row_json[row["vector_tile_id"]]["meta_data"] = []

        meta_data = {}
        meta_data["meta_id"]  = row["vector_tile_meta_id"]
        meta_data["url"]  = row["url"]
        meta_data["directory"]  = row["directory"]
        meta_data["zoom_level_min"]  = row["zoom_level_min"]
        meta_data["zoom_level_max"]  = row["zoom_level_max"]
        meta_data["resolution"]  = row["resolution"]
        meta_data["start_datetime"]  = row["start_datetime"]
        meta_data["end_datetime"]  = row["end_datetime"]

        row_json[row["vector_tile_id"]]["meta_data"].append(meta_data)

    return JSONResponse(row_json)

