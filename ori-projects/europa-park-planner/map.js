const rides=window.ATTRACTIONS||[];
const API_BASE='/europa-park-planner-api';
const areaNames={Abenteuerland:'ארץ ההרפתקאות',Deutschland:'גרמניה',England:'אנגליה',Frankreich:'צרפת',Griechenland:'יוון','Grimms Märchenwald':'יער האגדות של גרים',Holland:'הולנד',Irland:'אירלנד',Island:'איסלנד',Italien:'איטליה',Kroatien:'קרואטיה','Königreich der Minimoys':'ממלכת המינימויים',Luxemburg:'לוקסמבורג',Monaco:'מונקו',Portugal:'פורטוגל',Russland:'רוסיה',Schweiz:'שווייץ',Skandinavien:'סקנדינביה',Spanien:'ספרד','Österreich':'אוסטריה'};
const $=id=>document.getElementById(id);
const esc=value=>String(value||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
const areaHe=value=>areaNames[value]||value;
let profile=null,selections={},mapQuery='',chosenOnly=false,filterTouched=false,parkMap=null;
const markers=new Map();
try{profile=JSON.parse(localStorage.getItem('europa-active-profile'))}catch{}
if(profile?.id){try{selections=JSON.parse(localStorage.getItem(`europa-profile-${profile.id}-selections`))||{}}catch{}}
const selected=id=>Boolean(selections[id]);
function useChosenDefault(){if(filterTouched)return;chosenOnly=Object.values(selections).some(Boolean);$('mapChosenOnly').checked=chosenOnly}
function popup(ride){const [lat,lon]=window.ATTRACTION_LOCATIONS[ride.id];return`<div class="map-pin-popup"><img src="${ride.image}" alt=""><strong>${esc(ride.name)}</strong><span>${esc(areaHe(ride.area))} · פחד ${ride.fear}/5</span><div class="map-popup-actions"><a href="index.html?ride=${encodeURIComponent(ride.id)}#catalog">לכרטיס המתקן</a><a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}" target="_blank" rel="noopener">ניווט</a></div></div>`}
function refresh(){if(!parkMap)return;let visible=0;for(const [id,marker] of markers){const ride=marker.ride,text=`${ride.name} ${ride.area} ${areaHe(ride.area)}`.toLowerCase(),show=(!mapQuery||text.includes(mapQuery))&&(!chosenOnly||selected(id));if(show){if(!parkMap.hasLayer(marker))marker.addTo(parkMap);marker.setStyle({fillColor:selected(id)?'#ffc928':'#1268d7',color:selected(id)?'#071d49':'#fff'});marker.setRadius(selected(id)?9:7);visible++}else if(parkMap.hasLayer(marker))parkMap.removeLayer(marker)}$('mapStatus').textContent=`מציג ${visible} מתוך ${rides.length} מתקנים${chosenOnly?' שבחרת':''}`}
function focusRequested(){const id=new URLSearchParams(location.search).get('ride'),marker=markers.get(id);if(!marker)return;if(chosenOnly&&!selected(id)){chosenOnly=false;$('mapChosenOnly').checked=false;refresh()}parkMap.setView(marker.getLatLng(),19,{animate:true});marker.openPopup()}
function init(){const locations=window.ATTRACTION_LOCATIONS||{};if(!window.L||!Object.keys(locations).length){$('mapStatus').textContent='המפה לא נטענה. בדקו את החיבור ונסו לרענן.';return}parkMap=L.map('parkMap',{zoomControl:true,minZoom:16,maxZoom:20,scrollWheelZoom:false}).setView([48.265,7.721],17);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:20,attribution:'&copy; OpenStreetMap contributors'}).addTo(parkMap);const bounds=[];rides.forEach(ride=>{const coords=locations[ride.id];if(!coords)return;const marker=L.circleMarker(coords,{radius:7,weight:2,color:'#fff',fillColor:'#1268d7',fillOpacity:.95}).bindPopup(popup(ride),{maxWidth:240});marker.ride=ride;markers.set(ride.id,marker);marker.addTo(parkMap);bounds.push(coords)});parkMap.fitBounds(bounds,{padding:[24,24]});refresh();setTimeout(focusRequested,300)}
async function syncProfile(){if(!profile?.name)return;try{const response=await fetch(`${API_BASE}/profile`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:profile.name}),cache:'no-store'});if(!response.ok)return;const data=await response.json();profile={id:data.id,name:data.name};selections={...(data.selections||{})};localStorage.setItem('europa-active-profile',JSON.stringify(profile));localStorage.setItem(`europa-profile-${profile.id}-selections`,JSON.stringify(selections));useChosenDefault();refresh()}catch{}}
$('mapSearch').addEventListener('input',event=>{mapQuery=event.target.value.trim().toLowerCase();refresh()});
$('mapChosenOnly').addEventListener('change',event=>{filterTouched=true;chosenOnly=event.target.checked;refresh()});
useChosenDefault();
init();
syncProfile();
