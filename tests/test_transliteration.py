import unicodedata
import unittest

from SanskritTransliteration import transliterate
from SanskritTransliteration.transliteration import (
    _CANONICAL_IDS,
    _load_table,
    _normalize_scheme,
)


class TestNormalizeScheme(unittest.TestCase):
    """Alias resolution and error handling."""

    def test_canonical_ids(self):
        for cid in _CANONICAL_IDS:
            self.assertEqual(_normalize_scheme(cid), cid)

    def test_case_insensitive(self):
        self.assertEqual(_normalize_scheme("IAST"), "iast")
        self.assertEqual(_normalize_scheme("Iso"), "iso")
        self.assertEqual(_normalize_scheme("SLP1"), "slp1")

    def test_aliases(self):
        self.assertEqual(_normalize_scheme("ISO 15919"), "iso")
        self.assertEqual(_normalize_scheme("Harvard-Kyoto"), "kh")
        self.assertEqual(_normalize_scheme("Tokunaga-Fujii"), "tf")

    def test_unknown_scheme_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _normalize_scheme("nonexistent")
        self.assertIn("nonexistent", str(ctx.exception))
        self.assertIn("Available schemes", str(ctx.exception))

    def test_tsu_excluded(self):
        with self.assertRaises(ValueError):
            _normalize_scheme("tsu")


class TestSameScheme(unittest.TestCase):
    """Same input/output scheme returns text unchanged."""

    def test_identity(self):
        text = "agním īḷe puróhitam"
        self.assertEqual(transliterate(text, "iast", "iast"), text)

    def test_identity_alias(self):
        text = "agním īḷe puróhitam"
        self.assertEqual(transliterate(text, "IAST", "iast"), text)


class TestReadmeSample(unittest.TestCase):
    """The example from README must pass."""

    def test_tf_to_iso(self):
        result = transliterate("agn;im ii;le pur;ohitam", "tf", "iso")
        self.assertEqual(result, "agním īḷe puróhitam")


class TestRegressionBugs(unittest.TestCase):
    """Specific regressions the old sequential-replace engine got wrong."""

    def test_kh_to_iast_kh(self):
        # 'kh' in KH scheme should become 'kh' in IAST, not mangled
        result = transliterate("kh", "kh", "iast")
        self.assertEqual(result, "kh")

    def test_ipa_to_iast_kh_aspirate(self):
        # kʰ (IPA) -> kh (IAST); must not collapse to kḥ
        result = transliterate("kʰ", "ipa", "iast")
        self.assertEqual(result, "kh")

    def test_jh_to_ipa(self):
        # jh (IAST) -> jʰ (IPA); old engine produced ɟʰ
        result = transliterate("jh", "iast", "ipa")
        self.assertEqual(result, "jʰ")

    def test_no_double_replacement(self):
        # 'a' should not be re-processed after first replacement
        result = transliterate("ā", "iast", "ipa")
        self.assertEqual(result, "aː")

    def test_nfd_input_matches(self):
        # NFD form of ā (a + combining macron) should match just like NFC ā
        nfd_aa = unicodedata.normalize("NFD", "ā")
        self.assertNotEqual(nfd_aa, "ā")  # confirm it's actually decomposed
        result = transliterate(nfd_aa, "iast", "ipa")
        self.assertEqual(result, "aː")


class TestAllSingleTokenPairs(unittest.TestCase):
    """For every row in the CSV, verify single-token conversion across all
    scheme pairs.  Ambiguous source tokens (same token in multiple rows for
    the same scheme) use first-win semantics."""

    @classmethod
    def setUpClass(cls):
        header, rows = _load_table()
        cls.header = header
        cls.rows = rows
        # Build first-win expectation: for each (src_scheme, dst_scheme),
        # map src_token -> expected dst_token (first row wins).
        cls.expected: dict[tuple[str, str, str], str] = {}
        for src_scheme in _CANONICAL_IDS:
            src_col = header.index(src_scheme)
            for dst_scheme in _CANONICAL_IDS:
                if src_scheme == dst_scheme:
                    continue
                dst_col = header.index(dst_scheme)
                seen_src: set[str] = set()
                for row in rows:
                    src_token = row[src_col]
                    if not src_token or src_token in seen_src:
                        continue
                    seen_src.add(src_token)
                    cls.expected[(src_scheme, dst_scheme, src_token)] = row[dst_col]

    def test_all_pairs(self):
        failures = []
        for (src_scheme, dst_scheme, src_token), expected_dst in self.expected.items():
            try:
                result = transliterate(src_token, src_scheme, dst_scheme)
            except Exception as e:
                failures.append(f"{src_scheme}->{dst_scheme}: {src_token!r} raised {e}")
                continue
            if result != expected_dst:
                failures.append(
                    f"{src_scheme}->{dst_scheme}: {src_token!r} -> "
                    f"{result!r} (expected {expected_dst!r})"
                )
        if failures:
            self.fail(
                f"{len(failures)} single-token conversion(s) failed:\n"
                + "\n".join(failures[:30])
                + ("\n..." if len(failures) > 30 else "")
            )


if __name__ == "__main__":
    unittest.main()
