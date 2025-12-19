#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
from pathlib import Path

# ANSI 颜色码（兼容大多数现代终端）
C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
}

def color(text, col):
    return f"{C[col]}{text}{C['reset']}"

def get_sample_rate(file_path):
    """使用 ffprobe 获取音频文件的采样率（Hz），失败返回 None"""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate",
            "-of", "json",
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        if streams and "sample_rate" in streams[0]:
            return int(streams[0]["sample_rate"])
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, IndexError, KeyError):
        pass
    return None

def classify_sr(sr):
    return "HI-RES" if sr and sr > 44100 else "Standard"

def print_result(file_path, sr):
    rel_path = os.path.basename(file_path) if len(str(file_path)) > 60 else file_path
    if sr is None:
        status = color("⚠️  Failed", "red")
        print(f"  {status}  {rel_path}")
        return False
    category = classify_sr(sr)
    sr_khz = sr / 1000
    if category == "HI-RES":
        tag = color(f"🎯 HI-RES ({sr_khz:.1f} kHz)", "green")
    else:
        tag = color(f"🎧 Standard ({sr_khz:.1f} kHz)", "yellow")
    print(f"  {tag}  {rel_path}")
    return True

def scan_folder(folder_path):
    folder = Path(folder_path).resolve()
    if not folder.is_dir():
        print(color(f"❌ 错误：'{folder}' 不是有效文件夹", "red"))
        return

    print(color(f"\n🔍 正在扫描文件夹：{folder}", "blue"))
    print(color("="*80, "cyan"))

    extensions = {".flac", ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".opus"}
    audio_files = sorted([
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in extensions
    ])

    if not audio_files:
        print(color("⚠️  未找到支持的音频文件（flac/mp3/m4a/wav/aac/ogg/opus）", "yellow"))
        return

    print(f"🔎 共发现 {len(audio_files)} 个音频文件，正在分析...\n")

    hi_res_count = 0
    total_valid = 0

    for i, f in enumerate(audio_files, 1):
        sr = get_sample_rate(f)
        ok = print_result(f, sr)
        if ok:
            total_valid += 1
            if sr > 44100:
                hi_res_count += 1
        # 显示进度（简洁）
        if i % 10 == 0 or i == len(audio_files):
            print(f"   {color(f'📌 进度: {i}/{len(audio_files)}', 'cyan')}", end="\r", flush=True)
    print()  # 换行

    # === 汇总 ===
    print(color("\n📊 分析完成", "bold"))
    print(color("-" * 40, "cyan"))
    print(f"✅ 有效音频文件: {total_valid}")
    print(f"🎯 HI-RES ( >44.1kHz ): {hi_res_count}")
    if total_valid > 0:
        ratio = hi_res_count / total_valid * 100
        print(f"📈 HI-RES 占比: {ratio:.1f}%")
    if len(audio_files) != total_valid:
        print(f"⚠️  解析失败: {len(audio_files) - total_valid}")

def check_single_file():
    print(color("\n📁 请选择音频文件（支持 flac/mp3/m4a 等）", "blue"))
    print("提示：可拖拽文件到终端，或手动输入路径")
    try:
        path = input(color("➤ 文件路径: ", "cyan")).strip().strip("'\"")
    except (KeyboardInterrupt, EOFError):
        print("\n👋 再见！")
        sys.exit(0)

    if not path:
        print(color("❌ 路径为空", "red"))
        return

    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        print(color(f"❌ 文件不存在：{file_path}", "red"))
        return

    print(color(f"\n🔍 正在分析：{file_path.name}", "blue"))
    print(color("="*80, "cyan"))

    sr = get_sample_rate(file_path)
    print_result(file_path, sr)

    if sr is not None:
        category = classify_sr(sr)
        if category == "HI-RES":
            print(color("\n🎉 恭喜！这是高解析音频（HI-RES）", "green"))
        else:
            print(color(f"\nℹ️  这是标准音频（≤44.1kHz）", "yellow"))

def main():
    # ASCII Banner（可选，增加仪式感 😊）
    banner = r"""
  🎵 Audio Sample Rate Inspector
  ───────────────────────────────
    由 jiangzhihao 定制 · macOS 专用
    """
    print(color(banner, "cyan"))

    while True:
        print(color("\n❓ 请选择操作：", "bold"))
        print("  [1] 🔍 检测单个音频文件")
        print("  [2] 📁 批量检测整个文件夹")
        print("  [0] 🚪 退出")

        try:
            choice = input(color("➤ 请输入选项 [0/1/2]: ", "cyan")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见！")
            break

        if choice == "1":
            check_single_file()
        elif choice == "2":
            print(color("\n📁 请输入要扫描的文件夹路径", "blue"))
            print("提示：可拖拽文件夹到终端，或输入 ~/Music 等路径")
            try:
                folder = input(color("➤ 文件夹路径: ", "cyan")).strip().strip("'\"")
            except (KeyboardInterrupt, EOFError):
                continue
            if folder:
                scan_folder(folder)
        elif choice == "0":
            print(color("✨ 感谢使用！期待下次为您服务～", "green"))
            break
        else:
            print(color("⚠️  无效输入，请输入 0 / 1 / 2", "yellow"))

if __name__ == "__main__":
    # 检查 ffprobe 是否可用
    try:
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(color("❌ 错误：未找到 ffprobe（请先运行 `brew install ffmpeg`）", "red"))
        sys.exit(1)

    main()