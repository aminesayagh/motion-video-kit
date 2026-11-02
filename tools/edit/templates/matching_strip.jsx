// ==== Scene 5 "Step 4, Matching", v8 (narration v9, take v10; no closing summary): every element is an editable layer; each beat starts on a
// narration cue. No storyboard for this narration: layout follows the approved v2 build (panel, icons, strip,
// model pills, dot wall). Elements that stay on screen are built once and never redrawn.
// AUDIO, WORDS and ICONS are defined by tools/edit/build_scene.py before this file (AUDIO = full path of the scene's soundtrack).
var T = {
 step: cue('Step four matching'), lit: cue('four'), body: cue('body'),
 what: cue('what it does'), which: cue('which rows'), how: cue('and how those rows'),
 matches: cue('It matches them'), oValues: cue('first the values'), oTables: cue('then the tables'),
 oColumns: cue('then the columns'), oOps: cue('and last the operations'),
 values: cue('First the values', cue('and last the operations')), knows: cue('The tool already knows'), created: cue('created holds'),
 status: cue('status and brand'), brand: cue('brand each'), name: cue('name is free'),
 looks: cue('So it looks'), casa: cue('Casa is one'), draft: cue('Draft is one'), sept: cue('September is no'),
 becomes: cue('Each value becomes'),
 tables: cue('Next the tables'), r1: cue('Request one works'), r2: cue('Request two names'), writes: cue('A change always writes'),
 sqlite: cue('that is how SQLite works'), like: cue('like the sales'), bring: cue('You can also bring'), compares: cue('the tool compares'), update: cue('can update'),
 add: cue("add what you don't have"), anything: cue('or do anything else'), enough: cue('Here products is enough'),
 columns: cue('Then the columns', cue('Here products is enough')), grammar: cue('A grammar reader'), meaning: cue('a meaning model'), created2: cue('created is the creation'),
 ops: cue('Last the operations', cue('created is the creation')), catalog: cue('The catalog lists'), on: cue('and sixty-five'), forEach: cue('For each change'),
 keeps: cue('keeps the ten'), ten: cue('ten closest'), picks: cue('Jev picks'), here: cue('here set a value'),
 end: narrationEnd()
};
T.done = cue('archive', cue('For each change'));   // step 4 ticks on "archive."
T.shrink = cueEnd('and last the operations') + 0.1;   // the order strip shrinks to the top before "First, the values"
var DUR = 97.32;   // the mix length (the voice ends with its own tail)
var C = newScene('V2 S05 Matching v8', DUR, AUDIO, P.bgA);

function tx(s, x, y, sz, fill, w, mono, mid) { return txt(C, 's5 ' + s, s, x, y, {size: sz, fill: fill || P.ink, w: w || 400, f: mono ? 'm' : 'h', a: mid ? 'middle' : 'start'}); }
function R(n, x, y, w, h, o) { return rect(C, n, x, y, w, h, o); }
function inAt(ls, t, rise) { fadeIn(ls, t, rise); return ls; }
function outAt(ls, t) { fadeTo(ls, t - EASE, 0); }
function mw(s, sz, w, mono) { return measure(C, s, {size: sz, w: w || 400, f: mono ? 'm' : 'h'}); }
// An arrow drawn on at t (line traced in 350 ms, its head after). Returns [line, head].
function arr(n, d, color, sw, t) {
 var a = arrow(C, n, d, color, sw);
 keys(a[0].transform.opacity, [[0, 0], [t, 0], [t + 0.02, 100]]);
 drawOn(a[0], t, 0.35);
 keys(a[1].transform.opacity, [[0, 0], [t + 0.25, 0], [t + 0.4, 100]]);
 return a;
}
function num(n, cx, cy, r, s, sz, fill) { return [circle(C, 'number ' + n + ' circle', cx, cy, r, {fill: fill || P.teal}), tx(String(s), cx, cy + sz * 0.38, sz, '#FFFFFF', 700, true, true)]; }
// A model chip: white pill, purple 1.5 outline, mono semibold label; its width is the measured text plus 10 each side.
function modelPill(name, x, y, label) {
 var w = mw(label, 10.5, 600, true) + 20;
 return {w: w, layers: [R('model ' + name, x, y, w, 22, {stroke: P.purple, sw: 1.5, rx: 11}), tx(label, x + 10, y + 15, 10.5, P.purple, 600, true)]};
}

