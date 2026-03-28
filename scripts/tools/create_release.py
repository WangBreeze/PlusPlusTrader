#!/usr/bin/env python3
"""
PlusPlusTrader 发布工具
用于创建和管理项目发布
"""

import os
import sys
import shutil
import subprocess
import json
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

# 项目配置
PROJECT_NAME = "pplustrader"
VERSION = "1.0.0"
AUTHOR = "PlusPlusTrader Team"
LICENSE = "MIT"
DESCRIPTION = "高性能量化交易系统"

class ReleaseCreator:
    """发布创建器"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.dist_dir = self.project_root / "dist"
        self.releases_dir = self.project_root / "releases"
        self.build_dir = self.project_root / "build"
        
        # 创建目录
        self.dist_dir.mkdir(exist_ok=True)
        self.releases_dir.mkdir(exist_ok=True)
        
    def run_command(self, cmd, cwd=None):
        """运行命令"""
        if cwd is None:
            cwd = self.project_root
        
        print(f"运行命令: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"命令失败: {result.stderr}")
            return False
        
        print(f"命令输出: {result.stdout}")
        return True
    
    def get_git_info(self):
        """获取Git信息"""
        info = {
            "branch": "unknown",
            "commit": "unknown",
            "tag": "unknown",
            "clean": False
        }
        
        try:
            # 获取当前分支
            result = subprocess.run(
                "git rev-parse --abbrev-ref HEAD",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()
            
            # 获取最新提交
            result = subprocess.run(
                "git rev-parse --short HEAD",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                info["commit"] = result.stdout.strip()
            
            # 获取标签
            result = subprocess.run(
                "git describe --tags --abbrev=0 2>/dev/null || echo 'none'",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                info["tag"] = result.stdout.strip()
            
            # 检查工作区是否干净
            result = subprocess.run(
                "git status --porcelain",
                shell=True, capture_output=True, text=True
            )
            info["clean"] = result.stdout.strip() == ""
            
        except Exception as e:
            print(f"获取Git信息失败: {e}")
        
        return info
    
    def create_source_package(self):
        """创建源码包"""
        print("创建源码包...")
        
        # 包名
        package_name = f"{PROJECT_NAME}-{VERSION}"
        tar_file = self.dist_dir / f"{package_name}.tar.gz"
        zip_file = self.dist_dir / f"{package_name}.zip"
        
        # 排除的文件和目录
        exclude_patterns = [
            ".git",
            ".github",
            ".vscode",
            ".idea",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.so",
            "*.o",
            "build",
            "dist",
            "releases",
            "venv",
            ".env",
            "*.log",
            "*.tmp",
            "*.bak",
        ]
        
        # 创建tar.gz包
        print(f"创建 {tar_file}...")
        with tarfile.open(tar_file, "w:gz") as tar:
            for item in self.project_root.rglob("*"):
                # 检查是否应该排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(item.relative_to(self.project_root)):
                        should_exclude = True
                        break
                
                if should_exclude or not item.is_file():
                    continue
                
                # 添加到tar包
                arcname = package_name / item.relative_to(self.project_root)
                tar.add(item, arcname=arcname)
        
        # 创建zip包
        print(f"创建 {zip_file}...")
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in self.project_root.rglob("*"):
                # 检查是否应该排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(item.relative_to(self.project_root)):
                        should_exclude = True
                        break
                
                if should_exclude or not item.is_file():
                    continue
                
                # 添加到zip包
                arcname = package_name / item.relative_to(self.project_root)
                zipf.write(item, arcname)
        
        print(f"源码包创建完成:")
        print(f"  - {tar_file}")
        print(f"  - {zip_file}")
        
        return tar_file, zip_file
    
    def create_python_package(self):
        """创建Python包"""
        print("创建Python包...")
        
        # 进入python目录
        python_dir = self.project_root / "python"
        
        # 构建wheel包
        print("构建wheel包...")
        if not self.run_command("python setup.py bdist_wheel", cwd=python_dir):
            return None
        
        # 构建源码包
        print("构建源码包...")
        if not self.run_command("python setup.py sdist", cwd=python_dir):
            return None
        
        # 移动文件到dist目录
        dist_files = []
        for pattern in ["*.whl", "*.tar.gz"]:
            for file in (python_dir / "dist").glob(pattern):
                dest = self.dist_dir / file.name
                shutil.move(file, dest)
                dist_files.append(dest)
                print(f"移动: {file.name} -> {dest}")
        
        return dist_files
    
    def create_docker_image(self):
        """创建Docker镜像"""
        print("创建Docker镜像...")
        
        # 构建镜像
        if not self.run_command(f"docker build -t {PROJECT_NAME}:{VERSION} ."):
            return None
        
        # 标记为latest
        self.run_command(f"docker tag {PROJECT_NAME}:{VERSION} {PROJECT_NAME}:latest")
        
        # 保存为tar文件
        docker_file = self.dist_dir / f"{PROJECT_NAME}-{VERSION}.docker.tar"
        print(f"保存Docker镜像: {docker_file}")
        
        if not self.run_command(f"docker save {PROJECT_NAME}:{VERSION} -o {docker_file}"):
            return None
        
        return docker_file
    
    def create_installer_package(self):
        """创建安装包"""
        print("创建安装包...")
        
        # 包名
        package_name = f"{PROJECT_NAME}-installer-{VERSION}"
        installer_dir = self.dist_dir / package_name
        
        # 创建安装包目录
        if installer_dir.exists():
            shutil.rmtree(installer_dir)
        installer_dir.mkdir()
        
        # 复制文件
        files_to_copy = [
            ("README.md", "README.md"),
            ("INSTALL.md", "INSTALL.md"),
            ("CHANGELOG.md", "CHANGELOG.md"),
            ("LICENSE", "LICENSE"),
            ("requirements.txt", "requirements.txt"),
            ("install.sh", "install.sh"),
            ("Dockerfile", "Dockerfile"),
            ("docker-compose.yml", "docker-compose.yml"),
            ("Makefile", "Makefile"),
        ]
        
        for src, dst in files_to_copy:
            src_path = self.project_root / src
            if src_path.exists():
                shutil.copy2(src_path, installer_dir / dst)
                print(f"复制: {src} -> {dst}")
        
        # 复制脚本
        scripts_dir = installer_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        if (self.project_root / "scripts").exists():
            shutil.copytree(
                self.project_root / "scripts",
                scripts_dir,
                dirs_exist_ok=True
            )
        
        # 复制示例
        examples_dir = installer_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        if (self.project_root / "examples").exists():
            shutil.copytree(
                self.project_root / "examples",
                examples_dir,
                dirs_exist_ok=True
            )
        
        # 创建安装脚本
        self._create_installer_script(installer_dir)
        
        # 创建tar包
        tar_file = self.dist_dir / f"{package_name}.tar.gz"
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(installer_dir, arcname=package_name)
        
        # 清理
        shutil.rmtree(installer_dir)
        
        print(f"安装包创建完成: {tar_file}")
        return tar_file
    
    def _create_installer_script(self, installer_dir):
        """创建安装脚本"""
        script_content = """#!/bin/bash
