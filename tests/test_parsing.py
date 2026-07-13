import unittest
from decimal import Decimal

from growth_ab_analyzer.parsing import normalize_header, parse_money


class ParsingTest(unittest.TestCase):
    def test_parse_money_brazilian_thousands(self) -> None:
        self.assertEqual(parse_money("R$ 10.273"), Decimal("10273"))

    def test_parse_money_brazilian_decimal(self) -> None:
        self.assertEqual(parse_money("R$ 10.273,55"), Decimal("10273.55"))

    def test_normalize_header_removes_accents(self) -> None:
        self.assertEqual(normalize_header("Grupos de usu\u00e1rios"), "grupos de usuarios")


if __name__ == "__main__":
    unittest.main()