// ---- persistent: the right panel (plain prompt; steps 1-3 done, step 4 current) and the top-right icons ----
var STEPS = ['Coreference', 'Split', 'Action', 'Matching', 'Parameter', 'Operation'];
R('panel', 632, 20, 308, 500, {rx: 18});
tx('THE PROMPT', 656, 52, 10.5, P.purple, 600, true);
tx('Archive the draft Casa products', 656, 80, 15);
tx('created in September,', 656, 102, 15);
tx('and show them.', 656, 124, 15);
tx('WHERE WE ARE', 656, 172, 10.5, P.purple, 600, true);
path(C, 'panel steps connector', [[[667, 204], [667, 384]]], {stroke: P.lav, sw: 3});
var stepName = [], i;
for (i = 0; i < 6; i++) {
 var y = 204 + i * 36;
 circle(C, 'panel step ' + (i + 1), 667, y, 9, {fill: P.paper, stroke: P.lav, sw: 2.5});
 tx(String(i + 1), 667, y + 4, 10, P.purple, 600, true, true);
 stepName.push(tx(STEPS[i], 690, y + 5, 14, i < 3 ? P.ink : P.mute, 400));
}
function lit(i) {
 var y = 204 + i * 36;
 return [circle(C, 'panel step ' + (i + 1) + ' on', 667, y, 9, {fill: P.teal, stroke: P.teal, sw: 2.5}),
         tx(String(i + 1), 667, y + 4, 10, '#FFFFFF', 600, true, true), tx(STEPS[i], 690, y + 5, 14, P.ink, 600)];
}
// Scene 4 ended on step 3 lit (and ticked): it hands over to step 4 on the word "four".
var lit3 = lit(2), lit4 = lit(3);
stepName[2].transform.opacity.setValue(0);
keys(stepName[2].transform.opacity, [[T.lit, 0], [T.lit + EASE, 100]]);
fadeTo(lit3, T.lit, 0);
inAt(lit4, T.lit);
fadeTo([stepName[3]], T.lit, 0);
tick(C, 'panel step 1 done', 912, 204, 8);
tick(C, 'panel step 2 done', 912, 240, 8);
tick(C, 'panel step 3 done', 912, 276, 8);
var done4 = tick(C, 'panel step 4 done', 912, 312, 8);
inAt([done4[0]], T.done); keys(done4[1].transform.opacity, [[0, 0], [T.done, 0], [T.done + 0.05, 100]]); drawOn(done4[1], T.done + 0.1, 0.25);
var jev = icon(C, 'jev', 512, 16, 36);
icon(C, 'code', 556, 16, 36);

// ---- context label ----
var lab = contextLabel(C, 'Matching the words to the table', 0);
inAt([lab[1]], 0);

// ---- 1. step card ----
var s1 = [R('step card', 170, 210, 300, 90, {stroke: P.teal, sw: 3})].concat(num('step', 215, 255, 22, 4, 22), [tx('Matching', 252, 264, 26, P.ink, 700)]);
inAt(s1, 0, 6); outAt(s1, T.body);

