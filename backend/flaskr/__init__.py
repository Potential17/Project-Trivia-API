import os
from flask import Flask, request, abort, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  db = SQLAlchemy()
  
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Add-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      if request.method != 'GET':
        abort(405)

      categories = Category.query.order_by('id').all()
      formatted_categories = [category.format() for category in categories]

      if len(categories) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'categories': formatted_categories,
        'status_code': 200
      })
    except:
      abort(422)

  @app.route('/questions', methods=['GET'])
  def get_questions():
    if request.method != 'GET' and request.method != 'POST':
      abort(405)

    try:
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      questions = Question.query.order_by('id').all()
      formatted_questions = [question.format() for question in questions]
      categories = Category.query.order_by('id').all()
      formatted_categories = [category.format() for category in categories]
      if len(questions) == 0 or len(categories) == 0:
        abort(404)
      return jsonify({
        'success': True,
        'status_code': 200,
        'questions': formatted_questions[start:end],
        'total_questions': len(formatted_questions),
        'categories': formatted_categories
      })
    except:
      abort(422)

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    if request.method != 'DELETE':
      abort(405)
    question = Question.query.get(question_id)
    if not question:
      abort(404)
    question.delete()
    db.session.commit()

    return jsonify({
      'success': True,
      'message': 'Delete occured'
    }), 200

  @app.route('/questions', methods=['POST'])
  def create_new_question():
    if request.method != 'GET' and request.method != 'POST':
      abort(405)

    try:
      req_data = request.get_json()
   
      new_question = Question(
        question = req_data['question'],
        answer = req_data['answer'],
        category = req_data['category'],
        difficulty = req_data['difficulty']
      )
      db.session.add(new_question)
  
      db.session.commit()
    except:
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()

    return jsonify({
      'success': True,
      'status_code': 200
    })
 
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    if request.method != 'POST':
      abort(405)

    req_data = request.get_json()
    term = req_data.get('searchTerm', None)
    
    questions = Question.query.filter(Question.question.ilike(f'%{term}%')).all()

    formatted_questions = [question.format() for question in questions]
    page = 1
    start = (page - 1) * 10
    end = start + 10

    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end]
    }), 200

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):
      if request.method != 'GET':
        abort(405)
            
      questions = Question.query.filter(Question.category.__eq__(category_id)).all()
      formatted_questions = [question.format() for question in questions]
      page = 1
      start = (page - 1) * 10
      end = start + 10

      return jsonify({
        'questions': formatted_questions[start:end],
        'total_questions': len(formatted_questions),
        'success': True
      }), 200

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    if request.method != 'POST':
      abort(405)

    try:
      req_data = request.get_json()

      valid_categories = [0,1,2,3,4,5,6]
      if 'quiz_category' not in req_data or 'previous_questions' not in req_data:
        abort(400)
      elif int(req_data.get('quiz_category')['id']) not in valid_categories:
        abort(422)

      questions = [question.format() for question in 
                  Question.query.filter(Question.id.notin_(
                    req_data.get('previous_questions'))).all()]
      
      if req_data.get('quiz_category')['id'] != 0:
        questions = [question.format() for question in
                    Question.query.filter_by(category=req_data.get(
                      'quiz_category')['id']).filter(
                        Question.id.notin_(req_data.get(
                          'previous_questions'))).all()]

      if questions:
        next_question = random.choice(questions)
      else:
        next_question = None

      return jsonify({
        'success': True,
        'question': next_question,
      }), 200

    except Exception as error:
      raise error
    finally:
      db.session.close()




  @app.errorhandler(404)
  def not_found(e):
    return jsonify({
      'success': False,
      'message': 'Not found'
    }), 404

  @app.errorhandler(405)
  def not_allowed(e):
    return jsonify({
      'success': False,
      'message': 'Not allowed'
    }), 405

  @app.errorhandler(422)
  def not_processable(e):
    return jsonify({
      'success': False,
      'message': 'Not processable'
    }), 422

  @app.errorhandler(500)
  def internal_error(e):
    return jsonify({
      'success': False,
      'message': 'Internal server error'
    }), 500
  
  return app

    