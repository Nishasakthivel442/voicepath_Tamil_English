from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import csv, re, uuid
import edge_tts

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "opportunities.csv"
AUDIO = BASE / "audio"
AUDIO.mkdir(exist_ok=True)
app = FastAPI(title="VoicePath")

PATTERNS = {
"Two-wheeler repair":["bike","motorcycle","two wheeler","two-wheeler","bike repair","bike mechanic","பைக்","பைக்க","பைக் வேலை","மோட்டார் சைக்கிள்","வண்டி வேலை","bike velai","mechanic velai","vandi velai","bike service","bike repair panuven","vandi repair","two wheeler mechanic"],
"Engine servicing":["engine","engine service","engine servicing","servicing","சர்வீஸ்","சர்வீசிங்","இன்ஜின்","எஞ்சின்","என்ஜின் சர்வீஸ்","engine velai","engine work","engine repair","engine mechanic","engine service panuven"],
"Automotive electrical repair":["electrical","electric problem","electrical problem","wiring","battery","எலக்ட்ரிக்கல்","எலக்ட்ரிக்","கரண்ட் பிராப்ளம்","வயரிங்","பேட்டரி","wiring velai","electrical velai","battery problem","current problem","wiring repair","electrical work"],
"Tyre maintenance":["tyre","tire","tyres","tires","puncture","டயர்","பஞ்சர்","tyre change","tire change","tyre velai","puncture velai","puncture otthuven","tyre mathuven","puncture shop"],
"Welding":["welding","welder","வெல்டிங்","வெல்டர்","welding velai","welding work","welding panuven","welder velai"],
"Metal fabrication":["metal fabrication","fabrication","metal work","இரும்பு வேலை","மெட்டல் வேலை","irumbu velai","metal velai","fabrication work","fabrication velai"],
"Agricultural work":["agriculture","farming","farmer","farm work","விவசாயம்","விவசாய வேலை","வயல் வேலை","vivasayam","vivasaya velai","vayal velai","vivasayi","farming work"],
"Tractor operation":["tractor","tractor driving","டிராக்டர்","டிராக்டர் ஓட்ட","tractor ottuven","tractor driver","tractor running","tractor velai"],
"Irrigation":["irrigation","water pump","watering","பாசனம்","தண்ணீர் பாய்ச்ச","மோட்டார் பம்ப்","motor pump","thanni paachuven","thanni viduven","motor velai","irrigation work","paasanam"],
"Tailoring":["tailoring","tailor","stitching","stitch","dress making","sewing","தையல்","தையல் வேலை","தையற்காரர்","சட்டை தைப்ப","பேன்ட் தைப்ப","துணி தைப்ப","thayal","thaiyal","thuni thaippen","tailor velai","stitching work","dress thaippen","tailoring work","thayyal velai"],
"Beautician":["beautician","beauty parlour","beauty parlor","facial","அழகு கலை","பியூட்டி பார்லர்","பியூட்டி பார்லரில்","பியூட்டிஷியன்","beauty parlour velai","beautician work","facial panuven","makeup panuven","makeup artist"],
"Hairdressing":["hair cutting","hairdresser","hair dressing","barber","hair cut","முடி வெட்ட","முடி வெட்டுதல்","முடி திருத்த","சலூன்","mudi vettuven","hair cut panuven","saloon velai","barber velai","mudi thirutthuven","salon work"],
"Beauty & salon services":["salon","salon services","beauty salon","சலூன் வேலை","salon work","saloon","saloon service","beauty salon velai"],
"Cooking / Catering":["cooking","cook","catering","food preparation","சமையல்","சமையல் வேலை","கேட்டரிங்","கேட்டரிங் வேலை","சமைக்கிறேன்","samayal","samayal velai","cook panuven","samaipen","catering velai","food preparation work","cooking work"],
"Housekeeping":["housekeeping","house cleaning","cleaning","cleaner","வீட்டு வேலை","வீடு சுத்தம்","சுத்தம் செய்ய","veetu velai","house cleaning work","sutham seiven","cleaning velai","cleaning work","housekeeper"],
"Masonry":["masonry","mason","brick work","construction","கொத்தனார்","கொத்தனார் வேலை","செங்கல் வேலை","கட்டிட வேலை","kothanar","kothanar velai","katida velai","building velai","chengal velai","construction work","kothanaar"],
"Embroidery":["embroidery","embroider","எம்பிராய்டரி","ஜரி வேலை","embroidery work","embroidery velai","jari velai","aari work","aari velai"],
"Handicrafts":["handicraft","handicrafts","hand craft","craft work","கைவினை","கைவினை பொருட்கள்","கைவினை வேலை","kaivinai","kaivinai velai","craft velai","handicraft work"],
"Laundry":["laundry","washing clothes","ironing clothes","washerman","துணி துவைக்க","சலவை","துணி இஸ்திரி","salavai","thuni thuvaipen","ironing panuven","laundry work","laundry velai","thuni istri","istri panuven"],
"Mobile phone repair":["mobile repair","phone repair","mobile servicing","phone servicing","மொபைல் ரிப்பேர்","மொபைல் சர்வீஸ்","போன் ரிப்பேர்","போன் சர்வீஸ்","செல்போன் ரிப்பேர்","mobile velai","phone velai","cellphone repair","mobile mechanic","phone service panuven","mobile repair work"],
"Computer / Data Entry":["computer","data entry","typing","computer work","ms office","excel","கம்ப்யூட்டர்","கணினி","டேட்டா என்ட்ரி","டைப்பிங்","computer velai","data entry work","typing work","typing velai","system velai","data entry panuven","ms office velai"],
"Carpentry":["carpentry","carpenter","wood work","furniture","தச்சு","தச்சு வேலை","மர வேலை","thachu velai","mara velai","carpenter work","furniture velai","wood work panuven","carpenter velai"],
"Plumbing":["plumbing","plumber","pipe fitting","pipe work","பிளம்பிங்","பிளம்பர்","குழாய் வேலை","plumber velai","pipe velai","plumbing work","kuzhai velai","plumbing panuven"],
"Electrical installation":["electrician","electrical installation","electrical work","wiring work","எலக்ட்ரீஷியன்","எலக்ட்ரிஷியன்","மின்சார வேலை","வயரிங் வேலை","electrician velai","current velai","wiring velai","electrical maintenance"]
}

