; Hover Dictionary - Inno Setup installer script
;
; This builds a single setup.exe that end users double-click to install.
; It installs the app, adds a Start Menu shortcut, registers it to launch
; automatically at Windows login, and creates a normal uninstaller.
;
; Prerequisites before compiling this:
;   1. Run build.bat first, so dist\HoverDictionary.exe exists.
;   2. Install Inno Setup (free): https://jrsoftware.org/isdl.php
;   3. Open this file in the Inno Setup Compiler and click Compile
;      (or run from command line: iscc installer.iss)

#define MyAppName "Hover Dictionary"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "HoverDictionary.exe"

[Setup]
AppId={{B8F1A2C4-7E3D-4A9B-9C1E-2F6D8A0B5E11}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=HoverDictionary-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; No admin rights required - installs to the current user's local folder
PrivilegesRequired=lowest
DefaultDirName={userpf}\{#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "startupicon"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup options:"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; If you built with --onedir instead of --onefile, uncomment the next
; line to also copy the rest of the bundled folder contents:
; Source: "dist\HoverDictionary\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Autostart entry - drops a shortcut in the user's Startup folder
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up log files created in %LOCALAPPDATA%\HoverDictionary on uninstall
Type: filesandordirs; Name: "{localappdata}\HoverDictionary"
