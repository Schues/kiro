#!/bin/bash
# kiro v1.2 - macOS ビルド & zip パッケージングスクリプト
# 実行前に pip install -r requirements.txt を済ませること
set -e

cd "$(dirname "$0")/.."
VERSION="1.2"
ZIP_NAME="kiro_mac_v${VERSION}.zip"

echo "=== kiro v${VERSION} macOS ビルド開始 ==="

# PyInstaller でアプリバンドルを生成
# --windowed : ターミナル非表示の .app を作成
# --workpath : 一時ファイルを .pyinstaller_work に隔離（build/ と混在させない）
pyinstaller \
  --windowed \
  --name kiro \
  --distpath dist \
  --workpath .pyinstaller_work \
  --noconfirm \
  --add-data "src:src" \
  main.py

echo ""
echo "=== zip パッケージング ==="

# ステージングディレクトリに必要ファイルを集める
STAGE="dist/_stage"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -r dist/kiro.app "$STAGE/"
cp README.md "$STAGE/"

# zip 作成（dist/ 直下に出力）
cd "$STAGE"
zip -r "../../${ZIP_NAME}" .
cd ../..

# ステージングを削除
rm -rf "$STAGE"

echo ""
echo "完了: dist/${ZIP_NAME}"
echo "このファイルを配布してください。"
