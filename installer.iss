; ============================================================
; 超级骆狗工具箱 - Inno Setup 安装脚本
; 运行环境: Windows + Inno Setup 6
; 用法: iscc installer.iss
; ============================================================

#define AppName       "超级骆狗工具箱"
#define AppVersion    "3.0.0"
#define AppPublisher  "骆狗"
#define AppURL        "https://github.com/RobustLuo/scanne"
#define AppExeName    "超级骆狗工具箱.exe"

[Setup]
AppId={{B8F4A3D2-7E61-4C92-A1F5-9D83C6E52041}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
UninstallDisplayName={#AppName}
OutputDir=installer_output
OutputBaseFilename={#AppName}-Setup-v{#AppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

; 安装器显示中文
[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkedonce

[Files]
; 主程序（Web UI 版）
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 附加版本
Source: "dist\超级骆狗工具箱-GUI.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "dist\超级骆狗工具箱-命令行.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"
Name: "{group}\超级骆狗工具箱 (GUI)";    Filename: "{app}\超级骆狗工具箱-GUI.exe"
Name: "{group}\超级骆狗工具箱 (命令行)";  Filename: "{app}\超级骆狗工具箱-命令行.exe"
Name: "{group}\卸载 {#AppName}";         Filename: "{uninstallexe}"

; 桌面快捷方式
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent runascurrentuser

[Code]
// 安装前检查：关闭正在运行的程序
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // 尝试关闭旧版本
  if CheckForMutexes('{#AppName}') then
  begin
    if MsgBox('检测到 {#AppName} 正在运行，是否关闭并继续安装？',
               mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec('taskkill', '/f /im "{#AppExeName}"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
      Result := False;
  end;
end;
