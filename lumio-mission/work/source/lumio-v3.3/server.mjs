import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,extname,sep} from 'node:path';
const root=process.cwd(), port=Number(process.env.PORT||5173);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.json':'application/json; charset=utf-8','.webmanifest':'application/manifest+json'};
createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');let path=decodeURIComponent(url.pathname);if(path==='/'||path==='/index.html')path='/index.html';const target=resolve(root,'.'+path);if(target!==root&&!target.startsWith(root+sep))throw Error('Traversal');const s=await stat(target);if(!s.isFile())throw Error('Not file');const data=await readFile(target);res.writeHead(200,{'Content-Type':types[extname(target)]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(data);}catch{res.writeHead(404);res.end('Not found');}}).listen(port,()=>console.log(`Lumio running at http://localhost:${port}`));
