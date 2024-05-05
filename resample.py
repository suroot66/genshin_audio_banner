import os, subprocess
curr_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg = os.path.join(curr_dir, 'depends', 'ffmpeg', 'ffmpeg.exe')


target_dir = os.path.join(curr_dir, 'wavwav')  # 转码后的wav路径
output_dir = os.path.join(curr_dir, 'resample')  # 重采样的输出路径
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

def task(cd, f):
    input_file = os.path.join(cd, f)  # 输入文件
    new_sample_rate = 16000  # 新的采样率
    output_file = os.path.join(output_dir, f[:-4] + f'-{new_sample_rate}.wav')  # 输出文件
    r = subprocess.run(f'{ffmpeg} -i "{input_file}" -ar {new_sample_rate} "{output_file}"', 
                       shell=True, capture_output=True, check=True)
    print(f'[ Resampled ] {f}', flush=True)
    
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
tp = ThreadPoolExecutor(cpu_count())
for cd, sds, fs in os.walk(target_dir):
    if cd == target_dir:
        for f in fs:
            if f[-4:] == '.wav':
                ft = tp.submit(task, cd, f)
tp.shutdown()
