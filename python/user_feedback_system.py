#!/usr/bin/env python3
"""
用户反馈系统
功能：收集用户反馈、指标分享、问题报告、性能监控
"""

import sys
import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import hashlib
import threading
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class FeedbackType(Enum):
    """反馈类型"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    PERFORMANCE_ISSUE = "performance_issue"
    USABILITY_ISSUE = "usability_issue"
    DOCUMENTATION_ISSUE = "documentation_issue"
    INDICATOR_SHARE = "indicator_share"
    GENERAL_FEEDBACK = "general_feedback"

class FeedbackSeverity(Enum):
    """反馈严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class UserFeedback:
    """用户反馈数据类"""
    feedback_id: str
    feedback_type: FeedbackType
    title: str
    description: str
    severity: FeedbackSeverity
    user_id: Optional[str] = None
    email: Optional[str] = None
    indicator_name: Optional[str] = None
    indicator_config: Optional[Dict[str, Any]] = None
    performance_data: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    attachments: Optional[List[str]] = None
    created_at: str = ""
    updated_at: str = ""
    status: str = "new"
    priority: int = 0
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['feedback_type'] = self.feedback_type.value
        data['severity'] = self.severity.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserFeedback':
        """从字典创建"""
        data['feedback_type'] = FeedbackType(data['feedback_type'])
        data['severity'] = FeedbackSeverity(data['severity'])
        return cls(**data)

@dataclass
class SharedIndicator:
    """共享指标数据类"""
    indicator_id: str
    name: str
    description: str
    author: str
    author_email: Optional[str] = None
    indicator_code: str = ""
    indicator_config: Dict[str, Any] = None
    dependencies: List[str] = None
    tags: List[str] = None
    version: str = "1.0.0"
    downloads: int = 0
    rating: float = 0.0
    ratings_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    license: str = "MIT"
    verified: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.indicator_config is None:
            self.indicator_config = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SharedIndicator':
        """从字典创建"""
        return cls(**data)

