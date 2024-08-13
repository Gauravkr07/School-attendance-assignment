import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logging():
    """
    setup logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_file_name = datetime.now().strftime(".logger_%Y-%m-%d.log") 
    handler = TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)




# engine = create_engine(db_url)
# Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()


# @contextmanager
# def db_session() -> Session:
#     session = Session()
#     try:
#         # Base.metadata.create_all(bind=engine)

#         yield session
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()
