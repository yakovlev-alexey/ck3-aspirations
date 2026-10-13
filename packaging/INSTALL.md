# Install Aspirations manually

This archive contains the assembled native Aspirations prototype. It needs no source checkout, PowerShell, Git or development fixtures to load. The prototype targets CK3 1.20.0.4 (Crozier), single player and an adult landed ruler. English localization only.

1. Close CK3. Resolve Documents from the operating system rather than assuming a drive or unredirected folder. In PowerShell, run `[Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)` and select the existing `Paradox Interactive/Crusader Kings III` user-data directory beneath the returned folder. If your launcher uses another configured directory, select that actual directory instead.
2. Extract this archive into a temporary directory. Copy its `mod/` contents into `<CK3 user data>/mod/aspirations/`, preserving `descriptor.mod` directly inside `aspirations/` and native directories beside it. Do not add a second nested `mod/` directory.
3. Create `<CK3 user data>/mod/aspirations.mod` using the copied `descriptor.mod` metadata and add `path="<absolute path to the aspirations directory>"`, using forward slashes. This local path is not part of the portable archive. Never invent a Workshop item ID.
4. Use a disposable launcher playset and save. Enable Aspirations there separately; installation does not change the user's active playset. Load the test campaign and run the owning scenario procedures before using normal saves.

Subscribers to a future published Workshop item will receive assembled native files and require no PowerShell, Git or source checkout. Publication and subscribed-download acceptance have not occurred.

## Scope and troubleshooting

Aspirations adds contextual vengeance and holding recovery ambitions plus personal-bond desires for the current player. Maximum capacity is three ambitions and five desires. Use the native Situations list and Review my aspirations decision; existing game interactions and restrictions still apply. Keep a separate campaign for prototype play.

If it does not appear, inspect the local descriptor path and confirm `common/`, `events/`, `localization/` and `descriptor.mod` are directly inside the installed aspirations directory. English is the only included localization. Inspect fresh `<CK3 user data>/logs/error.log` and compare the loaded game version. Disable other mods when reproducing a conflict; RICE and multiplayer are not verified. The supported construction pool is narrow, and direct public murder exposure before the mod observes a known secret is unsupported.

To uninstall, first disable Aspirations in its disposable playset and close CK3. Remove only the folder and local descriptor you created above; preserve all saves and unrelated mods. A campaign containing active prototype Stories should not be continued with the mod removed.

The manual archive is a local deliverable. Workshop upload source is the assembled release mod root itself, with no enclosing `mod/` layer. No Workshop publication or subscribed-download acceptance has occurred. The public license remains undecided; select and document it before public distribution.
