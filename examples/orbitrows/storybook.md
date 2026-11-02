# OrbitRows video: the storybook

Version 5, all nine scenes: your review of scenes 1 to 3 and the technical review applied. Written from your Excalidraw frame "Video Scenes" and your review notes. No images yet: this is the content, scene by scene. The drawn frames follow scene by scene once you approve the text.

## The example, the steps, the rows

**One example prompt runs through the whole video:**

> Archive the draft Casa products created in September, and show them.

**Six steps, and only six are numbered on screen:**

| 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- |
| Coreference | Split | Action | Matching | Parameter | Operation |

Scene 1 introduces them and scenes 2 to 7 take one each. Scene 8, the assembly, closes the work without a number, and scene 9 closes the video. The smaller steps inside a step (the values, the table, the columns, the ledger…) are named in the narration, never numbered.

**Two workers.** Jev is a System One model: it makes judgment calls by picking among options. An algorithm does the exact work. At every level the pattern is the same: models read the message and propose candidates, the real table proves them, and Jev concludes by choosing. When Jev isn't sure enough, it asks you.

**Rows on screen (real rows of the demo store):**

| Name | Brand | Status | Created |
| --- | --- | --- | --- |
| Desk Lamp | Casa | draft | 2026-09-01 |
| Mug 100% | Casa | active | 2026-09-05 |
| Travel Mug | Casa | active | 2026-08-05 |
| Adapter_USB | Volt | draft | 2026-10-01 |
| Notebook | PaperHub | active | 2026-09-02 |
| Orbit Tee Kids | Orbit | active | 2026-09-03 |

The Desk Lamp is the only row that matches all three conditions, so it is the only row that changes.

**On every screen** the prompt stays in a panel on the right, with the six steps under it and the current one lit. A short plain label at the top left says where we are. Only what the viewer should see is drawn.

---

# Scene 1 · Introduction

**In one line:** the problem, the six steps, and the promise.

## Narration

You have a table of products. You want to change some of them, and you would rather say it in plain English than write a database query. So you type this.

Archive the draft Casa products created in September, and show them.

For a person, this is easy. For a computer, it is full of traps. Which products are "the Casa products"? Is "draft" a status, or a word in a name? Is "September" a word, or a period of time? And what does "them" mean? Get any of these wrong, and the tool changes the wrong rows, quietly.

Many AI tools ask a language model to write the query in one go, and hope it is right. This tool does it differently. It breaks your message down into six small steps: coreference, split, action, matching, parameter, and operation. Each step answers one narrow question, and each answer is checked before the next step starts.

And it makes you a promise: your data stays safe. Every change is versioned, so you can undo it until you save. Every change is schema-safe: it is checked against the structure of your tables before it runs. And if any part of what you asked can't be placed, nothing runs: it stops, and tells you why.

## On screen

1. The product table appears, centred, with the six real rows. The caption reads "rows of a product table".
2. The prompt is typed into an input box under the table, word by word, as the narrator reads it. The table stays where it is. The text is left-aligned in the box, and the whole composition stays centred while there is no panel.
3. The panel slides in from the right and the prompt settles into it. Four question cards appear one by one and stay, then leave together: "the Casa products" (a brand? or a supplier?), "draft" (a status? or a word in a name?), "September" (a word? or a period of time?), "them" (all products? or only the changed ones?).
4. The table comes back in the same place. One row that should not change changes anyway (Mug 100%: Casa, but not a draft), in red: "a wrong reading changes a row you never asked for, and nothing tells you."
5. Centred: "the prompt → language model → records updated", the last box in red, with the caption "one guess, hoping it is right". It stays until the narrator has finished the sentence.
6. "six small steps, each one checked": six numbered cards, three per row, each ticked. They shrink into the panel's list.
7. The promise, in three cards, one per line of the narration: "Versioned: every change can be undone" · "Schema-safe: checked against your tables' structure" · "Nothing dropped: if a part can't be placed, it stops and asks". The three icons are one family.
8. Title card: "OrbitRows: from one sentence to a safe change".

