from pathlib import Path
import subprocess,base64
root=Path(__file__).resolve().parent
subprocess.run(['npx','--yes','esbuild',str(root/'journey.js'),'--bundle','--minify','--format=iife','--outfile='+str(root/'journey.bundle.js')],check=True)
(root/'journey-all.css').write_text((root/'scroll-film.css').read_text()+'\n'+(root/'journey.css').read_text())
s=(root/'journey.html').read_text()
for key,f in [('__FONTS__','fonts-inline.css'),('__CSS__','journey-all.css'),('__SCRIPT__','journey.bundle.js')]: s=s.replace(key,(root/f).read_text())
s=s.replace('__ASSETS__',(root/'render-assets.json').read_text() if (root/'render-assets.json').exists() else '{}')
s=s.replace('__IMAGE__','data:image/jpeg;base64,'+base64.b64encode((root/'wave.jpg').read_bytes()).decode())
(root/'hokusai-scroll-film.html').write_text(s)
(root/'hokusai-guided-journey.html').write_text(s)
