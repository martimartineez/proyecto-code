from src.core.database import db
from src.core.issue import Issue


def list_issues():
    issues = db.session.query(Issue).all()
    return issues

def create_issue(**kwargs):
    issue = Issue(**kwargs)
    db.session.add(issue)
    db.session.commit()
    
    return issue

