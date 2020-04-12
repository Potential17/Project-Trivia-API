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
        self.database_name = "trivia_test"
        self.password = 'postgres'
        self.user = 'postgres'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.user, self.password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path) 
        self.new_question = {
            "question": "question",
            "answer": "answer",
            "category": 1,
            "difficulty": 2
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories_success(self):
        '''
            Tests get all categories
        '''
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_get_categories_with_wrong_route_failure(self):
        '''
            Test calling a wrong endpoint
        '''
        response = self.client().get('/category')

        self.assertEqual(response.status_code, 404)
    
    def test_create_question_success(self):
        '''
            Test create question
        '''
        response = self.client().post('/questions',
                                      content_type='application/json',
                                      data=json.dumps(self.new_question))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], "Question Successfully added.")
        self.assertEqual(data['success'], True)
    
    def test_delete_question_with_valid_id__success(self):
        '''
            Tests delete a question by id
        '''
        response = self.client().post('/questions',
                                      content_type='application/json',
                                      data=json.dumps(self.new_question))
        respons = self.client().delete('/questions/1')
        print(respons.data)

        self.assertEqual(respons.status_code, 200)
    
    def test_delete_question_with_invalid_id_failure(self):
        '''
            Tests delete a question by id
        '''
        response = self.client().delete('/questions/10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(data['success'], False)

    def test_route_wrong_method_failure(self):
        '''
            Tests enpoint with wrong method
        '''
        response = self.client().patch('/categories')

        self.assertEqual(response.status_code, 405)   


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