# PlusPlusTrader 安装脚本
# 版本: {version}

set -e

# 颜色定义
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

# 日志函数
log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $1"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# 显示欢迎信息
show_welcome() {{
    echo -e "${{GREEN}}"
    echo "================================================"
    echo "        PlusPlusTrader 安装程序"
    echo "================================================"
    echo -e "${{NC}}"
    echo "版本: {version}"
    echo "项目: {project_name}"
    echo "作者: {author}"
    echo "许可证: {license}"
    echo ""
}}

# 主函数
main() {{
    show_welcome
    
    log_info "开始安装 PlusPlusTrader..."
    
    # 检查系统要求
    log_info "检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "需要Python 3.8+，请先安装Python"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "需要pip，请先安装pip"
        exit 1
    fi
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip3 install -r requirements.txt
    
    # 运行安装脚本
    if [ -f "install.sh" ]; then
        log_info "运行安装脚本..."
        chmod +x install.sh
        ./install.sh
    else
        log_info "使用Makefile安装..."
        make build
        make install-user
    fi
    
    # 验证安装
    log_info "验证安装..."
    if python3 -c "import pplustrader; print(f'✅ PlusPlusTrader版本: {{pplustrader.get_version()}}')"; then
        log_success "安装成功！"
        echo ""
        echo "🚀 快速开始:"
        echo "  运行示例: python3 examples/basic_usage.py"
        echo "  启动Web界面: python3 web/dashboard.py"
        echo ""
        echo "📚 文档:"
        echo "  查看 README.md 获取更多信息"
    else
        log_error "安装验证失败"
        exit 1
    fi
}}

