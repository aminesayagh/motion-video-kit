// Motion kit for effectcraft-cli (from the OrbitRows video, identity v4): drawing and motion helpers, cue timing, and the parts every scene
// reuses (context label, chips, icons, ticks, the right-hand panel). Coordinates are storyboard
// units (960x540), drawn x2. Rules: storyboard_v4.html (pastel, Poppins + JetBrains Mono,
// one idea at a time, 300-400 ms slides and fades, nothing decorative moves).

var K = 2;
var P = {bgA: "#F9FEF6", bgB: "#F3E8E4", paper: "#FFFFFF", ink: "#2C353A", mute: "#7A8287", faint: "#C9CFC6",
         teal: "#0A6E89", coral: "#FB938F", yellow: "#FED84D", lav: "#C9BCEB", purple: "#6D5BA8", red: "#E63946",
         green: "#1FA35B", blue: "#2F6FED", char: "#2C353A", hl: "#1D5980"};
var EASE = 0.35;

function rgb(h) {
    return [parseInt(h.substr(1, 2), 16) / 255, parseInt(h.substr(3, 2), 16) / 255, parseInt(h.substr(5, 2), 16) / 255];
}

// f: "h" (Poppins) or "m" (JetBrains Mono); w: CSS weight.
function font(f, w) {
    if (f == "m") return w >= 600 ? "JetBrainsMono-Bold" : "JetBrainsMono-Regular";
    return w >= 700 ? "Poppins-Bold" : w >= 600 ? "Poppins-SemiBold" : "Poppins-Regular";
}

// ---- drawing -------------------------------------------------------------

// Point text at baseline (x, y); o: {size, fill, w, f, a: start|middle}.
function txt(comp, name, s, x, y, o) {
    o = o || {};
    var L = comp.layers.addText(s);
    L.name = name;
    var p = L.property("Source Text"), d = p.value;
    d.font = font(o.f || "h", o.w || 400);
    d.fontSize = (o.size || 15) * K;
    d.applyFill = true;
    d.fillColor = rgb(o.fill || P.ink);
    d.applyStroke = false;
    d.justification = o.a == "middle" ? ParagraphJustification.CENTER_JUSTIFY : ParagraphJustification.LEFT_JUSTIFY;
    p.setValue(d);
    L.transform.position.setValue([x * K, y * K]);
    return L;
}

function setText(L, s) {
    var p = L.property("Source Text"), d = p.value;
    d.text = s;
    p.setValue(d);
}

// Right edge of a text layer's ink, in storyboard units from its position (unscaled).
function textRight(L) {
    var r = L.sourceRectAtTime(0, false);
    return (r.left + r.width) / K;
}

// Width of s in a given style, measured on a throwaway layer.
function measure(comp, s, o) {
    var p = txt(comp, "probe", s, 0, 0, o), w = textRight(p);
    p.remove();
    return w;
}

// Stroke is added before fill so it paints on top, as in SVG. o: {fill, op, stroke, sw, round, dash: [d, g], evenodd}.
function paint(g, o) {
    if (o.stroke) {
        var s = g.addProperty("ADBE Vector Graphic - Stroke");
        s.property("ADBE Vector Stroke Color").setValue(rgb(o.stroke));
        s.property("ADBE Vector Stroke Width").setValue(o.sw * K);
        if (o.round) {
            s.property("ADBE Vector Stroke Line Cap").setValue(2);
            s.property("ADBE Vector Stroke Line Join").setValue(2);
        }
        if (o.dash) {
            var d = s.property("ADBE Vector Stroke Dashes");
            d.addProperty("ADBE Vector Stroke Dash 1").setValue(o.dash[0] * K);
            d.addProperty("ADBE Vector Stroke Gap 1").setValue(o.dash[1] * K);
        }
    }
    if (o.fill) {
        var f = g.addProperty("ADBE Vector Graphic - Fill");
        f.property("ADBE Vector Fill Color").setValue(rgb(o.fill));
        f.property("ADBE Vector Fill Opacity").setValue((o.op == null ? 1 : o.op) * 100);
        if (o.evenodd) f.property("ADBE Vector Fill Rule").setValue(2);
    }
}

