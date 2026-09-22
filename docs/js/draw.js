/* draw.js — the black hole, drawn on your graphics card.
   One fragment shader: for every pixel a ray is stepped backwards from the camera through
   d²u/dφ² + u = 3u² (G=c=M=1) until it falls in, lands on the disk, or leaves. */
(function () {
  const root = document.getElementById('draw');
  if (!root) return;
  const canvas = root.querySelector('canvas');
  const hud = root.querySelector('.hud');
  const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false });
  if (!gl) {
    root.querySelector('.stage').innerHTML = '<p class="nowebgl">This browser has no WebGL 2, so the live drawing is off. The pictures on this page were made by the same method.</p>';
    return;
  }
  const VS = `#version 300 es
  in vec2 p; void main(){ gl_Position = vec4(p,0.,1.); }`;
  const FS = `#version 300 es
  precision highp float;
  out vec4 o;
  uniform vec2 res; uniform float incl, rout, rin, tpeak, hw, expo, dop, grav, stars, spin;
  // a hash for the star field
  float h21(vec2 q){ q = fract(q*vec2(123.34,456.21)); q += dot(q,q+45.32); return fract(q.x*q.y); }
  vec3 sky(vec3 v){
    float lon = atan(v.y, v.x), lat = asin(clamp(v.z,-1.,1.));
    vec2 uv = vec2(lon/6.2831853+0.5, lat/3.1415926+0.5);
    vec3 c = vec3(0.);
    // the band of the galaxy
    float band = exp(-pow((lat-0.35*sin(lon+1.1))/0.13,2.));
    c += band*vec3(0.02,0.024,0.04);
    // stars on a fine grid, three scales
    for (int k=0;k<3;k++){
      float s = (k==0)?900.:(k==1)?450.:220.;
      vec2 g = uv*vec2(2.,1.)*s; vec2 id = floor(g); vec2 f = fract(g)-0.5;
      float r = h21(id+float(k)*17.3);
      if (r > 0.985 - float(k)*0.01){
        float br = pow(h21(id*1.7+3.1), 6.)*2.5 + 0.15;
        float d = length(f);
        float tint = h21(id*2.3);
        vec3 col = tint<0.3?vec3(1.,.86,.72):(tint<0.75?vec3(.95,.96,1.):vec3(.72,.82,1.));
        c += col*br*exp(-d*d*40.);
      }
    }
    return c;
  }
  vec3 blackbody(float T){
    T = clamp(T,1000.,40000.)/100.;
    float r = T<=66.?255.:329.698727446*pow(max(T-60.,1e-6),-0.1332047592);
    float g = T<=66.?99.4708025861*log(max(T,1e-6))-161.1195681661:288.1221695283*pow(max(T-60.,1e-6),-0.0755148492);
    float b = T>=66.?255.:(T<=19.?0.:138.5177312231*log(max(T-10.,1e-6))-305.0447927307);
    vec3 c = pow(clamp(vec3(r,g,b)/255.,0.,1.),vec3(2.2));
    float l = dot(c,vec3(.2126,.7152,.0722));
    return c/max(l,1e-6);
  }
  void main(){
    float rcam = 60.;
    float i = radians(incl);
    vec3 n = vec3(sin(i),0.,cos(i));
    vec3 f = -n; vec3 right = vec3(0.,1.,0.); vec3 up = normalize(cross(right,f));
    vec2 px = (gl_FragCoord.xy/res)*2.-1.;
    float aspect = res.y/res.x;
    vec3 d = normalize(f + right*(px.x*hw/rcam) + up*(px.y*hw*aspect/rcam));
    vec3 e1 = n; float dn = dot(d,n);
    vec3 e2 = d - dn*e1; float e2n = max(length(e2),1e-9); e2 /= e2n;
    float bx = rcam*dot(d,right);
    float u = 1./rcam, du = -dn/(rcam*e2n), phi = 0.;
    float zprev = (1./u)*(e1.z);
    vec3 col = vec3(0.);
    int kind = 0; float rhit = 0.;
    float dphi = 0.02;
    for (int s=0; s<700; s++){
      // RK4
      float k1u=du, k1d=(grav>0.5)?(3.*u*u-u):(-u);
      float u2=u+0.5*dphi*k1u, d2=du+0.5*dphi*k1d, k2d=(grav>0.5)?(3.*u2*u2-u2):(-u2);
      float u3=u+0.5*dphi*d2, d3=du+0.5*dphi*k2d, k3d=(grav>0.5)?(3.*u3*u3-u3):(-u3);
      float u4=u+dphi*d3, d4=du+dphi*k3d, k4d=(grav>0.5)?(3.*u4*u4-u4):(-u4);
      float un = u + dphi/6.*(k1u+2.*d2+2.*d3+d4);
      float dun = du + dphi/6.*(k1d+2.*k2d+2.*k3d+k4d);
      float pn = phi + dphi;
      if (un >= 0.5){ kind = 0; break; }
      float zn = (1./max(un,1e-9))*(cos(pn)*e1.z + sin(pn)*e2.z);
      if (zprev*zn < 0. && un > 0.){
        float t = zprev/(zprev-zn);
        float uc = (1.-t)*u + t*un;
        float rc = 1./max(uc,1e-9);
        if (rc >= rin && rc <= rout){ kind = 1; rhit = rc; break; }
      }
      if (un <= 0.){
        float t = u/(u-un);
        float pe = phi + t*dphi;
        vec3 v = normalize(cos(pe)*e1 + sin(pe)*e2);
        kind = 2; col = (stars>0.5)?sky(v):vec3(0.);
        break;
      }
      if (pn > 10.){ kind = 0; break; }
      u = un; du = dun; phi = pn; zprev = zn;
    }
    if (kind == 1){
      float r = rhit;
      float tp = pow(max(pow(r,-3.)*(1.-sqrt(rin/r)),0.),0.25);
      float rmax = rin*49./36.;
      float tpmax = pow(pow(rmax,-3.)*(1.-sqrt(rin/rmax)),0.25);
      float tem = tpeak*tp/tpmax;
      float om = pow(r,-1.5);
      float g = sqrt(max(1.-3./r,0.)) / (1. + (dop>0.5?1.:0.)*spin*om*bx*sin(i));
      float tobs = g*tem;
      float bright = pow(g,4.)*pow(tem/tpeak,4.);
      col = blackbody(tobs)*bright*1.6;
    }
    vec3 x = 1. - exp(-col*expo);
    o = vec4(pow(clamp(x,0.,1.),vec3(1./2.2)),1.);
  }`;
  function sh(t, s) { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; }
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  gl.useProgram(prog);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = {}; for (const k of ['res', 'incl', 'rout', 'rin', 'tpeak', 'hw', 'expo', 'dop', 'grav', 'stars', 'spin']) U[k] = gl.getUniformLocation(prog, k);

  const ctl = {};
  root.querySelectorAll('input[type=range]').forEach(el => { ctl[el.name] = el; el.addEventListener('input', () => { out(el); dirty = true; }); out(el); });
  function out(el) { const o = root.querySelector(`output[for="${el.id}"]`); if (o) o.textContent = fmt(el); }
  function fmt(el) { const v = +el.value; return el.dataset.unit ? `${v}${el.dataset.unit}` : `${v}`; }
  const tog = {};
  root.querySelectorAll('button[data-toggle]').forEach(b => {
    tog[b.dataset.toggle] = b.getAttribute('aria-pressed') === 'true';
    b.addEventListener('click', () => { tog[b.dataset.toggle] = !tog[b.dataset.toggle]; b.setAttribute('aria-pressed', tog[b.dataset.toggle]); dirty = true; });
  });
  root.querySelectorAll('.presets button').forEach(b => b.addEventListener('click', () => {
    const p = JSON.parse(b.dataset.set);
    for (const k in p) { if (ctl[k]) { ctl[k].value = p[k]; out(ctl[k]); } else if (k in tog) { tog[k] = p[k]; root.querySelector(`[data-toggle="${k}"]`).setAttribute('aria-pressed', p[k]); } }
    dirty = true;
  }));

  let dirty = true, last = 0;
  function size() {
    const w = Math.min(root.clientWidth, 1280);
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const W = Math.round(w * dpr), H = Math.round(W * 9 / 16);
    if (canvas.width !== W) { canvas.width = W; canvas.height = H; dirty = true; }
  }
  function frame(t) {
    size();
    if (dirty) {
      const t0 = performance.now();
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(U.res, canvas.width, canvas.height);
      gl.uniform1f(U.incl, +ctl.incl.value);
      gl.uniform1f(U.rout, +ctl.rout.value);
      gl.uniform1f(U.rin, 6);
      gl.uniform1f(U.tpeak, +ctl.tpeak.value);
      gl.uniform1f(U.hw, +ctl.zoom.value);
      gl.uniform1f(U.expo, +ctl.expo.value);
      gl.uniform1f(U.dop, tog.doppler ? 1 : 0);
      gl.uniform1f(U.grav, tog.gravity ? 1 : 0);
      gl.uniform1f(U.stars, tog.stars ? 1 : 0);
      gl.uniform1f(U.spin, 1);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      gl.finish();
      const ms = performance.now() - t0;
      hud.textContent = `${canvas.width}×${canvas.height} = ${(canvas.width * canvas.height / 1e6).toFixed(2)} million rays · ${ms.toFixed(0)} ms`;
      dirty = false;
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.addEventListener('resize', () => { dirty = true; });

  const save = root.querySelector('[data-save]');
  if (save) save.addEventListener('click', () => {
    dirty = true;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      canvas.toBlob(b => { const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'black-hole.png'; a.click(); }, 'image/png');
    }));
  });
})();
