# TOFIX

Findings from a code scan on 2026-10-04.

## High

- `src/stickread.c:88` - `if (pevent->keycode == 'q') ;` has a stray empty statement, so `exit(0)` on the next line runs for every key press; it also compares a hardware keycode to an ASCII char. Use `XLookupString` and test the char like `src/dance.c:190` and `src/stickman.c:127` do.
- `INSTALL:1` - the whole file describes the removed Makefile (`make`, `sudo make install`, editing `DEST`, XFree). The build is now `rsconstruct build` driving `scripts/build_xmeltdown.py` into `out/bin/`. Rewrite it for the current build or delete it.

## Medium

- `rsconstruct.toml:51` - `input_globs = ["src/*.c", "protocol/*.xml"]` leaves out `src/stickman.h` (included by draw/stickman/stickread/dance) and `scripts/build_xmeltdown.py`. The explicit processor only rebuilds when a listed input changes, so editing the header or the build script leaves stale binaries. Add `src/*.h` and the script to the inputs.
- `src/stickread.c:199`, `src/dance.c:276` and `src/dance.c:320` - the read loops run `while (okayflag >= 0)`, and `fscanf` returns 0 on a format mismatch, so a malformed pose file loops forever allocating skeletons. The `Fill()` return value (`src/stickread.c:243`, `src/dance.c:364`) is ignored too. Loop on `okayflag == 3` and check that `Fill()` returns 2.
- `doc/TODO.txt:1` - its only item is about `make depend` changing the Makefile, which no longer exists. Delete the stale item or the file.

## Low

- `support/uncrustify.cfg`, `support/uncrustify.full.cfg` - nothing references them (`rsconstruct.toml:46` says the uncrustify target was dropped with the Makefile). Either wire them into an rsconstruct formatter/checker or delete them.
- `rsconstruct.toml:49` - the explicit processor runs `gcc`, `pkg-config` and `wayland-scanner` through a wrapper script but sets no `required_tools`, so `rsconstruct tool` cannot report them missing. Declare them.
- `pyproject.toml:10` - `pytest` is in the dev group, but the repo has no tests and no pytest processor. Drop it, or add a test for `scripts/build_xmeltdown.py`.
