#!/usr/bin/env python3
"""
Synthesize spoken Undead Scourge / Lich King voiceover narration for all 12
campaign mission briefings (01_intro.txt .. 12_intro.txt) and the victory
epilogue (ending_1.txt) using espeak-ng + ffmpeg DSP processing.
"""

import gzip
import os
import subprocess
import tempfile

BASE_DIR = "/home/smiles/forsaken-mod"
CAMP_DIR = os.path.join(BASE_DIR, "campaigns", "forsaken")


def synthesize_scourge_voice(text_path, out_wav_gz_path):
    with open(text_path, "r") as f:
        text = f.read().strip()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_raw, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_proc:
        raw_path = tmp_raw.name
        proc_path = tmp_proc.name

    try:
        # 1. Generate base speech with espeak-ng (Received Pronunciation, deep pitch, deliberate cadence)
        subprocess.run(
            [
                "espeak-ng",
                "-v", "en-gb-x-rp",
                "-p", "22",
                "-s", "142",
                "-w", raw_path,
                text,
            ],
            check=True,
        )

        # 2. Apply dark Lich King / Scourge DSP filter chain via ffmpeg:
        #    - Darken formant/pitch slightly (0.86x)
        #    - Add dual-voice spectral echo/reverb (aecho)
        #    - Warm low-end boost & smooth high-pass/low-pass for WC1 11025Hz u8 PCM format
        af_chain = (
            "asetrate=22050*0.86,aresample=22050,"
            "aecho=0.85:0.78:32|68:0.30|0.18,"
            "highpass=f=70,lowpass=f=4500,"
            "volume=1.6"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", raw_path,
                "-af", af_chain,
                "-ar", "11025",
                "-ac", "1",
                "-acodec", "pcm_u8",
                proc_path,
            ],
            check=True,
        )

        # 3. Compress to .wav.gz matching War1gus's campaign audio format
        with open(proc_path, "rb") as f_in, gzip.open(out_wav_gz_path, "wb") as f_out:
            f_out.write(f_in.read())

        print(f"Generated spoken narration: {os.path.basename(out_wav_gz_path)} ({os.path.getsize(out_wav_gz_path)} bytes)")
    finally:
        for p in (raw_path, proc_path):
            if os.path.exists(p):
                os.remove(p)


def main():
    for i in range(1, 13):
        mid = f"{i:02d}"
        txt_path = os.path.join(CAMP_DIR, f"{mid}_intro.txt")
        wav_gz_path = os.path.join(CAMP_DIR, f"{mid}_intro.wav.gz")
        synthesize_scourge_voice(txt_path, wav_gz_path)

    ending_txt = os.path.join(CAMP_DIR, "ending_1.txt")
    ending_wav_gz = os.path.join(CAMP_DIR, "ending_1.wav.gz")
    synthesize_scourge_voice(ending_txt, ending_wav_gz)
    print("All 12 mission intro voiceovers + ending narration generated successfully!")


if __name__ == "__main__":
    main()
