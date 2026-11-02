// ==== Scene 7 "Step 6, Operation", v4 (narration v8, take v8; master C take v8 mix). Changes from v3, per the user's notes:
// the right panel slides out when the example starts and stays out, so the example has the full width (x 30-930); the prompt
// card is wider with larger text and stays to the end; the table is larger; the order arcs are gone, an "Order" column fills
// in instead and two soft row highlights link the rows the narration names; the sorted list is gone; the tree has its
// branches flipped (each node takes the result of the node below it) and one shared "price" node.
// AUDIO, WORDS and ICONS are defined by tools/edit/build_scene.py before this file (AUDIO = full path of the scene's soundtrack).
var MIX = 78.36;   // the mix length (ffprobe 78.360 s): the scene runs as long as its soundtrack
var P4 = cue('Sorted');
var T = {
 six: cue('six'), here: cue('Here is a harder'),
 raise: cue('raise'), orbit: cue('Orbit'), take1: cue('take five off'), black: cue('black'), ones: cue('ones'),
 take2: cue('take the five off'), first: cue('first'), round: cue('round to the nearest'), above: cue('never above'),
 twice: cue('twice'), below: cue('never below'), costPlus: cue('cost plus'), leave: cue('leave'),
 every: cue('Every part is'), condition: cue('A condition answers'), brandIs: cue('the brand is Orbit'), variantIs: cue('the variant is black'),
 grouping: cue('one grouping joins'),
 each: cue('Each operation takes'), takeQ: cue('Take five off takes'), roundQ: cue('Round to five'), sets: cue("That's what sets"),
 sorted: P4, tree: cue('tree', P4), nBelow: cue('never below', P4), nAbove: cue('never above', P4), nRound: cue('round to the nearest', P4),
 choice: cue('choice', P4), question: cue('is the variant black', P4),
 yes: cue('If yes'), yMinus: cue('take five off', cue('If yes')), yPlus: cue('add fifteen percent', cue('If yes')),
 no: cue('If no'), nPlus: cue('add fifteen percent', cue('If no')), nMinus: cue('take five off', cue('If no')),
 price: cue('current price', cue('Both paths')),
 end: narrationEnd()
};
var DUR = Math.round(MIX * 30) / 30;

// The scene comp. Unlike the kit's newScene, the soundtrack is imported by its full path every time: a project item
// with the same file name (an older scene07_master_C_v1.wav) must never be reused.
var old = findItem('V2 S07 Operation v4');
if (old) old.remove();
var C = app.project.items.addComp('V2 S07 Operation v4', 1920, 1080, 1, DUR, 30);
C.bgColor = rgb(P.bgA);
C.layers.addSolid(rgb(P.bgA), 'background', 1920, 1080, 1, DUR);
var AUDIO_ITEM = app.project.importFile(new ImportOptions(new File(AUDIO)));
C.layers.add(AUDIO_ITEM).name = 'narration';
writeLn('AUDIO ' + AUDIO_ITEM.file.fsName);

function tx(s, x, y, sz, fill, w, mono, mid) { return txt(C, 's7 ' + s, s, x, y, {size: sz, fill: fill || P.ink, w: w || 400, f: mono ? 'm' : 'h', a: mid ? 'middle' : 'start'}); }
function R(n, x, y, w, h, o) { return rect(C, n, x, y, w, h, o); }
function inAt(ls, t, rise) { fadeIn(ls, t, rise); return ls; }
function outAt(ls, t) { fadeTo(ls, t - EASE, 0); }
function mw(s, sz, w, mono) { return measure(C, s, {size: sz, w: w || 400, f: mono ? 'm' : 'h'}); }
// A plain connector (no head) drawn on at t.
function line(n, pts, color, sw, t) {
 var L = path(C, n, [pts], {stroke: color, sw: sw, round: true, trim: true});
 keys(L.transform.opacity, [[0, 0], [t, 0], [t + 0.02, 100]]);
 drawOn(L, t, 0.3);
 return L;
}
function num(n, cx, cy, r, s, sz, fill) { return [circle(C, 'number ' + n + ' circle', cx, cy, r, {fill: fill || P.teal}), tx(String(s), cx, cy + sz * 0.38, sz, '#FFFFFF', 700, true, true)]; }
// A small grey "intended" tag, top-left (x, y). Returns {w, layers}.
function intended(n, x, y, sz) {
 sz = sz || 9;
 var w = Math.round(mw('intended', sz, 400, true) + 10), h = sz + 4.5;
 return {w: w, layers: [R('intended tag ' + n, x, y, w, h, {fill: '#FFFFFF', stroke: P.mute, sw: 1, rx: h / 2}), tx('intended', x + 5, y + h / 2 + sz * 0.36, sz, P.mute, 400, true)]};
}
// Layers added since a count taken before (new layers go on top: indices 1..n).
function since(n0) { var out = []; for (var j = 1; j <= C.numLayers - n0; j++) out.push(C.layer(j)); return out; }

