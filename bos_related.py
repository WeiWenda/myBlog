# -*- coding: utf8 -*-
#导入BosClient配置文件
import bos_sample_conf 
import time
import random
import string 
import os
#导入BOS相关模块
from baidubce import utils
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient
bucket_name = 'weiwendablog'
def _random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
def getClient():
    bos_client = BosClient(bos_sample_conf.config)
    if not bos_client.does_bucket_exist(bucket_name):
        bos_client.create_bucket(bucket_name)
    return bos_client
def save(file,folder):
    #新建BosClient
    bos_client = getClient()
    key = _random_string(6)
    file_name = file.filename
    fp = file.stream
    try:
        fp.seek(0, os.SEEK_END)
        content_length = fp.tell()
        fp.seek(0)
        recv_buf_size = bos_client._get_config_parameter(None, 'recv_buf_size')
        content_md5 = utils.get_md5_from_fp(fp, length=content_length,
                                            buf_size=recv_buf_size)
        content_type = utils.guess_content_type_by_file_name(file_name)
        bos_client.put_object(bucket_name, folder+key, fp, content_length=content_length, content_md5=content_md5, content_type=content_type)
        # bos_client.put_object_from_file(bucket_name,folder+key,file)
        url = bos_client.generate_pre_signed_url(bucket_name,folder+key, int(time.time()), -1)
        return (url,folder+key,int(content_length))
    finally:
        fp.close()

def get(filename):
    bos_client = getClient()
    bos_client.get_object_to_file(bucket_name,filename)

def listdir(folder):
    bos_client = getClient()
    bos_client.list_all_objects(bucket_name,prefix = folder)

def rmdir(folder):
    bos_client = getClient()
    for item in bos_client.list_all_objects(bucket_name,prefix = folder):
        bos_client.delete_object(bucket_name, item.key)

def delete(filename):
    bos_client = getClient()
    bos_client.delete_object(bucket_name, filename)