class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self, storage_path: str = "feedback_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # 初始化存储目录
        self.feedback_dir = self.storage_path / "feedbacks"
        self.indicators_dir = self.storage_path / "indicators"
        self.stats_dir = self.storage_path / "stats"
        
        for directory in [self.feedback_dir, self.indicators_dir, self.stats_dir]:
            directory.mkdir(exist_ok=True)
        
        # 初始化统计
        self.stats = self._load_stats()
        
        # 反馈队列
        self.feedback_queue = []
        self.queue_lock = threading.Lock()
        
        # 启动处理线程
        self.processing = True
        self.processor_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processor_thread.start()
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载统计信息"""
        stats_file = self.stats_dir / "overall_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 默认统计
        return {
            "total_feedbacks": 0,
            "feedbacks_by_type": {ft.value: 0 for ft in FeedbackType},
            "feedbacks_by_severity": {fs.value: 0 for fs in FeedbackSeverity},
            "total_indicators": 0,
            "total_downloads": 0,
            "average_rating": 0.0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = self.stats_dir / "overall_stats.json"
        self.stats["last_updated"] = datetime.now().isoformat()
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def submit_feedback(self, feedback: UserFeedback) -> str:
        """
        提交反馈
        返回: 反馈ID
        """
        # 生成唯一ID
        if not feedback.feedback_id:
            feedback.feedback_id = str(uuid.uuid4())
        
        # 更新时间戳
        feedback.updated_at = datetime.now().isoformat()
        
        # 添加到队列
        with self.queue_lock:
            self.feedback_queue.append(feedback)
        
        return feedback.feedback_id
    
    def share_indicator(self, indicator: SharedIndicator) -> str:
        """
        共享指标
        返回: 指标ID
        """
        # 生成唯一ID
        if not indicator.indicator_id:
            indicator_hash = hashlib.md5(
                f"{indicator.name}{indicator.author}{time.time()}".encode()
            ).hexdigest()[:12]
            indicator.indicator_id = indicator_hash
        
        # 保存指标
        indicator_file = self.indicators_dir / f"{indicator.indicator_id}.json"
        
        with open(indicator_file, 'w', encoding='utf-8') as f:
            json.dump(indicator.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 更新统计
        self.stats["total_indicators"] += 1
        self._save_stats()
        
        return indicator.indicator_id
    
    def get_indicator(self, indicator_id: str) -> Optional[SharedIndicator]:
        """获取共享指标"""
        indicator_file = self.indicators_dir / f"{indicator_id}.json"
        
        if not indicator_file.exists():
            return None
        
        try:
            with open(indicator_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return SharedIndicator.from_dict(data)
        except:
            return None
    
    def search_indicators(self, query: str = "", tags: List[str] = None, 
                         min_rating: float = 0.0) -> List[SharedIndicator]:
        """搜索共享指标"""
        indicators = []
        
        for indicator_file in self.indicators_dir.glob("*.json"):
            try:
                with open(indicator_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    indicator = SharedIndicator.from_dict(data)
                    
                    # 应用过滤器
                    matches = True
                    
                    if query and query.lower() not in indicator.name.lower() and \
                       query.lower() not in indicator.description.lower():
                        matches = False
                    
                    if tags and not any(tag in indicator.tags for tag in tags):
                        matches = False
                    
                    if indicator.rating < min_rating:
                        matches = False
                    
                    if matches:
                        indicators.append(indicator)
            except:
                continue
        
        # 按评分和下载量排序
        indicators.sort(key=lambda x: (x.rating, x.downloads), reverse=True)
        
        return indicators
    
    def rate_indicator(self, indicator_id: str, rating: float, comment: str = "") -> bool:
        """评价指标"""
        indicator = self.get_indicator(indicator_id)
        if not indicator:
            return False
        
        # 更新评分
        total_rating = indicator.rating * indicator.ratings_count
        indicator.ratings_count += 1
        indicator.rating = (total_rating + rating) / indicator.ratings_count
        indicator.updated_at = datetime.now().isoformat()
        
        # 保存更新
        indicator_file = self.indicators_dir / f"{indicator_id}.json"
        with open(indicator_file, 'w', encoding='utf-8') as f:
            json.dump(indicator.to_dict(), f, indent=2, ensure_ascii=False)
        
        return True
    
    def download_indicator(self, indicator_id: str) -> Optional[SharedIndicator]:
        """下载指标（增加下载计数）"""
        indicator = self.get_indicator(indicator_id)
        if not indicator:
            return None
        
        # 更新下载计数
        indicator.downloads += 1
        indicator.updated_at = datetime.now().isoformat()
        
        # 保存更新
        indicator_file = self.indicators_dir / f"{indicator_id}.json"
        with open(indicator_file, 'w', encoding='utf-8') as f:
            json.dump(indicator.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 更新统计
        self.stats["total_downloads"] += 1
        self._save_stats()
        
        return indicator
    
    def get_feedback(self, feedback_id: str) -> Optional[UserFeedback]:
        """获取反馈"""
        feedback_file = self.feedback_dir / f"{feedback_id}.json"
        
        if not feedback_file.exists():
            return None
        
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserFeedback.from_dict(data)
        except:
            return None
    
    def get_all_feedbacks(self, limit: int = 100, offset: int = 0) -> List[UserFeedback]:
        """获取所有反馈"""
        feedbacks = []
        
        for feedback_file in sorted(self.feedback_dir.glob("*.json"), 
                                   key=lambda x: x.stat().st_mtime, 
                                   reverse=True):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    feedbacks.append(UserFeedback.from_dict(data))
            except:
                continue
        
        return feedbacks[offset:offset+limit]
    
    def update_feedback_status(self, feedback_id: str, status: str, 
                              response: str = "") -> bool:
        """更新反馈状态"""
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            return False
        
        feedback.status = status
        feedback.updated_at = datetime.now().isoformat()
        
        # 保存更新
        feedback_file = self.feedback_dir / f"{feedback_id}.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def _process_queue(self):
        """处理反馈队列"""
        while self.processing:
            time.sleep(1)  # 每秒检查一次
            
            with self.queue_lock:
                if not self.feedback_queue:
                    continue
                
                # 处理队列中的反馈
                feedbacks_to_process = self.feedback_queue.copy()
                self.feedback_queue.clear()
            
            # 处理每个反馈
            for feedback in feedbacks_to_process:
                self._save_feedback(feedback)
    
    def _save_feedback(self, feedback: UserFeedback):
        """保存反馈到文件"""
        # 保存反馈文件
        feedback_file = self.feedback_dir / f"{feedback.feedback_id}.json"
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 更新统计
        self.stats["total_feedbacks"] += 1
        self.stats["feedbacks_by_type"][feedback.feedback_type.value] += 1
        self.stats["feedbacks_by_severity"][feedback.severity.value] += 1
        self._save_stats()
        
        # 记录日志
        self._log_feedback(feedback)
    
    def _log_feedback(self, feedback: UserFeedback):
        """记录反馈日志"""
        log_file = self.storage_path / "feedback_log.txt"
        
        log_entry = (
            f"[{datetime.now().isoformat()}] "
            f"ID: {feedback.feedback_id} | "
            f"Type: {feedback.feedback_type.value} | "
            f"Severity: {feedback.severity.value} | "
            f"Title: {feedback.title}\n"
        )
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def stop(self):
        """停止处理"""
        self.processing = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5.0)
        
        # 处理剩余队列
        with self.queue_lock:
            for feedback in self.feedback_queue:
                self._save_feedback(feedback)
            self.feedback_queue.clear()

class FeedbackUI:
    """反馈用户界面"""
    
    def __init__(self, collector: FeedbackCollector):
        self.collector = collector
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("PlusPlusTrader 用户反馈系统")
        print("="*60)
        
        while True:
            print("\n请选择操作:")
            print("1. 提交反馈/问题报告")
            print("2. 共享自定义指标")
            print("3. 浏览共享指标")
            print("4. 查看反馈统计")
            print("5. 搜索指标")
            print("6. 退出")
            
            choice = input("\n请输入选项 (1-6): ").strip()
            
            if choice == "1":
                self.submit_feedback_ui()
            elif choice == "2":
                self.share_indicator_ui()
            elif choice == "3":
                self.browse_indicators_ui()
            elif choice == "4":
                self.show_stats_ui()
            elif choice == "5":
                self.search_indicators_ui()
            elif choice == "6":
                print("感谢使用反馈系统！")
                break
            else:
                print("无效选项，请重新选择。")
    
    def submit_feedback_ui(self):
        """提交反馈界面"""
        print("\n" + "-"*60)
        print("提交反馈/问题报告")
        print("-"*60)
        
        # 选择反馈类型
        print("\n请选择反馈类型:")
        for i, ft in enumerate(FeedbackType, 1):
            print(f"{i}. {ft.value}")
        
        try:
            type_choice = int(input("\n请选择类型 (1-7): ")) - 1
            feedback_type = list(FeedbackType)[type_choice]
        except:
            print("无效选择，使用默认类型。")
            feedback_type = FeedbackType.GENERAL_FEEDBACK
        
        # 选择严重程度
        print("\n请选择严重程度:")
        for i, fs in enumerate(FeedbackSeverity, 1):
            print(f"{i}. {fs.value}")
        
        try:
            severity_choice = int(input("\n请选择严重程度 (1-4): ")) - 1
            severity = list(FeedbackSeverity)[severity_choice]
        except:
            print("无效选择，使用默认严重程度。")
            severity = FeedbackSeverity.MEDIUM
        
        # 输入标题和描述
        title = input("\n请输入标题: ").strip()
        if not title:
            print("标题不能为空！")
            return
        
        print("\n请输入详细描述 (输入空行结束):")
        description_lines = []
        while True:
            line = input()
            if not line:
                break
            description_lines.append(line)
        
        description = "\n".join(description_lines)
        if not description:
            print("描述不能为空！")
            return
        
        # 用户信息（可选）
        user_id = input("\n用户ID (可选): ").strip() or None
        email = input("邮箱 (可选): ").strip() or None
        
        # 创建反馈
        feedback = UserFeedback(
            feedback_id="",
            feedback_type=feedback_type,
            title=title,
            description=description,
            severity=severity,
            user_id=user_id,
            email=email
        )
        
        # 提交反馈
        feedback_id = self.collector.submit_feedback(feedback)
        
        print(f"\n✅ 反馈提交成功！")
        print(f"反馈ID: {feedback_id}")
        print(f"我们会尽快处理您的反馈。")
    
    def share_indicator_ui(self):
        """共享指标界面"""
        print("\n" + "-"*60)
        print("共享自定义指标")
        print("-"*60)
        
        # 输入指标信息
        name = input("\n指标名称: ").strip()
        if not name:
            print("指标名称不能为空！")
            return
        
        description = input("指标描述: ").strip()
        author = input("作者姓名: ").strip()
        author_email = input("作者邮箱 (可选): ").strip() or None
        
        # 输入指标代码
        print("\n请输入指标代码 (输入空行结束):")
        code_lines = []
        while True:
            line = input()
            if not line:
                break
            code_lines.append(line)
        
        indicator_code = "\n".join(code_lines)
        if not indicator_code:
            print("指标代码不能为空！")
            return
        
        # 输入配置参数
        print("\n请输入配置参数 (JSON格式，输入空行结束):")
        config_lines = []
        while True:
            line = input()
            if not line:
                break
            config_lines.append(line)
        
        config_str = "\n".join(config_lines)
        indicator_config = {}
        if config_str:
            try:
                indicator_config = json.loads(config_str)
            except:
                print("配置参数格式错误，使用空配置。")
        
        # 输入标签
        tags_input = input("\n标签 (用逗号分隔): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        # 创建共享指标
        indicator = SharedIndicator(
            indicator_id="",
            name=name,
            description=description,
            author=author,
            author_email=author_email,
            indicator_code=indicator_code,
            indicator_config=indicator_config,
            tags=tags
        )
        
        # 共享指标
        indicator_id = self.collector.share_indicator(indicator)
        
        print(f"\n✅ 指标共享成功！")
        print(f"指标ID: {indicator_id}")
        print(f"其他用户现在可以搜索和下载您的指标。")
    
    def browse_indicators_ui(self):
        """浏览共享指标界面"""
        print("\n" + "-"*60)
        print("浏览共享指标")
        print("-"*60)
        
        indicators = self.collector.search_indicators()
        
        if not indicators:
            print("\n暂无共享指标。")
            return
        
        print(f"\n找到 {len(indicators)} 个共享指标:")
        
        for i, indicator in enumerate(indicators, 1):
            print(f"\n{i}. {indicator.name} (v{indicator.version})")
            print(f"   作者: {indicator.author}")
            print(f"   描述: {indicator.description[:100]}...")
            print(f"   评分: {indicator.rating:.1f}/5.0 ({indicator.ratings_count} 评价)")
            print(f"   下载: {indicator.downloads} 次")
            print(f"   标签: {', '.join(indicator.tags[:5])}")
        
        # 选择指标查看详情
        try:
            choice = input(f"\n输入编号查看详情 (1-{len(indicators)}) 或按回车返回: ").strip()
            if choice:
                index = int(choice) - 1
                if 0 <= index < len(indicators):
                    self.show_indicator_detail(indicators[index])
        except:
            pass
    
    def show_indicator_detail(self, indicator: SharedIndicator):
        """显示指标详情"""
        print("\n" + "="*60)
        print(f"指标详情: {indicator.name}")
        print("="*60)
        
        print(f"\n📋 基本信息:")
        print(f"   指标ID: {indicator.indicator_id}")
        print(f"   版本: {indicator.version}")
        print(f"   作者: {indicator.author}")
        if indicator.author_email:
            print(f"   邮箱: {indicator.author_email}")
        print(f"   创建时间: {indicator.created_at}")
        print(f"   更新时间: {indicator.updated_at}")
        print(f"   许可证: {indicator.license}")
        print(f"   已验证: {'✅' if indicator.verified else '❌'}")
        
        print(f"\n📊 统计信息:")
        print(f"   评分: {indicator.rating:.1f}/5.0 ({indicator.ratings_count} 评价)")
        print(f"   下载: {indicator.downloads} 次")
        
        print(f"\n🏷️  标签:")
        print(f"   {', '.join(indicator.tags)}")
        
        print(f"\n📝 描述:")
        print(f"   {indicator.description}")
        
        print(f"\n⚙️  配置参数:")
        if indicator.indicator_config:
            for key, value in indicator.indicator_config.items():
                print(f"   {key}: {value}")
        else:
            print("   无配置参数")
        
        print(f"\n📦 依赖:")
        if indicator.dependencies:
            for dep in indicator.dependencies:
                print(f"   - {dep}")
        else:
            print("   无依赖")
        
        print(f"\n💻 指标代码:")
        print("   " + "\n   ".join(indicator.indicator_code.split("\n")[:20]))
        if len(indicator.indicator_code.split("\n")) > 20:
            print("   ... (代码过长，只显示前20行)")
        
        # 操作选项
        print("\n" + "-"*60)
        print("操作选项:")
        print("1. 下载指标")
        print("2. 评价指标")
        print("3. 返回")
        
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == "1":
            self.download_indicator_ui(indicator.indicator_id)
        elif choice == "2":
            self.rate_indicator_ui(indicator.indicator_id)
    
    def download_indicator_ui(self, indicator_id: str):
        """下载指标界面"""
        indicator = self.collector.download_indicator(indicator_id)
        
        if indicator:
            print(f"\n✅ 指标下载成功！")
            print(f"指标: {indicator.name}")
            print(f"下载次数: {indicator.downloads}")
            
            # 保存指标代码到文件
            filename = f"{indicator.name.replace(' ', '_')}_{indicator.indicator_id}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(indicator.indicator_code)
            
            print(f"指标代码已保存到: {filename}")
        else:
            print("\n❌ 下载失败，指标不存在。")
    
    def rate_indicator_ui(self, indicator_id: str):
        """评价指标界面"""
        try:
            rating = float(input("\n请输入评分 (0.0-5.0): ").strip())
            if rating < 0 or rating > 5:
                print("评分必须在0.0到5.0之间。")
                return
            
            comment = input("评价说明 (可选): ").strip()
            
            success = self.collector.rate_indicator(indicator_id, rating, comment)
            
            if success:
                print("✅ 评价提交成功！")
            else:
                print("❌ 评价失败，指标不存在。")
        except:
            print("❌ 输入无效。")
    
    def show_stats_ui(self):
        """显示统计信息界面"""
        stats = self.collector.get_stats()
        
        print("\n" + "="*60)
        print("反馈系统统计信息")
        print("="*60)
        
        print(f"\n📊 总体统计:")
        print(f"   总反馈数: {stats['total_feedbacks']}")
        print(f"   总指标数: {stats['total_indicators']}")
        print(f"   总下载数: {stats['total_downloads']}")
        print(f"   平均评分: {stats['average_rating']:.2f}/5.0")
        print(f"   最后更新: {stats['last_updated']}")
        
        print(f"\n📈 反馈类型分布:")
        for fb_type, count in stats['feedbacks_by_type'].items():
            if count > 0:
                print(f"   {fb_type}: {count}")
        
        print(f"\n⚠️  反馈严重程度分布:")
        for severity, count in stats['feedbacks_by_severity'].items():
            if count > 0:
                print(f"   {severity}: {count}")
    
    def search_indicators_ui(self):
        """搜索指标界面"""
        print("\n" + "-"*60)
        print("搜索共享指标")
        print("-"*60)
        
        query = input("\n搜索关键词: ").strip()
        tags_input = input("标签 (用逗号分隔，可选): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        try:
            min_rating = float(input("最低评分 (0.0-5.0，可选): ").strip() or "0.0")
        except:
            min_rating = 0.0
        
        indicators = self.collector.search_indicators(
            query=query,
            tags=tags,
            min_rating=min_rating
        )
        
        if not indicators:
            print("\n未找到匹配的指标。")
            return
        
        print(f"\n找到 {len(indicators)} 个匹配的指标:")
        
        for i, indicator in enumerate(indicators, 1):
            print(f"\n{i}. {indicator.name} (评分: {indicator.rating:.1f})")
            print(f"   作者: {indicator.author}")
            print(f"   描述: {indicator.description[:80]}...")
            print(f"   标签: {', '.join(indicator.tags[:3])}")
        
        # 选择查看详情
        try:
            choice = input(f"\n输入编号查看详情 (1-{len(indicators)}) 或按回车返回: ").strip()
            if choice:
                index = int(choice) - 1
                if 0 <= index < len(indicators):
                    self.show_indicator_detail(indicators[index])
        except:
            pass

def test_feedback_system():
    """测试反馈系统"""
    print("="*60)
    print("用户反馈系统测试")
    print("="*60)
    
    # 创建反馈收集器
    collector = FeedbackCollector("test_feedback_data")
    
    # 创建UI
    ui = FeedbackUI(collector)
    
    # 测试提交反馈
    print("\n1. 测试提交反馈...")
    test_feedback = UserFeedback(
        feedback_id="",
        feedback_type=FeedbackType.BUG_REPORT,
        title="测试反馈标题",
        description="这是一个测试反馈描述，用于验证反馈系统功能。",
        severity=FeedbackSeverity.MEDIUM,
        user_id="test_user_001",
        email="test@example.com"
    )
    
    feedback_id = collector.submit_feedback(test_feedback)
    print(f"   反馈ID: {feedback_id}")
    
    # 测试共享指标
    print("\n2. 测试共享指标...")
    test_indicator = SharedIndicator(
        indicator_id="",
        name="测试移动平均线",
        description="这是一个测试用的移动平均线指标，用于验证指标分享功能。",
        author="测试作者",
        author_email="author@example.com",
        indicator_code="""
