# Native ownership audit

## Immutable inputs

Baseline: `b6fd248e3ae5a6de79554b6f8047399be59a37fc`.
Canonical `miyako/skills/4d-skills/skills/4dplugin/SKILL.md` was read
through the contents API at `e6b492fcb81e5e1a7f7db723594b420e63bf6eb9`.
No SDK/engine/ABI file was changed. The SDK header says `rev : v13`;
this is not independently verified upstream release provenance.

All paths below are under `4D Plugin API/`. The runner verifies these Git
blobs before compiling the complete unchanged SDK.

| File | Baseline Git blob |
|---|---|
| `4DPluginAPI.c` | `478081f0238f6bc5393222f574bc2656f010b67b` |
| `4DPluginAPI.h` | `9054b45ffc7ff6f5b8d57529a3788a55d977b314` |
| `4DPluginAPI.def` | `996ecc4ab11ad165de9192eba2e7478db141c757` |
| `EntryPoints.h` | `730f2f77ff2713fb2fe4b7d6562baeedf5f664cb` |
| `Flags.h` | `10a83185333dac06a62dda61b9f9428243d1e2ee` |
| `PrivateTypes.h` | `77053dc0c0a3718d2d3b6f158371a6af78c6ae66` |
| `PublicTypes.h` | `2bb392e73e9c556c274fe0a75b3a6b83e310b77c` |

Prior art was read as immutable individual files, not another checkout:
`miyako/4d-plugin-picture-to-ico@656c0bc9577de01cf19f761a31a918d375f64609`
(`ownership_host.mm`, `ownership_platform.h`, `test_ownership.py`,
`CommandArguments.h`, `C_PICTURE.cpp`, `C_POINTER.cpp`). Tests are adapted
to this target's SDK, manifest, dispatcher and platform boundaries; results
are not copied from another repository.

## Complete native/build inventory

Tracked native sources comprise one SDK implementation, one plugin dispatcher
and 16 wrapper implementations with their headers. Both the Xcode Sources
phase and Visual C++ configurations include all 18 translation units. No
additional tracked native implementations, alternate SDK copies or uncompiled
wrappers were found. Indexed absence is not a proof of runtime safety.

Wrapper paths below are under `4D Plugin API/Classes/`.

| Sources | Owners, helpers and reachability |
|---|---|
| `4DPlugin.cpp`, `4DPlugin.h` | `PluginMain` dispatches selector 1 only. `SET_APPLICATION_ICON` copies a scalar path and retains a borrowed picture. Windows converts/renders six thumbnails and updates executable resources; macOS returns before picture commands/icon operations. Internal production helpers: `getPNG`, `getIcons`, two resource enumeration callbacks. |
| `C_TEXT.cpp/.h` | Copies UTF-16 input into independent C++ storage; parameter/return output calls the content setter. UTF conversion and Cocoa path helpers own copied storage/results. Its raw owned string pointer is already noncopyable at baseline. Production uses parameter input and pointer access; other helpers are latent capabilities. |
| `ARRAY_TEXT.cpp/.h` | Windows callback collects resource names and copies one out. Parameter-array input/output, UTF and Cocoa helpers are compiled but dormant. Borrowed elements are copied before mutation; each output element gets a distinct SDK string without post-transfer disposal. |
| `C_PICTURE.cpp/.h` (`CPicture`, `C_PICTURE`) | Production uses parameter input/destruction. File/byte input, native images, conversion, grayscale, dimensions, thumbnail and output/return methods are dormant capabilities. `CPicture` owns a picture reference plus raw `CBytes*`; facade owns raw `CPicture*`. |
| `C_POINTER.cpp/.h` | Borrowed pointer storage. Dormant owning pointer-value lookup requires error checking/cleanup. Definition output remains a reference descriptor, not a second owning value. |
| `C_BLOB.cpp/.h` (`CBytes`, `C_BLOB`) | Dormant parameter/output, hex/base64 helpers copy data; output handles are separately allocated. `CBytes` owns its vector by value and is used by `CPicture`; facade owns raw `CBytes*`. |
| `ARRAY_BOOLEAN.cpp/.h`, `ARRAY_DATE.cpp/.h`, `ARRAY_INTEGER.cpp/.h`, `ARRAY_LONGINT.cpp/.h`, `ARRAY_REAL.cpp/.h`, `ARRAY_TIME.cpp/.h` | Dormant primitive/date array wrappers, no SDK string owners. Each owns a heap vector through a raw pointer. Date elements are copyable by-value `C_DATE`. |
| `C_DATE.cpp/.h`, `C_INTEGER.cpp/.h`, `C_LONGINT.cpp/.h`, `C_REAL.cpp/.h`, `C_TIME.cpp/.h` | Dormant primitive/date scalar wrappers with by-value fields and empty destructors; no string/picture/handle owner. |
| `C_TYPES.h` | C++ string/vector aliases and platform includes, no engine implementation. |
| SDK files listed above | Protected complete implementation, engine selectors and ABI. `FourDPackex` calls `PluginMain`; Windows `.def` exports only `FourDPackex`. Internal `PA_GetProcessInfo(C_TEXT&)` uses the noncopyable text wrapper by reference. SDK internal arrays/getters/setters are included in the contract trace. |
| `4D Plugin_Prefix.pch` | Carbon prefix include, no owners. |

