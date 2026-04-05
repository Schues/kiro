#!/bin/bash
# セットアップスクリプト

echo "=== 仮想環境を作成 ==="
python3 -m venv .venv

echo "=== 仮想環境を有効化 ==="
source .venv/bin/activate

echo "=== 依存パッケージをインストール ==="
pip install watchdog

echo ""
echo "=== セットアップ完了 ==="
echo "実行するには:"
echo "  source .venv/bin/activate"
echo "  python main.py"
