#!/usr/bin/env python3
"""
Build Authentic Warcraft-Style Scourge Victory & Defeat Fanfares
===============================================================
Synthesizes cinematic, gothic, and chilling audio for Scourge / Forsaken
victory and defeat sequences:
1. Deep, inharmonic Cathedral Death Bell knells (physical acoustics model).
2. Thunderous War Drum / Timpani impacts with sub-bass resonance.
3. Dark spectral choral swells (D minor harmonic pad).
4. Haunting, cavernous Necromancer / Lich vocal proclamations.
5. Mournful funeral knells, sorrowful weeping crypt winds, and dying chimes.

Formatted in Warcraft 1 native 11,025 Hz 8-bit unsigned mono PCM (.wav.gz).
"""

import gzip
import os
import subprocess
import tempfile
import wave
import numpy as np

BASE_DIR = "/home/smiles/forsaken-mod"
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds", "forsaken")
SR = 11025


def ensure_dirs():
    os.makedirs(SOUNDS_DIR, exist_ok=True)


def gen_cathedral_bell(dur=5.0, f0=110.0, strike_power=1.0):
    """
    Synthesize authentic inharmonic cathedral bell resonance.
    Partials: Hum (0.5), Prime (1.0), Minor Third (1.19), Quint (1.51),
    Nominal (2.0), Decime (2.74), Upper (4.07).
    """
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    partials = [
        (0.5, 0.45, 1.1),
        (1.0, 0.70, 1.6),
        (1.19, 0.65, 1.9),
        (1.51, 0.45, 2.4),
        (2.0, 0.50, 2.9),
        (2.74, 0.35, 3.6),
        (4.07, 0.25, 4.8),
    ]
    sig = np.zeros(n_samples)
    for ratio, amp, decay in partials:
        freq = f0 * ratio
        partial_wave = np.sin(2 * np.pi * freq * t)
        env = np.exp(-decay * t)
        sig += partial_wave * amp * env

    # Metal strike transient
    trans_len = min(int(0.04 * SR), n_samples)
    sig[:trans_len] += (
        np.random.randn(trans_len) * np.linspace(1, 0, trans_len) ** 2 * (0.5 * strike_power)
    )
    return sig


def gen_war_drum(dur=2.5, f_start=95.0, f_end=35.0, decay_rate=3.0):
    """Deep thunderous war drum / timpani impact."""
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    pitch_env = f_start * (f_end / f_start) ** (np.minimum(t, 0.3) / 0.3)
    phase = 2 * np.pi * np.cumsum(pitch_env) / SR
    sub = np.sin(phase) * np.exp(-decay_rate * t)
    noise = np.random.randn(n_samples) * np.exp(-14.0 * t) * 0.45
    return sub + noise


def gen_spectral_choir(dur=5.0, freqs=(146.83, 174.61, 220.0, 293.66)):
    """Dark spectral choral pad swell in D minor."""
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    pad = np.zeros(n_samples)
    for f in freqs:
        for detune in [-0.8, 0.0, 0.8]:
            pad += np.sin(2 * np.pi * (f + detune) * t) * 0.18

    # Swell envelope
    att = int(0.6 * SR)
    env = np.ones(n_samples)
    env[:att] = np.linspace(0, 1, att)
    env[att:] = np.exp(-0.65 * (t[att:] - 0.6))
    return pad * env


def gen_mournful_wind(dur=6.0):
    """Eerie, desolate weeping wind for defeat."""
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    # Slow gentle swell
    wind_env = np.sin(np.pi * t / dur) ** 1.3
    # Low howling resonance
    howl1 = np.sin(2 * np.pi * (135 + 25 * np.sin(2 * np.pi * 0.35 * t)) * t) * 0.22
    howl2 = np.sin(2 * np.pi * (92 + 15 * np.sin(2 * np.pi * 0.2 * t)) * t) * 0.18
    noise = np.random.randn(n_samples) * 0.25
    return (noise + howl1 + howl2) * wind_env


