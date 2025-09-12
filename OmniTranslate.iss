[Setup]
AppName=OmniTranslate
AppVersion=1.0
DefaultDirName={pf}\OmniTranslate
DefaultGroupName=OmniTranslate
OutputDir=dist
OutputBaseFilename=OmniTranslateSetup
SetupIconFile=icon.ico
LicenseFile=LICENSE.txt
WizardStyle=modern

[Messages]
WelcomeLabel1=Welcome to the OmniTranslate Setup Wizard
WelcomeLabel2=This wizard will guide you through the installation of OmniTranslate.\n\nClick Next to continue.

[Files]
Source: "dist\\OmniTranslate.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "instruction.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "language.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "settings.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\OmniTranslate"; Filename: "{app}\OmniTranslate.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\OmniTranslate"; Filename: "{app}\OmniTranslate.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "autorun"; Description: "Start OmniTranslate automatically with Windows"; GroupDescription: "Startup options:"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "OmniTranslate"; ValueData: """{app}\\OmniTranslate.exe"""; Flags: uninsdeletevalue; Tasks: autorun 