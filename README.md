# pylock

文件加密工具，使用 AES ZIP + TAR 多层打包。

## 功能

1. 使用 AES-256 加密 ZIP 打包目标文件
2. 原文件名以 UTF-8 编码写入 `.ciper` 文件
3. ZIP 名字、TAR 名字和 ZIP 内的文件名均使用随机字符（20位字母数字）
4. 将加密 ZIP 和元数据打包成 TAR
5. 自动记录加密日志到 `cipertext.json`

## 加密流程

```
输入: 123.mp3
输出: asdfwini82afsooino.tar

asdfwini82afsooino.tar:
    123.mp3.txt              (空文件，用于迷惑)
    ninodfasfjonpn.zip      (加密 ZIP)

ninodfasfjonpn.zip:
    qwerasdfzxcv12345       (加密后的文件内容)
    892jiae40n.ciper        (包含原始文件名)
```

## 安装

```bash
uv sync
```

## 配置

首次运行程序后，会在同级目录生成 `config.json`：

```json
{
    "password": ""
}
```

编辑此文件设置默认密码。

## 使用

### GUI 模式（推荐）

```bash
uv run python -m pylock.gui
```

或安装后使用：

```bash
pylock-gui
```

功能：
- 点击选择文件
- 密码输入（支持显示/隐藏）
- 加密/解密模式切换
- 进度显示
- 加密历史记录查看

### CLI 模式

加密文件：

```bash
uv run python -m pylock <目标文件>
```

解密文件：

```bash
uv run python -m pylock -u <tar文件>
```

## 打包

```bash
python -m PyInstaller build/pylock.spec --clean
```

打包产物位于 `dist/` 目录：
- `pylock-gui.exe` - 主程序
- `config.json` - 首次运行自动生成
- `cipertext.json` - 首次运行自动生成

## 环境

- Python 3.14+
- uv（包管理）
