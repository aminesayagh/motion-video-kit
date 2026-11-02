// ==== Scene 8 "Assembly", v4: the two code blocks drawn as a dark code editor (near-black card, top bar with three dots, syntax colours). From v3 (master C take v8 soundtrack; '>=' carries a zero-width non-joiner so JetBrains Mono shows the two characters, not its ligature): the trees join into one abstract syntax tree; request 1's
// real AST typed in as code, a highlight band moving node by node as spoken; then the real SQL of both requests.
// Every element is an editable layer; every beat starts on a narration word. Elements on screen are built once and
// never redrawn; within a part only the element named moves, and a part's elements fade out once, before the next part.
// AUDIO, WORDS and ICONS are defined by tools/edit/build_scene.py before this file (AUDIO = full path of the scene's soundtrack).
var MIX = 63.63;   // the mix's length (ffprobe 63.630 s): the scene runs as long as its soundtrack
var T = {
 last: cue('Last the assembly'), step: cue('Step six left us'), trees: cue('trees of operations'),
 rows: cue('which rows'), changes: cue('what changes'), order: cue('in what order'),
 joins: cue('joins them into one structure'), ast: cue('abstract syntax tree'), text: cue('not as text'),
 here: cue('Here is request one'),
 update: cue('an update of the products table'), assign: cue('the status becomes'), all: cue('all of these must be true'),
 brand: cue('brand equals Casa'), status: cue('status equals draft'), sept: cue('from the first of September'),
 column: cue('Every column is a node'), value: cue('every value is a node'),
 only: cue('Only at the end'), sql: cue('SQL'), r1: cue('Request one becomes an update'), gives: cue('gives back the ids'),
 r2: cue('Request two reads exactly those ids')
};
var DUR = Math.round(MIX * 30) / 30;
// The soundtrack is imported by its full path every time (newScene would reuse an older file of the same name).
var C = (function () {
 var old = findItem('V2 S08 Assembly v4');
 if (old) old.remove();
 var comp = app.project.items.addComp('V2 S08 Assembly v4', 1920, 1080, 1, DUR, 30);
 comp.bgColor = rgb(P.bgA);
 comp.layers.addSolid(rgb(P.bgA), 'background', 1920, 1080, 1, DUR);
 var audio = app.project.importFile(new ImportOptions(new File(AUDIO)));
 comp.layers.add(audio).name = 'narration';
 return comp;
})();

function tx(s, x, y, sz, fill, w, mono, mid) { return txt(C, 's8 ' + s, s, x, y, {size: sz, fill: fill || P.ink, w: w || 400, f: mono ? 'm' : 'h', a: mid ? 'middle' : 'start'}); }
function R(n, x, y, w, h, o) { return rect(C, n, x, y, w, h, o); }
function inAt(ls, t, rise) { fadeIn(ls, t, rise); return ls; }
function outAt(ls, t) { fadeTo(ls, t - EASE, 0); }
function mw(s, sz, w, mono) { return measure(C, s, {size: sz, w: w || 400, f: mono ? 'm' : 'h'}); }

// ---- persistent: the right panel (plain prompt; all six steps ticked, none lit) and the top-right icons ----
var STEPS = ['Coreference', 'Split', 'Action', 'Matching', 'Parameter', 'Operation'], i;
R('panel', 632, 20, 308, 500, {rx: 18});
tx('THE PROMPT', 656, 52, 10.5, P.purple, 600, true);
tx('Archive the draft Casa products', 656, 80, 15);
tx('created in September,', 656, 102, 15);
tx('and show them.', 656, 124, 15);
tx('WHERE WE ARE', 656, 172, 10.5, P.purple, 600, true);
path(C, 'panel steps connector', [[[667, 204], [667, 384]]], {stroke: P.lav, sw: 3});
for (i = 0; i < 6; i++) {
 var y = 204 + i * 36;
 circle(C, 'panel step ' + (i + 1), 667, y, 9, {fill: P.paper, stroke: P.lav, sw: 2.5});
 tx(String(i + 1), 667, y + 4, 10, P.purple, 600, true, true);
 tx(STEPS[i], 690, y + 5, 14, P.ink, 400);
 tick(C, 'panel step ' + (i + 1) + ' done', 912, y, 8);
}
icon(C, 'jev', 512, 16, 36);
icon(C, 'code', 556, 16, 36);

// ---- context label ----
var lab = contextLabel(C, 'Building the query', 0);
inAt([lab[1]], 0);

