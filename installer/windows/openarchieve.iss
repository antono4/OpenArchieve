; OpenArchieve Windows Installer (Inno Setup)
; Build on Windows:
;   1. pip install -r requirements.txt
;   2. python -m PyInstaller OpenArchieve.spec --noconfirm
;   3. "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\windows\openarchieve.iss
; Output: dist_installers\OpenArchieve-Setup-1.0.0.exe

#define MyAppName "OpenArchieve"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OpenArchieve"
#define MyAppURL "https://github.com/antono4/OpenArchieve"
#define MyAppExeName "OpenArchieve.exe"

[Setup]
AppId={{8F9B3C2A-1D4E-4F2A-9B6C-7E1F0A2D3C4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\..\dist_installers
OutputBaseFilename=OpenArchieve-Setup-{#MyAppVersion}
SetupIconFile=..\..\icon_256.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "indonesian"; MessagesFile: "compiler:Languages\Indonesian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\OpenArchieve.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\icon_256.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Kill the app before uninstalling
Filename: "{cmd}"; Parameters: "/C taskkill /IM OpenArchieve.exe /F"; Flags: runhidden; RunOnceId: "KillApp"
