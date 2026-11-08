from pathlib import Path
import subprocess,base64
root=Path(__file__).resolve().parent
subprocess.run(['npx','--yes','esbuild',str(root/'scroll-film.js'),'--bundle','--minify','--format=iife','--outfile='+str(root/'scroll-film.bundle.js')],check=True)
s=(root/'scroll-film.html').read_text()
for key,f in [('__FONTS__','fonts-inline.css'),('__CSS__','scroll-film.css'),('__SCRIPT__','scroll-film.bundle.js')]: s=s.replace(key,(root/f).read_text())
s=s.replace('__IMAGE__','data:image/jpeg;base64,'+base64.b64encode((root/'wave.jpg').read_bytes()).decode())
(root/'hokusai-scroll-film.html').write_text(s)
