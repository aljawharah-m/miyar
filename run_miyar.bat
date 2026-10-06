@echo off
cd /d %~dp0
set HF_HUB_DOWNLOAD_TIMEOUT=300
set HF_HUB_ETAG_TIMEOUT=30
python -m streamlit run app.py
