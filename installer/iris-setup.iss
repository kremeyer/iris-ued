; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define AppName "Iris - Interactive UES Exploration"
#define AppVersion "5.1.1"
#define AppPublisher "Laurent P. René de Cotret"
#define AppURL "https://iris-ued.readthedocs.io"
#define AppEXEName "iris.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{36E6FD0E-1B80-451E-8B5F-6158004844EE}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={pf}\{#AppName}
DisableProgramGroupPage=yes
ChangesEnvironment=true
LicenseFile=..\LICENSE.txt
OutputDir=.\dist\setup-{#AppVersion}
OutputBaseFilename=iris-setup-{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: ".\dist\executable\iris\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\{#AppName}"; Filename: "{app}\{#AppEXEName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppEXEName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppEXEName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent