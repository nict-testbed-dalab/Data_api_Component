"""
/******************************************************************************/
/* 各種util                                                                   */
/* Copyright (c) NICT. All rights reserved.                                   */
/* See License.txt for the license information.                               */
/******************************************************************************/
"""


# def make_date_range(startDate:str=None, endDate:str=None, granularity:str=None):
#     """ 開始日、終了日のWhere句
#     # Returns
#         文字列
#     """

#     if granularity == 'hour':
#         startDate = startDate[0:8] + " " + startDate[8:10] + "00"
#         endDate = endDate[0:8] + " " + endDate[8:10] + "00"
#     elif granularity == 'day':
#         startDate = startDate[0:8] + " 0000"
#         endDate = endDate[0:8] + " 0000"
#     else:
#         # YYYYMMDD と HHMIの間にスペース必要
#         startDate = startDate[0:8] + " " + startDate[8:]
#         endDate = endDate[0:8] + " " + endDate[8:]

#     where_date_query = " datetime >= cast('" + startDate +"' as timestamp) "
#     where_date_query += " and datetime <= cast('" + endDate +"' as timestamp) "

#     return where_date_query


def is_validate_point(point:str):
    """ 座標値のチェック
    # Argment
        point: 座標(カンマ区切り)
    # Returns
        True :正常
        False:異常
    """
    if point == None or len(point.split(",")) < 2:
        return False

    try:
        # 整数または小数点であるチェック
        float(point.split(",")[0])
        float(point.split(",")[1])
    except ValueError:
        return False

    return True


def make_extent_str( point_1:str = None, point_2:str = None, point_3:str = None, point_4:str = None):
    """ 領域を文字列として生成
    # Argment
        point_1: XY座標
        point_2: XY座標
        point_3: XY座標
        point_4: XY座標
    # Returns
        座標自体は半角スペースで区切り、全座標を半角カンマで連結させた文字列(x1 y1, x2 y2, x3 y3, x4 y4)
    """
    if ((not is_validate_point(point_1)) or (not is_validate_point(point_2)) or (not is_validate_point(point_3)) or (not is_validate_point(point_4))):
        # 領域がない場合は空で返却
        print("Some point_x are invalidate.")
        return None
    else:
        ext_poly = [point_1.split(",")[0] + " " + point_1.split(",")[1], 
                    point_2.split(",")[0] + " " + point_2.split(",")[1],
                    point_3.split(",")[0] + " " + point_3.split(",")[1],
                    point_4.split(",")[0] + " " + point_4.split(",")[1],
                    point_1.split(",")[0] + " " + point_1.split(",")[1]
                    ]

        # 文字列として返却
        return ",".join(ext_poly)

# リサンプルの指定文字列
# 月は「M」では月末になるので、Sを付けて月初にする（年も同様）
RESAMPLE_MAP = {
    'sec':'S',
    'minute': 'T',
    'hour': 'H',
    'day':'D',
    'month':'MS',
    'year':'YS',
    }
