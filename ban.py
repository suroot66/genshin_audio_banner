import os
curr_dir = os.path.dirname(os.path.abspath(__file__))

def get_wav_info(b, wav_num):
    info = b[0x38 + 0x18 * wav_num - 12: \
             0x38 + 0x18 * wav_num - 4][::-1]
    pos = int(info[:4].hex(), base=16)
    size = int(info[4:].hex(), base=16)
    return pos, size

def ban_one_file(pck_num, wav_nums, target_dir, output_dir):
    target_pck = os.path.join(target_dir, f'External{pck_num}.pck')
    output_pck = os.path.join(output_dir, f'External{pck_num}.pck')
    with open(target_pck, 'rb') as f:
        b = f.read()
    
    out_b = b
    for wav_num in wav_nums:
        pos, size = get_wav_info(b, wav_num)
        out_b = out_b[:pos] + b'\x00' * size + out_b[pos + size:]
    
    with open(output_pck, 'wb') as f:
        f.write(out_b)
        

def ban(target_dict, target_dir, output_dir):
    for pck_num, wav_nums in target_dict.items():
        ban_one_file(pck_num, wav_nums, target_dir, output_dir)


# main
'''
target_dict为目标语音的位置
如 External5 00041.wav 和 External5 00988.wav 为需要屏蔽的语音，
则填入 5: [41, 988], 
以下数值仅为示例，为手机端流浪者大世界语音位置
'''
target_dict = {
    1: [883],
    2: [512, 334],
    3: [575, 1053, 398],
    4: [56, 492],
    6: [980, 815],
    5: [988, 41],
    8: [702],
    10: [1141],
    11: [34],
    12: [339, 137],
    14: [884, 913],
    16: [923, 450, 1138],
    17: [410, 32],
    18: [754, 617],
    19: [614, 127, 980, 310],
    20: [393],
    21: [614],
    23: [487, 1059],
    24: [915],
    25: [499],
    26: [42, 339],
    27: [766, 271, 674, 28],
    28: [793],
    29: [638],
    30: [703],
    31: [262]
}
target_dict = {
    10: [1141, 1142]
}
target_dir = os.path.join(curr_dir, 'pck')
output_dir = os.path.join(curr_dir, 'out-pck')
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
# 生成pck
ban(target_dict, target_dir, output_dir)
# 修改校验文件
'''
此步骤似乎不需要 只有在更新游戏时会重新计算md5
另外json中hash字段含义不明
'''
# import hashlib, json
# out_md5 = {}
# for cd, sds, fs in os.walk(output_dir):
#     if cd != output_dir:
#         continue
#     for f in fs:
#         if f[-4:] != '.pck':
#             continue
#         with open(os.path.join(output_dir, f), 'rb') as _:
#             b = _.read()
#         out_md5["Chinese/" + f] = hashlib.md5(b).hexdigest()
# persist_file = os.path.join(curr_dir, 'res_versions_persist')
# new_lines = []
# with open(persist_file, 'r') as f:
#     for line in f:
#         t = json.loads(line.strip())
#         if t['remoteName'] in out_md5:
#             t['md5'] = out_md5[t['remoteName']]
#             new_lines.append(json.dumps(t) + '\n')
#         else:
#             new_lines.append(line)
# if not os.path.exists(persist_file + '_ori'):
#     os.rename(persist_file, persist_file + '_ori')
# with open(persist_file, 'w') as f:
#     f.writelines(new_lines)
            