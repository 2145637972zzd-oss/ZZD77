# app/utils/common.py
from flask import jsonify

def success_response(data=None, msg="成功", code=200):
    return jsonify({"code": code, "msg": msg, "data": data}), code

def error_response(msg="失败", code=400, data=None):
    return jsonify({"code": code, "msg": msg, "data": data}), code