from datetime import datetime
import requests
import aiohttp
import asyncio
import time

BOT_TOKEN = "6374582132:AAEMjw8CO2YRLNvEAl0VSzZ9AXTvaU9u96A"
CHAT_ID = "-823196726"
LINK_URL = "https://kaconkalus.site/checker/Link.txt"
# LINK_URL = "https://kaconkalus.site/checker/Link.txt"
CHECK_INTERVAL = 60 * 5

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data = data)
    return response.json()

async def check_url(session, url):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if url != False:
        try:
            async with session.get(url) as response:
                result = await response.text()
                if any(text in result for text in ["This site can’t be reached", "Situs ini tidak dapat dijangkau", "SITUS DIBLOKIR"]):
                    raise ValueError("Nawala")
        except Exception as e:
            error_msg = f"{url} \n{timestamp} \n{str(e)}\n"
            print(error_msg)
            await send_telegram_message(error_msg)

async def main():
    while True:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            try:
                response = requests.get(LINK_URL)
                # domain_list = response.text.splitlines()
                domain_list = response.text.splitlines()
            except Exception as e:
                print("Error", str(e))
                domain_list = []

            tasks = []
            for domain in domain_list:
                domain = domain.strip()
                if domain.startswith("http://") or domain.startswith("https://"):
                    url = domain
                elif '=' not in domain and len(domain) != 0 :
                    url = "https://" + domain
                else:
                    continue
                
                tasks.append(asyncio.ensure_future(check_url(session, url)))

            await asyncio.gather(*tasks)
        execution_time = "--- %s seconds ---" % (time.time() - start_time)
        print(execution_time)
        time.sleep(CHECK_INTERVAL)

asyncio.run(main())
