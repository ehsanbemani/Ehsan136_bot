import logging
import pandas as pd
import pandas_ta as ta
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# توکن ربات
TOKEN = "7899158333:AAFNxophK13V7aFE2OpCGE968M5XdyW1MGk"

# فعال‌سازی لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تابع برای دریافت داده‌های ساختگی سهم (جایگزین کن با API واقعی TSETMC در آینده)
def get_stock_data():
    # داده فرضی
    data = {
        'close': [100, 105, 102, 108, 110, 115, 120, 118, 125, 130, 135, 138, 140],
        'volume': [2000, 2100, 2200, 5000, 2500, 3000, 10000, 3200, 3300, 4000, 6000, 6200, 6400]
    }
    df = pd.DataFrame(data)
    return df

# تحلیل سهم با اندیکاتورها
def analyze_stock():
    df = get_stock_data()
    
    # اندیکاتورهای پایه
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)
    df['ema_9'] = ta.ema(df['close'], length=9)
    
    # حجم مشکوک
    average_volume = df['volume'].rolling(window=5).mean()
    df['suspicious_volume'] = df['volume'] > (1.8 * average_volume)

    last = df.iloc[-1]
    signals = []

    # بررسی RSI
    if last['rsi'] < 30:
        signals.append("RSI: اشباع فروش (احتمال ورود)")
    elif last['rsi'] > 70:
        signals.append("RSI: اشباع خرید (احتمال خروج)")

    # بررسی MACD
    if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
        signals.append("MACD: سیگنال ورود")
    else:
        signals.append("MACD: سیگنال خروج")

    # بررسی حجم مشکوک
    if last['suspicious_volume']:
        signals.append("حجم مشکوک: بررسی بیشتر توصیه می‌شود")

    return "\n".join(signals)

# فرمان `/start`
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دریافت تحلیل سهم دستور /analyze را بزنید.")

# فرمان `/analyze`
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = analyze_stock()
    await update.message.reply_text(f"نتیجه تحلیل:\n{result}")

# اجرای ربات
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))

    print("ربات ehsan136_bot فعال است...")
    app.run_polling()
