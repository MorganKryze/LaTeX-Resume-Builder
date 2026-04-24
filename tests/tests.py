"""Unit tests for the resume template scripts."""

import tempfile
import unittest
from pathlib import Path

from scripts.compile_latex import build_latexmk_command
from scripts.convert_and_merge import merge_pdfs, pdf_to_jpg
from scripts.load_yaml import load_options


class TestLoadOptions(unittest.TestCase):
    """Tests for load_yaml.load_options."""

    def test_valid_yaml_returns_dict(self):
        result = load_options("tests/resources/options-valid.yml")
        assert isinstance(result, dict)
        assert result["languages"] == ["english", "french"]
        assert result["paths"]["resumes"]["english"] == "examples/resume-en.tex"

    def test_empty_yaml_raises_value_error(self):
        with self.assertRaises(ValueError):
            load_options("tests/resources/options-empty.yml")

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_options("tests/resources/nonexistent.yml")

    def test_non_yaml_extension_raises_value_error(self):
        with self.assertRaises(ValueError):
            load_options("tests/resources/something.txt")

    def test_missing_paths_section_raises_value_error(self):
        with self.assertRaises(ValueError):
            load_options("tests/resources/options-missing-paths.yml")


class TestPdfToJpg(unittest.TestCase):
    """Tests for convert_and_merge.pdf_to_jpg."""

    def test_happy_path_single_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            pdf_to_jpg("tests/resources/sample.pdf", str(out))
            assert (out.parent / "out.jpg").exists()

    def test_nonexistent_pdf_raises(self):
        with self.assertRaises(FileNotFoundError):
            pdf_to_jpg("tests/resources/nonexistent.pdf", "/tmp/out")

    def test_non_pdf_input_raises(self):
        with self.assertRaises(ValueError):
            pdf_to_jpg("tests/resources/options-valid.yml", "/tmp/out")


class TestMergePdfs(unittest.TestCase):
    """Tests for convert_and_merge.merge_pdfs."""

    def test_merges_single_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "merged.pdf"
            merge_pdfs(["tests/resources/sample.pdf"], str(out))
            assert out.exists() and out.stat().st_size > 0


class TestCompileLatex(unittest.TestCase):
    """Tests for compile_latex.build_latexmk_command."""

    def test_builds_expected_command(self):
        cmd = build_latexmk_command(
            tex_file=Path("examples/resume-en.tex"),
            output_dir=Path("build"),
        )
        assert cmd[0] == "latexmk"
        assert "-pdf" in cmd
        assert "-output-directory=build" in cmd
        assert cmd[-1] == "examples/resume-en.tex"

    def test_output_dir_absolute(self):
        cmd = build_latexmk_command(
            tex_file=Path("foo.tex"),
            output_dir=Path("/tmp/out"),
        )
        assert "-output-directory=/tmp/out" in cmd


if __name__ == "__main__":
    unittest.main()
