import os
import time
import zipfile
from flask import Blueprint, request, session, jsonify
import predict
from path_required import set_single_dir_path, set_src_dir_path
import path_required
from predict.BRNN import get_result
from predict.get_data import run_ir2vec
from predict.slice import run_dg

ALLOWED_UPLOAD_FILE_TYPES = ['zip', 'rar']
ALLOWED_CHECK_LANGUAGE_TYPES = ['c']


def allowed_upload_type(filename):
    '''允许接受的文件类型'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_UPLOAD_FILE_TYPES


def allowed_check_language_type(filename):
    '''允许检查的编程语言文件类型'''
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_CHECK_LANGUAGE_TYPES


bp = Blueprint('upload', __name__)


@bp.route('/', methods=['GET', 'POST'])
def upload_package():
    '''上传待测项目'''
    if request.method == 'POST':
        # 创建工作目录
        if os.path.exists(path_required.work_dir_path) == 0:
            os.mkdir(path_required.work_dir_path)
        # 获取文件对象
        package = request.files['package']
        # 检查文件类型
        if not allowed_upload_type(package.filename):
            return "请上传zip格式的文件", 406
        # return "上传成功"
        # 保存到指定文件夹
        type = package.filename.split('.')[-1]
        rand_name = str(int(time.time()))  # 随机生成名保存
        newFileName = package.filename.split(
            '.')[0] + '_'+rand_name + '.' + type
        # 单独文件夹存放数据
        single_dir_path = set_single_dir_path(newFileName.split('.')[0])
        if os.path.exists(single_dir_path) == 0:
            os.mkdir(single_dir_path)
        zip_file_path = os.path.join(single_dir_path, newFileName)
        package.save(zip_file_path)
        # 源文件所在目录
        src_dir_path = set_src_dir_path(single_dir_path+'/C_file')
        # 解压zip
        if (type == 'zip'):
            un_zip(zip_file_path, src_dir_path)
        from predict.compile import generate_bc
        if generate_bc(single_dir_path) == 0:
            return "编译失败，请检查文件", 406
        print("1")
        run_dg(single_dir_path)
        print("2")
        run_ir2vec(single_dir_path)
        print("3")
        return get_result(single_dir_path)


def un_zip(file_path, unzip_dir):
    """
    unzip zip file
    file_path:zip文件路径
    unzip_dir:解压路径
    """
    zip_file = zipfile.ZipFile(file_path)
    if os.path.isdir(unzip_dir):
        pass
    else:
        os.mkdir(unzip_dir)
    for names in zip_file.namelist():
        zip_file.extract(names, unzip_dir)
    zip_file.close()
