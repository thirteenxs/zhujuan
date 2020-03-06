from tqdm import tqdm
import time

pbar = tqdm(range(1,9))
for c in pbar:
    # time.sleep(0.1)
    pbar.set_description("Processing %s" % c)

# base_path= os.path.dirname(__file__)
# mp4_path=os.path.join(base_path,'tmp_video')
# print(mp4_path)