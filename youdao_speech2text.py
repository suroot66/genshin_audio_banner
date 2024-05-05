# -*- coding: utf-8 -*-

import sys, os
import uuid
import requests
import wave
import base64
import hashlib
import json

from imp import reload
import time
reload(sys)
curr_dir = os.path.dirname(os.path.abspath(__file__))

##———————————————————————————————————————— start ————————————————————————————————————————
YOUDAO_URL = 'https://openapi.youdao.com/asrapi'
APP_KEY = ''
APP_SECRET = ''
DURATION_LIMIT = 3  # 识别的音频时长上限，超过秒数的不进行识别

def get_audio_info(file_path):  
    with wave.open(file_path, 'r') as wf:  
        _n_channels, _samp_width, framerate, nframes = wf.getparams()[:4]  
  
        # 计算音频时长（秒）  
        duration = nframes / framerate  
  
        # 采样率  
        sample_rate = framerate
  
        return duration, sample_rate
    
def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()

def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)

def connect(file, target_dir, output_dir):
    audio_file_path = os.path.join(target_dir, file)
    lang_type = 'zh-CHS'  # 语种
    extension = audio_file_path[audio_file_path.rindex('.')+1:]
    if extension != 'wav':  # wav、mp3、aac都支持
        print('不支持的音频类型')
        sys.exit(1)
    #wav_info = wave.open(audio_file_path, 'rb')
    #sample_rate = wav_info.getframerate()
    #nchannels = wav_info.getnchannels()
    #wav_info.close()
    duration, sample_rate = get_audio_info(audio_file_path)
    if duration >= DURATION_LIMIT:
        return
    
    with open(audio_file_path, 'rb') as file_wav:
        q = base64.b64encode(file_wav.read()).decode('utf-8')

    data = {}
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['signType'] = "v2"
    data['langType'] = lang_type
    data['rate'] = 16000  # 推荐16000，支持8000/16000，已重采样
    data['format'] = 'wav'
    data['channel'] = 1  # 仅支持单声道
    data['type'] = 1

    response = do_request(data)
    #return response.content
    
    with open(os.path.join(output_dir, file + '.txt'), "w", encoding='utf-8') as f:
        f.write(' '.join(json.loads(response.content.decode('utf-8'))['result']))
    print(f'[ Finished ] {file}', flush=True)
    



# main
target_dir = os.path.join(curr_dir, 'resample')  # 重采样的输出路径
output_dir = os.path.join(curr_dir, 'txt-youdao')  # 识别结果保存路径
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
file_list = []
for cd, sds, fs in os.walk(target_dir):
    if cd == target_dir:
        for f in fs:
            if f[-4:] == '.wav':
                file_list.append(f)

from concurrent.futures import ThreadPoolExecutor
tp = ThreadPoolExecutor(64)  # 有道官方未说明并发量上限
fts = []
for file in file_list:
    ft = tp.submit(connect, file, target_dir, output_dir)
    fts.append(ft)
tp.shutdown()