package Vitja.TexturePackStarter;

import Vitja.TexturePackManager.api.TexturePackApi;
import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;

/** Minimal pack lifecycle; activation and ordering belong to the manager. */
public final class StarterPlugin extends JavaPlugin {
    private boolean registered;

    public StarterPlugin(JavaPluginInit init) {
        super(init);
    }

    @Override
    protected void setup() {
        TexturePackApi.get().register(StarterPack.create(), StarterPack.class);
        registered = true;
    }

    @Override
    protected void shutdown() {
        if (registered) {
            try {
                TexturePackApi.get().unregister(StarterPack.ID);
            } catch (IllegalStateException managerAlreadyStopped) {
                // The manager API is unavailable after its own shutdown.
            }
            registered = false;
        }
    }
}