// ---- 1. the card "Assembly", no number ----
var s1 = [R('assembly card', 170, 210, 300, 90, {stroke: P.teal, sw: 3}), tx('Assembly', 320, 264, 26, P.ink, 700, false, true)];
inAt(s1, T.last, 6); outAt(s1, T.step);

// ---- 2. three small trees, labelled as spoken; they slide together into one box, the abstract syntax tree ----
// A tree: root at (cx, 160), two children 46 below, label under it; every part rides its root.
function tree(name, cx, color, label, tLabel) {
 var e = path(C, 'tree ' + name + ' edges', [[[cx - 28, 206], [cx, 160], [cx + 28, 206]]], {stroke: P.faint, sw: 2.5, round: true});
 var root = circle(C, 'tree ' + name + ' root', cx, 160, 11, {fill: color});
 var kids = [circle(C, 'tree ' + name + ' left', cx - 28, 206, 9, {fill: P.paper, stroke: color, sw: 2.5}),
             circle(C, 'tree ' + name + ' right', cx + 28, 206, 9, {fill: P.paper, stroke: color, sw: 2.5})];
 var lb = tx(label, cx, 246, 14, P.ink, 600, false, true);
 inAt([root, e].concat(kids), T.trees, 6);
 inAt([lb], tLabel, 3);
 parentAll([e, lb].concat(kids), root);
 return {root: root, layers: [root, e, lb].concat(kids)};
}
var TREES = [tree('which rows', 130, P.teal, 'which rows', T.rows), tree('what changes', 320, P.coral, 'what changes', T.changes),
             tree('in what order', 510, P.purple, 'in what order', T.order)];
// On "joins": they slide in to 120 apart and 40 lower; a top node and its three edges join them, a box closes round them.
var TX2 = [200, 320, 440], p2 = [];
for (i = 0; i < 3; i++) { moveTo(TREES[i].root, T.joins, TX2[i], 200, 0.5); p2 = p2.concat(TREES[i].layers); }
var top = [path(C, 'ast top edges', [[[200, 200], [320, 146]], [[320, 146], [320, 200]], [[440, 200], [320, 146]]], {stroke: P.faint, sw: 2.5, round: true}),
           circle(C, 'ast top node', 320, 146, 12, {fill: P.ink})];
var box = R('ast box', 110, 116, 420, 186, {fill: null, stroke: P.teal, sw: 2.5, rx: 14});
top[0].moveAfter(TREES[0].layers[1]);   // under every tree, so the edges never cross a node
inAt(top.concat([box]), T.joins + 0.5);
var astLabel = inAt([tx('abstract syntax tree', 320, 330, 15, P.teal, 600, true, true)], T.ast, 4);
// A small "text" tag, struck through, on "not as text".
var tw = mw('text', 12, 400, true) + 16;
var textTag = [R('text tag', 320 - tw / 2, 350, tw, 22, {fill: P.paper, stroke: P.faint, sw: 1.5, rx: 6}), tx('text', 320, 365, 12, P.mute, 400, true, true)];
var textStrike = path(C, 'text tag strike', [[[320 - tw / 2 - 4, 361], [320 + tw / 2 + 4, 361]]], {stroke: P.red, sw: 2, round: true, trim: true});
inAt(textTag, T.text, 4);
keys(textStrike.transform.opacity, [[0, 0], [T.text + 0.25, 0], [T.text + 0.3, 100]]);
drawOn(textStrike, T.text + 0.3, 0.3);
p2 = p2.concat(top, [box], astLabel, textTag, [textStrike]);
outAt(p2, T.here);

// ---- shared for the two code blocks: mono 12, measured advance, lines typed in by hold keys on Source Text ----
var CS = 12, CW = (mw('00000000000000000000000000000000000000000', CS, 400, true) - mw('0', CS, 400, true)) / 40;
var CX = 46;                          // text left edge
// Editor look: near-black card, a subtle border, an 18-unit top bar with three window dots. Returns its layers.
var ED = {bg: '#1E1E1E', border: '#2D333B', bar: '#2D2D2D', key: '#9CDCFE', str: '#CE9178', pun: '#D4D4D4', typ: '#DCDCAA',
          kw: '#569CD6', par: '#C586C0'}, BAR = 18;
