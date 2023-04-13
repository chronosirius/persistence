"The base of the extension."

from .persistence import Persistence

version = {
    "version": "3.0.0",
    "authors": [
        {
            "name": "chronosirius",
            "email": "chronosirius@proton.me"
        },
        {
            "name": "Dworv",
            "email": "dwarvyt@gmail.com"
        }
    ]
}

base = {
    "name": "Persistence",
    "version": version,
    "link": "https://github.com/dworv/interactions-persistence",
    "description": "An extension to add simple custom_id encoding to interactions.py.",
    "packages": "interactions.ext.persistence",
}

def setup(bot, cipher_key=None):
    return Persistence(bot, cipher_key)
