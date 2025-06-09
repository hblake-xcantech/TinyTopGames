# Tiny Top Games

A collection of simple games for my son, designed to run on an old 32-bit Acer KAV60 laptop.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the game

```bash
python main.py
```

## Notes

- Fixed window size: 1024x600 (native KAV60 res)
- Snake is manual move mode — does not auto move.
- Collisions play a *brrrp* sound but do not kill you.

## TODO

- Add more games under this window framework
