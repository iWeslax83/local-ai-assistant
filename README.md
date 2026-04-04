# Yerel AI Asistan

WhatsApp uzerinden Turkce konusan, tamamen yerel calisan kisisel uretkenlik asistani.

## Ozellikler

- **Gorev Yonetimi** — Dogal dille gorev ekle, listele, tamamla
- **Takvim** — Etkinlik ekle, hatirlatma ayarla
- **Notlar** — Hizli not kaydet, etiketle, ara
- **Hatirlatmalar** — Zamana dayali hatirlatmalar
- **Aliskanlik Takibi** — Gunluk hedefler, seri takibi
- **Harcama Takibi** — Kategori bazli kayit, aylik/haftalik ozet
- **Ruh Hali Gunlugu** — Gunluk ruh hali kaydi, trend analizi
- **Hedef Takibi** — Uzun vadeli hedefler, ilerleme cubugu
- **Raporlar** — Sabah ozeti, haftalik/aylik raporlar
- **Self-Modify** — WhatsApp'tan bot davranisini ve kodunu degistir

## Mimari

```
Desktop (RTX 3060 Ti)
+---------------------------+
|  WhatsApp Bot (Node.js)   |  <-- whatsapp-web.js
|  Core API (FastAPI)       |  <-- Ollama entegrasyonu
|  Scheduler (APScheduler)  |  <-- Zamanlanmis gorevler
|  Ollama (Llama 3.1 8B)   |  <-- Yerel AI
|  SQLite (assistant.db)    |  <-- Tum veriler
+---------------------------+
```

Laptop sadece gelistirme icin kullanilir (VS Code + SSH).

## Teknoloji Yigini

| Bilesen | Teknoloji |
|---------|-----------|
| API | Python 3.11+ / FastAPI / uvicorn |
| AI | Ollama / Llama 3.1 8B |
| Bot | Node.js / whatsapp-web.js |
| Zamanlayici | APScheduler |
| Veritabani | SQLite3 |
| GPU | NVIDIA RTX 3060 Ti (8GB VRAM) |

## Kurulum

### 1. Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

### 2. Python Bagimliliklari

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Node.js Bagimliliklari

```bash
cd bot
npm install
cd ..
```

### 4. Baslat

```bash
./start.sh
```

Terminal'de QR kod gorunecek — WhatsApp'tan tarayin. Bot hazir.

## Kullanim

WhatsApp'tan mesaj yazarak kullanin:

| Mesaj | Sonuc |
|-------|-------|
| `yarin raporu bitir` | Gorev ekler |
| `bugün ne var?` | Gunun gorevlerini listeler |
| `rapor bitti` | Gorevi tamamlar |
| `yarin saat 3'te doktor` | Takvime etkinlik ekler |
| `not al: Ali'nin tel 0532...` | Not kaydeder |
| `2 saat sonra hatırlat: ilacı iç` | Hatirlatma kurar |
| `su içtim` | Aliskanlik kaydeder |
| `markette 450 lira harcadım` | Harcama kaydeder |
| `bu ay 10 kitap oku` | Hedef olusturur |
| `sabah özetini 7:30'a al` | Bot ayarini degistirir |

### Otomatik Mesajlar

- **Sabah ozeti** (08:00) — Gunun gorevleri, etkinlikler, aliskanliklar
- **Ruh hali sorgusu** (21:00) — "Bugun nasil gecti?"
- **Haftalik rapor** (Pazar 21:00) — Performans ozeti
- **Aylik rapor** (Ayin son gunu) — Detayli ozet + hedef ilerlemesi

## Proje Yapisi

```
local-ai-assistant/
├── core/
│   ├── main.py            # FastAPI sunucu
│   ├── ai.py              # Ollama entegrasyonu
│   ├── db.py              # SQLite sema + baglanti
│   ├── reports.py         # Rapor olusturma
│   └── intents/           # Intent handler'lar
│       ├── tasks.py
│       ├── events.py
│       ├── notes.py
│       ├── reminders.py
│       ├── habits.py
│       ├── expenses.py
│       ├── moods.py
│       ├── goals.py
│       ├── preferences.py
│       └── self_modify.py
├── scheduler/
│   ├── main.py            # APScheduler kurulumu
│   └── jobs.py            # Zamanlanmis is tanimlari
├── bot/
│   ├── index.js           # WhatsApp bot
│   └── package.json
├── tests/                 # 61 test
├── start.sh               # Tum servisleri baslat
└── requirements.txt
```

## Test

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Ortam Degiskenleri

| Degisken | Varsayilan | Aciklama |
|----------|-----------|----------|
| `OWNER_NUMBER` | (bos) | WhatsApp numarasi (orn: 905551234567@c.us) |
| `CORE_API_URL` | http://localhost:8000 | Core API adresi |
| `BOT_PORT` | 3000 | Bot HTTP portu |

## Lisans

MIT
