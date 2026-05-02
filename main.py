import os
import time
import mss
import keyboard
import imagehash
from PIL import Image

FINGER_PRINT = {"left": 1290, "top": 175, "width": 525, "height": 845}

FRAGRANT = [
    {"left": 565, "top": 400, "width": 150, "height": 160}, # 0 第一行左
    {"left": 785, "top": 400, "width": 150, "height": 160}, # 1 第一行右
    {"left": 565, "top": 615, "width": 150, "height": 160}, # 2 第二行左
    {"left": 785, "top": 615, "width": 150, "height": 160}, # 3 第二行右
    {"left": 565, "top": 830, "width": 150, "height": 160}, # 4 第三行左
    {"left": 785, "top": 830, "width": 150, "height": 160}, # 5 第三行右
    {"left": 565, "top": 1045, "width": 150, "height": 160}, # 6 第四行左
    {"left": 785, "top": 1045, "width": 150, "height": 160}  # 7 第四行右
]

TRAVERSE_PATH = [
    (0, 'd'), (1, 's'), (3, 'a'), (2, 's'), 
    (4, 'd'), (5, 's'), (7, 'a'), (6, None)
]


def load_templates():
    print("正在加载本地指纹模板，请稍候...")
    big_hashes = {}
    frag_hashes = {}

    for i in range(4):
        big_path = f"print_{i}.png"
        if os.path.exists(big_path):
            big_hashes[i] = imagehash.phash(Image.open(big_path))
        else:
            print(f"警告：未找到大指纹模板 {big_path}")

        frag_hashes[i] = []
        folder_path = str(i)
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    frag_path = os.path.join(folder_path, file_name)
                    frag_hashes[i].append(imagehash.phash(Image.open(frag_path)))
        else:
            print(f"警告：未找到碎片文件夹 {folder_path}/")
            
    print("模板加载完成！")
    return big_hashes, frag_hashes

BIG_HASHES, FRAG_HASHES = load_templates()


def get_screen_hash(sct, area):
    sct_img = sct.grab(area)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return imagehash.phash(img)


def solve_with_keys():
    if not BIG_HASHES:
        print("错误：由于未加载到任何大指纹模板，无法执行破解。")
        return

    with mss.mss() as sct:
        current_big_hash = get_screen_hash(sct, FINGER_PRINT)
        model_id = min(BIG_HASHES, key=lambda k: current_big_hash - BIG_HASHES[k])
        distance = current_big_hash - BIG_HASHES[model_id]

        print(f"锁定模板: {model_id} (距离: {distance})")
        target_frags = FRAG_HASHES.get(model_id, [])

        for current_idx, move_key in TRAVERSE_PATH:
            area = FRAGRANT[current_idx]
            current_frag_hash = get_screen_hash(sct, area)

            distances = [(current_frag_hash - t_hash) for t_hash in target_frags]
            min_dist = min(distances) if distances else 999
            
            print(f"检测碎片 {current_idx}: 最小距离 {min_dist}", end="")

            is_correct = False
            if min_dist < 22: 
                is_correct = True
                print(" -> [匹配成功!]")
            else:
                print(" -> [不匹配]")
            
            if is_correct:
                keyboard.press_and_release('enter')
                time.sleep(0.02)
            
            if move_key:
                keyboard.press_and_release(move_key)
                time.sleep(0.02)

        print("遍历完毕")
        time.sleep(0.02)
        keyboard.press_and_release('tab')

if __name__ == "__main__":
    print("-" * 30)
    print("GTA 名钻赌场指纹破解辅助 by Yank233 已启动")
    print("确保游戏窗口在前台，并且在指纹界面第一个指纹位置")
    print("快捷键：[F4] 执行破解  |  [ESC] 退出程序")
    print("-" * 30)
    
    keyboard.add_hotkey('f4', solve_with_keys)
    keyboard.wait('esc')
    print("程序已退出。")