const P={bgA:'#F9FEF6',bgB:'#F3E8E4',paper:'#FFFFFF',ink:'#2C353A',mute:'#7A8287',faint:'#C9CFC6',teal:'#0A6E89',coral:'#FB938F',yellow:'#FED84D',lav:'#C9BCEB',purple:'#6D5BA8',red:'#E63946',green:'#1FA35B',blue:'#2F6FED',char:'#2C353A',hl:'#1D5980'};
const F={h:"'Poppins',system-ui,sans-serif",m:"'JetBrains Mono',ui-monospace,monospace"};
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
let SID=0;
const t=(x,y,s,o={})=>{const{size=15,fill=P.ink,w=400,a='start',f='h',op=1}=o;return `<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="${w}" text-anchor="${a}" font-family="${F[f]}" opacity="${op}">${esc(s)}</text>`};
const r=(x,y,w,h,o={})=>{const{fill=P.paper,stroke='none',rx=12,sw=2,dash='',op=1}=o;return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" opacity="${op}" stroke="${stroke}" stroke-width="${sw}"${dash?` stroke-dasharray="${dash}"`:''}/>`};
const ar=(d,c,o={})=>`<path d="${d}" fill="none" stroke="${c}" stroke-width="${o.sw||3}" stroke-linecap="round"${o.dash?` stroke-dasharray="${o.dash}"`:''} marker-end="url(#m${SID}-${c.slice(1)})"/>`;
const tick=(x,y,s=10)=>`<circle cx="${x}" cy="${y}" r="${s}" fill="${P.green}"/><path d="M${x-s*.45} ${y}l${s*.32} ${s*.32}l${s*.6}-${s*.62}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>`;
const icon=(x,y,name,s=56)=>`<svg x="${x}" y="${y}" width="${s}" height="${s}" viewBox="0 0 64 64">${ICONS[name]}</svg>`;
const chip=(x,y,l,c,o={})=>{const sz=o.size||22,w=Math.round(l.length*sz*.62+36),h=sz+22;return r(x-w/2,y,w,h,{fill:c,rx:h/2})+t(x,y+h/2+sz*.36,l,{f:'m',size:sz,w:600,a:'middle',fill:o.ink||P.ink})};