---

# Scene 2 · Step 1, Coreference

**In one line:** meet the two workers, then find what "them" points to.

## Narration

Two kinds of workers do the job. A System One model, called Jev, makes judgment calls: what does this word mean, which column is this about. And an algorithm does everything that must be exact: searching the table's values, building the query, checking it. When Jev is not sure enough, it doesn't guess. It stops, and asks you a question.

Step one: coreference. Some words point back to other words. Here, "them". The tool finds every word that points back, and Jev answers one question for each: what does it point to? Here, "them" means "the draft Casa products created in September": the ones the first part archives. The link is saved for future decisions.

## On screen

1. Two cards slide in: Jev (speech bubble, "makes judgment calls") and the algorithm (gear, "does the exact work").
2. Under Jev: a confidence bar that stops short of "sure enough", and a question card: "'Casa': which column? brand or supplier". The caption: "it never guesses". The two workers shrink into small icons at the top right.
3. A large card "1 · Coreference". Step 1 lights up in the panel.
4. The prompt appears as word chips. "them" turns coral.
5. Dashed outlines appear around every phrase "them" could point to: "the draft Casa products", "created in September", "the draft Casa products created in September". Jev's icon pulses.
6. A coral arrow runs from "them" to the full phrase, which turns solid coral. The others fade. A small tag appears under "them" for two seconds: "= the draft Casa products created in September". The step gets its tick.

---

# Scene 3 · Step 2, Split

**In one line:** cut the message into requests, then decide how they relate.

## Narration

Step two: split. Your message actually asks for two things. The tool marks where each request starts, and Jev confirms every cut. A cut is kept only when Jev is sure. The first request is "archive the draft Casa products created in September". The second is "and show them".

Why so careful? Cutting one request in two by mistake would separate an action from its filter. Keeping two requests together is a smaller error: the next part catches it.

Next, the links. Jev decides how the two requests are related. You wrote "and", but that is not enough to decide. There are two possibilities. With "then", the second request reads the result of the first. With "and", both requests read the original table, as it was before either one runs. Here, "them" points to the products the first request archives, so the tool links the two requests with "then": first archive, then show.

Two more examples, quickly. First, four requests: show the black variants, then raise their price by ten percent, and delete the cancelled sales, but first show every sale. Jev groups them. The price change reads the rows of the first show: that is a "then". The rest is joined by "and": they all read the original table, as one group. So "show every sale" still sees the sales before the delete.

And a swap: put the cost into the price, and the price into the cost. Here Jev picks "and": both parts read the original table, so the values really swap. If the second part read the first one's result, both columns would end up equal.

## On screen

1. A card "2 · Split". The prompt as word chips. The two actions get teal outlines, "archive" and "show". The word "then" gets a lavender outline, "joiner".
2. A dashed cut line appears before "then". A confidence bar fills past the "sure" mark, and the cut turns solid. The prompt splits into two cards: "r1: Archive the draft Casa products created in September" and "r2: and show them".
3. "Why so careful?": two cards side by side. In red, "a wrong cut": the action is torn from its filter, and "every product would change". In teal, "a missed cut": both stay together, "a smaller error, caught at the next step".
4. The two request cards with a coral question mark between them. Jev's icon pulses.
5. Two small diagrams side by side. "then": the table feeds request 1, which feeds request 2 ("request 2 reads the result of request 1"). "and": the table feeds both requests ("both read the original table").
6. "them" gets the coral marker in the panel. The "then" diagram gets a teal frame and a tick; "and" fades. A tag "then" appears for two seconds under "then" in the prompt.
7. Label "Requests grouping". Four request chips; "original table" feeds three branches inside a dashed frame "one group, run together": [1 → 2], [3], [4]. Request 4 is marked "still sees the sales before the delete".
8. The swap: "original table" feeds two requests, "cost → price" and "price → cost". A small before-and-after table slides each value across (Notebook 30/10 becomes 10/30, Desk Lamp 400/250 becomes 250/400). Then a green box "and: the values really swap" and a faded red box "with then: both equal".

