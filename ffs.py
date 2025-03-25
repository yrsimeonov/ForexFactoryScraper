"""ForexFactoryScraper - Versión Estable Final"""
import json
import csv
import time
import random
from datetime import datetime, timedelta
from os import path
import undetected_chromedriver as uc
from dateutil.tz import gettz

# Configuración
TIMEZONE_NAME = 'Europe/Madrid'  # Usar nombre de zona horaria como string
CSV_FILENAME = 'forex_factory_catalog.csv'
ERRORS_FILENAME = 'errors.csv'
START_YEAR = 2025
START_MONTH = 3
START_DAY = 16

def setup_driver():
    """Configuración robusta del driver"""
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920x1080')
    return uc.Chrome(options=options, use_subprocess=False)

def get_js_data(driver):
    """Extrae datos de calendarComponentStates[1]"""
    script = """
    if (window.calendarComponentStates && window.calendarComponentStates[1]) {
        return JSON.stringify({
            days: window.calendarComponentStates[1].days,
            updated: new Date().toISOString()
        });
    }
    return '{}';
    """
    return json.loads(driver.execute_script(script))

def parse_datetime(timestamp, tz):
    """Convierte timestamp Unix a datetime con zona horaria"""
    return datetime.fromtimestamp(timestamp, tz).isoformat()

def process_day(day_data, tz):
    """Procesa un día completo de eventos"""
    results = []
    for event in day_data.get('events', []):
        try:
            event_date = parse_datetime(event['dateline'], tz)
            
            results.append({
                'datetime': event_date,
                'currency': event.get('currency', ''),
                'impact': event.get('impactTitle', '').replace('Non-Economic', 'Holiday'),
                'event': event.get('name', ''),
                'actual': event.get('actual', ''),
                'forecast': event.get('forecast', ''),
                'previous': event.get('previous', '')
            })
        except Exception as e:
            error_msg = f"{datetime.now().isoformat()}|Error procesando evento: {str(e)}"
            with open(ERRORS_FILENAME, 'a') as f:
                f.write(error_msg + '\n')
    return results

def scrap():
    """Función principal de scraping"""
    driver = None
    try:
        driver = setup_driver()
        tz = gettz(TIMEZONE_NAME)  # Obtener tzfile desde el nombre
        
        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'datetime', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous'
            ])
            
            if csvfile.tell() == 0:
                writer.writeheader()

            current_date = get_start_date(tz)
            end_date = datetime.now(tz)

            while current_date <= end_date:
                url_date = current_date.strftime("%b%d.%Y").lower()
                url = f'https://www.forexfactory.com/calendar?day={url_date}'
                
                print(f"\rProcesando: {current_date.date()}", end='', flush=True)
                
                try:
                    time.sleep(random.uniform(2, 4))
                    driver.get(url)
                    
                    js_data = get_js_data(driver)
                    
                    for day in js_data.get('days', []):
                        if 'events' in day:
                            for row in process_day(day, tz):
                                writer.writerow(row)
                    
                    current_date += timedelta(days=1)

                except Exception as e:
                    error_msg = f"{datetime.now().isoformat()}|{url}|{str(e)}"
                    with open(ERRORS_FILENAME, 'a') as f:
                        f.write(error_msg + '\n')
                    continue

    finally:
        if driver:
            try:
                driver.close()
                driver.quit()  # Cierre seguro
            except Exception as e:
                print(f"\nError al cerrar driver: {str(e)}")
        print("\nScraping completado. Datos guardados en:", CSV_FILENAME)

def get_start_date(timezone_obj):
    """Obtiene la última fecha desde el CSV usando objeto tzfile"""
    if path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
            last_line = None
            for line in csv.DictReader(f):
                if line: last_line = line
            if last_line:
                try:
                    last_date = datetime.fromisoformat(last_line['datetime']).astimezone(timezone_obj)
                    return last_date + timedelta(seconds=1)
                except ValueError:
                    pass
    return datetime(year=START_YEAR, month=START_MONTH, day=START_DAY, tzinfo=timezone_obj)

if __name__ == '__main__':
    scrap()