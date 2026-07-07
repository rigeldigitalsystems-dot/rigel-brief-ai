import os, re, json, html
from io import BytesIO
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

import streamlit as st

try:
    from groq import Groq
except Exception:
    Groq = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except Exception:
    SimpleDocTemplate = None

APP_NAME = "RIGEL Brief AI"
RDS_HOME_URL = "https://rigeldigitalsystems.carrd.co/#"
ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "rds_logo.png"

st.set_page_config(page_title=APP_NAME, page_icon=str(LOGO) if LOGO.exists() else "RDS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root{--bg:#090b16;--panel:rgba(14,17,31,.74);--line:rgba(255,255,255,.13);--text:#fbf7f3;--muted:#b8afbe;--muted2:#8d8494;--purple:#9b5cff;--pink:#ff4fb8;--orange:#ff5a3c;--blue:#5da9ff;}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
.stApp{color:var(--text);background:radial-gradient(circle at 8% 8%,rgba(155,92,255,.32),transparent 25%),radial-gradient(circle at 92% 5%,rgba(255,90,60,.24),transparent 24%),radial-gradient(circle at 72% 94%,rgba(93,169,255,.15),transparent 27%),linear-gradient(135deg,#090b16 0%,#111528 46%,#090b16 100%);}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(rgba(255,255,255,.032) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:38px 38px;opacity:.52;mask-image:linear-gradient(to bottom,black,transparent 82%);z-index:0;}
.stApp:after{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 0%,rgba(0,0,0,.20) 100%);z-index:0;}
header[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding-top:1.15rem;padding-bottom:2.2rem;position:relative;z-index:1;}
.rds-navbar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:1rem;padding:.72rem .84rem;margin-bottom:.82rem;border:1px solid var(--line);background:rgba(10,12,22,.66);backdrop-filter:blur(22px);border-radius:26px;box-shadow:0 22px 70px rgba(0,0,0,.28);animation:riseIn .35s ease both;}
.rds-left{display:flex;align-items:center;gap:.78rem}.rds-wordmark{font-size:1.54rem;line-height:1;font-weight:950;letter-spacing:-.07em;color:#fffaf6;padding:.48rem .62rem;border-radius:17px;background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.045));border:1px solid rgba(255,255,255,.16)}.rds-app-title{font-size:.98rem;font-weight:850;letter-spacing:-.025em;color:#fffaf6}.rds-app-subtitle{font-size:.74rem;color:var(--muted);margin-top:.02rem}.rds-center{color:#eee5ef;font-size:.9rem;letter-spacing:.02em;opacity:.92;white-space:nowrap}.rds-right{display:flex;justify-content:flex-end}.home-button{text-decoration:none!important;color:#fff!important;border:1px solid rgba(255,255,255,.18);background:linear-gradient(135deg,rgba(155,92,255,.28),rgba(255,90,60,.18)),rgba(255,255,255,.055);padding:.66rem .9rem;border-radius:14px;font-weight:760;font-size:.86rem;transition:transform .2s ease,border-color .2s ease,background .2s ease;white-space:nowrap}.home-button:hover{transform:translateY(-1px);border-color:rgba(255,255,255,.34);background:linear-gradient(135deg,rgba(155,92,255,.36),rgba(255,90,60,.24)),rgba(255,255,255,.08)}
.compact-hero{display:grid;grid-template-columns:1fr;gap:.75rem;align-items:center;border:1px solid var(--line);background:rgba(15,18,32,.58);backdrop-filter:blur(22px);border-radius:28px;padding:1.05rem 1.16rem;margin-bottom:.88rem;box-shadow:0 20px 64px rgba(0,0,0,.23);overflow:hidden;position:relative;animation:riseIn .42s ease both}.compact-hero:after{content:"";position:absolute;right:-82px;top:-110px;width:250px;height:250px;border-radius:70px;transform:rotate(24deg);background:linear-gradient(135deg,var(--purple),var(--pink),var(--orange));opacity:.36}.compact-hero h1{position:relative;z-index:2;margin:0;max-width:900px;font-size:clamp(1.75rem,2.75vw,3.05rem);line-height:1;letter-spacing:-.058em;font-weight:920;color:#fffaf6}.compact-hero h1 span{background:linear-gradient(90deg,#fffaf6,#d8c0ff 52%,#ffb1a1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.compact-hero p{position:relative;z-index:2;margin:.52rem 0 0;max-width:900px;color:#d7cfda;font-size:.93rem;line-height:1.56}.hero-chip{position:relative;z-index:2;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);color:#f8efff;border-radius:999px;padding:.48rem .76rem;font-size:.8rem;font-weight:700;white-space:nowrap}
.ui-card{border:1px solid var(--line);background:rgba(10,12,22,.54);backdrop-filter:blur(22px);border-radius:24px;padding:.92rem;box-shadow:0 22px 70px rgba(0,0,0,.22);animation:riseIn .5s ease both}.card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:.85rem;margin-bottom:.72rem}.card-head h2{margin:0 0 .18rem;color:#fffaf6;font-size:.98rem;letter-spacing:-.02em}.card-head p{margin:0;color:var(--muted);line-height:1.45;font-size:.86rem}.step-badge{display:inline-flex;align-items:center;justify-content:center;min-width:4.75rem;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.06);color:#eee4f2;border-radius:999px;padding:.34rem .52rem;font-size:.75rem;font-weight:760}.progress-wrap{height:7px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;margin:.28rem 0 .72rem;border:1px solid rgba(255,255,255,.08)}.progress-bar{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--purple),var(--pink),var(--orange));transition:width .25s ease}.step-card,.groq-card{border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.055);border-radius:18px;padding:.82rem;margin:.68rem 0}.groq-card{border-color:rgba(155,92,255,.22);background:linear-gradient(135deg,rgba(155,92,255,.10),rgba(255,90,60,.055)),rgba(255,255,255,.05)}.step-card h3,.groq-card h3{margin:0 0 .25rem;color:#fffaf6;font-size:.95rem}.step-card p,.groq-card p{margin:0 0 .62rem;color:var(--muted);line-height:1.46;font-size:.85rem}.char-count{color:var(--muted2);text-align:right;font-size:.72rem;margin-top:-.24rem}.soft-label{color:#f1eaf7;font-size:.82rem;font-weight:720;margin:.78rem 0 .38rem}.status-box{border:1px solid rgba(255,255,255,.11);background:rgba(255,255,255,.055);border-radius:14px;padding:.66rem;color:#d8d0dc;line-height:1.45;font-size:.8rem;margin-top:.52rem}.status-ok{border-color:rgba(74,222,128,.28);background:rgba(74,222,128,.08);color:#c9fbd9}
.empty-state{min-height:330px;border-radius:20px;border:1px dashed rgba(255,255,255,.18);background:radial-gradient(circle at 50% 0%,rgba(155,92,255,.16),transparent 35%),rgba(255,255,255,.04);display:grid;place-items:center;text-align:center;padding:1.8rem;color:var(--muted)}.empty-state h3{margin:0 0 .45rem;color:#fffaf6;font-size:1rem}.empty-state p{max-width:470px;margin:0 auto;line-height:1.62;font-size:.9rem}.meta-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.55rem;margin:.75rem 0 .85rem}.meta-item{border:1px solid rgba(255,255,255,.11);background:rgba(255,255,255,.055);border-radius:15px;padding:.64rem}.meta-item span{display:block;color:var(--muted2);font-size:.68rem;margin-bottom:.14rem}.meta-item strong{color:#fffaf6;font-size:.84rem}.brief-grid{display:grid;grid-template-columns:1fr 1fr;gap:.65rem}.brief-card{border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.055);border-radius:17px;padding:.78rem;margin-bottom:.65rem;min-height:auto}.brief-card.full{grid-column:1/-1}.brief-card h3{margin:0 0 .4rem;color:#fffaf6;font-size:.9rem;letter-spacing:-.01em}.brief-card p,.brief-card li{color:#d7cfda;line-height:1.55;font-size:.86rem}.brief-card ul{margin:.35rem 0 0 1rem;padding:0}.coach-card{border:1px solid rgba(155,92,255,.28);background:linear-gradient(135deg,rgba(155,92,255,.15),rgba(255,90,60,.08)),rgba(255,255,255,.04);border-radius:18px;padding:.82rem;margin-top:.65rem}.coach-card strong{display:block;color:#fffaf6;margin-bottom:.28rem;font-size:.9rem}.coach-card p{color:#e1d8e5;line-height:1.54;margin:0 0 .65rem;font-size:.86rem}.footer{margin-top:1.8rem;padding:1rem 0 .3rem;color:#aaa1ae;text-align:center;font-size:.82rem}
div[data-baseweb="textarea"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.14)!important;border-radius:18px!important;overflow:hidden!important;box-shadow:none!important}.stTextArea textarea{min-height:205px!important;color:#fffaf6!important;background:transparent!important;border:0!important;border-radius:18px!important;line-height:1.55!important;font-size:.92rem!important;padding:.9rem!important;resize:none!important;box-shadow:none!important;outline:none!important}.stTextArea textarea:focus{border:0!important;box-shadow:none!important;background:transparent!important}div[data-baseweb="textarea"]:focus-within{border-color:rgba(192,132,252,.72)!important;box-shadow:0 0 0 4px rgba(155,92,255,.12)!important}.stTextInput input{color:#fffaf6!important;background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.14)!important;border-radius:14px!important}.stSelectbox div[data-baseweb="select"]>div{color:#fffaf6!important;background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.14)!important;border-radius:14px!important;min-height:40px}.stSelectbox label,.stTextInput label,.stTextArea label{color:#e7deeb!important;font-size:.82rem!important;font-weight:650!important}.stButton>button{border:1px solid rgba(255,255,255,.13)!important;background:rgba(255,255,255,.06)!important;color:#fffaf6!important;border-radius:14px!important;font-weight:720!important;min-height:38px;transition:transform .18s ease,border-color .18s ease,background .18s ease,filter .18s ease}.stButton>button:hover{transform:translateY(-1px);border-color:rgba(255,255,255,.28)!important;background:rgba(255,255,255,.10)!important;color:#fff!important}.stButton>button[kind="primary"]{border:0!important;background:linear-gradient(135deg,var(--purple),var(--pink) 58%,var(--orange))!important;box-shadow:0 15px 38px rgba(155,92,255,.28);color:#fff!important;min-height:42px}.stButton>button[kind="primary"]:hover{filter:brightness(1.04);transform:translateY(-2px)}.stDownloadButton>button{width:100%;border:1px solid rgba(255,255,255,.13)!important;background:rgba(255,255,255,.06)!important;color:#fffaf6!important;border-radius:12px!important;font-weight:740!important;min-height:38px;transition:transform .18s ease,border-color .18s ease,background .18s ease}.stDownloadButton>button:hover{transform:translateY(-1px);border-color:rgba(192,132,252,.50)!important;background:rgba(255,255,255,.095)!important}div[data-testid="stTabs"] button{color:#d8d0dc!important;font-weight:650!important;font-size:.86rem!important}div[data-testid="stTabs"] button[aria-selected="true"]{color:#fffaf6!important}div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:linear-gradient(90deg,var(--purple),var(--orange))!important}div[data-testid="stCaptionContainer"]{color:var(--muted2)!important}@keyframes riseIn{from{opacity:0;transform:translateY(10px) scale(.994)}to{opacity:1;transform:translateY(0) scale(1)}}@media(max-width:1050px){.rds-navbar{grid-template-columns:1fr;align-items:flex-start}.rds-center{display:none}.rds-right{justify-content:flex-start}.compact-hero{grid-template-columns:1fr}.meta-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:720px){.meta-grid,.brief-grid{grid-template-columns:1fr}.rds-left{align-items:flex-start}.rds-wordmark{font-size:1.35rem}}
</style>
""", unsafe_allow_html=True)

EXAMPLES = {
    "Ders çalışma uygulaması": "Öğrencilerin ders çalışma sürecini daha düzenli hale getiren bir web uygulaması yapmak istiyorum. Kullanıcı ders notlarını yükleyebilsin, sistem bu notlardan özet çıkarsın, kısa quizler hazırlasın ve kişiye özel çalışma planı önersin.",
    "Freelancer teklif aracı": "Freelancer çalışanların müşteri taleplerinden hızlıca teklif dokümanı hazırlamasını sağlayan bir araç. Kullanıcı hizmetini, süreyi ve fiyat aralığını yazar; sistem düzenli bir teklif metni oluşturur.",
    "Kişisel bütçe takip aracı": "Gelir ve giderleri kolayca takip eden, ay sonunda sade bir rapor veren kişisel finans uygulaması. Kullanıcılar harcamalarını kategoriye ayırabilsin ve gereksiz harcamalar için uyarı alabilsin.",
    "E-ticaret açıklama aracı": "Küçük işletmelerin ürünleri için daha düzgün açıklamalar hazırlamasına yardım eden basit bir araç. Ürün özellikleri girilir, uygulama kısa açıklama, uzun açıklama ve sosyal medya metni üretir.",
}
PROJECT_TYPES = ["Seçilmedi", "Web uygulaması", "Mobil uygulama", "SaaS", "AI aracı", "Veri analizi aracı", "Eğitim projesi", "İçerik aracı", "E-ticaret aracı", "Mühendislik aracı"]
AUDIENCES = ["Seçilmedi", "Öğrenciler", "Freelancerlar", "Küçük işletmeler", "Yazılımcılar", "Ekip yöneticileri", "İçerik üreticileri", "Mühendisler", "Genel kullanıcılar"]
DETAIL_LEVELS = ["Kısa ve net", "Dengeli", "Detaylı"]
LANGUAGES = ["Türkçe", "English"]

def h(text):
    return html.escape(str(text or ""))

def html_list(items):
    return "<ul>" + "".join(f"<li>{h(item)}</li>" for item in (items or [])) + "</ul>"

def clean_json_response(text: str) -> dict:
    if not text:
        raise ValueError("Boş model yanıtı")
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group(0)
    return json.loads(text)

def split_sentences(text: str):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p.strip()]

def infer_project_name(idea: str, project_type: str) -> str:
    lower = idea.lower()
    if "öğrenci" in lower or "ders" in lower or "çalışma" in lower: return "StudyMate"
    if "bütçe" in lower or "gider" in lower or "gelir" in lower: return "PocketPlan"
    if "freelancer" in lower or "teklif" in lower: return "OfferDesk"
    if "e-ticaret" in lower or "ürün" in lower: return "ProductNote"
    if "görev" in lower or "öncelik" in lower: return "TaskPilot"
    if project_type and project_type != "Seçilmedi": return project_type.replace(" ", "") + " One"
    return "Project One"

def build_fallback_brief(idea: str, project_type: str, audience: str, detail_level: str, language: str) -> dict:
    sentences = split_sentences(idea)
    project_name = infer_project_name(idea, project_type)
    if audience == "Seçilmedi": audience = "üründen doğrudan fayda görecek kullanıcılar"
    if project_type == "Seçilmedi": project_type = "Dijital ürün"
    first_sentence = sentences[0] if sentences else "Bu proje, kullanıcıların belirli bir ihtiyacını daha düzenli ve hızlı şekilde çözmeyi hedefleyen bir dijital üründür."
    return {
        "project_name": project_name,
        "tagline": "Fikrini daha anlaşılır bir proje planına dönüştür.",
        "summary": f"{first_sentence} İlk sürümde ürünün amacı, kullanıcının işini mümkün olduğunca kısa bir akışla çözmek olmalı. Gereksiz ayarları azaltmak, sonucu açık göstermek ve ilk denemede güven veren bir deneyim sunmak önemli.",
        "problem": "Fikir ilk anda anlaşılır görünse bile proje planına dönüştürülmediğinde kapsam, öncelik ve ilk adım belirsiz kalabiliyor.",
        "solution": "Ürün, ham fikri daha net parçalara ayırır: problem, çözüm, kullanıcı, özellikler, MVP kapsamı ve yol haritası.",
        "target_audience": [f"Bu problemi hızlıca çözmek isteyen {audience}.", "Karmaşık araçlarla uğraşmadan sonuç almak isteyen kullanıcılar.", "İlk kullanımda ürünün amacını hemen anlamak isteyen kişiler."],
        "key_features": ["Sade fikir girişi", "Otomatik proje özeti", "Hedef kitle çıkarımı", "MVP kapsamı", "Teknik gereksinim listesi", "PDF, Markdown, TXT ve README çıktısı"],
        "technical_requirements": ["Streamlit tabanlı tek sayfalık arayüz", "Python ile çıktı üretimi", "Groq API ile isteğe bağlı AI analizi", "API anahtarı yoksa yedek analiz motoru", "Unicode destekli PDF üretimi", "Genişletilebilir dosya yapısı"],
        "roadmap": [{"phase":"MVP","items":["Ana arayüzü tamamla","Brief bölümlerini üret","Export seçeneklerini test et"]},{"phase":"İlk kullanıcı testi","items":["3-5 kişiye kullandır","Anlaşılmayan alanları not al","Çıktı metinlerini sadeleştir"]},{"phase":"Sonraki sürüm","items":["Proje geçmişi ekle","Daha fazla şablon hazırla","Paylaşılabilir link üret"]}],
        "mvp_scope": ["Fikir girme alanı", "Brief üretimi", "Proje özeti", "Özellik listesi", "Teknik gereksinimler", "Yol haritası", "README taslağı", "Dosya indirme seçenekleri"],
        "risks": ["Kullanıcı fikri çok kısa yazarsa çıktı yüzeysel kalabilir.", "MVP kapsamı büyürse ürünün basitliği kaybolabilir.", "AI çıktılarının son kullanıcıya sunulmadan önce gözden geçirilmesi gerekebilir."],
        "coach_note": "Bu fikirde başlanacak en doğru yer, tüm özellikleri eklemek değil; tek bir kullanıcı için tek bir problemi çok temiz çözmek. İlk sürümde bunu başarırsan proje daha hızlı şekillenir.",
        "next_questions": ["Bu ürünü ilk kim kullanacak?", "Kullanıcı bu işi bugün hangi yöntemle çözüyor?", "İlk sürümde olmazsa olmaz tek özellik hangisi?"],
        "first_next_step": "Bugün yapılacak en iyi adım: fikri tek cümleye indirip ardından sadece MVP ekranlarını çıkarmak.",
        "ai_suggestion": "Önce küçük bir kullanıcı senaryosu yaz. Sonra her özelliği bu senaryoya hizmet edip etmediğine göre ele.",
        "difficulty": "Orta", "estimated_time": "2 - 4 hafta", "platform": "Web", "project_type": project_type,
    }

def build_system_prompt(language: str) -> str:
    if language == "English":
        return "You are a practical, attentive product coach. Write like a human teammate. Avoid hype. Return only valid JSON."
    return "Sen erken aşama yazılım projeleri için pratik ve ilgili bir ürün koçusun. Pazarlama metni, yapay zeka klişesi ve abartılı övgü kullanma. Sadece geçerli JSON döndür."

def build_user_prompt(idea, project_type, audience, detail_level, language):
    return f'''Dil: {language}\nDetay seviyesi: {detail_level}\nProje türü: {project_type}\nHedef kitle: {audience}\n\nHam fikir:\n{idea}\n\nAşağıdaki JSON şemasına birebir uy:\n{{"project_name":"Kısa proje adı","tagline":"Tek cümlelik açıklama","summary":"Doğal proje özeti","problem":"Çözülen problem","solution":"Çözüm yaklaşımı","target_audience":["madde","madde","madde"],"key_features":["madde","madde","madde","madde","madde","madde"],"technical_requirements":["madde","madde","madde","madde","madde"],"roadmap":[{{"phase":"MVP","items":["madde","madde","madde"]}},{{"phase":"İlk kullanıcı testi","items":["madde","madde"]}},{{"phase":"Sonraki sürüm","items":["madde","madde"]}}],"mvp_scope":["madde","madde","madde","madde"],"risks":["madde","madde","madde"],"coach_note":"Gerçekçi koç notu","next_questions":["soru","soru","soru"],"first_next_step":"Bugün atılabilecek tek somut adım","ai_suggestion":"Tek uygulanabilir öneri","difficulty":"Kolay / Orta / Zor","estimated_time":"tahmini süre","platform":"önerilen platform","project_type":"önerilen proje türü"}}'''

def generate_with_groq(idea, project_type, audience, detail_level, language, api_key, model):
    if Groq is None: raise RuntimeError("Groq paketi bulunamadı. requirements.txt kurulmalı.")
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(model=model, messages=[{"role":"system","content":build_system_prompt(language)}, {"role":"user","content":build_user_prompt(idea, project_type, audience, detail_level, language)}], temperature=0.5, max_tokens=3000, response_format={"type":"json_object"})
    return clean_json_response(completion.choices[0].message.content)

def as_markdown(data, original_idea):
    def list_md(values): return "\n".join([f"- {v}" for v in values or []])
    roadmap_md = ""
    for item in data.get("roadmap", []):
        roadmap_md += f"### {item.get('phase','')}\n" + "\n".join([f"- {x}" for x in item.get("items", [])]) + "\n\n"
    return f'''# {data.get('project_name','Proje Briefi')}\n\n> {data.get('tagline','')}\n\n## Ham Fikir\n\n{original_idea.strip()}\n\n## Proje Özeti\n\n{data.get('summary','')}\n\n## Problem\n\n{data.get('problem','')}\n\n## Çözüm Yaklaşımı\n\n{data.get('solution','')}\n\n## Proje Bilgileri\n\n- **Proje türü:** {data.get('project_type','')}\n- **Platform:** {data.get('platform','')}\n- **Zorluk:** {data.get('difficulty','')}\n- **Tahmini süre:** {data.get('estimated_time','')}\n\n## Hedef Kitle\n\n{list_md(data.get('target_audience', []))}\n\n## Anahtar Özellikler\n\n{list_md(data.get('key_features', []))}\n\n## MVP Kapsamı\n\n{list_md(data.get('mvp_scope', []))}\n\n## Teknik Gereksinimler\n\n{list_md(data.get('technical_requirements', []))}\n\n## Yol Haritası\n\n{roadmap_md.strip()}\n\n## Riskler\n\n{list_md(data.get('risks', []))}\n\n## Koç Notu\n\n{data.get('coach_note','')}\n\n## Cevaplanması İyi Olacak Sorular\n\n{list_md(data.get('next_questions', []))}\n\n## Bugünkü İlk Adım\n\n{data.get('first_next_step','')}\n\n## Kısa Öneri\n\n{data.get('ai_suggestion','')}\n\n---\n\nHazırlayan: RIGEL Brief AI\nTarih: {datetime.now().strftime('%d.%m.%Y')}'''

def as_readme(data):
    def list_md(values): return "\n".join([f"- {v}" for v in values or []])
    roadmap = ""
    for r in data.get("roadmap", []): roadmap += f"### {r.get('phase','')}\n" + "\n".join([f"- {x}" for x in r.get("items", [])]) + "\n\n"
    return f'''# {data.get('project_name','Project')}\n\n{data.get('tagline','')}\n\n## Overview\n\n{data.get('summary','')}\n\n## Problem\n\n{data.get('problem','')}\n\n## Solution\n\n{data.get('solution','')}\n\n## Core Features\n\n{list_md(data.get('key_features', []))}\n\n## MVP Scope\n\n{list_md(data.get('mvp_scope', []))}\n\n## Technical Requirements\n\n{list_md(data.get('technical_requirements', []))}\n\n## Roadmap\n\n{roadmap.strip()}\n\n## Product Note\n\n{data.get('coach_note','')}'''

def find_unicode_font():
    regular_candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf","/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf","/Library/Fonts/Arial.ttf","/System/Library/Fonts/Supplemental/Arial.ttf","C:/Windows/Fonts/arial.ttf"]
    bold_candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf","/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf","/Library/Fonts/Arial Bold.ttf","/System/Library/Fonts/Supplemental/Arial Bold.ttf","C:/Windows/Fonts/arialbd.ttf"]
    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    bold = next((p for p in bold_candidates if Path(p).exists()), regular)
    return regular, bold

def register_pdf_fonts():
    regular, bold = find_unicode_font()
    if regular:
        try:
            if "RigelSans" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("RigelSans", regular))
            if bold and "RigelSansBold" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("RigelSansBold", bold))
            return "RigelSans", "RigelSansBold"
        except Exception: pass
    return "Helvetica", "Helvetica-Bold"

def make_pdf(markdown_text, title):
    if SimpleDocTemplate is None: raise RuntimeError("PDF için reportlab paketi kurulu olmalı.")
    regular_font, bold_font = register_pdf_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.55*cm, leftMargin=1.55*cm, topMargin=1.55*cm, bottomMargin=1.55*cm, title=title, author="RIGEL Brief AI")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="RigelTitle", parent=styles["Title"], fontName=bold_font, fontSize=19, leading=23, spaceAfter=12, textColor=colors.HexColor("#141414")))
    styles.add(ParagraphStyle(name="RigelHeading", parent=styles["Heading2"], fontName=bold_font, fontSize=12.5, leading=16, spaceBefore=9, spaceAfter=5, textColor=colors.HexColor("#141414")))
    styles.add(ParagraphStyle(name="RigelBody", parent=styles["BodyText"], fontName=regular_font, fontSize=9.2, leading=13.4, spaceAfter=6, textColor=colors.HexColor("#141414")))
    styles.add(ParagraphStyle(name="RigelQuote", parent=styles["BodyText"], fontName=regular_font, fontSize=9.2, leading=13.4, leftIndent=8, spaceAfter=7, textColor=colors.HexColor("#444444")))
    story = []
    for raw_line in markdown_text.splitlines():
        raw = raw_line.strip()
        if not raw: story.append(Spacer(1, 5)); continue
        if raw.startswith("---"): story.append(Spacer(1, 8)); continue
        line = xml_escape(raw).replace("**", "")
        if raw.startswith("# "): story.append(Paragraph(xml_escape(raw.replace("# ", "", 1)), styles["RigelTitle"]))
        elif raw.startswith("## "): story.append(Paragraph(xml_escape(raw.replace("## ", "", 1)), styles["RigelHeading"]))
        elif raw.startswith("### "): story.append(Paragraph(xml_escape(raw.replace("### ", "", 1)), styles["RigelHeading"]))
        elif raw.startswith("- "): story.append(Paragraph("• " + xml_escape(raw.replace("- ", "", 1)).replace("**", ""), styles["RigelBody"]))
        elif raw.startswith("> "): story.append(Paragraph(xml_escape(raw.replace("> ", "", 1)), styles["RigelQuote"]))
        else: story.append(Paragraph(line, styles["RigelBody"]))
    doc.build(story); buffer.seek(0); return buffer.read()

def get_saved_groq_key():
    if os.getenv("GROQ_API_KEY", ""): return os.getenv("GROQ_API_KEY", "")
    try: return st.secrets.get("GROQ_API_KEY", "")
    except Exception: return ""

def init_state():
    defaults = {"idea_text": EXAMPLES["Ders çalışma uygulaması"], "brief_data": None, "used_ai": False, "error_message": "", "wizard_step": 1, "language_choice": "Türkçe", "project_type_choice": "Seçilmedi", "audience_choice": "Seçilmedi", "detail_choice": "Dengeli"}
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

def next_step(): st.session_state.wizard_step = min(4, st.session_state.wizard_step + 1)
def prev_step(): st.session_state.wizard_step = max(1, st.session_state.wizard_step - 1)

init_state()

st.markdown(f'<div class="rds-navbar"><div class="rds-left"><div class="rds-wordmark">RDS</div><div><div class="rds-app-title">RIGEL Brief AI</div><div class="rds-app-subtitle">Fikirden proje briefine</div></div></div><div class="rds-center">Rigel Digital Systems</div><div class="rds-right"><a class="home-button" href="{RDS_HOME_URL}" target="_blank" rel="noopener noreferrer">RDS Ana Sayfa &#8599;</a></div></div>', unsafe_allow_html=True)
st.markdown('<div class="compact-hero"><div><h1>Fikrini <span>temiz bir proje briefine</span> dönüştür.</h1><p>Kısa bir fikir yaz. RIGEL Brief AI onu proje özeti, hedef kitle, MVP kapsamı, teknik ihtiyaçlar, riskler ve ilk yol haritası olarak düzenlesin.</p></div></div>', unsafe_allow_html=True)

left, right = st.columns([0.9, 1.35], gap="large")

with left:
    st.markdown('<div class="card-head"><div><h2>1. Fikrini yaz</h2><p>Önce fikri alalım. Ayarları aşağıda tek tek soracağım.</p></div></div>', unsafe_allow_html=True)
    idea = st.text_area("Proje fikri", key="idea_text", label_visibility="collapsed", placeholder="Örneğin: Öğrencilerin ders çalışma sürecini planlayan basit bir web uygulaması yapmak istiyorum...")
    st.markdown(f'<div class="char-count">Karakter: {len(idea)} / 5000</div>', unsafe_allow_html=True)
    st.markdown('<div class="soft-label">Örnekle başla</div>', unsafe_allow_html=True)
    ex_cols = st.columns(2)
    for idx, name in enumerate(EXAMPLES.keys()):
        with ex_cols[idx % 2]:
            if st.button(name, key=f"example_{idx}"):
                st.session_state.idea_text = EXAMPLES[name]
                st.rerun()

    st.write("")
    step = st.session_state.wizard_step
    progress = int(step / 4 * 100)
    st.markdown(f'<div class="card-head"><div><h2>2. Brief ayarları</h2><p>Her şeyi aynı anda göstermiyorum. Sırayla ilerleyelim.</p></div><span class="step-badge">Adım {step}/4</span></div><div class="progress-wrap"><div class="progress-bar" style="width:{progress}%"></div></div>', unsafe_allow_html=True)

    if step == 1:
        st.markdown('<div class="step-card"><h3>Önce hangi dil ile başlamak istiyorsun?</h3><p>Brief çıktısı bu dilde hazırlanacak.</p>', unsafe_allow_html=True)
        st.session_state.language_choice = st.selectbox("Dil", LANGUAGES, index=LANGUAGES.index(st.session_state.language_choice))
        st.markdown('</div>', unsafe_allow_html=True)
        st.button("Devam", on_click=next_step, type="primary")
    elif step == 2:
        st.markdown('<div class="step-card"><h3>Bu fikir hangi proje türüne daha yakın?</h3><p>Emin değilsen “Seçilmedi” olarak bırakabilirsin.</p>', unsafe_allow_html=True)
        st.session_state.project_type_choice = st.selectbox("Proje türü", PROJECT_TYPES, index=PROJECT_TYPES.index(st.session_state.project_type_choice))
        st.markdown('</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1: st.button("Geri", on_click=prev_step)
        with b2: st.button("Devam", on_click=next_step, type="primary")
    elif step == 3:
        st.markdown('<div class="step-card"><h3>Kimin için hazırlıyoruz?</h3><p>Hedef kitleyi seçmek, AI çıktısını daha net hale getirir.</p>', unsafe_allow_html=True)
        st.session_state.audience_choice = st.selectbox("Hedef kitle", AUDIENCES, index=AUDIENCES.index(st.session_state.audience_choice))
        st.markdown('</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1: st.button("Geri", on_click=prev_step)
        with b2: st.button("Devam", on_click=next_step, type="primary")
    else:
        st.markdown('<div class="step-card"><h3>Çıktı ne kadar detaylı olsun?</h3><p>İlk deneme için “Dengeli” genelde en iyi seçimdir.</p>', unsafe_allow_html=True)
        st.session_state.detail_choice = st.selectbox("Çıktı uzunluğu", DETAIL_LEVELS, index=DETAIL_LEVELS.index(st.session_state.detail_choice))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="groq-card"><h3>Groq API bağlantısı</h3><p>İstersen anahtarını burada girebilirsin. Boş bırakılırsa yedek analiz kullanılır.</p>', unsafe_allow_html=True)
        env_key = get_saved_groq_key()
        api_key_input = st.text_input("Groq API anahtarı", value="", type="password", placeholder="Boş bırakılabilir", help="Terminal değişkeni, Streamlit secrets veya bu alan kullanılabilir.")
        api_key = api_key_input or env_key or ""
        model = st.selectbox("Model", ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "qwen/qwen3-32b"], index=0)
        if api_key: st.markdown('<div class="status-box status-ok">Groq anahtarı hazır. Brief oluşturunca AI destekli çıktı üretilecek.</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="status-box">API anahtarı yok. Yedek analiz sistemiyle devam edebilirsin.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1: st.button("Geri", on_click=prev_step)
        with b2: generate = st.button("Brief oluştur", type="primary")

if "api_key" not in locals(): api_key = get_saved_groq_key()
if "model" not in locals(): model = "llama-3.1-8b-instant"
if "generate" not in locals(): generate = False

if generate:
    if not st.session_state.idea_text.strip():
        st.session_state.error_message = "Önce kısa da olsa bir proje fikri yazmalısın."
    else:
        st.session_state.error_message = ""
        with st.spinner("Brief hazırlanıyor..."):
            if api_key:
                try:
                    st.session_state.brief_data = generate_with_groq(st.session_state.idea_text, st.session_state.project_type_choice, st.session_state.audience_choice, st.session_state.detail_choice, st.session_state.language_choice, api_key, model)
                    st.session_state.used_ai = True
                except Exception as exc:
                    st.session_state.brief_data = build_fallback_brief(st.session_state.idea_text, st.session_state.project_type_choice, st.session_state.audience_choice, st.session_state.detail_choice, st.session_state.language_choice)
                    st.session_state.used_ai = False
                    st.session_state.error_message = f"AI yanıtı alınamadı. Yedek analiz kullanıldı. Detay: {exc}"
            else:
                st.session_state.brief_data = build_fallback_brief(st.session_state.idea_text, st.session_state.project_type_choice, st.session_state.audience_choice, st.session_state.detail_choice, st.session_state.language_choice)
                st.session_state.used_ai = False

with right:
    data = st.session_state.brief_data
    st.markdown(f'<div class="card-head"><div><h2>3. Proje briefi</h2><p>{"AI destekli çıktı" if data and st.session_state.used_ai else "Yedek analiz çıktısı" if data else "Sonuç burada görünecek"}</p></div></div>', unsafe_allow_html=True)
    if data:
        markdown_text = as_markdown(data, st.session_state.idea_text)
        txt_text = re.sub(r"[#>*_`]", "", markdown_text)
        readme_text = as_readme(data)
        filename_base = re.sub(r"[^a-zA-Z0-9_-]+", "_", data.get("project_name", "rigel_brief").strip()).strip("_").lower()
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            try:
                pdf_bytes = make_pdf(markdown_text, data.get("project_name", "Brief"))
                st.download_button("PDF", data=pdf_bytes, file_name=f"{filename_base}_brief.pdf", mime="application/pdf")
            except Exception as exc:
                st.download_button("PDF hata", data=f"PDF oluşturulamadı: {exc}".encode("utf-8"), file_name=f"{filename_base}_pdf_error.txt", mime="text/plain")
        with d2: st.download_button("MD", data=markdown_text.encode("utf-8"), file_name=f"{filename_base}_brief.md", mime="text/markdown")
        with d3: st.download_button("TXT", data=txt_text.encode("utf-8"), file_name=f"{filename_base}_brief.txt", mime="text/plain")
        with d4: st.download_button("README", data=readme_text.encode("utf-8"), file_name="README.md", mime="text/markdown")
        if st.session_state.error_message: st.warning(st.session_state.error_message)
        st.markdown(f'<div class="meta-grid"><div class="meta-item"><span>Proje adı</span><strong>{h(data.get("project_name", "-"))}</strong></div><div class="meta-item"><span>Zorluk</span><strong>{h(data.get("difficulty", "-"))}</strong></div><div class="meta-item"><span>Tahmini süre</span><strong>{h(data.get("estimated_time", "-"))}</strong></div><div class="meta-item"><span>Platform</span><strong>{h(data.get("platform", "-"))}</strong></div></div>', unsafe_allow_html=True)
        tabs = st.tabs(["Özet", "Hedef kitle", "Özellikler", "Teknik", "Yol haritası", "README"])
        with tabs[0]:
            st.markdown(f'<div class="brief-grid"><div class="brief-card full"><h3>Proje özeti</h3><p>{h(data.get("summary", ""))}</p></div><div class="brief-card"><h3>Problem</h3><p>{h(data.get("problem", ""))}</p></div><div class="brief-card"><h3>Çözüm yaklaşımı</h3><p>{h(data.get("solution", ""))}</p></div></div><div class="coach-card"><strong>Koç notu</strong><p>{h(data.get("coach_note", ""))}</p><strong>Bugünkü ilk adım</strong><p>{h(data.get("first_next_step", ""))}</p></div>', unsafe_allow_html=True)
        with tabs[1]:
            st.markdown(f'<div class="brief-card"><h3>Kimler için?</h3>{html_list(data.get("target_audience", []))}</div><div class="brief-card"><h3>Cevaplanması iyi olacak sorular</h3>{html_list(data.get("next_questions", []))}</div>', unsafe_allow_html=True)
        with tabs[2]:
            st.markdown(f'<div class="brief-grid"><div class="brief-card"><h3>Ana özellikler</h3>{html_list(data.get("key_features", []))}</div><div class="brief-card"><h3>MVP kapsamı</h3>{html_list(data.get("mvp_scope", []))}</div></div>', unsafe_allow_html=True)
        with tabs[3]:
            st.markdown(f'<div class="brief-card"><h3>Teknik ihtiyaçlar</h3>{html_list(data.get("technical_requirements", []))}</div>', unsafe_allow_html=True)
        with tabs[4]:
            roadmap_html = ""
            for phase in data.get("roadmap", []): roadmap_html += f'<h3>{h(phase.get("phase", ""))}</h3>{html_list(phase.get("items", []))}'
            st.markdown(f'<div class="brief-card">{roadmap_html}</div><div class="brief-card"><h3>Riskler</h3>{html_list(data.get("risks", []))}</div><div class="brief-card"><h3>Kısa öneri</h3><p>{h(data.get("ai_suggestion", ""))}</p></div>', unsafe_allow_html=True)
        with tabs[5]: st.code(readme_text, language="markdown")
    else:
        if st.session_state.error_message: st.warning(st.session_state.error_message)
        st.markdown('<div class="empty-state"><div><h3>Brief henüz oluşturulmadı</h3><p>Soldaki alana fikrini yaz, ardından ayarları adım adım tamamla. Sonuç burada özet, hedef kitle, MVP kapsamı, teknik ihtiyaçlar ve yol haritası olarak görünecek.</p></div></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Rigel Digital Systems · İlim bir avdır, yazı ise onu bağlayan iptir</div>', unsafe_allow_html=True)
