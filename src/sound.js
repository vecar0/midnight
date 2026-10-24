const Snd = {ctx:null,master:null,live:[],timer:null,cur:'none',
 ensure(){ if(!this.ctx){ this.ctx=new (window.AudioContext||window.webkitAudioContext)();
   this.master=this.ctx.createGain(); this.master.gain.value=parseFloat($('vol').value);
   this.master.connect(this.ctx.destination);} if(this.ctx.state==='suspended') this.ctx.resume(); },
 noise(){ const n=this.ctx.sampleRate*2,b=this.ctx.createBuffer(1,n,this.ctx.sampleRate),d=b.getChannelData(0);
   for(let i=0;i<n;i++) d[i]=Math.random()*2-1;
   const s=this.ctx.createBufferSource(); s.buffer=b; s.loop=true; return s; },
 stop(){ if(this.timer){clearInterval(this.timer);this.timer=null;}
   this.live.forEach(n=>{try{n.stop&&n.stop()}catch(e){}try{n.disconnect()}catch(e){}}); this.live=[]; },
 play(k){ this.stop(); this.cur=k; if(k==='none') return; this.ensure();
   ({rain:()=>this.rain(),city:()=>this.city(),white:()=>this.white(),
     clock:()=>this.clock(),piano:()=>this.piano()})[k](); },
 rain(){ const c=this.ctx,s=this.noise();
   const hp=c.createBiquadFilter();hp.type='highpass';hp.frequency.value=430;
   const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=1600;
   const g=c.createGain();g.gain.value=.5;
   s.connect(hp);hp.connect(lp);lp.connect(g);g.connect(this.master);s.start();
   const lf=c.createOscillator();lf.frequency.value=.13;
   const lg=c.createGain();lg.gain.value=380;lf.connect(lg);lg.connect(lp.frequency);lf.start();
   this.live.push(s,hp,lp,g,lf,lg); },
 city(){ const c=this.ctx,s=this.noise();
   const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=420;
   const g=c.createGain();g.gain.value=.3;
   s.connect(lp);lp.connect(g);g.connect(this.master);s.start();
   const lf=c.createOscillator();lf.type='sine';lf.frequency.value=.07;
   const lg=c.createGain();lg.gain.value=.22;lf.connect(lg);lg.connect(g.gain);lf.start();
   this.live.push(s,lp,g,lf,lg); },
 white(){ const c=this.ctx,s=this.noise();
   const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=5200;
   const g=c.createGain();g.gain.value=.26;
   s.connect(lp);lp.connect(g);g.connect(this.master);s.start(); this.live.push(s,lp,g); },
 clock(){ /* 실제 기계식 시계: 탈진기의 '틱'과 '톡'이 번갈아, 금속 울림과 작은 방 잔향 */
   const c=this.ctx;
   if(!this.room){ const len=c.sampleRate*.45, ir=c.createBuffer(2,len,c.sampleRate);
     for(let ch=0;ch<2;ch++){ const d=ir.getChannelData(ch); for(let i=0;i<len;i++) d[i]=(Math.random()*2-1)*Math.pow(1-i/len,3.2)*.6; }
     this.room=c.createConvolver(); this.room.buffer=ir; const rg=c.createGain(); rg.gain.value=.22;
     this.room.connect(rg); rg.connect(this.master); this.roomGain=rg; }
   const bus=c.createGain(); bus.gain.value=1; bus.connect(this.master); bus.connect(this.room); this.live.push(bus);
   let odd=false;
   const click=(t,pitch,amp)=>{
     // 1) 짧은 금속 타격음(노이즈를 공진 필터 두 개로)
     const n=c.createBufferSource(), len=Math.floor(c.sampleRate*.03), b=c.createBuffer(1,len,c.sampleRate), d=b.getChannelData(0);
     for(let i=0;i<len;i++) d[i]=(Math.random()*2-1)*Math.exp(-i/(c.sampleRate*.0025));
     n.buffer=b;
     const hp=c.createBiquadFilter(); hp.type='highpass'; hp.frequency.value=1200;
     const r1=c.createBiquadFilter(); r1.type='bandpass'; r1.frequency.value=3100*pitch; r1.Q.value=9;
     const r2=c.createBiquadFilter(); r2.type='bandpass'; r2.frequency.value=5200*pitch; r2.Q.value=12;
     const g=c.createGain(); g.gain.value=amp*1.6;
     n.connect(hp); hp.connect(r1); hp.connect(r2); r1.connect(g); r2.connect(g); g.connect(bus); n.start(t);
     // 2) 태엽 몸체의 낮은 '톡'
     const o=c.createOscillator(); o.type='sine'; o.frequency.setValueAtTime(190*pitch,t); o.frequency.exponentialRampToValueAtTime(95,t+.03);
     const og=c.createGain(); og.gain.setValueAtTime(amp*.35,t); og.gain.exponentialRampToValueAtTime(.0001,t+.045);
     o.connect(og); og.connect(bus); o.start(t); o.stop(t+.06);
   };
   const tick=()=>{ try{ const t=c.currentTime+.02, pitch=odd?.86:1, amp=(odd?.8:1)*(.92+Math.random()*.16);
     click(t,pitch,amp); click(t+.016+Math.random()*.004,pitch*1.12,amp*.35);   // 탈진기의 겹 클릭
     odd=!odd; }catch(e){} };
   this.timer=setInterval(tick,1000); tick(); },
 rustle(){ try{ if(!this.ctx) return; const c=this.ctx, t=c.currentTime, len=Math.floor(c.sampleRate*.5);
   const b=c.createBuffer(1,len,c.sampleRate), d=b.getChannelData(0);
   for(let i=0;i<len;i++){ const env=Math.pow(Math.sin(Math.PI*i/len),.6); d[i]=(Math.random()*2-1)*env*(Math.random()<.08?1:.35); }
   const n=c.createBufferSource(); n.buffer=b;
   const bp=c.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=2600; bp.Q.value=.7;
   const g=c.createGain(); g.gain.value=.18; n.connect(bp); bp.connect(g); g.connect(this.master); n.start(t); }catch(e){} },
 piano(){ const c=this.ctx, sc=[261.63,293.66,329.63,392,440,523.25,587.33,659.25];
   const note=()=>{ try{ const t=c.currentTime,f=sc[(Math.random()*sc.length)|0];
     const g=c.createGain(); g.gain.setValueAtTime(0,t);
     g.gain.linearRampToValueAtTime(.09,t+.012);
     g.gain.exponentialRampToValueAtTime(.0004,t+3.4);
     const lp=c.createBiquadFilter();lp.type='lowpass';
     lp.frequency.setValueAtTime(3200,t);lp.frequency.exponentialRampToValueAtTime(700,t+2.2);
     [[1,'triangle',1],[2,'sine',.3],[3,'sine',.1]].forEach(([m,ty,a])=>{
       const o=c.createOscillator();o.type=ty;o.frequency.value=f*m;
       const og=c.createGain();og.gain.value=a;
       o.connect(og);og.connect(g);o.start(t);o.stop(t+3.6);});
     g.connect(lp);lp.connect(this.master);}catch(e){} };
   this.timer=setInterval(note,2600); note(); },
 notes(l,d){ this.ensure(); const c=this.ctx;
   l.forEach((f,i)=>{ const t=c.currentTime+i*.13;
     const o=c.createOscillator();o.type='triangle';o.frequency.value=f;
     const g=c.createGain();g.gain.setValueAtTime(0,t);
     g.gain.linearRampToValueAtTime(.12,t+.02);
     g.gain.exponentialRampToValueAtTime(.001,t+(d||.9));
     o.connect(g);g.connect(this.master);o.start(t);o.stop(t+(d||.9)+.2);}); },
 bell(n){ this.ensure(); const c=this.ctx;
   for(let k=0;k<n;k++){ const t=c.currentTime+k*.85;
     [[1,.13,7],[2,.07,5],[2.76,.04,3.6]].forEach(([r,a,dec])=>{
       const o=c.createOscillator();o.type='sine';o.frequency.value=124*r;
       const g=c.createGain();g.gain.setValueAtTime(0,t);
       g.gain.linearRampToValueAtTime(a,t+.01);
       g.gain.exponentialRampToValueAtTime(.0004,t+dec);
       o.connect(g);g.connect(this.master);o.start(t);o.stop(t+dec+.2);});} }
};