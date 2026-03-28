# 贡献指南

感谢你对PlusPlusTrader项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 修复问题
- 🚀 提交新功能

## 📋 目录

1. [行为准则](#行为准则)
2. [如何贡献](#如何贡献)
3. [开发环境设置](#开发环境设置)
4. [代码规范](#代码规范)
5. [提交规范](#提交规范)
6. [测试要求](#测试要求)
7. [文档要求](#文档要求)
8. [发布流程](#发布流程)

## 📜 行为准则

本项目遵守 [贡献者公约行为准则](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)。参与本项目即表示您同意遵守此准则。

### 我们的承诺
我们致力于为所有贡献者营造一个开放、友好的环境，无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、个人形象、种族、宗教或性取向如何。

### 我们的标准
有助于创造积极环境的行为包括：
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

不可接受的行为包括：
- 使用性暗示的语言或图像，以及不受欢迎的性关注或挑逗
- 挑衅、侮辱/贬损的评论，以及人身或政治攻击
- 公开或私下的骚扰
- 未经明确许可，发布他人的私人信息，例如住址或电子地址
- 其他在专业环境中可能被认为不适当的行为

## 🛠️ 如何贡献

### 报告Bug

如果你发现了一个bug，请通过 [GitHub Issues](https://github.com/WangBreeze/PlusPlusTrader/issues) 报告。

**好的bug报告应该包含：**
1. **清晰的标题和描述**
2. **复现步骤** - 如何重现这个问题
3. **期望的行为** - 你期望发生什么
4. **实际的行为** - 实际发生了什么
5. **环境信息** - 操作系统、Python版本、项目版本等
6. **可能的解决方案** - 如果你有想法的话
7. **截图或日志** - 如果适用的话

**示例：**
```
标题: 回测引擎在空数据源上崩溃

描述:
当使用空数据源运行回测时，程序会抛出未处理的异常。

复现步骤:
1. 创建空数据源: `data_source = ppt.CSVDataSource("empty.csv")`
2. 创建策略: `strategy = ppt.MACrossStrategy()`
3. 运行回测: `backtest.run()`

期望行为:
应该优雅地处理空数据源，返回有意义的错误信息。

实际行为:
抛出 `IndexError: list index out of range`

环境:
- 操作系统: Ubuntu 22.04
- Python: 3.9.12
- PlusPlusTrader: 1.0.0

建议修复:
在BacktestEngine.run()开始时检查数据源是否为空。
```

### 提出新功能

我们欢迎新功能的建议！请通过 [GitHub Issues](https://github.com/WangBreeze/PlusPlusTrader/issues) 提出。

**好的功能建议应该包含：**
1. **问题描述** - 这个功能解决什么问题
2. **解决方案** - 你建议如何实现
3. **替代方案** - 你考虑过的其他方案
4. **附加信息** - 任何相关的信息

### 提交代码

1. **Fork仓库**
2. **创建分支**
   ```bash
   git checkout -b feature/amazing-feature
   # 或
   git checkout -b fix/annoying-bug
   ```
3. **进行更改**
4. **运行测试**
5. **提交更改**
6. **推送到分支**
7. **创建Pull Request**

## 💻 开发环境设置

### 1. 克隆仓库

```bash
# Fork仓库到你的GitHub账户
# 然后克隆你的fork
git clone https://github.com/your-username/PlusPlusTrader.git
cd PlusPlusTrader

# 添加上游仓库
git remote add upstream https://github.com/WangBreeze/PlusPlusTrader.git
```

### 2. 设置开发环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
pip install -e .

# 安装预提交钩子
pre-commit install
```

### 3. 编译C++核心

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug  # 调试模式
make -j$(nproc)
cd ..
```

### 4. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_strategies.py

# 运行测试并生成覆盖率报告
pytest --cov=pplustrader --cov-report=html

# 打开覆盖率报告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

## 📝 代码规范

### Python代码规范

我们使用以下工具确保代码质量：

```bash
# 代码格式化
black pplustrader/ tests/ examples/

# 导入排序
isort pplustrader/ tests/ examples/

# 代码检查
flake8 pplustrader/ tests/ examples/

# 类型检查（可选）
mypy pplustrader/
```

#### 命名约定
- **类名**: `CamelCase`，例如 `BacktestEngine`
- **函数名**: `snake_case`，例如 `calculate_returns`
- **变量名**: `snake_case`，例如 `total_return`
- **常量**: `UPPER_CASE`，例如 `MAX_RETRY_COUNT`
- **私有成员**: 前缀 `_`，例如 `_internal_method`

#### 文档字符串
所有公共函数、类和方法都需要文档字符串。

```python
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列，numpy数组或列表
        risk_free_rate: 无风险利率，默认为2%
    
    Returns:
        float: 夏普比率
    
    Raises:
        ValueError: 如果returns为空或标准差为0
    
    Examples:
        >>> calculate_sharpe_ratio([0.01, 0.02, -0.01])
        0.577
    """
    if len(returns) == 0:
        raise ValueError("returns不能为空")
    
    # 实现逻辑
    excess_returns = returns - risk_free_rate / 252
    sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
    
    return sharpe
```

### C++代码规范

#### 命名约定
- **类名**: `CamelCase`，例如 `TradingEngine`
- **函数名**: `camelCase`，例如 `calculateReturns`
- **变量名**: `camelCase`，例如 `totalReturn`
- **常量**: `UPPER_CASE`，例如 `MAX_RETRY_COUNT`
- **私有成员**: 前缀 `m_`，例如 `m_internalData`

#### 代码格式
```cpp
// 头文件示例
#ifndef TRADING_ENGINE_H
#define TRADING_ENGINE_H

#include <vector>
#include <string>

namespace ppt {
namespace core {

/**
 * @brief 交易引擎类
 * 
 * 负责执行交易订单和管理持仓。
 */
class TradingEngine {
public:
    /**
     * @brief 构造函数
     * @param initialCapital 初始资金
     */
    explicit TradingEngine(double initialCapital);
    
    /**
     * @brief 执行订单
     * @param order 订单对象
     * @return 执行结果
     */
    OrderResult executeOrder(const Order& order);
    
private:
    double m_capital;           ///< 当前资金
    std::vector<Position> m_positions;  ///< 持仓列表
};

} // namespace core
} // namespace ppt

#endif // TRADING_ENGINE_H
```

## 📤 提交规范

### 提交消息格式

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型
- **feat**: 新功能
- **fix**: bug修复
- **docs**: 文档更新
- **style**: 代码格式（不影响代码运行的变动）
- **refactor**: 代码重构（既不是新功能也不是bug修复）
- **perf**: 性能优化
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

#### 示例
```
feat(strategy): 添加移动平均交叉策略

- 实现MACrossStrategy类
- 添加相关测试
- 更新文档

Closes #123
```

```
fix(backtest): 修复回测引擎内存泄漏

修复了在长时间回测时出现的内存泄漏问题。

BREAKING CHANGE: BacktestEngine构造函数参数顺序改变

Closes #456
```

### Pull Request流程

1. **确保分支是最新的**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **运行测试**
   ```bash
   pytest
   pre-commit run --all-files
   ```

3. **更新文档**
   - 如果添加了新功能，更新相关文档
   - 如果修改了API，更新API文档

4. **创建Pull Request**
   - 标题: `[类型] 简短描述`，例如 `[feat] 添加布林带策略`
   - 描述: 详细说明更改内容和原因
   - 关联Issue: 使用 `Closes #123` 或 `Fixes #456`

5. **等待审查**
   - 至少需要一名核心贡献者的批准
   - 解决审查意见
   - 保持PR的更新

## 🧪 测试要求

### 测试覆盖率
- 所有新代码必须有测试
- 整体覆盖率不低于80%
- 关键模块覆盖率不低于90%

### 测试类型
```python
# 单元测试
def test_sma_calculation():
    """测试SMA计算"""
    sma = ppt.SMA(period=3)
    assert sma.update(100) is None
    assert sma.update(102) is None
    assert sma.update(101) == 101  # (100+102+101)/3
    
# 集成测试
def test_backtest_integration():
    """测试回测集成"""
    data_source = ppt.CSVDataSource("test_data.csv")
    strategy = ppt.MACrossStrategy()
    backtest = ppt.BacktestEngine(data_source, strategy)
    results = backtest.run()
    assert results.total_return is not None
    
# 性能测试
def test_performance_large_dataset():
    """测试大数据集性能"""
    import time
    n = 100000
    data = create_large_dataset(n)
    
    start = time.time()
    results = run_backtest(data)
    elapsed = time.time() - start
    
    assert elapsed < 5.0  # 5秒内完成
    assert results.trade_count > 0
```

### 测试文件结构
```
tests/
├── unit/
│   ├── test_indicators.py
│   ├── test_strategies.py
│   └── test_data_sources.py
├── integration/
│   ├── test_backtest.py
│   └── test_trading.py
├── performance/
│   └── test_performance.py
└── conftest.py  # 测试配置
```

## 📚 文档要求

### 文档类型
1. **API文档**: 所有公共API必须有文档字符串
2. **教程**: 新手入门指南
3. **示例**: 实际使用示例
4. **开发指南**: 开发者文档

### 文档更新
- 添加新功能时，必须更新相关文档
- 修改API时，必须更新API文档
- 修复bug时，如果影响使用，更新相关文档

### 文档格式
- 使用Markdown格式
- 代码示例要有可运行性
- 复杂的图表要有说明

## 🚀 发布流程

### 版本号规则
我们使用 [语义化版本](https://semver.org/)：
- **主版本 (1.0.0)**: 不兼容的API变更
- **次版本 (1.1.0)**: 向后兼容的功能新增
- **修订号 (1.0.1)**: 向后兼容的问题修复

### 发布步骤
1. **创建发布分支**
   ```bash
   git checkout -b release/v1.1.0
   ```

2. **更新版本号**
   - `pyproject.toml` 中的版本号
   - `CHANGELOG.md` 中的更新日志
   - 代码中的版本常量

3. **运行完整测试**
   ```bash
   pytest --cov=pplustrader --cov-report=html
   make test-all  # 如果有makefile
   ```

4. **构建发布包**
   ```bash
   python -m build
   python -m twine check dist/*
   ```

5. **创建Git标签**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

6. **发布到PyPI** (仅核心贡献者)
   ```bash
   python -m twine upload dist/*
   ```

7. **创建GitHub Release**
   - 标题: `v1.1.0`
   - 描述: 从CHANGELOG.md复制
   - 上传构建的文件

## 🏆 贡献者奖励

为了感谢贡献者的付出，我们有以下奖励机制：

### 贡献者名单
所有贡献者都会在以下位置被列出：
1. `README.md` 中的贡献者部分
2. 项目网站的贡献者页面
3. 发布公告中的特别感谢

### 特殊贡献
- **重大贡献**: 在项目网站和文档中特别提及
- **长期贡献**: 获得"核心贡献者"称号
- **社区贡献**: 在社区活动中表彰

### 如何成为核心贡献者
要成为核心贡献者，需要：
1. 至少提交10个有意义的PR
2. 至少修复5个重要bug或实现3个重要功能
3. 积极参与社区讨论和代码审查
4. 得到现有核心贡献者的推荐

## ❓ 常见问题

### Q: 我可以从哪里开始贡献？
A: 查看 [Good First Issues](https://github.com/WangBreeze/PlusPlusTrader/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 标签的问题。

### Q: 我的PR需要多长时间才能被合并？
A: 通常需要1-3天。如果一周后还没有回复，可以友好地提醒。

### Q: 我可以添加新的数据源吗？
A: 当然可以！请确保新数据源有稳定的API和良好的文档。

### Q: 我可以使用不同的编程语言贡献吗？
A: 目前我们主要支持Python和C++。如果你有其他语言的实现，可以作为独立项目贡献。

### Q: 如何获取帮助？
A: 可以通过以下方式获取帮助：
1. GitHub Issues
2. Discord社区
3. 项目文档

## 📞 联系方式

- **项目维护者**: @WangBreeze
- **问题报告**: [GitHub Issues](https://github.com/WangBreeze/PlusPlusTrader/issues)
- **讨论区**: [Discord](https://discord.gg/your-discord-link)
- **邮件**: contributors@pplustrader.com

---

**感谢你的贡献！** 🙏

你的每一份贡献都让这个项目变得更好。我们期待与你合作！

Happy Coding! 🚀