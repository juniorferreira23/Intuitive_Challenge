import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import requests
from bs4 import BeautifulSoup
from io import StringIO
import zipfile

from scripts.scraper_gov_docs import (
    fetch_page,
    parse_files,
    dowload_file,
    compress_file,
    main,
)


class TesteGovDocs(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_page_success(self, mock_get):
        """Testa o sucesso na obtenção do conteúdo HTML"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test content</html>"
        mock_get.return_value = mock_response

        result = fetch_page("http://test.com")
        self.assertEqual(result, "<html>Test content</html>")
        mock_get.assert_called_once_with("http://test.com")

    @patch("requests.get")
    def test_fetch_page_failure(self, mock_get):
        """Testa a falha na requisição HTTP"""
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        result = fetch_page("http://test.com")
        self.assertIsNone(result)

    def test_parse_files_with_tag_content(self):
        """Testa a extração de links com conteúdo de tag específico"""
        html = """
        <html>
            <a href="file1.pdf">Anexo I</a>
            <a href="file2.pdf">Anexo II</a>
            <a href="image.png">Not a PDF</a>
        </html>
        """
        result = parse_files(html, tag_content="Anexo", target_file=".pdf")
        self.assertEqual(result, ["file1.pdf", "file2.pdf"])

    def test_parse_files_with_class_content(self):
        """Testa a extração de links com classe específica"""
        html = """
        <html>
            <a class="pdf-link" href="file1.pdf">Link 1</a>
            <a class="other" href="file2.pdf">Link 2</a>
            <a class="pdf-link" href="image.png">Not PDF</a>
        </html>
        """
        result = parse_files(html, class_content="pdf-link", target_file=".pdf")
        self.assertEqual(result, ["file1.pdf"])

    def test_parse_files_with_invalid_params(self):
        """Testa o erro quando tag_content e class_content são usados juntos"""
        with self.assertRaises(ValueError):
            parse_files("<html></html>", tag_content="test", class_content="test")

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_file_success(self, mock_file, mock_get):
        """Testa o download bem-sucedido de um arquivo"""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"test data"]
        mock_get.return_value.__enter__.return_value = mock_response

        dowload_file("http://test.com/file.pdf", "./downloads")

        mock_get.assert_called_once_with("http://test.com/file.pdf", stream=True)
        mock_file.assert_called_once_with("./downloads/file.pdf", "wb")

    @patch("os.listdir")
    @patch("zipfile.ZipFile")
    def test_compress_file_with_types(self, mock_zip, mock_listdir):
        """Testa a compressão bem-sucedida de arquivos com tipos de arquivo específicos"""
        mock_listdir.return_value = ["file1.pdf", "file2.txt", "file3.pdf"]

        with patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            compress_file("./downloads", "./output.zip", file_types=[".pdf"])

        mock_zip.assert_called_once_with("./output.zip", "w")
        self.assertEqual(
            mock_zip.return_value.__enter__.return_value.write.call_count, 2
        )

    @patch("os.listdir")
    @patch("zipfile.ZipFile")
    def test_compress_file_success(self, mock_zip, mock_listdir):
        """Testa a compressão bem-sucedida de arquivos sem especificar tipos"""
        mock_listdir.return_value = ["file1.pdf", "file2.txt", "file3.pdf"]

        with patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            compress_file("./downloads", "./output.zip")

        mock_zip.assert_called_once_with("./output.zip", "w")
        self.assertEqual(
            mock_zip.return_value.__enter__.return_value.write.call_count, 3
        )

    @patch("os.listdir")
    @patch("zipfile.ZipFile")
    def test_compress_file_no_matching_files(self, mock_zip, mock_listdir):
        """Testa a compressão sem arquivos que correspondem aos tipos especificados"""
        mock_listdir.return_value = ["file1.pdf", "file2.txt", "file3.pdf"]

        with patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            result = compress_file("./downloads", "./output.zip", file_types=[".jpg"])

        mock_zip.assert_not_called()
        self.assertIsNone(result)

    @patch("os.listdir")
    def test_compress_file_empty_dir_with_types(self, mock_listdir):
        """Testa a tentativa de compressão de diretório vazio com tipos específicos"""
        mock_listdir.return_value = []

        result = compress_file("./empty", "./output.zip", file_types=[".txt"])
        self.assertIsNone(result)

    @patch("os.listdir")
    def test_compress_file_empty_dir(self, mock_listdir):
        """Testa a tentativa de compressão de diretório vazio sem tipos especificados"""
        mock_listdir.return_value = []

        result = compress_file("./empty", "./output.zip")
        self.assertIsNone(result)


    @patch("scripts.scraper_gov_docs.fetch_page")
    @patch("scripts.scraper_gov_docs.parse_files")
    @patch("scripts.scraper_gov_docs.dowload_file")
    @patch("scripts.scraper_gov_docs.compress_file")
    @patch("os.makedirs")
    def test_main_success_flow(
        self, mock_makedirs, mock_compress, mock_download, mock_parse, mock_fetch
    ):
        """Testa o fluxo principal bem-sucedido"""
        mock_fetch.return_value = "<html>content</html>"
        mock_parse.return_value = ["file1.pdf", "file2.pdf"]

        main("http://test.com", "./downloads", "./output.zip")

        mock_fetch.assert_called_once_with("http://test.com")
        mock_parse.assert_called_once_with(
            "<html>content</html>", tag_content=".*Anexo*.", target_file=".pdf"
        )
        mock_makedirs.assert_called_once_with("./downloads", exist_ok=True)
        self.assertEqual(mock_download.call_count, 2)
        mock_compress.assert_called_once_with("./downloads", "./output.zip", [".pdf"])

    @patch("scripts.scraper_gov_docs.fetch_page")
    def test_main_fetch_failure(self, mock_fetch):
        """Testa o fluxo principal quando o fetch falha"""
        mock_fetch.return_value = None

        main("http://test.com", "./downloads", "./output.zip")

        mock_fetch.assert_called_once_with("http://test.com")

    @patch("scripts.scraper_gov_docs.fetch_page")
    @patch("scripts.scraper_gov_docs.parse_files")
    def test_main_no_files_found(self, mock_parse, mock_fetch):
        """Testa o fluxo principal quando nenhum arquivo é encontrado"""
        mock_fetch.return_value = "<html>content</html>"
        mock_parse.return_value = []

        main("http://test.com", "./downloads", "./output.zip")

        mock_fetch.assert_called_once_with("http://test.com")
        mock_parse.assert_called_once_with(
            "<html>content</html>", tag_content=".*Anexo*.", target_file=".pdf"
        )


if __name__ == "__main__":
    unittest.main()
