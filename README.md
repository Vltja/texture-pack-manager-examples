# Texture Pack Manager — API Guide and Starter

A small, buildable texture-pack mod for **Texture Pack Manager 0.3.1 / API v1**.
Use it as a starting point for your own packs. It registers three original
diagnostic stone textures using Hytale's native **Common/** paths.

## New here? Start with the beginner guide / Neu hier? Starte hier!

**No Java knowledge needed for your first test. / Für deinen ersten Test sind keine Java-Kenntnisse nötig.**

- **[Deutsch: Dein erstes Texture Pack – Schritt für Schritt](docs/BEGINNER_DE.md)** – mit Windows-PowerShell-Befehlen, Beispieltexturen, Mod-Namen, Pack-ID, Installation und Fehlerhilfe.
- **[English: Your first texture pack – step by step](docs/BEGINNER_EN.md)** – with copyable build commands, edits to real files, installation and troubleshooting.

**Quick route:** Download **Code → Download ZIP** → change the PNGs in `resources/Common/` → edit `resources/manifest.json` and `src/Vitja/TexturePackStarter/StarterPack.java` → run `build.py` with your server/manager JAR paths → install the built JAR next to the manager → enable it with `/texturepacks` and **Apply / Reload**. Follow the beginner guide for every step; the two required dependency JARs are **not** included.

**Ask ChatGPT with your own GitHub URL / Mit ChatGPT und deinem GitHub-Link:**

