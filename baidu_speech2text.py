# -*- coding: utf-8 -*-

import sys, os
import json
import time
import wave
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode

timer = time.perf_counter
curr_dir = os.path.dirname(os.path.abspath(__file__))

def get_audio_info(file_path):  
    with wave.open(file_path, 'r') as wf:  
        _n_channels, _samp_width, framerate, nframes = wf.getparams()[:4]  
  
        # 计算音频时长（秒）  
        duration = nframes / framerate  
  
        # 采样率  
        sample_rate = framerate
  
        return duration, sample_rate

##———————————————————————————————————————— start ————————————————————————————————————————
# api密钥
API_KEY = ''
SECRET_KEY = ''
CUID = 'test'  # 用户名，随意
DURATION_LIMIT = 10  # 识别的音频时长上限，超过秒数的不进行识别

# 普通版

DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
        result_str = result_str.decode()

    #print(result_str)
    result = json.loads(result_str)
    #print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        #print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  TOKEN end """


# main
target_dir = os.path.join(curr_dir, 'resample')  # 重采样的输出路径
output_dir = os.path.join(curr_dir, 'txt-baidu')  # 识别结果保存路径
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
file_list = []
for cd, sds, fs in os.walk(target_dir):
    if cd == target_dir:
        for f in fs:
            if f[-4:] == '.wav':
                file_list.append(f)

def process_one_file(file):
    # 文件准备
    AUDIO_FILE = os.path.join(target_dir, file)  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    RATE = 16000  # 固定采样率（仅支持16000、8000）
    duration, sample_rate = get_audio_info(AUDIO_FILE)
    #print(f"音频时长: {duration} 秒")
    #print(f"采样率: {sample_rate} Hz")
    if duration >= DURATION_LIMIT:
        return
    
    # 文件读取
    speech_data = b''
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()
    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    
    # 请求构造
    token = fetch_token()
    params = {'cuid': CUID, 'token': token, 'dev_pid': DEV_PID}
    params_query = urlencode(params);
    headers = {
        'Content-Type': 'audio/' + FORMAT + '; rate=' + str(RATE),
        'Content-Length': length
    }
    url = ASR_URL + "?" + params_query
    #print("url is", url);
    #print("header is", headers)
    req = Request(ASR_URL + "?" + params_query, speech_data, headers)
    
    # 调用api
    try:
        begin = timer()
        f = urlopen(req, timeout=60)
        result = f.read()
        print("Request time cost %f" % (timer() - begin), flush=True)
    except  URLError as err:
        print('asr http response http code : ' + str(err.code))
        result = err.read()
    
    result_d = json.loads(result.decode('utf-8'))
    with open(os.path.join(output_dir, file + '.txt'), "w", encoding='utf-8') as f:
        f.write(' '.join(result_d['result']))
    print(f'[ Finished ] {file}', flush=True)

from concurrent.futures import ThreadPoolExecutor
tp = ThreadPoolExecutor(50)
fts = []
for file in file_list:
    ft = tp.submit(process_one_file, file)
    fts.append(ft)
tp.shutdown()