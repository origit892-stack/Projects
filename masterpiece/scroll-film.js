import * as THREE from 'three';
import {keys,beats} from './film-timeline.js';
import {startSoftwareFilm} from './film-software.js';
const $=id=>document.getElementById(id),reduce=matchMedia('(prefers-reduced-motion: reduce)');
const clamp=THREE.MathUtils.clamp,lerp=THREE.MathUtils.lerp,smooth=(a,b,x)=>THREE.MathUtils.smoothstep(x,a,b);
const source=$('original-art').src;
let renderer;try{renderer=new THREE.WebGLRenderer({canvas:$('world'),antialias:true,powerPreference:'high-performance'});}catch(e){startSoftwareFilm(source);window.__graphicsFallbackReason=e.message;}
if(renderer){
const gl=renderer.getContext(),debug=gl.getExtension('WEBGL_debug_renderer_info'),software=debug&&/swiftshader|llvmpipe|software/i.test(gl.getParameter(debug.UNMASKED_RENDERER_WEBGL));renderer.setPixelRatio(software?.75:Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.08,180);camera.position.set(0,0,12);
const world=new THREE.Group();scene.add(world);
const texture=new THREE.TextureLoader().load(source,()=>{dirty=true;document.body.classList.add('ready');$('loading').hidden=true;});texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=renderer.capabilities.getMaxAnisotropy();
// Studio reflections: broad windows, a soft ceiling and a dark floor.
const envCanvas=document.createElement('canvas');envCanvas.width=512;envCanvas.height=256;const ec=envCanvas.getContext('2d'),eg=ec.createLinearGradient(0,0,0,256);eg.addColorStop(0,'#faf5ee');eg.addColorStop(.46,'#9cbdca');eg.addColorStop(.55,'#354859');eg.addColorStop(1,'#111824');ec.fillStyle=eg;ec.fillRect(0,0,512,256);
for(const [x,w,c] of [[40,65,'#fff9e9'],[220,25,'#ffffff'],[345,90,'#b4eef7']]){let g=ec.createLinearGradient(x-12,0,x+w+12,0);g.addColorStop(0,'#ffffff00');g.addColorStop(.18,c);g.addColorStop(.82,c);g.addColorStop(1,'#ffffff00');ec.fillStyle=g;ec.fillRect(x-12,25,w+24,165)}
const env=new THREE.CanvasTexture(envCanvas);env.mapping=THREE.EquirectangularReflectionMapping;env.colorSpace=THREE.SRGBColorSpace;const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromEquirectangular(env).texture;pmrem.dispose();
const hemi=new THREE.HemisphereLight('#ffffff','#345368',2.4);scene.add(hemi);const key=new THREE.DirectionalLight('#fff4e3',3.3);key.position.set(-5,8,10);scene.add(key);const rim=new THREE.DirectionalLight('#c6fdff',3);rim.position.set(5,1,-5);scene.add(rim);
const uniforms={morph:{value:0},paper:{value:1},bend:{value:0},phase:{value:0}};
const shapeCode=`
uniform float morph;uniform float bend;uniform float phase;
const float PI=3.14159265359;
vec3 knotCenter(float a){float r=2.0+.65*cos(a*3.);return vec3(r*cos(a*2.),r*sin(a*2.),.9*sin(a*3.));}
vec3 shapeAt(vec2 uv,float kind){float u=uv.x,v=uv.y,a=u*2.*PI,b=v*2.*PI;vec3 p;
if(kind<.5){p=vec3((u-.5)*9.,(v-.5)*6.156,sin(u*PI)*sin(v*PI)*bend);}
else if(kind<1.5){float q=-PI*.5+v*4.4,r=2.1+.4*sin(u*PI);p=vec3((u-.5)*7.4,sin(q)*r+.18*sin(u*8.),-cos(q)*r);}
else if(kind<2.5){float r=2.15+.64*cos(b);p=vec3(r*cos(a),r*sin(a),.64*sin(b));}
else if(kind<3.5){float q=v*PI,rr=2.22*(1.+.12*sin(a*3.+phase)*sin(q*2.)+.07*cos(a*5.-q*3.));p=vec3(cos(a)*sin(q)*rr,cos(q)*rr,sin(a)*sin(q)*rr);}
else if(kind<4.5){vec3 c=knotCenter(a),t=normalize(knotCenter(a+.005)-knotCenter(a-.005)),n=normalize(cross(t,vec3(0.,0.,1.))),binormal=normalize(cross(t,n));p=c+.38*(cos(b)*n+sin(b)*binormal);}
else {p=vec3((u-.5)*9.,(v-.5)*6.156,sin(u*PI*2.+phase*.2)*sin(v*PI)*bend);}
return p;}
vec3 shape(vec2 uv){float i=min(4.,floor(morph));float f=morph-i;return mix(shapeAt(uv,i),shapeAt(uv,i+1.),f);}
`;
const material=new THREE.MeshPhysicalMaterial({color:'#ffffff',map:texture,metalness:0,roughness:.55,clearcoat:1,clearcoatRoughness:.12,side:THREE.DoubleSide,envMapIntensity:1.25});
material.onBeforeCompile=shader=>{shader.uniforms.morph=uniforms.morph;shader.uniforms.bend=uniforms.bend;shader.uniforms.phase=uniforms.phase;shader.uniforms.paper=uniforms.paper;
shader.vertexShader=shapeCode+shader.vertexShader;
shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>',`vec2 normalUV=clamp(uv,vec2(.0005),vec2(.9995));vec3 dx=shape(normalUV+vec2(.0002,0.))-shape(normalUV-vec2(.0002,0.));vec3 dy=shape(normalUV+vec2(0.,.0002))-shape(normalUV-vec2(0.,.0002));vec3 objectNormal=normalize(cross(dx,dy)+vec3(0.,0.,.0000001));`);
shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','vec3 transformed=shape(uv);');
shader.fragmentShader='uniform float paper;\n'+shader.fragmentShader;
shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#ifdef USE_MAP\nvec4 sampledDiffuseColor=texture2D(map,vMapUv);diffuseColor*=mix(vec4(1.),sampledDiffuseColor,paper);\n#endif`);
};
const mesh=new THREE.Mesh(new THREE.PlaneGeometry(9,6.156,96,72),material);mesh.frustumCulled=false;world.add(mesh);
// Hundreds of tiles become a spiral, then assemble into the original image.
const cols=18,rows=12,tileG=new THREE.PlaneGeometry(9/cols,6.156/rows),offsets=[],tiles=[];
for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){offsets.push(i/cols,(rows-j-1)/rows);tiles.push({x:(i+.5)*9/cols-4.5,y:3.078-(j+.5)*6.156,a:Math.random()*Math.PI*2,r:Math.random(),i,j});}
tileG.setAttribute('offset',new THREE.InstancedBufferAttribute(new Float32Array(offsets),2));
const tileM=new THREE.ShaderMaterial({uniforms:{map:{value:texture},opacity:{value:1}},transparent:true,side:THREE.DoubleSide,vertexShader:`attribute vec2 offset;varying vec2 vUv;void main(){vUv=uv/vec2(18.,12.)+offset;gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);}`,fragmentShader:`uniform sampler2D map;uniform float opacity;varying vec2 vUv;void main(){gl_FragColor=vec4(texture2D(map,vUv).rgb,opacity);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`});
const tileMesh=new THREE.InstancedMesh(tileG,tileM,tiles.length);tileMesh.frustumCulled=false;scene.add(tileMesh);const dummy=new THREE.Object3D();
const sparkCanvas=document.createElement('canvas');sparkCanvas.width=sparkCanvas.height=32;const cx=sparkCanvas.getContext('2d'),gr=cx.createRadialGradient(16,16,0,16,16,16);gr.addColorStop(0,'#fff');gr.addColorStop(.25,'#ffffffdd');gr.addColorStop(1,'#ffffff00');cx.fillStyle=gr;cx.fillRect(0,0,32,32);const sparkTexture=new THREE.CanvasTexture(sparkCanvas);
const particleN=1800,particleP=new Float32Array(particleN*3),particleSeeds=Array.from({length:particleN},()=>({a:Math.random()*6.28,r:Math.random()*8+.4,z:(Math.random()-.5)*24}));const particleG=new THREE.BufferGeometry();particleG.setAttribute('position',new THREE.BufferAttribute(particleP,3));const particleM=new THREE.PointsMaterial({map:sparkTexture,size:.048,color:'#fff7e3',transparent:true,opacity:.6,depthWrite:false,alphaTest:.01});const particles=new THREE.Points(particleG,particleM);scene.add(particles);
const orbit=new THREE.Group();const orbitM=new THREE.MeshStandardMaterial({color:'#eadaad',metalness:.8,roughness:.21});for(let k=0;k<3;k++){const points=[];for(let i=0;i<=180;i++){const a=i/180*Math.PI*4.2;points.push(new THREE.Vector3(Math.cos(a)*(4+k*.32),Math.sin(a)*(4+k*.32),i/180*15-7.5));}const m=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),180,.016,5,false),orbitM);m.rotation.set(k*.5,k*.7,0);orbit.add(m)}scene.add(orbit);
// Every keyframe is sampled from scroll position, including shape, scale and colour.

