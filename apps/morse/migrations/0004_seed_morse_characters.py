"""Seed do alfabeto Morse (ITU-R M.1677-1): letras, números e pontuação."""

from django.db import migrations

LETTERS = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}

NUMBERS = {
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}

PUNCTUATION = {
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "'": ".----.",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "$": "...-..-",
    "@": ".--.-.",
}


def seed_characters(apps, _schema_editor):
    morse_character = apps.get_model("morse", "MorseCharacter")
    for type_name, table in (
        ("letter", LETTERS),
        ("number", NUMBERS),
        ("punctuation", PUNCTUATION),
    ):
        for character, code in table.items():
            morse_character.objects.get_or_create(
                character=character, defaults={"code": code, "type": type_name}
            )


def unseed_characters(apps, _schema_editor):
    morse_character = apps.get_model("morse", "MorseCharacter")
    all_characters = [*LETTERS, *NUMBERS, *PUNCTUATION]
    morse_character.objects.filter(character__in=all_characters).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("morse", "0003_morsecharacter"),
    ]

    operations = [
        migrations.RunPython(seed_characters, unseed_characters),
    ]
