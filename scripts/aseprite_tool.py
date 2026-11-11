#!/usr/bin/env python3
"""
Aseprite (.ase / .aseprite) format parser, packer, and Stratagus spritesheet compiler.
Specification: https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
"""

import os
import sys
import struct
import zlib
import numpy as np
from PIL import Image

ASE_MAGIC_FILE = 0xA5E0
ASE_MAGIC_FRAME = 0xF1FA

CHUNK_LAYER = 0x2004
CHUNK_CEL = 0x2005
CHUNK_TAGS = 0x2018
CHUNK_PALETTE = 0x2019


def write_aseprite(path, frames, width, height, palette, tags=None, frame_duration_ms=100):
    """
    Writes an 8-bit indexed .aseprite file.
    frames: list of bytes or bytearrays, each of length width * height (palette indices 0..255).
    palette: list or tuple of 768 ints (R, G, B for 256 colors).
    tags: optional list of (tag_name, from_frame, to_frame).
    """
    num_frames = len(frames)
    frame_datas = []

    for f_idx, frame_raw in enumerate(frames):
        chunks = []
        if f_idx == 0:
            # Chunk 1: Palette chunk (0x2019)
            pal_payload = bytearray()
            pal_payload += struct.pack('<III', 256, 0, 255)
            pal_payload += b'\x00' * 8  # reserved
            for i in range(256):
                r = palette[i * 3]
                g = palette[i * 3 + 1]
                b = palette[i * 3 + 2]
                a = 0 if i == 255 else 255
                pal_payload += struct.pack('<HBBBB', 0, r, g, b, a)
            pal_chunk = struct.pack('<IH', len(pal_payload) + 6, CHUNK_PALETTE) + pal_payload
            chunks.append(pal_chunk)

            # Chunk 2: Layer chunk (0x2004)
            layer_payload = bytearray()
            layer_name = 'Sprite'.encode('utf-8')
            layer_payload += struct.pack('<HHHHHB', 3, 0, 0, width, height, 0)  # visible & editable
            layer_payload += struct.pack('<B', 255)  # opacity
            layer_payload += b'\x00' * 3
            layer_payload += struct.pack('<H', len(layer_name)) + layer_name
            layer_chunk = struct.pack('<IH', len(layer_payload) + 6, CHUNK_LAYER) + layer_payload
            chunks.append(layer_chunk)

            # Chunk 3: Tags chunk (0x2018)
            if tags:
                tag_payload = bytearray()
                tag_payload += struct.pack('<H', len(tags))
                tag_payload += b'\x00' * 8
                for t_name, t_from, t_to in tags:
                    tn_bytes = t_name.encode('utf-8')
                    tag_payload += struct.pack('<HHBH', t_from, t_to, 0, 0)  # loop forward
                    tag_payload += b'\x00' * 6
                    tag_payload += b'\x40\x60\x80\x00'  # muted blue tag color
                    tag_payload += struct.pack('<H', len(tn_bytes)) + tn_bytes
                tag_chunk = struct.pack('<IH', len(tag_payload) + 6, CHUNK_TAGS) + tag_payload
                chunks.append(tag_chunk)

        # Cel chunk (0x2005) - compressed image
        compressed = zlib.compress(bytes(frame_raw))
        cel_payload = bytearray()
        cel_payload += struct.pack('<HhhBHh', 0, 0, 0, 255, 2, 0)  # layer=0, pos=(0,0), type=2 (zlib)
        cel_payload += b'\x00' * 5
        cel_payload += struct.pack('<HH', width, height)
        cel_payload += compressed
        cel_chunk = struct.pack('<IH', len(cel_payload) + 6, CHUNK_CEL) + cel_payload
        chunks.append(cel_chunk)

        # Assemble frame
        frame_body = b''.join(chunks)
        frame_len = len(frame_body) + 16
        # Frame Header: DWORD size, WORD magic (0xF1FA), WORD old_chunks, WORD duration_ms, 2 bytes zero, DWORD new_chunks
        frame_header = struct.pack('<IHHH2sI', frame_len, ASE_MAGIC_FRAME, len(chunks), frame_duration_ms, b'\x00\x00', 0)
        frame_datas.append(frame_header + frame_body)

    all_frames = b''.join(frame_datas)
    file_size = 128 + len(all_frames)
    header = bytearray(128)
    struct.pack_into('<IH', header, 0, file_size, ASE_MAGIC_FILE)
    struct.pack_into('<HHH', header, 6, num_frames, width, height)
    struct.pack_into('<H', header, 12, 8)  # 8 bpp indexed
    struct.pack_into('<I', header, 14, 1)  # flags
    struct.pack_into('<H', header, 18, frame_duration_ms)
    header[28] = 255  # transparent index
    struct.pack_into('<H', header, 32, 256)
    header[34] = 1
    header[35] = 1

    with open(path, 'wb') as f:
        f.write(header)
        f.write(all_frames)


