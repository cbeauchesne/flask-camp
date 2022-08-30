class Test_Profile:
    def test_main(self):
        from api.models.profile import Profile

        Profile().create()
