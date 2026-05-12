import sys
ver = sys.argv[1]
outpath = sys.argv[2]
content = """; Crossfire Server Installer
; Built with NSIS

Unicode True

!define APP_NAME      "Crossfire Server"
!ifndef APP_VERSION
!define APP_VERSION   \"""" + ver + """"
!endif
!define APP_PUBLISHER "Crossfire Development Team"
!define INSTALL_DIR   "$PROGRAMFILES64\\Crossfire Server"
!define STAGING       "C:\\msys64\\home\\leaf\\crossfire-staging\\usr\\local\\crossfire"
!define SRCDIR        "C:\\msys64\\home\\leaf\\crossfire\\crossfire-server"
!define MSYS2         "C:\\msys64\\ucrt64"
!define DOWNLEVEL     "C:\\Windows\\System32\\downlevel"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "CrossfireServer-${APP_VERSION}-Setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\\Crossfire Server" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Crossfire Server" SecMain

    SectionIn RO

    SetOutPath "$INSTDIR\\bin"
    File "${STAGING}\\bin\\crossfire-server.exe"
    File "${SRCDIR}\\crossfire.dll"
    File "${MSYS2}\\bin\\libgcc_s_seh-1.dll"
    File "${MSYS2}\\bin\\libwinpthread-1.dll"
    File "${MSYS2}\\bin\\libstdc++-6.dll"
    File "${MSYS2}\\bin\\libpython3.14.dll"
    File "${MSYS2}\\bin\\libsqlite3-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-conio-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-convert-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-environment-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-filesystem-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-heap-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-locale-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-math-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-multibyte-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-private-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-process-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-runtime-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-stdio-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-string-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-time-l1-1-0.dll"
    File "${DOWNLEVEL}\\api-ms-win-crt-utility-l1-1-0.dll"

    SetOutPath "$INSTDIR\\lib\\crossfire\\plugins"
    File "${SRCDIR}\\plugins\\cfanim\\cfanim.dll"
    File "${SRCDIR}\\plugins\\cfpython\\cfpython.dll"

    SetOutPath "$INSTDIR\\etc\\crossfire"
    File "${STAGING}\\etc\\crossfire\\ban_file"
    File "${STAGING}\\etc\\crossfire\\dm_file"
    File "${STAGING}\\etc\\crossfire\\exp_table"
    File "${STAGING}\\etc\\crossfire\\forbid"
    File "${STAGING}\\etc\\crossfire\\gavoiddefs"
    File "${STAGING}\\etc\\crossfire\\metaserver2"
    File "${STAGING}\\etc\\crossfire\\motd"
    File "${STAGING}\\etc\\crossfire\\news"
    File "${STAGING}\\etc\\crossfire\\rules"
    File "${STAGING}\\etc\\crossfire\\settings"
    File "${STAGING}\\etc\\crossfire\\stat_bonus"
    File "${STAGING}\\etc\\crossfire\\treedefs"
    File "${STAGING}\\etc\\crossfire\\waterdefs"
    File "${STAGING}\\etc\\crossfire\\wavoiddefs"
    File "${STAGING}\\etc\\crossfire\\wevapdefs"
    File "${STAGING}\\etc\\crossfire\\wmeltdefs"
    File "${STAGING}\\etc\\crossfire\\wreplacedefs"
    File "${STAGING}\\etc\\crossfire\\wsettings"

    SetOutPath "$INSTDIR\\share\\crossfire"
    File "${STAGING}\\share\\crossfire\\attackmess"
    File "${STAGING}\\share\\crossfire\\crossfire.arc"
    File "${STAGING}\\share\\crossfire\\crossfire.artifacts"
    File "${STAGING}\\share\\crossfire\\crossfire.face"
    File "${STAGING}\\share\\crossfire\\crossfire.tar"
    File "${STAGING}\\share\\crossfire\\crossfire.trs"
    File "${STAGING}\\share\\crossfire\\def_help"
    File "${STAGING}\\share\\crossfire\\formulae"
    File "${STAGING}\\share\\crossfire\\image_info"
    File "${STAGING}\\share\\crossfire\\materials"
    File "${STAGING}\\share\\crossfire\\messages"
    File "${STAGING}\\share\\crossfire\\races"

    SetOutPath "$INSTDIR\\share\\crossfire\\help"
    File "${STAGING}\\share\\crossfire\\help\\*"

    SetOutPath "$INSTDIR\\share\\crossfire\\wizhelp"
    File "${STAGING}\\share\\crossfire\\wizhelp\\*"

    SetOutPath "$INSTDIR\\share\\crossfire\\i18n"
    File "${STAGING}\\share\\crossfire\\i18n\\*"

    SetOutPath "$INSTDIR\\share\\crossfire\\adm"
    File "${STAGING}\\share\\crossfire\\adm\\*"

    SetOutPath "$INSTDIR\\share\\crossfire\\maps"
    File /r "${STAGING}\\share\\crossfire\\maps\\*"

    SetOutPath "$INSTDIR"
    Delete "$INSTDIR\\start-server.bat"
    FileOpen $0 "$INSTDIR\\start-server.bat" w
    FileWrite $0 "@echo off$\\r$\\n"
    FileWrite $0 "cd /d $\\"$INSTDIR$\\"$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "set LOCALDIR=%ProgramData%\\Crossfire Server$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "set PYTHONHOME=C:\\msys64\\ucrt64$\\r$\\n"
    FileWrite $0 "set PYTHONPATH=C:\\msys64\\ucrt64\\lib\\python3.14;C:\\msys64\\ucrt64\\lib\\python3.14\\lib-dynload$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\players$\\" mkdir $\\"%LOCALDIR%\\players$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\accounts$\\" mkdir $\\"%LOCALDIR%\\accounts$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\account$\\" mkdir $\\"%LOCALDIR%\\account$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\unique-items$\\" mkdir $\\"%LOCALDIR%\\unique-items$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\template-maps$\\" mkdir $\\"%LOCALDIR%\\template-maps$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\maps$\\" mkdir $\\"%LOCALDIR%\\maps$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\highscores$\\" mkdir $\\"%LOCALDIR%\\highscores$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\bookarch$\\" mkdir $\\"%LOCALDIR%\\bookarch$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%LOCALDIR%\\tmp$\\" mkdir $\\"%LOCALDIR%\\tmp$\\"$\\r$\\n"
    FileWrite $0 "if not exist $\\"%ProgramData%\\Crossfire_Server\\highscores$\\" mkdir $\\"%ProgramData%\\Crossfire_Server\\highscores$\\"$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "icacls $\\"%LOCALDIR%$\\" /grant Everyone:(OI)(CI)F /T >nul 2>&1$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "del /f /q $\\"%LOCALDIR%\\accounts.tmp$\\" 2>nul$\\r$\\n"
    FileWrite $0 "del /q $\\"%LOCALDIR%\\account\\*.tmp$\\" 2>nul$\\r$\\n"
    FileWrite $0 "del /q $\\"%LOCALDIR%\\unique-items\\*.tmp$\\" 2>nul$\\r$\\n"
    FileWrite $0 "del /q $\\"%LOCALDIR%\\players\\*.tmp$\\" 2>nul$\\r$\\n"
    FileWrite $0 "del /q $\\"%LOCALDIR%\\highscore.tmp$\\" 2>nul$\\r$\\n"
    FileWrite $0 "for /r $\\"%LOCALDIR%\\players$\\" %%f in (*.tmp) do del /q $\\"%%f$\\" 2>nul$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "echo Crossfire Server starting...$\\r$\\n"
    FileWrite $0 "echo To stop the server, close this window.$\\r$\\n"
    FileWrite $0 "echo.$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "bin\\crossfire-server.exe -data share\\crossfire -conf etc\\crossfire -local $\\"%LOCALDIR%$\\" -p 13327$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "echo.$\\r$\\n"
    FileWrite $0 "echo Server has stopped.$\\r$\\n"
    FileWrite $0 "pause$\\r$\\n"
    FileClose $0

    ExecWait 'netsh advfirewall firewall delete rule name="Crossfire Server"'
    ExecWait 'netsh advfirewall firewall add rule name="Crossfire Server" dir=in action=allow protocol=TCP localport=13327 description="Crossfire RPG Server"'

    WriteRegStr HKLM "Software\\Crossfire Server" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CrossfireServer" \\
        "DisplayName" "${APP_NAME} ${APP_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CrossfireServer" \\
        "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CrossfireServer" \\
        "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CrossfireServer" \\
        "DisplayVersion" "${APP_VERSION}"
    WriteUninstaller "$INSTDIR\\uninstall.exe"

    SetShellVarContext all
    CreateDirectory "$SMPROGRAMS\\Crossfire Server"
    CreateShortcut "$SMPROGRAMS\\Crossfire Server\\Start Server.lnk" \\
        "$WINDIR\\system32\\cmd.exe" \\
        '/c start "Crossfire Server" "$INSTDIR\\start-server.bat"' \\
        "$INSTDIR\\bin\\crossfire-server.exe" 0
    CreateShortcut "$SMPROGRAMS\\Crossfire Server\\Uninstall.lnk" \\
        "$INSTDIR\\uninstall.exe"

SectionEnd

Section "Uninstall"

    SetShellVarContext all
    Delete "$INSTDIR\\uninstall.exe"
    Delete "$INSTDIR\\start-server.bat"
    RMDir /r "$INSTDIR\\bin"
    RMDir /r "$INSTDIR\\lib"
    RMDir /r "$INSTDIR\\etc"
    RMDir /r "$INSTDIR\\share"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\\Crossfire Server\\Start Server.lnk"
    Delete "$SMPROGRAMS\\Crossfire Server\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\Crossfire Server"

    ExecWait 'netsh advfirewall firewall delete rule name="Crossfire Server"'

    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\CrossfireServer"
    DeleteRegKey HKLM "Software\\Crossfire Server"

SectionEnd
"""
with open(outpath, 'w') as f:
    f.write(content)
print('Done - wrote ' + outpath)
