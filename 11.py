
import os
import sounddevice as sd
import soundfile as sf
import re
import sys

# Welcome message
print("Mo hee kɛ ba Dangme klãmã nɛ̃ tsɔ̃ɔ̃ nɔ̃ bɔ nɛ̃ a tsɛ ɔ nɔ́ hã!")
print("I kpaa mo pɛɛ nɛ̃ ó ngma nɔ̃ nɛ́ o suɔ̃ nɛ́ mã tsɛ hã mo ɔ.")

# Directory containing the phoneme audio files
audio_dir = r"C:\Users\jacob\OneDrive\Desktop\Der Feige droht nur, wo er sicher ist\TTS"

# Comprehensive mapping of all recorded phonemes and words to corresponding file names
valid_word_file_map = {
    # A vowel grouping: A, À are the same, but different from Á and Ã
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
    "ɔ́": "Ɔ́.wav", "ɔ̃": ".Ɔ̃wav",  # Different sounds

    # U vowel grouping: U, Ù are the same, but different from Ú and Ũ
    "u": "U.wav", "ù": "U.wav",  # Same sound
    "ú": "Ú.wav", "ũ": "Ũ.wav",  # Different sounds

    # Consonant mappings (These remain unaffected)
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

    # Word mappings with distinct tonal vowel variations
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






    ###### corrections
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
    
    
#Numerals           # Numerals                        # Numerals
    "kake": "1.wav", "1": "1.wav",
    "enyɔ": "2.wav", "2": "2.wav",
    "etɛ̃": "3.wav", "3": "3.wav",
    "eywiɛ": "4.wav", "4": "4.wav",
    "enuɔ": "5.wav", "5": "5.wav",
    "ekpa": "6.wav", "6": "6.wav",
    "kpaago": "7.wav", "7": "7.wav",
    "kpaanyɔ": "8.wav", "8": "8.wav",
    "nɛ̃ɛ̃": "9.wav", "9": "9.wav",
    "nyɔngmá": "10.wav", "10": "10.wav",
    "nyingmí enyƆ": "20.wav", "20": "20.wav",
    "nyingmí etƐ̃": "30.wav", "30": "30.wav",
    "nyingmí eywiƐ": "40.wav", "40": "40.wav",
    "nyingmí enuƆ": "50.wav", "50": "50.wav",
    "nyingmí ekpa": "60.wav", "60": "60.wav",
    "nyingmí kpaago": "70.wav", "70": "70.wav",
    "nyingmí kpaanyƆ": "80.wav", "80": "80.wav",
    "nyingmí nƐ̃Ɛ̃": "90.wav", "90": "90.wav",
    "lafá": "100.wav", "100": "100.wav",
    "akpé kake": "1000.wav", "1000": "1000.wav",
    "ayɔ kake": "1000000.wav", "1000000": "1000000.wav",
    
    }





# Function to split input text into possible phoneme sequences
def split_into_phonemes(text, phoneme_map):
    phonemes = []
    i = 0
    while i < len(text):
        for j in range(len(text), i, -1):
            substring = text[i:j]
            if substring in phoneme_map:
                phonemes.append(substring)
                i = j
                break
        else:
            # If no valid phoneme is found, proceed to the next character (this might be improved)
            i += 1
    return phonemes

# Function to play the phonemes
def play_phonemes(phonemes, phoneme_map, audio_directory):
    for phoneme in phonemes:
        audio_file = os.path.join(audio_directory, phoneme_map[phoneme])
        if os.path.exists(audio_file):
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate)
            sd.wait()
        else:
            print(f"E pe ɔ mi kãã '{phoneme}' yá pee wé Dangme munyu ngu aloo wa tui he blɔ nya ngɛ́ wa klãmã a mi lolo.")

# Main loop for user input
while True:
    # Input the text to be spoken
    user_input = input("I kpaa mo pɛɛ nɛ̃ ó ngma nɔ̃ nɛ́ o suɔ̃ nɛ́ mã tsɛ hã mo ɔ: ").strip().lower()
    
    if user_input == 'exit':
        print("Ké Mawu sũɔ̃, wá mãã kpe!.")
        break
    
    # Split the input text into valid phonemes
    phonemes = split_into_phonemes(user_input, valid_word_file_map)
    
    # Play the phonemes
    if phonemes:
        print(f" I kpaa mo pɛɛ nɛ̃ ó bu tue be mĩ nɛ̃ I yaa tsɛ aloo kane: {' '.join(phonemes)}")
        play_phonemes(phonemes, valid_word_file_map, audio_dir)
    else:
        print("E pe ɔ mĩ kãã nɔ̃ nɛ̃ o ngmãã yá pee wé Dangme munyu ngú aloo wa tui he blɔ nya ngɛ́ wa klãmã a mi lolo.")