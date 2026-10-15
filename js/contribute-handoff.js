/**
 * DocStory — Move an interview draft to another device (js/contribute-handoff.js)
 *
 * The draft travels inside the link itself, after the "#", so it never reaches our server or
 * Vercel (browsers don't send that part of a link). The school email is left out on purpose:
 * people send these links to themselves by text or email, and the address isn't needed until
 * they continue, when /contribute/continue/ asks for it again.
 *
 *   link:  /contribute/continue/#d=z<base64url of deflate-compressed JSON>   (z = compressed)
 *          /contribute/continue/#d=j<base64url of JSON>                       (j = browsers without compression)
 */
window.DocStoryHandoff = (function () {
  'use strict';
  const PATH = '/contribute/continue/';
  const LEAVE_OUT = ['email', 'rqEmail'];

  const toB64 = bytes => {
    let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  };
  const fromB64 = str => {
    const s = atob(str.replace(/-/g, '+').replace(/_/g, '/'));
    const out = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i);
    return out;
  };
  const pipe = (bytes, stream) => new Response(new Blob([bytes]).stream().pipeThrough(stream)).arrayBuffer().then(b => new Uint8Array(b));
  const canZip = typeof CompressionStream === 'function' && typeof DecompressionStream === 'function';

  function payload(state) {
    const d = { v: 1, savedAt: Date.now() };
    Object.keys(state).forEach(k => { if (LEAVE_OUT.indexOf(k) < 0) d[k] = state[k]; });
    return new TextEncoder().encode(JSON.stringify(d));
  }
  const base = () => location.origin + PATH + '#d=';

  return {
    /* Uncompressed link, available instantly (used if a tap comes before the compressed one is ready) */
    linkNow: state => base() + 'j' + toB64(payload(state)),
    /* Shorter, compressed link */
    link: state => canZip
      ? pipe(payload(state), new CompressionStream('deflate-raw')).then(b => base() + 'z' + toB64(b))
      : Promise.resolve(base() + 'j' + toB64(payload(state))),
    /* The draft in a #d=… fragment, or null if it's missing or damaged */
    read: hash => {
      const m = /[#&]d=([zj])([A-Za-z0-9_-]+)/.exec(hash || '');
      if (!m) return Promise.resolve(null);
      let bytes;
      try { bytes = fromB64(m[2]); } catch (e) { return Promise.resolve(null); }
      const unzip = m[1] === 'z'
        ? (canZip ? pipe(bytes, new DecompressionStream('deflate-raw')) : Promise.reject(new Error('old browser')))
        : Promise.resolve(bytes);
      return unzip.then(b => {
        const d = JSON.parse(new TextDecoder().decode(b));
        return d && d.v === 1 ? d : null;
      }).catch(e => (e && e.message === 'old browser' ? { error: 'old-browser' } : null));
    },
  };
})();