1. Copy the URL of **this repository** or **your own public fork**.
2. Paste it into ChatGPT and ask: *„Lies dieses Repository und erkläre mir als Anfänger Schritt für Schritt, wie ich daraus mein eigenes Hytale-Texture-Pack erstelle. Zeige mir genau, welche Dateien ich bearbeiten, wie ich die JAR bauen und im Spiel testen muss. Mein Link: [hier GitHub-URL einfügen].“*
3. For a longer, copyable prompt, see **[Deutsch](docs/BEGINNER_DE.md#9-hilfe-mit-chatgpt-github-link-kopieren)** or **[English](docs/BEGINNER_EN.md#9-ask-chatgpt-using-your-github-link)**.

**Access note:** Public GitHub URLs can be read when ChatGPT has web access; private repos or edits require explicitly authorized connections. Pasting a URL **does not grant ChatGPT PC access or GitHub write access**. GitHub Actions/CI by itself does not grant either; it runs configured workflows.

| Start here | Link |
|---|---|
| Beginner guide (German / English) | [Deutsch](docs/BEGINNER_DE.md) · [English](docs/BEGINNER_EN.md) |
| Complete API guide | [Documentation website](https://vltja.github.io/texture-pack-manager-examples/) · [Markdown reference](docs/API.md) |
| Download all example sources | **[Source ZIP](https://github.com/Vltja/texture-pack-manager-examples/archive/refs/tags/v1.0.0.zip)** or **Code → Download ZIP** |
| Try the compiled demo | **[Starter 1.0.0 JAR](https://github.com/Vltja/texture-pack-manager-examples/releases/download/v1.0.0/texture-pack-starter-1.0.0.jar)** · [Release/checksum](https://github.com/Vltja/texture-pack-manager-examples/releases/tag/v1.0.0) |
| Required Manager | [Texture Pack Manager on CurseForge](https://www.curseforge.com/hytale/mods/texture-pack-manager) |

**The example uses two separate dependencies: the Manager JAR and HytaleServer.jar.**
The Manager implementation and Hytale SDK are not included.
Pack selection is server-wide: all players receive the same effective textures
selected by the administrator. Personal per-player packs are currently unsupported.

## Build from source

### 1. Get the prerequisites

- **JDK 25 or newer**, with **javac** and **jar** on PATH (or set JAVA_HOME). The build targets Java 25.
- **Python 3.9 or newer**. Building the mod uses only Python's standard library; no pip packages, Gradle or Maven are required.
- Your legally obtained **HytaleServer.jar**, matching your server.
- **texture-pack-manager-0.3.1.jar**, downloaded separately from CurseForge.

Obtain the server JAR through your Hytale installation or the
[official server distribution workflow](https://support.hytale.com/hc/en-us/articles/45326769420827-Hytale-Server-Manual).
Do not upload either dependency to this repository or bundle its classes in a pack.
**Built/checked with Hytale 0.7.7**; the manifest supports **>=0.7.0 <0.8.0**.
On a new Manager release, CurseForge may need to approve the project/file before
the public download appears. The initial Manager 0.3.1 submission is awaiting
that approval; building requires obtaining both dependency JARs separately.

### 2. Download and extract the source

Choose **Code → Download ZIP**, extract it and open a terminal in the folder
containing **build.py** and this README. Alternatively:

~~~sh
git clone https://github.com/Vltja/texture-pack-manager-examples.git
cd texture-pack-manager-examples
~~~

### 3. Build the JAR

On **Linux/macOS**, run this as one command, replacing both paths:

~~~sh
python3 build.py --server-jar "/path/to/HytaleServer.jar" --manager-jar "/path/to/texture-pack-manager-0.3.1.jar"
~~~

On **Windows PowerShell**, run:

~~~powershell
py -3 build.py --server-jar "C:\path\to\HytaleServer.jar" --manager-jar "C:\path\to\texture-pack-manager-0.3.1.jar"
~~~

Alternatively, set **HYTALE_SERVER_JAR** and **TEXTURE_PACK_MANAGER_JAR** to those
absolute paths and run **python3 build.py** (or **py -3 build.py** on Windows).
Quote paths containing spaces. The script needs no sibling project or private build script.

The output is **build/texture-pack-starter-1.0.0.jar**, plus a SHA-256 checksum.
Missing files or JDK tools produce an actionable error.
The portable script is verified on Linux; Windows/macOS use the same Python/JDK
workflow but have not received separate native acceptance tests.

## Try the demo

1. Put the Manager JAR and Starter JAR in the server's **mods/** directory.
2. Restart the server. Keep one installed version of each plugin identity.
3. With permission **vitja.texturepacks.admin**, run **/texturepacks**.
4. Enable **Texture Pack Starter** and choose **Apply / Reload**.
5. Inspect ordinary stone, including its variants. Three diagnostic patterns make the replacement recognizable.
6. Disable the Starter and Apply again to restore the captured baseline. **/tpm reset** disables all registered packs and applies restoration.

A new pack ID starts disabled. The Starter adds no items, commands, entities,
recipes or background tasks: it registers during setup and unregisters on shutdown.
These are diagnostic images; the author's first artistic texture pack is a separate
upcoming project. The Manager download itself contains no texture collection.

## Create your own texture-pack mod

**First time?** Follow the [German](docs/BEGINNER_DE.md) or [English](docs/BEGINNER_EN.md) beginner guide. For a first **local test**, you can keep the existing Java package and manifest `Main` while changing your manifest identity, `StarterPack.ID`, display metadata and PNGs. Rename the Java package and update `Main` **before publishing**. The steps below describe a fully renamed project.

1. Rename the Java package/classes and manifest **Group**, **Name**, **Main**, **Authors** and **Version** consistently.
2. Give **StarterPack.ID** your own stable, unique ID. Do not publish an unrelated pack as **vitja.starter.stone**.
3. Add your replacement PNGs under **resources/Common/**, keeping exact native paths and case. An API target omits the Common/ prefix.
4. Run the build. It regenerates **resources/textures.list**, compiles and packages your resources.
5. Test enable/disable, overlaps, higher/lower priority, missing-texture fallback and restoration on actual consumers.

The index and StarterPack reader are example-local helpers, not a required Manager
format or automatic runtime scanning API. Keep **IncludesAssetPack: false** so
the Manager controls which replacement textures are applied. Do not copy or shade
Manager/SDK classes into your JAR. For another mod's textures, use its existing
Common paths and require that content mod as an additional dependency.

### CurseForge dependencies

The root manifest must require **Vitja:TexturePackManager**. Additionally, each
published CurseForge pack file must list [Manager project **1799221**](https://www.curseforge.com/hytale/mods/texture-pack-manager)
as **Required Dependency**. Mod-specific patches also require their content mods.
A manifest identity is different from CurseForge's numeric project ID.

The Starter uses "*" as a simple manifest example; choose an appropriate tested
Manager version constraint for your own release. Verify saved relations and the
intended installer's behavior. Manual browser/JAR downloads do not install missing
dependencies. See the [dependency guide](docs/API.md#publish-the-required-dependency-on-curseforge).

## Layout

~~~text
build.py                              Standalone Python/JDK build
src/Vitja/TexturePackStarter/          Setup/shutdown registration and index reader
resources/manifest.json               Plugin manifest and runtime dependency
resources/Common/BlockTextures/       Three original diagnostic stone PNGs
resources/textures.list               Generated Common-relative paths
tools/index_textures.py               Build-time PNG index generator
docs/BEGINNER_DE.md                   Step-by-step beginner guide in German
docs/BEGINNER_EN.md                   Step-by-step beginner guide in English
docs/API.md                           Complete API v1 guide
docs/index.html                       Generated documentation website
docs/beginner-de.html                 Generated beginner website (German)
docs/beginner-en.html                 Generated beginner website (English)
tools/build_site.py                   Documentation renderer
~~~

## Verification boundary

The standalone build, final JAR contents and registration/selection/unregister
through Manager API v1 are checked against **Manager 0.3.1 / Hytale 0.7.7**.
The underlying stone override/restoration mechanism has representative native client
evidence. This Starter binary has not received a separate native gameplay acceptance
test; registration alone does not certify every visual consumer.
Read the API guide for dimensions, UVs, memory/loading costs, exclusions and reload limits.

## Maintain the documentation

Edit **docs/API.md**, **docs/BEGINNER_DE.md** or **docs/BEGINNER_EN.md**, then regenerate the site:

~~~sh
python3 -m pip install -r requirements-docs.txt
python3 tools/build_site.py
~~~

Only documentation generation needs this optional Python package.
Commit the Markdown and generated site together. GitHub Pages publishes the committed
**docs/** folder; each guide is maintained in its Markdown source, not edited in HTML.

## Permission and feedback

You may use and adapt the example to build and distribute compatible texture-pack
mods under the [example permission](LICENSE.md). The Manager remains proprietary;
neither it nor Hytale is licensed or bundled by this example.

Open a GitHub issue for example/build/API-guide problems. Include versions, the build
command and error. Use the [CurseForge project](https://www.curseforge.com/hytale/mods/texture-pack-manager)
for Manager gameplay feedback. Do not include credentials or private world data.