// ---- the right panel (plain prompt; steps 1-5 done, step 6 current): here at the start, slides out when the example starts ----
var STEPS = ['Coreference', 'Split', 'Action', 'Matching', 'Parameter', 'Operation'];
var n0 = C.numLayers;
R('panel', 632, 20, 308, 500, {rx: 18});
tx('THE PROMPT', 656, 52, 10.5, P.purple, 600, true);
tx('Archive the draft Casa products', 656, 80, 15);
tx('created in September,', 656, 102, 15);
tx('and show them.', 656, 124, 15);
tx('WHERE WE ARE', 656, 172, 10.5, P.purple, 600, true);
path(C, 'panel steps connector', [[[667, 204], [667, 384]]], {stroke: P.lav, sw: 3});
var stepName = [], i, k;
for (i = 0; i < 6; i++) {
 var y = 204 + i * 36;
 circle(C, 'panel step ' + (i + 1), 667, y, 9, {fill: P.paper, stroke: P.lav, sw: 2.5});
 tx(String(i + 1), 667, y + 4, 10, P.purple, 600, true, true);
 stepName.push(tx(STEPS[i], 690, y + 5, 14, i < 5 ? P.ink : P.mute, 400));
}
function lit(i) {
 var y = 204 + i * 36;
 return [circle(C, 'panel step ' + (i + 1) + ' on', 667, y, 9, {fill: P.teal, stroke: P.teal, sw: 2.5}),
         tx(String(i + 1), 667, y + 4, 10, '#FFFFFF', 600, true, true), tx(STEPS[i], 690, y + 5, 14, P.ink, 600)];
}
// Scene 6 ended on step 5 lit (and ticked): it hands over to step 6 on the word "six".
var lit5 = lit(4), lit6 = lit(5);
stepName[4].transform.opacity.setValue(0);
keys(stepName[4].transform.opacity, [[T.six, 0], [T.six + EASE, 100]]);
fadeTo(lit5, T.six, 0);
inAt(lit6, T.six);
fadeTo([stepName[5]], T.six, 0);
for (i = 0; i < 5; i++) tick(C, 'panel step ' + (i + 1) + ' done', 912, 204 + 36 * i, 8);
var PNL = since(n0);
shift(PNL, T.here, 340, 0, 0.4);
fadeTo(PNL, T.here + 0.05, 0);
icon(C, 'jev', 512, 16, 36);
icon(C, 'code', 556, 16, 36);
// Step 6 done, at the very end: a small "step 6" and a green tick at the top right (the panel is out by then).
var T6 = Math.min(T.price + 0.2, DUR - 0.5);
var s6 = [tx('step 6', 862, 45, 12, P.ink, 600, true)];
var done6 = tick(C, 'step 6 done', 919, 41, 8);
inAt(s6.concat([done6[0]]), T6); keys(done6[1].transform.opacity, [[0, 0], [T6, 0], [T6 + 0.05, 100]]); drawOn(done6[1], T6 + 0.1, 0.25);

// ---- context label ----
var lab = contextLabel(C, 'Building the operations', 0);
inAt([lab[1]], 0);

// ---- 1. step card "6 · Operation" (the stage still has the panel at its right) ----
var s1 = [R('step card', 170, 210, 300, 90, {stroke: P.teal, sw: 3})].concat(num('step', 215, 255, 22, 6, 22), [tx('Operation', 252, 264, 26, P.ink, 700)]);
inAt(s1, 0, 6); outAt(s1, T.here);