def synthesize_scourge_voice(text, speed=135, pitch=28):
    """Synthesize deep, commanding, cavernous Scourge proclamation."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_raw, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_proc:
        raw_path = f_raw.name
        proc_path = f_proc.name

    try:
        # Base speech
        cmd_espeak = [
            "espeak-ng", "-v", "en-us+Demonic", "-p", str(pitch), "-s", str(speed),
            "-w", raw_path, text,
        ]
        res = subprocess.run(cmd_espeak, stderr=subprocess.PIPE)
        if res.returncode != 0:
            # Fallback voice
            subprocess.run(
                ["espeak-ng", "-v", "en-gb-x-rp", "-p", str(pitch), "-s", str(speed), "-w", raw_path, text],
                check=True,
            )

        # Cavernous gothic DSP
        dsp = (
            "asetrate=22050*0.78,aresample=22050,"
            "equalizer=f=120:width_type=h:w=80:g=6,"
            "equalizer=f=2800:width_type=h:w=600:g=5,"
            "aecho=0.85:0.7:35|70:0.4|0.25,"
            "compand=attacks=0.01:decays=0.1:points=-70/-70|-20/-8|0/-2:gain=5,"
            f"aresample={SR}"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw_path, "-af", dsp, proc_path],
            check=True,
            stderr=subprocess.DEVNULL,
        )

        with wave.open(proc_path, "rb") as w:
            frames = w.readframes(w.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        return audio

    finally:
        for p in (raw_path, proc_path):
            if os.path.exists(p):
                os.remove(p)


def save_wav_gz(pcm_u8_bytes, out_path_gz):
    """Write standard 11025Hz 1-channel 8-bit unsigned PCM as .wav.gz."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    try:
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(1)
            w.setframerate(SR)
            w.writeframes(pcm_u8_bytes)

        with open(wav_path, "rb") as f_in, gzip.open(out_path_gz, "wb") as f_out:
            f_out.write(f_in.read())
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