NUM = {
"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,
"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,
"ஒரு":1,"ஓரு":1,"ஒன்று":1,"இரண்டு":2,"ரெண்டு":2,"ரெண்ட":2,"மூன்று":3,"மூணு":3,"மூனு":3,"நான்கு":4,"நாலு":4,"ஐந்து":5,"அஞ்சு":5,"ஆறு":6,"ஏழு":7,"எட்டு":8,"ஒன்பது":9,"ஒம்பது":9,"பத்து":10,
"onnu":1,"oru":1,"rendu":2,"moonnu":3,"moonu":3,"naalu":4,"nalu":4,"anju":5,"aaru":6,"ezhu":7,"ettu":8,"onbadhu":9,"ombadhu":9,"pathu":10,
"pathinonnu":11,"pannendu":12,"pathimoonu":13,"pathinaalu":14,"pathinanju":15,"pathinaaru":16,"pathinezhu":17,"pathinettu":18,"patthonbadhu":19,"irubadhu":20,
"iruvathu":20,"iruvadhu":20
}

TA_NUM = {"௦":0,"௧":1,"௨":2,"௩":3,"௪":4,"௫":5,"௬":6,"௭":7,"௮":8,"௯":9}

TA = {
"Two-wheeler repair":"இருசக்கர வாகன பழுதுபார்ப்பு","Engine servicing":"எஞ்சின் சர்வீசிங்","Automotive electrical repair":"வாகன எலக்ட்ரிக்கல் பழுதுபார்ப்பு","Tyre maintenance":"டயர் பராமரிப்பு","Welding":"வெல்டிங்","Metal fabrication":"மெட்டல் ஃபேப்ரிகேஷன்","Agricultural work":"விவசாய வேலை","Tractor operation":"டிராக்டர் இயக்கம்","Irrigation":"நீர்ப்பாசனம்","Tailoring":"தையல்","Beautician":"அழகு கலை","Hairdressing":"முடி திருத்தம்","Beauty & salon services":"அழகு நிலைய சேவைகள்","Cooking / Catering":"சமையல் / கேட்டரிங்","Housekeeping":"வீட்டு பராமரிப்பு","Masonry":"கட்டிட வேலை","Embroidery":"எம்பிராய்டரி","Handicrafts":"கைவினை","Laundry":"சலவை","Mobile phone repair":"மொபைல் போன் பழுதுபார்ப்பு","Computer / Data Entry":"கணினி / டேட்டா என்ட்ரி","Carpentry":"தச்சு வேலை","Plumbing":"பிளம்பிங்","Electrical installation":"மின்சார நிறுவல்",
"Two-Wheeler Mechanic":"இருசக்கர வாகன மெக்கானிக்","Tailor":"தையல்காரர்","Beautician / Salon Worker":"அழகு நிலைய பணியாளர்","Mobile Phone Repair Technician":"மொபைல் போன் பழுதுபார்ப்பு தொழில்நுட்ப நிபுணர்","Cook / Catering Worker":"சமையல்காரர் / கேட்டரிங் பணியாளர்","Mason":"கொத்தனார்","Welder":"வெல்டர்","Carpenter":"தச்சர்","Plumber":"பிளம்பர்","Electrician":"எலக்ட்ரீஷியன்","Computer / Data Entry Operator":"கணினி / டேட்டா என்ட்ரி ஆபரேட்டர்","Skilled Worker":"திறன் வாய்ந்த பணியாளர்",
"Agricultural Worker":"விவசாயப் பணியாளர்",
"Housekeeping Worker":"வீட்டு பராமரிப்பு பணியாளர்",
"Laundry Worker":"சலவை பணியாளர்",
"Handicrafts Worker":"கைவினை கலைஞர்"
}

