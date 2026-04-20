import os
import requests
from PIL import Image

def download_image(image_url, save_path):
    """
    下载图片 / Download image
    """
    try:
        image_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Referer': 'https://www.javbus.com/',
        }
        
        response = requests.get(image_url, headers=image_headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"图片下载失败 / Failed to download image {image_url}: {e}")
        return False

def create_poster_from_fanart(fanart_path, poster_path):
    """
    从 fanart 裁剪 poster (右半部分) / Crop poster from fanart (right half)
    """
    try:
        with Image.open(fanart_path) as img:
            width, height = img.size
            left = width // 2
            right = width
            cropped = img.crop((left, 0, right, height))
            cropped.save(poster_path)
        return True
    except Exception as e:
        print(f"创建 poster 失败 / Failed to create poster: {e}")
        return False

def process_pics(vid_id, pics_dir, image_url):
    """
    处理图片的主流程 / Main process for handling pictures
    """
    result = {
        'pics_status': '失败',
        'javbus_image_url': image_url or ''
    }
    
    if not image_url:
        print(f"无图片链接 / No image url provided for {vid_id}")
        return result
        
    fanart_path = os.path.join(pics_dir, f"{vid_id}-fanart.jpg")
    poster_path = os.path.join(pics_dir, f"{vid_id}-poster.jpg")
    
    if download_image(image_url, fanart_path):
        if create_poster_from_fanart(fanart_path, poster_path):
            result['pics_status'] = '成功'
        else:
            print(f"海报生成失败 / Failed to generate poster for {vid_id}")
            
    return result
