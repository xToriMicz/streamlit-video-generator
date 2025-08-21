#!/usr/bin/env python3
"""
CREATE SHORT 60S - Video Generator (Streamlit Web Version)
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import threading
import json
import time
import requests
import base64
import tempfile
import math
import hashlib
import gc
import logging
import io
import zipfile
import shutil
import re
import pickle
import psutil
import getpass
from cryptography.fernet import Fernet
import imageio_ffmpeg as ffmpeg

import streamlit as st

# Configure logging ()
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Exception Classes ()
class SecurityError(Exception):
    """Exception สำหรับปัญหาด้านความปลอดภัย"""
    pass

class APIError(Exception):
    """Exception สำหรับปัญหา API"""
    pass

# Streamlit Configuration ()
st.set_page_config(
    page_title="🎬 CREATE SHORT 60S - Video Generator",
    page_icon="🎬",
    layout="centered",  # เปลี่ยนจาก wide เป็น centered เหมือน PyQt6
    initial_sidebar_state="collapsed"  # ซ่อน sidebar เริ่มต้น
)

# CSS Minimal Style with Noto Sans Thai ()
st.markdown("""
<style>
    /* Import Noto Sans Thai font */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap');
    
    /* Global font settings */
    * {
        font-family: "Noto Sans Thai", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    /* Main container - minimal width */
    .main > div {
        max-width: 480px;
        padding: 1.5rem 1rem;
        margin: 0 auto;
    }
    
    /* Header styling - โดดเด่นขึ้น */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #667eea; /* fallback */
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
    }
    
    .subtitle {
        color: #374151;
        font-size: 14px;
        text-align: center;
        margin-bottom: 24px;
        font-weight: 500;
        opacity: 0.9;
    }
    
    /* Input frame - minimal borders */
    .input-frame {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .section-label {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: -0.1px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    
    /* Form inputs - minimal style */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #374151 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;        
        font-size: 14px !important;
        font-weight: 400 !important;        
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {        
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Select dropdown - minimal */
    .stSelectbox > div > div > select {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        color: #0f172a !important;
        font-weight: 400 !important;
        font-size: 14px !important;
        min-width: 160px;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Buttons - minimal style */
    .stButton > button {
        background-color: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #2563eb !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        min-height: 40px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.2px;
    }
    
    .stButton > button:hover {
        background-color: #f8fafc !important;
        border-color: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:active {
        background-color: #f1f5f9 !important;
        border-color: #1e40af !important;
        transform: translateY(0);
    }
    
    /* Primary button - โดดเด่นและสวยขึ้น */
    .primary-button > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .primary-button > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4395 100%) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Settings button - ปรับปรุงให้โดดเด่น */
    .settings-button > button {
        background-color: #ffffff !important;
        color: #374151 !important;
        border: 2px solid #d1d5db !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        min-height: 42px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .settings-button > button:hover {
        background-color: #f9fafb !important;
        border-color: #9ca3af !important;
        color: #111827 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Progress container - minimal */
    .progress-container {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Progress bar - minimal blue */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 50%, #dbeafe 100%) !important;
        border-radius: 6px;
        border: none;
    }
    
    /* Status text - minimal */
    .status-text {
        font-size: 13px;
        color: #1e40af;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    .progress-text {
        font-size: 11px;
        color: #1d4ed8;
        font-weight: 600;
        text-align: center;
        margin-top: 4px;
        letter-spacing: 0.3px;
    }
    
    /* Settings dialog - minimal */
    .settings-dialog {
        background-color: #fefefe;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .settings-title {
        font-size: 20px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #667eea; /* fallback */
        text-align: center;
        margin-bottom: 24px;
        letter-spacing: -0.3px;
    }
    
    .api-key-label {
        font-size: 16px;
        color: #ffffff;
        margin-bottom: 8px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Output area - minimal */
    .output-section {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Success/Error messages - minimal */
    .stSuccess {
        background-color: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #166534 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #dc2626 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border: 1px solid #fed7aa !important;
        color: #d97706 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    .stInfo {
        background-color: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        color: #1d4ed8 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    /* Download button - minimal */
    .stDownloadButton > button {
        background-color: #10b981 !important;
        color: #ffffff !important;
        border: 1px solid #10b981 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #059669 !important;
        border-color: #047857 !important;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    /* Expander - minimal */
    .streamlit-expanderHeader {
        background-color: #f3f4f6 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e5e7eb !important;
        border-color: #9ca3af !important;
        color: #111827 !important;
    }
</style>
""", unsafe_allow_html=True)

# Secure API Key Management ()
class SecureAPIKeyManager:
    """คลาสสำหรับจัดการ API Keys อย่างปลอดภัยด้วยการเข้ารหัส"""
    
    def __init__(self):
        self.app_name = "FFMPEG_SHORT_40S_GENERATOR"
        self.username = getpass.getuser()
        try:
            # ใช้ session state แทน keyring ใน web version
            self.encryption_key = self._get_or_create_encryption_key()
            self.fernet = Fernet(self.encryption_key)
        except:
            # Fallback สำหรับ web version
            self.fernet = None
    
    def _get_or_create_encryption_key(self):
        """สร้าง encryption key สำหรับ session"""
        if 'encryption_key' not in st.session_state:
            st.session_state.encryption_key = Fernet.generate_key()
        return st.session_state.encryption_key
    
    def save_api_key(self, key_name, api_key):
        """บันทึก API key อย่างปลอดภัย"""
        try:
            if not api_key or api_key.strip() == "":
                # ลบ key ถ้าเป็นค่าว่าง
                if f'secure_{key_name}' in st.session_state:
                    del st.session_state[f'secure_{key_name}']
                return True
            
            # เข้ารหัส API key
            if self.fernet:
                encrypted_key = self.fernet.encrypt(api_key.strip().encode())
                st.session_state[f'secure_{key_name}'] = base64.urlsafe_b64encode(encrypted_key).decode()
            else:
                st.session_state[f'secure_{key_name}'] = api_key.strip()
            return True
            
        except Exception as e:
            log_error(e, f"การบันทึก API key: {key_name}")
            return False
    
    def get_api_key(self, key_name):
        """ดึง API key ที่ถอดรหัสแล้ว"""
        try:
            encrypted_data = st.session_state.get(f'secure_{key_name}', "")
            
            if not encrypted_data:
                return ""
            
            # ถอดรหัส
            if self.fernet:
                encrypted_key = base64.urlsafe_b64decode(encrypted_data.encode())
                decrypted_key = self.fernet.decrypt(encrypted_key)
                return decrypted_key.decode()
            else:
                return encrypted_data
                
        except Exception as e:
            log_error(e, f"การดึง API key: {key_name}")
            return ""
    
    def get_all_api_keys(self):
        """ดึง API keys ทั้งหมด"""
        keys = {}
        key_names = ['OPENAI_KEY', 'GOOGLE_TTS_KEY', 'FAL_AI_KEY']
        
        for key_name in key_names:
            keys[key_name] = self.get_api_key(key_name)
        
        return keys
    
    def save_all_api_keys(self, keys_dict):
        """บันทึก API keys ทั้งหมด"""
        success_count = 0
        for key_name, api_key in keys_dict.items():
            if self.save_api_key(key_name, api_key):
                success_count += 1
        
        return success_count == len(keys_dict)
    
    def has_any_keys(self):
        """ตรวจสอบว่ามี API keys ที่บันทึกไว้หรือไม่"""
        keys = self.get_all_api_keys()
        return any(key.strip() for key in keys.values())

# Template Manager ()
class TemplateManager:
    def __init__(self):
        self.templates_file = Path("prompt_templates.json")
        self.load_templates()
    
    def load_templates(self):
        """โหลดเทมเพลตจากไฟล์ JSON"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            else:
                self.templates = self.get_default_templates()
                self.save_templates()
        except Exception:
            self.templates = self.get_default_templates()
    
    def get_default_templates(self):
        """เทมเพลตเริ่มต้น"""
        return {
            "default": {
                "name": "เทมเพลตเริ่มต้น",
                "prompt": """กรุณาสร้างสคริปต์เล่าประวัติศาสตร์เรื่อง: "{topic}"

คำแนะนำ:
- ความยาวรวม: ไม่เกิน 60 วินาที เมื่อพูดออกเสียง (ประมาณ 200-205 ตัวอักษร รวมเว้นวรรค หรือ 115-125 โทเคน)
- ใช้ภาษาไทยที่สร้างบรรยากาศน่าสนใจ เล่าได้อย่างชวนติดตาม เหมาะสำหรับการอ่านออกเสียงด้วยเสียงชายที่ใส มีพลัง
- โครงสร้างควรประกอบด้วย: การเปิดเรื่องที่ดึงดูดความสนใจ, การดำเนินเหตุการณ์สำคัญ, จุดเปลี่ยนหรือไฮไลท์, และการสรุปความสำคัญ
- เขียนในรูปแบบการเล่าเรื่องที่น่าสนใจ ใช้คำว่า "คุณ" เพื่อให้ผู้ฟังรู้สึกเป็นส่วนหนึ่งของประวัติศาสตร์
- ไม่ต้องมีการจัดรูปแบบพิเศษ เช่น หัวข้อ ลำดับเลข หรือเครื่องหมายวรรคตอนพิเศษ
- ให้เป็นข้อความต่อเนื่องกันไปเลย ไม่ต้องแบ่งย่อหน้า
- ใส่ข้อเท็จจริงที่น่าสนใจ หรือรายละเอียดที่ไม่ค่อยมีคนรู้ 1-2 จุด
- จบด้วยการสรุปความสำคัญของเหตุการณ์นั้นและชวนให้ผู้ฟังติดตามเรื่องเล่าต่อไป

สคริปต์เรื่องเล่า:"""
            },
            "fairy_tale": {
                "name": "นิทานสำหรับเด็ก",
                "prompt": """สร้างนิทานสำหรับเด็กเรื่อง: "{topic}"

คำแนะนำ:
- ความยาวรวม: ไม่เกิน 60 วินาที เมื่อพูดออกเสียง (ประมาณ 200-205 ตัวอักษร รวมเว้นวรรค หรือ 115-125 โทเคน)
- ใช้ภาษาง่ายๆ เหมาะสำหรับเด็ก
- มีตัวละครที่น่าสนใจและมีบุคลิกชัดเจน
- มีข้อคิดหรือคติสอนใจ
- ใช้คำซ้ำและจังหวะที่สนุก
- จบด้วยข้อคิดดีๆ
- ให้เป็นข้อความต่อเนื่องกันไปเลย ไม่ต้องแบ่งย่อหน้า

นิทาน:"""
            },
            "sales": {
                "name": "สคริปต์ขายสินค้า",
                "prompt": """สร้างสคริปต์ขายสินค้า: "{topic}"

คำแนะนำ:
- ความยาวรวม: ไม่เกิน 60 วินาที เมื่อพูดออกเสียง (ประมาณ 200-205 ตัวอักษร รวมเว้นวรรค หรือ 115-125 โทเคน)
- เน้นประโยชน์และคุณค่าของสินค้า
- สร้างความต้องการและความเร่งด่วน
- ใช้คำที่กระตุ้นอารมณ์ (สุดพิเศษ, จำกัด, โอกาสเดียว)
- มี call-to-action ที่ชัดเจน
- เน้นความคุ้มค่าและข้อเสนอพิเศษ
- ให้เป็นข้อความต่อเนื่องกันไปเลย ไม่ต้องแบ่งย่อหน้า

สคริปต์ขาย:"""
            }
        }
    
    def get_template(self, template_id):
        """ดึงเทมเพลตตาม ID"""
        return self.templates.get(template_id, self.templates.get("story", {}))
    
    def get_template_list(self):
        """ดึงรายการเทมเพลตสำหรับ dropdown"""
        return [(k, v.get('name', k)) for k, v in self.templates.items()]
    
    def save_templates(self):
        """บันทึกเทมเพลตลงไฟล์"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

# Initialize managers ()
if 'api_manager' not in st.session_state:
    st.session_state.api_manager = SecureAPIKeyManager()
if 'template_manager' not in st.session_state:
    st.session_state.template_manager = TemplateManager()

# Initialize API keys with default values for testing ()
if 'api_keys_initialized' not in st.session_state:
    st.session_state.api_keys_initialized = True
    # Set default API keys for testing
    st.session_state.api_manager.save_all_api_keys({
        'OPENAI_KEY': '',
        'GOOGLE_TTS_KEY': '',  # Add your Google TTS API key
        'FAL_AI_KEY': ''  # Add your FAL AI API key
    })

# Helper Functions ()
def get_ffmpeg_path():
    """หา path ของ ffmpeg สำหรับทั้ง local และ cloud"""
    try:
        # ลองหา ffmpeg.exe ในโฟลเดอร์ปัจจุบัน (local)
        if os.path.exists('./ffmpeg.exe'):
            return './ffmpeg.exe'
        
        # ใช้ imageio-ffmpeg สำหรับ cloud deployment
        return ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        try:
            log_error(e, "Get FFmpeg Path")
        except:
            pass
        return 'ffmpeg'  # fallback ใช้ system ffmpeg

def log_error(error, context="", response_text=""):
    """บันทึก error อย่างปลอดภัยพร้อมรายละเอียด"""
    import traceback
    
    error_details = []
    error_details.append(f"Error Type: {type(error).__name__}")
    error_details.append(f"Error Message: {str(error)}")
    
    if response_text:
        error_details.append(f"Response Text (first 200 chars): {response_text[:200]}")
    
    # เพิ่ม traceback สำหรับ debug
    error_details.append(f"Traceback: {traceback.format_exc()}")
    
    error_msg = f"[{context}] {' | '.join(error_details)}" if context else ' | '.join(error_details)
    logging.error(error_msg)
    
    # แสดงใน console ด้วย
    print(f"ERROR [{context}]: {error_msg}")

def get_user_friendly_error(error, operation=""):
    """แปลง error เป็นข้อความที่ผู้ใช้เข้าใจได้โดยไม่เปิดเผยข้อมูลระบบ"""
    error_str = str(error)
    error_type = type(error).__name__
    
    if "APIError" in error_type:
        return error_str
    
    error_mappings = {
        "FileNotFoundError": f"ไม่พบไฟล์ที่จำเป็นสำหรับ{operation}",
        "PermissionError": f"ไม่มีสิทธิ์เข้าถึงไฟล์สำหรับ{operation}",
        "ConnectionError": f"ไม่สามารถเชื่อมต่อเครือข่ายสำหรับ{operation} - ตรวจสอบอินเทอร์เน็ต",
        "TimeoutError": f"หมดเวลารอสำหรับ{operation} - ลองใหม่อีกครั้ง",
        "requests.exceptions.RequestException": f"เกิดปัญหาเชื่อมต่อ API สำหรับ{operation}"
    }
    
    if "Read timed out" in error_str or "timeout" in error_str.lower():
        return f"เครือข่ายช้า - รอให้การเชื่อมต่อดีขึ้นแล้วลองใหม่\n\nคำแนะนำ:\n- ตรวจสอบสัญญาณอินเทอร์เน็ต\n- ปิด VPN (ถ้ามี)\n- ลองใหม่ในเวลาที่เครือข่ายดีกว่า"
    
    return error_mappings.get(error_type, f"เกิดข้อผิดพลาดไม่ทราบสาเหตุสำหรับ{operation}")

def sanitize_filename(filename):
    """ทำความสะอาดชื่อไฟล์"""
    if not filename:
        return "untitled"
    
    filename = str(filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    filename = filename[:100]
    
    if not filename.strip():
        filename = "untitled"
    
    return filename.strip()

def validate_api_keys():
    """ตรวจสอบว่ามี API keys ที่จำเป็น"""
    api_manager = st.session_state.api_manager
    keys = api_manager.get_all_api_keys()
    required_keys = ['OPENAI_KEY', 'FAL_AI_KEY']  # Google TTS is optional
    missing_keys = []
    
    for key_name in required_keys:
        if not keys.get(key_name, "").strip():
            missing_keys.append(key_name)
    
    return len(missing_keys) == 0, missing_keys

# Video Generation Functions ()
def create_story_script(topic, template_category="story"):
    """สร้างสคริปต์เรื่องเล่าจาก OpenAI ()"""
    try:
        api_manager = st.session_state.api_manager
        openai_key = api_manager.get_api_key('OPENAI_KEY')
        
        if not openai_key:
            raise APIError("ไม่พบ OpenAI API Key")
        
        template_manager = st.session_state.template_manager
        template = template_manager.get_template(template_category)
        
        base_prompt = template.get('prompt', 'สร้างเรื่องเล่าเกี่ยวกับ "{topic}"')
        
        prompt = f"""สร้างสคริปต์สำหรับวิดีโอสั้น 60 วินาที เรื่อง "{topic}"

{base_prompt.format(topic=topic)}

ข้อกำหนด:
1. เนื้อหาต้องน่าสนใจและติดตาม
2. เหมาะสำหรับอ่านใน 60 วินาที (ประมาณ 200-205 ตัวอักษร รวมเว้นวรรค หรือ 115-125 โทเคน)
3. ใช้ภาษาไทยที่เข้าใจง่าย
4. เน้นจุดเด่นที่สำคัญ
5. จบด้วยการเรียกการกระทำ (Call to Action)

รูปแบบ:
[เนื้อหาสคริปต์]"""

        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'คุณเป็นนักเขียนสคริปต์วิดีโอสั้นมืออาชีพ'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            try:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            except json.JSONDecodeError as e:
                log_error(e, "OpenAI Story Script JSON Parse", response.text)
                raise APIError(f"Failed to parse OpenAI response: {str(e)}")
        else:
            raise APIError(f"OpenAI API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_error(e, "OpenAI Story Script", getattr(response, 'text', ''))
        raise e

def create_title_description(story_script):
    """สร้าง Title และ Description จาก OpenAI ()"""
    try:
        api_manager = st.session_state.api_manager
        openai_key = api_manager.get_api_key('OPENAI_KEY')
        
        if not openai_key:
            raise APIError("ไม่พบ OpenAI API Key")
        
        prompt = f"""
        สร้าง Title and Description for Youtube ให้มีความน่าสนใจ เร้าอารมณ์ น่าติดตามจากไอเดียด้านล่างนี้:
        {story_script}

        ** เขียนเป็นภาษาไทย **
        ** Title สั้นๆ **
        ** Description (ไม่เกิน 50 คำ) เพิ่มแฮชแท็ก **

        Output Format:
        {{  
          "title": "Title",
          "description": "Description"  
        }}
        """

        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'คุณเป็นผู้เชี่ยวชาญด้านการตลาดเนื้อหา'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 200,
            'temperature': 0.5
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions',
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            try:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                try:
                    # ลอง parse JSON ก่อน
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    log_error(e, "OpenAI Title Description Content JSON Parse", content)
                    # ถ้า JSON ไม่ได้ ให้แยกแบบเดิม
                    lines = content.split('\n')
                    title = ""
                    description = ""
                    
                    for line in lines:
                        if line.startswith('Title:'):
                            title = line.replace('Title:', '').strip()
                        elif line.startswith('Description:'):
                            description = line.replace('Description:', '').strip()
                    
                    return {'title': title, 'description': description}
            except json.JSONDecodeError as e:
                log_error(e, "OpenAI Title Description Response JSON Parse", response.text)
                raise APIError(f"Failed to parse OpenAI response: {str(e)}")
        else:
            raise APIError(f"OpenAI API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_error(e, "OpenAI Title Description", getattr(response, 'text', ''))
        raise e

def generate_audio(text, language='th'):
    """สร้างไฟล์เสียงด้วย Google TTS หรือ fallback"""
    try:
        # Get Google TTS API key from session state
        api_manager = st.session_state.api_manager
        google_tts_key = api_manager.get_api_key('GOOGLE_TTS_KEY')
        
        if not google_tts_key:
            log_error("Google TTS API key not found", "Google TTS Audio")
            return create_silent_audio()
        
        # Clean text for TTS
        cleaned_text = clean_text_for_tts(text)
        
        # Use Gemini TTS API (เหมือน PyQt6 ที่ทำงานได้)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:streamGenerateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "role": "user",
                "parts": [{"text": cleaned_text}]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "temperature": 1,
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": "Achird"
                        }
                    }
                }
            }
        }
        
        response = requests.post(f"{url}?key={google_tts_key}", 
                               headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        try:
            if isinstance(response_data, list) and len(response_data) > 0:
                base64_data = response_data[0]["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            elif "candidates" in response_data:
                base64_data = response_data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            else:
                raise Exception("ไม่พบโครงสร้าง response ที่คาดหวัง")
        except (KeyError, IndexError) as e:
            raise Exception(f"ไม่สามารถแยกข้อมูลเสียงจาก response: {e}")
        
        audio_buffer = base64.b64decode(base64_data)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        with open(audio_file.name, 'wb') as f:
            f.write(create_wav_file(audio_buffer))
        
        return audio_file.name
            
    except Exception as e:
        log_error(e, "Google TTS Audio")
        # Fallback on any error
        return create_silent_audio()

def clean_text_for_tts(text):
    """ทำความสะอาดข้อความสำหรับ TTS แบบปรับปรุง"""
    import re
    
    # STEP 1: จัดการอักขระพิเศษก่อน (ตามความต้องการ)
    cleaned = text.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    cleaned = cleaned.replace('"', ' ').replace("'", ' ')
    cleaned = cleaned.replace('"', ' ').replace('"', ' ')  # smart quotes
    cleaned = cleaned.replace(''', ' ').replace(''', ' ')  # smart single quotes
    cleaned = cleaned.replace('*', ' ')
    
    # STEP 2: จัดการเครื่องหมาย ? ! ก่อน
    cleaned = cleaned.replace('?!', ' ')  # ลบ ?! ที่ซ้อนกัน
    cleaned = cleaned.replace('!!!', '!').replace('!!', '!')  # ลด !!! และ !! เป็น !
    cleaned = cleaned.replace('???', '?').replace('??', '?')  # ลด ??? และ ?? เป็น ?
    
    # STEP 3: จัดการตัวเลขและ comma
    # จัดการตัวเลขที่มี comma ก่อน (เช่น 1,000)
    cleaned = re.sub(r'\b(\d{1,3}(?:,\d{3})+)\b', 
                     lambda m: number_to_thai_text(m.group(1)), cleaned)
    # จัดการช่วงตัวเลข (เช่น 1-15)
    cleaned = re.sub(r'\b(\d+)-(\d+)\b', 
                     lambda m: f"{number_to_thai_text(m.group(1))} ถึง {number_to_thai_text(m.group(2))}", cleaned)
    # แปลงตัวเลขปกติเป็นคำไทย
    cleaned = re.sub(r'\b\d+\b', lambda m: number_to_thai_text(m.group()), cleaned)
    
    # STEP 4: จัดการสัญลักษณ์อื่นๆ
    cleaned = cleaned.replace('#', ' ').replace('_', ' ')
    cleaned = cleaned.replace('&', ' และ ').replace('@', ' ที่ ')
    cleaned = cleaned.replace('%', ' เปอร์เซ็นต์ ').replace('$', ' ดอลลาร์ ')
    cleaned = cleaned.replace('€', ' ยูโร ').replace('£', ' ปอนด์ ')
    
    # STEP 5: จัดการเครื่องหมายวรรคตอน
    cleaned = cleaned.replace('...', ' ').replace('..', ' ')
    cleaned = cleaned.replace('--', ' ').replace('—', ' ').replace('–', ' ')
    cleaned = re.sub(r'([.!?])(?!\s)', r'\1 ', cleaned)
    cleaned = re.sub(r'([,;:])(?!\s)', r'\1 ', cleaned)
    
    # STEP 6: ทำความสะอาดช่องว่าง
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def number_to_thai_text(num_str):
    """แปลงตัวเลขเป็นคำไทย (รองรับ 0-99,999)"""
    try:
        num_str = num_str.replace(',', '')
        num = int(num_str)
        
        if num == 0:
            return 'ศูนย์'
        
        ones = ['', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า', 'สิบ',
                'สิบเอ็ด', 'สิบสอง', 'สิบสาม', 'สิบสี่', 'สิบห้า', 'สิบหก', 'สิบเจ็ด', 'สิบแปด', 'สิบเก้า']
        
        if 0 <= num <= 19:
            return ones[num]
        elif 20 <= num <= 99:
            tens = num // 10
            remainder = num % 10
            if tens == 2:
                return 'ยี่สิบ' + (ones[remainder] if remainder != 0 else '')
            else:
                return ones[tens] + 'สิบ' + (ones[remainder] if remainder != 0 else '')
        elif 100 <= num <= 999:
            hundreds = num // 100
            remainder = num % 100
            result = (ones[hundreds] if hundreds != 1 else '') + 'ร้อย'
            if remainder != 0:
                result += number_to_thai_text(str(remainder))
            return result
        elif 1000 <= num <= 99999:
            thousands = num // 1000
            remainder = num % 1000
            if thousands == 1:
                result = 'หนึ่งพัน'
            else:
                result = number_to_thai_text(str(thousands)) + 'พัน'
            if remainder != 0:
                result += number_to_thai_text(str(remainder))
            return result
        else:
            return num_str
    except:
        return num_str

def create_wav_file(pcm_data, channels=1, sample_rate=24000, bits_per_sample=16):
    """สร้างไฟล์ WAV จาก PCM data"""
    import struct
    
    header = bytearray(44)
    
    header[0:4] = b'RIFF'
    header[4:8] = struct.pack('<I', 36 + len(pcm_data))
    header[8:12] = b'WAVE'
    
    header[12:16] = b'fmt '
    header[16:20] = struct.pack('<I', 16)
    header[20:22] = struct.pack('<H', 1)
    header[22:24] = struct.pack('<H', channels)
    header[24:28] = struct.pack('<I', sample_rate)
    header[28:32] = struct.pack('<I', sample_rate * channels * (bits_per_sample // 8))
    header[32:34] = struct.pack('<H', channels * (bits_per_sample // 8))
    header[34:36] = struct.pack('<H', bits_per_sample)
    
    header[36:40] = b'data'
    header[40:44] = struct.pack('<I', len(pcm_data))
    
    return bytes(header) + pcm_data

def create_silent_audio():
    """สร้างไฟล์เสียงว่างสำหรับ fallback ()"""
    try:
        # สร้างไฟล์ WAV ว่าง (60 วินาที)
        silent_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        silent_audio.close()
        
        # ใช้ FFmpeg สร้างไฟล์เสียงว่าง
        ffmpeg_path = get_ffmpeg_path()
        cmd = [
            ffmpeg_path, '-f', 'lavfi', '-i', 'anullsrc=channel_layout=mono:sample_rate=44100', 
            '-t', '60', str(silent_audio.name), '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return silent_audio.name
        else:
            # ถ้า FFmpeg ไม่ได้ สร้างไฟล์ว่าง
            with open(silent_audio.name, 'wb') as f:
                f.write(b'')  # ไฟล์ว่าง
            return silent_audio.name
            
    except Exception as e:
        log_error(e, "Create Silent Audio")
        # สร้างไฟล์ว่างสุดท้าย
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.close()
        return temp_file.name

def create_image_prompts(story_script):
    """สร้าง Image Prompts จาก OpenAI ()"""
    try:
        api_manager = st.session_state.api_manager
        openai_key = api_manager.get_api_key('OPENAI_KEY')
        
        if not openai_key:
            raise APIError("ไม่พบ OpenAI API Key")
        
        prompt = f"""
        Realistic narrative script: {story_script}

        Create 8 concise realistic image prompts in English (under 200 chars each) for key events from this narrative script.

        All images must be in the SAME consistent photorealistic style: Realistic photography style with authentic details, natural lighting, and photographic composition that captures the reality and significance of real moments.

        Each prompt starts with 'Photorealistic:' and includes realistic setting, accurate details, natural lighting, realistic atmosphere, and authentic emotional tone.

        IMPORTANT: Images should match the context of the narration. If the story mentions people, they should be male to match the male narrator voice. If the story is about places, objects, or events without people, focus on those elements instead.

        Focus on creating authentic, realistic photographic visuals with accurate details, natural scenes, and compositions that convey the reality and impact of real events.

        Number each prompt 1-8. Follow narrative timeline in sequence. Max 200 chars per prompt. Maintain CONSISTENT photorealistic photography style across ALL images. Use realistic photography style with authentic details, natural lighting, and photographic composition. 

        SPECIAL EMPHASIS: All images MUST be in 9:16 VERTICAL FORMAT specifically optimized for TikTok Reels content creation.

        VERY IMPORTANT: Create inspiring, authentic realistic imagery with photorealistic quality perfect for vertical social media format. Match the visual content to what is being described in the narration.

        **Write in ENG**

        Return as JSON array:
        [
          {{"scene_number": 1, "image_prompt": "Realistic Image Prompt 1"}},
          {{"scene_number": 2, "image_prompt": "Realistic Image Prompt 2"}}
        ]
        """
        
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'คุณเป็นผู้เชี่ยวชาญด้านการสร้าง AI Image Prompts'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 800,
            'temperature': 0.7
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions',
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            try:
                # ลอง parse JSON ก่อน
                prompts = json.loads(content)
                if isinstance(prompts, list):
                    return prompts
            except:
                pass
            
            # ถ้า JSON ไม่ได้ ให้แยกแบบเดิม
            lines = content.split('\n')
            prompts = []
            
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    prompt_text = re.sub(r'^\d+\.\s*', '', line)
                    if prompt_text:
                        prompts.append({"scene_number": len(prompts) + 1, "image_prompt": prompt_text})
            
            # ถ้าได้น้อยกว่า 8 ให้เพิ่ม
            while len(prompts) < 8:
                prompts.append({
                    "scene_number": len(prompts) + 1,
                    "image_prompt": f"Photorealistic: Realistic scene {len(prompts) + 1} matching narration context, natural lighting, authentic details, photographic composition, 9:16 vertical format"
                })
            
            return prompts[:8]  # เอาแค่ 8 อันแรก
        else:
            raise APIError(f"OpenAI API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        log_error(e, "OpenAI Image Prompts")
        raise e

def generate_images_with_fal(image_prompts, progress_callback=None):
    """สร้างรูปภาพด้วย FAL AI ()"""
    try:
        api_manager = st.session_state.api_manager
        fal_key = api_manager.get_api_key('FAL_AI_KEY')
        
        if not fal_key:
            raise APIError("ไม่พบ FAL AI API Key")
        
        headers = {
            'Authorization': f'Key {fal_key}',
            'Content-Type': 'application/json'
        }
        
        image_files = [None] * len(image_prompts)
        completed_count = 0
        failed_count = 0
        rate_limit_hit = False
        
        def generate_single_image(i, prompt_data):
            nonlocal completed_count, failed_count, rate_limit_hit
            max_api_retries = 3
            
            for api_retry in range(max_api_retries):
                try:
                    if progress_callback:
                        progress_callback(f"🎨 สร้างรูป {i+1}/{len(image_prompts)} (ลองครั้งที่ {api_retry + 1})")
                    
                    data = {
                        "prompt": prompt_data["image_prompt"],
                        "image_size": "portrait_16_9"
                    }
                    
                    # ส่งคำขอสร้างรูป (ใช้ FAL.ai API ที่ถูกต้อง)
                    response = requests.post(
                        "https://fal.run/fal-ai/flux/schnell",
                        headers=headers, json=data, timeout=30
                    )
                    
                    # ตรวจสอบ Rate Limiting
                    if response.status_code == 429:  # Too Many Requests
                        rate_limit_hit = True
                        wait_time = int(response.headers.get('Retry-After', 60))
                        if progress_callback:
                            progress_callback(f"⏳ Rate Limit! รอ {wait_time} วินาที...")
                        time.sleep(wait_time)
                        continue
                    elif response.status_code == 403:  # Forbidden (Quota exceeded)
                        if progress_callback:
                            progress_callback(f"❌ Quota หมด! รูป {i+1}")
                        break
                    
                    response.raise_for_status()
                    
                    # FAL.ai FLUX Schnell ให้ผลลัพธ์ทันที ไม่ต้องรอ queue
                    try:
                        result_data = response.json()
                    except json.JSONDecodeError as e:
                        log_error(e, f"FAL AI Direct Response JSON Parse - Image {i+1}", response.text)
                        raise e
                    
                    if "images" in result_data and result_data["images"]:
                        image_url = result_data["images"][0]["url"]
                        
                        # ดาวน์โหลดรูปภาพ
                        img_response = requests.get(image_url, timeout=15)
                        img_response.raise_for_status()
                        
                        # บันทึกภาพ
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        temp_file.write(img_response.content)
                        temp_file.close()
                        
                        image_files[i] = temp_file.name
                        completed_count += 1
                        if progress_callback:
                            progress_callback(f"✅ รูป {i+1} เสร็จสิ้น ({completed_count}/{len(image_prompts)})")
                        return
                    
                    # หากมาถึงตรงนี้ = สำเร็จ
                    break
                    
                except requests.exceptions.RequestException as e:
                    if "429" in str(e) or "Too Many Requests" in str(e):
                        rate_limit_hit = True
                        if progress_callback:
                            progress_callback(f"⏳ Rate Limit! รูป {i+1} รอ 30 วินาที...")
                        time.sleep(30)
                        continue
                    elif api_retry == max_api_retries - 1:
                        raise e
                    else:
                        if progress_callback:
                            progress_callback(f"⚠️ Network Error รูป {i+1}: {str(e)[:30]}")
                        time.sleep(5)  # รอ 5 วินาทีก่อนลองใหม่
                        continue
                        
            # หากมาถึงตรงนี้ = ล้มเหลวทั้งหมด
            failed_count += 1
            if progress_callback:
                progress_callback(f"❌ รูป {i+1} ล้มเหลวทั้งหมด ({failed_count} รูปที่ล้มเหลว)")
            # สร้างรูปภาพ placeholder
            placeholder_file = create_placeholder_image(f"Realistic Scene {i+1}")
            image_files[i] = placeholder_file
            completed_count += 1
        
        # สร้างรูปภาพแบบลำดับ (sequential) - แก้ไข Streamlit threading issue
        if progress_callback:
            progress_callback(f"🚀 เริ่มสร้างรูปภาพ {len(image_prompts)} รูป")
        
        # สร้างรูปภาพทีละรูป
        for i, prompt_data in enumerate(image_prompts):
            generate_single_image(i, prompt_data)
        
        # กรอง None values ออก
        final_image_files = [f for f in image_files if f is not None]
        
        # สรุปผลลัพธ์
        success_count = len([f for f in final_image_files if "placeholder" not in f])
        placeholder_count = len(final_image_files) - success_count
        
        if rate_limit_hit:
            if progress_callback:
                progress_callback(f"⚠️ เกิด Rate Limiting - บางรูปอาจใช้ Placeholder")
        
        if progress_callback:
            progress_callback(f"🎨 สร้างรูปภาพเสร็จสิ้น: {success_count} รูปจริง, {placeholder_count} รูป placeholder")
        return final_image_files
        
    except Exception as e:
        log_error(e, "FAL AI Image Generation")
        raise e

def create_placeholder_image(text):
    """สร้างรูปภาพ placeholder ()"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1080, 1920), color='darkblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # วัดขนาดข้อความ
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1080 - text_width) // 2
        y = (1920 - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='white')
        
        # บันทึกเป็นไฟล์ชั่วคราว
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        log_error(e, "Create Placeholder Image")
        # สร้างไฟล์ว่างถ้าไม่ได้
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        return temp_file.name

def create_video_with_ffmpeg(image_files, audio_file, title):
    """สร้างวิดีโอด้วย FFmpeg ()"""
    try:
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            raise APIError("ไม่พบ FFmpeg ในระบบ")
        
        if not image_files:
            raise APIError("ไม่มีรูปภาพสำหรับสร้างวิดีโอ")
        
        # สร้างไฟล์รายการรูปภาพ
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            image_list_file = f.name
            for img_file in image_files:
                img_path = str(Path(img_file).resolve()).replace('\\', '/')
                f.write(f"file '{img_path}'\n")
                f.write("duration 5\n")
            if image_files:
                img_path = str(Path(image_files[-1]).resolve()).replace('\\', '/')
                f.write(f"file '{img_path}'\n")
        
        # ไฟล์วิดีโอชั่วคราว
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.close()
        
        # สร้างวิดีโอจากรูปภาพ
        cmd1 = [
            ffmpeg_path, "-f", "concat", "-safe", "0", "-i", image_list_file,
            "-vf", "scale=8000:-1,zoompan=z='zoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1080x1920:fps=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "25",
            temp_video.name, "-y"
        ]
        
        result1 = subprocess.run(cmd1, capture_output=True, text=True)
        
        if result1.returncode != 0:
            raise APIError(f"ไม่สามารถสร้างวิดีโอได้: {result1.stderr}")
        
        # รวมเสียงกับวิดีโอ
        safe_title = sanitize_filename(title)
        final_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        final_video.close()
        
        cmd2 = [
            ffmpeg_path, "-i", temp_video.name, "-i", audio_file,
            "-c:v", "libx264", "-c:a", "aac", 
            "-movflags", "+faststart",  # เพิ่มเพื่อให้เล่นใน web ได้ดีขึ้น
            "-pix_fmt", "yuv420p",      # เพิ่มความเข้ากันได้
            "-shortest",
            final_video.name, "-y"
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        
        if result2.returncode != 0:
            raise APIError(f"ไม่สามารถรวมเสียงได้: {result2.stderr}")
        
        # ลบไฟล์ชั่วคราว
        try:
            os.unlink(image_list_file)
            os.unlink(temp_video.name)
        except:
            pass
        
        return final_video.name
        
    except Exception as e:
        log_error(e, "FFmpeg Video Creation")
        raise e

# Initialize session states ()
if 'video_generated' not in st.session_state:
    st.session_state['video_generated'] = False
if 'video_path' not in st.session_state:
    st.session_state['video_path'] = None
if 'generation_in_progress' not in st.session_state:
    st.session_state['generation_in_progress'] = False
if 'show_settings' not in st.session_state:
    st.session_state['show_settings'] = False
if 'current_topic' not in st.session_state:
    st.session_state['current_topic'] = ""

# Settings Dialog Function ()
def show_settings_dialog():
    """แสดงหน้าจอการตั้งค่า API Keys """
    
    st.markdown('<div class="settings-title">🔑 การตั้งค่า API Keys</div>', unsafe_allow_html=True)
    
    api_manager = st.session_state.api_manager
    current_keys = api_manager.get_all_api_keys()
    
    # OpenAI API Key
    st.markdown('<div class="api-key-label">🤖 OpenAI API Key:</div>', unsafe_allow_html=True)
    openai_key = st.text_input(
        "OpenAI API Key",
        value=current_keys.get('OPENAI_KEY', ''),
        type="password",
        placeholder="sk-...",
        key="settings_openai_key",
        label_visibility="collapsed"
    )
    
    # Google TTS API Key
    st.markdown('<div class="api-key-label">🗣️ Google TTS API Key:</div>', unsafe_allow_html=True)
    google_tts_key = st.text_input(
        "Google TTS API Key",
        value=current_keys.get('GOOGLE_TTS_KEY', ''),
        type="password",
        placeholder="Your Google TTS API Key",
        key="settings_google_tts_key",
        label_visibility="collapsed"
    )
    
    # FAL AI API Key
    st.markdown('<div class="api-key-label">🎨 FAL AI API Key:</div>', unsafe_allow_html=True)
    fal_key = st.text_input(
        "FAL AI API Key",
        value=current_keys.get('FAL_AI_KEY', ''),
        type="password", 
        placeholder="Your FAL AI API Key",
        key="settings_fal_key",
        label_visibility="collapsed"
    )
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="settings-button">', unsafe_allow_html=True)
        if st.button("💾 บันทึก", use_container_width=True):
            api_manager.save_all_api_keys({
                'OPENAI_KEY': openai_key,
                'GOOGLE_TTS_KEY': google_tts_key,
                'FAL_AI_KEY': fal_key
            })
            st.success("✅ บันทึก API Keys เรียบร้อยแล้ว!")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="settings-button">', unsafe_allow_html=True)
        if st.button("🗑️ ล้าง", use_container_width=True):
            api_manager.save_all_api_keys({
                'OPENAI_KEY': '',
                'GOOGLE_TTS_KEY': '',
                'FAL_AI_KEY': ''
            })
            st.warning("⚠️ ล้าง API Keys แล้ว")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="settings-button">', unsafe_allow_html=True)
        if st.button("❌ ปิด", use_container_width=True):
            st.session_state['show_settings'] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# Main Application ()
def main():
    # Header ()
    st.markdown('<div class="main-title">🎬 CREATE SHORT 60S</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">สร้างวิดีโอสมจริงแบบอัตโนมัติ (Streamlit Web Version)</div><hr />', unsafe_allow_html=True)
    
    # Settings Dialog
    if st.session_state.get('show_settings', False):
        show_settings_dialog()
        return
    
    
    
    # Topic input
    st.markdown('<div class="section-label">หัวข้อที่ต้องการสร้างวิดีโอ:</div>', unsafe_allow_html=True)
    topic = st.text_area(
        "หัวข้อ",
        value=st.session_state.get('current_topic', ''),
        height=100,
        placeholder="พิมพ์หัวข้อที่ต้องการสร้างวิดีโอ...",
        key="topic_input",
        label_visibility="collapsed"
    )
    st.session_state['current_topic'] = topic
    
    # Template selection row
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("⚙️ ตั้งค่า", use_container_width=True):
            st.session_state['show_settings'] = True
            st.rerun()
    
    with col2:
        template_manager = st.session_state.template_manager
        template_list = template_manager.get_template_list()
        template_names = [name for _, name in template_list]
        template_ids = [id for id, _ in template_list]
        
        selected_index = st.selectbox(
            "เทมเพลต",
            range(len(template_names)),
            format_func=lambda x: template_names[x],
            key="template_select",
            label_visibility="collapsed"
        )
        selected_template = template_ids[selected_index]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Button ()
    st.markdown('<div class="primary-button">', unsafe_allow_html=True)
    generate_clicked = st.button("🚀 สร้างวิดีโอ", use_container_width=True, disabled=st.session_state.get('generation_in_progress', False))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Video Generation Process
    if generate_clicked and not st.session_state.get('generation_in_progress', False):
        if not topic.strip():
            st.error("❌ กรุณากรอกหัวข้อที่ต้องการสร้างวิดีโอ")
        else:
            is_valid, missing_keys = validate_api_keys()
            if not is_valid:
                st.error(f"❌ กรุณาตั้งค่า API Keys ที่ขาดหาย: {', '.join(missing_keys)}")
                st.info("💡 กด 'ตั้งค่า' เพื่อใส่ API Keys")
            else:
                # Start generation
                st.session_state['generation_in_progress'] = True
                st.session_state['video_generated'] = False
                
                # Progress container ()
                st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                progress_info = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # แสดงข้อมูลเริ่มต้น ()
                progress_info.info(f"🚀 เริ่มสร้างวิดีโอด้วยเทมเพลต: {selected_template}")
                progress_info.info(f"⏱️ ความยาวเป้าหมาย: 60 วินาที (115-125 โทเคน)")
                
                try:
                    # Step 1: สร้างสคริปต์เรื่องเล่า (0-20%)
                    status_text.markdown('<div class="status-text">🤖 กำลังสร้างเนื้อหา...</div>', unsafe_allow_html=True)
                    progress_info.info(f"📝 หัวข้อ: {topic}")
                    progress_bar.progress(10)
                    
                    story_script = create_story_script(topic, selected_template)
                    progress_info.success("📖 สร้างสคริปต์เรื่องเล่าเสร็จสิ้น")
                    progress_bar.progress(20)
                    
                    # Step 2: สร้าง Title & Description (20-30%)
                    status_text.markdown('<div class="status-text">🏷️ กำลังสร้าง Title และ Description...</div>', unsafe_allow_html=True)
                    
                    title_desc = create_title_description(story_script)
                    progress_info.success("🏷️ สร้าง Title และ Description เสร็จสิ้น")
                    progress_bar.progress(30)
                    
                    # Step 3: สร้างเสียง (30-40%)
                    status_text.markdown('<div class="status-text">🎙️ กำลังสร้างเสียงพากย์...</div>', unsafe_allow_html=True)
                    
                    audio_file = generate_audio(story_script)
                    google_tts_key = st.session_state.api_manager.get_api_key('GOOGLE_TTS_KEY')
                    if not google_tts_key or "silent" in audio_file or not os.path.getsize(audio_file):
                        progress_info.warning("⚠️ ใช้ไฟล์เสียงว่าง (Google TTS ไม่พร้อมใช้งาน)")
                    else:
                        progress_info.success("🎵 สร้างเสียงพากย์เสร็จสิ้น")
                    progress_bar.progress(40)
                    
                    # Step 4: สร้าง Image Prompts (40-50%)
                    status_text.markdown('<div class="status-text">🎨 กำลังสร้าง Image Prompts...</div>', unsafe_allow_html=True)
                    
                    image_prompts = create_image_prompts(story_script)
                    progress_info.success("💡 สร้าง Image Prompts เสร็จสิ้น")
                    progress_bar.progress(50)
                    
                    # Step 5: สร้างรูปภาพ (50-80%)
                    status_text.markdown('<div class="status-text">🖼️ กำลังสร้างรูปภาพ...</div>', unsafe_allow_html=True)
                    
                    image_progress = st.empty()
                    
                    def update_image_progress(message):
                        image_progress.info(message)
                        # อัพเดต progress bar ตามจำนวนรูปที่เสร็จ
                        if "เสร็จสิ้น" in message:
                            try:
                                completed = int(message.split('(')[1].split('/')[0])
                                total = int(message.split('/')[1].split(')')[0])
                                progress = 50 + (completed / total) * 30  # 50-80%
                                progress_bar.progress(int(progress))
                            except:
                                pass
                    
                    image_files = generate_images_with_fal(image_prompts, update_image_progress)
                    progress_info.success("🎨 สร้างรูปภาพเสร็จสิ้น")
                    progress_bar.progress(80)
                    
                    # Step 6: สร้างวิดีโอ (80-100%)
                    status_text.markdown('<div class="status-text">🎬 กำลังสร้างวิดีโอ...</div>', unsafe_allow_html=True)
                    
                    title = title_desc.get('title', topic)
                    video_file = create_video_with_ffmpeg(image_files, audio_file, title)
                    
                    progress_bar.progress(100)
                    status_text.markdown('<div class="status-text">✅ สร้างวิดีโอเสร็จสิ้น!</div>', unsafe_allow_html=True)
                    progress_info.success("🎬 วิดีโอพร้อมใช้งาน!")
                    
                    # Save to session
                    st.session_state['video_generated'] = True
                    st.session_state['video_path'] = video_file
                    st.session_state['video_title'] = title
                    st.session_state['video_description'] = title_desc.get('description', '')
                    st.session_state['video_script'] = story_script
                    st.session_state['generation_in_progress'] = False
                    
                    # Clean up temp files
                    try:
                        if audio_file and os.path.exists(audio_file):
                            # Don't delete silent audio files immediately
                            if "silent" not in audio_file and os.path.getsize(audio_file) > 0:
                                os.unlink(audio_file)
                        for img_file in image_files:
                            if img_file and os.path.exists(img_file):
                                os.unlink(img_file)
                    except:
                        pass
                    
                    # ไม่ต้อง rerun เพื่อป้องกันลูปไม่สิ้นสุด
                    time.sleep(1)
                    
                except Exception as e:
                    progress_bar.progress(0)
                    error_message = get_user_friendly_error(e, "การสร้างวิดีโอ")
                    status_text.error(f"❌ เกิดข้อผิดพลาด: {error_message}")
                    progress_info.error(f"รายละเอียด: {str(e)[:100]}")
                    st.session_state['generation_in_progress'] = False
    
    # Output Section ()
    if st.session_state.get('video_generated', False) and st.session_state.get('video_path'):
        st.markdown('<div class="output-section">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #059669; font-weight: 700; font-size: 24px; margin-bottom: 20px; text-shadow: 0 2px 4px rgba(5, 150, 105, 0.2);">🎬 วิดีโอที่สร้างเสร็จแล้ว</h2>', unsafe_allow_html=True)
        
        # Video display
        video_path = st.session_state['video_path']
        if os.path.exists(video_path):
            st.success("✅ วิดีโอพร้อมใช้งาน!")
            
            # แสดงวิดีโอแบบหลายรูปแบบเพื่อแก้ปัญหาการเล่น
            try:
                # วิธีที่ 1: ใช้ st.video ปกติ
                st.video(video_path)
            except Exception as e:
                st.warning("⚠️ ไม่สามารถเล่นวิดีโอในเบราว์เซอร์ได้")
                
                # วิธีที่ 2: แสดงเป็น HTML video tag
                try:
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    
                    # เปลี่ยนเป็น base64 สำหรับแสดงใน HTML
                    import base64
                    video_base64 = base64.b64encode(video_bytes).decode()
                    
                    video_html = f"""
                    <video width="100%" controls>
                        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                        เบราว์เซอร์ของคุณไม่รองรับการเล่นวิดีโอ
                    </video>
                    """
                    st.markdown(video_html, unsafe_allow_html=True)
                except Exception as e2:
                    st.error(f"❌ ไม่สามารถแสดงวิดีโอได้: {str(e2)}")
                    st.info("💡 กรุณาดาวน์โหลดไฟล์เพื่อดูวิดีโอ")
            
            # Video info
            st.markdown(f"**🏷️ ชื่อ:** {st.session_state.get('video_title', 'ไม่มีชื่อ')}")
            st.markdown(f"**📄 คำอธิบาย:** {st.session_state.get('video_description', 'ไม่มีคำอธิบาย')}")
            
            # File info
            try:
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                st.markdown(f"**📊 ขนาดไฟล์:** {file_size:.1f} MB")
            except:
                pass
            
            # Download button
            with open(video_path, 'rb') as file:
                video_data = file.read()
                safe_filename = sanitize_filename(st.session_state.get('video_title', 'video')) + '.mp4'
                
                st.download_button(
                    label="💾 ดาวน์โหลดวิดีโอ",
                    data=video_data,
                    file_name=safe_filename,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # Script display
            if st.session_state.get('video_script'):
                with st.expander("📄 ดูเนื้อหาสคริปต์"):
                    st.text_area(
                        "สคริปต์:",
                        st.session_state['video_script'],
                        height=150,
                        disabled=True,
                        label_visibility="collapsed"
                    )
            
            # Action buttons
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🆕 สร้างวิดีโอใหม่", use_container_width=True):
                    # Clean up old video
                    try:
                        if os.path.exists(video_path):
                            os.unlink(video_path)
                    except:
                        pass
                    
                    st.session_state['video_generated'] = False
                    st.session_state['video_path'] = None
                    st.session_state['current_topic'] = ""
            
            with col2:
                if st.button("🗑️ ลบวิดีโอ", use_container_width=True):
                    # Clean up
                    try:
                        if os.path.exists(video_path):
                            os.unlink(video_path)
                    except:
                        pass
                    
                    st.session_state['video_generated'] = False
                    st.session_state['video_path'] = None
                    st.success("🗑️ ลบวิดีโอแล้ว")
        else:
            st.error(f"❌ ไม่พบไฟล์วิดีโอ: {video_path}")
            st.session_state['video_generated'] = False
            st.session_state['video_path'] = None
                    
        st.markdown('</div>', unsafe_allow_html=True)
    
    # System Status Panel - จัดเรียงใหม่ให้สวยงาม
    if not st.session_state.get('show_settings', False):
        st.markdown("---")
        st.markdown('<h3 style="color: #374151; font-weight: 700; font-size: 20px; margin-bottom: 16px; text-shadow: 0 1px 3px rgba(0,0,0,0.1);">📊 สถานะระบบ</h3>', unsafe_allow_html=True)
        
        # แถวที่ 1: API Keys Status (3 คอลัมน์)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Main API Keys Check
            is_valid, missing_keys = validate_api_keys()
            if is_valid:
                st.success("✅ API Keys พร้อมใช้งาน")
            else:
                st.warning("⚠️ ขาด API Keys")
        
        with col2:
            # Google TTS Status
            google_tts_key = st.session_state.api_manager.get_api_key('GOOGLE_TTS_KEY')
            if google_tts_key:
                st.success("✅ Google TTS: พร้อมใช้งาน")
            else:
                st.info("💡 Google TTS: ไม่บังคับ")
        
        with col3:
            # FFmpeg Status
            try:
                ffmpeg_path = get_ffmpeg_path()
                ffmpeg_exists = ffmpeg_path is not None
                if ffmpeg_exists:
                    st.success("✅ พบ FFmpeg")
                else:
                    st.error("❌ ไม่พบ FFmpeg")
            except:
                ffmpeg_exists = False
                st.error("❌ ไม่พบ FFmpeg")
        
        # แถวที่ 2: System Resources (2 คอลัมน์)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Memory Usage
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                st.info(f"💾 หน่วยความจำ: {memory_mb:.1f} MB")
            except:
                st.info("💾 ระบบทำงานปกติ")
        
        with col2:
            # Overall System Status
            if is_valid and ffmpeg_exists:
                st.success("🚀 ระบบพร้อมสร้างวิดีโอ")
            else:
                st.warning("⚠️ ระบบยังไม่พร้อม")
        
        # Missing Keys Detail (แสดงเฉพาะเมื่อมี key ขาด)
        if not is_valid:
            st.warning(f"🔑 กรุณาตั้งค่า API Keys ที่ขาดหาย: {', '.join(missing_keys)}")

if __name__ == "__main__":
    main()