let target=0,p=0,last=performance.now(),time=0,paused=reduce.matches,quality=false,slow=0,frames=0;const pointer=new THREE.Vector2();let oldBeat=-1,dirty=true;
function scroll(){target=clamp(scrollY/(Math.max(innerHeight,1)*1.25),0,8);$('progress').style.transform=`scaleX(${target/8})`;$('scroll-number').textContent=Math.round(target/8*100).toString().padStart(2,'0')+'%';}
addEventListener('scroll',scroll,{passive:true});addEventListener('pointermove',e=>{pointer.set(e.clientX/innerWidth*2-1,e.clientY/innerHeight*2-1);dirty=true});
function resize(){dirty=true;camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);scroll()}addEventListener('resize',resize);resize();
function go(v){window.scrollTo({top:v*innerHeight*1.25,behavior:reduce.matches?'instant':'smooth'})}document.querySelectorAll('[data-position]').forEach(b=>b.onclick=()=>go(Number(b.dataset.position)));$('start').onclick=()=>go(1);$('restart').onclick=()=>go(0);$('next').onclick=()=>go(Math.min(8,Math.floor(p+.4)+1));$('show-story').onclick=()=>story.showModal();$('open-story-end').onclick=()=>story.showModal();
function syncPause(){dirty=true;$('pause').textContent=paused?'▶ תנועה':'Ⅱ תנועה';$('pause').setAttribute('aria-pressed',String(paused));document.body.classList.toggle('paused',paused)}$('pause').onclick=()=>{paused=!paused;syncPause()};reduce.addEventListener('change',e=>{paused=e.matches;syncPause()});syncPause();
$('quality').onclick=()=>{quality=!quality;renderer.setPixelRatio(quality?Math.min(devicePixelRatio,1.75):1);$('quality').textContent=quality?'איכות גבוהה':'איכות רגילה';$('quality').setAttribute('aria-pressed',String(quality));resize()};
let audio,gain,sound=false;$('sound').onclick=()=>{if(!audio){audio=new(window.AudioContext||window.webkitAudioContext)();const b=audio.createBuffer(1,audio.sampleRate*4,audio.sampleRate),d=b.getChannelData(0);let n=0;for(let i=0;i<d.length;i++){n=(n+(Math.random()-.5)*.025)*.983;d[i]=n*4}const src=audio.createBufferSource();src.buffer=b;src.loop=true;gain=audio.createGain();gain.gain.value=0;const filter=audio.createBiquadFilter();filter.type='lowpass';filter.frequency.value=500;src.connect(filter).connect(gain).connect(audio.destination);src.start()}audio.resume();sound=!sound;gain.gain.setTargetAtTime(sound?.22:0,audio.currentTime,.5);$('sound').textContent=sound?'♫ צליל פועל':'♫ צלילי ים';$('sound').setAttribute('aria-pressed',String(sound))};
const bg=new THREE.Color(),colour=new THREE.Color(),sample=Array(15).fill(0);
function animate(now){requestAnimationFrame(animate);if(software&&now-last<50)return;let gap=now-last,dt=clamp(gap/1000,0,.1);last=now;if(document.hidden)return;if(!dirty&&Math.abs(p-target)<.00002)return;dirty=false;if(!paused)time+=dt;p=reduce.matches?target:lerp(p,target,1-Math.exp(-dt*10));if(Math.abs(p-target)<.00002)p=target;let index=0;while(index<keys.length-2&&p>keys[index+1][0])index++;const a=keys[index],b=keys[index+1],linear=clamp((p-a[0])/(b[0]-a[0]),0,1),f=linear*linear*(3-2*linear);for(let j=1;j<15;j++){if(j===10||j===11)continue;sample[j]=lerp(a[j],b[j],f)}
const mobile=innerWidth<760;
uniforms.morph.value=sample[1];uniforms.paper.value=sample[9];uniforms.bend.value=sample[13];uniforms.phase.value=p*1.7;
colour.set(a[10]).lerp(new THREE.Color(b[10]),f);material.color.copy(colour);material.metalness=sample[14];material.roughness=lerp(.17,.8,sample[9]);material.clearcoat=1-sample[9]*.8;
bg.set(a[11]).lerp(new THREE.Color(b[11]),f);scene.background=bg;document.documentElement.style.setProperty('--scene',bg.getStyle());
const mobileFit=mobile?lerp(.56,1,smooth(.65,1.5,p))*(1-.44*smooth(7,7.5,p)):1;world.scale.setScalar(sample[2]*mobileFit);world.position.set(sample[3]*(mobile?.5:1),sample[4],sample[5]);world.rotation.set(sample[6]+(paused?0:pointer.y*.045),sample[7]+(paused?0:pointer.x*.07),sample[8]);
mesh.visible=!(p>5.9&&p<7.05);camera.position.set(0,0,sample[12]*(mobile?1.25:1));camera.lookAt(0,.4,0);camera.fov=42+(Math.sin(p*Math.PI)*2);camera.updateProjectionMatrix();
// In the final passage paper fragments coil towards the camera, then lock in place.
const tilesOn=p>5.6&&p<7.4;tileMesh.visible=tilesOn;if(tilesOn){const explode=smooth(5.6,5.98,p)*(1-smooth(6.45,7.35,p));const turn=smooth(5.6,6.6,p)*Math.PI*3;tiles.forEach((s,i)=>{const angle=s.a+turn+(s.i/cols)*Math.PI*2;const radius=2.5+s.r*4;dummy.position.set(lerp(s.x,Math.cos(angle)*radius,explode),lerp(s.y+.8,Math.sin(angle)*radius*.75,explode),explode*(Math.sin(angle+s.j*.3)*7));dummy.rotation.set(explode*(s.r-.5)*4,explode*angle,explode*angle*.35);dummy.scale.setScalar(lerp(1,1.5,explode));dummy.updateMatrix();tileMesh.setMatrixAt(i,dummy.matrix)});tileMesh.instanceMatrix.needsUpdate=true;tileMesh.scale.setScalar(mobile?.65:1);tileM.uniforms.opacity.value=smooth(5.6,5.95,p)*(1-smooth(7.04,7.4,p));}
const orbitOn=smooth(1.3,1.8,p)*(1-smooth(2.3,2.8,p))+smooth(4.05,4.5,p)*(1-smooth(5.6,6.05,p));orbit.visible=orbitOn>.01;orbit.scale.setScalar(orbitOn*.75);orbit.rotation.set(p*.5,p*1.7,p*.7);orbitM.color.copy(colour).lerp(new THREE.Color('#fff2bd'),.4);
particles.visible=p>.65&&p<7.15;particleM.opacity=.3+Math.sin(p*.5)*.18;particleM.color.set(p>4&&p<5.65?'#ffe6b5':'#eefff7');for(let i=0;i<particleN;i++){const s=particleSeeds[i],angle=s.a+p*.8;particleP[i*3]=Math.cos(angle)*s.r;particleP[i*3+1]=Math.sin(angle)*s.r*.7;particleP[i*3+2]=s.z+Math.sin(angle)*3+Math.sin(p*.8)*1.5}particleG.attributes.position.needsUpdate=true;
let beatIndex=beats.findIndex(x=>p>=x.a&&p<=x.b);const beat=beats[beatIndex];if(beatIndex!==oldBeat){oldBeat=beatIndex;if(beat){$('kinetic-kicker').textContent=beat.k;$('kinetic-title').textContent=beat.title;$('kinetic-desc').textContent=beat.desc;$('words').dataset.side=beat.side;$('words').classList.toggle('opening',beat.side==='start');$('start').hidden=beat.side!=='start';$('open-story-end').hidden=beat.side!=='end';}}
if(beat){const local=(p-beat.a)/(beat.b-beat.a),enter=smooth(0,.18,local),exit=1-smooth(.77,1,local);const opacity=beat.side==='start'?exit:enter*exit;const scale=beat.side==='start'?lerp(1,1.25,local):lerp(.72,1.26,smooth(0,1,local));const x=beat.side==='left'?lerp(-130,80,local):beat.side==='right'?lerp(140,-80,local):lerp(0,-50,local);$('words').style.opacity=opacity;$('words').style.transform=`translate3d(${mobile?x*.25:x}px,${lerp(50,-55,local)}px,0) scale(${scale})`; $('words').style.visibility=opacity<.025?'hidden':'visible';}else{$('words').style.opacity=0;$('words').style.visibility='hidden'}
const dark=(p>3.9&&p<7.0);document.body.classList.toggle('dark',dark);$('next').style.opacity=p>.1&&p<7.85?1:0;$('next').style.pointerEvents=p>.1&&p<7.85?'auto':'none';document.querySelectorAll('[data-position]').forEach(el=>el.classList.toggle('active',Math.abs(Number(el.dataset.position)-p)<.6));
renderer.render(scene,camera);frames++;if(gap>95&&frames>20){slow++;if(slow>20&&renderer.getPixelRatio()>.75){renderer.setPixelRatio(.75);resize();$('quality').textContent='איכות רגילה';quality=false}}else slow=Math.max(0,slow-1);
}requestAnimationFrame(animate);
window.__film={renderer,scene,world,uniforms,camera,get progress(){return p},get scrollTarget(){return target},keys};
}
const story=$('story-dialog');$('close-story').onclick=()=>story.close();story.addEventListener('click',e=>{if(e.target===story)story.close()});$('show-story').onclick=()=>story.showModal();$('open-story-end').onclick=()=>story.showModal();