Both `manifest.json` copies declare one command:
`SET APPLICATION ICON(&T;&P)`: scalar text/picture parameters, no return
or manifest array. Internal/dormant arrays were audited regardless.
Constants, documentation, `.vcxproj.filters`, `.sln`, Xcode schemes/workspaces
and resource memberships introduce no other native entry points. Tracked
prebuilt macOS/Windows binaries and 4D database/project assets were not
executed or changed.

There are no JSON/object/collection wrappers or object/collection value APIs
in this SDK. Dialog UI APIs containing "Object" are not JSON property getters.
Object/collection counters are explicitly **not applicable**, not simulated
passing coverage.

## Exact local contracts and corrections

Line references here refer to the immutable SDK implementation.

* String creation, disposal and content setter (244-270) forward descriptors
  and content to the engine. Content replacement differs from struct transfer.
* `PA_CreateVariable` (3523-3654) creates empty owned pictures/strings.
  Scalar/picture setters (3826-3831, 3852-3857) shallow-overwrite without
  clearing existing values. `CommandArguments` initializes undefined slots
  so first assignment cannot abandon empty owners; its destructor clears
  independently owning arguments on success and exception.
* `PA_GetStringInArray` (4266-4284) is borrowed. Accepted insertion
  (4444-4459) disposes the old element and transfers the supplied descriptor.
  Predicates: Unicode array kind, non-null data, `0 <= index <= count`,
  non-null descriptor. Index zero is accepted. Existing wrapper success
  transfers are already correct and unchanged.
* Dormant `CPicture::fromFileAtPath` previously disposed the transferred path,
  then cleared its alias, and left the picture-output argument uncleared.
  It now retains the picture through `setPicture` before argument cleanup;
  the path has one disposer. `setBytes` releases the creation owner after
  `setPicture` retains it, including repeated calls.
* `PA_ConvertCharsetToCharset` (4775-4794) explicitly returns **bytes**.
  `createCopy` checks error before using output and divides by
  `sizeof(PA_Unichar)` for the C++ UTF-16 constructor. The baseline ASCII
  case gives an ASan buffer overread, not just a leak.
* Picture command helpers/Windows dispatcher no longer overwrite initialized
  input owners, detach borrowed output aliases, or discard successful owning
  returns. Returned pictures retain their own reference before argument
  cleanup. Each thumbnail's owner spans PNG extraction, so a later command
  exception cannot strand earlier thumbnails.
* `PA_ExecuteCommandByID` (5257-5290) allocates an argument-pointer handle.
  Failure can return raw kind zero, normalized by `PA_GetVariableKind` as
  string. The helper captures error before result inspection/adoption/cleanup.
  Failed output is unspecified and never cleared; successful returns are
  cleared independently of arguments. Tests probe undefined/string/picture
  return contracts, not a claim that these procedure commands actually
  return strings/pictures in a real host.
* `C_POINTER::getVariable` checks error before inspecting owning lookup output
  and clears the successful temporary after copying the reference descriptor.
  Header line 409 explicitly requires clearing `PA_GetPointerValue` results.
* Seven array wrappers, `C_BLOB`, `CPicture`, `C_PICTURE` had raw heap-owning
  pointers plus implicit shallow copying. They follow existing `C_TEXT`
  deleted-copy prior art. No production copy sites were found and all actual
  consumers compile: these are **latent** capabilities. By-value `CBytes`,
  date/scalar wrappers and borrowed `C_POINTER` are not blanket-disabled.

The existing plugin catch-all boundary now writes a diagnostic instead of
silently swallowing a surfaced command failure. Other unrelated error/format
behavior is not redesigned.

## Executed differential regression

Run `python3 .github/tests/test_ownership.py`.