**Note:** the swap is intended behaviour, not produced yet; you will fix it before delivery. The four-request example is drawn as you want it (three branches from the original table); in the product's last run it linked 4 before 3 instead. Keep it labelled as intended.

---

# Scene 4 · Step 3, Action

**In one line:** name what each request does, and show that every action works on records or on the structure.

## Narration

Step three: action. Each request needs one kind of action: show, add, change, or delete. And an action can work on two things: the records in a table, or the structure of the table itself. Jev answers once for each request.

Request one changes existing rows: a change. Request two only shows. And since request one changes rows, "them" now means precisely the rows request one changed, not the rows as they were before.

One more example. "Add a column for the warranty" is a change to the structure. The tool recognizes it, and then, for now, it stops and tells you that changing the structure isn't supported yet. Nothing is changed.

## On screen

1. A card "3 · Action".
2. Four empty card slots appear. Their headers fill on the narration: Show, Add, Change, Delete. Under "records" and "structure", each card reveals two paths: Records (SELECT, INSERT, UPDATE, DELETE) and Schema (create a table; add, rename or remove a column; remove a table — showing works on records only).
3. Request 1 gets a badge "change · UPDATE". Request 2 gets a badge "show · SELECT".
4. A mini table shows the rows request 1 changed (status draft → archived). A coral arrow runs into "them" in request 2: "them = these rows". A grey note: "not the rows as they were before".
5. A new request card, "add a column for the warranty", gets a badge "structure change · ALTER TABLE", then a red stop sign: "recognized, then refused for now". The step gets its tick.

---

# Scene 5 · Step 4, Matching

**In one line:** match the words of the message to the real table: the values, the table, the columns, and what each request does to them. This is the part where the tool is most at risk, so it gets the most care.

## Narration

Step four: matching. Now the tool builds the body of each request, from three pieces. What it does, which rows, and how those rows are arranged. It matches them from the bottom up: first the values, then the tables, then the columns, and last, the operations.

First, the values. The tool already knows your table, from when you imported it: "created" holds dates, "status" and "brand" each hold a short list of values, and "name" is free text. So it looks for each value only where it can live. "Casa" is one of the brands. "Draft" is one of the statuses. "September" is no listed value: it is a date. Each value becomes the parameter of a condition.

Next, the tables. Request one works on the products table. Request two names no table: it works on the result of request one. A change always writes to one table: that is how SQLite works. But it can read others to choose its rows, like "the sales of the Casa products". You can also bring in a file, like a supplier's price list: the tool compares it with your store, and can update your store from it, add what you don't have yet, or do anything else you ask in your message. Here, products is enough.

Then the columns. A grammar reader and a meaning model find the column each word names: "created" is the creation date.

Last, the operations. The catalog lists six hundred and eighty-two, and sixty-five of them are production-ready today. For each change, a meaning search keeps the ten closest and offers them to Jev, and Jev picks one: here, "set a value", to archive.

## On screen

