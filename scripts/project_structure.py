import os
import argparse
from pathlib import Path
from datetime import datetime


class ProjectStructureGenerator:
    def __init__(self):
        # 除外するパターン（Windows環境に最適化）
        self.ignore_patterns = {
            # Python関連
            '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.pytest_cache',
            '*.egg-info', 'dist', 'build', '.tox', '.coverage',

            # 仮想環境
            '.venv', 'venv', '.env', 'env',

            # IDE/エディタ
            '.vscode', '.idea', '*.swp', '*.swo', '*~',

            # バージョン管理
            '.git', '.gitignore', '.hg', '.svn',

            # OS固有
            '.DS_Store', 'Thumbs.db', 'desktop.ini',

            # Node.js（混在プロジェクトの場合）
            'node_modules', '.npm',

            # その他
            '*.log', '*.tmp', '.cache'
        }

        # 表示優先度の高いファイル（ソート用のみ）
        self.important_files = {
            'README.md', 'README.txt', 'requirements.txt',
            'setup.py', 'pyproject.toml', 'Dockerfile',
            'config.ini', 'alembic.ini', '.env', 'Procfile'
        }

    def should_ignore(self, path):
        """ファイル/ディレクトリを無視するかどうか判定"""
        path_name = path.name.lower()

        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                # 拡張子パターン
                if path_name.endswith(pattern[1:]):
                    return True
            elif pattern in path_name:
                return True
        return False

    def get_file_size_str(self, size):
        """ファイルサイズを読みやすい形式で返す"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size // 1024}KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size // (1024 * 1024):.1f}MB"
        else:
            return f"{size // (1024 * 1024 * 1024):.1f}GB"

    def generate_structure(self, root_path=".", max_depth=None, show_size=False):
        """プロジェクト構造を生成"""
        output_lines = []
        root = Path(root_path).resolve()

        # ヘッダー情報
        output_lines.extend([
            "=" * 60,
            f"プロジェクト構造: {root.name}",
            f"パス: {root}",
            f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ])

        def print_tree(path, prefix="", is_last=True, level=0):
            if max_depth is not None and level > max_depth:
                return

            if self.should_ignore(path):
                return

            # 現在のパスを出力
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{path.name}"

            # ファイルの場合は追加情報を表示
            if path.is_file():
                try:
                    size = path.stat().st_size
                    if show_size:
                        line += f" ({self.get_file_size_str(size)})"

                except (OSError, PermissionError):
                    line += " (アクセス不可)"

            output_lines.append(line)

            # ディレクトリの場合は中身を処理
            if path.is_dir():
                try:
                    children = [p for p in path.iterdir() if not self.should_ignore(p)]

                    # ソート: ディレクトリ優先、その後重要ファイル優先、最後にアルファベット順
                    def sort_key(x):
                        is_file = x.is_file()
                        is_important = x.name in self.important_files
                        return (is_file, not is_important, x.name.lower())

                    children.sort(key=sort_key)

                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        extension = "    " if is_last else "│   "
                        print_tree(child, prefix + extension, is_last_child, level + 1)

                except PermissionError:
                    output_lines.append(f"{prefix}    (アクセス権限なし)")

        print_tree(root)

        # フッター情報
        output_lines.extend([
            "",
            "=" * 60,
            f"除外パターン: {', '.join(sorted(self.ignore_patterns))}",
            "=" * 60
        ])

        return "\n".join(output_lines)

    def save_to_file(self, content, filename):
        """ファイルに保存"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ プロジェクト構造を '{filename}' に保存しました")
            return True
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Pythonプロジェクトの構造を出力するスクリプト"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="プロジェクトのルートパス (デフォルト: 現在のディレクトリ)"
    )
    parser.add_argument(
        "-o", "--output",
        default="project_structure.txt",
        help="出力ファイル名 (デフォルト: project_structure.txt)"
    )
    parser.add_argument(
        "-d", "--depth",
        type=int,
        help="表示する最大深度 (デフォルト: 制限なし)"
    )
    parser.add_argument(
        "--show-size",
        action="store_true",
        help="ファイルサイズを表示"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="隠しファイルも表示"
    )

    args = parser.parse_args()

    # プロジェクト構造生成器を初期化
    generator = ProjectStructureGenerator()

    # 隠しファイルを含める場合はパターンを調整
    if args.include_hidden:
        generator.ignore_patterns = {
            pattern for pattern in generator.ignore_patterns
            if not pattern.startswith('.')
        }

    # 構造を生成
    try:
        structure = generator.generate_structure(
            root_path=args.path,
            max_depth=args.depth,
            show_size=args.show_size
        )

        # ファイルに保存
        if generator.save_to_file(structure, args.output):
            print(f"📁 ファイルの場所: {os.path.abspath(args.output)}")

    except FileNotFoundError:
        print(f"❌ エラー: パス '{args.path}' が見つかりません")
    except PermissionError:
        print(f"❌ エラー: パス '{args.path}' にアクセス権限がありません")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")


def quick_structure(path=".", depth=3):
    """クイック構造表示用の関数"""
    generator = ProjectStructureGenerator()
    structure = generator.generate_structure(path, max_depth=depth, show_size=True)
    print(structure)


def save_structure(path=".", output_file="project_structure.txt", depth=None):
    """構造をファイルに保存する関数"""
    generator = ProjectStructureGenerator()
    structure = generator.generate_structure(path, max_depth=depth, show_size=True)
    return generator.save_to_file(structure, output_file)


if __name__ == "__main__":
    main()