TYPE_TA={"Skill Training":"திறன் பயிற்சி","Job Opportunity":"வேலை வாய்ப்பு","Livelihood Support":"வாழ்வாதார ஆதரவு"}
DISTRICT_TA={"Coimbatore":"கோயம்புத்தூர்","Chennai":"சென்னை","Madurai":"மதுரை","Salem":"சேலம்","Thanjavur":"தஞ்சாவூர்"}
PROVIDER_TA={"Demo Skill Centre":"டெமோ திறன் மையம்","Demo Technical Centre":"டெமோ தொழில்நுட்ப மையம்","Demo Agriculture Centre":"டெமோ வேளாண்மை மையம்","Demo Training Centre":"டெமோ பயிற்சி மையம்"}

OPP_TA={
"Automotive Service Technician Training":"ஆட்டோமொட்டிவ் சர்வீஸ் டெக்னீஷியன் பயிற்சி","Automotive Electrical Basics":"வாகன எலக்ட்ரிக்கல் அடிப்படை பயிற்சி","Tyre Service Technician":"டயர் சர்வீஸ் டெக்னீஷியன் பயிற்சி","Welder Training":"வெல்டர் பயிற்சி","Agriculture Skills Program":"விவசாய திறன் பயிற்சி","Tractor Operator Training":"டிராக்டர் ஆபரேட்டர் பயிற்சி","Tailoring and Garment Skills":"தையல் மற்றும் ஆடைத் திறன் பயிற்சி",
"Beautician Skills Program":"அழகுக்கலை திறன் பயிற்சி","Hairdressing Skills Program":"முடி திருத்தும் திறன் பயிற்சி","Cooking and Catering Skills":"சமையல் மற்றும் கேட்டரிங் திறன் பயிற்சி","Housekeeping Skills":"வீட்டு பராமரிப்புத் திறன் பயிற்சி","Masonry Skills Program":"கட்டிட வேலை திறன் பயிற்சி","Embroidery Skills":"எம்பிராய்டரி திறன் பயிற்சி","Handicrafts Enterprise Skills":"கைவினைத்தொழில் திறன் பயிற்சி","Laundry Services Skills":"சலவை சேவைகள் திறன் பயிற்சி","Mobile Phone Repair Technician":"மொபைல் போன் ரிப்பேர் டெக்னீஷியன் பயிற்சி","Computer and Data Entry Skills":"கணினி மற்றும் டேட்டா என்ட்ரி திறன் பயிற்சி","Carpentry Skills Program":"தச்சு வேலை திறன் பயிற்சி","Plumbing Skills Program":"பிளம்பிங் திறன் பயிற்சி","Electrical Installation Skills":"மின்சார நிறுவல் திறன் பயிற்சி"
}
DESC_TA={
"Hands-on two-wheeler maintenance and service training":"இருசக்கர வாகன பராமரிப்பு மற்றும் சர்வீசிங் குறித்த நடைமுறை பயிற்சி.",
"Basic vehicle electrical troubleshooting":"வாகன எலக்ட்ரிக்கல் பிரச்சினைகளை கண்டறிந்து சரிசெய்வதற்கான அடிப்படை பயிற்சி.",
"Tyre fitting puncture repair and wheel maintenance":"டயர் பொருத்துதல், பஞ்சர் சரிசெய்தல் மற்றும் சக்கர பராமரிப்பு பயிற்சி.",
"Basic welding and fabrication practice":"அடிப்படை வெல்டிங் மற்றும் ஃபேப்ரிகேஷன் நடைமுறை பயிற்சி.",
"Practical farming skills":"விவசாயப் பணிகளுக்கான நடைமுறை திறன் பயிற்சி.",
"Safe tractor operation":"பாதுகாப்பான டிராக்டர் இயக்கத்திற்கான பயிற்சி.",
"Stitching and garment making":"தையல் மற்றும் ஆடை தயாரிப்பிற்கான பயிற்சி.",
"Beauty care and grooming":"அழகு கலை மற்றும் ஒப்பனை பயிற்சி.",
"Hair cutting and salon skills":"முடி வெட்டுதல் மற்றும் சலூன் திறன்கள்.",
"Cooking and catering basics":"சமையல் மற்றும் கேட்டரிங் அடிப்படைகள்.",
"Cleaning and workplace hygiene":"சுத்தம் மற்றும் பணியிட சுகாதாரம்.",
"Brickwork and construction skills":"செங்கல் மற்றும் கட்டிட வேலை திறன்கள்.",
"Embroidery practice":"எம்பிராய்டரி நடைமுறை பயிற்சி.",
"Craft production and enterprise basics":"கைவினைப்பொருள் உற்பத்தி மற்றும் தொழில் அடிப்படைகள்.",
"Laundry and ironing skills":"சலவை மற்றும் இஸ்திரி திறன்கள்.",
"Smartphone diagnostics and repair":"ஸ்மார்ட்போன் பிரச்சினைகளை கண்டறிதல் மற்றும் பழுதுபார்த்தல்.",
"Typing spreadsheets and data entry":"டைப்பிங், எக்செல் மற்றும் டேட்டா என்ட்ரி.",
"Woodwork and furniture repair":"மர வேலைப்பாடு மற்றும் பர்னிச்சர் பழுதுபார்த்தல்.",
"Pipe fitting and plumbing":"குழாய் பொருத்துதல் மற்றும் பிளம்பிங்.",
"Wiring and electrical installation":"வயரிங் மற்றும் மின்சார நிறுவல்."
}


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[.,!?;:()\[\]{}\"']", " ", (s or "").lower())).strip()


