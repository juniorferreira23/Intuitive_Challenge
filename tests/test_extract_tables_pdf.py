import unittest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from scripts.extract_tables_pdf import extract_tables


class TestExtractTables(unittest.TestCase):
    @patch("pdfplumber.open")
    @patch("scripts.extract_tables_pdf.log")
    def test_extract_tables(self, mock_log, mock_pdfplumber):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[["Col1", "Col2"], ["Data1", "Data2"]]]
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

        output_file = "test_output.csv"

        try:
            extract_tables("fake_path.pdf", output_file)

            self.assertTrue(os.path.exists(output_file))

            df = pd.read_csv(output_file)
            self.assertListEqual(list(df.columns), ["Col1", "Col2"])
            self.assertListEqual(df.iloc[0].tolist(), ["Data1", "Data2"])

            mock_log.info.assert_called_with("Tables extracted successfully")
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
