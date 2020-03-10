import pytest

class FramesourceTestClass:

    @classmethod
    def setup_class(cls):
        print("Setup FramesourceTestClass!")


    @classmethod
    def teardown_class(cls):
        print("Teardown TestClass!")


    def test_CanCreateComponent(cls):
        _components['framesource'] = Framesource("framesource",
                                                 _qs['framesource_inq'],
                                                 pub,
                                                 _events,
                                                 configfile=config_file,
                                                 verbose=True
                                                )
        pass 

