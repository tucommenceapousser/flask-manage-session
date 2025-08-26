# Flask Session Cookie Decoder/Encoder ++
**Enhanced by trhacknon**  

---

## Description

FSCM est un outil avancé pour **encoder, décoder et bruteforcer les cookies de session Flask**.

Il permet de :

- Encoder une structure Python/JSON en cookie Flask.
- Décoder un cookie Flask avec ou sans la `secret_key`.
- Essayer de deviner un cookie depuis une URL.
- Bruteforcer la `secret_key` à partir d’un cookie et d’un wordlist.

Idéal pour des démonstrations ou tests de sécurité de sessions Flask.

---

## Installation

```bash
git clone https://github.com/tucommenceapousser/flask-manage-session.git
cd flask-manage-session
pip install -r requirements.txt
```

### Requirements :
```bash
Flask
itsdangerous
rich
requests
```


---

Usage CLI

```bash
python3 fscm.py <subcommand> [options]
```

1️⃣ Encode un cookie Flask

```bash
python3 fscm.py encode -s SECRET_KEY -t '{"user_id": 1, "admin": false}'
```
-s : La secret_key Flask.
-t : La structure du cookie (dict Python / JSON / "auto" pour mode interactif).

---

2️⃣ Décoder un cookie Flask

```bash
python3 fscm.py decode -c COOKIE_VALUE [-s SECRET_KEY]
```

-c : Le cookie Flask à décoder.
-s : La secret_key Flask (optionnelle).

---

3️⃣ Deviner un cookie depuis une URL

```bash
python3 fscm.py guess --url https://exemple.com [-s SECRET_KEY]
```

Tente de récupérer le cookie session depuis l’URL et de le décoder.



---

4️⃣ Bruteforce la secret_key

```bash
python3 fscm.py bruteforce -c COOKIE_VALUE -w wordlist.txt
```

-c : Le cookie Flask.
-w : Fichier wordlistcontenant des clés possibles.

---

## Mode interactif

Si vous utilisez "auto" comme structure de cookie pour encode, un assistant interactif vous guidera pour construire la structure clé/valeur.


---

Exemple rapide

```bash
python3 fscm.py encode -s mysecret -t "auto"
```

# -> Mode interactif

```bash
python3 fscm.py decode -c eyJ1c2VyX2lkIjoxfQ== -s mysecret
python3 fscm.py bruteforce -c eyJ1c2VyX2lkIjoxfQ== -w keys.txt
```

---

Auteurs & Licence
Wilson Sumanang
Alexandre ZANNI
Enhancements: trhacknon
Licence : MIT
