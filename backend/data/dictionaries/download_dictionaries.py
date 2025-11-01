"""
Script to download SymSpell dictionaries for multiple languages.
Run this script once to set up the dictionaries.
"""

from pathlib import Path

# This script now verifies dictionaries are present in the local directory
# instead of downloading them from remote URLs. Place all frequency
# dictionary files (word + frequency) in this directory.

DIRECTORY = Path(__file__).parent

# Expected dictionary filenames (you can add more files here). Names are
# suggestions; the loader in format_validator.py will try to load common
# filenames found here.
EXPECTED_FILES = {
    "English": "frequency_dictionary_en_82_765.txt",
    "French": "fr-100k.txt",
    "Italian": "it-100k.txt",
}

ROMANSH_NOTE = """
NOTE: Romansh dictionary not commonly available. Create a file named 'rm.txt'
in this directory with lines in the format:

    word frequency

Example:
    grazia 100
    buna 150
    savens 80

Place your custom 'rm.txt' in this directory to enable Romansh checks.
"""


def validate_local_dictionaries():
    """Check for expected dictionary files in this directory and report status."""
    print("Checking local SymSpell dictionaries in:", DIRECTORY)

    found = 0
    for lang, filename in EXPECTED_FILES.items():
        filepath = DIRECTORY / filename
        if filepath.exists():
            print(f"✓ Found {lang} dictionary: {filename}")
            found += 1
        else:
            print(f"- Missing {lang} dictionary: {filename}")
    print(
        f"\nSummary: {found} dictionaries found out of {len(EXPECTED_FILES)} expected."
    )


if __name__ == "__main__":
    validate_local_dictionaries()