def read_aseprite(path):
    """
    Parses an 8-bit indexed .aseprite file.
    Returns: (width, height, palette, frames, tags)
    where frames is a list of bytearrays (each w*h bytes)
    """
    with open(path, 'rb') as f:
        data = f.read()

    file_size, magic, num_frames, w, h, bpp = struct.unpack_from('<IHHHHH', data, 0)
    if magic != ASE_MAGIC_FILE:
        raise ValueError(f"Invalid Aseprite magic number: {hex(magic)}")
    if bpp != 8:
        raise ValueError(f"Only 8-bpp indexed Aseprite files supported (got {bpp} bpp)")

    offset = 128
    palette = [0] * 768
    frames = []
    tags = []

    for _ in range(num_frames):
        frame_len, frame_magic, chunk_count, dur, _, new_chunks = struct.unpack_from('<IHHH2sI', data, offset)
        if frame_magic != ASE_MAGIC_FRAME:
            raise ValueError(f"Invalid frame magic: {hex(frame_magic)}")
        if chunk_count == 0xFFFF and new_chunks > 0:
            chunk_count = new_chunks

        chunk_offset = offset + 16
        frame_pixel_data = bytearray(w * h)

        for _ in range(chunk_count):
            chunk_size, chunk_type = struct.unpack_from('<IH', data, chunk_offset)
            payload = data[chunk_offset + 6: chunk_offset + chunk_size]

            if chunk_type == CHUNK_PALETTE:
                n_colors, first_idx, last_idx = struct.unpack_from('<III', payload, 0)
                pal_pos = 20
                for c_idx in range(first_idx, last_idx + 1):
                    _, r, g, b, _ = struct.unpack_from('<HBBBB', payload, pal_pos)
                    palette[c_idx * 3] = r
                    palette[c_idx * 3 + 1] = g
                    palette[c_idx * 3 + 2] = b
                    pal_pos += 6

            elif chunk_type == CHUNK_TAGS:
                try:
                    n_tags = struct.unpack_from('<H', payload, 0)[0]
                    t_pos = 10
                    for _ in range(n_tags):
                        if t_pos + 15 > len(payload):
                            break
                        t_from, t_to, loop_dir, repeat = struct.unpack_from('<HHBH', payload, t_pos)
                        name_len = struct.unpack_from('<H', payload, t_pos + 13)[0]
                        t_name = payload[t_pos + 15: t_pos + 15 + name_len].decode('utf-8', errors='replace')
                        tags.append((t_name, t_from, t_to))
                        t_pos += 15 + name_len
                except Exception:
                    pass

            elif chunk_type == CHUNK_CEL:
                _, _, _, _, cel_type, _ = struct.unpack_from('<HhhBHh', payload, 0)
                if cel_type == 2:  # zlib compressed
                    cel_w, cel_h = struct.unpack_from('<HH', payload, 16)
                    comp_data = payload[20:]
                    decomp = zlib.decompress(comp_data)
                    frame_pixel_data[:len(decomp)] = decomp

            chunk_offset += chunk_size

        frames.append(frame_pixel_data)
        offset += frame_len

    return w, h, palette, frames, tags


