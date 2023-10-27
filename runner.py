from datetime import datetime
import requests
import aiohttp
import asyncio
import time
import hashlib

PANEL_URL = "https://greyhal.com"
PANEL_SALT="dskvjmf39svcm"
CHECK_INTERVAL = 60 * 5

async def generate_salt():
    date = datetime.now().strftime("%Y%m%d")
    return hashlib.md5(f"{date}{PANEL_SALT}".encode('utf-8')).hexdigest()
    
async def send_to_panel(domain):
    url = f"{PANEL_URL}/api-checker/deactivate-url"
    salt = await generate_salt()
    data = {"salt": salt, "domain": domain}
    response = requests.post(url, data = data)
    return response.json()

async def check_url(session, url):
    if url != False:
        try:
            async with session.get(url) as response:
                result = await response.text()
                if any(text in result for text in ["This site can’t be reached", "Situs ini tidak dapat dijangkau", "SITUS DIBLOKIR"]):
                    raise ValueError("Nawala")
        except Exception as e:
            error_msg = f"{url} \n{str(e)}\n"
            print(error_msg)
            await send_to_panel(url)

async def main():
    while True:
        start_time = time.time()
        print('Checking start...')
        async with aiohttp.ClientSession() as session:
            try:
                get_list_domain = f"{PANEL_URL}/api-checker/get-list-url"
                salt = await generate_salt()
                data = {"salt": salt}
                response = requests.post(get_list_domain, data = data)
                
                list = response.json()
                domain_list = list.get('data')
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
            
        print('Finished...')
        execution_time = "--- %s seconds ---" % (time.time() - start_time)
        print(execution_time)
        time.sleep(CHECK_INTERVAL)

asyncio.run(main())
