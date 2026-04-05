@echo off
REM kiro v1.2 - Windows ビルド & zip パッケージングスクリプト
REM 実行前に pip install -r requirements.txt を済ませること

cd /d "%~dp0\.."
set VERSION=1.2
set ZIP_NAME=kiro_win_v%VERSION%.zip

echo === kiro v%VERSION% Windows ビルド開始 ===

REM PyInstaller で単一 exe を生成
REM --noconsole : コマンドプロンプト非表示
REM --workpath  : 一時ファイルを .pyinstaller_work に隔離
pyinstaller ^
  --noconsole ^
  --onefile ^
  --name kiro ^
  --distpath dist ^
  --workpath .pyinstaller_work ^
  --noconfirm ^
  --add-data "src;src" ^
  main.py

echo.
echo === zip パッケージング ===

REM ステージングディレクトリに必要ファイルを集める
set STAGE=dist\_stage
if exist "%STAGE%" rmdir /s /q "%STAGE%"
mkdir "%STAGE%"
copy dist\kiro.exe "%STAGE%\"
copy README.md "%STAGE%\"

REM zip 作成（PowerShell を使用）
powershell -Command "Compress-Archive -Path '%STAGE%\*' -DestinationPath 'dist\%ZIP_NAME%' -Force"

REM ステージングを削除
rmdir /s /q "%STAGE%"

echo.
echo 完了: dist\%ZIP_NAME%
echo このファイルを配布してください。
pause
