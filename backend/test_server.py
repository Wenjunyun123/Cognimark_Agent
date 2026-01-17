#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 设置编码
import locale
locale.setlocale(locale.LC_ALL, '')

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing module imports...")
    import uvicorn
    from fastapi import FastAPI
    print("[OK] Basic modules imported successfully")
    
    print("Testing project modules...")
    from llm_service import DeepSeekLLM
    from data_model import default_store
    from agents import ProductSelectionAgent, MarketingCopyAgent
    print("[OK] Project modules imported successfully")
    
    print("Creating API application...")
    from api import app
    print("[OK] API application created successfully")
    
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()