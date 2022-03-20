# Copyright (c) 2022 Serum

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#: Used for handling builds

from pathlib import Path
import json
from jinja2 import (
    FileSystemLoader,
    Environment
)
from xhtml2pdf import pisa

class TemplateBuilder:
    pass

def get_template_by_name(
    name: str, 
    env: Path, 
    return_path: bool=False,
):
    env = Path(env)
    for f in env.glob('**/*'):
        if f.suffix == ".json":
            with open(f.absolute(), 'r') as w:
                data = json.load(w)

            tmpl_name = data.get('name', None)
            if tmpl_name and tmpl_name == name:
                _ = (f.parent / 'res' / 'layout.html')
                layout = _ if _.exists() else (f.parent / 'res' / 'index.html')
                if not layout.exists():
                    raise FileNotFoundError
                
                if return_path:
                    return str(
                        str(layout.parent / layout.name).replace('Templates\\', '')
                    ).replace('\\', '/')

                else:
                    with open(layout.absolute(), 'r') as f:
                        return f.read()

def get_all_templates(env: Path):
    env = Path(env)
    templates = []
    for f in env.glob('**/*'):
        if f.suffix == '.json':
            with open(f.absolute(), 'r') as w:
                data = json.load(w)
            
            tmpl_name = data.get('name', None)
            if tmpl_name:
                templates.append(data)
    return templates

def convert_html_to_pdf(source, output):
    with open(output, 'w+b') as f: 
        pisa.CreatePDF(
            source,
            dest=f
        )


class _Builder:
    template: Environment
    loader: FileSystemLoader

    def __init__(self, html: str, name: str, env_path: Path, **opt):
        self.env = env_path
        self.html = html
        self.tmpl_name = name
        self.opt = opt
        self.use_raw_path = opt.pop('use_raw_path', False)

        
        self.loader = FileSystemLoader(self.env.absolute())
        self.template = Environment(loader=self.loader)

    
    def render(self):
        name = get_template_by_name(self.name, self.env, True)
        tmpl = self.template.get_template(name)
        return tmpl.render(body=self.html)

class PDFBuilder(_Builder):
    def __init__(self, html: str, name: str):
        self.html = html
        self.name = name

        self.env_path = Path('./Templates')

        super().__init__(
            html=self.html,
            name=self.name,
            env_path=self.env_path
        )
    
    def export(self, output: str):
        convert_html_to_pdf(self.render(), output)
