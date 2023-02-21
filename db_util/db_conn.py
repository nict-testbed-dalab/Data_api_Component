"""
/******************************************************************************/
/* データベースアクセスutil                                                   */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""
import os
from starlette.requests import Request

import psycopg2
import psycopg2.extras


def fetch(request:Request, query, bind= {}):
    dict_result = []
    db_conn = None
    cur = None

    # envファイルから取得する
    host=str(os.getenv("DB_HOST"))
    port=str(os.getenv("DB_PORT"))
    dbname=str(os.getenv("DB_NAME"))
    user=str(os.getenv("DB_USER"))
    pw=str(os.getenv("DB_PW"))

    try:
        # # DBコネクション取得
        # conn = request.state.connection

        # DBコネクション取得
        db_conn = psycopg2.connect("host=" + host + " port=" + port + " dbname=" +  dbname + " user=" + user + " password=" + pw)

        # カーソル生成
        cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        ####################################################################
        # クエリ実行
        ####################################################################
        cur.execute(query, bind)

        dict_result = cur.fetchall()

    except Exception as e:
        print("DBエラー:", e.args)
        return None

    finally:
        # カーソルはここで閉じる
        if cur != None:
           cur.close()
        
        if db_conn != None:
            db_conn.close()

    return dict_result
