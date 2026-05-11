const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const express = require("express");

const CORE_API_URL = process.env.CORE_API_URL || "http://localhost:8000";
const OWNER_NUMBER = process.env.OWNER_NUMBER || "";
const PORT = process.env.BOT_PORT || 3000;

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  },
});

let ownerChatId = OWNER_NUMBER;
let isProcessing = false;

client.on("qr", (qr) => {
  console.log("[Bot] QR kodu tarayın:");
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("[Bot] WhatsApp bağlantısı kuruldu!");
});

client.on("message_create", async (msg) => {
  if (!msg.fromMe) return;
  if (isProcessing) return;

  if (!ownerChatId) {
    ownerChatId = msg.from;
    console.log(`[Bot] Sahip chat ID kaydedildi: ${ownerChatId}`);
  }
  const text = msg.body.trim();
  if (!text) return;

  isProcessing = true;
  try {
    const response = await fetch(`${CORE_API_URL}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      await client.sendMessage(msg.from, "Bir sorun oluştu, tekrar dener misin?");
      return;
    }
    const data = await response.json();
    await client.sendMessage(msg.from, data.response);
  } catch (error) {
    console.error("[Bot] API hatası:", error.message);
    await client.sendMessage(msg.from, "Şu an AI servisine ulaşamıyorum, lütfen biraz sonra tekrar dene.");
  } finally {
    setTimeout(() => { isProcessing = false; }, 1500);
  }
});

const app = express();
app.use(express.json());

app.post("/send", async (req, res) => {
  const { text } = req.body;
  if (!ownerChatId) {
    return res.status(400).json({ error: "Owner chat ID not set yet. Send a message first." });
  }
  try {
    await client.sendMessage(ownerChatId, text);
    res.json({ status: "sent" });
  } catch (error) {
    console.error("[Bot] Mesaj gönderilemedi:", error.message);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`[Bot] HTTP sunucusu port ${PORT}'da çalışıyor`);
});

client.initialize();