class TestMovingAverage:
    def __init__(self, window=20):
        self.window = window
        self.prices = []
    
    def update(self, price):
        self.prices.append(price)
        if len(self.prices) > self.window:
            self.prices.pop(0)
        
        if len(self.prices) >= self.window:
            return sum(self.prices) / len(self.prices)
        return None
    
    def get_value(self):
        if len(self.prices) >= self.window:
            return sum(self.prices) / len(self.prices)
        return None
""",
        indicator_config={"window": 20},
        tags=["moving-average", "test", "simple"],
        version="1.0.0"
    )
    
    indicator_id = collector.share_indicator(test_indicator)
    print(f"   指标ID: {indicator_id}")
    
    # 测试搜索指标
    print("\n3. 测试搜索指标...")
    indicators = collector.search_indicators(query="移动平均线")
    print(f"   找到 {len(indicators)} 个匹配指标")
    
    # 测试下载指标
    print("\n4. 测试下载指标...")
    if indicators:
        downloaded = collector.download_indicator(indicators[0].indicator_id)
        if downloaded:
            print(f"   下载成功: {downloaded.name}")
    
    # 测试评价指标
    print("\n5. 测试评价指标...")
    if indicators:
        collector.rate_indicator(indicators[0].indicator_id, 4.5, "很好的指标！")
        print("   评价成功")
    
    # 显示统计信息
    print("\n6. 显示统计信息...")
    stats = collector.get_stats()
    print(f"   总反馈数: {stats['total_feedbacks']}")
    print(f"   总指标数: {stats['total_indicators']}")
    print(f"   总下载数: {stats['total_downloads']}")
    
    # 停止收集器
    collector.stop()
    
    print("\n" + "="*60)
    print("反馈系统测试完成！")
    print("="*60)
    
    return {
        'feedback_id': feedback_id,
        'indicator_id': indicator_id,
        'indicators_found': len(indicators),
        'stats': stats
    }

def main():
    """主函数"""
    print("PlusPlusTrader 用户反馈系统")
    print("="*60)
    
    # 运行测试
    print("\n运行系统测试...")
    results = test_feedback_system()
    
    print("\n📊 测试结果:")
    print(f"   反馈ID: {results['feedback_id']}")
    print(f"   指标ID: {results['indicator_id']}")
    print(f"   找到指标: {results['indicators_found']}")
    
    # 启动交互式UI
    print("\n" + "="*60)
    print("启动交互式用户界面...")
    print("="*60)
    
    collector = FeedbackCollector("user_feedback_data")
    ui = FeedbackUI(collector)
    
    try:
        ui.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n用户中断操作。")
    finally:
        collector.stop()
    
    print("\n感谢使用 PlusPlusTrader 反馈系统！")

if __name__ == "__main__":
    main()