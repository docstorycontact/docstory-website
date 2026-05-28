(function () {
  // Fixed placement configs — cycle if more doodles than slots exist.
  // Positions are viewport % (left/top), size in px, base rotation in deg, opacity 0–1.
  var PLACEMENTS = [
    { x: 4,  y: 6,  size: 144, rot: -18, opacity: 0.084 },
    { x: 48, y: 4,  size: 168, rot:  12, opacity: 0.078 },
    { x: 80, y: 3,  size: 116, rot:  -8, opacity: 0.090 },
    { x: 18, y: 28, size: 136, rot:  22, opacity: 0.084 },
    { x: 62, y: 22, size: 112, rot: -15, opacity: 0.078 },
    { x: 35, y: 48, size: 152, rot:  10, opacity: 0.084 },
    { x: 72, y: 52, size: 124, rot: -22, opacity: 0.072 },
    { x: 8,  y: 62, size: 104, rot:   6, opacity: 0.078 },
    { x: 55, y: 70, size: 120, rot: -12, opacity: 0.084 },
    { x: 25, y: 80, size:  96, rot:  18, opacity: 0.072 },
    { x: 82, y: 76, size:  88, rot:  -5, opacity: 0.066 },
    { x: 44, y: 88, size: 100, rot:   8, opacity: 0.072 },
  ];

  // Each doodle gets its own drift direction, travel range, and speed.
  // dxFrom/dxTo control horizontal travel (negative = left bias, positive = right bias).
  // dyFrom/dyTo control vertical travel. rwFrom/rwTo control rotation swing.
  var MOTIONS = [
    { dxFrom: -18, dxTo:   6, dyFrom:  -8, dyTo:  16, rwFrom: -10, rwTo:   4 },
    { dxFrom:   6, dxTo:  22, dyFrom: -16, dyTo:   4, rwFrom:  -3, rwTo:  14 },
    { dxFrom: -14, dxTo:  14, dyFrom:   6, dyTo:  24, rwFrom: -14, rwTo:   4 },
    { dxFrom: -22, dxTo:  -4, dyFrom:  -8, dyTo:  10, rwFrom:   4, rwTo:  16 },
    { dxFrom:   8, dxTo:  24, dyFrom: -20, dyTo:  -2, rwFrom: -12, rwTo:   6 },
    { dxFrom: -10, dxTo:  18, dyFrom:   4, dyTo:  22, rwFrom:  -6, rwTo:  12 },
    { dxFrom: -24, dxTo:  -6, dyFrom:  -6, dyTo:  14, rwFrom: -16, rwTo:  -2 },
    { dxFrom:  12, dxTo:  26, dyFrom: -14, dyTo:   4, rwFrom:   2, rwTo:  16 },
    { dxFrom:  -8, dxTo:  10, dyFrom: -22, dyTo:  -4, rwFrom:  -8, rwTo:   8 },
    { dxFrom: -16, dxTo:   2, dyFrom:   8, dyTo:  24, rwFrom:   6, rwTo:  18 },
    { dxFrom:  10, dxTo:  26, dyFrom:  -8, dyTo:  12, rwFrom: -14, rwTo:   2 },
    { dxFrom: -12, dxTo:   8, dyFrom: -18, dyTo:   2, rwFrom:  -6, rwTo:  14 },
  ];

  var SPEEDS = [
    { durX: 13, durY: 10, durR: 17 },
    { durX: 19, durY: 14, durR: 23 },
    { durX: 10, durY: 17, durR: 14 },
    { durX: 23, durY:  9, durR: 19 },
    { durX: 15, durY: 21, durR: 12 },
    { durX:  9, durY: 15, durR: 25 },
    { durX: 21, durY: 11, durR: 16 },
    { durX: 14, durY: 19, durR: 10 },
    { durX: 17, durY: 12, durR: 21 },
    { durX: 11, durY: 23, durR: 15 },
    { durX: 25, durY: 16, durR: 20 },
    { durX: 16, durY: 10, durR: 13 },
  ];

  function buildDoodle(src, placement, index) {
    var wrap = document.createElement('div');
    wrap.className = 'doodle-float';
    wrap.setAttribute('aria-hidden', 'true');

    var m = MOTIONS[index % MOTIONS.length];
    var s = SPEEDS[index % SPEEDS.length];
    var delay = -(index * 3.1);

    wrap.style.cssText = [
      'left:'        + placement.x + '%',
      'top:'         + placement.y + '%',
      'width:'       + placement.size + 'px',
      'height:'      + placement.size + 'px',
      '--base-rot:'  + placement.rot  + 'deg',
      '--dur-x:'     + s.durX + 's',
      '--dur-y:'     + s.durY + 's',
      '--dur-r:'     + s.durR + 's',
      '--delay:'     + delay + 's',
      '--dx-from:'   + m.dxFrom + 'px',
      '--dx-to:'     + m.dxTo   + 'px',
      '--dy-from:'   + m.dyFrom + 'px',
      '--dy-to:'     + m.dyTo   + 'px',
      '--rw-from:'   + m.rwFrom + 'deg',
      '--rw-to:'     + m.rwTo   + 'deg',
      '--doodle-opacity:' + placement.opacity,
    ].join('; ');

    var img = document.createElement('img');
    img.src = src;
    img.alt = '';
    img.setAttribute('aria-hidden', 'true');
    img.draggable = false;
    wrap.appendChild(img);
    return wrap;
  }

  function init() {
    var bg = document.getElementById('doodle-bg');
    if (!bg) return;

    // Build the path to doodles/ relative to this page's location.
    // Works for index.html at root. Sub-pages would need a different root.
    var base = 'doodles/';

    fetch(base + 'index.json')
      .then(function (res) {
        if (!res.ok) throw new Error('manifest not found');
        return res.json();
      })
      .then(function (files) {
        if (!Array.isArray(files) || files.length === 0) return;
        var frag = document.createDocumentFragment();
        files.forEach(function (filename, i) {
          var placement = PLACEMENTS[i % PLACEMENTS.length];
          frag.appendChild(buildDoodle(base + filename, placement, i));
        });
        bg.appendChild(frag);
      })
      .catch(function () {
        // Fail silently — doodles are decoration only.
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
