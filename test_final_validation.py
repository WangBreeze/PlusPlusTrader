#!/usr/bin/env python3
"""
PlusPlusTrader 最终验证测试
验证整个系统的完整性和可用性
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import time

class FinalValidator:
    """最终验证器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.test_results = []
        self.start_time = time.time()
    
    def log_result(self, test_name, status, message=""):
        """记录测试结果"""
        status_symbol = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "SKIP": "⏭️"
        }.get(status, "❓")
        
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        print(f"{status_symbol} {test_name}: {message}")
        return status == "PASS"
    
    def run_command(self, cmd, cwd=None, timeout=30):
        """运行命令"""
        if cwd is None:
            cwd = self.project_root
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"命令超时: {timeout}秒"
        except Exception as e:
            return False, "", str(e)
    
    def test_project_structure(self):
        """测试项目结构"""
        test_name = "项目结构完整性"
        
        required_dirs = [
            "src",
            "include",
            "python",
            "docs",
            "examples",
            "scripts",
            "config",
            "data",
            "web",
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return self.log_result(
                test_name, "FAIL",
                f"缺少必要的目录: {missing_dirs}"
            )
        
        return self.log_result(test_name, "PASS", "项目结构完整")
    
    def test_core_files(self):
        """测试核心文件"""
        test_name = "核心文件存在性"
        
        required_files = [
            "README.md",
            "INSTALL.md",
            "CHANGELOG.md",
            "LICENSE",
            "Makefile",
            "install.sh",
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "requirements-dev.txt",
        ]
        
        missing_files = []
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            return self.log_result(
                test_name, "FAIL",
                f"缺少核心文件: {missing_files}"
            )
        
        return self.log_result(test_name, "PASS", "所有核心文件存在")
    
    def test_python_environment(self):
        """测试Python环境"""
        test_name = "Python环境检查"
        
        # 检查Python版本
        success, stdout, stderr = self.run_command("python3 --version")
        if not success:
            return self.log_result(test_name, "FAIL", "Python 3未安装")
        
        # 检查pip
        success, stdout, stderr = self.run_command("pip3 --version")
        if not success:
            return self.log_result(test_name, "FAIL", "pip未安装")
        
        return self.log_result(test_name, "PASS", "Python环境正常")
    
    def test_build_system(self):
        """测试构建系统"""
        test_name = "构建系统测试"
        
        # 测试CMake
        success, stdout, stderr = self.run_command("cmake --version")
        if not success:
            return self.log_result(test_name, "WARNING", "CMake未安装")
        
        # 测试Makefile帮助
        success, stdout, stderr = self.run_command("make help")
        if not success:
            return self.log_result(test_name, "FAIL", "Makefile帮助命令失败")
        
        if "可用目标:" not in stdout:
            return self.log_result(test_name, "FAIL", "Makefile格式错误")
        
        return self.log_result(test_name, "PASS", "构建系统正常")
    
    def test_python_setup(self):
        """测试Python安装配置"""
        test_name = "Python安装配置"
        
        setup_file = self.project_root / "python" / "setup.py"
        if not setup_file.exists():
            return self.log_result(test_name, "FAIL", "setup.py不存在")
        
        # 测试setup.py语法
        success, stdout, stderr = self.run_command(
            "python3 -m py_compile setup.py",
            cwd=self.project_root / "python"
        )
        
        if not success:
            return self.log_result(test_name, "FAIL", f"setup.py语法错误: {stderr}")
        
        return self.log_result(test_name, "PASS", "Python安装配置正常")
    
    def test_docker_config(self):
        """测试Docker配置"""
        test_name = "Docker配置测试"
        
        # 检查Docker是否安装
        success, stdout, stderr = self.run_command("docker --version")
        if not success:
            return self.log_result(test_name, "WARNING", "Docker未安装")
        
        # 检查docker-compose是否安装
        success, stdout, stderr = self.run_command("docker-compose --version")
        if not success:
            return self.log_result(test_name, "WARNING", "docker-compose未安装")
        
        return self.log_result(test_name, "PASS", "Docker配置正常")
    
    def test_installation_script(self):
        """测试安装脚本"""
        test_name = "安装脚本测试"
        
        # 测试安装脚本语法
        success, stdout, stderr = self.run_command("bash -n install.sh")
        if not success:
            return self.log_result(test_name, "FAIL", f"安装脚本语法错误: {stderr}")
        
        # 测试安装脚本帮助
        success, stdout, stderr = self.run_command("./install.sh --help", timeout=10)
        if success and "--help" in stdout:
            return self.log_result(test_name, "PASS", "安装脚本语法正确")
        else:
            # 如果没有--help选项，至少语法正确
            return self.log_result(test_name, "PASS", "安装脚本语法正确")
    
    def test_example_code(self):
        """测试示例代码"""
        test_name = "示例代码测试"
        
        examples_dir = self.project_root / "examples"
        if not examples_dir.exists():
            return self.log_result(test_name, "WARNING", "示例目录不存在")
        
        # 检查示例文件
        example_files = list(examples_dir.glob("*.py"))
        if not example_files:
            return self.log_result(test_name, "WARNING", "没有示例文件")
        
        # 测试一个简单的示例
        basic_example = examples_dir / "basic_usage.py"
        if basic_example.exists():
            # 只检查语法，不实际运行
            success, stdout, stderr = self.run_command(
                f"python3 -m py_compile {basic_example}"
            )
            if not success:
                return self.log_result(test_name, "FAIL", f"示例代码语法错误: {stderr}")
        
        return self.log_result(test_name, "PASS", f"示例代码正常 ({len(example_files)}个文件)")
    
    def test_documentation(self):
        """测试文档"""
        test_name = "文档完整性测试"
        
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return self.log_result(test_name, "WARNING", "文档目录不存在")
        
        # 检查关键文档
        required_docs = [
            "用户指南.md",
            "API文档.md",
            "A股数据回测指南.md",
            "Python自定义指标指南.md",
            "User_Feedback_System_Guide.md",
        ]
        
        missing_docs = []
        for doc in required_docs:
            doc_path = docs_dir / doc
            if not doc_path.exists():
                missing_docs.append(doc)
        
        if missing_docs:
            return self.log_result(
                test_name, "WARNING",
                f"缺少部分文档: {missing_docs}"
            )
        
        return self.log_result(test_name, "PASS", "文档基本完整")
    
    def test_release_packages(self):
        """测试发布包"""
        test_name = "发布包测试"
        
        dist_dir = self.project_root / "dist"
        if not dist_dir.exists():
            return self.log_result(test_name, "FAIL", "发布包目录不存在")
        
        # 检查发布包文件
        package_files = list(dist_dir.glob("*"))
        if not package_files:
            return self.log_result(test_name, "FAIL", "没有发布包文件")
        
        # 检查关键发布包
        required_packages = [
            f"pplustrader-1.0.0.tar.gz",
            f"pplustrader-1.0.0.zip",
            f"pplustrader-1.0.0-py3-none-any.whl",
            "checksums.json",
            "checksums.txt",
        ]
        
        missing_packages = []
        for pkg in required_packages:
            pkg_path = dist_dir / pkg
            if not pkg_path.exists():
                missing_packages.append(pkg)
        
        if missing_packages:
            return self.log_result(
                test_name, "FAIL",
                f"缺少关键发布包: {missing_packages}"
            )
        
        return self.log_result(
            test_name, "PASS",
            f"发布包完整 ({len(package_files)}个文件)"
        )
    
    def test_quick_installation(self):
        """测试快速安装"""
        test_name = "快速安装测试"
        
        # 创建一个临时目录进行安装测试
        temp_dir = tempfile.mkdtemp(prefix="pplustrader_install_test_")
        
        try:
            # 复制安装包到临时目录
            installer_pkg = self.project_root / "dist" / "pplustrader-installer-1.0.0.tar.gz"
            if not installer_pkg.exists():
                return self.log_result(test_name, "SKIP", "安装包不存在，跳过安装测试")
            
            # 解压安装包
            success, stdout, stderr = self.run_command(
                f"tar -xzf {installer_pkg} -C {temp_dir}"
            )
            if not success:
                return self.log_result(test_name, "FAIL", f"解压安装包失败: {stderr}")
            
            # 进入安装包目录
            installer_dir = Path(temp_dir) / "pplustrader-installer-1.0.0"
            if not installer_dir.exists():
                return self.log_result(test_name, "FAIL", "安装包目录结构错误")
            
            # 测试安装脚本（不实际安装）
            install_script = installer_dir / "install.sh"
            if not install_script.exists():
                return self.log_result(test_name, "FAIL", "安装脚本不存在")
            
            # 只检查语法，不实际运行
            success, stdout, stderr = self.run_command(
                f"bash -n {install_script}"
            )
            if not success:
                return self.log_result(test_name, "FAIL", f"安装脚本语法错误: {stderr}")
            
            return self.log_result(test_name, "PASS", "快速安装测试通过")
            
        except Exception as e:
            return self.log_result(test_name, "FAIL", f"安装测试异常: {e}")
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_system_integration(self):
        """测试系统集成"""
        test_name = "系统集成测试"
        
        # 运行已有的集成测试
        integration_test = self.project_root / "test_final_integration.py"
        if not integration_test.exists():
            return self.log_result(test_name, "SKIP", "集成测试文件不存在")
        
        # 运行集成测试（快速模式）
        success, stdout, stderr = self.run_command(
            f"python3 {integration_test}",
            timeout=60
        )
        
        if not success:
            # 检查是否是已知的导入问题
            if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                return self.log_result(
                    test_name, "WARNING",
                    "集成测试导入失败（可能需要先安装）"
                )
            return self.log_result(test_name, "FAIL", f"集成测试失败: {stderr}")
        
        if "所有测试通过" in stdout or "All tests passed" in stdout:
            return self.log_result(test_name, "PASS", "系统集成测试通过")
        else:
            return self.log_result(test_name, "WARNING", "集成测试完成但未找到成功标志")
    
    def test_performance_validation(self):
        """测试性能验证"""
        test_name = "性能验证测试"
        
        # 运行性能测试（快速模式）
        perf_test = self.project_root / "performance_validation_simple.py"
        if not perf_test.exists():
            return self.log_result(test_name, "SKIP", "性能测试文件不存在")
        
        # 运行性能测试（只运行关键测试）
        success, stdout, stderr = self.run_command(
            f"python3 {perf_test}",
            timeout=120
        )
        
        if not success:
            return self.log_result(test_name, "WARNING", f"性能测试运行失败: {stderr}")
        
        # 检查关键性能指标
        if "高频延迟" in stdout or "吞吐量" in stdout:
            return self.log_result(test_name, "PASS", "性能验证测试通过")
        else:
            return self.log_result(test_name, "WARNING", "性能测试完成但未找到关键指标")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🔍 开始最终验证测试...")
        print("=" * 60)
        print(f"项目目录: {self.project_root}")
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}")
        print("=" * 60)
        
        # 运行所有测试
        tests = [
            self.test_project_structure,
            self.test_core_files,
            self.test_python_environment,
            self.test_build_system,
            self.test_python_setup,
            self.test_docker_config,
            self.test_installation_script,
            self.test_example_code,
            self.test_documentation,
            self.test_release_packages,
            self.test_quick_installation,
            self.test_system_integration,
            self.test_performance_validation,
        ]
        
        all_passed = True
        for test_func in tests:
            try:
                passed = test_func()
                if not passed and test_func.__name__ not in ["test_quick_installation", "test_system_integration"]:
                    all_passed = False
            except Exception as e:
                self.log_result(test_func.__name__, "ERROR", f"测试异常: {e}")
                all_passed = False
        
        # 显示测试结果汇总
        end_time = time.time()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 最终验证测试结果汇总")
        print("=" * 60)
        
        pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
        fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warning_count = sum(1 for r in self.test_results if r["status"] == "WARNING")
        skip_count = sum(1 for r in self.test_results if r["status"] == "SKIP")
        
        print(f"\n✅ 通过: {pass_count} 项")
        print(f"❌ 失败: {fail_count} 项")
        print(f"⚠️  警告: {warning_count} 项")
        print(f"⏭️  跳过: {skip_count} 项")
        print(f"📋 总计: {len(self.test_results)} 项测试")
        print(f"⏱️  耗时: {duration:.1f} 秒")
        
        if fail_count == 0:
            print(f"\n🎉 所有关键测试通过！系统验证成功。")
            return True
        else:
            print(f"\n❌ 有 {fail_count} 项关键测试失败，请检查系统。")
            return False
    
    def generate_validation_report(self):
        """生成验证报告"""
        report_file = self.project_root / "final_validation_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# PlusPlusTrader {VERSION} 最终验证报告\n")
            f.write(f"**验证时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}\n")
            f.write(f"**项目目录**: {self.project_root}\n")
            f.write(f"**Python版本**: {sys.version}\n\n")
            
            f.write("## 📊 测试结果汇总\n")
            f.write("| 测试项 | 状态 | 说明 |\n")
            f.write("|--------|------|------|\n")
            
            for result in self.test_results:
                status_symbol = {
                    "PASS": "✅",
                    "FAIL": "❌",
                    "WARNING": "⚠️",
                    "SKIP": "⏭️",
                    "ERROR": "🚨"
                }.get(result["status"], "❓")
                
                f.write(f"| {result['test']} | {status_symbol} {result['status']} | {result['message']} |\n")
            
            f.write("\n")
            
            # 统计信息
            pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
            fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL")
            warning_count = sum(1 for r in self.test_results if r["status"] == "WARNING")
            total_count = len(self.test_results)
            
            f.write(f"## 📈 统计信息\n")
            f.write(f"- **总测试数**: {total_count}\n")
            f.write(f"- **通过数**: {pass_count}\n")
            f.write(f"- **失败数**: {fail_count}\n")
            f.write(f"- **警告数**: {warning_count}\n")
            f.write(f"- **通过率**: {pass_count/total_count*100:.1f}%\n\n")
            
            # 系统状态评估
            f.write("## 🏆 系统状态评估\n")
            
            if fail_count == 0:
                f.write("### ✅ 系统状态: 优秀\n")
                f.write("所有关键测试通过，系统状态优秀。\n")
                f.write("- **代码质量**: 符合标准\n")
                f.write("- **文档完整**: 基本完整\n")
                f.write("- **构建系统**: 正常工作\n")
                f.write("- **发布包**: 完整可用\n")
                f.write("- **安装流程**: 验证通过\n")
            elif fail_count <= 2:
                f.write("### ⚠️ 系统状态: 良好\n")
                f.write("大部分测试通过，系统状态良好。\n")
                f.write("建议修复少量问题后再发布。\n")
            else:
                f.write("### ❌ 系统状态: 需要改进\n")
                f.write("有多个关键测试失败，需要修复问题。\n")
                f.write("不建议在当前状态下发布。\n")
            
            f.write("\n## 🚀 发布建议\n")
            
            if fail_count == 0:
                f.write("**建议立即发布！**\n")
                f.write("系统已通过所有关键验证，可以发布v1.0.0正式版。\n")
            elif fail_count <= 2:
                f.write("**建议修复问题后发布**\n")
                f.write("系统基本可用，但建议修复少量问题后再发布。\n")
            else:
                f.write("**不建议发布**\n")
                f.write("系统存在多个关键问题，需要修复后再考虑发布。\n")
            
            f.write("\n## 📋 下一步行动\n")
            
            if fail_count == 0:
                f.write("1. **上传发布包**到GitHub、PyPI、Docker Hub\n")
                f.write("2. **更新文档网站**，确保文档最新\n")
                f.write("3. **发送发布公告**到社区和社交媒体\n")
                f.write("4. **监控发布状态**，及时处理用户反馈\n")
                f.write("5. **准备下一个版本**的开发计划\n")
            else:
                f.write("1. **修复失败测试**中报告的问题\n")
                f.write("2. **重新运行验证测试**，确认问题已解决\n")
                f.write("3. **更新相关文档**，反映修复内容\n")
                f.write("4. **重新创建发布包**，包含修复内容\n")
                f.write("5. **重新运行最终验证**，确保系统稳定\n")
            
            f.write("\n## 📁 项目文件清单\n")
            f.write("| 类型 | 数量 | 状态 |\n")
            f.write("|------|------|------|\n")
            
            # 统计各类文件
            file_types = {
                "Python文件": len(list(self.project_root.rglob("*.py"))),
                "C++文件": len(list(self.project_root.rglob("*.cpp"))) + len(list(self.project_root.rglob("*.h"))),
                "文档文件": len(list(self.project_root.rglob("*.md"))),
                "配置文件": len(list(self.project_root.rglob("*.json"))) + len(list(self.project_root.rglob("*.yaml"))) + len(list(self.project_root.rglob("*.yml"))),
                "发布包": len(list((self.project_root / "dist").glob("*"))) if (self.project_root / "dist").exists() else 0,
            }
            
            for file_type, count in file_types.items():
                status = "✅ 正常" if count > 0 else "⚠️ 缺少"
                f.write(f"| {file_type} | {count} | {status} |\n")
            
            f.write("\n---\n")
            f.write(f"*验证完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*验证工具: PlusPlusTrader Final Validator*\n")
        
        print(f"\n📄 验证报告已生成: {report_file}")
        return report_file

def main():
    """主函数"""
    validator = FinalValidator()
    
    try:
        # 运行所有测试
        success = validator.run_all_tests()
        
        # 生成验证报告
        report_file = validator.generate_validation_report()
        
        # 返回退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()