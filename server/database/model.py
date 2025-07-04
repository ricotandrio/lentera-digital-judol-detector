from database.db import db

class BlacklistsModel(db.Model):
  __tablename__ = "blacklists"
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  url = db.Column(db.String(255), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())  

  @staticmethod
  def add_to_blacklist(url):
    if not url:
      raise ValueError("URL cannot be empty.")
    
    existing = BlacklistsModel.query.filter_by(url=url).first()
    
    if existing:
      raise ValueError("This URL is already in the blacklist.")
    
    blacklist_entry = BlacklistsModel(url=url)
    db.session.add(blacklist_entry)
    db.session.commit()
    
    return blacklist_entry