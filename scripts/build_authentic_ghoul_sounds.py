#!/usr/bin/env python3
"""
Build Authentic Warcraft-Style Ghoul Sound Effects & Voice Lines
===============================================================
Generates high-fidelity, organic, rabid, and terrifying Ghoul audio for the
Scourge faction in Stratagus / Warcraft 1.

Replaces the previous artificial FM-synth buzzer and monotone TTS with:
1. Physical Glottal Pulse & Vocal Tract Acoustic Modeling:
   - Asymmetric Rosenberg glottal excitation with period-doubling (false vocal cords)
     creating genuine death-metal gravel / throat rasp.
   - Turbulent air aspiration modulated synchronously by the glottal cycle.
   - Cascaded formant filters (F1=380Hz, F2=1050Hz, F3=2500Hz, F4=3300Hz) modeling
     a constricted, rotted undead vocal tract.
   - Wet salivary clicks, foaming jaw snaps, and gnashing teeth transients.
2. Frantic, Rabid Ghoul Voice Lines (Vasily Firsov WC3 delivery):
   - "Me hungry!"
   - "Me eat dead people!"
   - "Me eat brains!"
   - "No guts, no gory!"
   - "Fresh meat!"
   - "Rip and tear!"
   - "Tear flesh!"
   - "Me scary! Stop poking!"
   - "Leave alone! Me bite you!"
3. Visceral Beast Sounds:
   - Leaping combat bark / snarl
   - Savage biting combat growl
   - Spine-chilling rising undead howl for Ready
   - Enraged foaming chitter-snarl for Annoyed
   - Agonizing wet throat death rattle & gargling corpse drop
"""

import gzip
import os
import subprocess
import tempfile
import wave
import numpy as np

BASE_DIR = "/home/smiles/forsaken-mod"
GHOUL_DIR = os.path.join(BASE_DIR, "sounds", "forsaken", "ghoul")
SR = 11025


def ensure_dir():
    os.makedirs(GHOUL_DIR, exist_ok=True)


def biquad_peaking(x, sr, f0, bw, gain_db):
    """Parametric peaking equalizer biquad filter."""
    if f0 >= sr / 2:
        return x
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / sr
    alpha = np.sin(w0) * np.sinh(np.log(2.0) / 2.0 * bw * w0 / np.sin(w0))
    b0 = 1.0 + alpha * A
    b1 = -2.0 * np.cos(w0)
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * np.cos(w0)
    a2 = 1.0 - alpha / A

    b = np.array([b0, b1, b2]) / a0
    a = np.array([a0, a1, a2]) / a0

    y = np.zeros_like(x)
    for i in range(2, len(x)):
        y[i] = b[0] * x[i] + b[1] * x[i - 1] + b[2] * x[i - 2] - a[1] * y[i - 1] - a[2] * y[i - 2]
    return y


def apply_ghoul_vocal_tract(x, sr=SR):
    """Run excitation through undead vocal tract formant resonators."""
    # F1 pharyngeal throat resonance (~380 Hz)
    y = biquad_peaking(x, sr, 380, 1.2, 14.0)
    # F2 oral cavity resonance (~1050 Hz)
    y = biquad_peaking(y, sr, 1050, 1.0, 11.0)
    # F3 teeth / mouth front snarl (~2500 Hz)
    y = biquad_peaking(y, sr, 2500, 0.8, 9.0)
    # F4 epilarynx bite (~3300 Hz)
    y = biquad_peaking(y, sr, 3300, 0.8, 8.0)
    return y


