import asyncio
from bs4 import BeautifulSoup
import httpx
from telegram.ext import Application

TOKEN = ''
CHAT_ID = ''
app = Application.builder().token(TOKEN).build()

ignored_models = {'iPhone 4', 'iPhone 5', 'iPhone 6', 'iPhone 6s', 'iPhone 7', 'iPhone 8'}


max_prices = {
    'iPhone X': 100,
    'iPhone Xs Max': 100,
    'iPhone Xs': 100,
    'iPhone Xr': 100,
    'iPhone 11': 120,
    'iPhone 11 Pro': 180,
    'iPhone 11 Pro Max': 200,
    'iPhone 12 Mini': 200,
    'iPhone 12': 200,
    'iPhone 12 Pro': 230,
    'iPhone 12 Pro Max': 230,
    'iPhone 13': 100,
    'iPhone 13 Pro': 100,
    'iPhone 13 Pro Max': 100,
    'iPhone 13 Mini': 100,
    'iPhone 14': 100,
    'iPhone 14 Plus': 100,
    'iPhone 14 Pro': 100,
    'iPhone 14 Pro Max': 100,
    'iPhone 15': 100,
    'iPhone 15 Pro': 100,
    'iPhone 15 Pro Max': 100,
    'iPhone 15 Plus': 100,
}

async def send_message(text):
    try:
        await app.bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print(f"Error sending message: {e}")

async def fetch_url(url):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
        return response
    except httpx.ReadTimeout:
        print("Timeout occurred, retrying...")
        return await fetch_url(url)

def extract_price(price_str):
    
    price_str = price_str.replace('€', '').strip()
    try:
        return float(price_str)
    except ValueError:
        return None

async def job():
    print("Парсинг данных...")
    url = "https://www.ss.lv/ru/electronics/phones/mobile-phones/apple/today/"
    response = await fetch_url(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for row in soup.select('tr[id^="tr_"]'):
        ad_text = row.select_one('.msg2 a').text if row.select_one('.msg2 a') else "No title found"
        ad_link = row.select_one('.msg2 a')['href'] if row.select_one('.msg2 a') else "No link found"
        if ad_link != "No link found" and not ad_link.startswith('http'):
            ad_link = "https://www.ss.lv" + ad_link

        columns = row.find_all('td', class_='msga2-o')
        if columns:
            model = columns[0].text.strip()
            memory = columns[1].text.strip() if len(columns) > 1 else "No memory info"
            price_str = columns[3].text.strip() if len(columns) > 3 else "No price found"
            price = extract_price(price_str)

            if model in ignored_models:
                continue

            if model in max_prices and price is not None and price <= max_prices[model]:
                message = f"Ad: {ad_text}, Model: {model}, Memory: {memory}, Price: {price_str}, Link: {ad_link}"
                await send_message(message)
            else:
                print(f"Skipping {model} with price {price_str} (too high or unknown model)")

    print("Парсинг завершен.")

async def scheduler():
    while True:
        await job()
        await asyncio.sleep(3600)  # set interval here

if __name__ == "__main__":
    asyncio.run(scheduler())



