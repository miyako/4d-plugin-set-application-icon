# 4d-plugin-set-application-icon

This plugin replaces the icons embedded in a Windows executable (`.exe`) by calling the Windows resource-update API. You give it a `Picture` and the path of an executable; it converts the picture to PNG, renders it at six sizes (16, 32, 48, 64, 128 and 256 pixels), and writes those into the executable's icon resources. Nothing is returned.

It is useful when 4D's own application builder can't produce the icon you want. The builder doesn't support ICO files that contain PNG-compressed images (see the [README](README.md) for background); this plugin accepts a plain PNG source instead.

| Command | Returns | Purpose |
|---|---|---|
| [SET APPLICATION ICON](#set-application-icon) | nothing | Replace the icons of a Windows executable with a picture |

**Platforms:** Windows only. On macOS the command is accepted and does nothing.

---

## Requirements & platform notes

- **Windows Vista or later.** The icons are stored as PNG-compressed images, which Windows XP doesn't support.
- **Both parameters are mandatory.** There is no optional form.
- **Failure is silent.** The command returns nothing and raises no 4D error. If the target can't be updated, you simply see no change. Check the result yourself (see [Error handling & troubleshooting](#error-handling--troubleshooting)).
- **Don't modify the executable that is currently running**, and don't target a file another process has locked. Windows will refuse the update, and as above you won't be told.
- **Write permission is required** on the target file and its folder.
- **Modifying an executable invalidates any digital signature it carries.** If you sign your applications, run this command first and sign afterwards.
- **The `path` must be a Windows system path** (for example `C:\Apps\MyApp.exe`), not a POSIX or 4D-colon path. This is inferred from the code, which hands the text straight to the Windows API. The `System folder` command used in the README example returns paths in this form.

---

## SET APPLICATION ICON

### Syntax

```4d
SET APPLICATION ICON ( path ; icon )
```

| Parameter | Type | Description |
|---|---|---|
| `path` | Text | Path of the executable to modify |
| `icon` | Picture | Source image for the icon |
| Result | | None |

### Description

`SET APPLICATION ICON` converts `icon` to PNG, then resizes it to 16, 32, 48, 64, 128 and 256 pixels square. Windows renders the 96 pixel size automatically, so none is generated. Those six images are written into the executable as its icon set, replacing the previous one.

**Which icon group is replaced.** An executable stores its icons in named groups. The command looks for the first *named* icon group in the file and replaces that one, keeping its language setting. If the file has no named group, it creates a group called `MAINICON` in English (US). A 4D-built application normally uses a group named `APPICON`, not `MAINICON`; the command finds it automatically, so you don't need to know the name.

> **Groups identified by a number are not recognised.** Some executables, such as many built with Visual Studio, identify their icon group by number (for example `101`) rather than by name. The command ignores those. For such a file it adds a new `MAINICON` group and leaves the original in place, so the old icon may still be the one Windows displays.

**Choosing the source image.** Pass a square picture of at least 256 × 256 pixels, ideally a PNG, for best results. Any format 4D can decode is accepted, because the plugin converts it first. All six sizes are produced by 4D's own thumbnail command, so how a non-square or small image is fitted into the square sizes is decided by 4D and isn't documented here. Square sources avoid the question.

**On Windows**, the update is all-or-nothing in the rebuilt plugin: if any icon image fails to write, the whole update is discarded and the executable is left as it was. If the source picture can't be converted to all six PNG sizes, the command stops before opening the file.

**On macOS**, the command returns immediately and does nothing. To change the icon of a window rather than of an executable, see `MDI USE ICON FILE` in the [mdi plugin](https://github.com/miyako/4d-plugin-mdi). To create large PNG icons, see the [picture-to-ico plugin](https://github.com/miyako/4d-plugin-picture-to-ico).

> **About the "all-or-nothing" behaviour.** The discard-on-failure and stop-before-opening behaviours were added to the source after a code review. They are true of a plugin built from the revised `4DPlugin.cpp`, not necessarily of a binary you already have installed. An older build may commit a partially updated icon set when something fails.

### Example

From the plugin's README:

```4d
$path:=Get 4D folder(Current Resources folder)+"4D.png"
READ PICTURE FILE($path;$icon)

$path:=System folder(Desktop)+"4D.exe"

SET APPLICATION ICON($path;$icon)
```

Applying the same icon to several executables, skipping any that don't exist:

```4d
READ PICTURE FILE($iconPath;$icon)

ARRAY TEXT($targets;2)
$targets{1}:=System folder(Desktop)+"First.exe"
$targets{2}:=System folder(Desktop)+"Second.exe"

For ($i;1;Size of array($targets))
	If (Test path name($targets{$i})=Is a document)
		SET APPLICATION ICON($targets{$i};$icon)
	End if
End for
```

Because a failed update can't be undone from 4D, keep a copy of the original executable before you run the command. Use 4D's file-copy command for this; check your Language Reference for its exact syntax on your version.

---

## Error handling & troubleshooting

- **Nothing happens and no error appears.** This is the normal way every failure looks. Confirm the file exists with `Test path name`, that it is a Windows executable, and that you have write access.
- **The file is locked or running.** Windows won't update an executable that is in use. Close the application, or work on a copy and swap it in later.
- **The old icon still shows.** Windows caches icons aggressively. Rename or move the file, or restart Explorer, before concluding the update failed. If the file uses a numbered icon group (see above), the original group may also still be the one displayed.
- **The icon looks stretched or padded.** The source wasn't square. Supply a square picture.
- **The icon is blank in some places (title bar, task switcher) but fine in others.** Windows documents PNG-compressed icons only for the 256 pixel size. The smaller PNG images are accepted by current versions of Windows Explorer, but older icon-loading paths haven't been tested, so verify on the Windows versions you support.
- **The digital signature is now invalid.** Expected, since any change to the file's resources invalidates it. Sign after running this command.
- **Nothing happens on macOS.** By design. The command is Windows-only.
- **Diagnostic output.** On Windows, the plugin writes a short message to the debugger output stream (`OutputDebugString`) when an individual update step fails, including the Windows error code. You can read it with a tool such as DebugView; 4D itself doesn't show it.

---

## Quick reference

```4d
// Load a square PNG, at least 256x256
READ PICTURE FILE($iconPath;$icon)

// Windows system path of the executable
SET APPLICATION ICON($exePath;$icon)

// Nothing is returned; verify the result yourself
```