1. A card "4 · Matching". Step 4 lights up in the panel.
2. The pattern, as three boxes in a row: "Models propose candidates" → "The real table proves them" → "Jev chooses". It shrinks to a small strip at the top of the stage and stays there, as a reminder, through the next states.
3. **Values.** The prompt as chips, with dashed outlines on "Casa", "draft" and "September". Small labelled chips appear under them, the models that propose candidates: "finds names (GLiNER2)", "finds meaning (multilingual embeddings)", "checks spelling (rapidfuzz)". Then a scan runs down the real product table. It stops on the brand column, which lights up, and the Casa rows turn yellow: "found exactly, in brand". The same for "draft" in the status column. "September" gets a small calendar icon: "stored nowhere: it's a date".
4. Jev's role card: "a value that finds rows" (ticked) against "a new value to write" (faded, with the example "add the supplier Nordic Paper").
5. **Why values first.** Two empty conditions appear: "brand = ?" and "status = ?". "Casa" and "draft" slide into them. The caption: "a condition needs a value".
6. **Table.** Both requests point at "products"; the rows request 1 changed light up for request 2. A dashed "suppliers" card appears: "added only when the request needs it". Jev's icon ticks.
7. **Columns.** Four arrows run from prompt words to columns: draft → status, Casa → brand, created → created_at, The models that find them appear as labelled chips: "grammar reader (spaCy)", "meaning (multilingual embeddings)".
8. **Parts.** A wall of 682 small dots appears, each one an operation, with a counter: "682 operations in the catalog". 65 of them light up: "65 switched on". A meaning search, labelled "meaning search (bge-small-en)", narrows them to the ten closest to "change a text value": "10 offered to Jev". Jev picks one: "set a value". The counter reads 682 → 65 → 10 → 1. Then "Request 2: shows every column", with an eye icon. The caption: "one of the most delicate moments". A strip: "models search → Jev chooses → an algorithm builds". The step gets its tick.

---

# Scene 6 · Step 5, Parameter

**In one line:** numbers and dates become exact values. A black box: only what goes in and what comes out.

## Narration

Step five: parameter. Written numbers and dates are turned into exact values by a module of their own. "In September" becomes a whole period: from the first of September up to, but not including, the first of October.

Two more examples with numbers. "Weigh more than two hundred grams" becomes the number two hundred, in grams, converted to the unit the weight column uses. And "by twenty", without a percent sign, stays a plain twenty: it is never silently taken for a percentage.

## On screen

1. A card "5 · Parameter".
2. A box in the middle, "number and date reader", with the algorithm icon and the note "a module of its own". "in September" goes in on the left; a calendar band comes out on the right: "1 Sep → 1 Oct (the end is not included)". The inside of the box is never shown.
3. "more than 200 grams" goes in; "200 · grams · converted to the column's unit" comes out.
4. "by 20" goes in; "20, a plain number, not a percentage" comes out. The step gets its tick.

---

# Scene 7 · Step 6, Operation

**In one line:** build the conditions and the operations, order them, and join them.

## Narration

Step six: operation. First, the conditions. For each written value, the tool builds one condition on a column. For request one there are three: the status is "draft", the brand is "Casa", and the creation date is within September.

Next, the operations. When a request changes a number, the change is cut into small operations, each matched to a tested one by the same meaning search as before. Here the change is just a word, "archived", so there is nothing to calculate. A harder example: "raise the price of the variants by fifteen percent, then take five off, round to the nearest five". That becomes three operations: plus fifteen percent, minus five, and round to five.

Then the graph. Each operation points to the value it uses, in the order you mean. Here: the current price, plus fifteen percent, minus five, round to five, and the new price. And if you add "but for the black ones, apply the fifteen percent after the five", a second path runs minus five, then plus fifteen percent. Both paths meet in a choice, by row.

Last, the grouping. The conditions are joined: do they all have to be true, or just one? For request one: draft and Casa and September. Request two has no sort and no limit. A harder example: "the September sales with a discount above five, or a quantity of at least two". That becomes September, and either of the two.

## On screen

1. A card "6 · Operation". Request 1 with its three words lit one by one, each building a chip: "status = draft", "brand = Casa", "created within September". After each chip, the table dims the rows that fail it: "draft" removes Mug 100%, Travel Mug, Notebook and Orbit Tee Kids; "Casa" removes Adapter_USB. One row stays lit: the Desk Lamp.
2. The change "status → archived" is a word: a grey note, "nothing to calculate". Then the harder prompt appears, and three operations drop in as chips: "+15%", "−5", "round to 5". The "meaning search" chip from scene 5 appears again, with the note "the same search".
3. The three operations line up: current price → +15% → −5 → round to 5 → new price. Then the black variants: a second path, −5 → +15%, joins the first in a "choice by row" node, before the rounding.
4. The three conditions of request 1 join with AND, then a tick. A further example: the September sales, with a bracket around the two alternatives: "discount > 5 OR quantity ≥ 2". The step gets its tick.

