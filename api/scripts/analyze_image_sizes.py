#!/usr/bin/env python3
"""画像ファイルサイズ比較スクリプト"""

import statistics
from pathlib import Path


def analyze_image_sizes(directory: str = ".data-dev/book_thum"):
    """jpgとwebpのファイルサイズを比較し統計情報を表示"""

    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"ディレクトリが存在しません: {directory}")
        return

    # ファイルサイズを収集
    jpg_sizes = {}
    webp_sizes = {}

    for file in dir_path.iterdir():
        if file.is_file() and file.suffix in {'.jpg', '.jpeg', '.webp'}:
            name = file.stem
            size = file.stat().st_size

            if file.suffix in {'.jpg', '.jpeg'}:
                jpg_sizes[name] = size
            elif file.suffix == '.webp':
                webp_sizes[name] = size

    # ペアを見つける
    pairs = []
    jpg_only = []
    webp_only = []

    for name in set(jpg_sizes.keys()) | set(webp_sizes.keys()):
        if name in jpg_sizes and name in webp_sizes:
            pairs.append((name, jpg_sizes[name], webp_sizes[name]))
        elif name in jpg_sizes:
            jpg_only.append((name, jpg_sizes[name]))
        elif name in webp_sizes:
            webp_only.append((name, webp_sizes[name]))

    # 統計情報を計算
    print("=" * 70)
    print("画像ファイルサイズ比較統計")
    print("=" * 70)

    print(f"\n対象ディレクトリ: {directory}")
    print(f"解析したファイル数: {len(pairs) * 2}")
    print(f"JPGファイル数: {len(jpg_sizes)}")
    print(f"WebPファイル数: {len(webp_sizes)}")
    print(f"ペア数（同一画像）: {len(pairs)}")

    if jpg_only:
        print(f"JPGのみのファイル: {len(jpg_only)}")
    if webp_only:
        print(f"WebPのみのファイル: {len(webp_only)}")

    if not pairs:
        print("\nペアが見つかりませんでした。")
        return

    # ペアのサイズ比較
    jpg_total = sum(s[1] for s in pairs)
    webp_total = sum(s[2] for s in pairs)

    # 圧縮率の計算
    compression_ratios = [
        (webp_size / jpg_size) * 100
        for _, jpg_size, webp_size in pairs
    ]

    # サイズ差
    size_differences = [
        jpg_size - webp_size
        for _, jpg_size, webp_size in pairs
    ]

    print("\n" + "=" * 70)
    print("全体統計")
    print("=" * 70)

    print(f"\nJPG総サイズ: {jpg_total:,} bytes ({jpg_total / 1024:.2f} KB)")
    print(f"WebP総サイズ: {webp_total:,} bytes ({webp_total / 1024:.2f} KB)")

    if jpg_total > 0:
        total_diff = jpg_total - webp_total
        total_saving_pct = (total_diff / jpg_total) * 100
        print(f"\nサイズ差: {total_diff:,} bytes ({total_diff / 1024:.2f} KB)")
        print(f"節約率: {total_saving_pct:.2f}%")

        if total_diff > 0:
            print(f"WebPの方が {total_saving_pct:.2f}% 小さい")
        elif total_diff < 0:
            print(f"JPGの方が {abs(total_saving_pct):.2f}% 小さい")
        else:
            print("サイズは等しい")

    print("\n" + "=" * 70)
    print("個別ファイル統計（サイズ比率 WebP/JPG）")
    print("=" * 70)

    print(f"\n平均圧縮率: {statistics.mean(compression_ratios):.2f}%")
    print(f"中央値圧縮率: {statistics.median(compression_ratios):.2f}%")
    print(f"最小圧縮率（WebPが一番小さい）: {min(compression_ratios):.2f}%")
    print(f"最大圧縮率（JPGが小さい場合）: {max(compression_ratios):.2f}%")

    # 分布
    smaller_webp = sum(1 for r in compression_ratios if r < 100)
    smaller_jpg = sum(1 for r in compression_ratios if r > 100)
    equal_size = sum(1 for r in compression_ratios if r == 100)

    print(f"\nWebPの方が小さい: {smaller_webp} ファイル ({smaller_webp/len(pairs)*100:.1f}%)")
    print(f"JPGの方が小さい: {smaller_jpg} ファイル ({smaller_jpg/len(pairs)*100:.1f}%)")
    print(f"サイズが等しい: {equal_size} ファイル")

    print("\n" + "=" * 70)
    print("サイズ差の詳細")
    print("=" * 70)

    print(f"\n平均サイズ差: {statistics.mean(size_differences):,.0f} bytes")
    print(f"中央値サイズ差: {statistics.median(size_differences):,.0f} bytes")
    print(f"最小サイズ差: {min(size_differences):,.0f} bytes")
    print(f"最大サイズ差: {max(size_differences):,.0f} bytes")

    # 圧縮率の分布
    print("\n" + "=" * 70)
    print("圧縮率分布")
    print("=" * 70)

    ranges = [
        (0, 50), (50, 70), (70, 80), (80, 90), (90, 95),
        (95, 100), (100, 105), (105, 110), (110, 130), (130, 150), (150, 200)
    ]

    for min_r, max_r in ranges:
        count = sum(1 for r in compression_ratios if min_r <= r < max_r)
        if count > 0:
            print(f"{min_r}% - {max_r}%: {count} ファイル ({count/len(pairs)*100:.1f}%)")

    # 200%以上
    count = sum(1 for r in compression_ratios if r >= 200)
    if count > 0:
        print(f"200%以上: {count} ファイル ({count/len(pairs)*100:.1f}%)")

    print("\n" + "=" * 70)
    print("上位10個の詳細")
    print("=" * 70)

    # サイズ差が大きい順にソートして表示
    sorted_pairs = sorted(pairs, key=lambda x: abs(x[1] - x[2]), reverse=True)[:10]

    print(f"\n{'ファイル名':<36} {'JPG(KB)':>10} {'WebP(KB)':>10} {'差(KB)':>10} {'比率':>8}")
    print("-" * 78)

    for name, jpg_size, webp_size in sorted_pairs:
        diff_kb = (jpg_size - webp_size) / 1024
        ratio = (webp_size / jpg_size) * 100 if jpg_size > 0 else 0
        print(f"{name[:35]:<36} {jpg_size/1024:>10.2f} {webp_size/1024:>10.2f} {diff_kb:>10.2f} {ratio:>7.1f}%")

if __name__ == "__main__":
    analyze_image_sizes()
