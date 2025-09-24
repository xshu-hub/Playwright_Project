"""二级目录下的测试文件"""
import pytest
from loguru import logger


class TestNestedModule:
    """嵌套模块测试类"""
    
    def test_nested_logging(self):
        """测试二级目录下的日志记录"""
        logger.info("这是来自二级目录的日志消息")
        assert True
        
    def test_another_nested_test(self):
        """另一个二级目录测试"""
        logger.warning("这是来自二级目录的警告消息")
        assert True