---

# Scene 8 · Assembly

**In one line:** the safety net, the final instruction, the questions, and the run, with undo.

## Narration

Last, the assembly. First, the ledger. Every value you wrote must be used by some part of the request, or the request is refused. Here, "draft", "Casa" and "September" are each used by a condition, so request one is allowed. Now imagine "the variants without a barcode that weigh more than two hundred grams", where "two hundred grams" ends up in no condition. The query would still look fine, and it would run, on far more rows than you meant. So the tool refuses, and says which words it couldn't place.

Then the assembly itself. The tool builds one checked instruction per request. Request one: archive the products where the status is draft, the brand is Casa, and the creation date is in September. Request two: show the products request one changed. Each instruction is tried once and immediately undone, to prove the database accepts it.

Next, the questions. Any decision Jev isn't sure about pauses the request and asks you. Here there are none, because every answer was sure. A different example: "raise the price of the Orbit Hoodie variants by twenty". The request pauses and asks: twenty percent, or an amount of twenty? It continues after you answer.

Finally, the run. The session runs both instructions. The Desk Lamp, which was a draft, from Casa, created on the first of September, becomes archived, and request two shows it. Nothing is final yet. "Undo" puts it back to draft. "Exit" saves the change.

## On screen

1. A card "Assembly", without a number. Two columns: "found in the message" (draft, Casa, September) and "used by" (the three conditions), each row ticked. Then the refusal example: the "200 grams" row turns red, and the screen reads: "the number '200 grams' used by no part of the request. Nothing changed."
2. Two readable instruction cards, one per request, built word by word; three small ticks: "well formed", "every column exists", "the database accepts it".
3. The Orbit Hoodie prompt, a pause icon, and a question card with two answer chips: "20 %" and "an amount of 20".
4. The product table: the Desk Lamp row, the only one that matched, changes from draft to archived, and request 2's result shows it. An "undo" button flips it back to draft. An "exit" button saves; a small "Saved." appears. The step gets its tick.

---

# Scene 9 · Conclusion

**In one line:** recap on the same example, then close on the promise.

## Narration

One message, six steps, many small decisions. Three things to remember. One: Jev makes judgment calls, one narrow question at a time, and an algorithm does everything that must be exact. Two: when Jev isn't sure, you are asked. Three: nothing runs unless every value you wrote has a place in the request, every change is checked against the structure of your tables, and every change can be undone until you save it.

OrbitRows: from one sentence to a safe change.

## On screen

1. The six steps replay in a row, one line each, showing what each did on our prompt: "them = the Casa drafts" · "two requests, first archive then show" · "archive = change, show = show" · "Casa = brand, draft = status, September = a date" · "September = 1 Sep to 1 Oct" · "three conditions, all true". A last line without a number: "then: checked, built, run, and can be undone".
2. The two worker icons reappear side by side. The "ask" card from scene 2 flashes once.
3. The three promise cards from scene 1 return, then the title card.

---

## Decisions taken

1. Steps 1 and 2 of your frame (Guard and Sources) are not mentioned anywhere in the video.
2. "Schema-safe" means that every change is checked against the schema, the structure of your tables. It is the second card of the promise in scenes 1 and 9.
3. The structure example in scene 4 stays: recognized, then refused for now.
4. Only six steps are numbered on screen. Assembly closes the work without a number.
6. As few transitions as possible, and nothing on screen the viewer doesn't need.
5. The change step of your frame is called "operation", never "formula".
