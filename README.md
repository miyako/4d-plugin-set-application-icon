4d-plugin-set-application-icon
==============================

Call the Windows Resouces API to replace application icons of an executable file.

Pass a 256 x 256 image for the best results.

**Note:** probably not compatible with Windows XP which does not support PNG icons.

Obviously you shouldn't modify your own icon at runtime. To simply change the icon of a window, consider ``MDI USE ICON FILE`` in [mdi](https://github.com/miyako/4d-plugin-mdi). You can use (picture-to-ico)[https://github.com/miyako/4d-plugin-picture-to-ico] to create large PNG icons.

##Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|🚫|🚫|🆗|🆗|

Commands
---

```c
// --- Main
SET_APPLICATION_ICON
```

##Example
```
$path:=Get 4D folder(Current Resources folder)+"4D.png"
READ PICTURE FILE($path;$icon)

$path:=System folder(Desktop)+"4D.exe"

SET APPLICATION ICON($path;$icon)
```
