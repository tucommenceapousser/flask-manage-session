#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Session Cookie Decoder/Encoder ++
Enhanced by trhacknon
"""

import sys
import zlib
import ast
import json
import argparse
import requests
from itsdangerous import base64_decode
from flask.sessions import SecureCookieSessionInterface
from rich import print
from rich.prompt import Prompt
from rich.progress import track


# ---------------- Mock Flask App ----------------
class MockApp(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key


# ---------------- FSCM Core ----------------
class FSCM:
    @staticmethod
    def encode(secret_key, session_cookie_structure):
        """Encode une structure Python/JSON en cookie Flask"""
        try:
            app = MockApp(secret_key)
            si = SecureCookieSessionInterface()
            s = si.get_signing_serializer(app)
            struct = parse_input(session_cookie_structure)
            return s.dumps(struct)
        except Exception as e:
            return f"[red][Encoding error][/red] {e}"

    @staticmethod
    def decode(session_cookie_value, secret_key=None):
        """Décode un cookie Flask, avec ou sans secret_key"""
        try:
            if secret_key is None:
                # Mode brut (sans clé)
                payload = session_cookie_value
                compressed = False
                if payload.startswith('.'):
                    compressed = True
                    payload = payload[1:]
                data = payload.split(".")[0]
                data = base64_decode(data)
                if compressed:
                    data = zlib.decompress(data)
                return data
            else:
                app = MockApp(secret_key)
                si = SecureCookieSessionInterface()
                s = si.get_signing_serializer(app)
                return s.loads(session_cookie_value)
        except Exception as e:
            return f"[red][Decoding error][/red] {e}"


# ---------------- Helpers ----------------
def parse_input(raw):
    """Détecte si entrée est JSON, dict Python ou 'auto'"""
    if raw.strip().lower() == "auto":
        return interactive_build()
    try:
        return json.loads(raw)  # JSON ?
    except Exception:
        try:
            return dict(ast.literal_eval(raw))  # dict Python ?
        except Exception as e:
            raise ValueError(f"Impossible de parser la structure (-t): {e}")


def interactive_build():
    """Construit la session cookie structure interactivement"""
    print("[cyan][*][/cyan] Mode interactif - construisons ta structure de session")
    data = {}
    while True:
        key = Prompt.ask(" ➤ Nom du champ (laisser vide pour terminer)")
        if key.strip() == "":
            break
        value = Prompt.ask(f"   Valeur pour '{key}'")
        # Essaie d'inférer type (int, bool, str)
        if value.isdigit():
            value = int(value)
        elif value.lower() in ["true", "false"]:
            value = value.lower() == "true"
        data[key] = value
    print(f"[green][+] Structure construite:[/green] {data}")
    return data


def guess_from_url(url, secret_key=None):
    """Essaye de récupérer le cookie Flask d'une URL et le décoder"""
    print(f"[cyan][*][/cyan] Tentative de récupération du cookie depuis {url}")
    try:
        r = requests.get(url, timeout=10)
        if "session" not in r.cookies:
            print("[red][!] Aucun cookie Flask 'session' trouvé[/red]")
            return
        cookie_val = r.cookies["session"]
        print(f"[green][+] Cookie trouvé :[/green] {cookie_val[:60]}...")

        if secret_key:
            decoded = FSCM.decode(cookie_val, secret_key)
            print(f"[green][+] Décodage avec clé '{secret_key}':[/green] {decoded}")
        else:
            print("[yellow][!] Aucune secret key donnée, affichage brut[/yellow]")
            decoded = FSCM.decode(cookie_val)
            print(decoded)

    except Exception as e:
        print(f"[red][!] Erreur pendant guess:[/red] {e}")


def bruteforce_secret_key(cookie_val, wordlist):
    """Bruteforce/dictionnaire pour retrouver la secret_key"""
    print(f"[cyan][*][/cyan] Lancement bruteforce sur cookie : {cookie_val[:40]}...")

    try:
        with open(wordlist, "r", encoding="utf-8") as f:
            keys = [k.strip() for k in f.readlines()]
    except Exception as e:
        print(f"[red][!] Impossible de lire le wordlist :[/red] {e}")
        return

    for key in track(keys, description="Bruteforce en cours..."):
        result = FSCM.decode(cookie_val, key)
        if isinstance(result, dict):  # Décodage valide = clé trouvée
            print(f"[green][+] Clé trouvée ![/green] '{key}' => {result}")
            return key

    print("[red][!] Aucune clé trouvée dans le wordlist[/red]")
    return None


# ---------------- Main CLI ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flask Session Cookie Decoder/Encoder ++",
        epilog="Authors : Wilson Sumanang, Alexandre ZANNI, enhanced by trhacknon"
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # Encode
    parser_encode = subparsers.add_parser("encode", help="Encoder un cookie Flask")
    parser_encode.add_argument("-s", "--secret-key", required=True, help="Secret key Flask")
    parser_encode.add_argument("-t", "--cookie-structure", required=True,
                               help="Structure du cookie (dict/json/auto)")

    # Decode
    parser_decode = subparsers.add_parser("decode", help="Décoder un cookie Flask")
    parser_decode.add_argument("-c", "--cookie-value", required=True, help="Cookie Flask à décoder")
    parser_decode.add_argument("-s", "--secret-key", required=False, help="Secret key Flask (optionnelle)")

    # Guess
    parser_guess = subparsers.add_parser("guess", help="Essayer de deviner un cookie depuis une URL")
    parser_guess.add_argument("--url", required=True, help="URL cible")
    parser_guess.add_argument("-s", "--secret-key", required=False, help="Secret key Flask")

    # Bruteforce
    parser_brute = subparsers.add_parser("bruteforce", help="Bruteforce la secret_key Flask")
    parser_brute.add_argument("-c", "--cookie-value", required=True, help="Cookie Flask")
    parser_brute.add_argument("-w", "--wordlist", required=True, help="Fichier wordlist contenant des clés possibles")

    args = parser.parse_args()

    if args.subcommand == "encode":
        result = FSCM.encode(args.secret_key, args.cookie_structure)
        print(result)

    elif args.subcommand == "decode":
        result = FSCM.decode(args.cookie_value, args.secret_key)
        print(result)

    elif args.subcommand == "guess":
        guess_from_url(args.url, args.secret_key)

    elif args.subcommand == "bruteforce":
        bruteforce_secret_key(args.cookie_value, args.wordlist)

    else:
        parser.print_help()