# 运行主函数
main "$@"
""".format(
            version=VERSION,
            project_name=PROJECT_NAME,
            author=AUTHOR,
            license=LICENSE
        )
        
        script_file = installer_dir / "install.sh"
        with open(script_file, "w") as f:
            f.write(script_content)
        
        # 设置执行权限
        script_file.chmod(0o755)
    
    def create_release_notes(self):
        """创建发布说明"""
        print("创建发布说明...")
        
        # 获取Git信息
        git_info = self.get_git_info()
        
        # 创建发布说明
        notes = {
            "project": PROJECT_NAME,
            "version": VERSION,
            "release_date": datetime.now().isoformat(),
            "git_info": git_info,
            "description": DESCRIPTION,
            "author": AUTHOR,
            "license": LICENSE,
            "files": [],
            "checksums": {}
        }
        
        # 保存发布说明
        notes_file = self.releases_dir / f"release-{VERSION}.json"
        with open(notes_file, "w") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        
        print(f"发布说明创建完成: {notes_file}")
        return notes_file
    
    def calculate_checksums(self):
        """计算文件校验和"""
        print("计算文件校验和...")
        
        import hashlib
        
        checksums = {}
        
        for file in self.dist_dir.glob("*"):
            if file.is_file():
                # 计算MD5
                with open(file, "rb") as f:
                    md5_hash = hashlib.md5()
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                    md5 = md5_hash.hexdigest()
                
                # 计算SHA256
                with open(file, "rb") as f:
                    sha256_hash = hashlib.sha256()
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                    sha256 = sha256_hash.hexdigest()
                
                checksums[file.name] = {
                    "md5": md5,
                    "sha256": sha256,
                    "size": file.stat().st_size
                }
        
        # 保存校验和文件
        checksums_file = self.dist_dir / "checksums.json"
        with open(checksums_file, "w") as f:
            json.dump(checksums, f, indent=2)
        
        # 创建文本格式的校验和文件
        text_file = self.dist_dir / "checksums.txt"
        with open(text_file, "w") as f:
            f.write(f"PlusPlusTrader {VERSION} 文件校验和\n")
            f.write("=" * 50 + "\n\n")
            
            for filename, checksum in checksums.items():
                f.write(f"文件: {filename}\n")
                f.write(f"大小: {checksum['size']} 字节\n")
                f.write(f"MD5: {checksum['md5']}\n")
                f.write(f"SHA256: {checksum['sha256']}\n")
                f.write("-" * 50 + "\n")
        
        print(f"校验和文件创建完成:")
        print(f"  - {checksums_file}")
        print(f"  - {text_file}")
        
        return checksums_file, text_file
    
    def create_full_release(self):
        """创建完整发布"""
        print("=" * 60)
        print(f"创建 PlusPlusTrader {VERSION} 发布包")
        print("=" * 60)
        
        # 获取Git信息
        git_info = self.get_git_info()
        print(f"Git信息: {git_info}")
        
        if not git_info["clean"]:
            print("⚠️  警告: Git工作区不干净")
            response = input("是否继续? (y/N): ")
            if response.lower() != "y":
                print("发布取消")
                return False
        
        # 清理dist目录
        print("清理dist目录...")
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir()
        
        # 创建各种包
        packages = []
        
        # 源码包
        print("\n1. 创建源码包...")
        source_packages = self.create_source_package()
        if source_packages:
            packages.extend(source_packages)
        
        # Python包
        print("\n2. 创建Python包...")
        python_packages = self.create_python_package()
        if python_packages:
            packages.extend(python_packages)
        
        # Docker镜像
        print("\n3. 创建Docker镜像...")
        docker_package = self.create_docker_image()
        if docker_package:
            packages.append(docker_package)
        
        # 安装包
        print("\n4. 创建安装包...")
        installer_package = self.create_installer_package()
        if installer_package:
            packages.append(installer_package)
        
        # 计算校验和
        print("\n5. 计算文件校验和...")
        self.calculate_checksums()
        
        # 创建发布说明
        print("\n6. 创建发布说明...")
        self.create_release_notes()
        
        # 显示结果
        print("\n" + "=" * 60)
        print("发布包创建完成!")
        print("=" * 60)
        
        print(f"\n创建的文件 ({len(packages)}个):")
        for package in packages:
            size_mb = package.stat().st_size / (1024 * 1024)
            print(f"  - {package.name} ({size_mb:.2f} MB)")
        
        total_size = sum(p.stat().st_size for p in packages) / (1024 * 1024)
        print(f"\n总大小: {total_size:.2f} MB")
        
        print(f"\n文件位置: {self.dist_dir}")
        print(f"发布说明: {self.releases_dir}/release-{VERSION}.json")
        
        print("\n下一步:")
        print("  1. 测试发布包")
        print("  2. 创建GitHub Release")
        print("  3. 上传文件")
        print("  4. 发布公告")
        
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PlusPlusTrader 发布工具")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--source", action="store_true", help="创建源码包")
    parser.add_argument("--python", action="store_true", help="创建Python包")
    parser.add_argument("--docker", action="store_true", help="创建Docker镜像")
    parser.add_argument("--installer", action="store_true", help="创建安装包")
    parser.add_argument("--all", action="store_true", help="创建所有包（默认）")
    parser.add_argument("--checksums", action="store_true", help="计算校验和")
    parser.add_argument("--notes", action="store_true", help="创建发布说明")
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，默认创建所有包
    if not any([args.source, args.python, args.docker, args.installer, args.checksums, args.notes]):
        args.all = True
    
    creator = ReleaseCreator()
    
    try:
        if args.all:
            # 创建完整发布
            success = creator.create_full_release()
            if not success:
                sys.exit(1)
        else:
            # 创建指定的包
            if args.source:
                creator.create_source_package()
            if args.python:
                creator.create_python_package()
            if args.docker:
                creator.create_docker_image()
            if args.installer:
                creator.create_installer_package()
            if args.checksums:
                creator.calculate_checksums()
            if args.notes:
                creator.create_release_notes()
        
        print("\n🎉 发布工具执行完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()