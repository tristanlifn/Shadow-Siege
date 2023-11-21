import json

class Read_JSON:
    def __init__(self, fileName):
        self.filename = fileName
        self.high_score = self.read_high_score()
        self.score = 0

    def read_high_score(self):
        try:
            with open(self.filename, 'r') as f:
                return int(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def update_high_score(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            with open(self.filename, 'w') as f:
                json.dump(str(self.high_score), f)

    def reset_high_score(self):
        self.high_score = 0
        with open(self.filename, 'w') as f:
            json.dump(str(self.high_score), f)

    def reset_current_score(self):
        self.score = 0