import errno
from pathlib import Path
import shutil
import subprocess
from tempfile import mkdtemp, NamedTemporaryFile, _TemporaryFileWrapper

from bs4 import BeautifulSoup
from markdown import Markdown
import pdfkit

from rich import print

class MarkdownMermaidMunger:
    def __init__(self, md_path: str, pdf_path: str | None = None) -> None:
        self.path = Path(md_path)
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path.as_posix()} not found")
        if not self.path.suffix == ".md":
            raise ValueError(f"{self.path.as_posix()} is not markdown")
        if pdf_path:
            self.pdf_path = Path(pdf_path)
        else:
            self.pdf_path = self.path.with_suffix(".pdf")
        if self.pdf_path.exists():
            raise FileExistsError
        
    def original_images(self):
        soup = BeautifulSoup(Markdown().convert(self.path.read_text()), features="lxml")
        return [img.get('src') for img in soup.find_all("img") if img]
    
    def materialize(self, src: str, root: str):
        origin = self.path.parent.joinpath(src)
        tgt = NamedTemporaryFile(dir=root, prefix=origin.name, suffix=origin.suffix, delete=False)
        target = Path(tgt.name)
        shutil.copyfile(src=origin.as_posix(), dst=target.as_posix())
        return target.name
    
    def mermaid2png(self, source: Path, temp_md: _TemporaryFileWrapper) -> None:
        subprocess.run(
            [
                "npx", "-p", "@mermaid-js/mermaid-cli", "mmdc", 
                f"--input={source.as_posix()}", 
                f"--output={temp_md.name}",
                f"--outputFormat=png"
            ],
            capture_output=True
        ).check_returncode()
        
    def munge(self) -> str:
        dir = mkdtemp()
        try:
            originals = self.original_images()
            source = shutil.copyfile(src=self.path, dst=Path(dir).joinpath(self.path.name))
            temp_md = NamedTemporaryFile(dir=dir, delete=False, suffix=".md")
            self.mermaid2png(source=source, temp_md=temp_md)
            
            soup = BeautifulSoup(Markdown().convert(Path(temp_md.name).read_text()), features="lxml")
            for img in soup.find_all('img'):
                src = img.get('src')
                if  src in originals:
                    img['src'] = self.materialize(src, dir)

            tmp_html  = Path(temp_md.name).with_suffix(".html")
            with tmp_html.open("+w") as fp:
                fp.write(str(soup))
            pdfkit.from_file(
                input=tmp_html.as_posix(), 
                output_path=self.pdf_path.as_posix() ,
                options={"enable-local-file-access": True},
            )
        finally:
            try:
                shutil.rmtree(dir)  # delete directory
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise
        return self.pdf_path.as_posix()
