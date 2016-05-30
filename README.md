4d-plugin-set-application-icon
==============================

Call the Windows Resouces API to replace application icons of an executable file.

Pass a 256 x 256 image for the best results.

**Note:** probably not compatible with Windows XP which does not support PNG icons.

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

* Example of an application with custom large PNG icon:
 
![v12](https://cloud.githubusercontent.com/assets/1725068/15647602/a56aff6a-269f-11e6-8e73-e5979182f170.png)
