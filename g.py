import os
import re
import soundfile as sf
import sounddevice as sd
import numpy as np
import librosa  # For advanced pitch shifting

# Define the directory containing the male audio files
male_audio_dir = r"C:\Users\jacob\OneDrive\Desktop\Der Feige droht nur, wo er sicher ist\TTS"

# Ask the user to choose a voice
voice_choice = input("Choose a voice (male/female): ").strip().lower()

# Function to transform male voice to female voice using librosa
def transform_to_female(audio_data, sample_rate):
    """
    Transform male voice to female voice using librosa's pitch shifting.
    """
    # Shift the pitch up by 4 semitones (to make it sound more like a female voice)
    audio_data_female = librosa.effects.pitch_shift(
        y=audio_data,  # Audio time-series
        sr=sample_rate,  # Sampling rate
        n_steps=4  # Number of semitones to shift (positive for higher pitch)
    )
    return audio_data_female, sample_rate

# Function to play audio files with adjustable speed
def play_audio(files, speed=1.0):
    for file in files:
        filepath = os.path.join(male_audio_dir, file)
        try:
            if os.path.exists(filepath):
                print(f"Playing audio file: {file}")
                data, fs = sf.read(filepath)

                # Transform to female voice if selected
                if voice_choice == "female":
                    data, fs = transform_to_female(data, fs)

                # Adjust the sample rate based on the speed
                adjusted_fs = int(fs * speed)
                # Play the audio with the correct sample rate
                sd.play(data, samplerate=adjusted_fs)
                sd.wait()
            else:
                print(f"Audio file not found: {file}")
        except Exception as e:
            print(f"Error playing {file}: {e}")

