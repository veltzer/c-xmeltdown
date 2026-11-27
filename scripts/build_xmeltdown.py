#!/usr/bin/env python

""" Build the five X11 demos, reproducing the Makefile: compile each src/*.c to
<name>.o, then link the per-binary object groups (draw.o is shared by
stickman, stickread and dance) with -lX11 -lm. File arguments are ignored -- the
object groups below define the build.

Also builds wlmelt, the Wayland port of xmeltdown: wayland-scanner turns the
protocol XMLs (vendored wlr ones in protocol/, standard ones from the installed
wayland-protocols) into headers and glue code, which wlmelt.c is compiled
against and linked with -lwayland-client -lpng.

The objects and the generated protocol code go to a temporary directory, so
only the declared binaries land in the tree. """

import os
import subprocess
import sys
import tempfile

CC = "gcc"
CFLAGS = ["-Wall", "-Werror", "-pedantic", "-O3"]
BIN_FOLDER = os.path.join("out", "bin")

# protocol name -> XML location; None means the installed wayland-protocols
PROTOCOLS = {
    "wlr-layer-shell-unstable-v1": os.path.join("protocol", "wlr-layer-shell-unstable-v1.xml"),
    "wlr-screencopy-unstable-v1": os.path.join("protocol", "wlr-screencopy-unstable-v1.xml"),
    # wlr-layer-shell's generated code references xdg_popup
    "xdg-shell": None,
    "viewporter": None,
}
STANDARD_PROTOCOL_PATHS = {
    "xdg-shell": os.path.join("stable", "xdg-shell", "xdg-shell.xml"),
    "viewporter": os.path.join("stable", "viewporter", "viewporter.xml"),
}

# binary name -> (object stems it links, libraries)
BINARIES = {
    "grid": (["grid"], ["-lX11", "-lm"]),
    "stickman": (["stickman", "draw"], ["-lX11", "-lm"]),
    "stickread": (["stickread", "draw"], ["-lX11", "-lm"]),
    "dance": (["dance", "draw"], ["-lX11", "-lm"]),
    "xmeltdown": (["xmeltdown"], ["-lX11", "-lm"]),
    "wlmelt": (["wlmelt"] + [f"{name}-protocol" for name in PROTOCOLS],
               ["-lwayland-client", "-lpng"]),
}


def run(cmd):
    """ Run a command, exiting the process on the first failure. """
    ret = subprocess.call(cmd)
    if ret != 0:
        sys.exit(ret)


def generate_protocols(gen_folder):
    """ Generate client headers and glue code for the Wayland protocols. """
    pkgdatadir = subprocess.check_output(
        ["pkg-config", "--variable=pkgdatadir", "wayland-protocols"],
        text=True).strip()
    for name, protocol_xml in PROTOCOLS.items():
        xml = protocol_xml
        if xml is None:
            xml = os.path.join(pkgdatadir, STANDARD_PROTOCOL_PATHS[name])
        header = os.path.join(gen_folder, f"{name}-client-protocol.h")
        code = os.path.join(gen_folder, f"{name}-protocol.c")
        run(["wayland-scanner", "client-header", xml, header])
        run(["wayland-scanner", "private-code", xml, code])


def compile_objects(stems, tmp):
    """ Compile each unique source stem to an object file in tmp. """
    for stem in stems:
        obj = os.path.join(tmp, stem + ".o")
        src = os.path.join(tmp, stem + ".c") if stem.endswith("-protocol") else os.path.join("src", stem + ".c")
        run([CC, *CFLAGS, "-I", tmp, "-c", "-o", obj, src])


def main():
    """ main entry point """
    with tempfile.TemporaryDirectory() as tmp:
        generate_protocols(tmp)
        stems = sorted({stem for group, _libs in BINARIES.values() for stem in group})
        compile_objects(stems, tmp)
        os.makedirs(BIN_FOLDER, exist_ok=True)
        for name, (group, libs) in BINARIES.items():
            objs = [os.path.join(tmp, stem + ".o") for stem in group]
            run([CC, "-o", os.path.join(BIN_FOLDER, name), *objs, *libs])


if __name__ == "__main__":
    main()
