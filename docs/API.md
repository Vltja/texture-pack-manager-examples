# Texture Pack Manager — Developer API Guide

**API v1 · Manager 0.3.1 · Hytale 0.7.7 · reviewed 2026-11-12**

A texture pack is a separate Hytale Java mod. It carries its replacement images in its own JAR, registers them with Texture Pack Manager, and lets the server administrator choose activation and priority. Keep the original Hytale `Common/...` directory layout. The manager reads the resources directly; server owners do not copy individual textures or merge packs by hand.

**Server-wide pack selection:** This Manager uses Hytale's server-authoritative asset workflow: the server administrator selects one enabled pack stack and priority order for the whole server. All players receive the same server-selected texture overrides. Separate personal texture-pack selections for individual players are currently not supported. The per-player UI language setting changes the menu language only.

This guide describes the current experimental implementation. The manifest declares the Hytale `0.7.x` range; actual runtime observations are from **0.7.7**. API v1 is the current contract name, not a guarantee of compatibility with every future manager release. Compile against the manager version you intend to support.

**First texture pack? / Erstes Texture Pack?** Start with the beginner guides: **[Deutsch – Schritt für Schritt](https://github.com/Vltja/texture-pack-manager-examples/blob/main/docs/BEGINNER_DE.md)** or **[English – step by step](https://github.com/Vltja/texture-pack-manager-examples/blob/main/docs/BEGINNER_EN.md)**. They cover editing the real Starter files, the two required JARs, building on Windows/Linux/macOS, testing on the server, common errors, and a copyable ChatGPT prompt that accepts your own GitHub URL. A public repository link helps ChatGPT read source files when web access is available, but does **not** itself grant PC access or permission to push changes; GitHub CI does not grant that access either.

## Contents

1. [What a pack can change](#1-what-a-pack-can-change)
2. [Quick start and demo mod](#2-quick-start-and-demo-mod)
3. [Use Hytale's directory layout](#3-use-hytales-directory-layout)
4. [Register a pack](#4-register-a-pack)
5. [Build and install](#5-build-and-install)
6. [Priority, fallback and activation](#6-priority-fallback-and-activation)
7. [Public API reference](#7-public-api-reference)
8. [Native visual definitions](#8-native-visual-definitions)
9. [Resolution, transparency and animation](#9-resolution-transparency-and-animation)
10. [Live reload, restoration and lifecycle](#10-live-reload-restoration-and-lifecycle)
11. [Troubleshooting](#11-troubleshooting)
12. [Pack author checklist](#12-pack-author-checklist)

## 1. What a pack can change

The normal API replaces **existing, registered Common PNGs by their exact path**. It does not add new content or infer which materials use a file. A single PNG can be shared by several consumers: replacing it affects all consumers that use that path.

| Visual content | Current API route | Evidence and limits on Hytale 0.7.7 |
|---|---|---|
| Block, terrain and prop textures | `TexturePack.Entry` | Selected stone, grass, dirt and workbench swaps and restoration observed live. Include each needed face/random variant. |
| Textures owned by other mods | `Entry` with that mod's exact Common-relative path | Aether Stone 0.6.10 quartz ore and lamp model textures changed live through a separate registration-only patch; source mod unchanged. Other mod consumers need their own checks. |
| Item and equipment textures | `Entry` | Original-dimensional iron hatchet observed. A scaled tool fixture was rejected by the client. |
| Armor textures | `Entry` | Original 64×64 iron chest texture observed on an NPC wearing the native equipped item; live swap and restoration. Other pieces and player third-person views remain unqualified. |
| Non-cosmetic NPC textures | `Entry` | Cow texture changed and restored live. Other NPCs require their own material/UV checks. |
| Water and lava textures | `Entry` | Both sources and naturally spread flow levels 1..7 changed and restored live in a controlled test. This does not replace fluid simulation or its shader. |
| Particle sprites and weather precipitation PNGs | `Entry`; optional native definitions | Sun-shaft particle appearance and rain impact sprites changed. Alpha correctness, all emitters and animation behavior are not fully qualified. |
| Beams and trails | `Entry`; `Beam`/`Trail` definitions | Basic beam PNG and native texture-path changes/restoration observed. Trail rendering has not been verified. |
| Sky and weather appearance | `Weather` definition; referenced PNGs via `Entry` | Sky/fog color changes/restoration observed. Moon/cloud/star texture replacement and a generic skybox/cubemap API are unqualified. |
| Other existing Common PNGs, including some icons/UI images | `Entry` | Eligible by file format and path if registered; no general UI/font/material compatibility guarantee. Native `.ui` and XAML files are not accepted. |
| Original character clothing, hair and official cosmetics | Excluded | Direct protected cosmetic PNG targets are rejected. Armor is a separate supported scope. |
| Models and skeletal animation files | Not exposed | `.blockymodel` and `.blockyanim` replacement is not implemented. `ModelAsset` JSON is a reference/configuration adapter, not a model-file loader. |
| Custom shader programs, general lighting engine, camera/ModelVFX stores | Not exposed as dedicated APIs | An image of a light ray changes its visible sprite; it does not establish control over actual light propagation or arbitrary shaders. |
| Sounds and other audio | Excluded | No audio file or audio-store interface. |

Registration success means the pack passed server-side resource checks. It does **not** certify that every consumer rendered the replacement. Current native JSON adapters are experimental; see section 8 before using them.

## 2. Quick start and demo mod

**Texture Pack Starter 1.0.0** is the small registration-only example for Manager 0.3.1. Get the complete source and standalone build from the [public example repository](https://github.com/Vltja/texture-pack-manager-examples), or download its [source ZIP](https://github.com/Vltja/texture-pack-manager-examples/archive/refs/tags/v1.0.0.zip) and [compiled demo JAR](https://github.com/Vltja/texture-pack-manager-examples/releases/download/v1.0.0/texture-pack-starter-1.0.0.jar). The Manager is a separate dependency. The complete manual-entry plugin in section 4 is an alternative starting point. It contains three original diagnostic stone PNGs at the native paths, one pack registration and no gameplay content or test commands. Its manifest identity is `Vitja:TexturePackStarter`; its manager pack ID is `vitja.starter.stone`. Those are different identifiers.

The starter follows this workflow:

1. Put replacement PNGs under `resources/Common/` using the original relative paths.
2. Generate `resources/textures.list` from those PNG paths during the build.
3. Register one `TexturePack` in the plugin's `setup()` method.
4. Install the starter JAR together with the manager JAR.
5. Open `/texturepacks`, enable the pack, choose its place with **Up / Down**, then **Apply / Reload**.

```text
Texture Pack Starter/
├── src/Vitja/TexturePackStarter/
│   ├── StarterPlugin.java
│   └── StarterPack.java
├── resources/
│   ├── manifest.json
│   ├── textures.list
│   └── Common/BlockTextures/
│       ├── Rock_Stone.png
│       ├── Rock_Stone_2.png
│       └── Rock_Stone_3.png
└── tools/index_textures.py
```

The larger **Texture Pack Demo 0.3.2** and **Texture Pack Conflict 0.2.2** are advanced local fixtures for visual probes and priority tests. Their local fixture commands, including `/tpmscene` and `/tpmvis` in Demo, are not part of the public manager API. The Demo world-editing probes depend on a specific local world. Start with the starter rather than copying those test commands to another server.

The starter's final JAR is compile- and registration-checked. This new starter artifact has not itself received a native gameplay test; the underlying stone target mechanism has earlier representative client evidence. The standalone source build is verified on Linux with JDK 25 and Python; Windows/macOS use the same portable workflow but have not received separate native acceptance tests. The example includes diagnostic artwork; replace it with your own PNGs for your real pack.

## 3. Use Hytale's directory layout

For an original file `Common/BlockTextures/Rock_Stone.png`, package your replacement at exactly the same location inside your JAR:

| Meaning | Value |
|---|---|
| Source project resource | `resources/Common/BlockTextures/Rock_Stone.png` |
| Final JAR entry | `Common/BlockTextures/Rock_Stone.png` |
| API target | `BlockTextures/Rock_Stone.png` |
| Absolute JAR resource | `/Common/BlockTextures/Rock_Stone.png` |

`Common/` is retained in your resource folders and omitted only from the API **target**. Use forward slashes and exact spelling/capitalization. `resources/` is a project source directory, not part of the JAR path. Maven/Gradle projects may use `src/main/resources/Common/...` with the same final JAR entries.

The API permits a resource at another private JAR location, but mirroring `Common/...` avoids unnecessary remapping. No manager-specific texture directory is required.

Find paths and references in the assets of the Hytale version you support. A block may refer to several face/random variants, an item may have separate held-model and icon PNGs, and a material may apply a tint or greyscale mask. A display name such as “Stone” is not an API target. Only ship the replacement resources you need.

### Patch textures owned by another mod

Vanilla and mod-provided PNGs use the same native Common asset registry. A patch targets the **exact registered path**, regardless of which mod originally supplied it. There is no special vanilla-only directory restriction. For example, an Aether Stone patch keeps this layout:

```text
Common/Blocks/VMCAether/Minerals/QuartzOre.png
Common/Blocks/VMCAether/Lamp_Off.png
Common/Icons/Items/VMCAether/QuartzOre.png
```

The corresponding API targets omit only `Common/`, for example `Blocks/VMCAether/Lamp_Off.png`. Declare required dependencies on both the manager and the content mod:

```json
"Dependencies": {
  "Vitja:TexturePackManager": "*",
  "Vitja:MCRedstone": "*"
},
"IncludesAssetPack": false
```

This fragment belongs inside the complete manifest from section 4. Aether Stone's current technical identity is `Vitja:MCRedstone`; its display name is not the dependency key. The diagnostic **Texture Pack Aether Patch 1.0.0** registers three PNG entries through the same public API. It adds no items, commands, listeners, scheduled work or threads and changes no Aether Stone code or native definitions.

A modpack can therefore install a base texture pack plus separate style patches for selected content mods. Enable the wanted packs, put any patch above another pack that supplies the **same path**, then Apply. Other paths keep their lower-pack replacement or captured original. “Original” for a mod-owned path means that content mod's previously active texture.

The source mod must be installed and its target registered before Apply. A required dependency establishes ordinary load ordering; a mod that generates/changes paths later at runtime needs additional coordination. Target version/variant changes, random generated names and a source mod that keeps rewriting the same asset are not automatically resolved. State which content-mod versions your patch was checked against. The PNG API replaces existing files; it does not invent missing assets or modify gameplay behavior.

### Automatic index in the starter

The manager does **not** scan your JAR automatically. The starter's build helper finds all `.png` files under `resources/Common/` and writes a UTF-8, newline-separated list without the `Common/` prefix:

```text
BlockTextures/Rock_Stone.png
BlockTextures/Rock_Stone_2.png
BlockTextures/Rock_Stone_3.png
```

`StarterPack.create()` reads this list and creates one entry per line:

```java
new TexturePack.Entry("textures", path, "/Common/" + path)
```

`textures.list`, the index generator and `StarterPack` are **example-local helpers**, not extra manager API methods or a required file format. Generate the index on every build so newly added or removed PNGs are reflected. You can instead construct the entries directly, as below. Native JSON definitions always need an explicit `(store, id, resource)` mapping.

## 4. Register a pack

### Required manifest

This is the starter's actual root `manifest.json`:

```json
{
  "Group": "Vitja",
  "Name": "TexturePackStarter",
  "Version": "1.0.0",
  "Description": "Minimal Common-path texture pack registration example.",
  "Authors": [{"Name": "Vitja"}],
  "Main": "Vitja.TexturePackStarter.StarterPlugin",
  "ServerVersion": ">=0.7.0 <0.8.0",
  "Dependencies": {"Vitja:TexturePackManager": "*"},
  "IncludesAssetPack": false
}
```

For your own mod, replace the example's group/name, author, main class and version with your identity. Keep the manager dependency required. `"*"` declares that the manager must be present; it is not evidence of compatibility with every manager version.

**Set `IncludesAssetPack` to `false` for a manager-controlled pack.** Your `Common/` resources are read by the manager after registration. Enabling ordinary native asset-pack loading as well can apply the same resources independently of the manager and defeat disabled state, priority and captured-baseline expectations. Do not separately load the replacement files through another asset-pack registration mechanism.

### Complete minimal registration without helpers

This alternative is self-contained and uses the three PNGs above. It has the same main class and pack ID as the starter: choose either this version or the starter's index-based version, not both.

```java
package Vitja.TexturePackStarter;

import Vitja.TexturePackManager.api.TexturePack;
import Vitja.TexturePackManager.api.TexturePackApi;
import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;
import java.util.List;

public final class StarterPlugin extends JavaPlugin {
    private static final String PACK_ID = "vitja.starter.stone";
    private boolean registered;

    public StarterPlugin(JavaPluginInit init) { super(init); }

    @Override protected void setup() {
        TexturePack pack = new TexturePack(
            PACK_ID, "Texture Pack Starter", "1.0.0", "Vitja",
            List.of(
                new TexturePack.Entry("blocks", "BlockTextures/Rock_Stone.png",
                                      "/Common/BlockTextures/Rock_Stone.png"),
                new TexturePack.Entry("blocks", "BlockTextures/Rock_Stone_2.png",
                                      "/Common/BlockTextures/Rock_Stone_2.png"),
                new TexturePack.Entry("blocks", "BlockTextures/Rock_Stone_3.png",
                                      "/Common/BlockTextures/Rock_Stone_3.png")
            )
        );
        TexturePackApi.get().register(pack, StarterPlugin.class);
        registered = true;
    }

    @Override protected void shutdown() {
        if (registered) {
            try { TexturePackApi.get().unregister(PACK_ID); }
            catch (IllegalStateException managerAlreadyStopped) { }
            registered = false;
        }
    }
}
```

The index-based starter's setup reduces this to:

```java
TexturePackApi.get().register(StarterPack.create(), StarterPack.class);
```

Use a resource-owner class **from your own pack JAR**. The manager uses `resourceOwner.getResourceAsStream(...)`; using a manager class as the owner will look in the wrong JAR. The dependency orders normal plugin setup; do not call `get()` from a static initializer or before the manager is ready.

One plugin may register several independent packs with unique IDs, each becoming a separate manager row. There is no partial-registration rollback across several calls: if you register several packs, track successful registrations and unregister them if a later setup step fails.

## 5. Build and install

Use a JDK compatible with the target server; this project compiles with **JDK 25**. Add the current Hytale server JAR and **Texture Pack Manager 0.3.1 JAR** to your compile classpath. Treat both as provided dependencies: do not shade, copy or embed Hytale classes or `Vitja/TexturePackManager/**` in the pack JAR. There is no published Maven coordinate for this Manager release.

The [public Starter README](https://github.com/Vltja/texture-pack-manager-examples#build-from-source) explains the standalone `build.py` workflow for Linux/macOS and Windows. It needs only Python 3.9+, JDK 25+ and your two local dependency JARs; no private project or sibling build script. The build regenerates the PNG index and produces `build/texture-pack-starter-1.0.0.jar`. The complete manual-entry plugin in section 4 needs neither `StarterPack.java` nor an index generator.

For your own project using the complete manifest and manual-entry `StarterPlugin.java` from section 4, equivalent POSIX-shell commands are:

```sh
# Set these to the two JARs on your development machine.
export HYTALE_SERVER_JAR='/absolute/path/to/HytaleServer.jar'
export TEXTURE_PACK_MANAGER_JAR='/absolute/path/to/texture-pack-manager-0.3.1.jar'

# Optional index-based variant only: run your own PNG index generator here.
# The complete manual-entry plugin does not need textures.list.
mkdir -p build/classes
javac --release 25 \
  -cp "$HYTALE_SERVER_JAR:$TEXTURE_PACK_MANAGER_JAR" \
  -d build/classes src/Vitja/TexturePackStarter/*.java
jar --create --file build/texture-pack-starter-1.0.0.jar \
  -C build/classes . -C resources .
```

Use a clean class-output directory when removing or renaming classes. On Windows the Java classpath separator is `;`; use your build system's provided/compile-only dependency support or adapt the commands for your shell. No SDK classes should enter the final archive.

Install the manager and pack JARs in the server's `mods/` directory, with only one version of each manifest identity. Restart the server to load/update a pack mod. The server supplies managed assets to clients; this is not a client-side Java-mod installation workflow. The new pack appears disabled unless saved settings already exist for its stable pack ID. Grant `vitja.texturepacks.admin`, then enable and apply it.

### Publish the required dependency on CurseForge

Pack authors must declare the manager in **both** places:

| Location | Required setting | Purpose |
|---|---|---|
| Pack JAR `manifest.json` | `"Dependencies": {"Vitja:TexturePackManager": "*"}` | Require the manager at runtime and establish normal plugin load ordering. Use a tested version constraint when preparing the actual release. |
| Pack's release file on CurseForge | Relation to the actual **Texture Pack Manager** project, type **Required Dependency** | Tell dependency-aware installers that the manager must be installed with the pack. This is separate from the JAR manifest. |

After the manager has a public CurseForge project and a compatible downloadable file:

1. Upload your pack to its own Hytale mod project, then edit the release file's dependency/relations metadata in the author dashboard.
2. Select the real **Texture Pack Manager** project and set **Required Dependency**. Check the project's identity and URL; use the published numeric CurseForge project ID when a publishing tool asks for it. `Vitja:TexturePackManager` is the Hytale identity, not a CurseForge project ID.
3. For a mod-specific patch, also mark the target content mod as a required CurseForge dependency, matching the additional manifest dependency. The Aether example therefore requires the Manager **and Aether Stone**.
4. Save and reopen the file's Relations/dependency view. Confirm that the actual file being distributed lists the required projects; check every new pack release/update. Do not use Optional Dependency or Embedded Library for the separately installed manager, and do not bundle the manager/API inside the pack JAR.
5. From a clean test installation/profile without the manager, install the pack through the intended supported client and verify that its dependency flow obtains a compatible manager. For a patch, check the content mod too. Then verify that the loaded pack appears in `/texturepacks`. Record the installer/version and result before advertising automatic installation.

Required-dependency metadata allows a dependency-aware installer to resolve the manager. **Automatic installation depends on the client**, and has not yet been end-to-end tested with a published compatible pack and this Manager release. A plain browser download only obtains the chosen file; server owners/manual installers must also obtain the required manager and any target mod. This publishing dependency flow is separate from joining an already configured server, which synchronizes native assets as described below.

**Manager project:** [Texture Pack Manager on CurseForge](https://www.curseforge.com/hytale/mods/texture-pack-manager), numeric project ID **1799221**. This is distinct from the Hytale runtime identity `Vitja:TexturePackManager`. The project was created for the first 0.3.1 Release submission on 2026-11-11; visibility and downloadable files remain subject to moderation. The Starter source and demo download are on GitHub, separate from the Manager download. The Aether Patch remains a local diagnostic example. Configure and verify Required Dependency relations when releasing your actual pack, then perform the clean-install check; no automatic-install success is claimed here.

Reference: CurseForge models dependencies on individual files with a project `modId` and `relationType`; `RequiredDependency` has value 3 in its [official API schema](https://docs.curseforge.com/rest-api/). Its [Hytale installation guide](https://support.curseforge.com/support/solutions/articles/9000273615-install-hytale-mods/) distinguishes supported app installation from manual file installation. Sources checked 2026-11-11; recheck the dashboard and installer behavior at publication.

### Lightweight pack behavior and real costs

Keep a pack plugin to registration during setup and unregister during shutdown. Texture data and an optional generated index are sufficient; pack authors need no tick systems, polling, custom networking, per-player listeners or background executors. The Starter and Aether Patch follow this pattern. The manager handles activation, ordering and asset submission centrally.

“Lightweight” does not mean zero memory or loading cost. In Manager **0.3.1**, registration reads, validates and decodes every installed pack's PNGs once, then retains their **encoded PNG bytes even while disabled**, plus metadata and plugin/class-loader overhead. Unregister releases the registered pack data, but applied/baseline/native caches can still retain assets. There is no lazy-only-active-pack loading policy yet. Many large packs can therefore increase startup work and server RAM; the 64 MiB PNG cap is **per pack**, not a global budget. PNG decoding also creates temporary image memory. No universal safe pack count is established.

There is no per-pack ongoing simulation/tick loop in the reference pack plugins. Selection/UI/Apply still perform work when used, and enabled high-resolution textures can increase client download/cache size, GPU memory, rebuild time and rendering cost. The manager's worker acts on submissions rather than continuously applying every installed pack.

### What players receive when joining

For these server-side Java mods, clients receive native **asset data**, not the pack's Java JAR or its code. With `IncludesAssetPack: false`, a registered but disabled pack's private resource bytes are not automatically loaded into Hytale's Common asset registry. Apply publishes the winning selected replacements under the existing paths; the native required-asset list reflects the effective asset/hash at each path, together with the server's other normal assets.

Clients request assets they need according to their cache. Installing many disabled manager packs therefore does **not** imply downloading every PNG alternative on every join. Switching a pack while connected submits the changed assets through the manager's live batch. Previously received data can remain cached; disabling is not a promise to erase the client's cache. A content mod's normally registered assets and packs also loaded independently through the native asset-pack system follow their own loading behavior.

The bounded Aether test checked a never-enabled sentinel resource: it was registered as pack metadata/data but absent from the native registry and required-asset list, and was not observed among requested/sent assets. This is scoped evidence, not a full bandwidth or concurrent-multiplayer benchmark.

## 6. Priority, fallback and activation

The **topmost enabled pack that contains a target wins that target**. Lower enabled packs fill missing targets. When none supplies a target, its captured baseline stays active or is restored. Resolution happens per PNG path, not per category, author or complete pack.

| Target | Upper pack: grass only | Lower pack: grass, dirt, stone | Result |
|---|---|---|---|
| Grass | Has replacement A | Has replacement B | Upper pack A |
| Dirt | Absent | Has replacement | Lower pack |
| Stone | Absent | Has replacement | Lower pack |
| Sand | Absent | Absent | Baseline/original |

Move the lower pack above the other one and its grass wins too. A fully transparent PNG still counts as a replacement; it does not mean “fall through.” A disabled pack never supplies a winner. The API does not allow pack authors to force activation or reserve priority.

Native JSON definitions use the same ordering, but their conflict key is the entire **store + asset ID**. Two definitions of `Weather / Zone1_Sunny` do not merge individual fields. A PNG and a definition are separate targets, so an upper PNG can coexist with a lower definition; authors should consider whether that combination makes visual sense.

| Administrator action | Effect |
|---|---|
| `/texturepacks` | Open the native administrator UI. |
| Enable/Disable, Up/Down | Save desired activation/order; do not change rendering until Apply. |
| **Apply / Reload** or `/tpm apply` | Resolve and submit the selected replacements/restorations. |
| **Disable all (then Apply)** | Disable registered packs in desired settings; press Apply afterwards. |
| `/tpm` | List registered pack IDs, enabled states and priorities. |
| `/tpm enable <id>` / `/tpm disable <id>` | Save a pack's desired state. |
| `/tpm raise <id>` / `/tpm lower <id>` | Move one visible row; run Apply afterwards. |
| `/tpm reset` | Disable registered packs and apply baseline restoration. |

All manager commands and UI actions require **`vitja.texturepacks.admin`**. Use the game's permission system to grant it; pack mods should not grant permissions themselves. The UI offers **Auto / Deutsch / English** per player.

The visible order and resolver match: descending numeric priority, then descending lexicographic pack ID for legacy ties. Up/Down normalizes the persisted order, so administrators need not manage numeric gaps or ties. UI “winning assets” counts describe the desired selection, not client-render acknowledgement.

Settings persist as `packs.properties` in the manager's native plugin data directory (`mods/Vitja_TexturePackManager/` in the inspected setup). Keep pack IDs stable across updates. Name, author and version are display metadata; changing them does not migrate an ID. Do not edit the settings file while the manager is running. Saved settings are applied after registrations at normal server boot.

## 7. Public API reference

The supported pack-author surface is in **`Vitja.TexturePackManager.api`**. Use the records and interface below; `PackService`, `ManagerPlugin`, `OverlayResolver`, the admin page and native packet code are manager internals.

### `TexturePackApi`

```java
static TexturePackApi get();
void register(TexturePack pack, Class<?> resourceOwner);
void unregister(String id);
```

| Member | Contract |
|---|---|
| `get()` | Obtain the running manager's API. Throws `IllegalStateException` if the manager is not ready/already stopped. |
| `register(pack, resourceOwner)` | Synchronously read and validate resources from the owner's JAR, then publish the pack to the available list. Does not activate or Apply it. Register once during setup. An already registered ID is rejected; this is not an update/upsert method. |
| `unregister(id)` | Remove the pack from future resolution. An unknown ID is a no-op. Desired settings are retained. Existing applied assets require another administrator Apply to resolve/restore. Normally call during plugin shutdown. |

Do not cache the API across manager shutdown/restart. There is no public method for Apply, enabled-state changes, priority control, runtime file discovery, client acknowledgement, winner queries or completion callbacks. Use administrator controls for those actions. Pack resources are read into memory on registration, so editing an already installed JAR does not refresh a registered pack; rebuild and restart normally.

### `TexturePack`

```java
new TexturePack(String id, String name, String version, String author,
                List<TexturePack.Entry> entries);
new TexturePack(String id, String name, String version, String author,
                List<TexturePack.Entry> entries,
                List<TexturePack.Definition> definitions);
```

| Field/accessor | Rules |
|---|---|
| `id()` | Unique across all registered packs. Regex `[a-z0-9][a-z0-9._-]{0,95}`: 1–96 characters. Prefer your own namespace, e.g. `yourname.packname`. Stable configuration key, unrelated to the Hytale manifest ID. |
| `name()` | Non-null display name. |
| `version()` | Non-null display version. Not parsed as a manager dependency constraint. |
| `author()` | Non-null display author. |
| `entries()` | Non-null, immutable copied list of PNG overrides. |
| `definitions()` | Non-null, immutable copied list of native JSON overrides. The five-argument constructor uses an empty list. |

At least one entry or definition is required. A definition-only pack is allowed. Null list elements are rejected by the immutable list copy. Record accessors, value equality, hash code and `toString()` follow Java record semantics; mutating the source list later does not change a registered pack.

### `TexturePack.Entry`

```java
new TexturePack.Entry(String category, String target, String resource);
```

| Field/accessor | Rules |
|---|---|
| `category()` | Non-null descriptive label such as `blocks` or `textures`. Not a store selector, validator, separate toggle or priority boundary. No fixed category enumeration. |
| `target()` | Exact Common-relative path ending in lowercase `.png`, without leading `/`, backslashes or `..`. Use the canonical path without `Common/`. The target must already be registered when Apply captures the baseline. Original protected cosmetics are rejected. |
| `resource()` | Absolute classpath/JAR resource beginning with `/`, without `..`. Must exist in the owner JAR and contain valid PNG data. Recommended: `/Common/` plus `target`. |

Duplicate target paths within one pack are rejected on registration; overlaps between different packs are expected and resolved by priority. Path existence is checked at Apply, after normal asset loading; PNG resource availability/bytes are checked at registration.

### `TexturePack.Definition`

```java
new TexturePack.Definition(String store, String id, String resource);
```

| Field/accessor | Rules |
|---|---|
| `store()` | Exact, case-sensitive allowlisted native store name from section 8. |
| `id()` | Existing native asset ID, regex `[A-Za-z0-9_]+`. Not a path or localized display name. |
| `resource()` | Absolute JAR resource beginning with `/`, ending in lowercase `.json`, without `..`. UTF-8 JSON document. |

Duplicate `(store, id)` definitions within one pack are rejected. JSON syntax/size is checked on registration. Native store availability, original ID, codec decoding, references and actual rendering are later concerns; registration alone does not validate them all.

### `ProtectedCosmetics`

`ProtectedCosmetics.contains(String path)` is a public, version-scoped helper returning whether an exact Common-relative path belongs to the manager's direct cosmetic exclusion. Pass a non-null path. In 0.3.1 it covers `Cosmetics/`, `Characters/Haircuts/` and 241 exact creator-catalog PNG references from the inspected installation. `Entry` invokes it automatically. Do not treat the list as a permanent inventory, a claim about every engine restriction, or a sandbox for native definitions.

### Limits and errors

| Check | Current limit/behavior |
|---|---|
| One PNG resource | At most **16 MiB** encoded bytes; valid PNG signature and decodable image. |
| PNG bytes in one pack | At most **64 MiB** total. Native JSON bytes are not included in this particular cap. |
| PNG dimensions | Each axis 1–4096 pixels, at most **16,777,216 pixels**. Accepted dimensions do not establish consumer compatibility. |
| One JSON definition | At most **1 MiB** UTF-8 resource bytes, syntactically a JSON document. |
| Number of packs/definitions | No public aggregate budget. Operators must budget total memory and rebuild work. |

Invalid IDs, paths, excluded targets, duplicate registrations/targets, missing resources, size or format failures generally produce `IllegalArgumentException`; null required fields/lists may produce `NullPointerException`. Do not parse exception text as a stable machine-readable protocol. Constructor validation precedes registration; registration precedes native Apply validation. Fix and report a failed setup rather than silently registering an incomplete pack.

## 8. Native visual definitions

Use PNG entries when the desired change is only an existing texture's pixels. Use a definition when you need a native visual field such as a weather color, a beam texture reference or a particle frame layout. A definition is a **whole native asset replacement**, not a JSON patch, field merge or new asset registration.

| Store | Intended visual use | Current scope |
|---|---|---|
| `Beam` | Beam appearance and referenced texture | Selected `Basic` texture-path change/restoration observed. |
| `Trail` | Trail appearance/reference | Adapter allowlisted; rendering unverified. |
| `Weather` | Native weather sky/fog/colors and related references | Selected `Zone1_Sunny` color change/restoration observed; does not automatically force the world to use that weather. |
| `ParticleSpawner` | Sprite/frame/emitter metadata | Selected sun-shaft appearance observed after re-emission. Broad emitter/animation behavior unqualified. |
| `ParticleSystem` | Particle system references/configuration | Adapter allowlisted; broad runtime behavior unverified. |
| `Fluid` | Existing fluid visual references | Experimental full-definition adapter; fluid PNG tests did not exercise definition changes. Gameplay properties must remain unchanged. |
| `FluidFX` | Fluid visual effect configuration | Adapter allowlisted; broad runtime behavior unverified. |
| `ModelAsset` | Existing model asset visual references | Does not expose binary model/animation-file replacement. Broad runtime behavior unverified. |
| `BlockType` | Existing block visual configuration | Full native definition can affect gameplay. No visual-field-only patch interface. |
| `Item` | Existing item visual configuration | Full native definition can affect gameplay. No visual-field-only patch interface. |

These are the complete store names accepted by 0.3.1. Environment, ModelVFX, camera, camera-shake and other stores are not added merely because they contain visual fields.

Preserve native directory conventions for clarity. For example, package a complete compatible `Zone1_Sunny` weather JSON at `Server/Weathers/Zone1/Zone1_Sunny.json`, then explicitly register:

```java
TexturePack weatherPack = new TexturePack(
    "yourname.weather", "Weather Colors", "1.0.0", "Your Name",
    List.of(),
    List.of(new TexturePack.Definition(
        "Weather", "Zone1_Sunny", "/Server/Weathers/Zone1/Zone1_Sunny.json"
    ))
);
TexturePackApi.get().register(weatherPack, YourPlugin.class);
```

Here `YourPlugin` is your own plugin class; `List` and the API records require the imports shown in section 4. The resource must contain the **complete native definition compatible with the installed server**, with unrelated properties preserved. A snippet containing only a changed color is not a manager patch. This guide does not supply Hytale's original definition files.

Some native sources have specialized extensions such as `.particlespawner`. The current definition resource API requires `.json` inside your JAR: preserve the source's logical directory and native ID, save the compatible JSON document as a `.json` resource, and explicitly select its store. This is a definition-adapter requirement; PNG structure remains unchanged.

The store and ID must exist before Apply. Native decoding/re-registration happens on the manager worker. A bad definition can fail Apply; test decoding, rendering and restoration against the exact game version. Editing an effect's definition does not guarantee that an already-running effect instance will recreate itself; re-emission or another native trigger may be required.

**Visual-only is the intended pack scope, not an enforced field sandbox in 0.3.1.** Full Item/BlockType/Fluid/Model definitions may also contain gameplay or sound-related fields. Preserve those properties, do not use this adapter to alter audio/gameplay/original cosmetics, and review full definitions before enabling a third-party pack. There is no implemented visual-field allowlist or merge layer yet.

References in definitions should point to assets already registered by Hytale or another required mod, or to existing PNG paths being overridden. The PNG API cannot introduce arbitrary fresh dependency paths. Dependencies on another mod's targets need that mod's own manifest dependency as well as the manager dependency.

## 9. Resolution, transparency and animation

**Start with the original dimensions and layout.** The manager validates image limits but does not rewrite UVs, atlas frames, masks, shader inputs, tint behavior or alpha modes. A larger file is not automatically a valid higher-resolution material for every consumer.

A close-up stone experiment showed finer visible detail with a 256×256 replacement than with a real 32×32 control. That is evidence beyond a 32-pixel representation for that target, not GPU readback, a universal resolution limit or a guarantee for tools/armor/UI. An upscaled iron-tool fixture was rejected by the client; its original-dimensional counterpart worked.

Keep alpha where the native material expects it. Transparency in a PNG does not change opaque/blended material settings or prove correct depth/sort behavior. Native grass/other tints can change the perceived color of a diagnostic image.

There is no standalone GIF/video/animation-file API. A native sprite atlas may use PNG plus existing or explicitly registered `ParticleSpawner` frame metadata. Preserve the target's frame grid, dimensions and playback assumptions, then test the actual emitter. A filename or successful JSON load alone is not proof of animated rendering. `.blockyanim` is not accepted by `Entry`.

## 10. Live reload, restoration and lifecycle

Registration supplies pack data; **Apply** resolves desired state and submits changes. The manager batches PNG updates and requests one native Common-assets rebuild per non-empty PNG batch. Native definitions are reloaded through their stores. Selected block, equipment, NPC, fluid and effect consumers updated live in representative tests.

There is no client-render completion acknowledgement. A “Submitted …” status means the server submitted work, not that every client finished or accepted the pixels. Inspect the actual consumer and client logs. Re-emitting an effect or rejoining may be necessary for consumers that retain old state. Rejoining is a diagnostic/fallback, not a promise that an invalid material will become valid.

Only one Apply runs at a time. Submissions are separated by a five-second minimum; existing joining sessions can delay Apply for up to 120 seconds. New connections during Apply are refused with a retry message. These guards are not complete concurrent-multiplayer qualification or an application-level readiness signal for pack authors.

For each affected target, the manager captures the bytes/native object active **when first touched**, before mutation. This is the restoration baseline. With only Hytale originals loaded, that is the vanilla appearance. If another mod already replaced the target, the captured baseline can contain that mod's appearance. The manager arbitrates conflicts **among packs registered through it**; unrelated direct asset writers/editors are not globally coordinated. Avoid concurrent writes to the same target from another mechanism.

Apply captures required originals before mutations. Failure attempts rollback and reports that the client state needs inspection. This is not a transaction across every client renderer. Original assets must exist; arbitrary new target creation/removal is not the API's purpose. Content-hashed image blobs and baseline overlays can remain in the manager data directory; do not delete them while the server is running.

On shutdown, unregister your own pack IDs. At runtime that changes future selection; a later Apply is needed to remove already applied overlays. A normal server restart reloads base assets and applies saved desired settings after registration. Hot-unloading the manager with active packs and relying on shutdown for synchronized client restoration is not supported. For removal/update, use a normal stopped-server JAR replacement, preserve manager settings, and restart.

## 11. Troubleshooting

| Symptom/message | Check and next action |
|---|---|
| `Texture Pack Manager is not ready` | Install the required dependency; register during setup; avoid early static API access and stale API references. |
| `NoClassDefFoundError` / class cast problems | Compile against the intended manager; declare the manifest dependency; remove shaded/copied manager API and Hytale classes. |
| Pack absent from UI | Read plugin setup logs; check root manifest/main class, required dependency and registration errors. A JAR with PNGs alone does not register itself. |
| `Pack ID already registered` | Give independent packs unique IDs; keep the same ID only for updates of that pack, with one installed version. |
| `Missing JAR resource` / missing index | Inspect the final JAR, not only the source folders. Check exact case, leading `/` on API resources, correct owner class, and generated `textures.list`. |
| `Target is not registered` | Use an existing exact Common-relative path without `Common/`; check game version, variants and dependencies on other mods. |
| Original cosmetic target rejected | Remove it. Official character clothing/hair/cosmetics are outside this pack format's intended scope; armor uses separate targets. |
| No visible change after enabling | Press Apply; inspect which enabled pack wins this exact path; check the real consumer/variant, native tint, texture dimensions and client warnings. |
| Only some faces/variants change | Add the other actual referenced PNG paths. An item icon and held/placed model may use different files. |
| Scaled texture distorted/rejected | Restore original dimensions/layout first. Review material/UV/frame constraints before increasing resolution. |
| JSON registers but Apply fails | Check allowed exact store name, existing asset ID, complete compatible native definition and references; syntactic JSON validation does not run the native codec. |
| `Native store unavailable or ambiguous` | The installed game/mod registry must expose exactly one native store with that class simple name. Do not assume all allowlisted names exist in every version. |
| `Apply already running` / players still joining | Let the current operation/setup finish, then retry. Do not run concurrent asset edits to force it through. |
| Reset does not look vanilla | Baseline may include a prior direct mod override; inspect other asset packs/writers and their normal load order. |
| Updated PNG on disk does nothing | Resources were captured during registration. Rebuild the JAR, replace it while stopped, and restart; use the same stable pack ID. |

For bug reports, include manager/pack/Hytale versions, pack ID, exact target/store+ID, original/replacement dimensions, active order, reproduction steps, client/server error excerpts and whether restoration/rejoin changed the result. Report feedback through comments or a private message on [Vitja's CurseForge profile](https://www.curseforge.com/members/ivitjai). Do not include login tokens or private world data.

## 12. Pack author checklist

- Use your own mod identity and a stable, unique pack ID.
- Keep Hytale's `Common/...` structure and exact case; include only the replacements you intend.
- Declare the manager dependency, set `IncludesAssetPack: false`, and bundle no manager/SDK classes.
- On each CurseForge pack release file, add the Manager as **Required Dependency**; add required target mods for patches. Verify the saved relations and the intended installer's clean-install behavior.
- Register from setup using a class in your own JAR; unregister your IDs on shutdown.
- Regenerate an optional PNG index on every build; explicitly register any native JSON definitions.
- Respect PNG/JSON limits, native material/UV/frame requirements and cosmetic/audio exclusions.
- Test enabled/disabled state, another pack above/below, an uncovered original, and restoration on the actual consumers.
- Describe exact tested versions and limits. Do not label all assets supported from a successful registration or build.

Read this guide on the [documentation website](https://vltja.github.io/texture-pack-manager-examples/) or in the [example repository](https://github.com/Vltja/texture-pack-manager-examples). The Starter is a separate download and is not bundled with the Manager. The repository includes explicit permission to reuse its example materials for compatible texture-pack mods. This does not change the proprietary status of the Manager implementation or grant redistribution rights to Hytale or other third-party assets.
