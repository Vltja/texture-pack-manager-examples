package Vitja.TexturePackStarter;

import Vitja.TexturePackManager.api.TexturePack;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/** Example-local index reader. This helper is not part of the manager API. */
public final class StarterPack {
    public static final String ID = "vitja.starter.stone";

    private StarterPack() {}

    public static TexturePack create() {
        var input = StarterPack.class.getResourceAsStream("/textures.list");
        if (input == null) {
            throw new IllegalStateException("Missing textures.list; run the texture index generator before packaging");
        }
        try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
            var entries = reader.lines()
                .filter(line -> !line.isBlank() && !line.startsWith("#"))
                .map(path -> new TexturePack.Entry("textures", path, "/Common/" + path))
                .toList();
            return new TexturePack(ID, "Texture Pack Starter", "1.0.0", "Vitja", entries);
        } catch (IOException error) {
            throw new IllegalStateException("Cannot read texture index", error);
        }
    }
}