The runner compiles all 16 actual wrappers, complete unchanged SDK and actual
dispatcher under ASan/UBSan. Alignment sanitization is excluded for the legacy
packed ABI. LeakSanitizer is disabled on macOS; explicit maps assert zero
strings, picture references and handles after each successful leaf.

Local platform: macOS 26.7 arm64, Apple clang 21.0.0
(`clang-2100.1.1.101`). The **same final harness** was run with
`OWNERSHIP_SOURCE_ROOT` pointing to an immutable `git archive` of the baseline
and to fixed actual source.

| Cases | Leaves | Baseline | Fixed |
|---|---:|---|---|
| Windows dispatch: success, failures at each of seven command calls, metadata enumeration/data failure, missing synthetic module, resource update/end failure; both empty engines | 26 | 26 fail (owner imbalance or unsurfaced error) | 26 pass |
| `path`, `copy`: ASCII, BMP U+65E5, supplementary U+1F600, empty; allocated/null empty engines | 16 | 16 fail (duplicate disposer, imbalance, ASCII ASan overflow) | 16 pass |
| Scalar copies, source mutation, output after wrapper destruction | 8 | 8 passing controls | 8 pass |
| Command-handle and command poison-output failure in five picture helpers; conversion failure | 11 | 11 fail | 11 pass |
| Repeated bytes creation, grayscale, size, thumbnail; output survives wrapper | 4 | 4 fail | 4 pass |
| Array copy, churn, repeated replacement, shrink, clear, undefined creation, index-zero acceptance and all setter rejection predicates | 2 | 2 passing controls | 2 pass |
| SDK raw-zero/physical-logical resize-failure characterization | 1 | 1 passing control | 1 pass |
| Independent undefined/string/picture command returns | 3 | 3 fail | 3 pass |
| Pointer owning lookup and poisoned failure output | 2 | 2 fail | 2 pass |
| macOS dispatcher no-op without icon commands/platform access | 1 | 1 passing control | 1 pass |
| Copy traits | 1 | 1 fail | 1 pass |
| Named copy-owner probes: boolean/date/integer/longint/real/text/time arrays, blob, picture, picture facade | 10 | 9 ASan heap-use-after-free; `CPicture` duplicate-picture-owner failure | 10 copy-disabled controls pass |
| **Total (11 test methods)** | **85** | **12 pass, 73 fail** | **85 pass** |

The existing offline lifecycle suite passes 46 tests; its release/tag messages
are mocked transports/local fixtures, not GitHub publication. Baseline/fixed
logs are retained as session artifacts, not bundled plugin binaries.
This is **not a reproduction of a Windows 4D crash**.

## Isolation, CI and explicit limits

Forced-include boundaries redirect URL/path/image classes before compiling
every source. The Windows dispatcher is compiled separately using synthetic
resource/loading/update/yield/debug declarations **after** including the
unchanged macOS SDK ABI. Only synthetic paths/pictures are dispatched;
exact PNG bytes/icon-group headers are asserted, without loading/mutating a
file. This tests Windows source branches, not Windows ABI/runtime. The macOS
dispatcher is compiled/executed separately. Engine callbacks reject unexpected
selectors; linked imports are checked for real URL/image/file-manager,
workspace, resource and process-launch boundaries. No application activation,
discovery, UI, private files, real image conversion or OS icon operations occur.

Project phases and CI/release scripts were inspected before choosing isolated
validation. Xcode has Headers/Resources/CopyFiles/Sources/Frameworks/Rez phases,
no shell phase; Visual C++ writes directly into tracked bundles and imports
platform/user property sheets. Neither project build was run. Existing
workflows are manual-only: version bump mutates source metadata; Build signs,
notarizes, packages and publishes. Neither was edited/dispatched. New
`ownership.yml` runs only the unsigned relevant-path harness for PRs and
pushes to `master` and the exact audit branch, with a read-only token and no
secrets, installation, signing, release or artifact upload.

Deferred, not certified:

* SDK allocation/resize failure preservation. `PA_ResizeArray` can change
  logical count despite physical resize failure. Tests characterize this and
  restore only the synthetic descriptor for cleanup. Passing success tests
  do not certify OOM safety; the void array wrapper boundary cannot safely
  repair arbitrary engine partial failure. The SDK remains protected.
* `PA_GetPictureData` metadata ownership is unspecified in this SDK. Tests
  use stable borrowed metadata, poison failed output and prove no reads on
  failure. No disposal was invented; real metadata ownership/leak
  certification needs an authoritative host contract.
* Actual 4D host behavior, Windows ABI/runtime, command cancellation, platform
  encoding branches and allocator failures beyond named synthetic predicates
  need separate authorized host testing.