// ---- 2. the parts: the prompt card (one layer per word, full width, to the end of the scene) and the table ----
var PROMPT = 'Raise the prices of the Orbit variants by 15%, then take 5 off, but for the black ones apply the 15% only after removing the 5. ' +
             'Round everything to the nearest 5, and never go above twice their cost or below the cost plus 10%. Leave the variants without a cost unchanged.';
var PW = PROMPT.split(' '), PSZ = 14, CXL = 30, CXR = 930, PX = CXL + 16, PMAX = CXR - 16;
function layoutPrompt(sz) {
 var sp = mw('a a', sz, 400, true) - mw('aa', sz, 400, true), x = PX, ln = 0, out = [];
 for (var j = 0; j < PW.length; j++) {
  var w = mw(PW[j], sz, 400, true);
  if (x + w > PMAX && x > PX) { ln++; x = PX; }
  out.push({x: x, w: w, line: ln});
  x += w + sp;
 }
 return {pos: out, lines: ln + 1};
}
// The largest mono size from 14 down to 13 that keeps the prompt on three lines (else 13, on as many lines as it needs).
var lay = layoutPrompt(PSZ);
while (lay.lines > 3 && PSZ > 13) { PSZ -= 0.25; lay = layoutPrompt(PSZ); }
var PPITCH = Math.round(PSZ * 1.5), CARD_Y = 58, CARD_H = 16 + lay.lines * PPITCH;
var p2 = [R('prompt card', CXL, CARD_Y, CXR - CXL, CARD_H, {stroke: P.teal, sw: 2, rx: 10})];
for (i = 0; i < PW.length; i++) { lay.pos[i].y = CARD_Y + 8 + PSZ + lay.pos[i].line * PPITCH; p2.push(tx(PW[i], lay.pos[i].x, lay.pos[i].y, PSZ, P.ink, 400, true)); }
inAt(p2, T.here + 0.2, 6);
var unders = [];
// A coral underline under prompt words a..b (split per line), drawn on at t.
function underline(n, a, b, t) {
 var out = [], s = a;
 for (var j = a; j <= b; j++) {
  if (j == b || lay.pos[j + 1].line != lay.pos[s].line) {
   var yy = lay.pos[s].y + 4;
   out.push(line('underline ' + n + ' ' + s, [[lay.pos[s].x, yy], [lay.pos[j].x + lay.pos[j].w, yy]], P.coral, 2, t));
   s = j + 1;
  }
 }
 return out;
}