# Rest of your code remains unchanged...
# Mapping of phonemes to corresponding audio files
valid_word_file_map = {
                       "a": "A.wav", "à": "A.wav",  # Same sound
        "á": "Á.wav", "ã": "Ã.wav",  # Different sounds

        # E vowel grouping: E, È are the same, but different from É and Ẽ
        "e": "E.wav", "è": "E.wav",  # Same sound
        "é": "É.wav", "ẽ": "Ẽ.wav",  # Different sounds

        # ɛ vowel grouping: ɛ, ɛ̀ are the same, but different from ɛ́ and ɛ̃
        "ɛ": "Ɛ.wav", "ɛ̀": "Ɛ.wav",  # Same sound
        "ɛ́": "Ɛ́.wav", "ɛ̃": "Ɛ̃.wav",  # Different sounds

        # I vowel grouping: I, Ì are the same, but different from Í and Ĩ
        "i": "I.wav", "ì": "I.wav",  # Same sound
        "í": "Í.wav", "ĩ": "Ĩ.wav",  # Different sounds

        # O vowel grouping: O, Ò are the same, but different from Ó and Õ
        "o": "O.wav", "ò": "O.wav",  # Same sound
        "ó": "Ó.wav", "õ": "Õ.wav",  # Different sounds

        # ɔ vowel grouping: ɔ, ɔ̀ are the same, but different from ɔ́ and ɔ̃
        "ɔ": "Ɔ.wav", "ɔ̀": "Ɔ.wav",  # Same sound
        "ɔ́": "Ɔ́.wav", "ɔ̃": "Ɔ̃.wav",  # Different sounds

        # U vowel grouping: U, Ù are the same, but different from Ú and Ũ
        "u": "U.wav", "ù": "U.wav",  # Same sound
        "ú": "Ú.wav", "ũ": "Ũ.wav",  # Different sounds

        "b": "B.wav", 
        "d": "D.wav", 
        "f": "F.wav", 
        "g": "G.wav", 
        "h": "H.wav", 
        "j": "J.wav", 
        "k": "K.wav", 
        "l": "L.wav", 
        "m": "M.wav", 
        "n": "N.wav", 
        "p": "P.wav", 
        "s": "S.wav", 
        "t": "T.wav", 
        "v": "V.wav", 
        "w": "W.wav", 
        "y": "Y.wav", 
        "z": "Z.wav",

        "ba": "BA.wav", "bà": "BA.wav", "bá": "BÁ.wav", "bã": "BÃ.wav", 
        "be": "BE.wav", "bè": "BE.wav", "bé": "BÉ.wav", "bẽ": "BẼ.wav",
        "bɛ": "Bɛ.wav", "bɛ̀": "Bɛ.wav", "bɛ́": "Bɛ́.wav", "bɛ̃": "Bɛ̃.wav", "bƐ̃": "BƐ̃.wav",
        "bi": "BI.wav", "bì": "BI.wav", "bí": "BÍ.wav", "bĩ": "BĨ.wav",
        "bo": "BO.wav", "bò": "BO.wav", "bó": "BÓ.wav", "bõ": "BÕ.wav",
        "bɔ": "Bɔ.wav", "bɔ̀": "Bɔ.wav", "bɔ́": "Bɔ́.wav", "bɔ̃": "Bɔ̃.wav",
        "bu": "BU.wav", "bù": "BU.wav", "bú": "BÚ.wav", "bũ": "BŨ.wav",

        "da": "DA.wav", "dà": "DA.wav", "dá": "DÁ.wav", "dã": "DÃ.wav", 
        "de": "DE.wav", "dè": "DE.wav", "dé": "DÉ.wav", "dẽ": "DẼ.wav",
        "dɛ": "Dɛ.wav", "dɛ̀": "Dɛ.wav", "dɛ́": "Dɛ́.wav", "dɛ̃": "Dɛ̃.wav", "dƐ̃": "DƐ̃.wav",
        "di": "DI.wav", "dì": "DI.wav", "dí": "DÍ.wav", "dĩ": "DĨ.wav",
        "do": "DO.wav", "dò": "DO.wav", "dó": "DÓ.wav", "dõ": "DÕ.wav",
        "dɔ": "Dɔ.wav", "dɔ̀": "Dɔ.wav", "dɔ́": "Dɔ́.wav", "dɔ̃": "Dɔ̃.wav",
        "du": "DU.wav", "dù": "DU.wav", "dú": "DÚ.wav", "dũ": "DŨ.wav",

        "fa": "FA.wav", "fà": "FA.wav", "fá": "FÁ.wav", "fã": "FÃ.wav",
        "fe": "FE.wav", "fè": "FE.wav", "fé": "FÉ.wav", "fẽ": "FẼ.wav",
        "fɛ": "Fɛ.wav", "fɛ̀": "Fɛ.wav", "fɛ́": "Fɛ́.wav", "fɛ̃": "Fɛ̃.wav", "fƐ̃": "FƐ̃.wav",
        "fi": "FI.wav", "fì": "FI.wav", "fí": "FÍ.wav", "fĩ": "FĨ.wav",
        "fo": "FO.wav", "fò": "FO.wav", "fó": "FÓ.wav", "fõ": "FÕ.wav",
        "fɔ": "Fɔ.wav", "fɔ̀": "Fɔ.wav", "fɔ́": "Fɔ́.wav", "fɔ̃": "Fɔ̃.wav",
        "fu": "FU.wav", "fù": "FU.wav", "fú": "FÚ.wav", "fũ": "FŨ.wav",

        "ga": "GA.wav", "gà": "GA.wav", "gá": "GÁ.wav", "gã": "GÃ.wav",
        "ge": "GE.wav", "gè": "GE.wav", "gé": "GÉ.wav", "gẽ": "GẼ.wav",
        "gɛ": "Gɛ.wav", "gɛ̀": "Gɛ.wav", "gɛ́": "Gɛ́.wav", "gɛ̃": "Gɛ̃.wav", "gƐ̃": "GƐ̃.wav",
        "gi": "GI.wav", "gì": "GI.wav", "gí": "GÍ.wav", "gĩ": "GĨ.wav",
        "go": "GO.wav", "gò": "GO.wav", "gó": "GÓ.wav", "gõ": "GÕ.wav",
        "gɔ": "Gɔ.wav", "gɔ̀": "Gɔ.wav", "gɔ́": "Gɔ́.wav", "gɔ̃": "Gɔ̃.wav",
        "gu": "GU.wav", "gù": "GU.wav", "gú": "GÚ.wav", "gũ": "GŨ.wav",
        
        "ha": "HA.wav", "hà": "HA.wav", "há": "HÁ.wav", "hã": "HÃ.wav", 
        "he": "HE.wav", "hè": "HE.wav", "hé": "HÉ.wav", "hẽ": "HẼ.wav",
        "hɛ": "Hɛ.wav", "hɛ̀": "Hɛ.wav", "hɛ́": "Hɛ́.wav", "hɛ̃": "Hɛ̃.wav", "hƐ̃": "HƐ̃.wav",
        "hi": "HI.wav", "hì": "HI.wav", "hí": "HÍ.wav", "hĩ": "HĨ.wav",
        "ho": "HO.wav", "hò": "HO.wav", "hó": "HÓ.wav", "hõ": "HÕ.wav",
        "hɔ": "Hɔ.wav", "hɔ̀": "Hɔ.wav", "hɔ́": "Hɔ́.wav", "hɔ̃": "Hɔ̃.wav",
        "hu": "HU.wav", "hù": "HU.wav", "hú": "HÚ.wav", "hũ": "HŨ.wav",
        
        "ja": "JA.wav", "jà": "JA.wav", "já": "JÁ.wav", "jã": "JÃ.wav", 
        "je": "JE.wav", "jè": "JE.wav", "jé": "JÉ.wav", "jẽ": "JẼ.wav",
        "jɛ": "Jɛ.wav", "jɛ̀": "Jɛ.wav", "jɛ́": "Jɛ́.wav", "jɛ̃": "Jɛ̃.wav", "jƐ̃": "JƐ̃.wav",
        "ji": "JI.wav", "jì": "JI.wav", "jí": "JÍ.wav", "jĩ": "JĨ.wav",
        "jo": "JO.wav", "jò": "JO.wav", "jó": "JÓ.wav", "jõ": "JÕ.wav",
        "jɔ": "Jɔ.wav", "jɔ̀": "Jɔ.wav", "jɔ́": "Jɔ́.wav", "jɔ̃": "Jɔ̃.wav",
        "ju": "JU.wav", "jù": "JU.wav", "jú": "JÚ.wav", "jũ": "JŨ.wav",

        "ka": "KA.wav", "kà": "KA.wav", "ká": "KÁ.wav", "kã": "KÃ.wav", 
        "ke": "KE.wav", "kè": "KE.wav", "ké": "KÉ.wav", "kẽ": "KẼ.wav",
        "kɛ": "Kɛ.wav", "kɛ̀": "Kɛ.wav", "kɛ́": "Kɛ́.wav", "kɛ̃": "Kɛ̃.wav", "kƐ̃": "KƐ̃.wav",
        "ki": "KI.wav", "kì": "KI.wav", "kí": "KÍ.wav", "kĩ": "KĨ.wav",
        "ko": "KO.wav", "kò": "KO.wav", "kó": "KÓ.wav", "kõ": "KÕ.wav",
        "kɔ": "Kɔ.wav", "kɔ̀": "Kɔ.wav", "kɔ́": "Kɔ́.wav", "kɔ̃": "Kɔ̃.wav",
        "ku": "KU.wav", "kù": "KU.wav", "kú": "KÚ.wav", "kũ": "KŨ.wav",

        "la": "LA.wav", "là": "LA.wav", "lá": "LÁ.wav", "lã": "LÃ.wav", 
        "le": "LE.wav", "lè": "LE.wav", "lé": "LÉ.wav", "lẽ": "LẼ.wav",
        "lɛ": "Lɛ.wav", "lɛ̀": "Lɛ.wav", "lɛ́": "Lɛ́.wav", "lɛ̃": "Lɛ̃.wav", "lƐ̃": "LƐ̃.wav",
        "li": "LI.wav", "lì": "LI.wav", "lí": "LÍ.wav", "lĩ": "LĨ.wav",
        "lo": "LO.wav", "lò": "LO.wav", "ló": "LÓ.wav", "lõ": "LÕ.wav",
        "lɔ": "Lɔ.wav", "lɔ̀": "Lɔ.wav", "lɔ́": "Lɔ́.wav", "lɔ̃": "Lɔ̃.wav",
        "lu": "LU.wav", "lù": "LU.wav", "lú": "LÚ.wav", "lũ": "LŨ.wav",

        "ma": "MA.wav", "mà": "MA.wav", "má": "MÁ.wav", "mã": "MÃ.wav", 
        "me": "ME.wav", "mè": "ME.wav", "mé": "MÉ.wav", "mẽ": "MẼ.wav",
        "mɛ": "Mɛ.wav", "mɛ̀": "Mɛ.wav", "mɛ́": "Mɛ́.wav", "mɛ̃": "Mɛ̃.wav", "mƐ̃": "MƐ̃.wav",
        "mi": "MI.wav", "mì": "MI.wav", "mí": "MÍ.wav", "mĩ": "MĨ.wav",
        "mo": "MO.wav", "mò": "MO.wav", "mó": "MÓ.wav", "mõ": "MÕ.wav",
        "mɔ": "Mɔ.wav", "mɔ̀": "Mɔ.wav", "mɔ́": "Mɔ́.wav", "mɔ̃": "Mɔ̃.wav",
        "mu": "MU.wav", "mù": "MU.wav", "mú": "MÚ.wav", "mũ": "MŨ.wav",

        "na": "NA.wav", "nà": "NA.wav", "ná": "NÁ.wav", "nã": "NÃ.wav", 
        "ne": "NE.wav", "nè": "NE.wav", "né": "NÉ.wav", "nẽ": "NẼ.wav",
        "nɛ": "NƐ.wav", "nɛ̀": "NƐ.wav", "nɛ́": "NƐ́.wav", "nɛ̃": "NƐ̃.wav", "nɛ̃": "NƐ̃.wav",
        "ni": "NI.wav", "nì": "NI.wav", "ní": "NÍ.wav", "nĩ": "NĨ.wav",
        "no": "NO.wav", "nò": "NO.wav", "nó": "NÓ.wav", "nõ": "NÕ.wav",
        "nɔ": "Nɔ.wav", "nɔ̀": "Nɔ.wav", "nɔ́": "Nɔ́.wav", "nɔ̃": "Nɔ̃.wav",
        "nu": "NU.wav", "nù": "NU.wav", "nú": "NÚ.wav", "nũ": "NŨ.wav",

        "pa": "PA.wav", "pà": "PA.wav", "pá": "PÁ.wav", "pã": "PÃ.wav", 
        "pe": "PE.wav", "pè": "PE.wav", "pé": "PÉ.wav", "pẽ": "PẼ.wav",
        "pɛ": "Pɛ.wav", "pɛ̀": "Pɛ.wav", "pɛ́": "Pɛ́.wav", "pɛ̃": "Pɛ̃.wav", "pƐ̃": "PƐ̃.wav",
        "pi": "PI.wav", "pì": "PI.wav", "pí": "PÍ.wav", "pĩ": "PĨ.wav",
        "po": "PO.wav", "pò": "PO.wav", "pó": "PÓ.wav", "põ": "PÕ.wav",
        "pɔ": "Pɔ.wav", "pɔ̀": "Pɔ.wav", "pɔ́": "Pɔ́.wav", "pɔ̃": "Pɔ̃.wav",
        "pu": "PU.wav", "pù": "PU.wav", "pú": "PÚ.wav", "pũ": "PŨ.wav",

        "sa": "SA.wav", "sà": "SA.wav", "sá": "SÁ.wav", "sã": "SÃ.wav", 
        "se": "SE.wav", "sè": "SE.wav", "sé": "SÉ.wav", "sẽ": "SẼ.wav",
        "sɛ": "Sɛ.wav", "sɛ̀": "Sɛ.wav", "sɛ́": "Sɛ́.wav", "sɛ̃": "Sɛ̃.wav", "sƐ̃": "SƐ̃.wav",
        "si": "SI.wav", "sì": "SI.wav", "sí": "SÍ.wav", "sĩ": "SĨ.wav",
        "so": "SO.wav", "sò": "SO.wav", "só": "SÓ.wav", "sõ": "SÕ.wav",
        "sɔ": "Sɔ.wav", "sɔ̀": "Sɔ.wav", "sɔ́": "Sɔ́.wav", "sɔ̃": "Sɔ̃.wav",
        "su": "SU.wav", "sù": "SU.wav", "sú": "SU.wav", "sũ": "SŨ.wav",

        "ta": "TA.wav", "tà": "TA.wav", "tá": "TÁ.wav", "tã": "TÃ.wav", 
        "te": "TE.wav", "tè": "TE.wav", "té": "TÉ.wav", "tẽ": "TẼ.wav",
        "tɛ": "Tɛ.wav", "tɛ̀": "Tɛ.wav", "tɛ́": "Tɛ́.wav", "tɛ̃": "Tɛ̃.wav", "tƐ̃": "TƐ̃.wav",
        "ti": "TI.wav", "tì": "TI.wav", "tí": "TÍ.wav", "tĩ": "TĨ.wav",
        "to": "TO.wav", "tò": "TO.wav", "tó": "TÓ.wav", "tõ": "TÕ.wav",
        "tɔ": "Tɔ.wav", "tɔ̀": "Tɔ.wav", "tɔ́": "Tɔ́.wav", "tɔ̃": "Tɔ̃.wav",
        "tu": "TU.wav", "tù": "TU.wav", "tú": "TU.wav", "tũ": "TŨ.wav",

        "va": "VA.wav", "và": "VA.wav", "vá": "VÁ.wav", "vã": "VÃ.wav", 
        "ve": "VE.wav", "vè": "VE.wav", "vé": "VÉ.wav", "vẽ": "VẼ.wav",
        "vɛ": "Vɛ.wav", "vɛ̀": "Vɛ.wav", "vɛ́": "Vɛ́.wav", "vɛ̃": "Vɛ̃.wav", "vƐ̃": "VƐ̃.wav",
        "vi": "VI.wav", "vì": "VI.wav", "ví": "VÍ.wav", "vĩ": "VĨ.wav",
        "vo": "VO.wav", "vò": "VO.wav", "vó": "VÓ.wav", "võ": "VÕ.wav",
        "vɔ": "Vɔ.wav", "vɔ̀": "Vɔ.wav", "vɔ́": "Vɔ́.wav", "vɔ̃": "Vɔ̃.wav",
        "vu": "VU.wav", "vù": "VU.wav", "vú": "VU.wav", "vũ": "VŨ.wav",

        "wa": "WA.wav", "wà": "WA.wav", "wá": "WÁ.wav", "wã": "WÃ.wav", 
        "we": "WE.wav", "wè": "WE.wav", "wé": "WÉ.wav", "wẽ": "WẼ.wav",
        "wɛ": "Wɛ.wav", "wɛ̀": "Wɛ.wav", "wɛ́": "Wɛ́.wav", "wɛ̃": "Wɛ̃.wav", "wɛ̃": "WƐ̃.wav",
        "wi": "WI.wav", "wì": "WI.wav", "wí": "WÍ.wav", "wĩ": "WĨ.wav",
        "wo": "WO.wav", "wò": "WO.wav", "wó": "WÓ.wav", "wõ": "WÕ.wav",
        "wɔ": "Wɔ.wav", "wɔ̀": "Wɔ.wav", "wɔ́": "Wɔ́.wav", "wɔ̃": "Wɔ̃.wav",
        "wu": "WU.wav", "wù": "WU.wav", "wú": "WU.wav", "wũ": "WŨ.wav",

        "ya": "YA.wav", "yà": "YA.wav", "yá": "YÁ.wav", "yã": "YÃ.wav", 
        "ye": "YE.wav", "yè": "YE.wav", "yé": "YÉ.wav", "yẽ": "YẼ.wav",
        "yɛ": "Yɛ.wav", "yɛ̀": "Yɛ.wav", "yɛ́": "Yɛ́.wav", "yɛ̃": "Yɛ̃.wav", "yƐ̃": "YƐ̃.wav",
        "yi": "YI.wav", "yì": "YI.wav", "yí": "YÍ.wav", "yĩ": "YĨ.wav",
        "yo": "YO.wav", "yò": "YO.wav", "yó": "YÓ.wav", "yõ": "YÕ.wav",
        "yɔ": "Yɔ.wav", "yɔ̀": "Yɔ.wav", "yɔ́": "Yɔ́.wav", "yɔ̃": "Yɔ̃.wav",
        "yu": "YU.wav", "yù": "YU.wav", "yú": "YÚ.wav", "yũ": "YŨ.wav",

        "za": "ZA.wav", "zà": "ZA.wav", "zá": "ZÁ.wav", "zã": "ZÃ.wav", 
        "ze": "ZE.wav", "zè": "ZE.wav", "zé": "ZÉ.wav", "zẽ": "ZẼ.wav",
        "zɛ": "Zɛ.wav", "zɛ̀": "Zɛ.wav", "zɛ́": "Zɛ́.wav", "zɛ̃": "Zɛ̃.wav", "zƐ̃": "ZƐ̃.wav",
        "zi": "ZI.wav", "zì": "ZI.wav", "zí": "ZÍ.wav", "zĩ": "ZĨ.wav",
        "zo": "ZO.wav", "zò": "ZO.wav", "zó": "ZÓ.wav", "zõ": "ZÕ.wav",
        "zɔ": "Zɔ.wav", "zɔ̀": "Zɔ.wav", "zɔ́": "Zɔ́.wav", "zɔ̃": "Zɔ̃.wav",
        "zu": "ZU.wav", "zù": "ZU.wav", "zú": "ZÚ.wav", "zũ": "ZŨ.wav",
        
        "kpla": "KPLA.wav", "kplà": "KPLA.wav", "kplá": "KPLÁ.wav", "kplã": "KPLÃ.wav",
        "kple": "KPLE.wav", "kplè": "KPLE.wav", "kplé": "KPLÉ.wav", "kplẽ": "KPLẼ.wav",
        "kplɛ": "KPLɛ.wav", "kplɛ̀": "KPLɛ.wav", "kplɛ́": "KPLɛ́.wav", "kplɛ̃": "KPLɛ̃.wav", "kplƐ̃": "KPLƐ̃.wav",
        "kpli": "KPLI.wav", "kplì": "KPLI.wav", "kplí": "KPLÍ.wav", "kplĩ": "KPLĨ.wav",
        "kplo": "KPLO.wav", "kplò": "KPLO.wav", "kpló": "KPLÓ.wav", "kplõ": "KPLÕ.wav",
        "kplɔ": "KPLɔ.wav", "kplɔ̀": "KPLɔ.wav", "kplɔ́": "KPLɔ́.wav", "kplɔ̃": "KPLɔ̃.wav",
        "kplu": "KPLU.wav", "kplù": "KPLU.wav", "kplú": "KPLÚ.wav", "kplũ": "KPLŨ.wav",

        

        "gbla": "GBLA.wav", "gblá": "GBLÁ.wav", "gblã": "GBLÃ.wav", "gblã́": "GBLÃ́.wav",
        "gble": "GBLE.wav", "gblè": "GBLÈ.wav", "gblé": "GBLÉ.wav", "gblẽ": "GBLẼ.wav",
        "gblɛ": "GBLɛ.wav", "gblƐ": "GBLƐ.wav", "gblɛ̀": "GBLɛ̀.wav", "gblɛ́": "GBLɛ́.wav", "gblɛ́": "GBLɛ́.wav", "gblɛ̃": "GBLɛ̃.wav", "gblƐ̃": "GBLƐ̃.wav",
        "gbli": "GBLI.wav", "gblì": "GBLÌ.wav", "gblí": "GBLÍ.wav", "gblĩ": "GBLĨ.wav",
        "gblo": "GBLO.wav", "gblò": "GBLÒ.wav", "gbló": "GBLÓ.wav", "gblõ": "GBLÕ.wav",
        "gblɔ": "GBLɔ.wav", "gblɔ̀": "GBLɔ̀.wav", "gblɔ́": "GBLɔ́.wav", "gblɔ̃": "GBLɔ̃.wav",
        "gblu": "GBLU.wav", "gblu": "GBLÙ.wav", "gblu": "GBLÚ.wav", "gblu": "GBLŨ.wav",

        
        "kpa": "KPA.wav",
        "kpà": "KPA.wav",
        "kpá": "KPÁ.wav",
        "kpã": "KPÃ.wav",
        
        "kpe": "KPE.wav",
        "kpè": "KPE.wav",
        "kpé": "KPÉ.wav",
        "kpẽ": "KPẼ.wav",
        
        "kpɛ": "KPɛ.wav",
        "kpɛ̀": "KPɛ.wav",
        "kpɛ́": "KPɛ́.wav",
        "kpɛ̃": "KPɛ̃.wav",
        "kpƐ̃": "KPƐ̃.wav",
        
        "kpi": "KPI.wav",
        "kpì": "KPI.wav",
        "kpí": "KPÍ.wav",
        "kpĩ": "KPĨ.wav",
        
        "kpo": "KPO.wav",
        "kpò": "KPO.wav",
        "kpó": "KPÓ.wav",
        "kpõ": "KPÕ.wav",
        
        "kpɔ": "KPɔ.wav",
        "kpɔ̀": "KPɔ.wav",
        "kpɔ́": "KPɔ́.wav",
        "kpɔ̃": "KPɔ̃.wav",
        
        "kpu": "KPU.wav",
        "kpù": "KPU.wav",
        "kpú": "KPÚ.wav",
        "kpũ": "KPŨ.wav",

        "gba": "GBA.wav",
        "gbà": "GBA.wav",
        "gbá": "GBÁ.wav",
        "gbã": "GBÃ.wav",
        "gbe": "GBE.wav",
        "gbè": "GBE.wav",
        "gbé": "GBÉ.wav",
        "gbẽ": "GBẼ.wav",
        "gbɛ": "GBɛ.wav",
        "gbɛ̀": "GBɛ.wav",
        "gbɛ́": "GBɛ́.wav",
        "gbɛ̃": "GBɛ̃.wav",
        "gbƐ̃": "GBƐ̃.wav",
        "gbi": "GBI.wav",
        "gbì": "GBI.wav",
        "gbí": "GBÍ.wav",
        "gbĩ": "GBĨ.wav",
        "gbo": "GBO.wav",
        "gbò": "GBO.wav",
        "gbó": "GBÓ.wav",
        "gbõ": "GBÕ.wav",
        "gbɔ": "GBɔ.wav",
        "gbɔ̀": "GBɔ.wav",
        "gbɔ́": "GBɔ́.wav",
        "gbɔ̃": "GBɔ̃.wav",
        "gbu": "GBU.wav",
        "gbù": "GBU.wav",
        "gbú": "GBÚ.wav",
        "gbũ": "GBŨ.wav",

        "tsa": "TSA.wav",
        "tsà": "TSA.wav",
        "tsá": "TSÁ.wav",
        "tsã": "TSÃ.wav",
        "tse": "TSE.wav",
        "tsè": "TSE.wav",
        "tsé": "TSÉ.wav",
        "tsẽ": "TSẼ.wav",
        "tsɛ": "TSɛ.wav",
        "tsɛ̀": "TSɛ.wav",
        "tsɛ́": "TSɛ́.wav",
        "tsɛ̃": "TSɛ̃.wav",
        "tsƐ̃": "TSƐ̃.wav",
        "tsi": "TSI.wav",
        "tsì": "TSI.wav",
        "tsí": "TSÍ.wav",
        "tsĩ": "TSĨ.wav",
        "tso": "TSO.wav",
        "tsò": "TSO.wav",
        "tsó": "TSÓ.wav",
        "tsõ": "TSÕ.wav",
        "tsɔ": "TSɔ.wav",
        "tsɔ̀": "TSɔ.wav",
        "tsɔ́": "TSɔ́.wav",
        "tsɔ̃": "TSɔ̃.wav",
        "tsu": "TSU.wav",
        "tsù": "TSU.wav",
        "tsú": "TSÚ.wav",
        "tsũ": "TSŨ.wav",

        "tsla": "TSLA.wav",
        "tslà": "TSLA.wav",
        "tslá": "TSLÁ.wav",
        "tslã": "TSLÃ.wav",
        "tsle": "TSLE.wav",
        "tslè": "TSLE.wav",
        "tslé": "TSLÉ.wav",
        "tslẽ": "TSLẼ.wav",
        "tslɛ": "TSLɛ.wav",
        "tslɛ̀": "TSLɛ.wav",
        "tslɛ́": "TSLɛ́.wav",
        "tslɛ̃": "TSLɛ̃.wav",
        "tslƐ̃": "TSLƐ̃.wav",
        "tsli": "TSLI.wav",
        "tslì": "TSLI.wav",
        "tslí": "TSLÍ.wav",
        "tslĩ": "TSLĨ.wav",
        "tslo": "TSLO.wav",
        "tslò": "TSLO.wav",
        "tsló": "TSLÓ.wav",
        "tslõ": "TSLÕ.wav",
        "tslɔ": "TSLɔ.wav",
        "tslɔ̀": "TSLɔ.wav",
        "tslɔ́": "TSLɔ́.wav",
        "tslɔ̃": "TSLɔ̃.wav",
        "tslu": "TSLU.wav",
        "tslù": "TSLU.wav",
        "tslú": "TSLÚ.wav",
        "tslũ": "TSLŨ.wav",

        "nya": "NYA.wav",
        "nyà": "NYA.wav",
        "nyá": "NYÁ.wav",
        "nyã": "NYÃ.wav",
        "nye": "NYE.wav",
        "nyè": "NYE.wav",
        "nyé": "NYÉ.wav",
        "nyẽ": "NYẼ.wav",
        "nyɛ": "NYɛ.wav",
        "nyɛ̀": "NYɛ.wav",
        "nyɛ́": "NYɛ́.wav",
        "nyɛ̃": "NYɛ̃.wav",
        "nyƐ̃": "NYƐ̃.wav",
        "nyi": "NYI.wav",
        "nyì": "NYI.wav",
        "nyí": "NYÍ.wav",
        "nyĩ": "NYĨ.wav",
        "nyo": "NYO.wav",
        "nyò": "NYO.wav",
        "nyó": "NYÓ.wav",
        "nyõ": "NYÕ.wav",
        "nyɔ": "NYɔ.wav",
        "nyɔ̀": "NYɔ.wav",
        "nyɔ́": "NYɔ́.wav",
        "nyɔ̃": "NYɔ̃.wav",
        "nyu": "NYU.wav",
        "nyù": "NYU.wav",
        "nyú": "NYÚ.wav",
        "nyũ": "NYŨ.wav",

        "kpa": "KPA.wav",
        "kpà": "KPA.wav",
        "kpá": "KPÁ.wav",
        "kpã": "KPÃ.wav",
        "kpe": "KPE.wav",
        "kpè": "KPE.wav",
        "kpé": "KPÉ.wav",
        "kpẽ": "KPẼ.wav",
        "kpɛ": "KPɛ.wav",
        "kpɛ̀": "KPɛ.wav",
        "kpɛ́": "KPɛ́.wav",
        "kpɛ̃": "KPɛ̃.wav",
        "kpƐ̃": "KPƐ̃.wav",
        "kpi": "KPI.wav",
        "kpì": "KPI.wav",
        "kpí": "KPÍ.wav",
        "kpĩ": "KPĨ.wav",
        "kpo": "KPO.wav",
        "kpò": "KPO.wav",
        "kpó": "KPÓ.wav",
        "kpõ": "KPÕ.wav",
        "kpɔ": "KPɔ.wav",
        "kpɔ̀": "KPɔ.wav",
        "kpɔ́": "KPɔ́.wav",
        "kpɔ̃": "KPɔ̃.wav",
        "kpu": "KPU.wav",
        "kpù": "KPU.wav",
        "kpú": "KPÚ.wav",
        "kpũ": "KPŨ.wav",

        "kpla": "KPLA.wav",
        "kplà": "KPLA.wav",
        "kplá": "KPLÁ.wav",
        "kplã": "KPLÃ.wav",
        "kple": "KPLE.wav",
        "kplè": "KPLE.wav",
        "kplé": "KPLÉ.wav",
        "kplẽ": "KPLẼ.wav",
        "kplɛ": "KPLɛ.wav",
        "kplɛ̀": "KPLɛ.wav",
        "kplɛ́": "KPLɛ́.wav",
        "kplɛ̃": "KPLɛ̃.wav",
        "kplƐ̃": "KPLƐ̃.wav",
        "kpli": "KPLI.wav",
        "kplì": "KPLI.wav",
        "kplí": "KPLÍ.wav",
        "kplĩ": "KPLĨ.wav",
        "kplo": "KPLO.wav",
        "kplò": "KPLO.wav",
        "kpló": "KPLÓ.wav",
        "kplõ": "KPLÕ.wav",
        "kplɔ": "KPLɔ.wav",
        "kplɔ̀": "KPLɔ.wav",
        "kplɔ́": "KPLɔ́.wav",
        "kplɔ̃": "KPLɔ̃.wav",
        "kplu": "KPLU.wav",
        "kplù": "KPLU.wav",
        "kplú": "KPLÚ.wav",
        "kplũ": "KPLŨ.wav",

        "ngma": "NGMA.wav",
        "ngmà": "NGMA.wav",
        "ngmá": "NGMÁ.wav",
        "ngmã": "NGMÃ.wav",
        "ngme": "NGME.wav",
        "ngmè": "NGME.wav",
        "ngmé": "NGMÉ.wav",
        "ngmẽ": "NGMẼ.wav",
        "ngmɛ": "NGMɛ.wav",
        "ngmɛ̀": "NGMɛ.wav",
        "ngmɛ́": "NGMɛ́.wav",
        "ngmɛ̃": "NGMɛ̃.wav",
        "ngmƐ̃": "NGMƐ̃.wav",
        "ngmi": "NGMI.wav",
        "ngmì": "NGMI.wav",
        "ngmí": "NGMÍ.wav",
        "ngmĩ": "NGMĨ.wav",
        "ngmo": "NGMO.wav",
        "ngmò": "NGMO.wav",
        "ngmó": "NGMÓ.wav",
        "ngmõ": "NGMÕ.wav",
        "ngmɔ": "NGMɔ.wav",
        "ngmɔ̀": "NGMɔ.wav",
        "ngmɔ́": "NGMɔ́.wav",
        "ngmɔ̃": "NGMɔ̃.wav",
        "ngmu": "NGMU.wav",
        "ngmù": "NGMU.wav",
        "ngmú": "NGMÚ.wav",
        "ngmũ": "NGMŨ.wav",

        "ngmla": "NGMLA.wav",
        "ngmlà": "NGMLA.wav",
        "ngmlá": "NGMLÁ.wav",
        "ngmlã": "NGMLÃ.wav",
        "ngmle": "NGMLE.wav",
        "ngmlè": "NGMLE.wav",
        "ngmlé": "NGMLÉ.wav",
        "ngmlẽ": "NGMLẼ.wav",
        "ngmlɛ": "NGMLɛ.wav",
        "ngmlɛ̀": "NGMLɛ.wav",
        "ngmlɛ́": "NGMLɛ́.wav",
        "ngmlɛ̃": "NGMLɛ̃.wav",
        "ngmlƐ̃": "NGMLƐ̃.wav",
        "ngmli": "NGMLI.wav",
        "ngmlì": "NGMLI.wav",
        "ngmlí": "NGMLÍ.wav",
        "ngmlĩ": "NGMLĨ.wav",
        "ngmlo": "NGMLO.wav",
        "ngmlò": "NGMLO.wav",
        "ngmló": "NGMLÓ.wav",
        "ngmlõ": "NGMLÕ.wav",
        "ngmlɔ": "NGMLɔ.wav",
        "ngmlɔ̀": "NGMLɔ.wav",
        "ngmlɔ́": "NGMLɔ́.wav",
        "ngmlɔ̃": "NGMLɔ̃.wav",
        "ngmlu": "NGMLU.wav",
        "ngmlù": "NGMLU.wav",
        "ngmlú": "NGMLÚ.wav",
        "ngmlũ": "NGMLŨ.wav",

        "nga": "NGA.wav",
        "ngà": "NGA.wav",
        "ngá": "NGÁ.wav",
        "ngã": "NGÃ.wav",
        "ngã́": "NGÃ́.wav",
        "nge": "NGE.wav",
        "ngè": "NGE.wav",
        "ngé": "NGÉ.wav",
        "ngẽ": "NGẼ.wav",
        "ngɛ": "NGɛ.wav",
        "ngɛ̀": "NGɛ.wav",
        "ngɛ́": "NGɛ́.wav",
        "ngɛ̃": "NGɛ̃.wav",
        "ngƐ̃": "NGƐ̃.wav",
        "ngi": "NGI.wav",
        "ngì": "NGI.wav",
        "ngí": "NGÍ.wav",
        "ngĩ": "NGĨ.wav",
        "ngo": "NGO.wav",
        "ngò": "NGO.wav",
        "ngó": "NGÓ.wav",
        "ngõ": "NGÕ.wav",
        "ngɔ": "NGɔ.wav",
        "ngɔ̀": "NGɔ.wav",
        "ngɔ́": "NGɔ́.wav",
        "ngɔ̃": "NGɔ̃.wav",
        "ngu": "NGU.wav",
        "ngù": "NGU.wav",
        "ngú": "NGÚ.wav",
        "ngũ": "NGŨ.wav",

        "ngla": "NGLA.wav",
        "nglà": "NGLA.wav",
        "nglá": "NGLÁ.wav",
        "nglã": "NGLÃ.wav",
        "nglã́": "NGLÃ́.wav",
        "ngle": "NGLE.wav",
        "nglè": "NGLE.wav",
        "nglé": "NGLÉ.wav",
        "nglẽ": "NGLẼ.wav",
        "nglɛ": "NGLɛ.wav",
        "nglɛ̀": "NGLɛ.wav",
        "nglɛ́": "NGLɛ́.wav",
        "nglɛ̃": "NGLɛ̃.wav",
        "nglƐ̃": "NGLƐ̃.wav",
        "ngli": "NGLI.wav",
        "nglì": "NGLI.wav",
        "nglí": "NGLÍ.wav",
        "nglĩ": "NGLĨ.wav",
        "nglo": "NGLO.wav",
        "nglò": "NGLO.wav",
        "ngló": "NGLÓ.wav",
        "nglõ": "NGLÕ.wav",
        "nglɔ": "NGLɔ.wav",
        "nglɔ̀": "NGLɔ.wav",
        "nglɔ́": "NGLɔ́.wav",
        "nglɔ̃": "NGLɔ̃.wav",
        "nglu": "NGLU.wav",
        "nglù": "NGLU.wav",
        "nglú": "NGLÚ.wav",
        "nglũ": "NGLŨ.wav",

        "gbla": "GBLA.wav",
        "gblà": "GBLA.wav",
        "gblá": "GBLÁ.wav",
        "gblã": "GBLÃ.wav",
        "gblã́": "GBLã́.wav",
        "gble": "GBLE.wav",
        "gblè": "GBLE.wav",
        "gblé": "GBLÉ.wav",
        "gblẽ": "GBLẼ.wav",
        "gblɛ": "GBLɛ.wav",
        "gblɛ̀": "GBLɛ.wav",
        "gblɛ́": "GBLɛ́.wav",
        "gblɛ̃": "GBLɛ̃.wav",
        "gblƐ̃": "GBLƐ̃.wav",
        "gbli": "GBLI.wav",
        "gblì": "GBLI.wav",
        "gblí": "GBLÍ.wav",
        "gblĩ": "GBLĨ.wav",
        "gblo": "GBLO.wav",
        "gblò": "GBLO.wav",
        "gbló": "GBLÓ.wav",
        "gblõ": "GBLÕ.wav",
        "gblɔ": "GBLɔ.wav",
        "gblɔ̀": "GBLɔ.wav",
        "gblɔ́": "GBLɔ́.wav",
        "gblɔ̃": "GBLɔ̃.wav",
        "gblu": "GBLU.wav",
        "gblù": "GBLU.wav",
        "gblú": "GBLÚ.wav",
        "gblũ": "GBLŨ.wav",

        "nyla": "NYLA.wav",
        "nylà": "NYLA.wav",
        "nylá": "NYLÁ.wav",
        "nylã": "NYLÃ.wav",
        "nylã́": "NYLÃ́.wav",
        "nyle": "NYLE.wav",
        "nylè": "NYLE.wav",
        "nylé": "NYLÉ.wav",
        "nylẽ": "NYLẼ.wav",
        "nylɛ": "NYLɛ.wav",
        "nylɛ̀": "NYLɛ.wav",
        "nylɛ́": "NYLɛ́.wav",
        "nylɛ̃": "NYLɛ̃.wav",
        "nylƐ̃": "NYLƐ̃.wav",
        "nyli": "NYLI.wav",
        "nylì": "NYLI.wav",
        "nylí": "NYLÍ.wav",
        "nylĩ": "NYLĨ.wav",
        "nylo": "NYLO.wav",
        "nylò": "NYLO.wav",
        "nyló": "NYLÓ.wav",
        "nylõ": "NYLÕ.wav",
        "nylɔ": "NYLɔ.wav",
        "nylɔ̀": "NYLɔ.wav",
        "nylɔ́": "NYLɔ́.wav",
        "nylɔ̃": "NYLɔ̃.wav",
        "nylu": "NYLU.wav",
        "nylù": "NYLU.wav",
        "nylú": "NYLÚ.wav",
        "nylũ": "NYLŨ.wav",
}

