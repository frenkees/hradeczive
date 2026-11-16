"""Ikona v oznamovací oblasti: barva = stav renderu (šedá nic, modrá běží, zelená hotovo, červená chyba); klik otevře dashboard; oznámení po dokončení.
Potřebuje: pystray, pillow (.venv/Scripts/pip install pystray). Spuštění: spustit.bat nebo python skripty/dashboard/tray.py"""
import sys, threading, time, webbrowser
from pathlib import Path
import pystray
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
import server

BARVY = {'bezi': (90, 162, 255), 'hotovo': (76, 195, 138), 'chyba': (239, 106, 91), 'stoji': (141, 153, 176), 'nic': (141, 153, 176)}
URL = f'http://127.0.0.1:{server.PORT}/'


def ikona(stav, hotovo, celkem):
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((2, 2, 62, 62), fill=BARVY.get(stav, BARVY['nic']) + (255,))
    if stav == 'bezi' and celkem and hotovo: d.pieslice((12, 12, 52, 52), -90, -90 + 360 * hotovo / celkem, fill=(16, 20, 28, 255))
    return im


def main():
    threading.Thread(target=lambda: server.ThreadingHTTPServer(('127.0.0.1', server.PORT), server.H).serve_forever(), daemon=True).start()
    ic = pystray.Icon('hradec', ikona('nic', 0, 16), 'Hradec Živě',
                      menu=pystray.Menu(pystray.MenuItem('Otevřít dashboard', lambda: webbrowser.open(URL), default=True),
                                        pystray.MenuItem('Konec', lambda i, _: i.stop())))

    def smycka():
        minule = None
        while True:
            try:
                r = server.render(); n = len(r['hotovo'])
                ic.icon = ikona(r['stav'], n, r['celkem']); ic.title = f"Render: {r['stav']} {n}/{r['celkem']}"
                if minule == 'bezi' and r['stav'] in ('hotovo', 'chyba'): ic.notify(f"Render {r['stav']} ({n}/{r['celkem']} čtverců)", 'Hradec Živě')
                minule = r['stav']
            except Exception:
                pass
            time.sleep(10)
    threading.Thread(target=smycka, daemon=True).start()
    ic.run()


if __name__ == '__main__':
    main()
