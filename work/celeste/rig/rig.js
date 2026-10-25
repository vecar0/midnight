// Céleste 리깅 모듈: const rig = await CelesteRig(canvas, {base, parts, input, capture})
//   rig.stage = 0~1 (석고 → 색이 돌아옴), rig.expr = '' | 'smile' | 'frown', rig.draw(초), rig.tap()
window.CelesteRig = async function(cv, opt = {}){

  // Céleste 리깅: See-through 레이어(가려진 부분까지 있음) + 원화 색.
  // 얼굴·이목구비·귀걸이는 절대 휘지 않고 통째로만 옮긴다. 휘는 건 머리카락 끝뿐.
  const R = opt.base || './', P = opt.parts || '../parts/';
  const gl = cv.getContext('webgl', {premultipliedAlpha:true, alpha:true, antialias:true, preserveDrawingBuffer:!!opt.capture});
  const sm = (a,b,x)=>{ const t = Math.min(1, Math.max(0, (x-a)/(b-a))); return t*t*(3-2*t); };
  const clamp = (v,a,b)=>Math.max(a, Math.min(b, v));
  let RIG, PARTS, IW, IH, EXPR = '';

  // ---------- 움직임 상태 ----------
  const S = {
    head:{x:0, y:0, vx:0, vy:0, tx:0, ty:0, next:0},        // 고개(시선 방향) — 스프링으로 목표를 따라감
    gaze:{x:0, y:0, tx:0, ty:0, next:0},                      // 눈동자
    blink:{t:-1, next:1.5, double:false},
    roll:{x:0, y:0, vx:0, vy:0, tx:0, next:0},              // 고개 기울기(라디안)
    smile:0, frown:0, react:0,
    torso:{x:0, y:0, vx:0, vy:0},                             // 상체: 고개를 조금 늦게, 조금만 따라온다
    breath:{ph:0, v:0},                                       // 숨: 들숨 짧고 날숨 길게, 박자도 조금씩 다르게
    wind:0, windT:0, windV:0,
    tilt:{x:0, y:0}, pointer:null, lastT:null,
  };
  // 머리카락 줄기: 노드마다 옆으로 흔들리는 양 (뿌리 노드는 고개에 붙어 있음)
  function chain(n){ return {x:new Float32Array(n), v:new Float32Array(n)}; }
  const HAIR = {
    front_hair:{root:935, len:720, chains:{L:chain(7), R:chain(7)}, stiff:.9},
    back_hair:{root:990, len:760, chains:{L:chain(7), R:chain(7)}, stiff:.75},
  };
  let STR = {};                                                // 다발 레이어 (rig.json 의 group 'strand')
  const EAR = { earMoon:{pivot:[460, 980], a:0, v:0, len:1.0}, earStar:{pivot:[851, 879], a:0, v:0, len:.8} };
  const FACE_X = 650;

  // ---------- WebGL ----------
  const load = src=>new Promise((ok, no)=>{ const i = new Image(); i.onload = ()=>ok(i); i.onerror = ()=>no(src); i.src = src; });
  function tex(img, unit){
    const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0+unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
    for(const [k,v] of [[gl.TEXTURE_MIN_FILTER,gl.LINEAR],[gl.TEXTURE_MAG_FILTER,gl.LINEAR],[gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE],[gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE]])
      gl.texParameteri(gl.TEXTURE_2D, k, v);
    return t;
  }
  const VS = `attribute vec2 p, uv, ip; varying vec2 v, w; uniform vec2 res;
    void main(){ v = uv; w = ip; gl_Position = vec4(p.x/res.x*2.-1., 1.-p.y/res.y*2., 0., 1.); }`;
  const FS = `precision mediump float; varying vec2 v, w;     // v: 레이어 그림 좌표, w: 원화 좌표(쉬는 자세)
    uniform sampler2D img, msk, clipT; uniform vec4 clipR; uniform vec2 gaze; uniform float isIris, alpha, plaster; uniform vec3 stage;
    // 석고: 몸에 붙은 좌표(w)로 만든 무늬라 리깅을 따라 움직인다
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7)))*43758.5453); }
    float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3. - 2.*f);
      return mix(mix(hash(i), hash(i + vec2(1., 0.)), f.x), mix(hash(i + vec2(0., 1.)), hash(i + vec2(1., 1.)), f.x), f.y); }
    float fbm(vec2 p){ return vnoise(p)*.55 + vnoise(p*2.1 + 3.7)*.3 + vnoise(p*4.3 + 9.1)*.15; }
    vec3 shards(vec2 p){                                  // 보로노이 조각: (경계까지 거리, 내 조각 값, 이웃 조각 값)
      vec2 i = floor(p), f = fract(p); float d1 = 8., d2 = 8., h1 = 0., h2 = 0.;
      for(int y = -1; y <= 1; y++) for(int x = -1; x <= 1; x++){
        vec2 o = vec2(float(x), float(y)), id = i + o, r = o + vec2(hash(id), hash(id + 17.3))*.9 - f; float d = dot(r, r);
        float h = hash(id + 41.7)*.5 + vnoise(id*.33)*.5;           // 이웃끼리 비슷하게 → 덩어리로 떨어진다
        if(d < d1){ d2 = d1; h2 = h1; d1 = d; h1 = h; } else if(d < d2){ d2 = d; h2 = h; } }
      return vec3(sqrt(d2) - sqrt(d1), h1, h2); }
    void main(){
      vec4 c = texture2D(img, v) * alpha;
      if(isIris > 0.){                                    // 눈동자는 흰자 밖으로 나가지 않게 흰자 모양으로 자른다
        vec2 e = (w + gaze - clipR.xy) / clipR.zw;
        float k = (e.x < 0. || e.y < 0. || e.x > 1. || e.y > 1.) ? 0. : texture2D(clipT, e).a;
        c *= k; }
      if(c.a < .004){ gl_FragColor = vec4(0.); return; }
      vec3 u = c.rgb / c.a;                                 // 미리 곱한 알파를 풀어서 계산
      vec3 m = texture2D(msk, w).rgb;                      // 단계별 색: r=손톱 g=머리 b=눈
      float g = max(max(m.r*(1.-stage.x), m.g*(1.-stage.y)), m.b*(1.-stage.z));
      float l = dot(u, vec3(.299,.587,.114));
      vec3 col = mix(u, vec3(l*1.05), g);
      if(plaster < 1.){
        // 석고: 밝은 무광 흰색으로 눌러 담고(선은 회색으로 남김), 고운 결 + 실금. 진행할수록 조각조각 벗겨진다
        vec2 q = vec2(w.x, w.y*1.967);
        vec2 sp = q*10.; sp += (vec2(fbm(sp*.7), fbm(sp*.7 + 7.)) - .5)*.45;      // 조각 경계를 비뚤게
        vec3 V = shards(sp);
        float th = plaster*1.12 - .08, edge = 1. - smoothstep(.0, .045, V.x);
        if(V.y < th){                                       // 떨어져 나간 조각: 색이 보이고, 남은 석고 가장자리 밑에 그림자
          col *= 1. - edge*.45*step(th, V.z);
        } else {
          vec3 P = mix(vec3(.42, .42, .41), vec3(.975, .968, .952), pow(l, .6));
          P += (hash(floor(q*700.)) - .5)*.035;
          float front = 1. - smoothstep(.0, .07, min(V.y, V.z) - max(th, .22));   // 곧 떨어질 조각 둘레부터 금이 간다
          P *= 1. - edge*front*.5;
          P = mix(P, vec3(1.), edge*.35*step(V.z, th));       // 떨어진 쪽과 맞닿은 면: 석고 두께의 흰 단면
          col = P;
        }
      }
      gl_FragColor = vec4(col*c.a, c.a);
    }`;
  let U, M = {}, T = {}, ORDER = [];
  function program(){
    const sh = (t,s)=>{ const o = gl.createShader(t); gl.shaderSource(o,s); gl.compileShader(o);
      if(!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; };
    const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER,VS)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER,FS));
    gl.linkProgram(p); gl.useProgram(p); return p;
  }
  function mesh(name, x0, y0, w, h, nx, ny){
    const rest = [], uv = [], ip = [], idx = [];
    for(let j=0;j<=ny;j++) for(let i=0;i<=nx;i++){ const x = x0 + i/nx*w, y = y0 + j/ny*h; rest.push(x, y); uv.push(i/nx, j/ny); ip.push(x/IW, y/IH); }
    for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const a = j*(nx+1)+i, b = a+1, c = a+nx+1, d = c+1; idx.push(a,b,c, b,d,c); }
    const buf = d=>{ const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(d), gl.STATIC_DRAW); return b; };
    const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(idx), gl.STATIC_DRAW);
    return {name, rest, pos:new Float32Array(rest.length), uv:buf(uv), ip:buf(ip), ib, n:idx.length, pb:gl.createBuffer(), alpha:1};
  }

  // ---------- 입력 ----------
  function setPointer(e){                                    // 그림이 준비되기 전이나 이상한 값은 무시
    const r = cv.getBoundingClientRect(); if(!IW || !r.width) return false;
    const x = (e.clientX-r.left)/r.width*IW, y = (e.clientY-r.top)/r.height*IH;
    if(!Number.isFinite(x) || !Number.isFinite(y)) return false;
    S.pointer = {x, y, t:performance.now()}; return true;
  }
  const IN = opt.input || window;
  IN.addEventListener('pointermove', setPointer);
  IN.addEventListener('pointerdown', e=>{ if(!setPointer(e)) return;
    S.react = 1; S.head.vy -= 8; });
  window.addEventListener('deviceorientation', e=>{ if(!Number.isFinite(e.gamma) || !Number.isFinite(e.beta)) return; S.tilt.x = clamp(e.gamma/30, -1, 1); S.tilt.y = clamp((e.beta-50)/30, -1, 1); });

  // ---------- 시뮬레이션 ----------
  const rnd = (a,b)=>a + Math.random()*(b-a);
  function spring(o, k, tx, ty, dt, damp){                   // 임계 감쇠에 가까운 스프링
    o.vx += ((tx - o.x)*k - o.vx*damp)*dt; o.vy += ((ty - o.y)*k - o.vy*damp)*dt; o.x += o.vx*dt; o.y += o.vy*dt;
  }
  function simulate(t, dt){
    const H = S.head, G = S.gaze;
    // 고개: 가끔 다른 곳을 본다. 손가락이 최근에 움직였으면 그쪽을 본다
    const pointing = S.pointer && Number.isFinite(S.pointer.x) && performance.now() - S.pointer.t < 2500;
    // 가만히 있어도 여러 느린 흔들림이 겹쳐 미세하게 움직이고, 가끔 천천히 다른 곳을 본다
    const idleX = Math.sin(t*.37)*3.0 + Math.sin(t*.61 + 1.3)*1.8 + Math.sin(t*1.13 + .4)*.55;
    const idleY = Math.sin(t*.29 + 2)*.05;
    let glance = false;
    if(pointing){ H.tx = clamp((S.pointer.x - FACE_X)/60, -10, 10); H.ty = clamp((S.pointer.y - 880)/1500, -.15, .15); }
    else if(t > H.next){ const look = Math.random() < .45; H.tx = look ? rnd(-9, 9) : rnd(-2, 2); H.ty = look ? rnd(-.12, .08) : 0; H.next = t + rnd(3, 7.5); glance = look; }
    spring(H, 7, H.tx + idleX + S.tilt.x*5, H.ty + idleY + S.tilt.y*.1, dt, 5.3);    // 느리고 부드럽게 (거의 임계 감쇠)
    // 상체는 고개의 1/4쯤을 늦게 따라온다 → 목이 덜 꺾인다
    spring(S.torso, 4, H.x*.33, 0, dt, 4);
    // 숨: 박자 3.8~4.8초, 들숨 40%·날숨 50%·쉼 10%
    S.breath.ph += dt/(4.3 + Math.sin(t*.11)*.5 + Math.sin(t*.037)*.3);
    const bp = S.breath.ph % 1;
    S.breath.v = bp < .4 ? sm(0, .4, bp) : 1 - sm(.4, .9, bp);
    // 기울기: 보는 쪽으로 살짝 + 가끔 갸웃
    const Rl = S.roll;
    if(t > Rl.next){ Rl.tx = rnd(-.012, .012); Rl.next = t + rnd(3, 7); }
    spring(Rl, 6, Rl.tx - (H.x - S.torso.x)*.0018 + S.tilt.x*.012 + S.react*.025, 0, dt, 4.9);
    // 눈: 고개보다 먼저 휙 움직이고(단속운동), 작은 떨림
    // 눈: 고개보다 먼저 휙(단속운동) → 고개가 따라오면 눈은 조금 돌아온다. 그 사이 아주 작은 떨림
    if(pointing){ G.tx = clamp((S.pointer.x - FACE_X)/45, -6, 6); G.ty = clamp((S.pointer.y - 880)/120, -3, 3); }
    else if(glance){ G.tx = clamp(H.tx*1.1, -5, 5); G.ty = clamp(H.ty*.8, -2.5, 2.5); G.next = t + rnd(.5, 1.2); }
    else if(t > G.next){ G.tx = (H.tx - H.x)*.5 + rnd(-1.6, 1.6); G.ty = rnd(-.8, .8); G.next = t + rnd(.9, 3.2); }
    G.x += (G.tx - G.x)*Math.min(1, dt*26); G.y += (G.ty - G.y)*Math.min(1, dt*26);
    // 깜빡임: 2~6초 간격, 가끔 두 번
    const B = S.blink;
    if(B.t < 0 && (t > B.next || (glance && Math.random() < .4))){ B.t = t; B.double = Math.random() < .12; }   // 크게 볼 때 같이 깜빡이기도
    if(B.t >= 0 && t - B.t > (B.double ? .5 : .24)){ B.t = -1; B.next = t + rnd(2.5, 6.5); }
    // 바람: 가끔 한 줄기씩
    // 바람 없음: 머리카락·귀걸이는 고개 움직임에만 반응한다
    S.wind += (S.windV - S.wind)*Math.min(1, dt*1.5); S.windV *= Math.pow(.6, dt);
    // 표정
    const want = EXPR === 'smile' || S.react > .3 ? 1 : 0;
    S.smile += (want - S.smile)*Math.min(1, dt*6); S.frown += ((EXPR === 'frown' ? 1 : 0) - S.frown)*Math.min(1, dt*6);
    S.react = Math.max(0, S.react - dt*.5);
    // 머리카락 줄기: 뿌리는 고개를 따라가고, 아래 노드는 위 노드를 늦게 따라간다
    for(const h of Object.values(HAIR)) for(const [side, c] of Object.entries(h.chains)){
      const n = c.x.length; c.x[0] = H.x;
      for(let i=1;i<n;i++){
        const pull = (c.x[i-1] - c.x[i])*90*h.stiff, home = (H.x - c.x[i])*3;
        c.v[i] += (pull + home*4 - c.v[i]*7.5)*dt;
      }
      for(let i=1;i<n;i++) c.x[i] += c.v[i]*dt;
    }
    // 다발: 스스로 움직이지 않는다. 고개가 움직이면 관성으로 한 박자 늦게 따라오고 천천히 멈춘다
    for(const d of Object.values(STR)){
      const c = d.c, n = c.x.length; c.x[0] = H.x;
      for(let i=1;i<n;i++){
        const pull = (c.x[i-1] - c.x[i])*60, home = (H.x - c.x[i])*25;      // 늦게 따라오되
        c.v[i] += (pull + home - c.v[i]*6)*dt;                               // 한 번에 가라앉는다 (계속 출렁이지 않게)
      }
      for(let i=1;i<n;i++) c.x[i] += c.v[i]*dt;
    }
    // 귀걸이: 고개가 움직인 가속도를 받는 진자
    for(const e of Object.values(EAR)){
      const acc = -H.vx*.008 - S.roll.vx*2.5;                     // 귀걸이는 살짝만 (빈자리가 보이지 않게)
      e.v += (-e.a*45/e.len + acc*30 - e.v*4.5)*dt; e.a += e.v*dt; e.a = clamp(e.a, -.12, .12);
    }
  }
  function breathAt(){ return S.breath.v; }

  // ---------- 자세 ----------
  // 머리는 얼굴·이목구비·귀·귀걸이 고리·앞머리 뿌리를 한 덩어리로: 목을 축으로 살짝 기울고(roll) 옮겨진다.
  // 휘지 않고 덩어리째 움직이므로 요소가 뭉개지지 않는다. 값은 소수점까지 부드럽게.
  const NECK = [650, 1150];
  let HT = {c:1, s:0, x:0, y:0};
  function headXform(t){
    const a = S.roll.x;
    HT = {c:Math.cos(a), s:Math.sin(a), x:S.head.x, y:S.head.y - breathAt()*.12};   // 머리는 어깨에 실려 오르내린다
  }
  function hp(x, y){                                          // 쉬는 자세의 점 → 머리를 따라 움직인 점
    const dx = x - NECK[0], dy = y - NECK[1];
    return [NECK[0] + dx*HT.c - dy*HT.s + HT.x, NECK[1] + dx*HT.s + dy*HT.c + HT.y];
  }
  function tp(x, y){                                          // 상체: 어깨는 숨·고개를 따라, 난간 쪽으로 갈수록 고정
    const wb = 1 - sm(1120, 1950, y);
    return [x + S.torso.x*wb, y - breathAt()*.18*wb];
  }
  function poseBody(m){ for(let k=0;k<m.rest.length;k+=2){ const q = tp(m.rest[k], m.rest[k+1]); m.pos[k] = q[0]; m.pos[k+1] = q[1]; } }
  function headRigid(m, ox, oy){ for(let k=0;k<m.rest.length;k+=2){ const q = hp(m.rest[k], m.rest[k+1]); m.pos[k] = q[0] + (ox||0); m.pos[k+1] = q[1] + (oy||0); } }
  function rigid(m, dx, dy){ for(let k=0;k<m.rest.length;k+=2){ m.pos[k] = m.rest[k] + dx; m.pos[k+1] = m.rest[k+1] + dy; } }
  function poseNeck(m, y0, y1){                               // 위쪽은 머리를, 아래쪽은 상체를 따라간다 (턱 밑 이음새가 안 보이게)
    for(let k=0;k<m.rest.length;k+=2){ const x = m.rest[k], y = m.rest[k+1], w = 1 - sm(y0 || 980, y1 || 1220, y), q = hp(x, y), b = tp(x, y);
      m.pos[k] = b[0]*(1-w) + q[0]*w; m.pos[k+1] = b[1]*(1-w) + q[1]*w; }
  }
  function chainAt(c, s){ const n = c.x.length, f = s*(n-1), i = Math.min(n-2, Math.floor(f)), r = f - i; return c.x[i]*(1-r) + c.x[i+1]*r; }
  function poseHair(m, h){
    for(let k=0;k<m.rest.length;k+=2){
      const x = m.rest[k], y = m.rest[k+1], s = clamp((y - h.root)/h.len, 0, 1), w = Math.pow(s, 1.25);
      const side = sm(FACE_X - 120, FACE_X + 120, x);           // 왼쪽 줄기 0 … 오른쪽 줄기 1
      const sway = (chainAt(h.chains.L, s)*(1-side) + chainAt(h.chains.R, s)*side) - S.head.x;
      const q = hp(x, y);                                       // 뿌리 쪽은 머리와 한 덩어리
      const bt = tp(x, y), hx = bt[0] + (HT.x - S.torso.x)*(1 - s*.5), hy = bt[1];   // 끝 쪽은 어깨에 걸쳐 늘어진다
      const px = q[0]*(1-w) + hx*w + sway*w, py = q[1]*(1-w) + hy*w;
      m.pos[k] = px; m.pos[k+1] = py - .5*(sway*w)*(sway*w)/(y - h.root + 90);
    }
  }
  function poseStrand(m, d){                                  // 위쪽(얼굴 옆)은 머리와 한 덩어리, 턱 아래로 갈수록 흔들림
    for(let k=0;k<m.rest.length;k+=2){
      const x = m.rest[k], y = m.rest[k+1], s = clamp((y - d.root[1])/d.len, 0, 1), w = Math.pow(sm(.28, 1, s), 1.1);
      const sway = 26*Math.tanh((chainAt(d.c, s) - S.head.x)*d.gain/26);   // 크게 흔들려도 뚝 멈추지 않게 부드러운 한계
      const q = hp(x, y), bt = tp(x, y), hx = bt[0] + (HT.x - S.torso.x)*(1 - s*.5), hy = bt[1];
      m.pos[k] = q[0]*(1-w) + hx*w + sway*w; m.pos[k+1] = q[1]*(1-w) + hy*w - .5*(sway*w)*(sway*w)/(y - d.root[1] + 120);
    }
  }
  function poseEar(m, e){
    const [px, py] = hp(e.pivot[0], e.pivot[1]), c = Math.cos(e.a), s = Math.sin(e.a);   // 고리는 머리를 따라, 몸통은 늘어진다
    for(let k=0;k<m.rest.length;k+=2){ const dx = m.rest[k]-e.pivot[0], dy = m.rest[k+1]-e.pivot[1];
      m.pos[k] = px + dx*c - dy*s; m.pos[k+1] = py + dx*s + dy*c; }
  }

  // ---------- 그리기 ----------
  function draw(t, stage){
    const dt = S.lastT == null ? 0 : clamp(t - S.lastT, 0, .05); S.lastT = t;
    if(dt > 0) for(let i=0;i<2;i++) simulate(t, dt/2);
    gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform3f(U.stage, sm(.5,.75,stage), sm(.25,.5,stage), sm(0,.25,stage)); gl.uniform1f(U.plaster, stage);
    headXform(t); const b = breathAt(t);
    const B = S.blink, bt = B.t < 0 ? 1 : (t - B.t);
    const one = p=>p < .07 ? p/.07 : p < .11 ? 1 : p < .22 ? 1 - (p-.11)/.11 : 0;          // 감기 빠르게, 뜨기 천천히
    const blink = B.t < 0 ? 0 : Math.max(one(bt), B.double ? one(bt - .26) : 0);
    const closed = Math.max(1 - sm(.12, .25, stage), blink);
    for(const name of ORDER){
      if(api.only && !api.only.includes(name)) continue;               // 확인용: 일부 레이어만 그리기
      const m = M[name], g = RIG.layers[name]?.group || m.group;
      let a = 1;
      if(g === 'static') rigid(m, 0, 0);
      else if(name === 'neck') poseNeck(m);
      else if(g === 'body') poseBody(m);
      else if(g === 'arms') rigid(m, 0, 0);
      else if(g === 'hairFront') headRigid(m);
      else if(g === 'hairBack' || g === 'underHair') poseNeck(m, 1050, 1400);
      else if(g === 'strand') poseStrand(m, STR[name]);
      else if(g === 'earring') poseEar(m, EAR[name]);
      else if(g === 'iris') headRigid(m, S.gaze.x, S.gaze.y);
      else if(g === 'patch'){ headRigid(m); a = name === 'eyes_closed' ? closed : name === 'mouth_smile' ? S.smile : S.frown; if(a <= .001) continue; }
      else headRigid(m);                                                                      // 얼굴·이목구비·귀·머리 조각: 통째로
      gl.uniform1f(U.alpha, a);
      if(g === 'iris'){ const ew = RIG.layers[name.replace('irides', 'eyewhite')];
        gl.uniform1f(U.isIris, 1); gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, T[name.replace('irides', 'eyewhite')]);
        gl.uniform4f(U.clipR, ew.xy[0]/IW, ew.xy[1]/IH, ew.size[0]/IW, ew.size[1]/IH); gl.uniform2f(U.gaze, S.gaze.x/IW, S.gaze.y/IH);
      } else gl.uniform1f(U.isIris, 0);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, T[name]);
      gl.bindBuffer(gl.ARRAY_BUFFER, m.pb); gl.bufferData(gl.ARRAY_BUFFER, m.pos, gl.DYNAMIC_DRAW); gl.vertexAttribPointer(U.p, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, m.uv); gl.vertexAttribPointer(U.uv, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, m.ip); gl.vertexAttribPointer(U.ip, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.ib); gl.drawElements(gl.TRIANGLES, m.n, gl.UNSIGNED_SHORT, 0);
    }
  }

  const api = {stage:1, expr:'', only:null, S, get STR(){ return STR; }, get ORDER(){ return ORDER; }, get size(){ return [IW, IH]; },
    draw(t, stage){ EXPR = api.expr; draw(t, stage == null ? api.stage : stage); },
    tap(){ S.react = 1; S.head.vy -= 8; },
    point(x, y){ S.pointer = {x, y, t:performance.now()}; },
    seed(s){ let x = s; Math.random = ()=>((x = (x*16807) % 2147483647) / 2147483647); }};

    [RIG, PARTS] = await Promise.all([fetch(R+'rig.json').then(r=>r.json()), fetch(P+'parts.json').then(r=>r.json())]);
    [IW, IH] = RIG.size;
    ORDER = RIG.order.slice();
    // 얼굴 편집 패치: 눈 감음은 속눈썹 위, 미소·찡그림은 그 위 (앞머리 아래)
    const at = ORDER.indexOf('front_hair');
    ORDER.splice(at, 0, 'face_frown', 'mouth_smile', 'eyes_closed');
    const imgs = {};
    await Promise.all(RIG.order.map(async n=>{ imgs[n] = await load(R+n+'.webp'); }).concat(
      ['face_frown','mouth_smile','eyes_closed','mask'].map(async n=>{ imgs[n] = await load(P+n+'.webp'); })));
    cv.width = IW; cv.height = IH; gl.viewport(0,0,IW,IH);
    const prog = program(); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    U = {p:gl.getAttribLocation(prog,'p'), uv:gl.getAttribLocation(prog,'uv'), ip:gl.getAttribLocation(prog,'ip')};
    [U.p, U.uv, U.ip].forEach(a=>gl.enableVertexAttribArray(a));
    for(const n of ['res','img','msk','clipT','clipR','gaze','isIris','alpha','stage','plaster']) U[n] = gl.getUniformLocation(prog,n);
    for(const n of ORDER) T[n] = tex(imgs[n], 0);
    tex(imgs.mask, 1); gl.uniform1i(U.img, 0); gl.uniform1i(U.msk, 1); gl.uniform1i(U.clipT, 2); gl.uniform2f(U.res, IW, IH);
    for(const n of ORDER){
      let x0, y0, w, h;
      if(RIG.layers[n]){ [x0, y0] = RIG.layers[n].xy; [w, h] = RIG.layers[n].size; }
      else { [x0, y0] = PARTS.patches[n]; w = imgs[n].naturalWidth; h = imgs[n].naturalHeight; }
      const g = RIG.layers[n]?.group;
      const hair = g === 'hairBack' || g === 'strand' || g === 'underHair';
      if(g === 'strand'){ const Ld = RIG.layers[n]; STR[n] = {root:Ld.root, len:Ld.len, c:chain(8), ph:0, gain:5.5, side:Ld.root[0] < FACE_X ? 'L' : 'R'}; }
      const bend = n === 'neck' || g === 'body';
      M[n] = mesh(n, x0, y0, w, h, hair ? 14 : bend ? 4 : 1, hair ? 64 : bend ? 24 : 1);   // 머리카락(과 목)만 그물, 나머지는 사각형 하나(휘지 않음)
      if(!RIG.layers[n]) M[n].group = 'patch';
    }
  return api;
};
