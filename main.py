"""
/******************************************************************************/
/* API main                                                                   */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""
import os
from pathlib import Path  # python3 only
from dotenv import load_dotenv

import psycopg2
import psycopg2.extras

from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers.people_flow.controllers import router as people_flow_router
from routers.amedas.controllers import router as amedas_routers
from routers.amedas.prepro_controllers import router as prepro_amedas_routers
from routers.garbagetruck.prepro_controllers import router as garbagetruck_routers
from routers.tile_meta.controllers import router as  tile_meta_router

from starlette.requests import Request

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


load_dotenv()

# OR, explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


app = FastAPI()

# CORSを回避するために追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

# DB接続インスタンス
_psycopg2 = {}

# 起動時にDatabaseに接続する。
@app.on_event("startup")
async def startup():
    print("startup")

    # # envファイルから取得する
    # host=str(os.getenv("DB_HOST"))
    # port=str(os.getenv("DB_PORT"))
    # dbname=str(os.getenv("DB_NAME"))
    # user=str(os.getenv("DB_USER"))
    # pw=str(os.getenv("DB_PW"))

    # print("dbname:", dbname)

    # _psycopg2["db_conn"] = psycopg2.connect("host=" + host + " port=" + port + " dbname=" +  dbname + " user=" + user + " password=" + pw)

# 終了時にDatabaseを切断する。
@app.on_event("shutdown")
async def shutdown():
    print("shutdown")
    # if _psycopg2["db_conn"] != None:
    #     print("db_conn close")
    #     _psycopg2["db_conn"].close()


# routerを登録する。
app.include_router(people_flow_router)
app.include_router(amedas_routers)
app.include_router(prepro_amedas_routers)
app.include_router(garbagetruck_routers)
app.include_router(tile_meta_router)

# middleware state.connectionにdatabaseオブジェクト(_psycopg2)をセットする。
# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     request.state.connection = _psycopg2["db_conn"]
#     response = await call_next(request)
#     return response


# #########################################################
@app.get("/test/1")
def dbtest():
    # conn2 = _psycopg2["db_conn"]
    # envファイルから取得する
    host=str(os.getenv("DB_HOST"))
    port=str(os.getenv("DB_PORT"))
    dbname=str(os.getenv("DB_NAME"))
    user=str(os.getenv("DB_USER"))
    pw=str(os.getenv("DB_PW"))

    try:
        db_conn = psycopg2.connect("host=" + host + " port=" + port + " dbname=" +  dbname + " user=" + user + " password=" + pw)

        cur2 = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur2.execute("select * from t_people_flow_base_data")
        results = cur2.fetchall()

        dict_result = []
        for row in results:
            dict_result.append(dict(row))

    finally:
        cur2.close()
        db_conn.close()

    result_json = jsonable_encoder(dict_result)
    return JSONResponse(content=result_json)