def experience(text):
    t=norm(text)
    # Numeric forms first: 2 years, 2 yrs, 2 வருடம், 2 மாதம்
    patterns=[
        (r"(?<!\w)(\d+(?:\.\d+)?)\s*(years?|yrs?|yr)\b", "years"),
        (r"(?<!\w)(\d+(?:\.\d+)?)\s*(months?|month|mos?)\b", "months"),
        (r"(?<!\w)(\d+(?:\.\d+)?)\s*(வருடம்|வருடமா|வருடங்கள்|வருடங்களாக|வருடமாக|வருஷம்|வருஷமா|வருஷங்கள்|வருஷங்களாக|வருஷமாக|வருசம்|வருசமா|வருசங்கள்|வருசங்களாக)\b", "years"),
        (r"(?<!\w)(\d+(?:\.\d+)?)\s*(மாதம்|மாதமா|மாதங்கள்|மாதங்களாக|மாதமாக)\b", "months")
    ]
    for p,unit in patterns:
        m=re.search(p,t)
        if m:
            n=float(m.group(1))
            if unit=="months":
                mo=int(n); return {"experience_years":mo//12,"experience_months":mo%12,"experience_text":f"{mo} months","experience_confidence":.99}
            return {"experience_years":int(n) if n.is_integer() else n,"experience_months":0,"experience_text":f"{n:g} years","experience_confidence":.99}

    # Number words, including English, Tamil and Tanglish.
    tokens=sorted(NUM,key=len,reverse=True)
    for tok in tokens:
        n=NUM[tok]
        if re.search(rf"(?<![A-Za-z]){re.escape(tok)}(?![A-Za-z])\s*(years?|yrs?|yr)\b",t):
            return {"experience_years":n,"experience_months":0,"experience_text":f"{n:g} years","experience_confidence":.98}
        if re.search(rf"(?<![A-Za-z]){re.escape(tok)}(?![A-Za-z])\s*(months?|month|mos?)\b",t):
            return {"experience_years":0,"experience_months":n,"experience_text":f"{n:g} months","experience_confidence":.98}
        if tok in t:
            # Tamil/Tanglish spoken forms: இரண்டு வருடங்களாக, ரெண்டு வருஷமா, rendu varushama, etc.
            if re.search(rf"{re.escape(tok)}\s*(வருடம்|வருடமா|வருடங்கள்|வருடங்களாக|வருடமாக|வருஷம்|வருஷமா|வருஷங்கள்|வருஷங்களாக|வருஷமாக|வருசம்|வருசமா|வருசங்கள்|வருசங்களாக|வருடம்|வருஷமா)",t):
                return {"experience_years":n,"experience_months":0,"experience_text":f"{n:g} years","experience_confidence":.98}
            if re.search(rf"{re.escape(tok)}\s*(மாதம்|மாதமா|மாதங்கள்|மாதங்களாக|மாதமாக)",t):
                return {"experience_years":0,"experience_months":n,"experience_text":f"{n:g} months","experience_confidence":.98}
            if re.search(rf"{re.escape(tok)}\s*(varush|varud|varushama|varudama|years?)",t):
                return {"experience_years":n,"experience_months":0,"experience_text":f"{n:g} years","experience_confidence":.97}

    # Contextual English: "working for two years", "two years of experience".
    word_alts="|".join(re.escape(x) for x in tokens if x.isascii())
    if word_alts:
        m=re.search(rf"\b({word_alts})\b\s*(?:years?|yrs?|yr)\b",t)
        if m:
            n=NUM[m.group(1)]; return {"experience_years":n,"experience_months":0,"experience_text":f"{n:g} years","experience_confidence":.95}

    return {"experience_years":None,"experience_months":None,"experience_text":"Not mentioned","experience_confidence":0}


def skills(text):
    t=norm(text); out=[]
    for name,pats in PATTERNS.items():
        hits=[p for p in pats if norm(p) in t]
        if hits: out.append({"name":name,"confidence":round(min(.97,.72+.08*len(hits)),2),"evidence":hits[:3]})
    return out


def occupation(ss):
    n={x["name"] for x in ss}
    for skill,title in [
        ("Two-wheeler repair", "Two-Wheeler Mechanic"), ("Engine servicing", "Two-Wheeler Mechanic"),
        ("Automotive electrical repair", "Two-Wheeler Mechanic"), ("Tyre maintenance", "Two-Wheeler Mechanic"),
        ("Tailoring", "Tailor"), ("Embroidery", "Tailor"),
        ("Beautician", "Beautician / Salon Worker"), ("Beauty & salon services", "Beautician / Salon Worker"), ("Hairdressing", "Beautician / Salon Worker"),
        ("Mobile phone repair", "Mobile Phone Repair Technician"),
        ("Cooking / Catering", "Cook / Catering Worker"),
        ("Masonry", "Mason"),
        ("Welding", "Welder"), ("Metal fabrication", "Welder"),
        ("Carpentry", "Carpenter"),
        ("Plumbing", "Plumber"),
        ("Electrical installation", "Electrician"),
        ("Computer / Data Entry", "Computer / Data Entry Operator"),
        ("Agricultural work", "Agricultural Worker"), ("Tractor operation", "Agricultural Worker"), ("Irrigation", "Agricultural Worker"),
        ("Housekeeping", "Housekeeping Worker"),
        ("Laundry", "Laundry Worker"),
        ("Handicrafts", "Handicrafts Worker")
    ]:
        if skill in n:return title
    return "Skilled Worker"


def opportunities():
    if not DATA.exists(): return []
    with DATA.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def match(ss):
    names={x["name"].lower() for x in ss}; out=[]
    for r in opportunities():
        rs=norm(r["skill"]); hit=[n for n in names if n in rs or rs in n]
        if hit:
            out.append({**r,"match_score":min(98,68+12*len(hit)),"matched_skills":hit})
    return sorted(out,key=lambda x:x["match_score"],reverse=True)[:3]


def localize_opp(r,lang):
    if lang != "ta":
        r["display_title"]=r["title"]; r["display_skill"]=r["skill"]; r["display_type"]=r["type"]; r["display_district"]=r["district"]; r["display_provider"]=r["provider"]; r["display_description"]=r.get("description",""); r["display_eligibility"]="Demo eligibility - verify before use"; r["display_nsqf"]="Demo mapping - verify NSQF pathway"
    else:
        r["display_title"]=OPP_TA.get(r["title"],r["title"]); r["display_skill"]=TA.get(r["skill"],r["skill"]); r["display_type"]=TYPE_TA.get(r["type"],r["type"]); r["display_district"]=DISTRICT_TA.get(r["district"],r["district"]); r["display_provider"]=PROVIDER_TA.get(r["provider"],r["provider"]); r["display_description"]=DESC_TA.get(r.get("description", ""),r.get("description","")); r["display_eligibility"]="டெமோ தகுதி — பயன்படுத்துவதற்கு முன் சரிபார்க்கவும்"; r["display_nsqf"]="டெமோ NSQF இணைப்பு — அதிகாரப்பூர்வ பாதையை சரிபார்க்கவும்"
    return r


class Analyze(BaseModel): text:str; language:str="ta"
class TTS(BaseModel): text:str; language:str="ta"

@app.get("/")
async def home(): return FileResponse(BASE/"frontend"/"index.html")

@app.post("/api/analyze")
async def analyze(r:Analyze):
    if not r.text.strip(): raise HTTPException(400,"No speech text received.")
    e=experience(r.text); s=skills(r.text); raw=match(s)
    localized=[]
    for item in raw:
        item=localize_opp(item,r.language)
        if r.language=="ta":
            matched=[TA.get(x,x) for x in item.get("matched_skills",[])]
            item["reason"]="உங்கள் பேச்சில் " + ", ".join(matched) + " தொடர்பான அனுபவம் இருப்பதால் இந்த வாய்ப்பு பரிந்துரைக்கப்படுகிறது."
        else:
            item["reason"]="Recommended because your speech indicates " + ", ".join(item.get("matched_skills",[])) + "."
        localized.append(item)
    return {"transcript":r.text,"language":r.language,**e,"skills":s,"occupation":occupation(s),"recommendations":localized}

@app.post("/api/tts")
async def tts(r:TTS):
    if not r.text.strip(): raise HTTPException(400,"No text.")
    voice="ta-IN-PallaviNeural" if r.language=="ta" else "en-IN-NeerjaNeural"
    fn=f"{uuid.uuid4().hex}.mp3"
    try: await edge_tts.Communicate(r.text,voice).save(str(AUDIO/fn))
    except Exception as e: raise HTTPException(503,f"TTS unavailable: {e}")
    return {"audio_url":f"/audio/{fn}"}

app.mount("/audio",StaticFiles(directory=AUDIO),name="audio")
app.mount("/static",StaticFiles(directory=BASE/"frontend"),name="static")
if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="127.0.0.1",port=8001)