// ---- 2. the body of a request: three pieces on their words; the order strip, each pill lit on its word ----
var CX = 315;                                          // the stage's centre (x 20-610)
var bodyCap = [tx('the body of a request', CX, 160, 14, P.mute, 600, false, true)];
inAt(bodyCap, T.body, 4);
var PIECES = [['what it does', P.purple, T.what], ['which rows', P.teal, T.which], ['how the rows are arranged', P.coral, T.how]];
var pw = [], ptot = 40, pieces = [];
for (i = 0; i < 3; i++) { pw[i] = mw(PIECES[i][0], 15, 600) + 40; ptot += pw[i]; }
var px = CX - ptot / 2;
for (i = 0; i < 3; i++) {
 var pc = [R('piece ' + PIECES[i][0], px, 180, pw[i], 60, {stroke: PIECES[i][1], sw: 2.5}), tx(PIECES[i][0], px + pw[i] / 2, 210 + 15 * 0.36, 15, P.ink, 600, false, true)];
 inAt(pc, PIECES[i][2], 6);
 pieces = pieces.concat(pc);
 px += pw[i] + 20;
}
var ORDER = [['values', T.oValues], ['tables', T.oTables], ['columns', T.oColumns], ['operations', T.oOps]];
// The small strip at the top of the stage (y 58-78, under the context label): measured pills, small arrows between.
var sx = 40, strip = [], stripHl = [], stripC = [], stripW = [];
for (i = 0; i < 4; i++) {
 var sw = mw(ORDER[i][0], 11, 600) + 20;
 strip.push(R('strip ' + ORDER[i][0], sx, 58, sw, 20, {stroke: P.faint, sw: 1.5, rx: 10}), tx(ORDER[i][0], sx + sw / 2, 72, 11, P.mute, 600, false, true));
 stripHl.push([R('strip ' + ORDER[i][0] + ' current', sx, 58, sw, 20, {fill: P.teal, stroke: P.teal, sw: 1.5, rx: 10}), tx(ORDER[i][0], sx + sw / 2, 72, 11, '#FFFFFF', 600, false, true)]);
 stripC.push([sx + sw / 2, 68]); stripW.push(sw);
 sx += sw;
 if (i < 3) { strip = strip.concat(arrow(C, 'strip arrow ' + (i + 1), 'M' + (sx + 5) + ' 68H' + (sx + 15), P.ink, 1.5)); sx += 22; }
}
// The big strip: grey pills and arrows on "It matches them"; each pill lights teal on its word.
var BG = 34, bw = [], btot = 3 * BG, big = [], bigArrows = [];
for (i = 0; i < 4; i++) { bw[i] = mw(ORDER[i][0], 17, 600) + 28; btot += bw[i]; }
var bx = CX - btot / 2;
for (i = 0; i < 4; i++) {
 var base = R('order ' + ORDER[i][0], bx, 286, bw[i], 40, {stroke: P.faint, sw: 2, rx: 20});
 var bt = tx(ORDER[i][0], bx + bw[i] / 2, 306 + 17 * 0.36, 17, P.mute, 600, false, true);
 var on = R('order ' + ORDER[i][0] + ' lit', bx, 286, bw[i], 40, {fill: P.teal, stroke: P.teal, sw: 2, rx: 20});
 var ot = tx(ORDER[i][0], bx + bw[i] / 2, 306 + 17 * 0.36, 17, '#FFFFFF', 600, false, true);
 parentAll([bt, on, ot], base);
 inAt([base, bt], T.matches + 0.06 * i, 6);
 inAt([on, ot], ORDER[i][1]);
 big.push([base, bt, on, ot]);
 bx += bw[i];
 if (i < 3) { var ba = arrow(C, 'order arrow ' + (i + 1), 'M' + (bx + 8) + ' 306H' + (bx + BG - 10), P.ink, 2.5); inAt(ba, T.matches + 0.1 + 0.06 * i); bigArrows = bigArrows.concat(ba); }
 bx += BG;
}
// The shrink: each lit pill flies to its place in the small strip and scales down while it fades; the strip fades in.
for (i = 0; i < 4; i++) {
 moveTo(big[i][0], T.shrink, stripC[i][0], stripC[i][1], 0.5);
 scaleTo(big[i][0], T.shrink, 100 * stripW[i] / bw[i], 0.5);
 fadeTo(big[i], T.shrink + 0.15, 0);
}
fadeTo(bigArrows.concat(pieces, bodyCap), T.shrink, 0);
inAt(strip, T.shrink + 0.25);
// The current part's pill, from its part's start to the next one's.
var PART = [T.values, T.tables, T.columns, T.ops, null];
for (i = 0; i < 4; i++) {
 inAt(stripHl[i], PART[i]);
 if (PART[i + 1] != null) outAt(stripHl[i], PART[i + 1]);
}

