class PipelineError(Exception):
    def __init__(self, code, message, status=422, usage=None):
        self.code = code
        self.message = message
        self.status = status
        self.usage = usage or {}
        super().__init__(message)
