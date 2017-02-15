4d-plugin-set-application-icon
==============================

Call the Windows Resouces API to replace application icons of an executable file.

**Note:** probably not compatible with Windows XP which does not support PNG icons.

Obviously you shouldn't modify your own icon at runtime. To simply change the icon of a window, consider ``MDI USE ICON FILE`` in [mdi](https://github.com/miyako/4d-plugin-mdi). You can use [picture-to-ico](https://github.com/miyako/4d-plugin-picture-to-ico) to create large PNG icons.

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|||<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|

###Version

<img src="https://cloud.githubusercontent.com/assets/1725068/18940649/21945000-8645-11e6-86ed-4a0f800e5a73.png" width="32" height="32" /> <img src="https://cloud.githubusercontent.com/assets/1725068/18940648/2192ddba-8645-11e6-864d-6d5692d55717.png" width="32" height="32" />

##Syntax

```
SET APPLICATION ICON(path;icon)
```

Parameter|Type|Description
------------|------|----
path|TEXT|Path to the application to modify
icon|IMAGE|Icon image; pass a ``256x256`` PNG for best results


##Example
```
$path:=Get 4D folder(Current Resources folder)+"4D.png"
READ PICTURE FILE($path;$icon)

$path:=System folder(Desktop)+"4D.exe"

SET APPLICATION ICON($path;$icon)
```
