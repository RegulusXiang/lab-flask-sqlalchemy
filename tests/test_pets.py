# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pet Model Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
coverage report -m
"""

import unittest
from server import Pet, DataValidationError, app, db

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(unittest.TestCase):
    """ Test Cases for Pets """

    @classmethod
    def setUpClass(cls):
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.drop_all()    # clean up the last tests
        Pet.initialize_db(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_pet(self):
        """ Create a pet and assert that it exists """
        pet = Pet(name="fido", category="dog", available=True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "fido")
        self.assertEqual(pet.category, "dog")
        self.assertEqual(pet.available, True)

    def test_add_a_pet(self):
        """ Create a pet and add it to the database """
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = Pet(name="fido", category="dog", available=True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, None)
        pet.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(pet.id, 1)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)

    def test_update_a_pet(self):
        """ Update a Pet """
        pet = Pet(name="fido", category="dog", available=True)
        pet.save()
        self.assertEqual(pet.id, 1)
        # Change it an save it
        pet.category = "k9"
        pet.save()
        self.assertEqual(pet.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].category, "k9")

    def test_delete_a_pet(self):
        """ Delete a Pet """
        pet = Pet(name="fido", category="dog", available=True)
        pet.save()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

    def test_serialize_a_pet(self):
        """ Test serialization of a Pet """
        pet = Pet(name="fido", category="dog", available=False)
        data = pet.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "fido")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "dog")
        self.assertIn('available', data)
        self.assertEqual(data['available'], False)

    def test_deserialize_a_pet(self):
        """ Test deserialization of a Pet """
        data = {"id": 1, "name": "kitty", "category": "cat", "available": True}
        pet = Pet()
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "kitty")
        self.assertEqual(pet.category, "cat")
        self.assertEqual(pet.available, True)

    def test_deserialize_with_no_name(self):
        """ Deserialize a Pet without a name """
        pet = Pet()
        data = {"id":0, "category": "cat", "available": True}
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Pet with no data """
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Pet with bad data """
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, "data")

    def test_find_pet(self):
        """ Find a Pet by ID """
        Pet(name="fido", category="dog", available=True).save()
        Pet(name="kitty", category="cat", available=False).save()
        pet = Pet.find(2)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, 2)
        self.assertEqual(pet.name, "kitty")
        self.assertEqual(pet.available, False)

    def test_find_with_no_pets(self):
        """ Find a Pet with no Pets """
        pet = Pet.find(1)
        self.assertIs(pet, None)

    def test_pet_not_found(self):
        """ Test for a Pet that doesn't exist """
        Pet(name="fido", category="dog", available=True).save()
        pet = Pet.find(2)
        self.assertIs(pet, None)

    def test_find_by_category(self):
        """ Find Pets by Category """
        Pet(name="fido", category="dog", available=True).save()
        Pet(name="kitty", category="cat", available=False).save()
        pets = Pet.find_by_category("cat")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "kitty")
        self.assertEqual(pets[0].available, False)

    def test_find_by_name(self):
        """ Find a Pet by Name """
        Pet(name="fido", category="dog", available=True).save()
        Pet(name="kitty", category="cat", available=False).save()
        pets = Pet.find_by_name("kitty")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "kitty")
        self.assertEqual(pets[0].available, False)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestPets)
    # unittest.TextTestRunner(verbosity=2).run(suite)
