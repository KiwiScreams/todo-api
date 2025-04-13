from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

with app.app_context():
    db.create_all()

def api_response(success=True, message="", data=None, status_code=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data or None
    }), status_code

ERROR_MESSAGES = {
    'not_found': "Todo not found",
    'missing_title': "Title is required",
    'server_error': "Internal server error",
    'empty_list': "No todos found"
}

SUCCESS_MESSAGES = {
    'retrieved': "Todo retrieved successfully",
    'created': "Todo created successfully",
    'updated': "Todo updated successfully",
    'deleted': "Todo deleted successfully",
    'list_retrieved': "Todos retrieved successfully"
}

@app.route('/')
def home():
    return redirect(url_for('get_todos'))

@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        todos = Todo.query.all()
        if not todos:
            return api_response(
                message=ERROR_MESSAGES['empty_list'],
                data=[],
                status_code=200
            )
        return api_response(
            message=SUCCESS_MESSAGES['list_retrieved'],
            data=[todo.to_dict() for todo in todos]
        )
    except Exception as e:
        return api_response(
            success=False,
            message=ERROR_MESSAGES['server_error'],
            status_code=500
        )

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return api_response(
                success=False,
                message=ERROR_MESSAGES['not_found'],
                status_code=404
            )
        return api_response(
            message=SUCCESS_MESSAGES['retrieved'],
            data=todo.to_dict()
        )
    except Exception as e:
        return api_response(
            success=False,
            message=ERROR_MESSAGES['server_error'],
            status_code=500
        )

@app.route('/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return api_response(
                success=False,
                message=ERROR_MESSAGES['missing_title'],
                status_code=400
            )

        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )

        db.session.add(todo)
        db.session.commit()

        return api_response(
            message=SUCCESS_MESSAGES['created'],
            data=todo.to_dict(),
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(
            success=False,
            message=ERROR_MESSAGES['server_error'],
            status_code=500
        )

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return api_response(
                success=False,
                message=ERROR_MESSAGES['not_found'],
                status_code=404
            )

        data = request.get_json()
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']

        db.session.commit()

        return api_response(
            message=SUCCESS_MESSAGES['updated'],
            data=todo.to_dict()
        )
    except Exception as e:
        db.session.rollback()
        return api_response(
            success=False,
            message=ERROR_MESSAGES['server_error'],
            status_code=500
        )

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return api_response(
                success=False,
                message=ERROR_MESSAGES['not_found'],
                status_code=404
            )

        db.session.delete(todo)
        db.session.commit()

        return api_response(
            message=SUCCESS_MESSAGES['deleted'],
            data={"id": todo_id}
        )
    except Exception as e:
        db.session.rollback()
        return api_response(
            success=False,
            message=ERROR_MESSAGES['server_error'],
            status_code=500
        )

if __name__ == '__main__':
    app.run(debug=True)