// Table. Rows: [role, function, applies to, value, role kind, cue, prompt word ranges, order].
var ROWS = [
 ['calculation', 'increase by %', 'price', '15%', 'calc', T.raise, [[0, 2], [7, 8]], 1],
 ['filter', 'brand = Orbit', 'the rows', '—', 'cond', T.orbit, [[5, 6]], 0],
 ['calculation', 'subtract', 'open', '5', 'calc', T.take1, [[10, 12]], 2],
 ['condition', 'color = black', '', '', 'cond', T.black, [[16, 17]], 0],
 ['choice', 'case', 'open / open', '', 'op', T.ones, [[13, 15]], 3],
 ['calculation', 'increase by %', 'open', '15%', 'calc', T.first, [[18, 22]], -2],
 ['calculation', 'subtract', 'open', '5', 'calc', T.take2, [[23, 25]], -1],
 ['rounding', 'to the nearest', 'open', '5', 'op', T.round, [[26, 31]], 4],
 ['limit', 'never above', 'open', 'open', 'op', T.above, [[33, 35]], 5],
 ['limit value', '×', 'cost', '2', 'op', T.twice, [[36, 38]], 0],
 ['limit value', '×', 'cost', '1.1', 'op', T.costPlus, [[41, 44]], 0],
 ['limit', 'never below', 'open', 'open', 'op', T.below, [[39, 40]], 6],
 ['condition', 'cost is present', 'the rows', '—', 'cond', T.leave, [[45, 51]], 0]
];
var FS = 12.5, HFS = 12, TX0 = CXL, PAD = 10, GAPC = 50, HEAD_Y = CARD_Y + CARD_H + 12, HEAD_H = 24, PITCH = 22, ROW_H = 19;
var ROW0 = HEAD_Y + HEAD_H + 3;                  // top of row 1
function rowTop(r) { return ROW0 + r * PITCH; }
function rowBase(r) { return rowTop(r) + ROW_H / 2 + FS * 0.36; }
function rowMid(r) { return rowTop(r) + ROW_H / 2; }
var TAGSZ = 10.5, TAGW = Math.round(mw('price', TAGSZ, 600, true) + 10), INT = Math.round(mw('intended', TAGSZ, 400, true) + 10);
var colW = [0, 0, 0, 0, 0];
for (i = 0; i < ROWS.length; i++) {
 colW[0] = Math.max(colW[0], mw(ROWS[i][0], FS, 600, true));
 colW[1] = Math.max(colW[1], mw(ROWS[i][1], FS, 400, true) + 10);
 colW[2] = Math.max(colW[2], mw(ROWS[i][2], FS, 400, true));
 colW[3] = Math.max(colW[3], mw(ROWS[i][3], FS, 600, true) + 10);
}
colW[2] = Math.max(colW[2], mw('open', FS, 400, true) + 6 + TAGW);
colW[3] = Math.max(colW[3], mw('—', FS, 400, true) + 8 + INT);
var HEADS = ['Role', 'Function', 'Applies to', 'Value', 'Order'];
for (k = 0; k < 5; k++) colW[k] = Math.max(colW[k], mw(HEADS[k], HFS, 600, true));
var CX = [TX0 + PAD];
for (k = 1; k < 5; k++) CX.push(CX[k - 1] + colW[k - 1] + (k == 4 ? GAPC - 10 : GAPC));
var TR = Math.round(CX[4] + colW[4] + PAD);      // the table's right edge
var TW = TR - TX0;
writeLn('PROMPT size ' + PSZ + ' lines ' + lay.lines + ' card y ' + CARD_Y + '-' + (CARD_Y + CARD_H));
writeLn('TABLE x ' + TX0 + '-' + TR + ' y ' + HEAD_Y + '-' + (rowTop(12) + ROW_H));
var head = [topRound(C, 'table header', TX0, HEAD_Y, TW, HEAD_H, 6, P.teal)];
for (k = 0; k < 5; k++) head.push(tx(HEADS[k], CX[k], HEAD_Y + HEAD_H / 2 + HFS * 0.36, HFS, P.paper, 600, true));
inAt(head, T.raise, 4);
var tbl = [].concat(head);
var rowLayers = [];
for (var r = 0; r < ROWS.length; r++) {
 var R_ = ROWS[r], kind = R_[4], ls = [R('row ' + (r + 1), TX0, rowTop(r), TW, ROW_H, {rx: 4})];
 ls.push(tx(R_[0], CX[0], rowBase(r), FS, kind == 'cond' ? P.coral : kind == 'calc' ? P.teal : P.ink, 600, true));
 if (kind == 'cond') {
  var fw = mw(R_[1], FS, 400, true) + 10;
  ls.push(R('row ' + (r + 1) + ' condition pill', CX[1] - 5, rowTop(r) + 2, fw, ROW_H - 4, {fill: P.coral, op: 0.25, rx: 7.5}));
  ls.push(tx(R_[1], CX[1], rowBase(r), FS, '#B3433F', 600, true));
 } else ls.push(tx(R_[1], CX[1], rowBase(r), FS, P.ink, 400, true));
 // Applies to: "open" cells in grey.
 if (R_[2] == 'open / open') {
  var xo = CX[2], wo = mw('open', FS, 400, true), sl = mw(' / ', FS, 400, true);
  ls.push(tx('open', xo, rowBase(r), FS, P.mute, 400, true), tx('/', xo + wo + sl / 2, rowBase(r), FS, P.mute, 400, true, true), tx('open', xo + wo + sl, rowBase(r), FS, P.mute, 400, true));
 } else if (R_[2] == 'open') ls.push(tx('open', CX[2], rowBase(r), FS, P.mute, 400, true));
 else if (R_[2]) ls.push(tx(R_[2], CX[2], rowBase(r), FS, P.ink, 400, true));
 // Value: a yellow pill for a number, grey for open, a dash for none.
 if (R_[3] == 'open') ls.push(tx('open', CX[3], rowBase(r), FS, P.mute, 400, true));
 else if (R_[3] == '—') ls.push(tx('—', CX[3], rowBase(r), FS, P.mute, 400, true));
 else if (R_[3]) {
  var vw = mw(R_[3], FS, 600, true) + 10;
  ls.push(R('row ' + (r + 1) + ' value', CX[3] - 5, rowTop(r) + 2, vw, ROW_H - 4, {fill: P.yellow, rx: 7.5}), tx(R_[3], CX[3], rowBase(r), FS, P.ink, 600, true));
 }
 if (r == 12) { var it = intended('row 13', CX[3] + mw('—', FS, 400, true) + 8, rowTop(r) + 2.5, TAGSZ); ls = ls.concat(it.layers); }
 inAt(ls, R_[5], 4);
 rowLayers.push(ls);
 tbl = tbl.concat(ls);
 for (k = 0; k < R_[6].length; k++) unders = unders.concat(underline('r' + (r + 1), R_[6][k][0], R_[6][k][1], R_[5] + 0.1));
}

