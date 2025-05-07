import requests
import pandas as pd
import numpy as np
import talib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# دریافت داده از tsetmc
def get_stock_data(inscode):
    url = f'https://www.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={inscode}&t=1'
    r = requests.get(url)
    lines = r.text.split(';')
    data = [line.split('@') for line in lines if line]
    df = pd.DataFrame(data, columns=["date", "high", "low", "close", "open", "last", "volume"])
    df = df.astype({"high": float, "low": float, "close": float, "open": float, "volume": float})
    df = df[::-1].reset_index(drop=True)
    return df

# محاسبه اندیکاتورها
def calculate_indicators(df):
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values

    indicators = {}
    indicators['rsi'] = talib.RSI(close)
    indicators['macd'], indicators['macdsignal'], _ = talib.MACD(close)
    indicators['ma20'] = talib.SMA(close, timeperiod=20)
    indicators['ma50'] = talib.SMA(close, timeperiod=50)
    indicators['ichimoku_a'] = (talib.SMA(high, 9) + talib.SMA(low, 9)) / 2
    indicators['ichimoku_b'] = (talib.SMA(high, 26) + talib.SMA(low, 26)) / 2
    return indicators

# تولید سیگنال
def generate_signal(df, ind):
    close = df['close'].values
    if len(close) < 50:
        return "داده کافی برای تحلیل نیست."

    if (
        ind['macd'][-1] > ind['macdsignal'][-1] and
        ind['rsi'][-1] > 50 and
        close[-1] > ind['ma20'][-1] > ind['ma50'][-1] and
        close[-1] > ind['ichimoku_a'][-1] and
        close[-1] > ind['ichimoku_b'][-1]
    ):
        return "سیگنال ورود"
    elif (
        ind['macd'][-1] < ind['macdsignal'][-1] and
        ind['rsi'][-1] < 50 and
        close[-1] < ind['ma20'][-1] < ind['ma50'][-1] and
        close[-1] < ind['ichimoku_a'][-1] and
        close[-1] < ind['ichimoku_b'][-1]
    ):
        return "سیگنال خروج"
    else:
        return "سیگنال خنثی"

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات تحلیل بورس ایران خوش اومدی!\n"
        "نام ربات: ehsan136_bot\n\n"
        "برای تحلیل سهم، کد نماد tsetmc رو بده:\nمثلاً:\n/check 46348559193224090"
    )

# دستور /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("لطفاً کد نماد رو درست وارد کن.")
        return
    inscode = context.args[0]
    try:
        df = get_stock_data(inscode)
        ind = calculate_indicators(df)
        signal = generate_signal(df, ind)
        await update.message.reply_text(
            f"نتیجه تحلیل ({inscode}) توسط ehsan136_bot:\n\n{signal}"
        )
    except Exception as e:
        await update.message.reply_text(f"خطا در تحلیل: {str(e)}")

# اجرای ربات
def main():
    TOKEN = "7899158333:AAFNxophK13V7aFE2OpCGE968M5XdyW1MGk"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    print("ربات ehsan136_bot فعال است...")
    app.run_polling()

if __name__ == "__main__":
    main()
