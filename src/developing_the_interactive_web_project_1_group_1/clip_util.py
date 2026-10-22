import clip
import numpy as np
import torch
from PIL import Image
from pillow_heif import register_heif_opener
import time
import os
register_heif_opener()

device = "cpu" 
print("Using:", device)

model_name = "ViT-B/32"
print("loading mdoel ")
cache_dir = "./.cache/torch"
os.makedirs(cache_dir, exist_ok=True)
model, preprocess = clip.load(model_name, device=device, download_root=cache_dir)
print("loaded mdoel ")

model.eval()

def embed_text(q):
    s = time.monotonic()
    print("EMbed:starting ")
    txt = clip.tokenize([q]).to(device)
    print(f"EMbed:tokenized{time.monotonic()-s} ")

    with torch.inference_mode():
        txt_emd = model.encode_text(txt)
    print(f"encoded: in {time.monotonic()-s} ")
    
    txt_emd = txt_emd.float()
    txt_emd = txt_emd/txt_emd.norm(dim=-1, keepdim= True)
    return txt_emd.cpu().numpy()[0].astype(np.float32)

def embed_img(img):
    image = preprocess(Image.open(img).convert("RGB")).unsqueeze(0).to(device)
    with torch.inference_mode():
        raw_image_embeddings = model.encode_image(image).float()
        image_embeddings = raw_image_embeddings / raw_image_embeddings.norm(dim=1, keepdim=True)
    return image_embeddings.cpu().numpy()[0].astype(np.float32)

if __name__ == '__main__':
    print(embed_text("works").shape)