// ---- 3. conditions and grouping: the condition rows pulse; true / false chips; one AND chooses the rows ----
var p3 = [], CONDROWS = [1, 3, 12];
for (i = 0; i < CONDROWS.length; i++) {
 var pl = R('condition pulse row ' + (CONDROWS[i] + 1), TX0, rowTop(CONDROWS[i]), TW, ROW_H, {fill: P.coral, op: 0.3, rx: 4});
 pl.moveBefore(rowLayers[CONDROWS[i]][0]);       // over the row's band, under its words
 var tp = T.condition + 0.05 * i;
 keys(pl.transform.opacity, [[0, 0], [tp, 0], [tp + 0.3, 100], [tp + 1.2, 100], [tp + 1.6, 0]]);
}
var TFS = 10.5, TFW = Math.round(mw('true / false', TFS, 600, true) + 14);
function tfChip(r, t) {
 var x = TR + 10;
 return inAt([R('true false chip row ' + (r + 1), x, rowTop(r) + 1, TFW, ROW_H - 2, {fill: '#FFFFFF', stroke: P.coral, sw: 1.2, rx: (ROW_H - 2) / 2}),
              tx('true / false', x + TFW / 2, rowMid(r) + TFS * 0.36, TFS, '#B3433F', 600, true, true)], t, 3);
}
p3 = p3.concat(tfChip(1, T.brandIs), tfChip(3, T.variantIs));
// The grouping: a coral bracket from rows 2 and 13 (row 2's line leaves from its chip) to an AND node.
var BX = TR + 10 + TFW + 14, yA = rowMid(1), yB = rowMid(12), yM = (yA + yB) / 2;
p3.push(line('grouping from row 2', [[TR + 10 + TFW + 2, yA], [BX, yA], [BX, yM]], P.coral, 2, T.grouping));
p3.push(line('grouping from row 13', [[TR + 2, yB], [BX, yB], [BX, yM]], P.coral, 2, T.grouping));
p3.push(line('grouping to AND', [[BX, yM], [BX + 12, yM]], P.coral, 2, T.grouping + 0.3));
var AW = Math.round(mw('AND', 13, 700, true) + 20);
p3 = p3.concat(inAt([R('AND node', BX + 12, yM - 13, AW, 26, {fill: P.coral, rx: 13}), tx('AND', BX + 12 + AW / 2, yM + 4.7, 13, '#FFFFFF', 700, true, true)], T.grouping + 0.3, 4));
p3 = p3.concat(inAt([tx('chooses the rows', BX + 12, yM + 32, 12, P.ink, 400)], T.grouping + 0.5, 3));
var itA = intended('AND', BX + 12, yM + 41, TAGSZ);
p3 = p3.concat(inAt(itA.layers, T.grouping + 0.5, 3));
writeLn('GROUPING right edge ' + Math.max(BX + 12 + AW, BX + 12 + mw('chooses the rows', 12)).toFixed(1));
outAt(p3, T.each);