// ---- 3. values: what the import knows of each column; the values go where they can live; they become conditions ----
// No table rows here: the tool uses the import profile, not the data.
var imp = [R('import card', 40, 100, 260, 190, {stroke: P.purple, sw: 2}), tx('from the import', 60, 128, 13, P.purple, 600)];
inAt(imp, T.knows, 6);
var COLS = [['created', 'dates', T.created], ['status', 'short list', T.status], ['brand', 'short list', T.brand], ['name', 'free text', T.name]];
var rowY = [], impRows = [];
for (i = 0; i < 4; i++) {
 var cy = 160 + 36 * i;
 rowY.push(cy);
 var row = [tx(COLS[i][0], 60, cy + 5, 14, P.ink, 600, true), tx(COLS[i][1], 150, cy + 5, 13, P.mute)];
 inAt(row, COLS[i][2], 4);
 impRows = impRows.concat(row);
}
// The prompt's values: yellow pills in a row under the card, then each slides next to its column on its word.
var VALS = [['Casa', 2, T.casa], ['draft', 1, T.draft], ['September', 0, T.sept]];
var vw = [], vtot = 2 * 16, vals = [], VX = 326;
for (i = 0; i < 3; i++) { vw[i] = mw(VALS[i][0], 15, 600) + 24; vtot += vw[i]; }
var vx = CX - vtot / 2;
for (i = 0; i < 3; i++) {
 var vr = R('value ' + VALS[i][0], vx, 385, vw[i], 30, {fill: P.yellow, rx: 15});
 var vt = tx(VALS[i][0], vx + vw[i] / 2, 400 + 15 * 0.36, 15, P.ink, 600, false, true);
 parentAll([vt], vr);
 inAt([vr, vt], T.looks + 0.08 * i, 6);
 moveTo(vr, VALS[i][2], VX + vw[i] / 2, rowY[VALS[i][1]], 0.5);
 vals.push([vr, vt]);
 vx += vw[i] + 16;
}
var cal = icon(C, 'calendar', VX + vw[2] + 8, rowY[0] - 13, 26);
inAt([cal], T.sept + 0.5);
// Each value becomes a condition, in its place: brand, then status, then created.
var CONDS = [['brand = Casa', 2, 0], ['status = draft', 1, 1], ['created in September', 0, 2]], conds = [];
for (i = 0; i < 3; i++) {
 var t = T.becomes + 0.15 * i, cw = mw(CONDS[i][0], 13, 600, true) + 20, ry = rowY[CONDS[i][1]];
 var cd = [R('condition ' + CONDS[i][0], VX, ry - 15, cw, 30, {stroke: P.teal, sw: 2, rx: 15}), tx(CONDS[i][0], VX + 10, ry + 13 * 0.36, 13, P.teal, 600, true)];
 fadeTo(vals[CONDS[i][2]].concat(CONDS[i][2] == 2 ? [cal] : []), t, 0);
 inAt(cd, t);
 conds = conds.concat(cd);
}
outAt(imp.concat(impRows, conds), T.tables);

