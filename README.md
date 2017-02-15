4d-plugin-set-application-icon
==============================

Call the Windows Resouces API to replace application icons of an executable file.

**Note:** probably not compatible with Windows XP which does not support PNG icons.

Obviously you shouldn't modify your own icon at runtime. To simply change the icon of a window, consider ``MDI USE ICON FILE`` in [mdi](https://github.com/miyako/4d-plugin-mdi). You can use [picture-to-ico](https://github.com/miyako/4d-plugin-picture-to-ico) to create large PNG icons.

**Discussion**

Normally you can customise the icon when you build an application using 4D.

Finalizing and deploying final applications > [Customizing a stand-alone application icon](http://doc.4d.com/4Dv15/4D/15.4/Customizing-a-stand-alone-application-icon.300-3285532.en.html)

See also [4D XML Keys BuildApplication](http://doc.4d.com/4Dv16/4D/16/4D-XML-Keys-BuildApplication.100-3130124.en.html)

However, 4D application builder does not support compressed PNG image embedded ICO files.

Use of compressed PNG is not mandatory for large icons, [it is not illegal to create large icons with BMP only](https://en.wikipedia.org/wiki/ICO_(file_format)), so the workaround is to find an ICO creator that supports large BMP. 

This plugin allows the direct use of a PNG icon source which is not supported in 4D (at least v14 and v15).

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
