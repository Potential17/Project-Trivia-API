import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        #self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:postgres@localhost:5432/trivia_test"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.search_term = {
            'search_term': 'what'
        }

        self.new_question = {
            'question': 'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category': 1,
            'category_name': 'Test Category Name'
        }

        self.quiz_options = {
            'quiz_category': { 'id': 1, 'type': 'Science'},
            'previous_questions': []
        }

        self.bad_request_new_question = {
            'kwestion': 'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category': 1,
            'category_name': 'Test Category Name'
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

 
    def test_search_questions(self):
        res = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        

    #Should be a way to test without harcoding an id

    # def test_delete_question(self):
    #     res = self.client().delete('/questions/2')
    #     data = json.loads(res.data)
    #     question = Question.query.get(2)
    #     self.assertEqual(200, res.status_code)
    #     self.assertEqual(question, None)
    #     self.assertEqual(data['success'], True)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz_options)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_not_found(self):
        res = self.client().delete('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)       
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_405_not_allowed(self):
        res = self.client().get('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)       
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not allowed')

    def test_422_not_processable(self):
        res = self.client().post('/questions', json=self.bad_request_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)       
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not processable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()