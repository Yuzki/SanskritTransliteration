# Sanskrit Transliteration Tool

## Supported Transliteration Schemes

- IAST
- ISO 15919
- Harvard-Kyoto
- Tokunaga-Fujii
- SLP1
- IPA
- CSX (code point)

## Usage

Install the package using pip:

```sh
pip install git+https://github.com/Yuzki/SanskritTransliteration.git
```

Import the library and use the transliterate function:

```python
from SanskritTransliteration import transliterate

text = "agn;im ii;le pur;ohitam"
input = "tf"
output = "iso"
s = transliterate(text, input, output)
print(s)
```

This will output:

```sh
agním īḷe puróhitam
```
