import cloudscraper
import json
import os
import time
from datetime import datetime

class SALottoScraper:
    def __init__(self):
        # Tenta simular um navegador real de forma mais profunda
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.base_url = "https://www.nationallottery.co.za/index.php?option=com_weaver&controller=lotto-history"
        self.data_dir = "data"
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_data(self, game_name):
        payload = {
            'gameName': game_name,
            'drawNumber': '', 
            'isAjax': 'true'
        }
        
        # Headers idênticos aos de um navegador Chrome real
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'referer': 'https://www.nationallottery.co.za/results/lotto'
        }

        try:
            print(f"[*] Solicitando {game_name}...")
            # Usamos o scraper que pula o Cloudflare
            response = self.scraper.post(self.base_url, data=payload, headers=headers, timeout=30)
            
            print(f"[DEBUG] Status Code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()
                if content.get('status') == 'success':
                    return content['data']['drawDetails']
                else:
                    print(f"[!] Site retornou erro: {content.get('message')}")
            else:
                # Se der 403, o IP do GitHub foi bloqueado
                print(f"[!] Erro HTTP {response.status_code}. O site pode estar bloqueando o bot.")
                
        except Exception as e:
            print(f"[!] Falha na requisição: {str(e)}")
        return None

    def save_data(self, name, data):
        filename = f"{self.data_dir}/{name.lower().replace(' ', '_')}.json"
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game": name,
            "results": data
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"[OK] Gravado: {filename}")

    def run(self):
        loterias = ["LOTTO", "POWERBALL", "DAILY LOTTO"]
        for lotto in loterias:
            result = self.fetch_data(lotto)
            if result:
                self.save_data(lotto, result)
            else:
                print(f"[!] Nenhum dado para {lotto}")
            time.sleep(10) # Aumentado para não parecer ataque

if __name__ == "__main__":
    bot = SALottoScraper()
    bot.run()
