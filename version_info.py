# PyInstaller版本信息文件
# 添加正规的exe元数据，减少SmartScreen误报

VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(2, 0, 0, 0),
        prodvers=(2, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'080404b0',  # 中文简体
                    [
                        StringStruct(u'CompanyName', u'超级骆狗工具箱'),
                        StringStruct(u'FileDescription', u'流氓软件扫描清理工具'),
                        StringStruct(u'FileVersion', u'2.0.0.0'),
                        StringStruct(u'InternalName', u'scanner'),
                        StringStruct(u'LegalCopyright', u'Copyright © 2024 超级骆狗'),
                        StringStruct(u'OriginalFilename', u'超级骆狗工具箱.exe'),
                        StringStruct(u'ProductName', u'超级骆狗工具箱'),
                        StringStruct(u'ProductVersion', u'2.0.0.0'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
    ]
)
