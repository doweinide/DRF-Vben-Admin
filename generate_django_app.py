import os
import argparse

# 子模块文件夹，常用于组织 app 的业务逻辑
BASE_SUBDIRS = [
    "serializers", "views",
    "services", "permissions", "utils", "tests", "migrations"
]
# 在模块添加/删除时跳过的目录（如 migrations 不添加业务模块）
EXCLUDED_MODEL_DIRS = ["migrations", "tests"]

# 应用初始化时默认创建的基本文件
BASIC_FILES = [
    "models.py", "admin.py", "urls.py", "__init__.py"
]

# 🧠 工具函数：将 snake_case 转为 CamelCase
def snake_to_camel(snake):
    return ''.join(word.capitalize() for word in snake.split('_'))

# 🧱 生成 apps.py 的内容
def create_apps_py(app_name):
    class_name = snake_to_camel(app_name) + "Config"
    return f"""from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
"""

# 🏗️ 创建增强版 Django App
def create_advanced_app(app_name):
    if os.path.exists(app_name):
        print(f"⚠️ App '{app_name}' already exists.")
        return

    os.makedirs(app_name)
    print(f"📁 Created app folder: {app_name}")

    # 创建基础 Python 文件
    for filename in BASIC_FILES:
        path = os.path.join(app_name, filename)
        open(path, "w").close()
        print(f"📝 Created file: {filename}")

    # 写入 apps.py 内容
    apps_path = os.path.join(app_name, "apps.py")
    with open(apps_path, "w") as f:
        f.write(create_apps_py(app_name))
    print(f"📝 Created file: apps.py with AppConfig class")

    # 创建子模块文件夹和 __init__.py
    for subdir in BASE_SUBDIRS:
        path = os.path.join(app_name, subdir)
        os.makedirs(path, exist_ok=True)
        open(os.path.join(path, "__init__.py"), "w").close()
        print(f"📂 Created folder: {subdir}/")

    print(f"\n✅ App '{app_name}' created with enhanced structure!\n")

# 🛠️ 添加一个或多个模块文件（如 role.py）到每个已存在的子目录中
def create_model_files(app_name, model_names):
    if not os.path.exists(app_name):
        print(f"❌ App '{app_name}' does not exist.")
        return

    for subdir in BASE_SUBDIRS:
        if subdir in EXCLUDED_MODEL_DIRS:
            continue  # ⛔ 跳过不适合放模块的目录

        subdir_path = os.path.join(app_name, subdir)
        if os.path.isdir(subdir_path):
            for model_name in model_names:
                file_path = os.path.join(subdir_path, f"{model_name}.py")
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        f.write(f"# {model_name.capitalize()} logic for {subdir}\n")
                    print(f"✅ Created: {subdir}/{model_name}.py")
                else:
                    print(f"⚠️ Already exists: {subdir}/{model_name}.py")
        else:
            print(f"⏩ Skipped missing folder: {subdir}/")
# 🗑️ 删除指定模块文件（如 serializers/role.py）
def delete_model_files(app_name, model_names):
    if not os.path.exists(app_name):
        print(f"❌ App '{app_name}' does not exist.")
        return

    for subdir in BASE_SUBDIRS:
        if subdir in EXCLUDED_MODEL_DIRS:
            continue  # ⛔ 同样跳过不相关的目录

        subdir_path = os.path.join(app_name, subdir)
        if os.path.isdir(subdir_path):
            for model_name in model_names:
                file_path = os.path.join(subdir_path, f"{model_name}.py")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Deleted: {subdir}/{model_name}.py")
                else:
                    print(f"⚠️ Not found: {subdir}/{model_name}.py")

# 🎮 命令行入口
def main():
    parser = argparse.ArgumentParser(description="Django App Generator")
    subparsers = parser.add_subparsers(dest="command")

    # startapp 命令：创建一个增强结构的 Django App
    createapp_parser = subparsers.add_parser("startapp", help="Create an enhanced Django app structure")
    createapp_parser.add_argument("app_name", type=str, help="Name of the app to create")

    # startmodel 命令：为现有 App 添加多个模块文件（支持批量）
    createmodel_parser = subparsers.add_parser("startmodel", help="Add model/module files to subfolders")
    createmodel_parser.add_argument("app_name", type=str, help="Target app name")
    createmodel_parser.add_argument("model_names", nargs="+", help="One or more module names")

    # deletemodel 命令：删除指定模块文件
    deletemodel_parser = subparsers.add_parser("deletemodel", help="Delete model/module files from subfolders")
    deletemodel_parser.add_argument("app_name", type=str, help="Target app name")
    deletemodel_parser.add_argument("model_names", nargs="+", help="One or more module names to delete")

    # 🧠 解析并执行命令
    args = parser.parse_args()

    if args.command == "startapp":
        create_advanced_app(args.app_name)
    elif args.command == "startmodel":
        create_model_files(args.app_name, args.model_names)
    elif args.command == "deletemodel":
        delete_model_files(args.app_name, args.model_names)
    else:
        parser.print_help()

# 🚀 主程序入口
if __name__ == "__main__":
    main()