// ---- 4. tables: products; request 1 works on it, request 2 on request 1's result; reads; a file; then products alone ----
function reqBox(n, x, y, w, s, label, color) {
 return [R('request ' + n + ' box', x, y, w, 44, {stroke: color, sw: 2, rx: 10})].concat(num('request ' + n, x + 22, y + 22, 12, s, 12, color), [tx(label, x + 42, y + 27, 13.5)]);
}
var prod = [R('products card', 330, 96, 120, 140, {stroke: P.teal, sw: 2.5}), topRound(C, 'products header', 330, 96, 120, 30, 12, P.teal), tx('products', 344, 116, 14, '#FFFFFF', 700)];
var PCOLS = ['name', 'brand', 'status', 'created'];
for (i = 0; i < 4; i++) prod.push(tx(PCOLS[i], 344, 150 + 22 * i, 12, P.mute, 400, true));
inAt(prod, T.tables, 6);
var q1 = reqBox('1', 40, 110, 160, 1, 'archive', P.teal);
inAt(q1, T.r1, 6);
var qa1 = arr('request 1 to products', 'M204 132H322', P.teal, 2.5, T.r1 + 0.3);
var q2 = reqBox('2', 40, 230, 160, 2, 'show them', P.coral);
inAt(q2, T.r2, 6);
var qa2 = arr('request 2 to the result of request 1', 'M120 226V162', P.coral, 2.5, T.r2 + 0.3);
var qa2l = [tx('result of request 1', 132, 198, 11.5, P.mute)];
inAt(qa2l, T.r2 + 0.5);
var writes = [tx('writes to one table', 263, 122, 11.5, P.teal, 600, false, true)];
inAt(writes, T.writes, 3);
var sqSz = Math.min(10.5, 10.5 * 112 / mw('that is how SQLite works', 10.5, 400));   // fits the 112 units between request 1's box and products
var sqlite = [tx('that is how SQLite works', 263, 150, sqSz, P.mute, 400, false, true)];
inAt(sqlite, T.sqlite, 3);
var sales = [R('sales card', 500, 96, 110, 56, {fill: null, stroke: P.purple, sw: 2, dash: [6, 5]}), tx('sales', 555, 129, 14, P.purple, 700, false, true)];
inAt(sales, T.like, 6);
var reads = arr('products reads sales', 'M454 124H492', P.purple, 2, T.like + 0.3).concat([tx('reads', 473, 115, 11, P.purple, 600, false, true)]);
inAt(reads.slice(2), T.like + 0.5);
var fm = mw("supplier's price list", 13.5), fw = 54 + fm + 16, fx = 390 - fw / 2;
var file = [R('file card', fx, 330, fw, 56, {stroke: P.ink, sw: 2}), icon(C, 'file', fx + 12, 342, 32), tx("supplier's price list", fx + 54, 363, 13.5)];
inAt(file, T.bring, 6);
var cmp = arr('file compared with products', 'M390 326V244', P.teal, 2.5, T.compares);
var upd = [tx('update', 402, 266, 12, P.teal, 600)];
inAt(upd, T.update);
var addL = [tx("add what's missing", 402, 288, 12, P.teal, 600)];
inAt(addL, T.add);
var anyL = [tx('anything you ask', 402, 310, 12, P.teal, 600)];
inAt(anyL, T.anything);
// Here, products is enough: everything else in this part steps back to 30 %.
var aside = sales.concat(reads, file, cmp, upd, addL, anyL);
fadeTo(aside, T.enough, 30);
outAt(prod.concat(q1, qa1, q2, qa2, qa2l, writes, sqlite, aside), T.columns);

// ---- 5. columns: the two models, each on its words; "created" names created_at ----
var gp1 = modelPill('grammar', 60, 120, 'grammar reader · spaCy');
var gp2 = modelPill('meaning columns', 60 + gp1.w + 16, 120, 'meaning · multilingual embeddings');
inAt(gp1.layers, T.grammar, 4); inAt(gp2.layers, T.meaning, 4);
var wcw = mw('created', 15, 600) + 30;
var wc = [R('word created', 130 - wcw / 2, 220, wcw, 33, {fill: P.coral, rx: 16.5}), tx('created', 130, 241.9, 15, P.ink, 600, false, true)];
inAt(wc, T.created2, 6);
var ca = arr('created to created_at', 'M' + (130 + wcw / 2 + 10) + ' 236.5H390', P.purple, 2.5, T.created2 + 0.15);
var ccw = mw('created_at', 14, 700) + 40;
var cbox = [R('column created_at', 400, 216.5, ccw, 40, {stroke: P.teal, sw: 2, rx: 10}), tx('created_at', 400 + ccw / 2, 241.5, 14, P.teal, 700, false, true)];
inAt(cbox, T.created2 + 0.45);
outAt(gp1.layers.concat(gp2.layers, wc, ca, cbox), T.ops);

