#!/usr/bin/env python3
"""Build the standalone Starter with Python's standard library and a local JDK."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parent


def jdk_tool(name):
    java_home = os.environ.get("JAVA_HOME")
    suffix = ".exe" if os.name == "nt" else ""
    candidate = Path(java_home) / "bin" / (name + suffix) if java_home else None
    found = str(candidate) if candidate and candidate.is_file() else shutil.which(name)
    if not found:
        raise ValueError(f"Missing {name}. Install JDK 25 or newer and set JAVA_HOME or PATH.")
    return found


def dependency(value, option, required_entry):
    if not value:
        raise ValueError(f"Supply {option}; see the README for the two provided dependencies.")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Dependency not found: {path}")
    with ZipFile(path) as archive:
        if required_entry not in archive.namelist():
            raise ValueError(f"Wrong dependency JAR: {path} (missing {required_entry})")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-jar", default=os.environ.get("HYTALE_SERVER_JAR"))
    parser.add_argument("--manager-jar", default=os.environ.get("TEXTURE_PACK_MANAGER_JAR"))
    args = parser.parse_args()
    try:
        server = dependency(args.server_jar, "--server-jar", "com/hypixel/hytale/server/core/plugin/JavaPlugin.class")
        manager = dependency(args.manager_jar, "--manager-jar", "Vitja/TexturePackManager/api/TexturePackApi.class")
        javac, jar = jdk_tool("javac"), jdk_tool("jar")
        version_text = subprocess.run([javac, "-version"], capture_output=True, text=True, check=True)
        match = re.search(r"javac\s+(\d+)", version_text.stdout + version_text.stderr)
        if not match or int(match.group(1)) < 25:
            raise ValueError("JDK 25 or newer is required; the build targets Java 25.")
        manifest = json.loads((ROOT / "resources/manifest.json").read_text(encoding="utf-8"))
        output = ROOT / "build" / ("texture-pack-starter-" + manifest["Version"] + ".jar")
        output.parent.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(ROOT / "tools/index_textures.py")], check=True)
        sources = sorted((ROOT / "src").rglob("*.java"))
        if not sources:
            raise ValueError("No Java source files found under src/.")
        with tempfile.TemporaryDirectory(prefix="texture-pack-starter-") as temporary:
            work = Path(temporary)
            classes = work / "classes"
            classes.mkdir()
            subprocess.run([javac, "--release", "25", "-encoding", "UTF-8", "-cp",
                            os.pathsep.join((str(server), str(manager))), "-d", str(classes),
                            *map(str, sources)], check=True)
            resources = work / "resources"
            shutil.copytree(ROOT / "resources", resources)
            shutil.copyfile(ROOT / "LICENSE.md", resources / "LICENSE.txt")
            subprocess.run([jar, "--create", "--file", str(output),
                            "--date=2026-01-01T00:00:00Z", "-C", str(classes), ".",
                            "-C", str(resources), "."], check=True)
        with ZipFile(output) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Duplicate entries in built JAR.")
            if any(n.startswith(("com/hypixel/", "Vitja/TexturePackManager/")) for n in names):
                raise ValueError("Dependency classes must not be bundled in the Starter.")
            if any(n.endswith((".java", ".py", ".log", ".zip")) for n in names):
                raise ValueError("Unexpected development files in built JAR.")
            if json.loads(archive.read("manifest.json")) != manifest:
                raise ValueError("Packaged manifest differs from resources/manifest.json.")
            index = archive.read("textures.list").decode("utf-8").splitlines()
            for path in index:
                if "Common/" + path not in names:
                    raise ValueError(f"Missing packaged texture: {path}")
            main_class = manifest["Main"].replace(".", "/") + ".class"
            if main_class not in names:
                raise ValueError("Manifest main class is missing from the built JAR.")
        digest = sha256(output.read_bytes()).hexdigest()
        output.with_suffix(".jar.sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
        print(f"Built {output}\nSHA-256 {digest}\nInstall it beside the Manager, restart, then enable it in /texturepacks.")
    except (ValueError, OSError, BadZipFile, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
