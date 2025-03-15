from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import soundfile as sf
import numpy as np
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Load from environment variable
app.debug = True

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Activity Log model
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Function to log user activity
def log_activity(user_id, username, ip_address, action):
    log = ActivityLog(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        action=action
    )
    db.session.add(log)
    db.session.commit()

# Define the directory containing the audio files
audio_dir = os.getenv('AUDIO_DIR', os.path.join(os.path.dirname(__file__), "audio_files"))

# Mapping of words and phonemes to corresponding audio files
valid_word_file_map = {
        "a": "A.wav", "à": "A.wav",  
    "á": "Á.wav", "ã": "Ã.wav", 

    "e": "E.wav", "è": "E.wav",  
    "é": "É.wav", "ẽ": "Ẽ.wav",  

    "ɛ": "Ɛ.wav", "ɛ̀": "Ɛ.wav",  
    "ɛ́": "Ɛ́.wav", "ɛ̃": "Ɛ̃.wav",  

    "i": "I.wav", "ì": "I.wav",  
    "í": "Í.wav", "ĩ": "Ĩ.wav",  
    
    "o": "O.wav", "ò": "O.wav",  
    "ó": "Ó.wav", "õ": "Õ.wav",  
    
    "ɔ": "Ɔ.wav", "ɔ̀": "Ɔ.wav",  
    "ɔ́": "Ɔ́.wav", "ɔ̃": "Ɔ̃.wav", 
    
    "u": "U.wav", "ù": "U.wav", 
    "ú": "Ú.wav", "ũ": "Ũ.wav",  

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
    "₵"   :"SÍDI.wav"
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

    # 1001 to 1010
    1001: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    1002: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    1003: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    1004: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    1005: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    1006: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    1007: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    1008: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    1009: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    1010: ["1000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 10,001 to 10,010
    10001: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    10002: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    10003: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    10004: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    10005: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    10006: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    10007: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    10008: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    10009: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    10010: ["10000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 100,001 to 100,010
    100001: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    100002: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    100003: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    100004: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    100005: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    100006: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    100007: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    100008: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    100009: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    100010: ["100000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 1,000,001 to 1,000,010
    1000001: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    1000002: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    1000003: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    1000004: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    1000005: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    1000006: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    1000007: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    1000008: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    1000009: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    1000010: ["1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 10,000,001 to 10,000,010
    10000001: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    10000002: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    10000003: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    10000004: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    10000005: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    10000006: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    10000007: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    10000008: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    10000009: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    10000010: ["10000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 100,000,001 to 100,000,010
    100000001: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    100000002: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    100000003: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    100000004: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    100000005: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    100000006: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    100000007: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    100000008: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    100000009: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    100000010: ["100000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 1,000,000,001 to 1,000,000,010
    1000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    1000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    1000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    1000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    1000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    1000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    1000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    1000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    1000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    1000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 10,000,000,001 to 10,000,000,010
    10000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    10000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    10000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    10000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    10000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    10000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    10000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    10000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    10000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    10000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,001 to 100,000,000,010
    100000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    100000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    100000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    100000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    100000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    100000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    100000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    100000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    100000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    100000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 1,000,000,000,001 to 1,000,000,000,010
    1000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    1000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    1000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    1000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    1000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    1000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    1000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    1000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    1000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    1000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "1.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 10,000,000,000,001 to 10,000,000,000,010
    10000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    10000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    10000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    10000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    10000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    10000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    10000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    10000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    10000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    10000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "10.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],

    # 100,000,000,000,001 to 100,000,000,000,010
    100000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "1.wav"],
    100000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "2.wav"],
    100000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "3.wav"],
    100000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "4.wav"],
    100000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "5.wav"],
    100000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "6.wav"],
    100000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "7.wav"],
    100000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "8.wav"],
    100000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "9.wav"],
    100000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "100.wav", "KƐ.wav", "E.wav", "NYÃ.wav", "10.wav"],


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

#2ssssssss