function editorCard(name, x, y, w, h) {
 var ls = [R(name, x, y, w, h, {fill: ED.bg, stroke: ED.border, sw: 1, rx: 10}), topRound(C, name + ' top bar', x + 0.5, y + 0.5, w - 1, BAR, 9.5, ED.bar)];
 var dots = ['#FF5F57', '#FEBC2E', '#28C840'];
 for (var d = 0; d < 3; d++) ls.push(circle(C, name + ' dot ' + (d + 1), x + 14 + d * 13, y + BAR / 2 + 0.5, 3.6, {fill: dots[d]}));
 return ls;
}
// Syntax segments of a line: [text, colour]; whitespace rides the segment before it, same colours merge.
function pushSeg(out, s, col) {
 if (/^\s+$/.test(s) && out.length) { out[out.length - 1][0] += s; return; }
 if (out.length && out[out.length - 1][1] == col) { out[out.length - 1][0] += s; return; }
 out.push([s, col]);
}
function astSegs(L) {
 var out = [], i = 0, prevKey = null, j;
 while (i < L.length) {
  if (L.charAt(i) == '"') {
   j = L.indexOf('"', i + 1);
   var s = L.substring(i, j + 1), isKey = /^\s*:/.test(L.substr(j + 1)), col;
   if (isKey) col = ED.key;
   else if (prevKey == '"type"' && /^"(update|all|comparison|literal)"$/.test(s)) col = ED.typ;
   else col = ED.str;
   pushSeg(out, s, col); prevKey = isKey ? s : null; i = j + 1;
  } else { j = i; while (j < L.length && L.charAt(j) != '"') j++; pushSeg(out, L.substring(i, j), ED.pun); i = j; }
 }
 return out;
}
var SQLKW = {UPDATE: 1, SET: 1, WHERE: 1, AND: 1, RETURNING: 1, SELECT: 1, FROM: 1, IN: 1, AS: 1, value: 1, json_each: 1};
function sqlSegs(L) {
 var out = [], i = 0, m, rest;
 while (i < L.length) {
  rest = L.substr(i);
  if ((m = /^'[^']*'/.exec(rest))) pushSeg(out, m[0], ED.str);
  else if ((m = /^"[^"]*"/.exec(rest))) pushSeg(out, m[0], ED.key);
  else if ((m = /^:[A-Za-z_]\w*/.exec(rest))) pushSeg(out, m[0], ED.par);
  else if ((m = /^[A-Za-z_]\w*/.exec(rest))) pushSeg(out, m[0], SQLKW[m[0]] ? ED.kw : ED.pun);
  else { m = [rest.charAt(0)]; pushSeg(out, m[0], ED.pun); }
  i += m[0].length;
 }
 return out;
}
// One text layer per coloured segment, at its column (mono: x = CX + visual column x CW; the zero-width
// non-joiner takes no column). ls[k] = [{layer, r0, s}] (r0: the segment's first character in the line).
function codeLines(name, lines, y0, pitch, segFn) {
 var ls = [];
 for (var k = 0; k < lines.length; k++) {
  var row = [];
  if (lines[k] !== '') {
   var sg = segFn(lines[k]), r = 0;
   for (var q = 0; q < sg.length; q++) {
    var lead = /^\s*/.exec(sg[q][0])[0].length, vis = lines[k].substr(0, r + lead).replace(/\u200c/g, '').length;
    if (sg[q][0].length > lead)
     row.push({layer: txt(C, name + ' line ' + (k + 1) + ' seg ' + (q + 1), ' ', CX + vis * CW, y0 + k * pitch, {size: CS, f: 'm', fill: sg[q][1]}),
               r0: r + lead, s: sg[q][0].substr(lead)});
    r += sg[q][0].length;
   }
  }
  ls.push(row);
 }
 return ls;
}
function codeLayers(ls) { var out = []; for (var k = 0; k < ls.length; k++) for (var q = 0; q < ls[k].length; q++) out.push(ls[k][q].layer); return out; }
// Types lines a..b in over [t, t + dur], frame by frame, as one stream of characters.
function typeLines(ls, lines, a, b, t, dur) {
 var total = 0, k, f, F = Math.max(1, Math.round(dur * 30));
 for (k = a; k <= b; k++) total += lines[k].length;
 for (k = a; k <= b; k++) {
  var before = 0, j;
  for (j = a; j < k; j++) before += lines[j].length;
  for (var q = 0; q < ls[k].length; q++) {
   var sg = ls[k][q], ks = [[0, ' ']], last = 0;
   for (f = 1; f <= F; f++) {
    var n = Math.min(lines[k].length, Math.max(0, Math.round(total * f / F) - before));
    var m = Math.min(sg.s.length, Math.max(0, n - sg.r0));
    if (m > last) { ks.push([t + (f - 1) / 30, sg.s.substr(0, m)]); last = m; }
   }
   holdKeys(sg.layer.property('Source Text'), ks);
  }
 }
}
function lineW(lines, a, b) { var m = 0; for (var k = a; k <= b; k++) m = Math.max(m, lines[k].length); return m * CW; }

// ---- 3. request 1's AST, as the tool holds it; a highlight band moves to each node as it is named ----
var AST = ["{\"type\": \"update\",", " \"target\": {\"type\": \"database_table\", \"reference\": \"t_products\"},", " \"assignments\": [{\"column\": {\"reference\": \"c_status\"},", "                  \"value\":  {\"type\": \"literal\", \"value\": \"archived\"}}],", " \"scope\": {\"where\": {\"type\": \"all\", \"children\": [", "   {\"type\": \"comparison\", \"operator\": \"=\",", "    \"left\": {\"reference\": \"c_brand\"},  \"right\": {\"value\": \"Casa\"}},", "   {\"type\": \"comparison\", \"operator\": \"=\",", "    \"left\": {\"reference\": \"c_status\"}, \"right\": {\"value\": \"draft\"}},", "   {\"type\": \"all\", \"children\": [", "     {\"operator\": \">\u200c=\", \"left\": {\"reference\": \"c_created_at\"},", "      \"right\": {\"value\": \"2026-09-01\"}},", "     {\"operator\": \"<\",  \"left\": {\"reference\": \"c_created_at\"},", "      \"right\": {\"value\": \"2026-10-01\"}}]}]}}}"];
var AP = 17, AY = 66, AB = AY + 23 + BAR;   // pitch; card top; first baseline (below the editor's top bar)
var astCard = inAt(editorCard('ast code card', 30, AY, 570, AST.length * AP + 22 + BAR), T.here, 6);
// The band: behind the text (made before it), one layer that moves and resizes from node to node.
var band = R('ast highlight band', 0, 0, 10, 10, {fill: '#FFFFFF', op: 0.11, rx: 5});
function bandAt(a, b) {   // lines a..b, 1-based
 var x = CX - 6, y = AB + (a - 1) * AP - 13, w = lineW(AST, a - 1, b - 1) + 12, h = (b - a) * AP + 18;
 return {pos: [(x + w / 2) * K, (y + h / 2) * K], size: [w * K, h * K]};
}
var BANDS = [[T.update, 1, 2], [T.assign, 3, 4], [T.all, 5, 5], [T.brand, 6, 7], [T.status, 8, 9], [T.sept, 10, 14]];
var bp = [], bs = [];
for (i = 0; i < BANDS.length; i++) {
 var bb = bandAt(BANDS[i][1], BANDS[i][2]);
 if (i == 0) { bp.push([0, bb.pos]); bs.push([0, bb.size]); }
 else { bp.push([BANDS[i][0], bp[bp.length - 1][1]]); bs.push([BANDS[i][0], bs[bs.length - 1][1]]); }
 bp.push([BANDS[i][0] + EASE, bb.pos]); bs.push([BANDS[i][0] + EASE, bb.size]);
}
keys(band.transform.position, bp.slice(1));
band.transform.position.setValueAtTime(0, bp[0][1]);
keys(rectSize(band), bs.slice(1));
rectSize(band).setValueAtTime(0, bs[0][1]);
keys(band.transform.opacity, [[0, 0], [T.update, 0], [T.update + EASE, 100], [T.column, 100], [T.column + EASE, 0]]);
var astL = codeLines('ast', AST, AB, AP, astSegs);
typeLines(astL, AST, 0, AST.length - 1, T.here + 0.15, 0.6);
// The two labels under the card, each with a thin arrow up to its token.
function tokenAt(line, s) { var c = AST[line - 1].indexOf(s); return {x: CX + (c + s.length / 2) * CW, y: AB + (line - 1) * AP + 4}; }
var cTok = tokenAt(13, '"c_created_at"'), vTok = tokenAt(14, '"2026-10-01"'), LY = AY + AST.length * AP + 22 + BAR + 46;
var colLab = [tx('column → a real column of the table', 600 - mw('column → a real column of the table', 12, 600, true), LY, 12, P.teal, 600, true)];
colLab = colLab.concat(arrow(C, 'column arrow', 'M ' + cTok.x + ' ' + (LY - 16) + ' L ' + cTok.x + ' ' + (cTok.y + 3), P.teal, 1.6));
var valLab = [tx('value → a node of its own', 30, LY, 12, P.teal, 600, true)];
valLab = valLab.concat(arrow(C, 'value arrow', 'M ' + vTok.x + ' ' + (LY - 16) + ' L ' + vTok.x + ' ' + (vTok.y + 3), P.teal, 1.6));
inAt([colLab[0]], T.column, 4); colLab[1].transform.opacity.setValue(100); drawOn(colLab[1], T.column, 0.3);
keys(colLab[2].transform.opacity, [[0, 0], [T.column + 0.25, 0], [T.column + 0.3, 100]]);
inAt([valLab[0]], T.value, 4); drawOn(valLab[1], T.value, 0.3);
keys(valLab[2].transform.opacity, [[0, 0], [T.value + 0.25, 0], [T.value + 0.3, 100]]);
var p3 = astCard.concat([band], colLab, valLab, codeLayers(astL));
outAt(p3, T.only);

// ---- 4. the SQL: request 1's UPDATE, its RETURNING lit; request 2's SELECT reads those rows ----
var SQL = ["UPDATE \"products\" AS \"p\" SET \"status\" = 'archived'", "WHERE (\"p\".\"brand\" = 'Casa') AND (\"p\".\"status\" = 'draft')", "  AND (\"p\".\"created_at\" >\u200c= '2026-09-01')", "  AND (\"p\".\"created_at\" < '2026-10-01')", "RETURNING \"product_id\";", "", "SELECT \u2026 8 columns FROM \"products\" AS \"p\"", "WHERE \"p\".\"product_id\" IN (SELECT value FROM json_each(:rows_r1));"];
var SP = 20, SY = 80, SB = SY + 26 + BAR;
var sqlCard = inAt(editorCard('sql code card', 30, SY, 570, SQL.length * SP + 26 + BAR), T.sql, 6);
function sqlBox(line, s, name) {
 var c = SQL[line - 1].indexOf(s), x = CX + c * CW - 3, y = SB + (line - 1) * SP - 14;
 return R(name, x, y, s.length * CW + 6, 19, {fill: P.coral, op: 0.3, rx: 4});
}
var retHl = sqlBox(5, 'RETURNING "product_id"', 'sql returning highlight');
var rowsHl = sqlBox(8, ':rows_r1', 'sql rows_r1 highlight');
inAt([retHl], T.gives);
inAt([rowsHl], T.r2 + 0.75);
var sqlL = codeLines('sql', SQL, SB, SP, sqlSegs);
typeLines(sqlL, SQL, 0, 4, T.r1, 0.6);
typeLines(sqlL, SQL, 6, 7, T.r2, 0.6);
// The coral arrow from RETURNING to :rows_r1, drawn on once the SELECT is typed, and its label.
var rEnd = CX + (SQL[4].indexOf('RETURNING "product_id"') + 22) * CW + 8, rY = SB + 4 * SP - 5;
var kX = CX + (SQL[7].indexOf(':rows_r1') + 4) * CW, kY = SB + 7 * SP - 16;
var link = arrow(C, 'rows arrow', 'M ' + rEnd + ' ' + rY + ' C ' + (kX - 40) + ' ' + rY + ' ' + kX + ' ' + rY + ' ' + kX + ' ' + kY, P.coral, 2);
link[0].transform.opacity.setValue(100);
drawOn(link[0], T.r2 + 0.75, 0.4);
keys(link[1].transform.opacity, [[0, 0], [T.r2 + 1.1, 0], [T.r2 + 1.15, 100]]);
var LBL = 'the rows request 1 changed';
var linkLab = inAt([tx(LBL, kX - 34 - mw(LBL, 12, 600), SB + 5 * SP + 4, 12, P.coral, 600)], T.r2 + 1.0, 3);

for (var key in T) marker(C, T[key], key);
var STILLS = [['screen01', T.step - EASE - 0.05], ['screen02', T.here - EASE - 0.05], ['screen03', T.only - EASE - 0.05],
              ['screen04', DUR - 1 / 30], ['g5a', T.brand - 0.2], ['g5b', T.brand + 0.6]];
for (i = 0; i < STILLS.length; i++) writeLn('STILL ' + STILLS[i][0] + ' ' + STILLS[i][1].toFixed(3));
writeLn('DUR ' + DUR + ' CW ' + CW.toFixed(3) + ' ASTW ' + lineW(AST, 0, AST.length - 1).toFixed(1) + ' SQLW ' + lineW(SQL, 0, SQL.length - 1).toFixed(1));
for (key in T) writeLn('T ' + key + ' ' + T[key].toFixed(3));
app.project.save();
C.name + ' ' + C.duration + ' ' + C.numLayers;
