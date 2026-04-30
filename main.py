"""
部署入口點 — 戰國三代記 MVP Webapp
Production entry point for gunicorn
"""
import sys, os

# 將 webapp 目錄加入 Python 路徑
webapp_dir = os.path.join(os.path.dirname(__file__), '00.Documentation', '0050.MVP', 'webapp')
sys.path.insert(0, webapp_dir)

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