# Mapping of numbers to corresponding audio files
number_to_wav = {
    0: "0.wav",
    1: "1.wav",
    2: "2.wav",
    3: "3.wav",
    4: "4.wav",
    5: "5.wav",
    6: "6.wav",
    7: "7.wav",
    8: "8.wav",
    9: "9.wav",
    10: "10.wav",
    20: "20-90.wav",
    30: "20-90.wav",
    40: "20-90.wav",
    50: "20-90.wav",
    60: "20-90.wav",
    70: "20-90.wav",
    80: "20-90.wav",
    90: "20-90.wav",
    100: "100.wav",
    1000: "1000.wav",
    1000000: "1000000.wav",
    "KƐ": "KƐ.wav"
}

# Master code dictionary for custom pronunciations
master_code = {
    # CORRECT
     101: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    102: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    103: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    104: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    105: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    106: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    107: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    108: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    109: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    110: ["100.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    1001: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1002: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1003: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1004: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1005: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1006: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1007: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1008: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1009: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1010: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 10,001 to 10,009
    10001: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    10002: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    10003: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    10004: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    10005: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    10006: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    10007: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    10008: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    10009: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    10010: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    1001: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1002: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1003: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1004: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1005: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1006: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1007: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1008: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1009: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1010: ["1000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 10,001 to 10,009
    10001: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    10002: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    10003: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    10004: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    10005: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    10006: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    10007: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    10008: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    10009: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    10010: ["10000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],
    
        # 1,000,001 to 1,000,009
    1000001: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1000002: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1000003: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1000004: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1000005: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1000006: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1000007: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1000008: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1000009: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1000010: ["1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 10,000,001 to 10,000,009
    10000001: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    10000002: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    10000003: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    10000004: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    10000005: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    10000006: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    10000007: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    10000008: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    10000009: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    10000010: ["10000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 100,000,001 to 100,000,010
    100000001: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    100000002: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    100000003: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    100000004: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    100000005: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    100000006: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    100000007: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    100000008: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    100000009: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    100000010: ["100000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 1,000,000,001 to 1,000,000,010
    1000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],
    
    # 10,001 to 10,010
10001: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
10002: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
10003: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
10004: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
10005: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
10006: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
10007: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
10008: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
10009: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
10010: ["1000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

# 100,001 to 100,010
100001: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
100002: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
100003: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
100004: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
100005: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
100006: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
100007: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
100008: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
100009: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
100010: ["1000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

# 10,000,001 to 10,000,010
10000001: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
10000002: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
10000003: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
10000004: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
10000005: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
10000006: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
10000007: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
10000008: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
10000009: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
10000010: ["1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

# 100,000,001 to 100,000,010
100000001: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
100000002: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
100000003: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
100000004: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
100000005: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
100000006: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
100000007: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
100000008: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
100000009: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
100000010: ["1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

# 10,000,000,001 to 10,000,000,010
10000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
10000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
10000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
10000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
10000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
10000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
10000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
10000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
10000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
10000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],
    
    


    # 100,000,000,000 (100 billion)
    100000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    100000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    100000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    100000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    100000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    100000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    100000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    100000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    100000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    100000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,000,001 (1 trillion)
    1000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,000,000,001 (10 trillion)
    1000000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    1000000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    1000000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    1000000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    1000000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    1000000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    1000000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    1000000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    1000000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    1000000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,000,000,001 (100 trillion)
    10000000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    10000000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    10000000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    10000000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    10000000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    10000000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    10000000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    10000000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    10000000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    10000000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,000,000,001 (Quadrillion)
    10000000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
    10000000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
    10000000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
    10000000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
    10000000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
    10000000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
    10000000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
    10000000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
    10000000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
    10000000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

    # Add the rest of your master code mappings here...
}

# Function to generate the correct sequence of .wav files for a number
def generate_wav_sequence(number):
    if number in master_code:
        return master_code[number]

    if number < 1:
        return []

    # Define the base wav files
    base_wavs = {
        1: "1.wav",
        2: "2.wav",
        3: "3.wav",
        4: "4.wav",
        5: "5.wav",
        6: "6.wav",
        7: "7.wav",
        8: "8.wav",
        9: "9.wav",
        10: "10.wav",
        20: "20-90.wav",
        30: "20-90.wav",
        40: "20-90.wav",
        50: "20-90.wav",
        60: "20-90.wav",
        70: "20-90.wav",
        80: "20-90.wav",
        90: "20-90.wav",
        100: "100.wav",
        1000: "1000.wav",
        1000000: "1000000.wav",
    }

    # Define the KƐ.wav file
    ke_wav = "KƐ.wav"
    mi_wav = "MĨ.wav"

    # Function to get the wav file for a single digit
    def get_wav(digit):
        return base_wavs.get(digit, "")

    # Function to handle numbers between 11 and 19
    def handle_teens(num):
        return [get_wav(10), ke_wav, get_wav(num % 10)]

    # Function to handle numbers between 20 and 99
    def handle_tens(num):
        tens = (num // 10) * 10
        units = num % 10
        if units == 0:
            return [get_wav(tens), get_wav(tens // 10)]
        else:
            return [get_wav(tens), get_wav(tens // 10), ke_wav, get_wav(units)]

    # Function to handle numbers between 100 and 999
    def handle_hundreds(num):
        hundreds = num // 100
        remainder = num % 100
        if remainder == 0:
            return [get_wav(100), get_wav(hundreds)]
        else:
            return [get_wav(100), get_wav(hundreds)] + generate_wav_sequence(remainder)

    # Function to handle numbers between 1000 and 999999
    def handle_thousands(num):
        thousands = num // 1000
        remainder = num % 1000
        if remainder == 0:
            return [get_wav(1000)] + generate_wav_sequence(thousands)
        else:
            return [get_wav(1000)] + generate_wav_sequence(thousands) + generate_wav_sequence(remainder)

    # Function to handle numbers between 1000000 and 999999999
    def handle_millions(num):
        millions = num // 1000000
        remainder = num % 1000000
        if remainder == 0:
            return [get_wav(1000000)] + generate_wav_sequence(millions)
        else:
            return [get_wav(1000000)] + generate_wav_sequence(millions) + generate_wav_sequence(remainder)

    # Function to handle numbers in billions (1,000,000,000 to 999,999,999,999)
    def handle_billions(num):
        billions = num // 1000000000
        remainder = num % 1000000000
        if remainder == 0:
            return [get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(billions)
        else:
            return [get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(billions) + generate_wav_sequence(remainder)

    # Function to handle numbers in trillions (1,000,000,000,000 to 999,999,999,999,999)
    def handle_trillions(num):
        trillions = num // 1000000000000
        remainder = num % 1000000000000
        if remainder == 0:
            return [get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(trillions)
        else:
            return [get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(trillions) + generate_wav_sequence(remainder)

    # Function to handle numbers in duadrillions (1,000,000,000,000,000 to 999,999,999,999,999,999)
    def handle_duadrillions(num):
        duadrillions = num // 1000000000000000
        remainder = num % 1000000000000000
        if remainder == 0:
            return [get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(duadrillions)
        else:
            return [get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000), mi_wav, get_wav(1000000)] + generate_wav_sequence(duadrillions) + generate_wav_sequence(remainder)

    # Determine the range of the number and handle accordingly
    if number < 11:
        return [get_wav(number)]
    elif 11 <= number < 20:
        return handle_teens(number)
    elif 20 <= number < 100:
        return handle_tens(number)
    elif 100 <= number < 1000:
        return handle_hundreds(number)
    elif 1000 <= number < 1000000:
        return handle_thousands(number)
    elif 1000000 <= number < 1000000000:
        return handle_millions(number)
    elif 1000000000 <= number < 1000000000000:
        return handle_billions(number)
    elif 1000000000000 <= number < 1000000000000000:
        return handle_trillions(number)
    elif 1000000000000000 <= number < 1000000000000000000:
        return handle_duadrillions(number)
    else:
        return ["Wa tui he blɔ nyã lolo."]

# Function to split input text into phonemes
def split_into_phonemes(text, phoneme_map):
    phonemes = []
    i = 0
    while i < len(text):
        matched = False
        for j in range(min(len(text), i + 5), i, -1):
            substring = text[i:j]
            if substring in phoneme_map:
                phonemes.append(substring)
                i = j
                matched = True
                break
        if not matched:
            print(f"Wa tui: {text[i]} he blɔ nyã aloo pí Dãngme pɛlɔ(i)")
            i += 1
    return phonemes

# Function to play phonemes
def play_phonemes(phonemes, phoneme_map, speed=1.0):
    for phoneme in phonemes:
        audio_file = phoneme_map.get(phoneme)
        if audio_file:
            play_audio([audio_file], speed)
        else:
            print(f"Wa tui : {phoneme} he blɔ nyã lolo aloo pí Dãngme")

# Function to process mixed input (words and numbers)
def process_mixed_input(text, speed=1.0):
    tokens = re.findall(r'\d+|\D+', text)  # Split into numbers and non-numbers
    for token in tokens:
        if token.isdigit():  # If the token is a number
            print(f"I kpaa mo pɛɛ nɛ̃ ó bu túe be mĩ nɛ̃ I yaa tsɛ: {token}")
            audio_files = generate_wav_sequence(int(token))
            play_audio(audio_files, speed)
        else:  # If the token is a word
            print(f"I kpaa mo pɛɛ nɛ̃ ó bu túe be mĩ nɛ̃ I yaa tsɛ aloo kãne: {token}")
            phonemes = split_into_phonemes(token, valid_word_file_map)
            play_phonemes(phonemes, valid_word_file_map, speed)

# Check if the user wants to skip the welcoming address
skip_welcome = input("Moo ngmã R ké o bé sɛ gbĩ ɔ túe bue. Press 'R' to skip the welcoming address or any other key to continue: ").strip().lower()
if skip_welcome != 'r':
    # Welcome the user
    print("Mo hee ekohũ kɛ ba Dãngme klãmã nɛ̃ tsɔ̃ɔ̃ nɔ̃ bɔ nɛ̃ a tsɛ ɔ nɔ́ hã!")

    # Play a welcoming audio file (add the file name here)
    welcome_audio_file = "mo hee.mp3"  # Replace with your actual welcome audio file name
    if os.path.exists(os.path.join(male_audio_dir, welcome_audio_file)):
        print("I kpaa mo pɛɛ nɛ̃ ó bu sɛ gbĩ nɛ ɔ túe......")
        play_audio([welcome_audio_file])
    else:
        print("Kusiɛ, wa nã nyãgba ngɛ́ sɛ gbĩ ɔ̃ he.")

# Ask the user for the playback speed
try:
    speed = float(input("I kpaa mo pɛɛ nɛ̃ o ngmã bɔnɛ̃ mã tsɛ́ aloo kané nɔ̃ hã mo hã( ké o ngmã 1.0 ɔ í mã tsɛ́ aloo kané nɔ̃ ɔ̃ blɛuu, ké o ngmã 1.5 ɔ í mã tsɛ́ aloo kané nɔ̃ ɔ̃ kɛ oyá bɔɔ, sé ké o ngmã 2.0 ɔ í mã tsɛ́ aloo kané nɔ̃ ɔ̃ oyá. Ké e sɔ nɛ̃ sũɔ̃ kle tsɔ̃ ɔ̃, o bé nũɛ̃ nɔ̃ nɛ̃ i mã dé ɔ): "))
except ValueError:
    print("Bɔ nɛ̃ o suɔ̃ nɛ̃ mã tsɛ́ aloo kané nɔ̃ nɛ̃ o ngmã ã bé hĩɛ̃ hã mĩ. Lɛɛ í mã tsɛ́ hã mo blɛuu mɔ́")
    speed = 1.0

# Main loop for user input
while True:
    user_input = input("I kpaa mo pɛɛ nɛ̃ ó ngma nɔ̃ nɛ́ o suɔ̃ nɛ́ mã tsɛ hã mo ɔ (aloo moo ngmã 'q' ké o gbe nyãã): ").strip().lower()
    if user_input == 'q':
        print("Ké Mawu sũɔ̃, wá mãã kpe!")
        break
    process_mixed_input(user_input, speed)