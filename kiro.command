#!/bin/bash
# ================================================================
#  kiro 起動スクリプト
#  このファイルをダブルクリックするとアプリが起動します
# ================================================================

cd "$(dirname "$0")"

# 仮想環境の確認
if [ ! -f ".venv/bin/activate" ]; then
    echo "[エラー] 仮想環境が見つかりません。"
    echo "  先に install.command を実行してください。"
    read -p "Enterキーで閉じます..."
    exit 1
fi

source .venv/bin/activate
python main.py
