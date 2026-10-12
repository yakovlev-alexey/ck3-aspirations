# Install Aspirations manually

The current bootstrap archive contains a descriptor only and is not playable. Use these steps when runtime modules have been implemented and verified. The prototype targets CK3 1.20.0.4 (Crozier), single player and an adult landed ruler. English localization only.

1. Close CK3. Resolve Documents from the operating system rather than assuming a drive or unredirected folder. In PowerShell, run `[Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)` and select the existing `Paradox Interactive/Crusader Kings III` user-data directory beneath the returned folder. If your launcher uses another configured directory, select that actual directory instead.
2. Extract this archive into a temporary directory. Copy its `mod/` contents into `<CK3 user data>/mod/aspirations/`, preserving `descriptor.mod` directly inside `aspirations/` and native directories beside it. Do not add a second nested `mod/` directory.
3. Create `<CK3 user data>/mod/aspirations.mod` using the copied `descriptor.mod` metadata and add `path="<absolute path to the aspirations directory>"`, using forward slashes. This local path is not part of the portable archive. Never invent a Workshop item ID.
4. Use a disposable launcher playset and save. Enable Aspirations there separately; installation does not change the user's active playset. Load the test campaign and run the owning scenario procedures before using normal saves.

Subscribers to a future published Workshop item will receive assembled native files and require no PowerShell, Git or source checkout. Publication and subscribed-download acceptance have not occurred.