def build_victory_1():
    """
    Victory 1:
    - 0.0s: Thunderous War Drum strike + Low D Cathedral Bell (110 Hz).
    - 0.4s: Spectral D minor choir pad swell.
    - 1.1s: Booming proclamation: 'Victory for the Scourge!'
    - 2.2s: Second Bell knell (F = 130.8 Hz).
    - 3.5s - 5.5s: Trailing bell harmonics and ghostly wind fadeout.
    """
    dur = 5.5
    n_samples = int(dur * SR)
    mix = np.zeros(n_samples)

    # 1. War drum at t=0s
    drum = gen_war_drum(dur=2.5, f_start=95.0, f_end=35.0)
    mix[: len(drum)] += drum * 0.75

    # 2. First bell at t=0s (D3 = 110 Hz)
    bell1 = gen_cathedral_bell(dur=4.8, f0=110.0, strike_power=1.1)
    mix[: len(bell1)] += bell1 * 0.55

    # 3. Spectral choir pad at t=0.3s
    choir = gen_spectral_choir(dur=4.5)
    c_idx = int(0.3 * SR)
    mix[c_idx : c_idx + len(choir)] += choir * 0.40

    # 4. Voice at t=1.0s
    voice = synthesize_scourge_voice("Victory for the Scourge!", speed=135, pitch=28)
    v_idx = int(1.0 * SR)
    v_len = min(len(voice), n_samples - v_idx)
    mix[v_idx : v_idx + v_len] += voice[:v_len] * 0.95

    # 5. Second bell at t=2.2s (F3 = 130.8 Hz)
    bell2 = gen_cathedral_bell(dur=3.2, f0=130.81, strike_power=0.85)
    b2_idx = int(2.2 * SR)
    mix[b2_idx : b2_idx + len(bell2)] += bell2 * 0.45

    # Master
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.96

    u8 = ((mix * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()
    dst = os.path.join(SOUNDS_DIR, "victory_1.wav.gz")
    save_wav_gz(u8, dst)
    print(f"Generated Scourge Victory 1 ({dur}s): {dst}")


def build_victory_2():
    """
    Victory 2:
    - 0.0s: Double iron bell knell + timpani roll.
    - 0.8s: Dark triumphant minor organ/choir swell.
    - 1.1s: Malevolent voice: 'The living have perished!'
    - 2.4s: Low thunder strike & feral beast roar.
    - 3.5s - 5.2s: Fading reverb.
    """
    dur = 5.2
    n_samples = int(dur * SR)
    mix = np.zeros(n_samples)

    # 1. Bells at t=0s and t=0.4s
    bell1 = gen_cathedral_bell(dur=4.5, f0=98.0, strike_power=1.0)
    mix[: len(bell1)] += bell1 * 0.50

    drum = gen_war_drum(dur=2.0, f_start=80.0, f_end=32.0)
    mix[: len(drum)] += drum * 0.70

    # 2. Choir
    choir = gen_spectral_choir(dur=4.2, freqs=(130.81, 164.81, 196.0, 261.63))  # C minor
    c_idx = int(0.4 * SR)
    mix[c_idx : c_idx + len(choir)] += choir * 0.38

    # 3. Voice
    voice = synthesize_scourge_voice("The living have perished!", speed=130, pitch=26)
    v_idx = int(1.1 * SR)
    v_len = min(len(voice), n_samples - v_idx)
    mix[v_idx : v_idx + v_len] += voice[:v_len] * 0.95

    # 4. Third bell at t=2.3s
    bell2 = gen_cathedral_bell(dur=2.8, f0=146.83, strike_power=0.8)
    b2_idx = int(2.3 * SR)
    mix[b2_idx : b2_idx + len(bell2)] += bell2 * 0.40

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.96

    u8 = ((mix * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()
    dst = os.path.join(SOUNDS_DIR, "victory_2.wav.gz")
    save_wav_gz(u8, dst)
    print(f"Generated Scourge Victory 2 ({dur}s): {dst}")


def build_victory_3():
    """
    Victory 3:
    - 0.0s: Heavy bronze death bell + thunderous drum impact.
    - 0.5s: Choral harmony.
    - 1.0s: Voice: 'Lordaeron falls before the Scourge!'
    - 2.5s: Resonant tolling chime.
    """
    dur = 5.6
    n_samples = int(dur * SR)
    mix = np.zeros(n_samples)

    drum = gen_war_drum(dur=2.8, f_start=105.0, f_end=32.0)
    mix[: len(drum)] += drum * 0.75

    bell1 = gen_cathedral_bell(dur=5.0, f0=110.0, strike_power=1.1)
    mix[: len(bell1)] += bell1 * 0.55

    choir = gen_spectral_choir(dur=4.6)
    c_idx = int(0.5 * SR)
    mix[c_idx : c_idx + len(choir)] += choir * 0.40

    voice = synthesize_scourge_voice("Lordaeron falls before the Scourge!", speed=138, pitch=27)
    v_idx = int(1.0 * SR)
    v_len = min(len(voice), n_samples - v_idx)
    mix[v_idx : v_idx + v_len] += voice[:v_len] * 0.95

    bell2 = gen_cathedral_bell(dur=3.0, f0=82.4, strike_power=0.9)  # Deep low E bell
    b2_idx = int(2.5 * SR)
    mix[b2_idx : b2_idx + len(bell2)] += bell2 * 0.45

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.96

    u8 = ((mix * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()
    dst = os.path.join(SOUNDS_DIR, "victory_3.wav.gz")
    save_wav_gz(u8, dst)
    print(f"Generated Scourge Victory 3 ({dur}s): {dst}")


def build_defeat():
    """
    Defeat:
    - 0.0s: Muffled, mournful single funeral knell in desolate crypt wind.
    - 0.6s: Weeping wind howling in low register.
    - 1.2s: Somber, ghostly, sorrowful whisper: 'The shadows... recede...'
    - 3.2s: Second distant, fading funeral knell.
    - 4.0s - 6.2s: Wind sighing and fading into crypt silence.
    """
    dur = 6.2
    n_samples = int(dur * SR)
    mix = np.zeros(n_samples)

    # 1. Weeping crypt wind across the whole duration
    wind = gen_mournful_wind(dur=6.0)
    mix[: len(wind)] += wind * 0.65

    # 2. Mournful low funeral bell at t=0s (muffled, f0=73.4 Hz, low D)
    bell1 = gen_cathedral_bell(dur=5.5, f0=73.41, strike_power=0.7)
    mix[: len(bell1)] += bell1 * 0.45

    # 3. Defeat voice (haunting, slow, tragic)
    voice = synthesize_scourge_voice("The shadows... recede... We shall return...", speed=115, pitch=22)
    v_idx = int(1.2 * SR)
    v_len = min(len(voice), n_samples - v_idx)
    mix[v_idx : v_idx + v_len] += voice[:v_len] * 0.92

    # 4. Distant lonely bell knell at t=3.4s
    bell2 = gen_cathedral_bell(dur=2.6, f0=65.4, strike_power=0.5)  # low C
    b2_idx = int(3.4 * SR)
    mix[b2_idx : b2_idx + len(bell2)] += bell2 * 0.35

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.95

    u8 = ((mix * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()
    dst = os.path.join(SOUNDS_DIR, "defeat.wav.gz")
    save_wav_gz(u8, dst)
    print(f"Generated Scourge Defeat ({dur}s): {dst}")


def main():
    ensure_dirs()
    print("Synthesizing authentic Scourge Victory & Defeat fanfares...")
    build_victory_1()
    build_victory_2()
    build_victory_3()
    build_defeat()
    print("\nALL SCOURGE VICTORY & DEFEAT FANFARES BUILT SUCCESSFULLY!")


if __name__ == "__main__":
    main()
