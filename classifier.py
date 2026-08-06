from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

class TicketClassifier:
    def __init__(self):
        # A small, targeted training dataset to show categorization
        self.training_data = [
            # Password/Access Issues
            ("I forgot my password, how to reset it?", "password_issue"),
            ("I can't log in, as password is incorrect.", "password_issue"),
            ("How to reset password?", "password_issue"),
            ("Forgot login password.", "password_issue"),
            ("My password is not working, lock out help.", "password_issue"),
            ("Need to change my password.", "password_issue"),
            ("Login page says incorrect password.", "password_issue"),
            ("How can I recover my password?", "password_issue"),
            ("Reset credentials link please.", "password_issue"),
            ("Can't access account, password error.", "password_issue"),
            
            # Leave Balance / HR Issues
            ("How to see leave balance?", "leave_issue"),
            ("Where can I find my annual leave balance?", "leave_issue"),
            ("How many sick leaves do I have left?", "leave_issue"),
            ("Show my remaining holidays count.", "leave_issue"),
            ("Leave balance status check.", "leave_issue"),
            ("Can I check my remaining time off?", "leave_issue"),
            ("How to view my vacation balance?", "leave_issue"),
            ("Total annual leaves remaining.", "leave_issue"),
            ("Check pending sick leaves.", "leave_issue"),
            ("Where do I check my time-off balance?", "leave_issue"),

            # General/Other Issues (Escalated to Human)
            ("My laptop screen is broken.", "human_escalation"),
            ("Need help with laptop hardware repair.", "human_escalation"),
            ("Where is the salary slip for this month?", "human_escalation"),
            ("Wi-Fi is not connecting in the office.", "human_escalation"),
            ("Printer is jammed on the second floor.", "human_escalation"),
            ("How to request a new keyboard?", "human_escalation"),
            ("When is the office closed for holidays?", "human_escalation"),
            ("Can you help me with a code bug?", "human_escalation"),
        ]
        
        self.texts = [x[0] for x in self.training_data]
        self.labels = [x[1] for x in self.training_data]
        
        # Initialize and train model
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.model = LogisticRegression(C=1.5, class_weight='balanced')
        
        # Fit vectorizer & model
        X_train = self.vectorizer.fit_transform(self.texts)
        self.model.fit(X_train, self.labels)
        
    def classify(self, ticket_text: str):
        """
        Classifies the ticket and returns (predicted_class, confidence, probability_dict)
        """
        X_input = self.vectorizer.transform([ticket_text])
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        
        classes = self.model.classes_
        confidence = float(np.max(probabilities))
        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
        
        # Threshold check: if classification confidence is very low, route to human
        if confidence < 0.45:
            return "human_escalation", confidence, prob_dict
            
        return prediction, confidence, prob_dict