def gen_organic_snarl(dur=0.85, f0_start=75, f0_end=110, rasp=0.85, snap_times=(0.08,)):
    """
    Synthesize physical acoustic undead growl / snarl with false cord flutter,
    breath turbulence, and salivary tooth clicks.
    """
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    f0_env = np.linspace(f0_start, f0_end, n_samples)
    jitter = 0.04 * np.sin(2 * np.pi * 11 * t) + 0.025 * np.random.randn(n_samples)
    inst_f0 = f0_env * (1.0 + jitter)

    phase = 0.0
    sub_toggle = 0
    sig = np.zeros(n_samples)

    for i in range(n_samples):
        phase += inst_f0[i] / SR
        if phase >= 1.0:
            phase -= 1.0
            sub_toggle = 1 - sub_toggle

        # Rosenberg glottal pulse
        if phase < 0.6:
            p = 0.5 * (1.0 - np.cos(np.pi * phase / 0.6))
        elif phase < 0.8:
            p = np.cos(0.5 * np.pi * (phase - 0.6) / 0.2)
        else:
            p = 0.0

        # Subharmonic false cord rumble
        if sub_toggle == 1:
            p *= (1.0 - 0.48 * rasp)

        # Modulated aspiration turbulence
        turb = np.random.randn() * p * 0.45 * rasp
        sig[i] = p * 0.6 + turb

    # Envelope
    att = max(1, int(0.04 * SR))
    rel = max(1, int(0.14 * SR))
    env = np.ones(n_samples)
    env[:att] = np.linspace(0, 1, att) ** 1.5
    env[-rel:] = np.linspace(1, 0, rel) ** 2

    # Throat flutter
    tremor = 1.0 + 0.3 * np.sin(2 * np.pi * 32 * t)
    sig = sig * env * tremor

    # Salivary snaps
    for st in snap_times:
        s_idx = int(st * SR)
        s_len = int(0.02 * SR)
        if s_idx + s_len < n_samples:
            click = np.random.randn(s_len) * np.linspace(1, 0, s_len) ** 3
            sig[s_idx : s_idx + s_len] += click * 2.2

    # Formant filtering
    out = apply_ghoul_vocal_tract(sig, SR)
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak
    return out


