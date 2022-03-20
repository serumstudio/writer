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

import json
import SerumWriter.Utils as Utils
from PyQt5.QtCore import QSettings

class Settings(QSettings):
    def __init__(
        self,
        org: str='Serum',
        app: str='Writer'
    ):
        super().__init__(org, app)
    
    def __getattr__(self, name: str):
        v: str = self.value(name, None)
        if isinstance(v, int):
            return v
            
        if v == None:
            return None

        if v == 'true':
            return True

        elif v == 'false':
            return False
        
        elif Utils.is_json(v):
            return json.load(v)
        
        
        return self.value(name, None)
    

    def __setattr__(self, name, value):
        return self.setValue(name, value)

