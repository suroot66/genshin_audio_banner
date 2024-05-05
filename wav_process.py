import os, subprocess
curr_dir = os.path.dirname(os.path.abspath(__file__))
test = os.path.join(curr_dir, 'depends', 'wav_to_good', 'test.exe')


target_dir = os.path.join(curr_dir, 'wav')  # 用Extractor解压出的wav路径
output_dir = os.path.join(curr_dir, 'wavwav')  # 转码后的wav路径
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for cd, sds, fs in os.walk(target_dir):
    if cd == target_dir:
        for f in fs:
            if f[-4:] == '.wav':
                subprocess.run([test,
                                os.path.join(cd, f),
                                '-o',
                                os.path.join(output_dir, f + '.wav')],
                               capture_output=True, check=True)
                print(f'[ Finished ] {f}')
