import os

def setup_logger(log_name='default', log_dir='logs/default'):
    import logging
    from logging.handlers import TimedRotatingFileHandler

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, f'{log_name}.log')
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        filename=log_path,
        encoding='big5',
        when='midnight',  # 每天午夜切割
        interval=1,       # 每 1 天
        backupCount=14,   # 保留 14 天的檔案
        errors='ignore'   # 遇到無法編碼的字元時忽略
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger