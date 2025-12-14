from flask import Flask, request, jsonify
import logging
import logging.config


class LoggerManager:
    _instance = None
    _configured = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_instance", None):
            return

    def configure(self):
        if self._configured:
            return logging.getLogger()

        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': 'INFO',
                },
                'file': {
                    'class': 'logging.handlers.WatchedFileHandler',
                    'formatter': 'standard',
                    'level': 'DEBUG',
                    'filename': 'app.log',
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG',
                    'propagate': True
                },
            }
        })
        self._configured = True
        return logging.getLogger()
        
LoggerManager().configure()
app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    return jsonify({'response': f'You said: {message}'})

if __name__ == '__main__':
    app.run(debug=True)