// Rounded rect, top-left (x, y) like SVG; the layer sits at its centre. Defaults follow the storyboard: white, no stroke, rx 12.
function rect(comp, name, x, y, w, h, o) {
    o = o || {};
    var L = comp.layers.addShape();
    L.name = name;
    L.transform.position.setValue([(x + w / 2) * K, (y + h / 2) * K]);
    var g = L.property("ADBE Root Vectors Group");
    var r = g.addProperty("ADBE Vector Shape - Rect");
    r.property("ADBE Vector Rect Size").setValue([w * K, h * K]);
    r.property("ADBE Vector Rect Roundness").setValue((o.rx == null ? 12 : o.rx) * K);
    paint(g, {fill: o.fill === undefined ? P.paper : o.fill, op: o.op, stroke: o.stroke, sw: o.sw || 2, dash: o.dash});
    return L;
}

function rectSize(L) {
    return L.property("ADBE Root Vectors Group").property("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size");
}

// A header band with only its top corners rounded: a rounded rect plus a square one over its lower part.
function topRound(comp, name, x, y, w, h, r, color) {
    var L = comp.layers.addShape();
    L.name = name;
    L.transform.position.setValue([(x + w / 2) * K, (y + h / 2) * K]);
    var g = L.property("ADBE Root Vectors Group");
    var a = g.addProperty("ADBE Vector Shape - Rect");
    a.property("ADBE Vector Rect Size").setValue([w * K, h * K]);
    a.property("ADBE Vector Rect Roundness").setValue(r * K);
    var b = g.addProperty("ADBE Vector Shape - Rect");
    b.property("ADBE Vector Rect Size").setValue([w * K, (h - r) * K]);
    b.property("ADBE Vector Rect Position").setValue([0, r / 2 * K]);
    paint(g, {fill: color});
    return L;
}

function circle(comp, name, cx, cy, r, o) {
    var L = comp.layers.addShape();
    L.name = name;
    L.transform.position.setValue([cx * K, cy * K]);
    var g = L.property("ADBE Root Vectors Group");
    g.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([2 * r * K, 2 * r * K]);
    paint(g, o);
    return L;
}

