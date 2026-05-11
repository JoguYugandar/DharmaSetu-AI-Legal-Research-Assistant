@echo off
echo Installing groq and python-dotenv into Anaconda Python...
C:\ProgramData\anaconda3\python.exe -m pip install groq==0.9.0 python-dotenv==1.0.1
echo.
echo Done! Now run: streamlit run streamlit_app.py
pause