// ---- 4. order: soft highlights link the rows the narration names; then the "Order" column fills in ----
// A soft lavender band over rows, under their words, from t to tOff.
function soft(rows, t, tOff) {
 for (var j = 0; j < rows.length; j++) {
  var b = R('order link row ' + (rows[j] + 1), TX0, rowTop(rows[j]), TW, ROW_H, {fill: P.lav, op: 0.55, rx: 4});
  b.moveBefore(rowLayers[rows[j]][0]);
  keys(b.transform.opacity, [[0, 0], [t, 0], [t + 0.3, 100], [tOff - 0.3, 100], [tOff, 0]]);
 }
}
soft([2, 0], T.takeQ, T.roundQ - 0.1);
soft([7, 4], T.roundQ, T.sets - 0.1);
// Row 1 and row 7 start from the price: a teal tint behind row 1's "price", a teal "price" tag after row 7's open cell.
var pw1 = mw('price', FS, 400, true) + 8;
var tag1 = R('price tag row 1', CX[2] - 4, rowTop(0) + 2, pw1, ROW_H - 4, {fill: P.teal, op: 0.2, rx: 7.5});
tag1.moveBefore(rowLayers[0][0]);
var tx7 = CX[2] + mw('open', FS, 400, true) + 6;
var tag7 = [R('price tag row 7', tx7, rowTop(6) + 2, TAGW, ROW_H - 4, {fill: P.teal, op: 0.2, rx: 7.5}), tx('price', tx7 + 5, rowMid(6) + TAGSZ * 0.36, TAGSZ, P.teal, 600, true)];
var TPRICE = cue('price', T.takeQ);
inAt([tag1], TPRICE); inAt(tag7, TPRICE + 0.15, 3);
tbl = tbl.concat([tag1], tag7);
// The order: a small disc per operation (teal for the normal path, ink for the black path), a dash for the rest;
// filled by rank on "That's what sets the order".
var ODX = CX[4] + mw('Order', HFS, 600, true) / 2;
for (r = 0; r < ROWS.length; r++) {
 var o = ROWS[r][7], rank = Math.abs(o), tO = T.sets + (rank ? (rank - 1) * 0.18 : 1.15) + (o < 0 ? 0.06 : 0);
 var ol = o ? num('order row ' + (r + 1), ODX, rowMid(r), 8, rank, 10.5, o < 0 ? P.ink : P.teal)
            : [tx('—', ODX, rowBase(r), FS, P.mute, 400, true, true)];
 inAt(ol, tO, 3);
 tbl = tbl.concat(ol);
}
// The table (and the prompt's underlines) go once, when the tree starts; the prompt card stays.
outAt(tbl.concat(unders), T.sorted + EASE);