// SVG path data (absolute M L H V C Z) to subpaths {v, i, o, closed}, with tangents relative as Shape wants them.
function parseD(d) {
    var tok = d.match(/[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?/g), subs = [], cur = null, x = 0, y = 0, cmd = "", k = 0;
    function num() { return parseFloat(tok[k++]); }
    function add() { cur.v.push([x, y]); cur.i.push([0, 0]); cur.o.push([0, 0]); }
    while (k < tok.length) {
        if (/[A-Za-z]/.test(tok[k])) cmd = tok[k++];
        if (cmd == "M") { x = num(); y = num(); cur = {v: [[x, y]], i: [[0, 0]], o: [[0, 0]], closed: false}; subs.push(cur); cmd = "L"; }
        else if (cmd == "L") { x = num(); y = num(); add(); }
        else if (cmd == "H") { x = num(); add(); }
        else if (cmd == "V") { y = num(); add(); }
        else if (cmd == "C") {
            var x1 = num(), y1 = num(), x2 = num(), y2 = num(), n = cur.v.length - 1;
            cur.o[n] = [x1 - cur.v[n][0], y1 - cur.v[n][1]];
            x = num(); y = num();
            cur.v.push([x, y]); cur.i.push([x2 - x, y2 - y]); cur.o.push([0, 0]);
        } else if (cmd == "Z") {
            var last = cur.v.length - 1;
            if (last > 0 && cur.v[last][0] == cur.v[0][0] && cur.v[last][1] == cur.v[0][1]) {
                cur.i[0] = cur.i[last];
                cur.v.pop(); cur.i.pop(); cur.o.pop();
            }
            cur.closed = true;
            x = cur.v[0][0]; y = cur.v[0][1];
            cmd = "";
        } else throw new Error("path command not supported: " + cmd + " in " + d);
    }
    return subs;
}

// Subpaths into a contents group, mapped by (scale, offset) into layer space.
function addPaths(g, subs, s, ox, oy) {
    for (var i = 0; i < subs.length; i++) {
        var sh = new Shape(), v = [], it = [], ot = [];
        for (var j = 0; j < subs[i].v.length; j++) {
            v.push([subs[i].v[j][0] * s + ox, subs[i].v[j][1] * s + oy]);
            it.push([subs[i].i[j][0] * s, subs[i].i[j][1] * s]);
            ot.push([subs[i].o[j][0] * s, subs[i].o[j][1] * s]);
        }
        sh.vertices = v; sh.inTangents = it; sh.outTangents = ot; sh.closed = subs[i].closed;
        g.addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(sh);
    }
}

// A path in comp coordinates: an SVG d string, or a list of point lists. o.trim adds Trim Paths to draw it on.
function path(comp, name, d, o) {
    var subs = typeof d == "string" ? parseD(d) : [];
    if (typeof d != "string")
        for (var i = 0; i < d.length; i++) {
            var z = {v: [], i: [], o: [], closed: !!o.closed};
            for (var j = 0; j < d[i].length; j++) { z.v.push(d[i][j]); z.i.push([0, 0]); z.o.push([0, 0]); }
            subs.push(z);
        }
    var L = comp.layers.addShape();
    L.name = name;
    L.transform.position.setValue([0, 0]);
    var g = L.property("ADBE Root Vectors Group");
    addPaths(g, subs, K, 0, 0);
    paint(g, o);
    if (o.trim) g.addProperty("ADBE Vector Filter - Trim");
    return L;
}

function trimEnd(L) {
    return L.property("ADBE Root Vectors Group").property("ADBE Vector Filter - Trim").property("ADBE Vector Trim End");
}

// Arrow like the storyboard's marker (refX 8 of 10, 5 stroke widths): a line drawn on, and its head. Returns [line, head].
function arrow(comp, name, d, color, sw, o) {
    o = o || {};
    var subs = typeof d == "string" ? parseD(d) : [{v: d, i: [], o: []}];
    var sp = subs[subs.length - 1], n = sp.v.length - 1, end = sp.v[n];
    var dx = -(sp.i[n] ? sp.i[n][0] : 0), dy = -(sp.i[n] ? sp.i[n][1] : 0);
    if (dx == 0 && dy == 0) { dx = end[0] - sp.v[n - 1][0]; dy = end[1] - sp.v[n - 1][1]; }
    var len = Math.sqrt(dx * dx + dy * dy), ux = dx / len, uy = dy / len, s = sw / 2;
    var tipX = end[0] + ux * 2 * s, tipY = end[1] + uy * 2 * s, bx = end[0] - ux * 8 * s, by = end[1] - uy * 8 * s;
    var line = path(comp, name, d, {stroke: color, sw: sw, round: true, dash: o.dash, trim: true});
    var head = path(comp, name + " head", [[[tipX, tipY], [bx - uy * 5 * s, by + ux * 5 * s], [bx + uy * 5 * s, by - ux * 5 * s]]],
                    {fill: color, closed: true});
    return [line, head];
}

// Green tick: a filled circle and a white check drawn on. Returns [ring, mark].
function tick(comp, name, cx, cy, s) {
    s = s || 10;
    var ring = circle(comp, name + " ring", cx, cy, s, {fill: P.green});
    var mark = path(comp, name + " mark", [[[cx - s * 0.45, cy], [cx - s * 0.13, cy + s * 0.32], [cx + s * 0.47, cy - s * 0.3]]],
                    {stroke: "#FFFFFF", sw: 2.4, round: true, trim: true});
    return [ring, mark];
}

// Pill chip centred on cx, top at y: mono semibold label. Returns [pill, label].
function chip(comp, name, cx, y, label, color, o) {
    o = o || {};
    var sz = o.size || 22, w = Math.round(label.length * sz * 0.62 + 36), h = sz + 22;
    var pill = rect(comp, name, cx - w / 2, y, w, h, {fill: color, rx: h / 2});
    var l = txt(comp, name + " label", label, cx, y + h / 2 + sz * 0.36, {f: "m", size: sz, w: 600, a: "middle", fill: o.ink || P.ink});
    return [pill, l];
}

// An icon from icons/v1 (ICONS[name] = its SVG text), s units square at (x, y). The layer sits at its centre.
function icon(comp, name, x, y, s) {
    s = s || 56;
    var L = comp.layers.addShape();
    L.name = "icon " + name;
    L.transform.position.setValue([(x + s / 2) * K, (y + s / 2) * K]);
    var root = L.property("ADBE Root Vectors Group"), f = s / 64 * K, re = /<path\b([^>]*)>/g, m, all = [];
    function attr(a, n) { var r = new RegExp("\\s" + n + "=\"([^\"]*)\"").exec(a); return r ? r[1] : null; }
    while ((m = re.exec(ICONS[name])) !== null) all.push(m[1]);
    // SVG paints later paths on top; a group added later sits below, so add them last to first.
    for (var p = all.length - 1; p >= 0; p--) {
        var a = all[p], g = root.addProperty("ADBE Vector Group").property("ADBE Vectors Group");
        addPaths(g, parseD(attr(a, "d")), f, -s / 2 * K, -s / 2 * K);
        var fill = attr(a, "fill"), stroke = attr(a, "stroke");
        paint(g, {fill: fill && fill != "none" ? fill.toUpperCase() : null, evenodd: attr(a, "fill-rule") == "evenodd",
                  stroke: stroke && stroke != "none" ? stroke.toUpperCase() : null,
                  sw: parseFloat(attr(a, "stroke-width") || "0") * s / 64, round: true});
    }
    return L;
}

// ---- motion --------------------------------------------------------------

// Keys with ease-out arrival (fast start, settle, no overshoot).
function keys(prop, ks) {
    for (var i = 0; i < ks.length; i++) prop.setValueAtTime(ks[i][0], ks[i][1]);
    for (var k = 1; k <= prop.numKeys; k++)
        prop.setTemporalEaseAtKey(k, [new KeyframeEase(0, 85)], [new KeyframeEase(0, 0.1)]);
}

function holdKeys(prop, ks) {
    for (var i = 0; i < ks.length; i++) prop.setValueAtTime(ks[i][0], ks[i][1]);
    for (var k = 1; k <= prop.numKeys; k++)
        prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
}

// Fade layers in at t; rise = storyboard units they slide up from (parented layers ride their parent).
// t null: already on screen when the scene opens (it carries on from the scene before).
function fadeIn(layers, t, rise) {
    if (t == null) return;
    for (var i = 0; i < layers.length; i++) {
        var L = layers[i];
        keys(L.transform.opacity, [[0, 0], [t, 0], [t + EASE, 100]]);
        if (rise && !L.parent) {
            var p = L.transform.position.valueAtTime(t, false);
            keys(L.transform.position, [[t, [p[0], p[1] + rise * K]], [t + EASE, [p[0], p[1]]]]);
        }
    }
}

function fadeTo(layers, t, v) {
    for (var i = 0; i < layers.length; i++) {
        var o = layers[i].transform.opacity;
        keys(o, [[t, o.valueAtTime(t, false)], [t + EASE, v]]);
    }
}

// One idea on screen: in at tIn, out by tOut. An entry too late to finish before the exit starts comes in
// earlier, so it never fades in after its own fade-out and stays.
function show(layers, tIn, tOut, rise) {
    if (tOut != null && tIn > tOut - 2 * EASE) tIn = Math.max(0, tOut - 2 * EASE);
    fadeIn(layers, tIn, rise);
    if (tOut != null) fadeTo(layers, tOut - EASE, 0);
}

// Move a layer to storyboard point (x, y) over [t, t + dur].
function moveTo(L, t, x, y, dur) {
    var p = L.transform.position;
    keys(p, [[t, p.valueAtTime(t, false)], [t + (dur || EASE), [x * K, y * K]]]);
}

// Shift layers by (dx, dy) storyboard units over [t, t + dur].
function shift(layers, t, dx, dy, dur) {
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].parent) continue;
        var p = layers[i].transform.position, v = p.valueAtTime(t, false);
        keys(p, [[t, v], [t + (dur || EASE), [v[0] + dx * K, v[1] + dy * K]]]);
    }
}

