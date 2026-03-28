#!/usr/bin/env python3
"""
PlusPlusTrader Python包安装脚本
"""

import os
import sys
import platform
import subprocess
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from pathlib import Path

# 项目信息
PACKAGE_NAME = "pplustrader"
VERSION = "1.0.0"
DESCRIPTION = "高性能量化交易系统"
LONG_DESCRIPTION = """
PlusPlusTrader是一个基于C++核心的高性能量化交易系统，提供完整的交易引擎、技术指标库、回测框架和风险管理模块。

主要特性：
- 🚀 高性能C++核心引擎，高频场景延迟仅67.7微秒
- 📊 完整的技术指标系统，支持自定义Python指标
- 🔧 专业的回测引擎，多策略并行回测
- 📈 智能数据管理，支持A股数据批量下载
- 🐍 完整的Python生态集成，pybind11绑定
- 🌐 现代化Web界面，基于Dash的交互式图表
- 💬 用户反馈系统，指标分享平台

性能指标：
- 高频延迟: 67.7微秒/数据点 (目标≤100μs)
- 吞吐量: 14,771数据点/秒 (优秀≥10K)
- 最佳吞吐量: 1,000,000+点/秒
- 内存效率: 内存池机制，无显著泄漏

系统要求：
- 操作系统: Linux/macOS/Windows (WSL2)
- Python: 3.8+ (推荐3.10+)
- 内存: 4GB+ (推荐8GB)
"""

# 作者信息
AUTHOR = "PlusPlusTrader Team"
AUTHOR_EMAIL = "support@pplustrader.com"
URL = "https://github.com/yourusername/PlusPlusTrader"
LICENSE = "MIT"

# 分类信息
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Financial and Insurance Industry",
    "Intended Audience :: Science/Research",
    "Topic :: Office/Business :: Financial :: Investment",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: C++",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
]

# 关键词
KEYWORDS = [
    "quantitative",
    "trading",
    "finance",
    "algorithmic",
    "backtesting",
    "technical-analysis",
    "high-frequency",
    "c++",
    "python",
]

# 依赖要求
INSTALL_REQUIRES = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "pybind11>=2.10.0",
    "plotly>=5.0.0",
    "dash>=2.0.0",
    "dash-bootstrap-components>=1.0.0",
    "yfinance>=0.2.0",
    "akshare>=1.10.0",
    "tushare>=1.2.0",
    "requests>=2.28.0",
    "python-dateutil>=2.8.0",
    "pytz>=2022.0",
]

# 开发依赖
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=0.991",
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "twine>=4.0.0",
        "wheel>=0.38.0",
    ],
    "test": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-xdist>=3.0.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "sphinx-autodoc-typehints>=1.0.0",
    ],
    "performance": [
        "psutil>=5.9.0",
        "memory-profiler>=0.60.0",
        "line-profiler>=4.0.0",
    ],
}

# 入口点
ENTRY_POINTS = {
    "console_scripts": [
        "pplustrader=pplustrader.cli:main",
        "ppl-download=scripts.download_a_shares:main",
        "ppl-backtest=scripts.run_backtest:main",
        "ppl-web=web.dashboard:main",
    ],
}

class CMakeExtension(Extension):
    """CMake扩展类"""
    
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    """CMake构建类"""
    
    def run(self):
        # 检查CMake是否可用
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake必须安装才能构建扩展")
        
        # 构建所有扩展
        for ext in self.extensions:
            self.build_extension(ext)
    
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # 创建构建目录
        build_temp = self.build_temp
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)
        
        # CMake配置
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            "-DCMAKE_BUILD_TYPE=Release",
        ]
        
        # 平台特定配置
        if platform.system() == "Windows":
            cmake_args += [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={}".format(extdir),
                "-G", "Visual Studio 17 2022",
            ]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
        else:
            cmake_args += ["-DCMAKE_BUILD_TYPE=Release"]
        
        # 构建参数
        build_args = ["--config", "Release"]
        
        if platform.system() == "Windows":
            build_args += ["--", "/m"]
        else:
            build_args += ["--", "-j4"]
        
        # 运行CMake
        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=build_temp)

def get_package_data():
    """获取包数据文件"""
    package_data = {
        "pplustrader": [
            "*.so",
            "*.pyd",
            "*.dll",
            "*.dylib",
        ],
        "custom_indicator": [
            "*.py",
            "*.pyi",
        ],
        "optimized_indicator": [
            "*.py",
            "*.pyi",
        ],
        "user_feedback_system": [
            "*.py",
            "*.pyi",
        ],
    }
    return package_data

def get_data_files():
    """获取数据文件"""
    data_files = [
        ("share/pplustrader/examples", [
            "examples/basic_usage.py",
            "examples/custom_indicator.py",
            "examples/backtest_strategy.py",
            "examples/high_frequency.py",
        ]),
        ("share/pplustrader/scripts", [
            "scripts/download_a_shares.py",
        ]),
        ("share/pplustrader/config", [
            "config/settings.yaml.example",
            "config/strategies.yaml.example",
        ]),
        ("share/pplustrader/docs", [
            "docs/用户指南.md",
            "docs/API文档.md",
            "docs/A股数据回测指南.md",
        ]),
    ]
    return data_files

def main():
    """主函数"""
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: PlusPlusTrader需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 设置扩展模块
    extensions = [
        CMakeExtension("pplustrader", sourcedir=".."),
    ]
    
    # 读取README作为长描述
    readme_path = Path(__file__).parent.parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            long_description = f.read()
    else:
        long_description = LONG_DESCRIPTION
    
    # 设置包信息
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        packages=find_packages(include=["pplustrader", "custom_indicator", "optimized_indicator", "user_feedback_system"]),
        package_data=get_package_data(),
        data_files=get_data_files(),
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        entry_points=ENTRY_POINTS,
        ext_modules=extensions,
        cmdclass={"build_ext": CMakeBuild},
        python_requires=">=3.8",
        zip_safe=False,
        include_package_data=True,
        project_urls={
            "Documentation": "https://docs.pplustrader.com",
            "Source": "https://github.com/yourusername/PlusPlusTrader",
            "Tracker": "https://github.com/yourusername/PlusPlusTrader/issues",
            "Discussions": "https://github.com/yourusername/PlusPlusTrader/discussions",
        },
        options={
            "bdist_wheel": {
                "universal": False,
            },
        },
    )

if __name__ == "__main__":
    main()