def synthesize_ghoul_voice(
    text,
    dur_growl_lead=0.14,
    growl_f0=(75, 115),
    growl_dur=None,
    snap_times=(0.06,),
    speed=182,
    pitch=58,
):
    """
    Synthesize ghoul speech using espeak-ng croak voice, processed through
    throat DSP and synchronized with physical organic growls and teeth snaps.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_sp_raw, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_sp_proc, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_gr_raw, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_gr_proc:

        sp_raw_path = f_sp_raw.name
        sp_proc_path = f_sp_proc.name
        gr_raw_path = f_gr_raw.name
        gr_proc_path = f_gr_proc.name

    try:
        # 1. Base phonetic voice
        cmd_espeak = [
            "espeak-ng", "-v", "en-us+croak", "-p", str(pitch), "-s", str(speed),
            "-w", sp_raw_path, text,
        ]
        subprocess.run(cmd_espeak, check=True)

        # 2. FFmpeg throat treatment
        dsp_speech = (
            "equalizer=f=340:width_type=h:w=120:g=6,"
            "equalizer=f=1100:width_type=h:w=250:g=4,"
            "equalizer=f=2800:width_type=h:w=500:g=8,"
            "tremolo=f=32:d=0.52,"
            "flanger=delay=1.5:depth=1.0:regen=22:speed=1.0,"
            "aecho=0.8:0.6:18|32:0.22|0.12,"
            "compand=attacks=0.01:decays=0.08:points=-70/-70|-20/-8|0/-2:gain=5,"
            f"aresample={SR}"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", sp_raw_path, "-af", dsp_speech, sp_proc_path],
            check=True,
            stderr=subprocess.DEVNULL,
        )

        with wave.open(sp_proc_path, "rb") as w:
            sp_frames = w.readframes(w.getnframes())
            sp_audio = np.frombuffer(sp_frames, dtype=np.int16).astype(np.float32) / 32768.0

        sp_dur = len(sp_audio) / SR
        actual_growl_dur = growl_dur if growl_dur is not None else (sp_dur + dur_growl_lead + 0.1)

        # 3. Synchronized physical growl track
        gr_sig = gen_organic_snarl(
            actual_growl_dur, growl_f0[0], growl_f0[1], rasp=0.88, snap_times=snap_times
        )
        gr_pcm = (np.clip(gr_sig, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
        with wave.open(gr_raw_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(gr_pcm)

        dsp_growl = (
            "equalizer=f=360:width_type=h:w=120:g=10,"
            "equalizer=f=1000:width_type=h:w=250:g=8,"
            "compand=attacks=0.01:decays=0.08:points=-70/-70|-20/-8|0/-2:gain=4"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", gr_raw_path, "-af", dsp_growl, gr_proc_path],
            check=True,
            stderr=subprocess.DEVNULL,
        )

        with wave.open(gr_proc_path, "rb") as w:
            gr_frames = w.readframes(w.getnframes())
            gr_audio = np.frombuffer(gr_frames, dtype=np.int16).astype(np.float32) / 32768.0

        # 4. Mix speech and growl
        mix_len = max(len(gr_audio), len(sp_audio) + int(dur_growl_lead * SR))
        mix = np.zeros(mix_len)
        gr_len = min(len(gr_audio), mix_len)
        mix[:gr_len] += gr_audio[:gr_len] * 0.42

        lead_idx = int(dur_growl_lead * SR)
        sp_len = min(len(sp_audio), mix_len - lead_idx)
        mix[lead_idx : lead_idx + sp_len] += sp_audio[:sp_len] * 0.90

        # Master and normalize
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.96

        return ((mix * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()

    finally:
        for p in (sp_raw_path, sp_proc_path, gr_raw_path, gr_proc_path):
            if os.path.exists(p):
                os.remove(p)


def gen_ghoul_ready_howl():
    """Spine-chilling rising undead howl and rabid screech."""
    dur = 1.35
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    # Rising pitch sweep: 75 Hz -> 260 Hz -> 140 Hz
    f0 = 75 + 185 * np.exp(-((t - 0.75) ** 2) / 0.18)
    jitter = 0.05 * np.sin(2 * np.pi * 14 * t) + 0.03 * np.random.randn(n_samples)
    inst_f0 = f0 * (1.0 + jitter)

    phase = 0.0
    sub_toggle = 0
    sig = np.zeros(n_samples)
    for i in range(n_samples):
        phase += inst_f0[i] / SR
        if phase >= 1.0:
            phase -= 1.0
            sub_toggle = 1 - sub_toggle

        if phase < 0.65:
            p = 0.5 * (1.0 - np.cos(np.pi * phase / 0.65))
        elif phase < 0.85:
            p = np.cos(0.5 * np.pi * (phase - 0.65) / 0.2)
        else:
            p = 0.0

        if sub_toggle == 1:
            p *= 0.52

        turb = np.random.randn() * p * 0.5
        sig[i] = p * 0.55 + turb

    env = np.ones(n_samples)
    att = int(0.12 * SR)
    rel = int(0.25 * SR)
    env[:att] = np.linspace(0, 1, att) ** 1.8
    env[-rel:] = np.linspace(1, 0, rel) ** 2

    # Severe throat rattle
    flutter = 1.0 + 0.35 * np.sin(2 * np.pi * 35 * t)
    sig = sig * env * flutter

    # Teeth snapping bites at apex (0.7s, 0.85s)
    for snap_t in [0.65, 0.82, 0.98]:
        s_idx = int(snap_t * SR)
        s_len = int(0.025 * SR)
        if s_idx + s_len < n_samples:
            sig[s_idx : s_idx + s_len] += np.random.randn(s_len) * np.linspace(1, 0, s_len) ** 3 * 2.5

    out = apply_ghoul_vocal_tract(sig, SR)
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.96
    return ((out * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()


def gen_ghoul_death_rattle():
    """Agonizing wet choking death rattle, gargling collapse, and thud."""
    dur = 1.45
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    # Falling pitch from 140 Hz down to 45 Hz dying croak
    f0 = np.linspace(140, 45, n_samples)
    inst_f0 = f0 * (1.0 + 0.05 * np.random.randn(n_samples))

    phase = 0.0
    sig = np.zeros(n_samples)
    for i in range(n_samples):
        phase += inst_f0[i] / SR
        if phase >= 1.0:
            phase -= 1.0

        # Harsh distorted pulse
        p = np.sin(2 * np.pi * phase) if phase < 0.5 else 0.0
        # Heavy wet gargling bile modulation (42 Hz)
        gargle = 1.0 + 0.55 * np.sin(2 * np.pi * 42 * t[i])
        turb = np.random.randn() * 0.45
        sig[i] = (p * 0.6 + turb) * gargle

    # Dying decay
    decay = np.exp(-2.2 * t)
    sig = sig * decay

    # Wet bone collapse at 0.75s
    c_idx = int(0.72 * SR)
    c_len = int(0.12 * SR)
    if c_idx + c_len < n_samples:
        thud = np.random.randn(c_len) * np.linspace(1, 0, c_len) ** 2
        sig[c_idx : c_idx + c_len] += thud * 1.8

    out = apply_ghoul_vocal_tract(sig, SR)
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.95
    return ((out * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()


def gen_ghoul_feral_bark():
    """Vicious combat snarl and biting bark."""
    dur = 0.72
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    f0 = np.linspace(90, 160, n_samples)
    f0[int(0.3 * SR) :] = np.linspace(160, 85, n_samples - int(0.3 * SR))

    sig = np.zeros(n_samples)
    phase = 0.0
    sub = 0
    for i in range(n_samples):
        phase += f0[i] / SR
        if phase >= 1.0:
            phase -= 1.0
            sub = 1 - sub

        p = 0.5 * (1.0 - np.cos(np.pi * phase / 0.6)) if phase < 0.6 else 0.0
        if sub:
            p *= 0.5
        turb = np.random.randn() * 0.5 * p
        sig[i] = p * 0.6 + turb

    att = int(0.03 * SR)
    rel = int(0.12 * SR)
    env = np.ones(n_samples)
    env[:att] = np.linspace(0, 1, att) ** 1.5
    env[-rel:] = np.linspace(1, 0, rel) ** 2

    # Salivary jaw snap
    s_idx = int(0.1 * SR)
    s_len = int(0.03 * SR)
    sig[s_idx : s_idx + s_len] += np.random.randn(s_len) * np.linspace(1, 0, s_len) ** 3 * 2.2

    out = apply_ghoul_vocal_tract(sig * env, SR)
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.96
    return ((out * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()


def gen_ghoul_chitter_snarl():
    """Rapid enraged chittering teeth and foaming snarl."""
    dur = 0.95
    n_samples = int(dur * SR)
    t = np.linspace(0, dur, n_samples)
    f0 = np.linspace(110, 180, n_samples)
    sig = np.zeros(n_samples)
    phase = 0.0
    for i in range(n_samples):
        phase += f0[i] / SR
        if phase >= 1.0:
            phase -= 1.0
        p = np.sin(2 * np.pi * phase) if phase < 0.5 else 0.0
        turb = np.random.randn() * 0.6
        sig[i] = p * 0.4 + turb

    # Rapid teeth chittering at 22 Hz
    chitter = 1.0 + 0.6 * np.sin(2 * np.pi * 22 * t)
    env = np.ones(n_samples)
    env[: int(0.04 * SR)] = np.linspace(0, 1, int(0.04 * SR))
    env[-int(0.15 * SR) :] = np.linspace(1, 0, int(0.15 * SR)) ** 2

    out = apply_ghoul_vocal_tract(sig * env * chitter, SR)
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.96
    return ((out * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()


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


def main():
    ensure_dir()
    print("Synthesizing authentic Warcraft-style Ghoul sounds...")

    # 1. SELECTED SOUNDS
    # selected_1: Feral greeting - "Me hungry!"
    print("  [1/14] selected_1: 'Me hungry!'")
    s1 = synthesize_ghoul_voice("Me hungry!", dur_growl_lead=0.18, growl_f0=(75, 110), snap_times=[0.05])
    save_wav_gz(s1, os.path.join(GHOUL_DIR, "selected_1.wav.gz"))

    # selected_2: Iconic quote - "Me eat dead people!"
    print("  [2/14] selected_2: 'Me eat dead people!'")
    s2 = synthesize_ghoul_voice("Me eat dead people!", dur_growl_lead=0.15, growl_f0=(80, 120), snap_times=[0.05, 0.4])
    save_wav_gz(s2, os.path.join(GHOUL_DIR, "selected_2.wav.gz"))

    # selected_3: Iconic quote - "Me eat brains!"
    print("  [3/14] selected_3: 'Me eat brains!'")
    s3 = synthesize_ghoul_voice("Me eat brains!", dur_growl_lead=0.12, growl_f0=(85, 125), snap_times=[0.06])
    save_wav_gz(s3, os.path.join(GHOUL_DIR, "selected_3.wav.gz"))

    # selected_4: Cannibal quote - "No guts, no gory!"
    print("  [4/14] selected_4: 'No guts, no gory!'")
    s4 = synthesize_ghoul_voice("No guts, no gory!", dur_growl_lead=0.14, growl_f0=(78, 115), snap_times=[0.08])
    save_wav_gz(s4, os.path.join(GHOUL_DIR, "selected_4.wav.gz"))

    # selected_5: Classic quote - "Fresh meat!"
    print("  [5/14] selected_5: 'Fresh meat!'")
    s5 = synthesize_ghoul_voice("Fresh meat!", dur_growl_lead=0.16, growl_f0=(72, 112), snap_times=[0.05, 0.3])
    save_wav_gz(s5, os.path.join(GHOUL_DIR, "selected_5.wav.gz"))

    # 2. ACKNOWLEDGE / ORDER SOUNDS
    # acknowledge_1: "Rip and tear!"
    print("  [6/14] acknowledge_1: 'Rip and tear!'")
    a1 = synthesize_ghoul_voice("Rip and tear!", dur_growl_lead=0.10, growl_f0=(90, 140), snap_times=[0.04])
    save_wav_gz(a1, os.path.join(GHOUL_DIR, "acknowledge_1.wav.gz"))

    # acknowledge_2: Savage leaping combat snarl (Pure beast sound)
    print("  [7/14] acknowledge_2: Savage leaping beast snarl")
    a2 = gen_ghoul_feral_bark()
    save_wav_gz(a2, os.path.join(GHOUL_DIR, "acknowledge_2.wav.gz"))

    # acknowledge_3: "Tear flesh!"
    print("  [8/14] acknowledge_3: 'Tear flesh!'")
    a3 = synthesize_ghoul_voice("Tear flesh!", dur_growl_lead=0.12, growl_f0=(85, 130), snap_times=[0.05])
    save_wav_gz(a3, os.path.join(GHOUL_DIR, "acknowledge_3.wav.gz"))

    # acknowledge_4: Combat snarling bite (Pure beast sound)
    print("  [9/14] acknowledge_4: Combat growl and bite")
    snarl_bytes = gen_organic_snarl(0.78, 80, 135, rasp=0.9, snap_times=(0.06, 0.35))
    a4 = ((snarl_bytes * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()
    save_wav_gz(a4, os.path.join(GHOUL_DIR, "acknowledge_4.wav.gz"))

    # 3. READY SOUND
    # ready: Spine-chilling rising undead howl
    print("  [10/14] ready: Spine-chilling rising undead howl")
    r1 = gen_ghoul_ready_howl()
    save_wav_gz(r1, os.path.join(GHOUL_DIR, "ready.wav.gz"))

    # 4. ANNOYED / POKED SOUNDS
    # annoyed_1: "Me scary! Stop poking!"
    print("  [11/14] annoyed_1: 'Me scary! Stop poking!'")
    an1 = synthesize_ghoul_voice("Me scary! Stop poking!", dur_growl_lead=0.12, growl_f0=(95, 145), snap_times=[0.05])
    save_wav_gz(an1, os.path.join(GHOUL_DIR, "annoyed_1.wav.gz"))

    # annoyed_2: "Leave alone! Me bite you!"
    print("  [12/14] annoyed_2: 'Leave alone! Me bite you!'")
    an2 = synthesize_ghoul_voice("Leave alone! Me bite you!", dur_growl_lead=0.10, growl_f0=(100, 155), snap_times=[0.04, 0.5])
    save_wav_gz(an2, os.path.join(GHOUL_DIR, "annoyed_2.wav.gz"))

    # annoyed_3: Foaming rabid chitter-snarl (Pure beast sound)
    print("  [13/14] annoyed_3: Foaming rabid chitter-snarl")
    an3 = gen_ghoul_chitter_snarl()
    save_wav_gz(an3, os.path.join(GHOUL_DIR, "annoyed_3.wav.gz"))

    # 5. DEATH SOUND
    # dead: Agonizing wet throat rattle & corpse collapse
    print("  [14/14] dead: Agonizing wet choking death rattle")
    d1 = gen_ghoul_death_rattle()
    save_wav_gz(d1, os.path.join(GHOUL_DIR, "dead.wav.gz"))

    print("\nAll 14 Ghoul audio files synthesized and saved with peak authenticity!")


if __name__ == "__main__":
    main()
