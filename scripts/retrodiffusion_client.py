#!/usr/bin/env python3
"""
RetroDiffusion API client for Warcraft 1 / Forsaken Mod.
Integrates RetroDiffusion's pixel-art AI directly into the modding workflow:
- Account balance and credit checks
- Cost estimations (free dry runs)
- Image and sprite generation
- Quantization to Warcraft 1's 256-color palette [96..254]
"""

import os
import sys
import time
import json
import argparse
import requests
import numpy as np
from PIL import Image

DEFAULT_API_KEY = ""  # set RD_API_KEY in your environment
API_BASE = "https://api.retrodiffusion.ai/v2"

BASE_DIR = "/home/smiles/forsaken-mod"
REF_PAL_IMG = os.path.join(BASE_DIR, "graphics", "human", "units", "footman.png")


def get_api_key():
    return os.environ.get("RD_API_KEY", DEFAULT_API_KEY)


def get_headers():
    return {
        "X-RD-Token": get_api_key(),
        "Content-Type": "application/json",
    }


def check_balance():
    """Query account credits and USD balance."""
    url = f"{API_BASE}/inferences/credits"
    res = requests.get(url, headers=get_headers())
    if res.status_code != 200:
        print(f"Error checking balance ({res.status_code}): {res.text}")
        return None
    data = res.json()
    print("=== RetroDiffusion Account Status ===")
    print(f"Prepaid Balance: ${data.get('balance', 0.0):.2f}")
    print(f"Credits: {data.get('credits', 0)}")
    usage = data.get("usage", {})
    free = usage.get("free", {})
    print(f"Free units left: {free.get('units_left_pct', 0)}%")
    return data


def check_cost(prompt, width=256, height=256, prompt_style="rd_pro__default"):
    """Check cost of a prompt without spending balance."""
    url = f"{API_BASE}/inferences"
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_images": 1,
        "prompt_style": prompt_style,
        "check_cost": True,
    }
    res = requests.post(url, headers=get_headers(), json=payload)
    print(f"Cost check response ({res.status_code}): {res.text}")
    return res.json()


def generate_image(prompt, width=256, height=256, prompt_style="rd_pro__default", output_path=None):
    """Submits inference and polls until completion."""
    url = f"{API_BASE}/inferences"
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_images": 1,
        "prompt_style": prompt_style,
    }
    print(f"Submitting inference request: '{prompt}' ({width}x{height}, style: {prompt_style})...")
    res = requests.post(url, headers=get_headers(), json=payload)
    if res.status_code != 200:
        print(f"Inference submission failed ({res.status_code}): {res.text}")
        return None

    data = res.json()
    task_id = data.get("task_id")
    if not task_id:
        print(f"Unexpected response: {data}")
        return None

    print(f"Inference accepted. Task ID: {task_id}. Polling for completion...")

    # Poll task
    poll_url = f"{API_BASE}/inferences/tasks/{task_id}"
    while True:
        poll_res = requests.get(poll_url, headers=get_headers())
        if poll_res.status_code != 200:
            print(f"Polling error ({poll_res.status_code}): {poll_res.text}")
            return None

        task_data = poll_res.json()
        status = task_data.get("status")

        if status == "succeeded":
            print("Inference completed successfully!")
            output = task_data.get("output", {})
            images = output.get("images", [])
            if not images:
                print("No images returned in output.")
                return None

            img_url = images[0].get("url")
            print(f"Image URL: {img_url}")

            if output_path:
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"Saved generated image to {output_path}")
            return img_url

        elif status == "failed":
            err = task_data.get("error", {})
            print(f"Task failed: {err.get('code')}: {err.get('message')}")
            return None

        else:
            time.sleep(2)


def quantize_to_wc1(src_png_path, dst_png_path):
    """
    Quantizes an image to the strict Warcraft 1 unit palette [96..254] (transparency 255).
    Guarantees 0 pixels in [0..95] (prevents terrain animation flickering).
    """
    ref_im = Image.open(REF_PAL_IMG)
    ref_pal = ref_im.getpalette()

    im = Image.open(src_png_path).convert("RGBA")
    w, h = im.size
    px = im.load()

    out_arr = np.full((h, w), 255, dtype=np.uint8)

    # Precalculate unit palette colors (indices 96..254)
    unit_colors = []
    for i in range(96, 255):
        if 200 <= i <= 207:
            continue  # Reserve team colors
        unit_colors.append((i, ref_pal[i * 3], ref_pal[i * 3 + 1], ref_pal[i * 3 + 2]))

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 64:
                out_arr[y, x] = 255
            else:
                best_i = 96
                best_d = 10**9
                for idx, pr, pg, pb in unit_colors:
                    d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
                    if d < best_d:
                        best_d = d
                        best_i = idx
                out_arr[y, x] = best_i

    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(ref_pal)
    out_im.save(dst_png_path, format="PNG", transparency=255)
    print(f"Quantized {src_png_path} -> {dst_png_path} (Strict WC1 Palette, 0 bad pixels)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetroDiffusion API Client")
    subparsers = parser.add_subparsers(dest="command")

    # balance
    subparsers.add_parser("balance", help="Check account balance and credits")

    # cost
    cost_p = subparsers.add_parser("cost", help="Check generation cost")
    cost_p.add_argument("--prompt", required=True)
    cost_p.add_argument("--width", type=int, default=256)
    cost_p.add_argument("--height", type=int, default=256)
    cost_p.add_argument("--style", default="rd_pro__default")

    # generate
    gen_p = subparsers.add_parser("generate", help="Generate an image")
    gen_p.add_argument("--prompt", required=True)
    gen_p.add_argument("--width", type=int, default=256)
    gen_p.add_argument("--height", type=int, default=256)
    gen_p.add_argument("--style", default="rd_pro__default")
    gen_p.add_argument("--out", required=True)
    gen_p.add_argument("--quantize", action="store_true")

    args = parser.parse_args()

    if args.command == "balance":
        check_balance()
    elif args.command == "cost":
        check_cost(args.prompt, args.width, args.height, args.style)
    elif args.command == "generate":
        tmp_out = args.out if not args.quantize else f"{args.out}.raw.png"
        res = generate_image(args.prompt, args.width, args.height, args.style, tmp_out)
        if res and args.quantize:
            quantize_to_wc1(tmp_out, args.out)
    else:
        parser.print_help()
