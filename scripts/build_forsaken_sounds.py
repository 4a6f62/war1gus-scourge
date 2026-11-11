#!/usr/bin/env python3
"""
Generate complete custom sound pack for the Scourge / Forsaken race in War1gus.
Produces authentic WC1 11025Hz 8-bit mono pcm_u8 compressed .wav.gz audio files for:
1. Every Scourge Unit (Acolyte, Ghoul, Dark Ranger, Sylvanas, Death Knight,
   Meat Wagon, Necromancer, Banshee, Varimathras):
   - selected_1 .. selected_4
   - acknowledge_1 .. acknowledge_4
   - annoyed_1 .. annoyed_2 (or 3)
   - ready
   - dead
2. Faction-wide voices:
   - work_complete ("Summoning complete")
   - ready ("The Scourge awakens")
   - help_1 .. help_4 ("Our forces are under attack!", etc.)
   - dead
   - acknowledgement_1 .. acknowledgement_4
   - selected_1 .. selected_5
   - annoyed_1 .. annoyed_3
   - victory_1 .. victory_3
   - defeat
3. All Scourge Buildings:
   - necropolis, ziggurat, crypt, graveyard, slaughterhouse, sacrificial_pit,
     temple_of_the_damned, spirit_tower, citadel
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
    for sub in [
        "", "acolyte", "ghoul", "dark_ranger", "sylvanas", "death_knight",
        "meat_wagon", "necromancer", "banshee", "varimathras", "buildings",
        "crypt_fiend", "abomination"
    ]:
        os.makedirs(os.path.join(SOUNDS_DIR, sub), exist_ok=True)


def save_wav_gz(pcm_u8_bytes, out_path_gz):
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


def synthesize_speech(text, voice, pitch, speed, af_filter, out_path_gz):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_raw, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_proc:
        raw_path = tmp_raw.name
        proc_path = tmp_proc.name

    try:
        subprocess.run(
            [
                "espeak-ng",
                "-v", voice,
                "-p", str(pitch),
                "-s", str(speed),
                "-w", raw_path,
                text,
            ],
            check=True,
        )

        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", raw_path,
                "-af", af_filter,
                "-ar", str(SR),
                "-ac", "1",
                "-acodec", "pcm_u8",
                proc_path,
            ],
            check=True,
        )

        with open(proc_path, "rb") as f_in, gzip.open(out_path_gz, "wb") as f_out:
            f_out.write(f_in.read())
    finally:
        for p in (raw_path, proc_path):
            if os.path.exists(p):
                os.remove(p)


def numpy_to_pcm_u8(samples):
    samples = np.clip(samples, -1.0, 1.0)
    return ((samples * 0.5 + 0.5) * 255.0).astype(np.uint8).tobytes()


# ==============================================================================
# PROCEDURAL AUDIO GENERATORS (Ghoul, Meat Wagon, Buildings)
# ==============================================================================
def gen_ghoul_snarl(duration=0.7, base_pitch=75, aggression=1.0, bite=True):
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    mod = np.sin(2 * np.pi * 32 * t)
    carrier = np.sin(2 * np.pi * (base_pitch + 45 * mod) * t)
    noise = np.random.uniform(-1, 1, len(t)) * (0.4 * aggression)
    env = np.exp(-3.5 * t) * (1 - np.exp(-25 * t))
    sig = (carrier * 0.6 + noise * 0.4) * env
    if bite:
        b_idx = int(0.12 * SR)
        b_len = int(0.04 * SR)
        b_env = np.linspace(1, 0, b_len) ** 2
        sig[b_idx:b_idx + b_len] += np.random.uniform(-0.8, 0.8, b_len) * b_env
    return numpy_to_pcm_u8(sig)


def gen_ghoul_screech(duration=0.9, bite_count=2):
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    sweep = np.linspace(220, 110, len(t))
    mod = np.sin(2 * np.pi * 45 * t)
    screech = np.sin(2 * np.pi * (sweep + 60 * mod) * t) * 0.5
    noise = np.random.uniform(-1, 1, len(t)) * 0.5
    env = np.exp(-2.8 * t) * (1 - np.exp(-30 * t))
    sig = (screech + noise) * env
    for i in range(bite_count):
        b_idx = int((0.15 + i * 0.18) * SR)
        b_len = int(0.05 * SR)
        b_env = np.linspace(1, 0, b_len) ** 2
        sig[b_idx:b_idx + b_len] += np.random.uniform(-0.7, 0.7, b_len) * b_env
    return numpy_to_pcm_u8(sig)


def gen_ghoul_death():
    t = np.linspace(0, 1.1, int(SR * 1.1), endpoint=False)
    screech = np.sin(2 * np.pi * np.linspace(260, 60, len(t)) * t) * 0.5
    noise = np.random.uniform(-1, 1, len(t)) * 0.5
    gurgle = np.sin(2 * np.pi * 18 * t)
    env = np.exp(-2.2 * t)
    sig = (screech + noise) * env * (1.0 + 0.4 * gurgle)
    # Bone crack at 0.5s
    c_idx = int(0.45 * SR)
    c_len = int(0.08 * SR)
    sig[c_idx:c_idx + c_len] += np.random.uniform(-0.9, 0.9, c_len) * np.linspace(1, 0, c_len)
    return numpy_to_pcm_u8(sig)


def gen_meat_wagon_creak(variation=1):
    dur = 0.85
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    f0 = 130 if variation == 1 else 95
    creak = np.sin(2 * np.pi * (f0 + 60 * np.sin(2 * np.pi * 9 * t)) * t) * 0.45
    squelch = np.random.uniform(-1, 1, len(t)) * np.exp(-np.abs(np.sin(2 * np.pi * 6 * t) * 3)) * 0.4
    env = np.exp(-1.8 * t)
    sig = (creak + squelch) * env
    return numpy_to_pcm_u8(sig)


def gen_meat_wagon_ratchet():
    dur = 0.9
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # Series of 5 ratchet clicks
    sig = np.zeros(len(t))
    for i in range(5):
        c_idx = int((0.08 + i * 0.14) * SR)
        c_len = int(0.04 * SR)
        sig[c_idx:c_idx + c_len] += np.random.uniform(-0.8, 0.8, c_len) * np.exp(-np.linspace(0, 5, c_len))
    # Engine hum & timber strain
    strain = np.sin(2 * np.pi * (110 + 30 * np.sin(2 * np.pi * 4 * t)) * t) * 0.35 * np.exp(-1.5 * t)
    sig += strain
    return numpy_to_pcm_u8(sig)


def gen_meat_wagon_death():
    dur = 1.2
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    # Timber crash + wet gore explosion
    timber = np.random.uniform(-1, 1, len(t)) * np.exp(-3.5 * t) * 0.6
    low_boom = np.sin(2 * np.pi * np.linspace(90, 35, len(t)) * t) * np.exp(-2.0 * t) * 0.7
    squelch = np.random.uniform(-1, 1, len(t)) * np.exp(-1.8 * t) * np.sin(2 * np.pi * 12 * t) * 0.4
    sig = timber + low_boom + squelch
    return numpy_to_pcm_u8(sig)


def gen_ambient_building(b_type):
    dur = 1.3
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.sin(np.pi * t / dur)

    if b_type == "necropolis":
        # Deep resonant crystal hum + pulsing occult drone
        hum = np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 110 * t) * 0.3 + np.sin(2 * np.pi * 220 * t) * 0.15
        whisper = np.random.uniform(-1, 1, len(t)) * 0.08 * (1 + np.sin(2 * np.pi * 3 * t))
        sig = (hum + whisper) * env
    elif b_type == "ziggurat":
        # Faceted emerald crystal resonance
        hum = np.sin(2 * np.pi * 82 * t) * 0.5 + np.sin(2 * np.pi * 164 * t) * 0.3 + np.sin(2 * np.pi * 328 * t) * 0.2
        mod = 1.0 + 0.4 * np.sin(2 * np.pi * 4 * t)
        sig = hum * mod * env
    elif b_type == "crypt":
        # Rattle of bones & subterranean wind
        drone = np.sin(2 * np.pi * 65 * t) * 0.4
        rattle = np.random.uniform(-1, 1, len(t)) * np.exp(-np.abs(np.sin(2 * np.pi * 5 * t) * 3)) * 0.3
        sig = (drone + rattle) * env
    elif b_type == "graveyard":
        # Blighted howling wind & shovel scrape
        wind = np.random.uniform(-1, 1, len(t)) * 0.35 * (1 + 0.5 * np.sin(2 * np.pi * 1.5 * t))
        scrape = np.sin(2 * np.pi * (180 + 70 * t) * t) * 0.25 * np.exp(-1.5 * t)
        sig = (wind + scrape) * env
    elif b_type == "slaughterhouse":
        # Grinding blade & bubbling vat
        grind = np.sin(2 * np.pi * (140 + 80 * np.sin(2 * np.pi * 12 * t)) * t) * 0.4
        bubble = np.random.uniform(-1, 1, len(t)) * np.exp(-np.abs(np.sin(2 * np.pi * 8 * t) * 4)) * 0.35
        sig = (grind + bubble) * env
    elif b_type == "sacrificial_pit":
        # Ghostly flame crackle & unholy whisper
        drone = np.sin(2 * np.pi * 70 * t) * 0.4
        flame = np.random.uniform(-1, 1, len(t)) * 0.3 * (1 + 0.3 * np.sin(2 * np.pi * 6 * t))
        sig = (drone + flame) * env
    elif b_type == "temple_of_the_damned":
        # Monolithic cult ritual drone + chanting harmonics
        sig = (
            np.sin(2 * np.pi * 48 * t) * 0.45
            + np.sin(2 * np.pi * 96 * t) * 0.3
            + np.sin(2 * np.pi * 144 * t) * 0.2
            + np.sin(2 * np.pi * 192 * t) * 0.1
        ) * env
    elif b_type == "spirit_tower":
        # Ethereal chime & weeping spirit echo
        chime = np.sin(2 * np.pi * 330 * t) * np.exp(-1.8 * t) * 0.5 + np.sin(2 * np.pi * 660 * t) * np.exp(-2.5 * t) * 0.25
        ghost = np.random.uniform(-1, 1, len(t)) * 0.15 * env
        sig = chime + ghost
    else:  # citadel
        # Thunderous fortress rumble
        rumble = np.sin(2 * np.pi * 40 * t) * 0.6 + np.sin(2 * np.pi * 80 * t) * 0.3
        sig = rumble * env

    return numpy_to_pcm_u8(sig)


def build_all_sounds():
    ensure_dirs()
    print("Synthesizing complete Scourge unit & faction sound pack...")

    # --------------------------------------------------------------------------
    # 1. ACOLYTE (Cultist Cowl Voice)
    # --------------------------------------------------------------------------
    ac_v = "en-gb-x-rp+croak"
    ac_p, ac_s = 22, 138
    ac_af = "aecho=0.8:0.65:25:0.35,highpass=f=90,lowpass=f=4500,volume=1.6"
    acolyte_lines = {
        "selected_1": "The damned stand ready.",
        "selected_2": "My life for Ner zhul.",
        "selected_3": "I wish only to serve.",
        "selected_4": "Where shall my blood be spilled?",
        "acknowledge_1": "I gladly obey.",
        "acknowledge_2": "Yes, Master.",
        "acknowledge_3": "Thy will be done.",
        "acknowledge_4": "As you wish.",
        "ready": "The shadows beckon.",
        "annoyed_1": "My life for Ner zhul!",
        "annoyed_2": "Death shall cleanse all!",
        "annoyed_3": "I cannot hear you over the summoning!",
        "dead": "My blood for the master...",
    }
    for k, text in acolyte_lines.items():
        dst = os.path.join(SOUNDS_DIR, "acolyte", f"{k}.wav.gz")
        synthesize_speech(text, ac_v, ac_p, ac_s, ac_af, dst)

    # --------------------------------------------------------------------------
    # 2. GHOUL (Authentic Warcraft III Voice & Feral Beast Sounds)
    # --------------------------------------------------------------------------
    import scripts.build_authentic_ghoul_sounds as ghoul_snd
    ghoul_snd.main()

    # --------------------------------------------------------------------------
    # 3. DARK RANGER (Haunting Undead Elven Voice)
    # --------------------------------------------------------------------------
    dr_v = "en-gb-x-rp+f2"
    dr_p, dr_s = 40, 142
    dr_af = "aecho=0.85:0.7:30|55:0.3|0.18,highpass=f=120,volume=1.7"
    dr_lines = {
        "selected_1": "I am here.",
        "selected_2": "Speak, fool.",
        "selected_3": "My bow is ready.",
        "selected_4": "The dark paths call.",
        "acknowledge_1": "Very well.",
        "acknowledge_2": "With precision.",
        "acknowledge_3": "They will suffer.",
        "acknowledge_4": "Without question.",
        "ready": "I walk the shadows.",
        "annoyed_1": "Do not test my patience.",
        "annoyed_2": "You are treading on thin ice.",
        "annoyed_3": "I have no time for fools.",
        "dead": "Darkness... takes me.",
    }
    for k, text in dr_lines.items():
        dst = os.path.join(SOUNDS_DIR, "dark_ranger", f"{k}.wav.gz")
        synthesize_speech(text, dr_v, dr_p, dr_s, dr_af, dst)

    # --------------------------------------------------------------------------
    # 4. SYLVANAS (Banshee Queen Regal Tone)
    # --------------------------------------------------------------------------
    sy_v = "en-gb-x-rp+f3"
    sy_p, sy_s = 36, 136
    sy_af = "chorus=0.7:0.9:55:0.4:0.25:2,aecho=0.85:0.75:35|70:0.35|0.2,volume=1.7"
    sy_lines = {
        "selected_1": "I have no time for games.",
        "selected_2": "What is your bidding?",
        "selected_3": "Give me a target.",
        "selected_4": "We are the Forsaken.",
        "acknowledge_1": "For the Scourge.",
        "acknowledge_2": "Right away.",
        "acknowledge_3": "They will know sorrow.",
        "acknowledge_4": "Torment them.",
        "ready": "Let none survive.",
        "annoyed_1": "I do not take orders lightly.",
        "annoyed_2": "Bow before the Banshee Queen!",
        "annoyed_3": "You test my wrath!",
        "dead": "Not like this...",
    }
    for k, text in sy_lines.items():
        dst = os.path.join(SOUNDS_DIR, "sylvanas", f"{k}.wav.gz")
        synthesize_speech(text, sy_v, sy_p, sy_s, sy_af, dst)

    # --------------------------------------------------------------------------
    # 5. DEATH KNIGHT (Deep Runic Plate Armor Terror)
    # --------------------------------------------------------------------------
    dk_v = "en-gb-x-rp+Demonic"
    dk_p, dk_s = 18, 125
    dk_af = "asetrate=22050*0.82,aresample=22050,aecho=0.85:0.72:28|58:0.4|0.22,equalizer=f=120:width_type=h:width=100:g=6,volume=1.6"
    dk_lines = {
        "selected_1": "The dead shall serve.",
        "selected_2": "You called?",
        "selected_3": "My might cannot be matched.",
        "selected_4": "Speak, mortal.",
        "acknowledge_1": "By Ner zhul.",
        "acknowledge_2": "For the Lich King.",
        "acknowledge_3": "As I order.",
        "acknowledge_4": "Death is cold.",
        "ready": "I have returned.",
        "annoyed_1": "Don't tempt my wrath.",
        "annoyed_2": "Frostmourne hungers!",
        "annoyed_3": "You are speaking to your master!",
        "dead": "The grave... claims me not...",
    }
    for k, text in dk_lines.items():
        dst = os.path.join(SOUNDS_DIR, "death_knight", f"{k}.wav.gz")
        synthesize_speech(text, dk_v, dk_p, dk_s, dk_af, dst)

    # --------------------------------------------------------------------------
    # 6. MEAT WAGON (Heavy Mechanical Creaks, Ratchets & Splatters)
    # --------------------------------------------------------------------------
    save_wav_gz(gen_meat_wagon_creak(1), os.path.join(SOUNDS_DIR, "meat_wagon", "selected_1.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(2), os.path.join(SOUNDS_DIR, "meat_wagon", "selected_2.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(1), os.path.join(SOUNDS_DIR, "meat_wagon", "selected_3.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(2), os.path.join(SOUNDS_DIR, "meat_wagon", "selected_4.wav.gz"))
    save_wav_gz(gen_meat_wagon_ratchet(), os.path.join(SOUNDS_DIR, "meat_wagon", "acknowledge_1.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(2), os.path.join(SOUNDS_DIR, "meat_wagon", "acknowledge_2.wav.gz"))
    save_wav_gz(gen_meat_wagon_ratchet(), os.path.join(SOUNDS_DIR, "meat_wagon", "acknowledge_3.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(1), os.path.join(SOUNDS_DIR, "meat_wagon", "acknowledge_4.wav.gz"))
    save_wav_gz(gen_meat_wagon_ratchet(), os.path.join(SOUNDS_DIR, "meat_wagon", "ready.wav.gz"))
    save_wav_gz(gen_meat_wagon_ratchet(), os.path.join(SOUNDS_DIR, "meat_wagon", "annoyed_1.wav.gz"))
    save_wav_gz(gen_meat_wagon_creak(1), os.path.join(SOUNDS_DIR, "meat_wagon", "annoyed_2.wav.gz"))
    save_wav_gz(gen_meat_wagon_death(), os.path.join(SOUNDS_DIR, "meat_wagon", "dead.wav.gz"))

    # --------------------------------------------------------------------------
    # 7. NECROMANCER (Raspy Cult Elder)
    # --------------------------------------------------------------------------
    nm_v = "en-gb-x-rp+croak"
    nm_p, nm_s = 30, 130
    nm_af = "flanger=delay=3:depth=2:regen=50,aecho=0.8:0.7:30|60:0.3|0.18,volume=1.6"
    nm_lines = {
        "selected_1": "The shadows beckon.",
        "selected_2": "Speak, mortal.",
        "selected_3": "The dead shall rise.",
        "selected_4": "Every soul has a purpose.",
        "acknowledge_1": "By the pact.",
        "acknowledge_2": "Tremble before the Scourge.",
        "acknowledge_3": "Right away.",
        "acknowledge_4": "As the Lich King wills.",
        "ready": "The dead will rise!",
        "annoyed_1": "You dare disturb my incantations?",
        "annoyed_2": "I will turn your skull into a chalice!",
        "annoyed_3": "Your soul is mine!",
        "dead": "Release...",
    }
    for k, text in nm_lines.items():
        dst = os.path.join(SOUNDS_DIR, "necromancer", f"{k}.wav.gz")
        synthesize_speech(text, nm_v, nm_p, nm_s, nm_af, dst)

    # --------------------------------------------------------------------------
    # 8. BANSHEE (Ghostly Spectral Wraith)
    # --------------------------------------------------------------------------
    bn_v = "en-gb-x-rp+whisperf"
    bn_p, bn_s = 54, 125
    bn_af = "vibrato=f=6.5:d=0.35,aecho=0.88:0.78:40|85|130:0.45|0.28|0.15,highpass=f=200,volume=1.6"
    bn_lines = {
        "selected_1": "Why have I been summoned?",
        "selected_2": "I am sorrow.",
        "selected_3": "We weep for the living.",
        "selected_4": "My soul aches.",
        "acknowledge_1": "If it pleases you.",
        "acknowledge_2": "Let it be done.",
        "acknowledge_3": "Suffer.",
        "acknowledge_4": "I go.",
        "ready": "I am returned to sorrow.",
        "annoyed_1": "You torment me!",
        "annoyed_2": "You shall feel my agony!",
        "dead": "Free at last...",
    }
    for k, text in bn_lines.items():
        dst = os.path.join(SOUNDS_DIR, "banshee", f"{k}.wav.gz")
        synthesize_speech(text, bn_v, bn_p, bn_s, bn_af, dst)

    # --------------------------------------------------------------------------
    # 9. VARIMATHRAS (Deep Cavernous Dreadlord)
    # --------------------------------------------------------------------------
    vm_v = "en-gb-x-rp+Demonic"
    vm_p, vm_s = 14, 118
    vm_af = "asetrate=22050*0.78,aresample=22050,aecho=0.85:0.75:35|75:0.45|0.25,equalizer=f=90:width_type=h:width=80:g=8,volume=1.6"
    vm_lines = {
        "selected_1": "I am listening.",
        "selected_2": "You waste my time.",
        "selected_3": "State your business.",
        "selected_4": "Darkness commands.",
        "acknowledge_1": "Very well.",
        "acknowledge_2": "A simple task.",
        "acknowledge_3": "They will die.",
        "acknowledge_4": "Treachery awaits.",
        "ready": "I have awakened.",
        "annoyed_1": "Do not mock a Dreadlord!",
        "annoyed_2": "I shall feast upon your despair!",
        "annoyed_3": "Your insolence will be your doom!",
        "dead": "This realm... is not the end...",
    }
    for k, text in vm_lines.items():
        dst = os.path.join(SOUNDS_DIR, "varimathras", f"{k}.wav.gz")
        synthesize_speech(text, vm_v, vm_p, vm_s, vm_af, dst)

    # --------------------------------------------------------------------------
    # 9B. CRYPT FIEND (Clicking Chitinous Nerubian Insectoid Voice)
    # --------------------------------------------------------------------------
    cf_v = "en-gb-x-rp+whisper"
    cf_p, cf_s = 45, 145
    cf_af = "asetrate=22050*1.12,aresample=22050,flanger=delay=3.5:depth=2.8:speed=4,aecho=0.8:0.65:25|45:0.3|0.18,volume=1.8"
    cf_lines = {
        "selected_1": "I hear the call.",
        "selected_2": "The brood awakens.",
        "selected_3": "By the Spider Kingdom.",
        "selected_4": "Speak, master.",
        "selected_5": "My life for Nerub.",
        "acknowledge_1": "For Nerub!",
        "acknowledge_2": "At once.",
        "acknowledge_3": "Underway.",
        "acknowledge_4": "Into the shadows.",
        "ready": "The Crypt Fiend rises.",
        "annoyed_1": "Stop poking my carapace!",
        "annoyed_2": "Do not test the nerubian...",
        "annoyed_3": "I have eight reasons to bite you!",
        "dead": "The brood... falls...",
    }
    for k, text in cf_lines.items():
        dst = os.path.join(SOUNDS_DIR, "crypt_fiend", f"{k}.wav.gz")
        synthesize_speech(text, cf_v, cf_p, cf_s, cf_af, dst)

    # --------------------------------------------------------------------------
    # 9C. ABOMINATION (Deep Sluggish Guttural Flesh Golem Voice)
    # --------------------------------------------------------------------------
    ab_v = "en-gb+croak"
    ab_p, ab_s = 6, 110
    ab_af = "asetrate=22050*0.58,aresample=22050,aecho=0.85:0.5:25:0.25,equalizer=f=80:width_type=h:width=70:g=9,volume=2.2"
    ab_lines = {
        "selected_1": "Me hear and obey!",
        "selected_2": "What we do?",
        "selected_3": "All stitched up!",
        "selected_4": "Huh?",
        "selected_5": "Me ready!",
        "acknowledge_1": "Chop chop!",
        "acknowledge_2": "Tear meat!",
        "acknowledge_3": "Me go!",
        "acknowledge_4": "Smash!",
        "ready": "Fresh meat!",
        "annoyed_1": "You tickle me!",
        "annoyed_2": "Don't poke my guts!",
        "annoyed_3": "Me got an itch me can't scratch...",
        "dead": "Too... much... pain...",
    }
    for k, text in ab_lines.items():
        dst = os.path.join(SOUNDS_DIR, "abomination", f"{k}.wav.gz")
        synthesize_speech(text, ab_v, ab_p, ab_s, ab_af, dst)

    # --------------------------------------------------------------------------
    # 10. FACTION-WIDE GENERAL SOUNDS (sounds/forsaken/)
    # --------------------------------------------------------------------------
    gen_v = "en-gb-x-rp"
    gen_af = "asetrate=22050*0.84,aresample=22050,aecho=0.85:0.7:30|60:0.35|0.2,volume=1.6"
    faction_lines = {
        "work_complete": "Summoning complete.",
        "ready": "The Scourge awakens.",
        "help_1": "Our forces are under attack!",
        "help_2": "Our sanctuary is besieged!",
        "help_3": "Defend the Necropolis!",
        "help_4": "The living strike at our borders!",
        "acknowledgement_1": "Thy will be done.",
        "acknowledgement_2": "At once.",
        "acknowledgement_3": "It shall be done.",
        "acknowledgement_4": "By your command.",
        "selected_1": "Command the dead.",
        "selected_2": "We await your word.",
        "selected_3": "The shadows stir.",
        "selected_4": "We obey.",
        "selected_5": "Darkness listens.",
        "annoyed_1": "Cease this badgering!",
        "annoyed_2": "You test our patience!",
        "annoyed_3": "Do not provoke the Scourge!",
    }
    for k, text in faction_lines.items():
        dst = os.path.join(SOUNDS_DIR, f"{k}.wav.gz")
        synthesize_speech(text, gen_v, 20, 130, gen_af, dst)

    # Build authentic cinematic Scourge Victory & Defeat fanfares
    import scripts.build_authentic_scourge_fanfares as fanfares
    fanfares.main()

    # General dead sound: dark guttural groan
    save_wav_gz(gen_ghoul_snarl(0.6, 60, 0.8, False), os.path.join(SOUNDS_DIR, "dead.wav.gz"))

    # --------------------------------------------------------------------------
    # 11. BUILDINGS SELECTED SOUNDS (sounds/forsaken/buildings/)
    # --------------------------------------------------------------------------
    buildings = [
        ("necropolis", "necropolis"),
        ("ziggurat", "ziggurat"),
        ("crypt", "crypt"),
        ("graveyard", "graveyard"),
        ("slaughterhouse", "slaughterhouse"),
        ("sacrificial_pit", "sacrificial_pit"),
        ("temple_of_the_damned", "temple_of_the_damned"),
        ("spirit_tower", "spirit_tower"),
        ("citadel", "citadel"),
    ]
    for b_file, b_type in buildings:
        dst = os.path.join(SOUNDS_DIR, "buildings", f"{b_file}.wav.gz")
        save_wav_gz(gen_ambient_building(b_type), dst)

    print("All custom Scourge sounds synthesized successfully!")


if __name__ == "__main__":
    build_all_sounds()
