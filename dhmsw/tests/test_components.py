import pytest

class FramesourceTestClass:


    @classmethod
    def setup_class(cls):
        print("Setup FramesourceTestClass!")


    @classmethod
    def teardown_class(cls):
        print("Teardown TestClass!")


    def test_CanCreateComponent(cls):
        pass 

