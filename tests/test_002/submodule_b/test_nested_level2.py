"""
测试二级目录日志记录功能 - test_002/submodule_b
"""
import pytest
from utils.logger_config import logger_config


class TestNestedLevel2:
    """二级目录测试类"""
    
    def test_level2_logging(self):
        """测试二级目录日志记录"""
        logger = logger_config.get_subdir_logger("test_002/submodule_b")
        logger.info("这是来自test_002/submodule_b的日志消息")
        assert True
    
    def test_level2_error_logging(self):
        """测试二级目录错误日志记录"""
        logger = logger_config.get_subdir_logger("test_002/submodule_b")
        logger.error("这是来自test_002/submodule_b的错误消息")
        assert True