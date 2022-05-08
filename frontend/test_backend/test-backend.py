# -*- coding:utf-8 -*-
from flask import Flask,request, jsonify, make_response
from flask_cors import *
import os
import time
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/upload", methods=["POST", "GET"])
def file_receive():
    # time.sleep(20)
    print(request.files)
    file = request.files.get("file")
    if file is None:# 表示没有发送文件
        return {
            'code': 400,
            'message': "文件上传失败"
        }
    file_name = file.filename.replace(" ","")
    print("获取上传文件的名称为[%s]\n" % file_name)
    # file.save(os.path.dirname(__file__)+'/upload/' + file_name)  # 保存文件

    with open("test-result.json", "r") as f:
        obj = json.load(f)
    return obj


# web 服务器
if __name__ == '__main__':
    app.run()
