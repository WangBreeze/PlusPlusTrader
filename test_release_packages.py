#!/usr/bin/env python3
"""
PlusPlusTrader 发布包验证测试
验证所有发布包的完整性和可用性
"""

import os
import sys
import tarfile
import zipfile
import json
import hashlib
import tempfile
import shutil
from pathlib import Path

# 项目配置
PROJECT_NAME = "pplustrader"
VERSION = "1.0.0"
DIST_DIR = Path("dist")

class ReleasePackageTester:
    """发布包测试器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.dist_dir = self.project_root / DIST_DIR
        self.test_results = []
        
    def log_result(self, test_name, status, message=""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        self.test_results.append(result)
        
        # 打印结果
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
        
        return status == "PASS"
    
    def test_dist_directory_exists(self):
        """测试dist目录是否存在"""
        test_name = "dist目录存在性检查"
        
        if not self.dist_dir.exists():
            return self.log_result(test_name, "FAIL", f"dist目录不存在: {self.dist_dir}")
        
        files = list(self.dist_dir.glob("*"))
        if not files:
            return self.log_result(test_name, "FAIL", "dist目录为空")
        
        return self.log_result(test_name, "PASS", f"找到 {len(files)} 个文件")
    
    def test_source_packages(self):
        """测试源码包"""
        test_name = "源码包完整性检查"
        
        # 检查tar.gz包
        tar_file = self.dist_dir / f"{PROJECT_NAME}-{VERSION}.tar.gz"
        if not tar_file.exists():
            return self.log_result(test_name, "FAIL", f"tar.gz包不存在: {tar_file.name}")
        
        # 检查zip包
        zip_file = self.dist_dir / f"{PROJECT_NAME}-{VERSION}.zip"
        if not zip_file.exists():
            return self.log_result(test_name, "FAIL", f"zip包不存在: {zip_file.name}")
        
        # 验证tar.gz包内容
        try:
            with tarfile.open(tar_file, "r:gz") as tar:
                members = tar.getmembers()
                file_count = len([m for m in members if m.isfile()])
                dir_count = len([m for m in members if m.isdir()])
                
                # 检查关键文件
                required_files = [
                    "README.md",
                    "INSTALL.md",
                    "CHANGELOG.md",
                    "LICENSE",
                    "requirements.txt",
                    "install.sh",
                    "Dockerfile",
                    "Makefile",
                ]
                
                missing_files = []
                tar_names = [m.name for m in members]
                
                for req_file in required_files:
                    # 检查文件是否存在（考虑目录前缀）
                    found = any(req_file in name for name in tar_names)
                    if not found:
                        missing_files.append(req_file)
                
                if missing_files:
                    return self.log_result(
                        test_name, "FAIL",
                        f"tar.gz包缺少必要文件: {missing_files}"
                    )
                
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"tar.gz包验证失败: {e}")
        
        # 验证zip包内容
        try:
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                members = zipf.namelist()
                file_count = len([m for m in members if not m.endswith('/')])
                
                # 检查关键文件
                missing_files = []
                for req_file in required_files:
                    found = any(req_file in name for name in members)
                    if not found:
                        missing_files.append(req_file)
                
                if missing_files:
                    return self.log_result(
                        test_name, "FAIL",
                        f"zip包缺少必要文件: {missing_files}"
                    )
                
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"zip包验证失败: {e}")
        
        return self.log_result(
            test_name, "PASS",
            f"源码包验证通过: {tar_file.name} ({file_count}个文件), {zip_file.name}"
        )
    
    def test_checksum_files(self):
        """测试校验和文件"""
        test_name = "校验和文件检查"
        
        checksum_json = self.dist_dir / "checksums.json"
        checksum_txt = self.dist_dir / "checksums.txt"
        
        if not checksum_json.exists():
            return self.log_result(test_name, "FAIL", f"JSON校验和文件不存在: {checksum_json.name}")
        
        if not checksum_txt.exists():
            return self.log_result(test_name, "FAIL", f"文本校验和文件不存在: {checksum_txt.name}")
        
        # 验证JSON格式
        try:
            with open(checksum_json, 'r') as f:
                checksums = json.load(f)
            
            if not isinstance(checksums, dict):
                return self.log_result(test_name, "FAIL", "JSON校验和文件格式错误")
            
            # 检查关键文件的校验和
            expected_files = [
                f"{PROJECT_NAME}-{VERSION}.tar.gz",
                f"{PROJECT_NAME}-{VERSION}.zip",
            ]
            
            missing_checksums = []
            for expected_file in expected_files:
                if expected_file not in checksums:
                    missing_checksums.append(expected_file)
                else:
                    file_info = checksums[expected_file]
                    required_keys = ["size", "md5", "sha256"]
                    for key in required_keys:
                        if key not in file_info:
                            missing_checksums.append(f"{expected_file}.{key}")
            
            if missing_checksums:
                return self.log_result(
                    test_name, "FAIL",
                    f"校验和文件缺少信息: {missing_checksums}"
                )
            
        except json.JSONDecodeError as e:
            return self.log_result(test_name, "FAIL", f"JSON校验和文件解析失败: {e}")
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"校验和文件验证失败: {e}")
        
        # 验证文本格式
        try:
            with open(checksum_txt, 'r') as f:
                content = f.read()
            
            if f"PlusPlusTrader {VERSION}" not in content:
                return self.log_result(test_name, "FAIL", "文本校验和文件格式错误")
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"文本校验和文件读取失败: {e}")
        
        return self.log_result(
            test_name, "PASS",
            f"校验和文件验证通过: {checksum_json.name}, {checksum_txt.name}"
        )
    
    def test_checksum_verification(self):
        """测试校验和验证"""
        test_name = "校验和验证检查"
        
        # 读取校验和文件
        checksum_json = self.dist_dir / "checksums.json"
        try:
            with open(checksum_json, 'r') as f:
                checksums = json.load(f)
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"无法读取校验和文件: {e}")
        
        # 验证每个文件的校验和
        verification_results = []
        
        for filename, expected_checksum in checksums.items():
            filepath = self.dist_dir / filename
            
            if not filepath.exists():
                verification_results.append(f"{filename}: 文件不存在")
                continue
            
            # 计算MD5
            try:
                with open(filepath, 'rb') as f:
                    md5_hash = hashlib.md5()
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                    actual_md5 = md5_hash.hexdigest()
            except Exception as e:
                verification_results.append(f"{filename}: MD5计算失败 - {e}")
                continue
            
            # 计算SHA256
            try:
                with open(filepath, 'rb') as f:
                    sha256_hash = hashlib.sha256()
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                    actual_sha256 = sha256_hash.hexdigest()
            except Exception as e:
                verification_results.append(f"{filename}: SHA256计算失败 - {e}")
                continue
            
            # 验证校验和
            if actual_md5 != expected_checksum["md5"]:
                verification_results.append(f"{filename}: MD5不匹配")
            
            if actual_sha256 != expected_checksum["sha256"]:
                verification_results.append(f"{filename}: SHA256不匹配")
            
            # 验证文件大小
            actual_size = filepath.stat().st_size
            if actual_size != expected_checksum["size"]:
                verification_results.append(f"{filename}: 文件大小不匹配")
        
        if verification_results:
            return self.log_result(
                test_name, "FAIL",
                f"校验和验证失败: {verification_results}"
            )
        
        return self.log_result(
            test_name, "PASS",
            f"校验和验证通过: 验证了 {len(checksums)} 个文件"
        )
    
    def test_installer_package(self):
        """测试安装包"""
        test_name = "安装包完整性检查"
        
        installer_file = self.dist_dir / f"{PROJECT_NAME}-installer-{VERSION}.tar.gz"
        
        if not installer_file.exists():
            return self.log_result(test_name, "FAIL", f"安装包不存在: {installer_file.name}")
        
        # 临时解压安装包
        temp_dir = tempfile.mkdtemp(prefix="pplustrader_test_")
        
        try:
            # 解压安装包
            with tarfile.open(installer_file, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # 检查安装包内容
            installer_dir = Path(temp_dir) / f"{PROJECT_NAME}-installer-{VERSION}"
            
            if not installer_dir.exists():
                return self.log_result(test_name, "FAIL", "安装包解压后目录结构错误")
            
            # 检查必要文件
            required_files = [
                "README.md",
                "INSTALL.md",
                "CHANGELOG.md",
                "LICENSE",
                "requirements.txt",
                "install.sh",
                "Dockerfile",
                "docker-compose.yml",
                "Makefile",
                "RELEASE_CHECKLIST.md",
                "RELEASE_ANNOUNCEMENT.md",
            ]
            
            missing_files = []
            for req_file in required_files:
                if not (installer_dir / req_file).exists():
                    missing_files.append(req_file)
            
            if missing_files:
                return self.log_result(
                    test_name, "FAIL",
                    f"安装包缺少必要文件: {missing_files}"
                )
            
            # 检查脚本目录
            scripts_dir = installer_dir / "scripts"
            if not scripts_dir.exists():
                return self.log_result(test_name, "FAIL", "安装包缺少scripts目录")
            
            # 检查示例目录
            examples_dir = installer_dir / "examples"
            if not examples_dir.exists():
                return self.log_result(test_name, "FAIL", "安装包缺少examples目录")
            
            # 检查安装脚本权限
            install_script = installer_dir / "install.sh"
            if not os.access(install_script, os.X_OK):
                # 尝试设置执行权限
                install_script.chmod(0o755)
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"安装包验证失败: {e}")
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return self.log_result(
            test_name, "PASS",
            f"安装包验证通过: {installer_file.name}"
        )
    
    def test_install_script(self):
        """测试安装脚本"""
        test_name = "安装脚本语法检查"
        
        install_script = self.project_root / "install.sh"
        
        if not install_script.exists():
            return self.log_result(test_name, "FAIL", "安装脚本不存在")
        
        # 检查脚本语法
        try:
            import subprocess
            result = subprocess.run(
                ["bash", "-n", str(install_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return self.log_result(
                    test_name, "FAIL",
                    f"安装脚本语法错误: {result.stderr}"
                )
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"安装脚本检查失败: {e}")
        
        return self.log_result(test_name, "PASS", "安装脚本语法正确")
    
    def test_makefile(self):
        """测试Makefile"""
        test_name = "Makefile语法检查"
        
        makefile = self.project_root / "Makefile"
        
        if not makefile.exists():
            return self.log_result(test_name, "FAIL", "Makefile不存在")
        
        # 检查Makefile语法
        try:
            import subprocess
            result = subprocess.run(
                ["make", "-n", "-f", str(makefile), "help"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return self.log_result(
                    test_name, "FAIL",
                    f"Makefile语法错误: {result.stderr}"
                )
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"Makefile检查失败: {e}")
        
        return self.log_result(test_name, "PASS", "Makefile语法正确")
    
    def test_docker_config(self):
        """测试Docker配置"""
        test_name = "Docker配置检查"
        
        dockerfile = self.project_root / "Dockerfile"
        docker_compose = self.project_root / "docker-compose.yml"
        
        if not dockerfile.exists():
            return self.log_result(test_name, "FAIL", "Dockerfile不存在")
        
        if not docker_compose.exists():
            return self.log_result(test_name, "FAIL", "docker-compose.yml不存在")
        
        # 检查Dockerfile基本语法
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            # 检查必要的指令
            required_instructions = ["FROM", "WORKDIR", "COPY", "RUN"]
            missing_instructions = []
            
            for instruction in required_instructions:
                if instruction not in content:
                    missing_instructions.append(instruction)
            
            if missing_instructions:
                return self.log_result(
                    test_name, "FAIL",
                    f"Dockerfile缺少必要指令: {missing_instructions}"
                )
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"Dockerfile检查失败: {e}")
        
        # 检查docker-compose.yml基本语法
        try:
            with open(docker_compose, 'r') as f:
                content = f.read()
            
            # 检查必要的服务定义
            if "services:" not in content:
                return self.log_result(test_name, "FAIL", "docker-compose.yml缺少services定义")
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"docker-compose.yml检查失败: {e}")
        
        return self.log_result(test_name, "PASS", "Docker配置检查通过")
    
    def test_release_documents(self):
        """测试发布文档"""
        test_name = "发布文档检查"
        
        required_docs = [
            "RELEASE_CHECKLIST.md",
            "RELEASE_ANNOUNCEMENT.md",
            "CHANGELOG.md",
            "README.md",
            "INSTALL.md",
        ]
        
        missing_docs = []
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)
        
        if missing_docs:
            return self.log_result(
                test_name, "FAIL",
                f"缺少发布文档: {missing_docs}"
            )
        
        # 检查CHANGELOG.md中的版本号
        try:
            changelog_path = self.project_root / "CHANGELOG.md"
            with open(changelog_path, 'r') as f:
                changelog_content = f.read()
            
            if f"## {VERSION}" not in changelog_content:
                return self.log_result(
                    test_name, "WARNING",
                    f"CHANGELOG.md中未找到版本 {VERSION}"
                )
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"发布文档检查失败: {e}")
        
        return self.log_result(test_name, "PASS", "发布文档检查通过")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🔍 开始发布包验证测试...")
        print("=" * 60)
        
        # 运行所有测试
        tests = [
            self.test_dist_directory_exists,
            self.test_source_packages,
            self.test_checksum_files,
            self.test_checksum_verification,
            self.test_installer_package,
            self.test_install_script,
            self.test_makefile,
            self.test_docker_config,
            self.test_release_documents,
        ]
        
        all_passed = True
        for test_func in tests:
            try:
                passed = test_func()
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_result(test_func.__name__, "ERROR", f"测试异常: {e}")
                all_passed = False
        
        # 显示测试结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
        fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warning_count = sum(1 for r in self.test_results if r["status"] == "WARNING")
        
        print(f"\n✅ 通过: {pass_count} 项")
        print(f"❌ 失败: {fail_count} 项")
        print(f"⚠️  警告: {warning_count} 项")
        print(f"📋 总计: {len(self.test_results)} 项测试")
        
        if fail_count == 0:
            print(f"\n🎉 所有测试通过！发布包验证成功。")
            return True
        else:
            print(f"\n❌ 有 {fail_count} 项测试失败，请检查发布包。")
            return False
    
    def generate_test_report(self):
        """生成测试报告"""
        report_file = self.project_root / "release_validation_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# PlusPlusTrader {VERSION} 发布包验证报告\n")
            f.write(f"**测试时间**: {self._get_timestamp()}\n")
            f.write(f"**测试环境**: Python {sys.version}\n\n")
            
            f.write("## 📊 测试结果汇总\n")
            f.write("| 测试项 | 状态 | 说明 |\n")
            f.write("|--------|------|------|\n")
            
            for result in self.test_results:
                status_symbol = {
                    "PASS": "✅",
                    "FAIL": "❌",
                    "WARNING": "⚠️",
                    "ERROR": "🚨"
                }.get(result["status"], "❓")
                
                f.write(f"| {result['test']} | {status_symbol} {result['status']} | {result['message']} |\n")
            
            f.write("\n")
            
            # 统计信息
            pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
            fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL")
            total_count = len(self.test_results)
            
            f.write(f"## 📈 统计信息\n")
            f.write(f"- **总测试数**: {total_count}\n")
            f.write(f"- **通过数**: {pass_count}\n")
            f.write(f"- **失败数**: {fail_count}\n")
            f.write(f"- **通过率**: {pass_count/total_count*100:.1f}%\n\n")
            
            if fail_count == 0:
                f.write("## 🎉 验证结论\n")
                f.write("**所有测试通过！发布包验证成功。**\n")
                f.write("发布包符合质量标准，可以发布。\n")
            else:
                f.write("## ❌ 验证结论\n")
                f.write("**有测试失败，发布包需要修复。**\n")
                f.write("请检查失败的测试项，修复问题后重新测试。\n")
            
            f.write("\n## 📁 发布的文件\n")
            f.write("| 文件名 | 大小 | 类型 |\n")
            f.write("|--------|------|------|\n")
            
            for file in self.dist_dir.glob("*"):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    f.write(f"| {file.name} | {size_mb:.2f} MB | 发布包 |\n")
        
        print(f"\n📄 测试报告已生成: {report_file}")
        return report_file
    
    def _get_timestamp(self):
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    tester = ReleasePackageTester()
    
    try:
        # 运行所有测试
        success = tester.run_all_tests()
        
        # 生成测试报告
        report_file = tester.generate_test_report()
        
        # 返回退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()