function scaleTo(L, t, pct, dur) {
    var s = L.transform.scale;
    keys(s, [[t, s.valueAtTime(t, false)], [t + (dur || EASE), [pct, pct]]]);
}

// Dim layers to v% from t and keep them there until tOut, whose fade-out key would otherwise bring them back to 100.
function dimHold(layers, t, v, tOut) {
    for (var i = 0; i < layers.length; i++) {
        var o = layers[i].transform.opacity;
        keys(o, [[t, o.valueAtTime(t, false)], [t + EASE, v]]);
        if (tOut != null) keys(o, [[tOut - EASE, v]]);
    }
}

function drawOn(L, t, dur) {
    if (t == null) return;
    keys(trimEnd(L), [[0, 0], [t, 0], [t + (dur || EASE), 100]]);
}

function parentAll(layers, p) {
    for (var i = 0; i < layers.length; i++) layers[i].parent = p;
}

// ---- cues: beats start on words of the narration (WORDS = [{word, start, end}]) ----

function norm(w) {
    return w.toLowerCase().replace(/[^a-z0-9%']/g, "");
}

// Index of the first word of `phrase` at or after time `after`.
function cueIndex(phrase, after) {
    var p = phrase.split(" ");
    for (var i = 0; i < WORDS.length; i++) {
        if (WORDS[i].start < (after || 0)) continue;
        for (var j = 0; j < p.length && i + j < WORDS.length && norm(WORDS[i + j].word) == norm(p[j]); j++) {}
        if (j == p.length) return i;
    }
    throw new Error("cue not found in the narration: \"" + phrase + "\"");
}

function cue(phrase, after) { return WORDS[cueIndex(phrase, after)].start; }

function cueEnd(phrase, after) { return WORDS[cueIndex(phrase, after) + phrase.split(" ").length - 1].end; }

function narrationEnd() { return WORDS[WORDS.length - 1].end; }

// ---- scene and project ---------------------------------------------------

function findItem(name) {
    for (var i = 1; i <= app.project.numItems; i++) if (app.project.item(i).name == name) return app.project.item(i);
    return null;
}

// A fresh scene comp (an older build of it is removed), with its background and narration.
function newScene(name, dur, audioPath, bg) {
    var old = findItem(name);
    if (old) old.remove();
    var comp = app.project.items.addComp(name, 1920, 1080, 1, dur, 30);
    comp.bgColor = rgb(bg);
    comp.layers.addSolid(rgb(bg), "background", 1920, 1080, 1, dur);
    // Always import by full path: reusing a project item by file name silently picked an OLD soundtrack
    // with the same name from another folder (see docs/04-artcraft-linux.md).
    var audio = app.project.importFile(new ImportOptions(new File(audioPath)));
    comp.layers.add(audio).name = "narration";
    return comp;
}

function marker(comp, t, label) {
    comp.markerProperty.setValueAtTime(t, new MarkerValue(label));
}

// Places the scene in the master comp, after the scene before it.
function placeInMaster(comp, prevName) {
    var master = findItem("orbit_rows");
    master.frameRate = 30;
    if (master.duration < 600) master.duration = 600;
    var start = 0;
    for (var i = 1; i <= master.numLayers; i++) if (master.layer(i).name == prevName) start = master.layer(i).outPoint;
    var L = master.layers.add(comp);
    L.startTime = start;
    master.workAreaStart = 0;
    master.workAreaDuration = master.duration;
}

// ---- shared parts --------------------------------------------------------

// Context label, top left of the stage: a coral dot and a few plain words in purple. dx = stage offset.
function contextLabel(comp, text, dx) {
    return [circle(comp, "context dot", 46 + dx, 40, 5, {fill: P.coral}),
            txt(comp, "context label", text, 60 + dx, 45, {size: 14, w: 600, fill: P.purple})];
}

// Words laid out from (x, y), one layer per word. Returns [{layer, text, x, y}].
function wordRow(comp, prefix, list, x, y, o) {
    var space = measure(comp, "a a", o) - measure(comp, "aa", o), out = [];
    for (var i = 0; i < list.length; i++) {
        var L = txt(comp, prefix + " " + list[i], list[i], x, y, o);
        out.push({layer: L, text: list[i], x: x, y: y});
        x += textRight(L) + space;
    }
    return out;
}

// Type words letter by letter; spans[i] = [t0, t1] for word i. A teal bar cursor (3 x 22, as drawn) follows
// the caret, blinks from tShow until typing starts and after it ends, and goes at tHide.
function typeWords(comp, ws, spans, tShow, tHide) {
    var cur = rect(comp, "cursor", 0, 0, 3, 22, {fill: P.teal, rx: 0});
    var curX = [[0, [(ws[0].x + 1.5) * K, (ws[0].y - 5) * K]]], curOn = [[0, 0]];
    for (var i = 0; i < ws.length; i++) {
        var w = ws[i], st = w.layer.property("Source Text"), n = w.text.length, rights = [];
        for (var k = 1; k <= n; k++) { setText(w.layer, w.text.substr(0, k)); rights.push(textRight(w.layer)); }
        var t0 = spans[i][0], dt = (spans[i][1] - t0) / n, ks = [[0, " "]];
        for (k = 1; k <= n; k++) {
            var tk = t0 + (k - 1) * dt;
            ks.push([tk, w.text.substr(0, k)]);
            curX.push([tk, [(w.x + rights[k - 1] + 3) * K, (w.y - 5) * K]]);
        }
        holdKeys(st, ks);
    }
    var tStart = spans[0][0], tEnd = spans[spans.length - 1][1];
    holdKeys(cur.transform.position, curX);
    for (var t = tShow; t < tStart; t += 1) { curOn.push([t, 100]); if (t + 0.5 < tStart) curOn.push([t + 0.5, 0]); }
    curOn.push([tStart, 100]);
    for (t = tEnd + 0.5; t < tHide; t += 1) { curOn.push([t, 0]); if (t + 0.5 < tHide) curOn.push([t + 0.5, 100]); }
    curOn.push([tHide, 0]);
    holdKeys(cur.transform.opacity, curOn);
    return cur;
}

// ---- the panel (right third, white card), persistent across scenes -------

var REQUEST = ["Lower", "the", "price", "of", "the", "Logitech", "products", "under", "50", "by", "10%,", "and", "show", "them", "sorted", "by", "price."];
// The request block's layout, the same in every scene: three lines 22 px apart, the steps below.
var LAYOUT = {lines: [[0, 5], [6, 10], [11, 16]], pitch: 22, stepsLabel: 172, steps: 196};
var STEP_NAMES = ["Coreference", "Split", "Action", "Values", "Table", "Parts", "Rows", "Formula", "Ledger", "Build"];
var PANEL = [];      // every panel layer, so the panel can slide as one

// The card and "THE PROMPT" label; slides in from the right at tIn.
function panelCard(comp, tIn) {
    var card = rect(comp, "panel", 632, 20, 308, 500, {rx: 18});
    var label = txt(comp, "panel request label", "THE PROMPT", 656, 52, {size: 10.5, f: "m", w: 600, fill: P.purple});
    PANEL.push(card, label);
    if (tIn != null) slideIn([card, label], tIn, 340);
    return card;
}

function slideIn(layers, t, dx) {
    for (var i = 0; i < layers.length; i++) {
        var p = layers[i].transform.position.valueAtTime(t, false);
        keys(layers[i].transform.position, [[t, [p[0] + dx * K, p[1]]], [t + 0.4, p]]);
        keys(layers[i].transform.opacity, [[0, 0], [t, 0], [t + 0.25, 100]]);
    }
}

// Where each request word sits in the panel: 15 px Poppins, lines from (656, 80) as LAYOUT says.
function requestSlots(comp) {
    var o = {size: 15}, space = measure(comp, "a a", o) - measure(comp, "aa", o), slots = [];
    for (var l = 0; l < LAYOUT.lines.length; l++) {
        var x = 656;
        for (var i = LAYOUT.lines[l][0]; i <= LAYOUT.lines[l][1]; i++) {
            var w = measure(comp, REQUEST[i], o);
            slots.push({x: x, y: 80 + l * LAYOUT.pitch, line: l, w: w});
            x += w + space;
        }
    }
    return slots;
}

// Words being discussed get a coral marker behind them (45%, 3 px padding: word gaps are ~4 px, 4 px corners); the text
// itself never changes, so nothing moves and it stays readable. In over 300 ms at tOn, out by tOff.
function highlight(comp, req, idxs, tOn, tOff) {
    for (var n = 0; n < idxs.length; n++) {
        var w = req[idxs[n]];
        var mk = rect(comp, "request marker " + w.text, w.x - 3, w.y - 15, w.w + 6, 23, {fill: P.coral, op: 0.45, rx: 4});
        mk.moveAfter(w.layer);
        keys(mk.transform.opacity, [[0, 0], [tOn, 0], [tOn + 0.3, 100], [tOff - 0.3, 100], [tOff, 0]]);
    }
}

// The request already in the panel (scenes after the first): one layer per word at its slot. Returns the words.
function panelRequest(comp) {
    var slots = requestSlots(comp), req = [];
    for (var i = 0; i < REQUEST.length; i++) {
        var L = txt(comp, "request " + REQUEST[i], REQUEST[i], slots[i].x, slots[i].y, {size: 15});
        req.push({layer: L, text: REQUEST[i], x: slots[i].x, y: slots[i].y, line: slots[i].line, w: slots[i].w});
        PANEL.push(L);
    }
    return req;
}

var STEP_DY = 27;    // room between the steps of "Where we are"

// "WHERE WE ARE": the ten steps on a lavender connector, fading in row by row from t (null: there from the start).
// Returns the rows, for stepOn and stepDone.
function panelSteps(comp, t) {
    var ls = [txt(comp, "panel steps label", "WHERE WE ARE", 656, LAYOUT.stepsLabel, {size: 10.5, f: "m", w: 600, fill: P.purple}),
              path(comp, "panel steps connector", [[[667, LAYOUT.steps], [667, LAYOUT.steps + (STEP_NAMES.length - 1) * STEP_DY]]], {stroke: P.lav, sw: 3})];
    if (t != null) fadeIn(ls, t);
    var rows = [];
    for (var i = 0; i < STEP_NAMES.length; i++) {
        var y = LAYOUT.steps + i * STEP_DY;
        var row = [circle(comp, "panel step " + (i + 1), 667, y, 8, {fill: P.paper, stroke: P.lav, sw: 2.5}),
                   txt(comp, "panel step " + (i + 1) + " number", String(i + 1), 667, y + 3.5, {size: 9, f: "m", w: 600, a: "middle", fill: P.purple}),
                   txt(comp, "panel step " + (i + 1) + " name", STEP_NAMES[i], 686, y + 5, {size: 13, fill: P.mute})];
        if (t != null) fadeIn(row, t + 0.05 * i, 4);
        rows.push({y: y, layers: row});
        ls = ls.concat(row);
    }
    PANEL = PANEL.concat(ls);
    return rows;
}

// The current step: filled teal, white number, its name in ink semibold; it fades in over the plain row
// (tOn null: lit from the scene's start).
function stepOn(comp, rows, i, tOn, tOff) {
    var y = rows[i].y;
    var lit = [circle(comp, "panel step " + (i + 1) + " on", 667, y, 8, {fill: P.teal, stroke: P.teal, sw: 2.5}),
               txt(comp, "panel step " + (i + 1) + " on number", String(i + 1), 667, y + 3.5, {size: 9, f: "m", w: 600, a: "middle", fill: "#FFFFFF"}),
               txt(comp, "panel step " + (i + 1) + " on name", STEP_NAMES[i], 686, y + 5, {size: 13, w: 600})];
    show(lit, tOn, tOff);
    if (tOn == null) rows[i].layers[2].transform.opacity.setValue(0);
    else fadeTo([rows[i].layers[2]], tOn, 0);
    if (tOff != null) fadeTo([rows[i].layers[2]], tOff - EASE, 100);
    PANEL = PANEL.concat(lit);
    return lit;
}

// A finished step: a small green tick at the right of its row (t null: ticked from the scene's start).
function stepDone(comp, rows, i, t) {
    var tk = tick(comp, "panel step " + (i + 1) + " done", 912, rows[i].y, 7);
    fadeIn([tk[0]], t);
    fadeIn([tk[1]], t);
    drawOn(tk[1], t + 0.1, 0.25);
    PANEL = PANEL.concat(tk);
    return tk;
}

// A fact tag under request words from..to, shown only while its fact is found: JetBrains Mono 10.5 teal on a
// 14% teal pill over an opaque white one (so it can cover the next line cleanly), 16 tall, 4 corners, 6 px under
// the baseline, left-aligned to the first word, or right-aligned to the last when it would pass the panel's inner
// edge (x 924); a 1.5 px teal underline ties it to the words. In with a 6 px rise at t, held `hold` s (default 2),
// then out. Returns {pill, cx, cy, w} (cx, cy: the pill's centre).
function tag(comp, req, from, to, text, t, hold) {
    var a = req[from], b = req[to], w = measure(comp, text, {size: 10.5, f: "m"}) + 12;
    var x = a.x + w > 924 ? b.x + b.w - w : a.x, y = a.y + 6, tOut = t + EASE + (hold || 2) + EASE;
    var pill = rect(comp, "tag " + text, x, y, w, 16, {fill: "#FFFFFF", rx: 4});
    var parts = [rect(comp, "tag " + text + " tint", x, y, w, 16, {fill: P.teal, op: 0.14, rx: 4}),
                 txt(comp, "tag " + text + " text", text, x + 6, y + 11.5, {size: 10.5, f: "m", fill: P.teal})];
    parentAll(parts, pill);
    var line = path(comp, "tag " + text + " underline", [[[a.x, a.y + 3.5], [b.x + b.w, b.y + 3.5]]], {stroke: P.teal, sw: 1.5});
    show([pill].concat(parts), t, tOut, 6);
    show([line], t, tOut);
    PANEL.push(pill, line);
    PANEL = PANEL.concat(parts);
    return {pill: pill, cx: x + w / 2, cy: y + 8, w: w};
}

// A tag that forms on the stage at (x, y), 2.2x its size, at t, then flies into its place under request words
// from..to and becomes the panel's tag (from t + 1.1, held `hold` s). Returns the tag.
function flyTag(comp, req, from, to, text, x, y, t, hold) {
    var tg = tag(comp, req, from, to, text, t + 1.1, hold), Z = 2.2;
    var fly = rect(comp, "tag flight " + text, x - tg.w * Z / 2, y - 8 * Z, tg.w * Z, 16 * Z, {fill: "#FFFFFF", rx: 4 * Z});
    var parts = [rect(comp, "tag flight " + text + " tint", x - tg.w * Z / 2, y - 8 * Z, tg.w * Z, 16 * Z, {fill: P.teal, op: 0.14, rx: 4 * Z}),
                 txt(comp, "tag flight " + text + " text", text, x, y + 3.5 * Z, {size: 10.5 * Z, f: "m", fill: P.teal, a: "middle"})];
    parentAll(parts, fly);
    fadeIn([fly].concat(parts), t, 8);
    moveTo(fly, t + 0.6, tg.cx, tg.cy, 0.6);
    scaleTo(fly, t + 0.6, 100 / Z, 0.6);
    fadeTo([fly].concat(parts), t + 1.1, 0);
    return tg;
}

// ---- the sentence as word chips on the stage (scenes 2 and 3) ----

// Three lines of white chips centred on the stage, in from t (one by one), out by tOut. Returns {pos, chips, texts}.
function wordChips(comp, t, tOut) {
    var rowsW = [[0, 3], [4, 8], [9, 16]], pos = [], chips = [], texts = [];
    function ww(i) { return Math.round(REQUEST[i].length * 9.6 + 18); }
    for (var r = 0; r < rowsW.length; r++) {
        var tw = 0;
        for (var i = rowsW[r][0]; i <= rowsW[r][1]; i++) tw += ww(i) + 8;
        var x = 320 - (tw - 8) / 2;
        for (i = rowsW[r][0]; i <= rowsW[r][1]; i++) { pos[i] = {x: x, y: 150 + r * 58, w: ww(i)}; x += ww(i) + 8; }
    }
    for (i = 0; i < REQUEST.length; i++) {
        chips.push(rect(comp, "word " + REQUEST[i], pos[i].x, pos[i].y, pos[i].w, 34, {rx: 8}));
        texts.push(txt(comp, "word " + REQUEST[i] + " text", REQUEST[i], pos[i].x + pos[i].w / 2, pos[i].y + 23, {size: 17, a: "middle"}));
        show([chips[i], texts[i]], t + 0.03 * i, tOut, 6);
    }
    return {pos: pos, chips: chips, texts: texts};
}

// An outline round chips a..b: solid, or dashed 6/5.
function wordOutline(comp, pos, a, b, color, dashed) {
    return rect(comp, "outline " + REQUEST[a] + "-" + REQUEST[b] + (dashed ? "" : " solid"), pos[a].x - 6, pos[a].y - 6,
                pos[b].x + pos[b].w - pos[a].x + 12, 46, {fill: null, stroke: color, sw: 2.5, rx: 12, dash: dashed ? [6, 5] : null});
}

// The two request cards on the stage (scenes 3 and 4): request 1 on top, request 2 below, with "them" in bold.
// Returns {layers, them} (them: the layer of the word, to point at).
function requestCards(comp) {
    var o = {size: 15}, sx = 60, them = [], gap = measure(comp, "a a", o) - measure(comp, "aa", o);
    var ls = [rect(comp, "card request 1", 40, 110, 560, 64, {stroke: P.teal}),
              txt(comp, "card request 1 label", "request 1", 60, 134, {size: 11, f: "m", w: 600, fill: P.purple}),
              txt(comp, "card request 1 text", "Lower the price of the Logitech products under 50 by 10%", 60, 158, o),
              rect(comp, "card request 2", 40, 300, 560, 64, {stroke: P.teal}),
              txt(comp, "card request 2 label", "request 2", 60, 324, {size: 11, f: "m", w: 600, fill: P.purple})];
    var parts = [["show", 400], ["them", 700], ["sorted by price", 400]];
    for (var k = 0; k < parts.length; k++) {                        // "them" in bold within the line, at measured offsets
        them.push(txt(comp, "card request 2 text " + k, parts[k][0], sx, 348, {size: 15, w: parts[k][1]}));
        sx += textRight(them[k]) + gap;
    }
    return {layers: ls.concat(them), them: them[1]};
}

// A worker icon acting: one short swell and back.
function pulse(L, t) {
    var s = L.transform.scale;
    keys(s, [[t, [100, 100]], [t + 0.25, [118, 118]], [t + 0.55, [100, 100]]]);
}

// The panel leaves to the right (only for the title card at the end of scene 1).
function panelOut(t) {
    shift(PANEL, t, 340, 0, 0.4);
    fadeTo(PANEL, t + 0.05, 0);
}