# 101 to 110
        201: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        202: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        203: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        204: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        205: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        206: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        207: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        208: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        209: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        210: ["100.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1001 to 1010
        2001: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        2002: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        2003: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        2004: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        2005: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        2006: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        2007: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        2008: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        2009: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        2010: ["1000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,001 to 10,010
        20001: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        20002: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        20003: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        20004: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        20005: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        20006: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        20007: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        20008: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        20009: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        20010: ["10000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,001 to 100,010
        200001: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        200002: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        200003: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        200004: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        200005: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        200006: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        200007: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        200008: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        200009: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        200010: ["100000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,001 to 1,000,010
        2000001: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        2000002: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        2000003: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        2000004: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        2000005: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        2000006: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        2000007: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        2000008: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        2000009: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        2000010: ["1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,001 to 10,000,010
        20000001: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        20000002: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        20000003: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        20000004: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        20000005: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        20000006: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        20000007: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        20000008: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        20000009: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        20000010: ["10000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,001 to 100,000,010
        200000001: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        200000002: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        200000003: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        200000004: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        200000005: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        200000006: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        200000007: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        200000008: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        200000009: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        200000010: ["100000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,001 to 1,000,000,010
        2000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        2000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        2000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        2000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        2000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        2000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        2000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        2000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        2000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        2000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,000,001 to 10,000,000,010
        20000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        20000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        20000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        20000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        20000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        20000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        20000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        20000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        20000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        20000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,000,001 to 100,000,000,010
        200000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        200000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        200000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        200000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        200000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        200000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        200000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        200000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        200000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        200000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,000,001 to 1,000,000,000,010
        2000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        2000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        2000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        2000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        2000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        2000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        2000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        2000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        2000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        2000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,000,000,001 to 10,000,000,000,010
        20000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        20000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        20000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        20000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        20000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        20000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        20000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        20000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        20000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        20000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "20.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,000,000,001 to 100,000,000,000,010
        200000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        200000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        200000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        200000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        200000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        200000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        200000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        200000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        200000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        200000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "200.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,000,000,001 to 1,000,000,000,000,010
        2000000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        2000000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        2000000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        2000000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        2000000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        2000000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        2000000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        2000000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        2000000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        2000000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "2.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        #3ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
        # 101 to 110
        301: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        302: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        303: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        304: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        305: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        306: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        307: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        308: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        309: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        310: ["100.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1001 to 1010
        3001: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        3002: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        3003: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        3004: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        3005: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        3006: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        3007: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        3008: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        3009: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        3010: ["1000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,001 to 10,010
        30001: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        30002: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        30003: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        30004: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        30005: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        30006: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        30007: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        30008: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        30009: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        30010: ["10000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,001 to 100,010
        300001: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        300002: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        300003: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        300004: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        300005: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        300006: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        300007: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        300008: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        300009: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        300010: ["100000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,001 to 1,000,010
        3000001: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        3000002: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        3000003: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        3000004: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        3000005: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        3000006: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        3000007: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        3000008: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        3000009: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        3000010: ["1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,001 to 10,000,010
        30000001: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        30000002: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        30000003: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        30000004: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        30000005: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        30000006: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        30000007: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        30000008: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        30000009: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        30000010: ["10000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,001 to 100,000,010
        300000001: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        300000002: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        300000003: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        300000004: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        300000005: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        300000006: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        300000007: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        300000008: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        300000009: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        300000010: ["100000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,001 to 1,000,000,010
        3000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        3000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        3000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        3000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        3000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        3000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        3000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        3000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        3000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        3000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,000,001 to 10,000,000,010
        30000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        30000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        30000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        30000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        30000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        30000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        30000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        30000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        30000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        30000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,000,001 to 100,000,000,010
        300000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        300000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        300000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        300000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        300000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        300000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        300000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        300000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        300000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        300000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,000,001 to 1,000,000,000,010
        3000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        3000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        3000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        3000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        3000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        3000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        3000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        3000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        3000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        3000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,000,000,001 to 10,000,000,000,010
        30000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        30000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        30000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        30000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        30000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        30000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        30000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        30000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        30000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        30000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "30.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,000,000,001 to 100,000,000,000,010
        300000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        300000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        300000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        300000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        300000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        300000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        300000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        300000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        300000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        300000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "300.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,000,000,001 to 1,000,000,000,000,010
        3000000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        3000000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        3000000000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        3000000000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        3000000000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        3000000000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        3000000000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        3000000000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        3000000000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        3000000000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "3.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        #4ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
        # 101 to 110
        401: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        402: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        403: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        404: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        405: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        406: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        407: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        408: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        409: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        410: ["100.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1001 to 1010
        4001: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        4002: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        4003: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        4004: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        4005: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        4006: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        4007: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        4008: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        4009: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        4010: ["1000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,001 to 10,010
        40001: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        40002: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        40003: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        40004: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        40005: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        40006: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        40007: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        40008: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        40009: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        40010: ["10000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,001 to 100,010
        400001: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        400002: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        400003: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        400004: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        400005: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        400006: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        400007: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        400008: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        400009: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        400010: ["100000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,001 to 1,000,010
        4000001: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        4000002: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        4000003: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        4000004: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        4000005: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        4000006: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        4000007: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        4000008: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        4000009: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        4000010: ["1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,001 to 10,000,010
        40000001: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        40000002: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        40000003: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        40000004: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        40000005: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        40000006: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        40000007: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        40000008: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        40000009: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        40000010: ["10000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,001 to 100,000,010
        400000001: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        400000002: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        400000003: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        400000004: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        400000005: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        400000006: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        400000007: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        400000008: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        400000009: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        400000010: ["100000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,001 to 1,000,000,010
        4000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        4000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        4000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        4000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        4000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        4000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        4000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        4000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        4000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        4000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 10,000,000,001 to 10,000,000,010
        40000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        40000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        40000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        40000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        40000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        40000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        40000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        40000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        40000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        40000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 100,000,000,001 to 100,000,000,010
        400000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        400000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
        400000000003: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "3.wav"],
        400000000004: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "4.wav"],
        400000000005: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "5.wav"],
        400000000006: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "6.wav"],
        400000000007: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "7.wav"],
        400000000008: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "8.wav"],
        400000000009: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "9.wav"],
        400000000010: ["1000000.wav", "MĨ.wav", "1000000.wav", "400.wav", "KƐ.wav", "NYÃ.wav", "10.wav"],

        # 1,000,000,000,001 to 1,000,000,000,010
        4000000000001: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "1.wav"],
        4000000000002: ["1000000.wav", "MĨ.wav", "1000000.wav", "MĨ.wav", "1000000.wav", "4.wav", "KƐ.wav", "NYÃ.wav", "2.wav"],
}

# Updated function to generate the correct sequence of .wav files for a number
def generate_wav_sequence(number):
    if number in master_code:
        return master_code[number]
    elif number < 1:
        return []
    else:
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
            1000000: "1000000.wav"
        }

        ke_wav = "KƐ.wav"
        mi_wav = "MĨ.wav"
        ngwohe_wav = "ngwɔhé.wav"
        
        def get_wav(digit):
            return base_wavs.get(digit, "")

        def get_wav(digit):
            return base_wavs.get(digit, "")

        def handle_teens(num):
            return [get_wav(10), ke_wav, get_wav(num % 10)]

        def handle_tens(num):
            tens = (num // 10) * 10
            units = num % 10
            if units == 0:
                return [get_wav(tens)]
            else:
                return [get_wav(tens), ke_wav, get_wav(units)]
            
            # Function to handle numbers between 20 and 99
        def handle_tens(num):
            tens = (num // 10) * 10
            units = num % 10
            if units == 0:
                return [get_wav(tens), get_wav(tens // 10)]
            else:
                return [get_wav(tens), get_wav(tens // 10), ke_wav, get_wav(units)]

       
        def handle_hundreds(num):
            hundreds = num // 100
            remainder = num % 100
            if remainder == 0:
                return [get_wav(100), get_wav(hundreds)]
            else:
                return [get_wav(100), get_wav(hundreds)] + generate_wav_sequence(remainder)

        def handle_thousands(num):
            thousands = num // 1000
            remainder = num % 1000
            if remainder == 0:
                return [get_wav(1000)] + generate_wav_sequence(thousands)
            else:
                return [get_wav(1000), get_wav(ke), get_wav(nya)] + generate_wav_sequence(thousands) + generate_wav_sequence(remainder)

        def handle_millions(num):
            millions = num // 1000000
            remainder = num % 1000000
            if remainder == 0:
                return [get_wav(1000), get_wav(1000)]  # Million is 1000.wav + 1000.wav
            else:
                return [get_wav(1000), get_wav(1000)] + generate_wav_sequence(remainder)

        def handle_billions(num):
            billions = num // 1000000000
            remainder = num % 1000000000
            if remainder == 0:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000)] 
            else:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000)] + generate_wav_sequence(remainder)

        def handle_trillions(num):
            trillions = num // 1000000000000
            remainder = num % 1000000000000
            if remainder == 0:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000), get_wav(1000)]  
            else:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000), get_wav(1000)] + generate_wav_sequence(remainder)

        def handle_quadrillions(num):
            quadrillions = num // 1000000000000000
            remainder = num % 1000000000000000
            if remainder == 0:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000)] 
            else:
                return [get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000), get_wav(1000), ngwohe_wav, get_wav(1000)] + generate_wav_sequence(remainder)

        # Updated number handling for 1001+
        def handle_thousands(num):
            if num in master_code:
                return master_code[num]
            
            thousands = num // 1000
            remainder = num % 1000
            if remainder == 0:
                return [get_wav(1000)] + generate_wav_sequence(thousands)
            else:
                return [get_wav(1000)] + generate_wav_sequence(thousands) + [ke_wav, "E.wav", "NYÃ.wav"] + generate_wav_sequence(remainder)

        def handle_large_numbers(num):
            # Define the magnitude names and their corresponding powers of 10
            magnitudes = [
                (100, "Hundred"),
                (1000, "Thousand"),
                (1000000, "Million"),
                (1000000000, "Billion"),
                (1000000000000, "Trillion"),
                (1000000000000000, "Quadrillion"),
                (10**18, "Quintillion"),
                (10**21, "Sextillion"),
                (10**24, "Septillion"),
                (10**27, "Octillion"),
                (10**30, "Nonillion"),
                (10**33, "Decillion"),
                (10**36, "Undecillion"),
                (10**39, "Duodecillion"),
                (10**42, "Tredecillion"),
                (10**45, "Quattuordecillion"),
                (10**48, "Quindecillion"),
                (10**51, "Sexdecillion"),
                (10**54, "Septendecillion"),
                (10**57, "Octodecillion"),
                (10**60, "Novemdecillion"),
                (10**63, "Vigintillion"),
                (10**303, "Centillion")
            ]

            # Find the appropriate magnitude for the number
            for magnitude, name in reversed(magnitudes):
                if num >= magnitude:
                    quotient = num // magnitude
                    remainder = num % magnitude
                    if remainder == 0:
                        return generate_wav_sequence(quotient) + [get_wav(magnitude)]
                    else:
                        return generate_wav_sequence(quotient) + [get_wav(magnitude)] + generate_wav_sequence(remainder)
            return []

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
        elif 1000000000000000 <= number < 10**18:
            return handle_quadrillions(number)
        else:
            return handle_large_numbers(number)

# Function to split text into phonemes or complete words, ignoring spaces
def split_into_phonemes(text, phoneme_map):
    # Remove all spaces from the text
    text = text.replace(" ", "")
    phonemes = []
    i = 0
    while i < len(text):
        # Check if the current character or a sequence of characters exists in the phoneme map
        for j in range(min(len(text), i + 5), i, -1):  # Check sequences up to 5 characters long
            substring = text[i:j]
            if substring in phoneme_map:
                phonemes.append(phoneme_map[substring])
                i = j
                break
        else:
            # If no sequence is found, move to the next character
            i += 1
    return phonemes

# Function to concatenate audio files
def concatenate_audio(files, speed=1.0):
    combined_audio = np.array([])
    sample_rate = None
    valid_files_processed = 0

    try:
        speed = float(speed)
    except ValueError:
        speed = 1.0

    for file in files:
        filepath = os.path.join(audio_dir, file)
        if os.path.exists(filepath):
            try:
                data, fs = sf.read(filepath)
                if sample_rate is None:
                    sample_rate = int(fs * speed)

                if data.dtype != np.float32:
                    data = data.astype(np.float32)

                # Skip 6% of the audio at the beginning and end
                start_index = int(0.06 * len(data))
                end_index = len(data) - int(0.25 * len(data))
                data = data[start_index:end_index]

                combined_audio = np.concatenate((combined_audio, data))
                valid_files_processed += 1
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")
        else:
            print(f"Warning: Audio file not found: {file}")

    if valid_files_processed == 0:
        raise ValueError("No valid audio files found to process.")
    return combined_audio, sample_rate

# Serve static audio files
@app.route('/audio_files/<filename>')
def serve_audio(filename):
    return send_from_directory(audio_dir, filename)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log_activity(user.id, user.username, request.remote_addr, "Logged in")
            return redirect(url_for('app'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, user.username, request.remote_addr, "Registered")
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))  # Redirect to login page after registration
    return render_template('register.html')

# Main app route
@app.route('/app')
@login_required
def app_route():
    return render_template('app.html')

# TTS route to handle user input
@app.route('/tts', methods=['POST'])
@login_required
def tts():
    data = request.json
    text = data.get('text')
    speed = data.get('speed', 1.0)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        tokens = re.findall(r'\d+|\D+', text)
        audio_files = []
        for token in tokens:
            if token.isdigit():
                sequence = generate_wav_sequence(int(token))
                audio_files.extend(sequence)
            else:
                phonemes = split_into_phonemes(token, valid_word_file_map)
                audio_files.extend(phonemes)

        if not audio_files:
            return jsonify({"error": "No valid audio files found for the input text"}), 400

        combined_audio, sample_rate = concatenate_audio(audio_files, speed)
        audio_buffer = BytesIO()
        sf.write(audio_buffer, combined_audio, sample_rate, format='WAV')
        audio_buffer.seek(0)
        
        return send_file(audio_buffer, mimetype='audio/wav')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Activity Logs route
@app.route('/activity_logs')
@login_required
def activity_logs():
    if request.remote_addr != "my_ip_address":  # Replace with your IP address
        return "Access denied", 403
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    return render_template('activity_logs.html', logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000, debug=True)