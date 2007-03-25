; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Editra"
!define PRODUCT_VERSION "0.0.80"
!define PRODUCT_PUBLISHER "Cody Precord"
!define PRODUCT_WEB_SITE "http://editra.org"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\editra.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "pixmaps\editra.ico"
!define MUI_UNICON "pixmaps\editra.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "COPYING.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\editra.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\CHANGELOG.txt"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "editra.win32.0.0.80.exe"
InstallDir "$PROGRAMFILES\Editra"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR\pixmaps"
  SetOverwrite try
  File "pixmaps\editra.ico"
  File "pixmaps\editra.png"
  File "pixmaps\editra.icns"
  SetOutPath "$INSTDIR\pixmaps\mime"
  File "pixmaps\mime\c.png"
  File "pixmaps\mime\cpp.png"
  File "pixmaps\mime\css.png"
  File "pixmaps\mime\header.png"
  File "pixmaps\mime\html.png"
  File "pixmaps\mime\java.png"
  File "pixmaps\mime\makefile.png"
  File "pixmaps\mime\perl.png"
  File "pixmaps\mime\php.png"
  File "pixmaps\mime\python.png"
  File "pixmaps\mime\ruby.png"
  File "pixmaps\mime\shell.png"
  File "pixmaps\mime\tex.png"
  File "pixmaps\mime\text.png"
  SetOutPath "$INSTDIR\language"
  SetOutPath "$INSTDIR\language\english"
  File "language\english\ed_lang.py"
  SetOutPath "$INSTDIR\language\japanese"
  File "language\japanese\ed_lang.py"
  SetOutPath "$INSTDIR\profiles"
  File "profiles\.loader"
  File "profiles\default.pp"
  File "profiles\default.pp.sample"
  SetOutPath "$INSTDIR\src"
  File "src\__init__.py"
  File "src\dev_tool.py"
  File "src\ed_glob.py"
  File "src\ed_pages.py"
  File "src\prefdlg.py"
  File "src\profiler.py"
  File "src\ed_stc.py"
  File "src\ed_theme.py"
  File "src\ed_toolbar.py"
  File "src\util.py"
  File "src\editra.py"
  File "src\setup.py"
  SetOutPath "$INSTDIR\src\extern"
  File "src\extern\__init__.py"
  File "src\extern\FlatNotebook.py"
  File "src\extern\README"
  SetOutPath "$INSTDIR\templates"
  File "templates\py"
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "w9xpopen.exe"
  File "README.txt"
  File "python24.dll"
  File "editra.exe"
  CreateDirectory "$SMPROGRAMS\Editra"
  CreateShortCut "$SMPROGRAMS\Editra\Editra.lnk" "$INSTDIR\editra.exe"
  CreateShortCut "$DESKTOP\Editra.lnk" "$INSTDIR\editra.exe"
  File "MSVCR71.dll"
  File "library.zip"
  File "COPYING.txt"
  File "CHANGELOG.txt"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Editra\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Editra\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\w9xpopen.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\w9xpopen.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\CHANGELOG.txt"
  Delete "$INSTDIR\COPYING.txt"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\MSVCR71.dll"
  Delete "$INSTDIR\editra.exe"
  Delete "$INSTDIR\python24.dll"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\templates\py"
  Delete "$INSTDIR\src\__init__.py"
  Delete "$INSTDIR\src\setup.py"
  Delete "$INSTDIR\src\editra.py"
  Delete "$INSTDIR\src\util.py"
  Delete "$INSTDIR\src\ed_stc.py"
  Delete "$INSTDIR\src\ed_theme.py"
  Delete "$INSTDIR\src\ed_toolbar.py"
  Delete "$INSTDIR\src\profiler.py"
  Delete "$INSTDIR\src\prefdlg.py"
  Delete "$INSTDIR\src\ed_pages.py"
  Delete "$INSTDIR\src\ed_glob.py"
  Delete "$INSTDIR\src\dev_tool.py"
  Delete "$INSTDIR\src\extern\__init__.py"
  Delete "$INSTDIR\src\extern\FlatNotebook.py"
  Delete "$INSTDIR\src\extern\README"
  Delete "$INSTDIR\profiles\default.pp.sample"
  Delete "$INSTDIR\profiles\default.pp"
  Delete "$INSTDIR\profiles\.loader"
  Delete "$INSTDIR\pixmaps\editra.png"
  Delete "$INSTDIR\pixmaps\editra.ico"
  Delete "$INSTDIR\pixmaps\editra.icns"
  Delete "$INSTDIR\pixmaps\mime\c.png"
  Delete "$INSTDIR\pixmaps\mime\cpp.png"
  Delete "$INSTDIR\pixmaps\mime\css.png"
  Delete "$INSTDIR\pixmaps\mime\header.png"
  Delete "$INSTDIR\pixmaps\mime\html.png"
  Delete "$INSTDIR\pixmaps\mime\java.png"
  Delete "$INSTDIR\pixmaps\mime\makefile.png"
  Delete "$INSTDIR\pixmaps\mime\perl.png"
  Delete "$INSTDIR\pixmaps\mime\php.png"
  Delete "$INSTDIR\pixmaps\mime\python.png"
  Delete "$INSTDIR\pixmaps\mime\ruby.png"
  Delete "$INSTDIR\pixmaps\mime\shell.png"
  Delete "$INSTDIR\pixmaps\mime\tex.png"
  Delete "$INSTDIR\pixmaps\mime\text.png"

  Delete "$SMPROGRAMS\Editra\Uninstall.lnk"
  Delete "$SMPROGRAMS\Editra\Website.lnk"
  Delete "$DESKTOP\Editra.lnk"
  Delete "$SMPROGRAMS\Editra\Editra.lnk"

  RMDir "$SMPROGRAMS\Editra"
  RMDir "$INSTDIR\templates"
  RMDir "$INSTDIR\src\extern"
  RMDir "$INSTDIR\src"
  RMDir "$INSTDIR\language\english"
  RMDir "$INSTDIR\language\japanese"
  RMDir "$INSTDIR\language"
  RMDir "$INSTDIR\profiles"
  RMDir "$INSTDIR\pixmaps\mime"
  RMDir "$INSTDIR\pixmaps"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

