# 07 · Sonido

> El sonido es el recurso más fácil de arruinar. **Por defecto: discreto, opcional y siempre silenciable (`U`).**

## 1. Categorías y uso

| Categoría | Ejemplo | Cuándo usar | Volumen |
|---|---|---|---|
| **Feedback UI** | "tick" suave al avanzar | Solo en modo kiosk / autoexploración | muy bajo |
| **Énfasis** | "whoosh" en reveal, "ding" al aparecer la cifra | Momento STAR, big-number | bajo |
| **Efectos de momento** | Redoble + platillo, aplausos, confeti | Celebraciones, lanzamientos (con atajo, nunca automático) | medio |
| **Ambiente / música** | Loop instrumental en portada o intro | Apertura antes de empezar, pausas, kiosk | muy bajo, fade in/out |
| **Narración** | Voz grabada o TTS por slide | Decks autoexplicativos / asincrónicos | normal |
| **Video con audio** | Demo, testimonio | Evidencia | normal |

Reglas:
- Ningún sonido en > 20% de las slides.
- Duración de efectos ≤ 1 s; fade-out siempre.
- Coherencia: un mismo "pack" sonoro por deck.
- Estado global de mute persistido (`localStorage`) y visible en el HUD.

## 2. Restricciones técnicas
- **Política de autoplay**: los navegadores bloquean audio hasta un gesto del usuario. Crear/reanudar el `AudioContext` en el primer `keydown`/`pointerdown` (`ctx.resume()`).
- Audio en la **ventana de audiencia**, no en la del presentador (evitar doble reproducción con BroadcastChannel).

## 3. Opción A — Sonidos sintetizados con Web Audio (peso 0 KB) ✅ recomendado
```js
const AC = new (window.AudioContext||window.webkitAudioContext)();
const master = AC.createGain(); master.gain.value = 0.25; master.connect(AC.destination);
function tone({f=880, type='sine', dur=.12, vol=.5, slideTo=null}={}){
  const o=AC.createOscillator(), g=AC.createGain(), t=AC.currentTime;
  o.type=type; o.frequency.setValueAtTime(f,t); if(slideTo) o.frequency.exponentialRampToValueAtTime(slideTo,t+dur);
  g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(vol,t+.01); g.gain.exponentialRampToValueAtTime(.0001,t+dur);
  o.connect(g).connect(master); o.start(t); o.stop(t+dur+.02);
}
const SFX = {
  tick:   () => tone({f:1200, dur:.05, vol:.2}),
  ding:   () => { tone({f:1318, dur:.6, vol:.3}); tone({f:1976, dur:.5, vol:.15}); },
  pop:    () => tone({f:600, slideTo:200, dur:.09, type:'triangle', vol:.4}),
  rise:   () => tone({f:300, slideTo:1200, dur:.35, type:'sawtooth', vol:.08}),
};
function whoosh(dur=.4){ // ruido filtrado
  const b=AC.createBuffer(1, AC.sampleRate*dur, AC.sampleRate), d=b.getChannelData(0);
  for(let i=0;i<d.length;i++) d[i]=(Math.random()*2-1)*(1-i/d.length);
  const s=AC.createBufferSource(), f=AC.createBiquadFilter(), t=AC.currentTime;
  f.type='bandpass'; f.frequency.setValueAtTime(400,t); f.frequency.exponentialRampToValueAtTime(3000,t+dur);
  s.buffer=b; s.connect(f).connect(master); s.start();
}
```
Asociación declarativa: `<div class="frag" data-step="2" data-sfx="ding">`.

## 4. Opción B — Archivos cortos incrustados
- MP3/OGG/Opus mono 64–96 kbps, ≤ 1 s → 5–15 KB c/u en base64 (`data:audio/mpeg;base64,...`).
- Decodificar una vez con `AC.decodeAudioData` y reproducir con `AudioBufferSourceNode` (latencia baja).
- Fuentes: librerías CC0 (verificar licencia de cada archivo) o generados.
- Música de fondo: **no incrustar** si > 1–2 MB; referenciar por URL o dejar como recurso externo opcional.

## 5. Opción C — Narración
- **TTS del navegador**: `speechSynthesis.speak(new SpeechSynthesisUtterance(notes))` con `lang='es-CL'` → narración automática a partir de las notas del orador (modo asincrónico). Calidad variable según SO.
- Voz grabada por slide (`data-audio`) con avance automático al terminar (`ended`).
- Siempre con subtítulos visibles (las notas) para accesibilidad.

## 6. Accesibilidad
- Nunca transmitir información **solo** por sonido.
- Respetar mute global y no reproducir si `prefers-reduced-motion` y el usuario no lo activó explícitamente (convención conservadora).
