# Figure checklist

Operator spec for the joke figures. Not a player file. The page loads the generators through `/get/images`; this file is how you tell a bad SVG from the joke.

`scripts/render-figures.sh` writes a gallery. Compare each picture to the list under its name. If a mark is missing, the generator is wrong.

References, so the jokes stay tied to something real:

- "have you tried ghidra-mcp?" is the February 2026 Show HN, [Ghidra MCP Server, 110 tools](https://news.ycombinator.com/item?id=46882389). The "did you install kali?" half is the older support-desk loop. No specific HN post for that one.
- left-pad is the March 2016 npm collapse. The picture's "11 lines" is the joke about that tiny package, not an audit.
- The decompiler card is the other 2026 Ghidra-and-AI thread: a confident summary over a listing that already gave up. It is not a claim about any one paper's result.
- The rest are standing jokes, not posts I could pin: endian `DEADBEEF`, `file(1)` refusing to pick a species, a Go binary that is mostly `runtime.*`, base64 presented as encryption, and a one-byte `jz`/`jnz` patch. The patch picture is the joke, not a recipe.

## 01_advice.py

Two columns on a white card, split by a light gray vertical line.

- Left title: `old advice`. Boxes, top to bottom: `won't disassemble`, `did you install kali?`, `install kali`.
- Right title: `new advice`. Boxes, top to bottom: `still won't`, `have you tried ghidra-mcp?`, `all 110 tools`.
- The two question boxes are red. The other boxes are black.
- Each column has arrows down, and a red loop from the bottom box back to the question box. Neither loop is a yes/no branch.
- Footer, red: `the bytes remain unread`.
- No text is cut off by a box edge. The long question fits on one line inside its box.

## 02_strings.py

A white card that reads as `xxd` / `strings`, monospace.

- Header: `strings(1)`.
- Six rows, eight bytes each. Addresses `0000`, `0008`, `0010`, `0018`, `0020`, `0028`.
- The third data row is highlighted yellow in both the hex and the ASCII column. Its ASCII is `SEGFAULT`.
- Every other ASCII cell is a dot. No second readable word.

## 03_leftpad.py

- Title: `to print one byte`.
- `main` on top, with arrows down to `capstone`, `binwalk`, and `left-pad`.
- `left-pad` is the red box. Under it, red: `11 lines` and `1 byte`.
- Arrowheads meet the top of each lower box. They do not float in the gap or cover the words.

## 04_decompile.py

A white card, not a copy of anyone's decompiler skin.

- Gray header bar reading `decompile`.
- Yellow banner: `AI summary: function is fine`.
- Monospace listing below it, in this order: `undefined FUN_08001234(void)`, an opening brace, `if (real)`, `respect();`, a closing brace for the if, `/* stopped here */`, a closing brace.
- Red footer: `backdoor not included`.
- The listing is left-aligned and does not run into the footer.

## 05_solid.py

The math-meme picture. No words.

- White card.
- Two wireframe cubes sharing a center. One black, one red, the red one turned about 45 degrees.
- Each cube has 12 edges. Corners are not clipped by the card. It should read as a solid, not a scribble or a flat hexagon.

## 06_endian.py

- Title: `the same four bytes`.
- One yellow row: `DE` `AD` `BE` `EF`.
- Under it, `big-endian` reads `DEADBEEF` and `little-endian` reads `EFBEADDE` in red.
- Red footer: `the beef moved`.
- The two readings are of that one row, not two different dumps.

## 07_file.py

A monospace `file(1)` card.

- Header: `file(1)`. Command: `$ file blob`.
- Four answers, in order: `data`, `PE32 executable`, `Zip archive data`, `JPEG image data`.
- Red footer: `pick one`.
- No fifth guess. The lines do not wrap.

## 08_sections.py

A bar chart, not a table of numbers.

- Title: `section sizes`.
- Three rows: `.text`, `.data`, `.rsrc`.
- `.text` is a short black bar. `.data` is shorter. `.rsrc` is a long red bar, several times the others, and does not run off the card.
- Red footer: `the program is the resource`.

## 09_stripped.py

- Small title: `symbols`.
- One box `a` with arrows down to `a.1`, `a.2`, and `a.3`.
- No other names. Red footer: `the names were the documentation`.
- Arrowheads meet the top of the lower boxes.

## 10_base64.py

- Title: `encrypted payload`.
- Top box: `aGVsbG8=`. Arrow down to a red-outlined box: `hello`.
- Red label `base64`, then red footer `the key was the alphabet`.
- `hello` is the decoding of that blob. Nothing else is in the boxes.

## 11_imports.py

- Title: `import address table`.
- A gray header `name`, then `GetProcAddress`, `LoadLibraryA`, and a gray `...`.
- Red footer: `the rest arrive later`.
- No third real import.

## 12_progress.py

- Title: `auto-analysis`.
- A yellow bar labeled `99%`, with a visible empty gray sliver on the right. The sliver is the point. A full bar is wrong.
- Under it: `still running`. Red footer: `99% since lunch`.

## 13_rename.py

- Two columns, `before` and `after`.
- Before, black box: `FUN_00401234`. After, red box: `FUN_00401234_1`.
- Red footer: `much clearer`.
- The after name is the before name plus `_1`. It still fits in the box.

## 14_runtime.py

A short `strings(1)` list, the Go-binary joke.

- Gray lines, in order: `runtime.mallocgc`, `runtime.morestack`, `runtime.convT64`, `runtime.gcBgMarkWorker`, `runtime.memmove`.
- Between `runtime.convT64` and `runtime.gcBgMarkWorker`, one yellow line: `main.main`.
- Red footer: `the program is in there`.
- `main.main` is the only highlighted line.

## 15_patch.py

- Title: `the patch`.
- Before: `74` `0A` and the mnemonic `jz`.
- After: `75` `0A` and the mnemonic `jnz`. The `75` cell is yellow with a red outline. `0A` is unchanged.
- Red footer: `one byte`.
- This is the whole joke. No surrounding shellcode, no addresses.
