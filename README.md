# Sanskrit Transliteration Tool

## Supported Transliteration Schemes

| Canonical ID | Scheme Name | Aliases |
|---|---|---|
| `iast` | IAST | `IAST` |
| `iso` | ISO 15919 | `ISO 15919`, `iso15919` |
| `kh` | Harvard-Kyoto | `Harvard-Kyoto`, `harvardkyoto` |
| `tf` | Tokunaga-Fujii | `Tokunaga-Fujii`, `tokunagafujii` |
| `slp1` | SLP1 | `SLP1` |
| `ipa` | IPA | `IPA` |
| `csx` | CSX (code point) | `CSX` |

All scheme names are case-insensitive. You can use either the canonical ID or any alias listed above.

## Usage

Install the package using pip:

```sh
pip install git+https://github.com/Yuzki/SanskritTransliteration.git
```

Import the library and use the `transliterate` function:

```python
from SanskritTransliteration import transliterate

text = "agn;im ii;le pur;ohitam"
s = transliterate(text, "tf", "iso")
print(s)
```

This will output:

```
agním īḷe puróhitam
```

Aliases work the same way:

```python
s = transliterate(text, "Tokunaga-Fujii", "ISO 15919")
print(s)  # agním īḷe puróhitam
```

## Ambiguous Reverse Mappings

When multiple CSV rows map the same source token to different targets, the first row in the table takes precedence (first-win rule).
