#!/usr/bin/env python3
import asyncio
import websockets
import pynitel
from annuaire import annuaire_teletel
from ulla_3615 import ulla_teletel

async def teletel_saisie(m, codes):
    m.resetzones()
    m.zone(17, 12, 28, '', m.blanc)
    touche = m.repetition
    zone = 1

    while True:
        # affichage initial ou répétition
        if touche == m.repetition:
            await m.home()
            await m.xdraw('ecrans/teletel/teletel3-1992.vtx')

        # gestion de la zone de saisie courante
        (zone, touche) = await m.waitzones(zone)
        # on récupère les quoi et le ou...
        code = m.zones[0]['texte'].upper().strip()

        if (touche == m.envoi):
            if code == '':
                await m.message(0, 1, 3,
                                "Entrez le code du service souhaité")
            elif code in codes:
                return (touche, code)
            else:
                await m.message(0, 1, 3,
                                "Code de service inconnu")
        elif touche != m.repetition:
            await m.message(0, 1, 3, "Désolé, pas encore disponible")


async def teletel(websocket, path):
    m = pynitel.Pynitel(pynitel.PynitelWS(websocket))
    # on récupère le code du service depuis le path du webSocket
    # //ws -> vide  /ulla/ws -> ULLA etc...
    code = path.replace('/ws', '').replace('/', '').upper().strip()
    touche = m.envoi
    # liste des service connus...
    codes = ['11', '3611', 'AE', 'ANNU', 'ANNUAIRE',
             'ULLA']

    while True:
        await m._print(m.PRO2+'\x6A\x45')  # passage clavier standard
        if code != '':
            # on lance la recherche
            await m.pos(0, 1)
            await m._print('connexion...           t0 0,00F/min')
            await asyncio.sleep(2)
            await m.home()
            if code in ['11', '3611', 'AE', 'ANNU', 'ANNUAIRE']:
                await annuaire_teletel(m)
            elif code == 'ULLA':
                await ulla_teletel(m)

        (touche, code) = await teletel_saisie(m, codes)
        if touche == m.envoi:
            code = code.upper().strip()
        else:
            code = ''


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        websockets.serve(teletel, 'localhost', 3615))
    loop.run_forever()
