# 6. Style and review rules

The rules the user set while directing the OrbitRows video. They are the review checklist for every scene. The colours and fonts are that video's identity; the other rules apply to any explainer.

## Motion

- **Animate only what changes.** A new arrow, outline or tag appears by itself; the rest of the screen stays still.
- **Never cross-fade a whole screen or a whole diagram to add one element.** The viewer sees the graph "reload".
- Enter and leave in 250–400 ms, ease-out, no bounce. Nothing decorative moves.
- As few transitions as possible.
- **Nothing appears before its words.** Every element shows in on its cue word, and goes out at least 1 s after its last spoken word.
- Elements that stay on screen are built once and never redrawn. Within a part, only the element named moves; a part's elements fade out together, once, before the next part.

## What is on screen

- **The screen starts empty and shows only what the voice is talking about.** Hide each thing before the next idea. One idea at a time.
- **Nothing on screen that is a note.** Editing notes ("kept on the right", motion paths, sources) never appear in a frame, in the storyboard or in the video. (A note once got built on screen; the user was upset.)
- Short text on screen. The narration explains; the screen names.
- No scene numbers on screen. A short plain-words label at the top left says where we are (coral dot + a few words, purple, Poppins SemiBold).
- No decorative icons. Question cards appear and stay.
- Show what the product does today. Black-box modules (in OrbitRows: number and date extraction) are one box with a plain name; never explain their inside.
- Use the product's words consistently (in OrbitRows: "the prompt", not "the request"; "algorithm", never "code", for the non-model worker).

## The right panel

A panel on the right keeps what the viewer needs to judge without memorising:

- "THE PROMPT": the example, on 3 compact lines, plain (no markers, tags or strikes on it from scene 2 on).
- "WHERE WE ARE": the numbered steps; the active step teal, a finished step gets a green tick.
- Facts show as a small tag under the prompt's words only at the moment they are found, hold ~2 s, then leave. No permanent "What we know" list.
- A highlighted word stays ink, regular weight, with a coral marker behind it (45 %, 3 px padding, 4 px corners, 300 ms fades).
- The panel appears once the prompt is typed and carries over between scenes. It may slide out when an example needs the full width (then stays out to the end of that scene).

## Colour (one meaning each)

| Colour | Hex | Meaning |
| --- | --- | --- |
| Pale green | `#F9FEF6` | the one background for the whole video (no alternating backgrounds) |
| Deep teal | `#0A6E89` | containers, data, the active step |
| Coral | `#FB938F` | what is being discussed; the language model |
| Yellow | `#FED84D` | the algorithm; highlights |
| Lavender / purple | `#C9BCEB` / `#6D5BA8` | connectors, menus, labels |
| Green | `#1FA35B` | a check passed |
| Red | `#E63946` | wrong or refused, only |
| Ink / code panel | `#2C353A` (active line `#1D5980`) | text, code |

Flat solid shapes. No shadows, gradients or textures.

## Type

- Poppins (Bold for titles and labels, Regular for text).
- JetBrains Mono for values, SQL, chips and code. Break its `>=` ligature with a zero-width non-joiner.
- Install the fonts before building; check the PostScript names (docs/04).

## Icons

- One family: same stroke weight (2 px charcoal, round caps and joins), same margin, one flat accent colour each, readable at 56 px on a 64×64 viewBox.
- Recurring characters stay distinct (the model a coral speech bubble, the algorithm a yellow gear); their colours aren't used on other icons.
- Plain paths, rects and circles in one group. No arc commands, filters, masks, clip paths, embedded images, text or leftover transforms. Holes as even-odd compound paths.

## Placement checks (every still)

- Centred things are really centred.
- Chips of one line sit on one baseline; values in a column start at the same x.
- Highlights exactly behind their word.
- Nothing overlaps an arrow or a label; arrowheads touch their target, not enter it.

## Voice and sound

- Never time-stretch, never denoise the speech, never stitch comma-sized clips.
- Sentence endings must close (falling pitch, full release). A clipped ending is the most noticed fault.
- No digital silence anywhere; no room tone that switches on and off.
- Music well under the voice (-32 dB), rising only in long pauses and scene holds.

## Process

- One scene at a time; the user confirms each scene before any work on the next.
- Every render gets a new version; the one under review is never overwritten.
- Directed small fixes are applied without another confirmation round; report them.