// ---- 5. the tree under the prompt card, centred in the full width; each node takes the result of the node below it ----
var p6 = [], TCX = (CXL + CXR) / 2, NH = 32, NG = 16, NFS = 12;
// A node: teal outline; label, and an optional yellow value chip after it. Centred on cx, top y.
function tnode(n, cx, y, label, value, t) {
 var lw = mw(label, NFS, 600, true), vw = value ? mw(value, 11.5, 600, true) + 12 : 0, gap = value ? 8 : 0, w = Math.round(lw + gap + vw + 26), x0 = cx - w / 2;
 var ls = [R('tree ' + n, x0, y, w, NH, {stroke: P.teal, sw: 2, rx: 8}), tx(label, x0 + 13, y + NH / 2 + NFS * 0.36, NFS, P.ink, 600, true)];
 if (value) ls.push(R('tree ' + n + ' value', x0 + 13 + lw + gap, y + 5, vw, NH - 10, {fill: P.yellow, rx: (NH - 10) / 2}), tx(value, x0 + 13 + lw + gap + 6, y + NH / 2 + 11.5 * 0.36, 11.5, P.ink, 600, true));
 writeLn('NODE ' + n + ' x ' + x0.toFixed(1) + '-' + (x0 + w).toFixed(1) + ' y ' + y);
 return {w: w, layers: inAt(ls, t, 4)};
}
var Y0 = CARD_Y + CARD_H + 16, y1 = Y0, y2 = y1 + NH + NG, y3 = y2 + NH + NG, yd = y3 + NH + NG, DH = 64, DW = 250, ycy = yd + DH / 2;
p6 = p6.concat(tnode('never below', TCX, y1, 'never below ·', 'cost × 1.1', T.nBelow).layers);
p6.push(line('tree link 1', [[TCX, y1 + NH], [TCX, y2]], P.mute, 2, T.nAbove));
p6 = p6.concat(tnode('never above', TCX, y2, 'never above ·', 'cost × 2', T.nAbove + 0.15).layers);
p6.push(line('tree link 2', [[TCX, y2 + NH], [TCX, y3]], P.mute, 2, T.nRound));
p6 = p6.concat(tnode('round', TCX, y3, 'round to the nearest 5', null, T.nRound + 0.15).layers);
p6.push(line('tree link 3', [[TCX, y3 + NH], [TCX, yd]], P.mute, 2, T.question));
var dia = path(C, 'tree choice diamond', [[[TCX, yd], [TCX + DW / 2, ycy], [TCX, yd + DH], [TCX - DW / 2, ycy]]], {fill: '#FDE3E2', stroke: P.coral, sw: 2, closed: true});
p6 = p6.concat(inAt([dia, tx('is the variant black?', TCX, ycy + 4.5, NFS, P.ink, 600, true, true)], T.question + 0.15, 4));
// Branches: down from the diamond's side corners; yes on the left, no on the right. Upper node = the later operation.
var XL = TCX - DW / 2, XR = TCX + DW / 2, b1 = ycy + 40, b2 = b1 + NH + NG, yP = b2 + NH + 18;
function branch(side, x, t, upper, lower, tLower, tUpper) {
 var out = [line('tree ' + side + ' link 1', [[x, ycy], [x, b1]], P.coral, 2, t)];
 out = out.concat(inAt([tx(side, side == 'yes' ? x - 8 - mw('yes', NFS, 700, true) : x + 8, ycy + 24, NFS, '#B3433F', 700, true, false)], t + 0.1, 3));
 out = out.concat(tnode(side + ' ' + lower, x, b2, lower, null, tLower).layers);
 out = out.concat(tnode(side + ' ' + upper, x, b1, upper, null, tUpper + 0.15).layers);
 out.push(line('tree ' + side + ' link 2', [[x, b1 + NH], [x, b2]], P.mute, 2, tUpper + 0.15));
 return out;
}
p6 = p6.concat(branch('yes', XL, T.yes, '+15%', '−5', T.yMinus, T.yPlus));
p6 = p6.concat(branch('no', XR, T.no, '−5', '+15%', T.nPlus, T.nMinus));
// One shared "price" node under both branches: each branch's lowest node takes from it.
var PWN = Math.round(mw('price', NFS, 600, true) + 26);
p6.push(line('tree price link yes', [[XL, b2 + NH], [XL, yP + NH / 2], [TCX - PWN / 2, yP + NH / 2]], P.mute, 2, T.price));
p6.push(line('tree price link no', [[XR, b2 + NH], [XR, yP + NH / 2], [TCX + PWN / 2, yP + NH / 2]], P.mute, 2, T.price));
p6 = p6.concat(tnode('price', TCX, yP, 'price', null, T.price + 0.15).layers);
writeLn('TREE y ' + Y0 + '-' + (yP + NH) + ' x ' + (XL - 50) + '-' + (XR + 50));
// To the side: the rows' grouping, coral, tagged intended.
var GW = 176, GX = XR + 90, GY = y1;
var gg = [R('tree grouping', GX, GY, GW, 52, {fill: '#FFFFFF', stroke: P.coral, sw: 2, rx: 10}),
          tx('brand = Orbit', GX + GW / 2, GY + 22, 12, '#B3433F', 600, true, true), tx('AND cost present', GX + GW / 2, GY + 40, 12, '#B3433F', 600, true, true),
          tx('chooses the rows', GX, GY + 72, 12, P.ink, 400)];
var itT = intended('tree', GX + mw('chooses the rows', 12) + 8, GY + 61, TAGSZ);
inAt(gg.concat(itT.layers), T.tree, 4);
writeLn('SIDE x ' + GX + '-' + Math.max(GX + GW, GX + mw('chooses the rows', 12) + 8 + itT.w).toFixed(1));

for (var key in T) marker(C, T[key], key);
var STILLS = [['screen01', T.here - EASE - 0.05], ['screen02', T.every - 0.1], ['screen03', T.each - EASE - 0.05],
              ['screen04', T.sorted - 0.05], ['screen05', DUR - 1 / 30], ['take', T.takeQ + 1.5], ['round', T.roundQ + 1.2], ['panel', T.here + 0.2]];
for (i = 0; i < STILLS.length; i++) writeLn('STILL ' + STILLS[i][0] + ' ' + STILLS[i][1].toFixed(3));
writeLn('DUR ' + DUR);
app.project.save();
C.name + ' ' + C.duration + ' ' + C.numLayers;
