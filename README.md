# Yerel AI Asistan

WhatsApp üzerinden Türkçe konuşan, tamamen yerel çalışan kişisel üretkenlik asistanı.

## Özellikler

- **Görev Yönetimi** — Doğal dille görev ekle, listele, tamamla
- **Takvim** — Etkinlik ekle, hatırlatma ayarla
- **Notlar** — Hızlı not kaydet, etiketle, ara
- **Hatırlatmalar** — Zamana dayalı hatırlatmalar
- **Alışkanlık Takibi** — Günlük hedefler, seri takibi
- **Harcama Takibi** — Kategori bazlı kayıt, aylık/haftalık özet
- **Ruh Hali Günlüğü** — Günlük ruh hali kaydı, trend analizi
- **Hedef Takibi** — Uzun vadeli hedefler, ilerleme çubuğu
- **Raporlar** — Sabah özeti, haftalık/aylık raporlar
- **Self-Modify** — WhatsApp'tan bot davranışını ve kodunu değiştir

## Mimari

```
Desktop (RTX 3060 Ti)
+---------------------------+
|  WhatsApp Bot (Node.js)   |  <-- whatsapp-web.js
|  Core API (FastAPI)       |  <-- Ollama entegrasyonu
|  Scheduler (APScheduler)  |  <-- Zamanlanmış görevler
|  Ollama (Llama 3.1 8B)   |  <-- Yerel AI
|  SQLite (assistant.db)    |  <-- Tüm veriler
+---------------------------+
```

Laptop sadece geliştirme için kullanılır (VS Code + SSH).

## Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| API | Python 3.11+ / FastAPI / uvicorn |
| AI | Ollama / Llama 3.1 8B |
| Bot | Node.js / whatsapp-web.js |
| Zamanlayıcı | APScheduler |
| Veritabanı | SQLite3 |
| GPU | NVIDIA RTX 3060 Ti (8GB VRAM) |

## Kurulum

### 1. Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

### 2. Python Bağımlılıkları

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Node.js Bağımlılıkları

```bash
cd bot
npm install
cd ..
```

### 4. Başlat

```bash
./start.sh
```

Terminal'de QR kod görünecek — WhatsApp'tan tarayın. Bot hazır.

## Kullanım

WhatsApp'tan mesaj yazarak kullanın:

| Mesaj | Sonuç |
|-------|-------|
| `yarın raporu bitir` | Görev ekler |
| `bugün ne var?` | Günün görevlerini listeler |
| `rapor bitti` | Görevi tamamlar |
| `yarın saat 3'te doktor` | Takvime etkinlik ekler |
| `not al: Ali'nin tel 0532...` | Not kaydeder |
| `2 saat sonra hatırlat: ilacı iç` | Hatırlatma kurar |
| `su içtim` | Alışkanlık kaydeder |
| `markette 450 lira harcadım` | Harcama kaydeder |
| `bu ay 10 kitap oku` | Hedef oluşturur |
| `sabah özetini 7:30'a al` | Bot ayarını değiştirir |

### Otomatik Mesajlar

- **Sabah özeti** (08:00) — Günün görevleri, etkinlikler, alışkanlıklar
- **Ruh hali sorgusu** (21:00) — "Bugün nasıl geçti?"
- **Haftalık rapor** (Pazar 21:00) — Performans özeti
- **Aylık rapor** (Ayın son günü) — Detaylı özet + hedef ilerlemesi

## Proje Yapısı

```
local-ai-assistant/
├── core/
│   ├── main.py            # FastAPI sunucu
│   ├── ai.py              # Ollama entegrasyonu
│   ├── db.py              # SQLite şema + bağlantı
│   ├── reports.py         # Rapor oluşturma
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
│   └── jobs.py            # Zamanlanmış iş tanımları
├── bot/
│   ├── index.js           # WhatsApp bot
│   └── package.json
├── tests/                 # 61 test
├── start.sh               # Tüm servisleri başlat
└── requirements.txt
```

## Test

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Ortam Değişkenleri

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `OWNER_NUMBER` | (boş) | WhatsApp numarası (örn: 905551234567@c.us) |
| `CORE_API_URL` | http://localhost:8000 | Core API adresi |
| `BOT_PORT` | 3000 | Bot HTTP portu |

## Lisans

MIT
