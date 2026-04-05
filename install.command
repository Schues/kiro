#!/bin/bash
# ================================================================
#  kiro インストーラ
#  このファイルをダブルクリックするとインストールが始まります
# ================================================================

# スクリプトのある場所へ移動（ダブルクリック時はホームが起点になるため）
cd "$(dirname "$0")"

echo ""
echo "================================================================"
echo "  kiro インストーラへようこそ"
echo "================================================================"
echo ""

# ----------------------------------------
# 1. Python バージョン確認
# ----------------------------------------
echo ">>> Python を確認中..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
        MAJOR=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        MINOR=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "[エラー] Python 3.10 以上が見つかりません。"
    echo "  https://www.python.org/downloads/ からインストールしてください。"
    echo ""
    read -p "Enterキーで閉じます..."
    exit 1
fi

echo "    OK: $($PYTHON --version)"

# ----------------------------------------
# 2. tkinter 確認
# ----------------------------------------
echo ">>> tkinter を確認中..."

if ! "$PYTHON" -c "import tkinter" &>/dev/null; then
    echo ""
    echo "[警告] tkinter が見つかりません。"
    echo "  インストールを試みます..."
    echo ""

    if command -v brew &>/dev/null; then
        PYVER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        brew install "python-tk@${PYVER}"
        if ! "$PYTHON" -c "import tkinter" &>/dev/null; then
            echo ""
            echo "[エラー] tkinter のインストールに失敗しました。"
            echo "  手動で 'brew install python-tk@${PYVER}' を実行してください。"
            read -p "Enterキーで閉じます..."
            exit 1
        fi
    else
        echo "[エラー] Homebrew が見つかりません。"
        echo "  https://brew.sh からインストール後、再度実行してください。"
        read -p "Enterキーで閉じます..."
        exit 1
    fi
fi

echo "    OK: tkinter"

# ----------------------------------------
# 3. 仮想環境の作成
# ----------------------------------------
echo ">>> 仮想環境を作成中..."

if [ -d ".venv" ]; then
    echo "    既存の .venv を再利用します"
else
    "$PYTHON" -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[エラー] 仮想環境の作成に失敗しました。"
        read -p "Enterキーで閉じます..."
        exit 1
    fi
    echo "    OK: .venv を作成しました"
fi

# ----------------------------------------
# 4. watchdog のインストール
# ----------------------------------------
echo ">>> watchdog をインストール中..."

.venv/bin/pip install --quiet --upgrade watchdog
if [ $? -ne 0 ]; then
    echo "[エラー] watchdog のインストールに失敗しました。"
    read -p "Enterキーで閉じます..."
    exit 1
fi

echo "    OK: watchdog"

# ----------------------------------------
# 5. 起動スクリプトに実行権限を付与
# ----------------------------------------
chmod +x kiro.command

# ----------------------------------------
# 完了
# ----------------------------------------
echo ""
echo "================================================================"
echo "  インストール完了！"
echo "================================================================"
echo ""
echo "  起動方法："
echo "    kiro.command をダブルクリック"
echo ""
echo "  または端末から："
echo "    source .venv/bin/activate"
echo "    python main.py"
echo ""
read -p "Enterキーで閉じます..."
