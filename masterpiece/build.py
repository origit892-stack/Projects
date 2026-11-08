from pathlib import Path
import base64, subprocess
root=Path(__file__).resolve().parent
subprocess.run(['npx','--yes','esbuild',str(root/'scene.js'),'--bundle','--minify','--format=iife','--outfile='+str(root/'scene.bundle.js')],check=True)
s=(root/'design.html').read_text()
for key,filename in [('__CSS__','layout.css'),('__FONTS__','fonts-inline.css'),('__SCRIPT__','scene.bundle.js')]:
 s=s.replace(key,(root/filename).read_text())
s=s.replace('__IMAGE__','data:image/jpeg;base64,'+base64.b64encode((root/'wave.jpg').read_bytes()).decode())
(root/'index.html').write_text(s)
