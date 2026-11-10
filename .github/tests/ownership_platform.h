#import <Carbon/Carbon.h>
#import <Cocoa/Cocoa.h>
#import <ImageIO/ImageIO.h>

@interface OwnershipURL : NSObject
- (id)initWithString:(NSString *)value;
- (NSString *)absoluteString;
@end
@interface OwnershipImage : NSObject
- (id)initWithCGImage:(CGImageRef)image size:(NSSize)size;
- (NSData *)TIFFRepresentation;
@end
CFURLRef OwnershipCreateURL(CFAllocatorRef, CFStringRef, CFURLPathStyle, Boolean);
CFStringRef OwnershipCopyPath(CFURLRef, CFURLPathStyle);

#define NSURL OwnershipURL
#define NSImage OwnershipImage
#define CFURLCreateWithFileSystemPath OwnershipCreateURL
#define CFURLCopyFileSystemPath OwnershipCopyPath

#include "4DPluginAPI.h"

#ifdef OWNERSHIP_WINDOWS_DISPATCH
// Preserve the unchanged SDK ABI, then compile the Windows dispatcher against
// synthetic platform declarations. No Windows/system implementation is linked.
#undef VERSIONWIN
#undef VERSIONMAC
#define VERSIONWIN 1
#define VERSIONMAC 0
typedef void *HMODULE;
typedef void *HANDLE;
typedef void *LPVOID;
typedef const PA_Unichar *LPCTSTR;
typedef PA_Unichar *LPTSTR;
typedef const PA_Unichar *LPCWSTR;
typedef intptr_t LONG_PTR;
typedef unsigned short WORD;
#define BOOL int
#define CALLBACK
#define FALSE 0
#define TRUE 1
#define IS_INTRESOURCE(value) (reinterpret_cast<uintptr_t>(value) <= 0xffff)
#define MAKEINTRESOURCE(value) reinterpret_cast<LPCTSTR>(static_cast<uintptr_t>(value))
#define RT_ICON MAKEINTRESOURCE(3)
#define RT_GROUP_ICON MAKEINTRESOURCE(14)
#define LANG_ENGLISH 9
#define SUBLANG_DEFAULT 1
#define MAKELANGID(language, sublanguage) ((sublanguage << 10) | language)
#define LOAD_LIBRARY_AS_DATAFILE 2
typedef BOOL (*ENUMRESNAMEPROC)(HMODULE, LPCTSTR, LPTSTR, LONG_PTR);
typedef BOOL (*ENUMRESLANGPROC)(HMODULE, LPCTSTR, LPCTSTR, WORD, LONG_PTR);
HMODULE OwnershipLoadLibrary(LPCWSTR, void *, unsigned);
void *OwnershipFindResource(HMODULE, LPCTSTR, LPCTSTR);
BOOL OwnershipEnumNames(HMODULE, LPCTSTR, ENUMRESNAMEPROC, LONG_PTR);
BOOL OwnershipEnumLanguages(HMODULE, LPCTSTR, LPCTSTR, ENUMRESLANGPROC, LONG_PTR);
BOOL OwnershipFreeLibrary(HMODULE);
HANDLE OwnershipBeginUpdate(LPCWSTR, BOOL);
BOOL OwnershipUpdate(HANDLE, LPCTSTR, LPCTSTR, WORD, LPVOID, unsigned);
BOOL OwnershipEndUpdate(HANDLE, BOOL);
unsigned long OwnershipLastError();
void OwnershipDebug(const char *);
void OwnershipYield();
#define LoadLibraryEx OwnershipLoadLibrary
#define FindResource OwnershipFindResource
#define EnumResourceNames OwnershipEnumNames
#define EnumResourceLanguages OwnershipEnumLanguages
#define FreeLibrary OwnershipFreeLibrary
#define BeginUpdateResource OwnershipBeginUpdate
#define UpdateResource OwnershipUpdate
#define EndUpdateResource OwnershipEndUpdate
#define GetLastError OwnershipLastError
#define OutputDebugStringA OwnershipDebug
#define PA_YieldAbsolute OwnershipYield
#define sprintf_s(buffer, ...) snprintf(buffer, sizeof(buffer), __VA_ARGS__)
#endif
