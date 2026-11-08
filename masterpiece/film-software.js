import {keys,beats} from './film-timeline.js';

// A CPU renderer keeps the same scroll film available without a WebGL context.
export function startSoftwareFilm(source){
 const $=id=>document.getElementById(id),old=$('world'),canvas=document.createElement('canvas');
 canvas.id='world';canvas.setAttribute('aria-label',old.getAttribute('aria-label'));old.replaceWith(canvas);
 const ctx=canvas.getContext('2d'),image=new Image();image.src=source;
 const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),mix=(a,b,t)=>a+(b-a)*t,ease=t=>t*t*(3-2*t),smooth=(a,b,p)=>ease(clamp((p-a)/(b-a)));
 let width=innerWidth,height=innerHeight,p=0,target=0,dirty=true,last=0,paused=false;
 const rgb=s=>s.match(/\w\w/g).map(v=>parseInt(v,16));
 const colour=(a,b,t)=>rgb(a.slice(1)).map((v,i)=>mix(v,rgb(b.slice(1))[i],t));
 const css=c=>`rgb(${c.map(Math.round).join(',')})`;
 const center=a=>{let r=2+.65*Math.cos(a*3);return [r*Math.cos(a*2),r*Math.sin(a*2),.9*Math.sin(a*3)]};
 function shape(u,v,k,bend,phase){let a=u*Math.PI*2,b=v*Math.PI*2;
  if(k===0||k===5)return [(u-.5)*9,(v-.5)*6.156,Math.sin(u*Math.PI)*Math.sin(v*Math.PI)*bend];
  if(k===1){let q=-Math.PI/2+v*4.4,r=2.1+.4*Math.sin(u*Math.PI);return [(u-.5)*7.4,Math.sin(q)*r+.18*Math.sin(u*8),-Math.cos(q)*r]}
  if(k===2){let r=2.15+.64*Math.cos(b);return [r*Math.cos(a),r*Math.sin(a),.64*Math.sin(b)]}
  if(k===3){let q=v*Math.PI,r=2.22*(1+.12*Math.sin(a*3+phase)*Math.sin(q*2)+.07*Math.cos(a*5-q*3));return [Math.cos(a)*Math.sin(q)*r,Math.cos(q)*r,Math.sin(a)*Math.sin(q)*r]}
  let c=center(a),l=center(a-.005),r=center(a+.005),t=r.map((x,i)=>x-l[i]),len=Math.hypot(...t);t=t.map(x=>x/len);let n=[t[1],-t[0],0],nl=Math.hypot(...n);n=n.map(x=>x/nl);let bi=[-t[2]*n[1],t[2]*n[0],t[0]*n[1]-t[1]*n[0]];return c.map((x,i)=>x+.38*(Math.cos(b)*n[i]+Math.sin(b)*bi[i]));
 }
 function resize(){width=innerWidth;height=innerHeight;const ratio=Math.min(devicePixelRatio,1.25);canvas.width=width*ratio;canvas.height=height*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);dirty=true;scroll()}
 function scroll(){target=clamp(scrollY/(height*1.25),0,8);dirty=true;$('progress').style.transform=`scaleX(${target/8})`;$('scroll-number').textContent=String(Math.round(target/8*100)).padStart(2,'0')+'%'}
 function go(v){scrollTo({top:v*height*1.25,behavior:'smooth'})}
 addEventListener('scroll',scroll,{passive:true});addEventListener('resize',resize);image.onload=()=>{dirty=true;$('loading').hidden=true};
 document.querySelectorAll('[data-position]').forEach(b=>b.onclick=()=>go(+b.dataset.position));$('start').onclick=()=>go(1);$('restart').onclick=()=>go(0);$('next').onclick=()=>go(Math.min(8,Math.floor(p+.4)+1));
 $('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'▶ תנועה':'Ⅱ תנועה';$('pause').setAttribute('aria-pressed',String(paused));};
 $('quality').hidden=true;$('sound').hidden=true;
 function frame(now){requestAnimationFrame(frame);if(now-last<33||(!dirty&&Math.abs(p-target)<.0001))return;const dt=Math.min(.1,(now-last)/1000);last=now;dirty=false;p=mix(p,target,1-Math.exp(-dt*10));if(Math.abs(p-target)<.0001)p=target;
  let index=0;while(index<keys.length-2&&p>keys[index+1][0])index++;const a=keys[index],b=keys[index+1],t=ease(clamp((p-a[0])/(b[0]-a[0]))),s=a.map((v,i)=>i===10||i===11?v:mix(v,b[i],t));const bg=colour(a[11],b[11],t),base=colour(a[10],b[10],t);ctx.fillStyle=css(bg);ctx.fillRect(0,0,width,height);document.documentElement.style.setProperty('--scene',css(bg));
  const mobile=width<760,fit=mobile?mix(.56,1,smooth(.65,1.5,p))*(1-.44*smooth(7,7.5,p)):1,scale=s[2]*fit,distance=s[12]*(mobile?1.25:1),focal=height/(2*Math.tan(42*Math.PI/360));
  function project(pos){let [x,y,z]=pos.map(q=>q*scale);let c=Math.cos(s[6]),sn=Math.sin(s[6]);[y,z]=[y*c-z*sn,y*sn+z*c];c=Math.cos(s[7]);sn=Math.sin(s[7]);[x,z]=[x*c+z*sn,-x*sn+z*c];c=Math.cos(s[8]);sn=Math.sin(s[8]);[x,y]=[x*c-y*sn,x*sn+y*c];x+=s[3]*(mobile?.5:1);y+=s[4]-.4;z+=s[5];const depth=Math.max(.15,distance-z);return [width/2+x*focal/depth,height/2-y*focal/depth,z,x,y]}
  if((p<.55||p>7.35)&&image.complete){const l=project([-4.5,3.078,0]),r=project([4.5,-3.078,0]);ctx.drawImage(image,l[0],l[1],r[0]-l[0],r[1]-l[1]);}
  else {
   const U=64,V=32,points=[],faces=[],k=Math.min(4,Math.floor(s[1])),m=s[1]-k;
   for(let j=0;j<=V;j++)for(let i=0;i<=U;i++){const q=shape(i/U,j/V,k,s[13],p*1.7),r=shape(i/U,j/V,k+1,s[13],p*1.7);points.push(project(q.map((v,n)=>mix(v,r[n],m))))}
   for(let j=0;j<V;j++)for(let i=0;i<U;i++){let n=j*(U+1)+i;for(const ids of [[n,n+1,n+U+1],[n+1,n+U+2,n+U+1]]){const q=ids.map(n=>points[n]);faces.push({q,z:q.reduce((v,p)=>v+p[2],0)/3})}}
   faces.sort((a,b)=>a.z-b.z);
   for(const {q} of faces){let [a,b,c]=q,ab=[b[3]-a[3],b[4]-a[4],b[2]-a[2]],ac=[c[3]-a[3],c[4]-a[4],c[2]-a[2]],n=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]],len=Math.hypot(...n)||1;n=n.map(x=>x/len);let light=.4+.45*Math.abs(n[0]*-.45+n[1]*.65+n[2]*.6),shine=Math.pow(Math.abs(n[0]*-.2+n[1]*.35+n[2]*.92),24)*.85;ctx.fillStyle=css(base.map(v=>Math.min(255,v*light+255*shine)));ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();}
   if(p>5.6&&p<7.35&&image.complete){const explode=smooth(5.6,5.98,p)*(1-smooth(6.45,7.35,p));for(let j=0;j<8;j++)for(let i=0;i<12;i++){const angle=i/12*Math.PI*2+j*.7+p*3,r=2.5+(j%3),x=mix((i+.5)*9/12-4.5,Math.cos(angle)*r,explode),y=mix(3.078-(j+.5)*6.156,Math.sin(angle)*r*.75,explode),q=project([x,y,explode*Math.sin(angle)*3]);ctx.save();ctx.translate(q[0],q[1]);ctx.rotate(explode*angle*.35);const w=focal*.75/Math.max(1,distance-q[2]);ctx.drawImage(image,i*image.naturalWidth/12,j*image.naturalHeight/8,image.naturalWidth/12,image.naturalHeight/8,-w/2,-w*.684/2,w,w*.684);ctx.restore()}}
  }
  const beat=beats.find(b=>p>=b.a&&p<=b.b),words=$('words');if(beat){$('kinetic-kicker').textContent=beat.k;$('kinetic-title').textContent=beat.title;$('kinetic-desc').textContent=beat.desc;words.dataset.side=beat.side;$('start').hidden=beat.side!=='start';$('open-story-end').hidden=beat.side!=='end';const local=(p-beat.a)/(beat.b-beat.a),opacity=(beat.side==='start'?1:smooth(0,.18,local))*(1-smooth(.77,1,local)),scale=beat.side==='start'?mix(1,1.25,local):mix(.72,1.26,smooth(0,1,local)),x=beat.side==='left'?mix(-130,80,local):beat.side==='right'?mix(140,-80,local):mix(0,-50,local);words.style.opacity=opacity;words.style.visibility=opacity<.025?'hidden':'visible';words.style.transform=`translate3d(${mobile?x*.25:x}px,${mix(50,-55,local)}px,0) scale(${scale})`;}else words.style.visibility='hidden';
  document.body.classList.toggle('dark',p>3.9&&p<7);document.querySelectorAll('[data-position]').forEach(b=>b.classList.toggle('active',Math.abs(+b.dataset.position-p)<.6));$('next').style.opacity=p>.1&&p<7.85?1:0;
 }
 resize();requestAnimationFrame(frame);window.__film={backend:'canvas2d',get progress(){return p},get scrollTarget(){return target}};
}
