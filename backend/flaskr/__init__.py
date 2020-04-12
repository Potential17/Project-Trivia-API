import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  # configure cors
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    '''
    Function to configure cors headers
    '''

    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response 

  def paginate_questions(page, selection):
    '''
        Method to pagenate questions.
    '''
    QUESTOINS_PER_PAGE = 10

    start = (page - 1) * QUESTOINS_PER_PAGE
    end = start + QUESTOINS_PER_PAGE

    allRecords = []  

    for item, category in selection:
        item = item.format()
        item['category_id'] = item['category']
        item['category'] = category
        allRecords.append(item)

    current_records = allRecords[start:end]

    return current_records 
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
    '''
      Endpoint to get all categories. 
    '''
    categories = []
    results = Category.query.all()
    for category in results:
      categories.append(category.type)
    return jsonify({
      'categories': categories,
      'success': True
    }), 200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    '''
      Endpoint to get all questions
      Pagination: 10
    '''
    page = request.args.get('page', 1, type=int)
    questions = Question.query.join(
        Category,
        Category.id == Question.category
    ).add_columns(Category.type).all()

    current_questions = paginate_questions(page, questions)

    categories = []
    for item in Category.query.all():
        categories.append(item.type)

    if len(current_questions) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': categories,
        'current_category': "all"
    }), 200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    '''
      Endpoint to delete a question 
    '''
  
    question = Question.query.filter_by(id=id).first()

    if not question:
        abort(404, "Question with id not found")
    question.delete()

    return jsonify({
        'success': True,
        'question_id': id,
        'message': 'Question Successfully deleted.'
    }), 200

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    '''
      Endpoint to create a question
    '''
    data = request.get_json()

    question = data['question']
    answer = data['answer']
    category = data['category']
    difficulty = data['difficulty']

    question = Question(question=question, 
                        answer=answer, 
                        category=int(category), 
                        difficulty=int(difficulty))
    question.insert()

    return jsonify({
      'success': True,
      'message': 'Question Successfully added.'
    }), 201

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_quetions_by_search_term():
    '''
      Endpoint to handle search questions by search term
    '''
    data = request.get_json()
    print(data)
    search_term = data["searchTerm"]
    page = request.args.get('page', 1, type=int)

    questions = Question.query.join(
        Category, Category.id == Question.category
    ).add_columns(Category.type).all()

    current_questions = paginate_questions(page, questions)

    questions = []
    for question in current_questions:
        if search_term.lower() in question['question'].lower():
            questions.append(question)
    print(questions)
    categories = []
    all_categories = Category.query.all()
    for item in all_categories:
        categories.append(item.type)

    return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions),
        'categories': categories,
        'current_category': None
    }), 200

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    '''
      Endpoint to handle get questions by category
    '''
    page = request.args.get('page', 1, type=int)

    questions = Question.query.filter_by(category=id).join(
        Category,
        Category.id == Question.category
      ).add_columns(Category.type).all()
      
    current_questions = paginate_questions(page, questions)

    if len(current_questions) == 0:
      abort(404)

    category = Category.query.filter_by(id=id).first()
    all_categories = Category.query.all()
    categories = []

    for item in all_categories:
      categories.append(item.type)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories,
      'current_category': category.type
      }), 200


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    '''
      Edpoint to get questions to play quiz
    '''
    data = request.get_json()

    category = data['quiz_category']
    
    questions = Question.query.filter_by(
        category=category['id']
    ).filter(Question.id.notin_(data['previous_questions'])).all()

    if category['id'] == 0:
      questions = Question.query.filter(
        Question.id.notin_(data['previous_questions'])).all()

    question = None
    if questions:
      question = random.choice(questions).format()

    return jsonify({
      'success': True,
      'question': question
    }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error":404,
      "message": "resource not found"
      }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error":422,
      "message": "unprocessable"
      }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error":400,
      "message": "bad request"
      }), 400
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error":405,
      "message": "method not allowed"
      }), 405

  return app

    
