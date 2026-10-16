# VoicePath — Tamil + English MVP v5 fixes

This version fixes three issues:

1. **Full language consistency:** Tamil mode localizes dynamic opportunity titles, skills, districts, provider/type labels, reasons, descriptions, eligibility and NSQF text. English mode stays English.
2. **Live transcription:** speech recognition now shows interim words while the person is speaking. Final words are preserved when Stop is pressed.
3. **Experience in words:** detects English, Tamil and Tanglish number words such as `two years`, `two years of experience`, `இரண்டு வருடங்களாக`, `இரண்டு வருஷமா`, `ரெண்டு வருஷமா`, `rendu varushama`, plus numeric forms.

## Run on Windows

```powershell
cd "VoicePath_Tamil_English_MVP_v4"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open:

`http://127.0.0.1:8001`

Port 8001 is intentional so the older VoicePath server on port 8000 does not open the wrong project.

## Demo data

`data/opportunities.csv` is demo data only. Replace it with verified official/district data before deployment.
