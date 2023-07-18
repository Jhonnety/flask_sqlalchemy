from flask import Flask, redirect, render_template, url_for, request
from sqlalchemy import DATETIME, create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = Flask(__name__)
Base = declarative_base()
engine = create_engine("sqlite:///mydb.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

class Todo(Base):
    __tablename__ = "task"
    tid = Column("tid", Integer, primary_key=True, autoincrement=True)
    content = Column("content", String, nullable=False)
    description = Column("description", String, nullable=True)
    owner = Column("owner", String, nullable=True)
    date_created = Column("date_created", DATETIME, default=datetime.utcnow)

    def __init__(self,content, description, owner):
        self.content = content
        self.description = description
        self.owner = owner

    def __repr__(self):
        return f"({self.tid} {self.content} {self.description} {self.date_created})"
    
    
if __name__ == "__main__":
    app.run()

@app.route('/index', methods=['POST', 'GET'])   
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['content'] != "":
            try:
                new_task = Todo( 
                                request.form['content'],
                                request.form['description'],
                                request.form['owner']
                                )
                session.add(new_task)
                session.commit()
                return redirect('/')
            except:
                return 'There was an issue adding your task'
        else:
            tasks = session.query(Todo).order_by(Todo.date_created).all()
            return render_template('index.html',  tasks=tasks, error=True)
    else:
        tasks = session.query(Todo).order_by(Todo.date_created).all()
        return render_template('index.html',  tasks=tasks, error=False)

@app.route('/delete/<int:tid>')
def delete(tid):
    task_to_delete = session.query(Todo).filter(Todo.tid == tid).first()
    try:   
        session.delete(task_to_delete)
        session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    
@app.route('/update/<int:tid>', methods=['POST','GET'])
def update(tid): 
    task = session.query(Todo).filter(Todo.tid == tid).first()   
    if request.method == 'POST':
        if request.form['content'] == "":
            return render_template('update.html', task=task, error=True)
        else:
            task.content = request.form['content']
            task.owner = request.form['owner']
            task.description = request.form['description']
            try:
                session.commit()
                return redirect('/')
            except:
                return 'There was an issue updating your task'
        
    else:
        return render_template('update.html', task=task, error=False)
         