def compile_aseprite_to_sheet(ase_path, png_path, unit_type):
    """
    Compiles an .aseprite file into a Stratagus interleaved unit spritesheet PNG.
    unit_type: 'ghoul' (15 rows, 32x32), 'crypt-fiend' (14 rows, 32x32), 'abomination' (15 rows, 48x48)
    """
    w, h, palette, frames, _ = read_aseprite(ase_path)

    # Frame mapping
    if unit_type in ("ghoul", "abomination"):
        # 15 rows of 5 cols = 75 frames
        # Row 0, 3, 6, 9, 12 = Move 0..4 (5 dirs each)
        # Row 1, 4, 7, 10, 13 = Attack 0..4 (5 dirs each)
        # Row 2, 5, 8, 11, 14 = Death 0..4 (5 dirs each)
        n_rows = 15
        n_cols = 5
        sheet_w = n_cols * w
        sheet_h = n_rows * h
        out_arr = np.full((sheet_h, sheet_w), 255, dtype=np.uint8)

        # In standard sequential tag layout:
        # Frames 0..24: Walk (5 steps x 5 dirs) -> step s, dir d -> index s*5 + d
        # Frames 25..49: Attack (5 steps x 5 dirs) -> step s, dir d -> index 25 + s*5 + d
        # Frames 50..74: Death (5 steps x 5 dirs) -> step s, dir d -> index 50 + s*5 + d
        move_rows = [0, 3, 6, 9, 12]
        attack_rows = [1, 4, 7, 10, 13]
        death_rows = [2, 5, 8, 11, 14]

        for s in range(5):
            r_move = move_rows[s]
            r_atk = attack_rows[s]
            r_die = death_rows[s]

            for d in range(5):
                # Move
                f_idx_move = s * 5 + d
                if f_idx_move < len(frames):
                    tile = np.frombuffer(frames[f_idx_move], dtype=np.uint8).reshape((h, w))
                    out_arr[r_move * h:(r_move + 1) * h, d * w:(d + 1) * w] = tile

                # Attack
                f_idx_atk = 25 + s * 5 + d
                if f_idx_atk < len(frames):
                    tile = np.frombuffer(frames[f_idx_atk], dtype=np.uint8).reshape((h, w))
                    out_arr[r_atk * h:(r_atk + 1) * h, d * w:(d + 1) * w] = tile

                # Death
                f_idx_die = 50 + s * 5 + d
                if f_idx_die < len(frames):
                    tile = np.frombuffer(frames[f_idx_die], dtype=np.uint8).reshape((h, w))
                    out_arr[r_die * h:(r_die + 1) * h, d * w:(d + 1) * w] = tile

    elif unit_type == "crypt-fiend":
        # 14 rows of 5 cols = 70 frames
        # Move: rows [0, 3, 6, 9, 12] (5 steps)
        # Attack: rows [1, 4, 7, 10] (4 steps)
        # Death: rows [2, 5, 8, 11, 13] (5 steps)
        n_rows = 14
        n_cols = 5
        sheet_w = n_cols * w
        sheet_h = n_rows * h
        out_arr = np.full((sheet_h, sheet_w), 255, dtype=np.uint8)

        move_rows = [0, 3, 6, 9, 12]
        attack_rows = [1, 4, 7, 10]
        death_rows = [2, 5, 8, 11, 13]

        for s in range(5):
            r_move = move_rows[s]
            for d in range(5):
                f_idx = s * 5 + d
                if f_idx < len(frames):
                    tile = np.frombuffer(frames[f_idx], dtype=np.uint8).reshape((h, w))
                    out_arr[r_move * h:(r_move + 1) * h, d * w:(d + 1) * w] = tile

        for s in range(4):
            r_atk = attack_rows[s]
            for d in range(5):
                f_idx = 25 + s * 5 + d
                if f_idx < len(frames):
                    tile = np.frombuffer(frames[f_idx], dtype=np.uint8).reshape((h, w))
                    out_arr[r_atk * h:(r_atk + 1) * h, d * w:(d + 1) * w] = tile

        for s in range(5):
            r_die = death_rows[s]
            for d in range(5):
                f_idx = 45 + s * 5 + d
                if f_idx < len(frames):
                    tile = np.frombuffer(frames[f_idx], dtype=np.uint8).reshape((h, w))
                    out_arr[r_die * h:(r_die + 1) * h, d * w:(d + 1) * w] = tile

    im = Image.fromarray(out_arr, mode='P')
    im.putpalette(palette)
    im.save(png_path, format='PNG', transparency=255)
    print(f"Compiled {ase_path} -> {png_path} ({im.size})")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 aseprite_tool.py compile <file.aseprite> <file.png> --type <ghoul|crypt-fiend|abomination>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "compile":
        ase_in = sys.argv[2]
        png_out = sys.argv[3]
        u_type = "ghoul"
        if "--type" in sys.argv:
            idx = sys.argv.index("--type")
            u_type = sys.argv[idx + 1]
        compile_aseprite_to_sheet(ase_in, png_out, u_type)
