import argparse
import json
import sys
from pathlib import Path


def minify_json_file(input_path, output_path=None):
    """
    JSONファイルを一行にまとめる関数

    Args:
        input_path (str): 入力JSONファイルのパス
        output_path (str, optional): 出力ファイルのパス。Noneの場合は入力ファイルを上書き
    """
    try:
        # JSONファイルを読み込み
        with open(input_path, encoding='utf-8') as file:
            data = json.load(file)

        # JSONを一行にまとめる（separatorsでスペースを削除）
        minified_json = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

        # 出力パスが指定されていない場合は入力ファイルを上書き
        if output_path is None:
            output_path = input_path

        # ファイルに保存
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(minified_json)

        print(f"成功: {input_path} を一行にまとめました")
        if output_path != input_path:
            print(f"出力先: {output_path}")

    except FileNotFoundError:
        print(f"エラー: ファイル '{input_path}' が見つかりません", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"エラー: JSONファイルの解析に失敗しました - {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"エラー: 処理中にエラーが発生しました - {e}", file=sys.stderr)
        return False

    return True


def get_file_path_interactive():
    while True:
        input_path = input("入力JSONファイルのパスを入力してください: ").strip()

        if not input_path:
            print("ファイルパスが入力されていません。もう一度入力してください。")
            continue

        # ファイル拡張子のチェック
        if not input_path.lower().endswith('.json'):
            print("警告: ファイル拡張子が .json ではありません。続行しますか？ (y/n): ", end="")
            if input().strip().lower() not in ['y', 'yes', 'はい']:
                continue

        # ファイルの存在確認
        if not Path(input_path).exists():
            print(f"エラー: ファイル '{input_path}' が見つかりません。もう一度入力してください。")
            continue

        return input_path


def get_output_path_interactive(input_path):
    """対話的に出力パスを取得する関数"""
    print(f"\n出力先の設定:")
    print("1. 入力ファイルを上書きする")
    print("2. 別のファイルに出力する")

    while True:
        choice = input("選択してください (1 または 2): ").strip()

        if choice == '1':
            return None  # 入力ファイルを上書き
        elif choice == '2':
            while True:
                output_path = input("出力ファイルのパスを入力してください: ").strip()
                if not output_path:
                    print("ファイルパスが入力されていません。もう一度入力してください。")
                    continue

                # 出力ファイルが既に存在する場合の確認
                if Path(output_path).exists():
                    print(f"ファイル '{output_path}' は既に存在します。上書きしますか？ (y/n): ", end="")
                    if input().strip().lower() not in ['y', 'yes', 'はい']:
                        continue

                return output_path
        else:
            print("1 または 2 を入力してください。")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="JSONファイルを一行にまとめるスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python json_minifier.py                           # 対話的にファイルパスを指定
  python json_minifier.py input.json               # コマンドライン引数で指定
  python json_minifier.py input.json -o output.json
  python json_minifier.py data.json --output minified_data.json
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',  # オプショナルな位置引数
        help='入力JSONファイルのパス（省略可能）'
    )

    parser.add_argument(
        '-o', '--output',
        help='出力ファイルのパス（指定しない場合は入力ファイルを上書き）'
    )

    args = parser.parse_args()

    # 入力ファイルパスの取得
    if args.input_file:
        # コマンドライン引数で指定された場合
        input_path = args.input_file
        output_path = args.output

        # 入力ファイルの存在確認
        if not Path(input_path).exists():
            print(f"エラー: ファイル '{input_path}' が見つかりません", file=sys.stderr)
            sys.exit(1)
    else:
        # 対話的にファイルパスを取得
        print("=== JSONファイルMinifyツール ===")
        input_path = get_file_path_interactive()
        output_path = get_output_path_interactive(input_path)

    print(f"\n処理中...")
    success = minify_json_file(input_path, output_path)

    if not success:
        sys.exit(1)

    print("処理が完了しました。")


if __name__ == "__main__":
    main()