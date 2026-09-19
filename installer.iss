; installer.iss
;
; Inno Setup script that wraps the PyInstaller onedir build
; (dist\LedgerLens\) into a single distributable LedgerLensSetup.exe:
; Start Menu shortcut, optional desktop icon, standard uninstaller
; registered in Windows "Apps & Features". Requires dist\LedgerLens\
; to already exist — run `pyinstaller --windowed --name LedgerLens
; --icon icon.ico main.py` first (see README.md).
;
; Compile with: ISCC installer.iss

#define MyAppName "LedgerLens"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "LedgerLens"
#define MyAppExeName "LedgerLens.exe"

[Setup]
AppId={{B3B6B0B0-6C9E-4A6B-9D2E-3F1C6E7B2A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=LedgerLensSetup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
