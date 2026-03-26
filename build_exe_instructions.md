# Build a Windows .exe for Business KPI Dashboard

## 1) Open terminal in the project folder

```bash
cd path\to\business-kpi-dashboard
```

## 2) Optional virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3) Install PyInstaller

```bash
pip install pyinstaller
```

## 4) Build the .exe

```bash
pyinstaller --onefile --windowed --name BusinessKPIDashboard --icon app_icon.ico dashboard.py
```

## 5) Finished executable

```bash
dist\BusinessKPIDashboard.exe
```
