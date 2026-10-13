# Motion-design principles

Goal: it should look like a motion designer made it, not like slides with transitions.

## 1. General principles

1. **One beat, one idea**: every narration line gets one visual change. What the viewer hears, they see.
2. **Enter → hold → exit**: enter fast (0.3–0.6 s), hold long enough to read, exit before the next scene. Don't let things pile up.
3. **At most 3 focal elements**: the emptier the frame, the clearer the point.
4. **Size contrast**: key words are big (shorts stickers 56–130 px, wide titles 110–170 px); supporting text is small.
5. **Easing sets the feel**:
   - Playful hand-drawn: `back.out(2)` bounce, `power4.in` slam.
   - Premium: `expo.out` slow settle, blur (rise), lots of white space.
6. **Motion has direction**: processes flow left to right, time flows top to bottom. Arrows are *drawn*, not just shown.
7. **Host character**: greets in the centre, steps to a corner (scale 0.45–0.6) while explaining, and returns for the close.
8. **Subtitles stay readable**: highlight key words with `hl`; nothing may cover the subtitle area.
9. **Outro**: one-line summary plus next-episode teaser or brand name, held for at least 2 seconds.

## 2. shorts (hand-drawn)

- Look: cream paper, thick black ink lines (6–10 px), hard shadows (8px 8px 0 black), orange accent.
- Texture comes from line boil (re-seeded every 0.1 s), film grain, dust and slight frame weave. These are built in.
- Props: draw everyday objects (phone, door, key, box, restaurant) as simple geometric SVG — thick lines, little detail, flat colour.
- Palette: `--accent` orange, `--teal`, `--sky` blue, `--yellow`, `--red`, `--green`, `--cream`, `--ink`.

## 3. wide (premium)

- Look: dark gradient, gold bokeh, glass cards, large serif headings, generous space.
- Slower rhythm than shorts: entrances 0.8–1.2 s, staggers 0.08–0.2 s.
- Data should *grow*: counting numbers (count) plus growing bars (bar), with a small footnote naming the data source.
- Screenshots go *in a frame*: the `.shot` browser frame with `tilt` and `sheen`.
- Brand colours: don't edit `_runtime/runtime.css` (it gets overwritten). Override in the `<style>` block of `index.html`, e.g. `:root{--gold:#4FA3FF;--glow-rgb:79,163,255;}`.

## 4. Checklist (go through it on every contact sheet)

- [ ] Each frame makes clear what that line is about
- [ ] No text overflows its card or the frame
- [ ] No elements overlap (especially the host)
- [ ] Subtitles are never covered and never exceed two lines
- [ ] The previous scene's elements are gone
- [ ] The other language version also lays out correctly
- [ ] The outro text is complete