// ---- 6. operations: the wall of 682; 65 on; the meaning search keeps ten; Jev picks one ----
// The dots: one shape layer per state, every dot an ellipse in it; a later state paints over the earlier one, so nothing redraws.
function dots(name, from, to, rad, color) {
 var L = C.layers.addShape();
 L.name = name;
 L.transform.position.setValue([0, 0]);
 var g = L.property('ADBE Root Vectors Group');
 for (var k = from; k < to; k++) {
  var e = g.addProperty('ADBE Vector Shape - Ellipse');
  e.property('ADBE Vector Ellipse Size').setValue([2 * rad * K, 2 * rad * K]);
  e.property('ADBE Vector Ellipse Position').setValue([(30 + 9 * (k % 62)) * K, (100 + 9 * Math.floor(k / 62)) * K]);
 }
 paint(g, {fill: color});
 return L;
}
var nBefore6 = C.numLayers;
var wall = dots('dots 682 operations', 0, 682, 2.3, P.faint);
var on65 = dots('dots 65 production-ready', 0, 65, 2.3, P.teal);
var ten = dots('dots 10 closest', 20, 30, 3.6, P.yellow);
var one = dots('dot 1 chosen', 24, 25, 5, P.coral);
var c682 = [tx('682', 30, 222, 26, P.mute, 700), tx('operations', 30, 244, 12.5, P.mute)];
inAt([wall].concat(c682), T.catalog);
var c65 = arr('counter arrow 1', 'M100 216H140', P.ink, 2, T.on).concat([tx('65', 180, 222, 26, P.teal, 700), tx('production-ready', 180, 244, 12.5, P.mute)]);
inAt([on65], T.on); inAt(c65.slice(2), T.on + 0.2);
var bge = modelPill('bge', 30, 266, 'meaning search · bge-small-en');
inAt(bge.layers, T.forEach, 4);
var c10 = arr('counter arrow 2', 'M250 216H290', P.ink, 2, T.keeps).concat([tx('10', 330, 222, 26, P.ink, 700), tx('offered to Jev', 330, 244, 12.5, P.mute)]);
inAt(c10.slice(2), T.keeps + 0.2);
inAt([ten], T.ten);
pulse(jev, T.picks);
var c1 = arr('counter arrow 3', 'M400 216H440', P.ink, 2, T.here).concat([tx('1', 480, 222, 26, P.coral, 700), tx('set a value', 480, 244, 12.5, P.mute)]);
inAt(c1.slice(2), T.here + 0.2);
inAt([one], T.here + 0.2);

writeLn('STILL g4 ' + (T.here + 0.3).toFixed(3));
for (var key in T) if (typeof T[key] == 'number') marker(C, T[key], key);
var STILLS = [['screen01', T.body - EASE - 0.05], ['screen02', T.shrink - 0.05], ['screen03', T.tables - EASE - 0.05],
              ['screen04', T.columns - EASE - 0.05], ['screen04b', T.enough - 0.1], ['screen05', T.ops - EASE - 0.05], ['screen06', DUR - 1 / 30]];
for (i = 0; i < STILLS.length; i++) writeLn('STILL ' + STILLS[i][0] + ' ' + STILLS[i][1].toFixed(3));
writeLn('DUR ' + DUR);
for (key in T) if (typeof T[key] == 'number') writeLn('T ' + key + ' ' + T[key].toFixed(3));
app.project.save();
C.name + ' ' + C.duration + ' ' + C.numLayers;
